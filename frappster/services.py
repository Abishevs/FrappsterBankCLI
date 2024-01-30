from sqlalchemy.exc import SQLAlchemyError
from frappster.auth import AbstractAuthService, AuthService

from frappster.models import Account, AccountData, Transaction, User
from frappster.database import AbstractDatabaseManager
from frappster.types import AccessRole, Permissions
from frappster.utils import gen_randomrange, hash_password, requires_permissions, requires_role
from frappster.errors import (AccountNotFoundError, DatabaseError, GeneralError, InsufficientFundsError, 
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
                 auth_service:AuthService) -> None:
        self.db_manager = db_manager
        self.auth_service = auth_service
        

    @requires_role(AccessRole.EMPLOYEE)
    @requires_permissions(Permissions.MANAGE_USERS)
    def create_user(self, **kwargs) -> int:
        # Only admins can create admin users
        if 'access_role' in kwargs and kwargs['access_role'] == AccessRole.ADMIN:
            if not self.auth_service.is_admin():
                raise PermissionDeniedError

        self.db_manager.open_session()
        try:
            new_user = User(**kwargs)

            new_user.login_id = gen_randomrange()
            
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
    @requires_permissions([Permissions.MANAGE_USERS, Permissions.DELETE_USER])
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
            if not isinstance(user, User):
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
    def create_account(self, **kwargs):
        self.db_manager.open_session()
        user_id = self.auth_service.current_user.id
        try:
            new_account = Account(**kwargs)

            new_account.user_id = user_id

            self.db_manager.create(new_account)
            self.db_manager.commit()


        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError(f"Database error occurred: {e}")

        else:
            print("Createeed account")
            return True            

        finally:
            self.db_manager.close_session()
        pass

    @requires_role(AccessRole.EMPLOYEE)
    @requires_permissions(Permissions.MANAGE_ACCOUNTS, Permissions.CLOSE_ACCOUNT)
    def close_account(self):
        print("Closing account")
        pass

    @requires_role(AccessRole.EMPLOYEE)
    @requires_permissions(Permissions.MANAGE_ACCOUNTS, Permissions.VIEW_ACCOUNT)
    def get_user_accounts(self, user:User | None = None):
        print("Getting account details")
        login_id = self.auth_service.current_user.login_id
        self.db_manager.open_session()
        
        try:
            user = self.db_manager.get_one(User, login_id)
            if user is None:
                raise UserNotFoundError

            accounts = []
            for account in user.accounts:
                accounts.append(AccountData(**account.to_dict()))

            return accounts

        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError(f"Database error occurred: {e}")

        finally:
            self.db_manager.close_session()

    def get_account(self, account_number):
            account = self.db_manager.get_one(Account, account_number)
            if account is None:
                raise AccountNotFoundError
            if not isinstance(account, Account):
                raise GeneralError
            return account

class TransactionService:
    """Handles transactions in the system"""
    def __init__(self,
                 db_manager:AbstractDatabaseManager,
                 user_manager: UserManager,
                 account_service: AccountService
                 ) -> None:
        self.db_manager = db_manager
        self.account_service = account_service
        self.user_manager = user_manager

    def make_deposit(self, account_id:int, amount: float):
        # 1) check if its users accounts
        # 2) Then check if amount is float
        # 3) Sheesh

        current_user = self.user_manager.auth_service.get_logged_in_user()
        senders_account = self.account_service.get_account(account_id)
        if amount < 0:
            raise ValueError("Value too lowe")


    def make_withdrawal(self, account_number:int , amount: float):
        # 1) check if its users accounts
        # 2) Then check if amount is float
        # 3) Check if sufficent funds
        current_user = self.user_manager.auth_service.get_logged_in_user()
        if amount >= senders_account.balance:
            raise InsufficientFundsError("Bre not enough moneeey")

    @requires_role(AccessRole.CUSTOMER)
    @requires_permissions(Permissions.MANAGE_ACCOUNTS, Permissions.INITIATE_OWN_TRANSACTION)
    def iniate_transaction(self,
                           senders_account_id: int,
                           recievers_account_id:int,
                           amount: float):
        try:
            self.db_manager.open_session()
            current_user = self.user_manager.auth_service.get_logged_in_user()
            senders_account = self.account_service.get_account(senders_account_id)
            if senders_account.user_id != current_user.id:
                raise GeneralError

            if amount >= senders_account.balance:
                raise InsufficientFundsError("Bre not enough moneeey")

                
            recievers_account = self.account_service.get_account(recievers_account_id)
            recievers_account.balance = amount
            new_transaction = Transaction()
            self.db_manager.commit()
        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError(e)

        else:
            return {"msg": f"Sent money to account: {recievers_account.account_number}" }

        finally:
            self.db_manager.close_session()


        # 1) check if sender is current user
        # 2) Check if reciever is valid
        # 3) Check if sender amount is float
        # 4) check if amount is sufficent 
