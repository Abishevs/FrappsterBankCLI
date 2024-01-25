from frappster.database import DatabaseManager
from frappster.models import User

class UserManager:
    """Handles user actions"""
    def __init__(self, db_manager:DatabaseManager) -> None:
        self.current_user = None
        self.db_manager = db_manager

    def create_user(self):
        pass

    def update_user(self):
        pass

    def delete_user(self):
        pass

    def get_user(self):
        pass

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

class AuthService:
    """Handles user authenication &
    authorization for roll based access
    """
    def __init__(self, db_manager:DatabaseManager) -> None:
        self.db_manager = db_manager

    def login_user(self):
        pass

    def logout_user(self):
        pass

    def check_permision(self):
        pass
