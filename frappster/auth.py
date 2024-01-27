from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError

from frappster.database import DatabaseManager
from frappster.models import User
from frappster.types import ROLE_PERMISSIONS, AccessRole, Permissions
from frappster.utils import (hash_password,
                             verify_password,
                             reset_login_attempts,
                             is_too_many_login_attempts)
from frappster.errors import (DatabaseError,
                              GeneralError,
                              InvalidPasswordError,
                              InvalidPasswordOrIDError,
                              LoginTimeoutError,
                              PermissionDeniedError,
                              TooManyLoginAttemptsError, 
                              UserNotFoundError,
                              UserNotLoggedInError)

class AbstractAuthService(ABC):
    @abstractmethod
    def update_own_password(self, old_password:str, new_password:str) -> bool:
        pass

    @abstractmethod
    def update_password(self, user_id: int, new_password:str) -> bool:
        pass

    @abstractmethod
    def login_user(self, user_id:int, password:str) -> bool:
        pass

    @abstractmethod
    def logout_user(self, user_id: Optional[int] = None) -> bool:
        pass

    @abstractmethod
    def is_admin(self) -> bool:
        pass

    @abstractmethod
    def has_permission(self, permission:Permissions) -> bool:
        pass

class AuthService(AbstractAuthService):
    """Handles user authenication &
    authorization for roll based access
    """
    def __init__(self, db_manager:DatabaseManager) -> None:
        self.current_user: User | None = None
        self.db_manager = db_manager
        self.max_login_attempts = 3
        self.max_login_timeout_seconds = 30

    def update_own_password(self, old_password:str, new_password:str):
        self.db_manager.open_session()
        user = self.current_user
        if user is None:
            raise UserNotLoggedInError

        if not self.has_permission(Permissions.UPDATE_OWN_USER):
            raise PermissionDeniedError

        try:
            
            if not verify_password(old_password, user.password):
                raise InvalidPasswordError

            user.password = hash_password(new_password)
            self.db_manager.commit()

        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError(f"Database error occurred: {e}")

        else:
            return True

        finally:
            self.db_manager.close_session()
    
    def update_password(self, user_id: int, new_password:str):
        if not self.has_permission(Permissions.MANAGE_USERS):
            raise PermissionDeniedError

        self.db_manager.open_session()
        
        try:
            fetched_user = self.db_manager.get_one(User, user_id)
            if not isinstance(fetched_user, User):
                raise TypeError("Fetched record is not type of User")

            if fetched_user is None:
                raise UserNotFoundError
            
            fetched_user.password = hash_password(new_password)
            self.db_manager.commit()

        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError(f"Database error occurred: {e}")

        else:
            return True

        finally:
            self.db_manager.close_session()

    def login_user(self, user_id:int, password:str):
        if self.current_user is not None:
            raise GeneralError("Oh no user already logged in, but trying to login ")

        self.db_manager.open_session()
        try:
            user = self.db_manager.get_one(User, user_id)
            if not isinstance(user, User):
                # Critical program error, this should be logged in error
                # logs!
                raise TypeError("Fetched record is not type of User")

            if user is None:
                # Generic error for login sequence
                raise InvalidPasswordOrIDError

            if not reset_login_attempts(user.last_login,
                                        self.max_login_timeout_seconds):
                raise LoginTimeoutError
             
            if is_too_many_login_attempts(user.login_attempts,
                                          self.max_login_attempts): 
                raise TooManyLoginAttemptsError

            if not verify_password(password, user.password):
                # Generic error for login sequence
                user.login_attempts += 1
                raise InvalidPasswordOrIDError

            # successsfull login
            user.login_attempts = 0
            user.last_login = datetime.now()
            self.current_user = user
            self.db_manager.commit()

        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError(f"Database error occurred: {e}")

        else:
            return True 

        finally:
            self.db_manager.close_session()

    def logout_user(self, user_id: int | None = None):
        if user_id is None:
            # normal user logout
            if self.current_user is None:
                raise UserNotLoggedInError("No user is currently logged in.")
            self.current_user = None  # Log out the current user
            return True

        else:
            # Admin initiated logout for another user
            # check if current user has permissions
            if not self.has_permission(Permissions.MANAGE_USERS) and not self.is_admin():
                raise PermissionDeniedError("Insufficient permissions to log out another user.")
            else:
                return True

            # TODO: check user state in db if that user is logged in
            # TODO: log this action for audit_logs

    def is_admin(self) -> bool:
        user = self.current_user
        if user is not None:
            if user.access_role == AccessRole.ADMIN:
                return True
        return False

    def has_permission(self, permission:Permissions) -> bool:
        user = self.current_user
        if user is not None:
            if permission in ROLE_PERMISSIONS.get(user.access_role, []):
                return True

        return False

    def create_super_admin(self):
        self.db_manager.open_session()
        admins = self.db_manager.session.query(User).filter(User.access_role == AccessRole.ADMIN).all()
        if admins:
            return "Super admin already exists."

        super_admin = User(
            first_name = "Anorak",
            password = hash_password("Anorak"),
            access_role = AccessRole.ADMIN
        )

        try:
            self.db_manager.create(super_admin)
            self.db_manager.commit()
            return f"Super admin with id: {super_admin.id} created successfully."
        except SQLAlchemyError as e:
            self.db_manager.rollback()
            return f"Failed to create super admin: {e}"
        finally:
            self.db_manager.close_session()
