from datetime import datetime, timedelta

from sqlalchemy.exc import SQLAlchemyError

from frappster.database import DatabaseManager
from frappster.models import User, UserData
from frappster.types import ROLE_PERMISSIONS, AccessRole, Permissions
from frappster.utils import (hash_password,
                             verify_password)
from frappster.errors import (DatabaseError,
                              GeneralError,
                              InvalidPasswordError,
                              InvalidPasswordOrIDError,
                              LoginTimeoutError,
                              PermissionDeniedError,
                              TooManyLoginAttemptsError, 
                              UserNotFoundError,
                              UserNotLoggedInError)



class AuthService:
    """Handles user authenication &
    authorization for roll based access
    """
    def __init__(self, db_manager:DatabaseManager) -> None:
        self.current_user: UserData | None = None
        self.db_manager = db_manager
        self.max_login_attempts = 3
        self.max_login_timeout_seconds = 30

    def get_logged_in_user(self) -> UserData:
        if self.current_user is None:
            raise UserNotLoggedInError
        return self.current_user

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
            fetched_user = self.db_manager.get_by_login_id(user_id)
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

        time_now = datetime.now()
        self.db_manager.open_session()
        try:
            user = self.db_manager.get_by_login_id(user_id)
            if user is None:
                # Generic error for login sequence
                # print("User is None")
                raise InvalidPasswordOrIDError

            if not isinstance(user, User):
                # Critical program error, this should be logged in error
                # logs!
                raise TypeError(f"Fetched record is not type of User, but of {type(user)}")


            # 1) Last login None -> First time login
            # 2) If login_timeout -> Raise LoginTimeOutError
            # 3) If TooManyLoginAttempts -> Set loginTimeout to max_time
            # Check for too many login attempts first
            if user.login_attempts == self.max_login_attempts:
                user.login_attempts += 1
                self.db_manager.commit()
                raise TooManyLoginAttemptsError

            # Check if the current time is before the login timeout
            if user.login_timeout and time_now < user.login_timeout:
                user.login_attempts += 1
                self.db_manager.commit()
                raise LoginTimeoutError

            if not verify_password(password, user.password):
                user.login_attempts += 1
                if user.login_attempts >= self.max_login_attempts:
                    # Set the login timeout on hitting the maximum failed attempts
                    user.login_timeout = time_now + timedelta(seconds=self.max_login_timeout_seconds)
                self.db_manager.commit()
                raise InvalidPasswordOrIDError("Invalid user ID or password.")


        except UserNotFoundError as e:
            # Log error? not show details
            raise InvalidPasswordOrIDError

        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError(f"Database error occurred: {e}")

        else:
            # Successful login
            user.login_attempts = 0
            user.login_timeout = None
            user.last_login = time_now
            self.current_user = UserData(**user.to_dict())
            self.db_manager.commit()

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

