from sqlalchemy.exc import SQLAlchemyError
from frappster.auth import AbstractAuthService

from frappster.models import User
from frappster.database import AbstractDatabaseManager
from frappster.types import AccessRole, Permissions
from frappster.utils import hash_password, requires_permissions, requires_role
from frappster.errors import (DatabaseError, 
                              PermissionDeniedError, 
                              UserNotFoundError,
                              )


class UserManager:
    """Handles user actions
    Admin can manage all users.
    Employees can manage customers. 
    Customers can't manage anyone.
    """
    def __init__(self, 
                 db_manager:AbstractDatabaseManager,
                 auth_service:AbstractAuthService) -> None:
        self.db_manager = db_manager
        self.auth_service = auth_service

    @requires_role(AccessRole.EMPLOYEE)
    @requires_permissions(Permissions.MANAGE_USERS)
    def create_user(self, **kwargs) -> int:
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

    @requires_role(AccessRole.EMPLOYEE)
    @requires_permissions(Permissions.MANAGE_USERS, Permissions.UPDATE_USER)
    def update_user(self, user: User):
        """Get user is used to fetch that user"""
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

    @requires_role(AccessRole.ADMIN)
    @requires_permissions(Permissions.MANAGE_USERS, Permissions.DELETE_USER)
    def delete_user(self, user: User):
        if not self.auth_service.has_permission(Permissions.MANAGE_USERS):
            raise PermissionDeniedError

        if not self.auth_service.is_admin() and user.access_role == AccessRole.ADMIN:
            raise PermissionDeniedError


            
        pass

    @requires_role(AccessRole.EMPLOYEE)
    @requires_permissions(Permissions.MANAGE_USERS, Permissions.VIEW_USER)
    def get_user(self, user_id:int):

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
    def __init__(self, 
                 db_manager:AbstractDatabaseManager,
                 auth_service: AbstractAuthService
                 ) -> None:
        self.db_manager = db_manager
        self.auth_service = auth_service

    @requires_role(AccessRole.EMPLOYEE)
    @requires_permissions(Permissions.MANAGE_ACCOUNTS, Permissions.CREATE_ACCOUNT)
    def create_account(self):
        print("Creating account")
        pass

    @requires_role(AccessRole.EMPLOYEE)
    @requires_permissions(Permissions.MANAGE_ACCOUNTS, Permissions.CLOSE_ACCOUNT)
    def close_account(self):
        print("Closing account")
        pass

    @requires_role(AccessRole.EMPLOYEE)
    @requires_permissions(Permissions.MANAGE_ACCOUNTS, Permissions.VIEW_ACCOUNT)
    def get_account_details(self):
        print("Getting account details")
        pass

class TransactionService:
    """Handles transactions in the system"""
    def __init__(self, db_manager:AbstractDatabaseManager) -> None:
        self.db_manager = db_manager

    def make_deposit(self):
        pass

    def make_withdrawal(self):
        pass

    @requires_role(AccessRole.CUSTOMER)
    @requires_permissions(Permissions.MANAGE_ACCOUNTS, Permissions.INITIATE_OWN_TRANSACTION)
    def initate_transaction(self, senders_account_id, recievers_account_id):
        pass

