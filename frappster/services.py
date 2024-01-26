from sqlalchemy.exc import SQLAlchemyError

from frappster.models import User
from frappster.database import DatabaseManager
from frappster.types import ROLE_PERMISSIONS, Permissions
from frappster.utils import hash_password, verify_password
from frappster.errors import (DatabaseError, 
                              InvalidPasswordError,
                              InvalidPasswordOrIDError,
                              PermissionDeniedError,
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
        self.login_attempts = 0

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
            print("Oh NO User already logged in")
            raise

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
            
            if not verify_password(password, user.password):
                # Generic error for login sequence
                raise InvalidPasswordOrIDError

        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError(f"Database error occurred: {e}")

        else:
            self.current_user = user
            return True # successssss

        finally:
            self.db_manager.close_session()
        

    def logout_user(self, user_id: int | None = None):
        if user_id is None:
            # Normal, then a normal user is using this
            # So current user is logged out.
            self.current_user = None

        elif user_id is not None:
            # Then Permisions should be checked
            # Admin or employee is trying to logout 
            # another user. Needs to have an state variable in db
            pass

    def has_permission(self, permission:Permissions) -> bool:
        user = self.current_user
        if user is not None:
            if permission in ROLE_PERMISSIONS.get(user.access_role, []):
                return True

        return False

class UserManager:
    """Handles user actions"""
    def __init__(self, 
                 db_manager:DatabaseManager,
                 auth_service:AuthService) -> None:
        self.db_manager = db_manager
        self.auth_service = auth_service

    def create_user(self, **kwargs) -> int:
        if not self.auth_service.has_permission(Permissions.MANAGE_USERS):
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

