from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from frappster.models import User
from frappster.database import DatabaseManager
from frappster.types import ROLE_PERMISSIONS, AccessRole, Permissions
from frappster.utils import hash_password, is_too_many_login_attempts, reset_login_attempts, verify_password
from frappster.errors import (DatabaseError, GeneralError, 
                              InvalidPasswordError,
                              InvalidPasswordOrIDError, LoginTimeoutError,
                              PermissionDeniedError, TooManyLoginAttemptsError,
                              UserNotFoundError,
                              UserNotLoggedInError,
                              )

class AuthService:
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

        else:
            # Admin initiated logout for another user
            # check if current user has permissions
            if not self.has_permission(Permissions.MANAGE_USERS) and not self.is_admin():
                raise PermissionDeniedError("Insufficient permissions to log out another user.")

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

class UserManager:
    """Handles user actions
    Admin can manage all users.
    Employees can manage customers. 
    Customers can't manage anyone.
    """
    def __init__(self, 
                 db_manager:DatabaseManager,
                 auth_service:AuthService) -> None:
        self.db_manager = db_manager
        self.auth_service = auth_service

    def create_user(self, **kwargs) -> int:
        if not self.auth_service.has_permission(Permissions.MANAGE_USERS):
            raise PermissionDeniedError

        if 'access_role' in kwargs and kwargs['access_role'] == AccessRole.ADMIN:
            if not self.auth_service.is_admin():
                raise PermissionDeniedError

        self.db_manager.open_session()
        try:
            new_user = User(**kwargs)
            
            if 'password' in kwargs:
                new_user.password = hash_password(kwargs['password'])

            self.db_manager.create(new_user)
            self.db_manager.commit()


        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError(f"Database error occurred: {e}")

        else:
            return new_user.id
            
        finally:
            self.db_manager.close_session()

    def update_user(self, user: User):
        """Get user is used to fetch that user"""
        if not self.auth_service.has_permission(Permissions.MANAGE_USERS):
            raise PermissionDeniedError

        if not self.auth_service.is_admin() and user.access_role == AccessRole.ADMIN:
            raise PermissionDeniedError

        self.db_manager.open_session()
        try:

            self.db_manager.session.merge(user)
            self.db_manager.commit()
           
        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError(f"Database error occurred: {e}")

        else:
            return True # successssss

        finally:
            self.db_manager.close_session()

    def delete_user(self):
        if not self.auth_service.has_permission(Permissions.MANAGE_USERS):
            raise PermissionDeniedError
        pass

    def get_user(self, user_id:int):
        if not self.auth_service.has_permission(Permissions.MANAGE_USERS):
            raise PermissionDeniedError

        self.db_manager.open_session()
        try:
            user = self.db_manager.get_one(User, user_id)
            if user is None:
                raise UserNotFoundError
            return user

        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError(f"Database error occurred: {e}")
        finally:
            self.db_manager.close_session()

class AccountService:
    """Handles user account related tasks"""
    def __init__(self, db_manager:DatabaseManager) -> None:
        self.db_manager = db_manager

    def create_account(self):
        pass

    def close_account(self):
        pass

    def get_account_details(self):
        pass

class TransactionService:
    """Handles transactions in the system"""
    def __init__(self, db_manager:DatabaseManager) -> None:
        self.db_manager = db_manager

    def make_deposit(self):
        pass

    def make_withdrawal(self):
        pass

    def transfer_funds(self, sender:User, reciever:User):
        pass

