from typing import List
from sqlalchemy.exc import SQLAlchemyError
from frappster.auth import  AuthService

from frappster.models import Account, AccountData, Transaction, User, UserData
from frappster.database import  DatabaseManager
from frappster.types import AccessRole, Permissions, TransactionType
from frappster.utils import (gen_randomrange,
                             hash_password,
                             is_valid_amount,
                             requires_permissions,
                             requires_role)
from frappster.errors import (AccountNotFoundError,
                              DatabaseError,
                              GeneralError,
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
                 db_manager:DatabaseManager,
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

            new_user.login_id = gen_randomrange(4)
            
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
    def update_user(self, user_data: dict, login_id:int):
        """Get user is used to fetch that user"""
        if not self.auth_service.is_admin() and user_data['access_role'] == AccessRole.ADMIN:
            raise PermissionDeniedError

        self.db_manager.open_session()
        try:

            user = self.db_manager.get_by_login_id(login_id)
            user.from_dict(**user_data) 
            self.db_manager.commit()
           
        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError(f"Database error occurred: {e}")

        else:
            return {'msg': "Succefully updated user"}

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
    def get_user(self, login_id:int):

        self.db_manager.open_session()
        try:
            user = self.db_manager.get_by_login_id(login_id)
            if user is None:
                raise UserNotFoundError
            if not isinstance(user, User):
                raise UserNotFoundError
            return UserData(**user.to_dict())

        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError(f"Database error occurred: {e}")
        finally:
            self.db_manager.close_session()

    @requires_role(AccessRole.EMPLOYEE)
    @requires_permissions(Permissions.MANAGE_USERS, Permissions.VIEW_USER)
    def get_all_users(self) -> List[UserData]:
        self.db_manager.open_session()
        try:
            users = self.db_manager.get_all(User)
            all_users: List[UserData] = []

            for user in users:
               user = UserData(**user.to_dict())
               all_users.append(user) 
            return all_users

        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError(f"Database error occurred: {e}")

        finally:
            self.db_manager.close_session()


class AccountService:
    """Handles user account related tasks"""
    def __init__(self, 
                 db_manager:DatabaseManager,
                 auth_service: AuthService
                 ) -> None:
        self.db_manager = db_manager
        self.auth_service = auth_service

    @requires_role(AccessRole.EMPLOYEE)
    @requires_permissions(Permissions.MANAGE_ACCOUNTS, Permissions.CREATE_ACCOUNT)
    def create_account(self, **kwargs):
        self.db_manager.open_session()
        try:
            login_id = kwargs['user_id']
            user = self.db_manager.get_by_login_id(login_id)
            if 'balance' in kwargs:
                amount = is_valid_amount(kwargs['balance'])
                kwargs['balance'] = amount

            new_account = Account(**kwargs)
            new_account.account_number = gen_randomrange(6)
            new_account.clearings_number = 123
            new_account.user_id = user.id

            self.db_manager.create(new_account)
            self.db_manager.commit()

        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError

        else:
            return {'msg': f"Created account for user ID: {user.login_id}"}

        finally:
            self.db_manager.close_session()

    @requires_role(AccessRole.EMPLOYEE)
    @requires_permissions(Permissions.MANAGE_ACCOUNTS, Permissions.CLOSE_ACCOUNT)
    def close_account(self):
        raise NotImplementedError

    @requires_role(AccessRole.CUSTOMER)
    @requires_permissions(Permissions.MANAGE_ACCOUNTS, Permissions.VIEW_ACCOUNT)
    def get_user_accounts(self, user:User | None = None):
        c_user = self.auth_service.get_logged_in_user()
        self.db_manager.open_session()
        
        try:
            user = self.db_manager.get_by_login_id(c_user.login_id)
            if user is None:
                raise UserNotFoundError

            accounts:List[AccountData] = []
            for account in user.accounts:
                accounts.append(AccountData(**account.to_dict()))

            return accounts

        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError

        finally:
            self.db_manager.close_session()

    def get_account(self, account_number):
            account = self.db_manager.get_by_account_number(account_number)
            if account is None:
                raise AccountNotFoundError
            if not isinstance(account, Account):
                raise GeneralError
            return account

class TransactionService:
    """Handles transactions in the system"""
    def __init__(self,
                 db_manager:DatabaseManager,
                 user_manager: UserManager,
                 auth_service: AuthService,
                 account_service: AccountService
                 ) -> None:
        self.db_manager = db_manager
        self.account_service = account_service
        self.auth_service = auth_service
        self.user_manager = user_manager

    @requires_role(AccessRole.CUSTOMER)
    def make_deposit(self, account_number:int, amount):
        # 1) check if its users accounts
        # 2) Then check if amount is float
        # 3) Sheesh
        try:
            self.db_manager.open_session()
            current_user = self.user_manager.auth_service.get_logged_in_user()
            account = self.db_manager.get_by_account_number(account_number)
            if account.user_id != current_user.id:
                # Log("sender account is not current users account")
                raise PermissionDeniedError

            amount = is_valid_amount(amount, account.balance)

            account.balance += amount
            new_transaction = Transaction()
            new_transaction.recipients_account_number = account_number
            new_transaction.amount = amount
            new_transaction.type = TransactionType.DEPOSIT

            self.db_manager.create(new_transaction)
            self.db_manager.commit()
        except SQLAlchemyError as e:
            self.db_manager.rollback()
            # Log db error
            raise DatabaseError(e)

        else:
            return {'msg': "Successfull deposit"}

        finally: 
            self.db_manager.close_session()

    @requires_role(AccessRole.CUSTOMER)
    def make_withdraw(self, account_number:int , amount):
        # 1) check if its users accounts
        # 2) Then check if amount is float
        # 3) Check if sufficent funds
        try:
            self.db_manager.open_session()
            current_user = self.user_manager.auth_service.get_logged_in_user()
            account = self.db_manager.get_by_account_number(account_number)
            if account.user_id != current_user.id:
                # Log("sender account is not current users account")
                # raise GeneralError
                raise PermissionDeniedError

            amount = is_valid_amount(amount, account.balance)

            account.balance -= amount
            new_transaction = Transaction()
            new_transaction.senders_account_number = account_number
            new_transaction.amount = amount
            new_transaction.type = TransactionType.WITHDRAW

            self.db_manager.create(new_transaction)
            self.db_manager.commit()
        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError(e)

        else:
            return {'msg': f"Succefull withdraw"}

        finally: 
            self.db_manager.close_session()

    @requires_role(AccessRole.CUSTOMER)
    @requires_permissions(Permissions.MANAGE_ACCOUNTS, Permissions.INITIATE_OWN_TRANSACTION)
    def initiate_transaction(self,
                           senders_account_number: int,
                           recievers_account_number:int,
                           amount):
        # 1) check if sender is current user
        # 2) Check if sender amount is valid
        # 3) check if amount is sufficent 
        # 4) Check if reciever is valid
        # Send it
        try:
            self.db_manager.open_session()
            current_user = self.user_manager.auth_service.get_logged_in_user()
            senders_account = self.account_service.get_account(senders_account_number)
            if senders_account.user_id != current_user.id:
                # Log("sender account is not current users account")
                # raise GeneralError
                raise PermissionDeniedError

            recievers_account = self.account_service.get_account(recievers_account_number)
            if recievers_account == senders_account:
                # IDK too lazy to build a new one or make own messages
                # all the time...
                raise GeneralError

            amount = is_valid_amount(amount, senders_account.balance) # gonna raise errors 
                
            senders_account.balance -= amount
            recievers_account.balance += amount

            new_transaction = Transaction()
            new_transaction.amount = amount
            new_transaction.senders_account_number = senders_account.account_number
            new_transaction.recipients_account_number = recievers_account.account_number
            new_transaction.type = TransactionType.TRANSFER 

            self.db_manager.create(new_transaction)
            self.db_manager.commit()
        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError(e)

        else:
            return {"msg": f"Sent to account: {recievers_account.account_number}" }

        finally:
            self.db_manager.close_session()

    def get_history(self, account_number):
        try:
            self.db_manager.open_session()
            current_user = self.user_manager.auth_service.get_logged_in_user()
            account = self.account_service.get_account(account_number)
            if account.user_id != current_user.id:
                # Log("sender account is not current users account")
                # raise GeneralError
                raise PermissionDeniedError
            transactions = []
            for transaction in account.sent_transactions:
                transaction = transaction.to_dict()
                transactions.append(transaction)

            for transaction in account.received_transactions:
                transactions.append(transaction.to_dict())

            self.db_manager.commit()
        except SQLAlchemyError as e:
            self.db_manager.rollback()
            raise DatabaseError(e)

        else:
            # return {"msg": f"Sent to account: {recievers_account.account_number}" }
            return transactions

        finally:
            self.db_manager.close_session()




