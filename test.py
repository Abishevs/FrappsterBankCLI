import time

from rich.table import Table
from rich.console import Console
from rich.progress import track

from frappster.auth import AuthService
from frappster.database import DatabaseManager
from frappster.services import AccountService, UserManager
from frappster.types import AccessRole, AccountType

db_manager = DatabaseManager()
db_manager.create_super_admin()
auth_service = AuthService(db_manager)
account_service = AccountService(db_manager, auth_service)

auth_service.login_user(42069, "secure")
user_manager = UserManager(db_manager, auth_service)
print(auth_service.current_user.first_name)
# user_manager.get_user(auth_service.current_user.login_id)
# user_manager.create_user(
#         first_name="Samantha",
#         login_id=4,
#         last_name="Smith",
#         address="456 Elm Street",
#         email="alice.smith@example.com",
#         phone_number="987-654-3210",
#         password="wade",  
#         access_role=AccessRole.EMPLOYEE
#         )
auth_service.logout_user()
auth_service.login_user(4, "wade")
# account_service.create_account(
#         clearings_number=123,
#         user_id=auth_service.current_user.id,
#         account_number=334,
#         account_type=AccountType.BUSINESS,
#         balance=330
#         )
accounts = account_service.get_account_details()
auth_service.logout_user()
auth_service.login_user(22, "alice")


console = Console()
console.print(accounts)
table = Table(show_header=True, header_style="bold magenta")
table.add_column("Number", style="dim", width=12)
table.add_column("User id", justify="right")
table.add_column("Balance", justify="right")
# table.add_column("Data", justify="right")
    
for account in accounts:
    table.add_row(str(account.account_number), str(account.user_id),
                  str(account.balance))
table.add_row("2024-01-26", "Withdrawal", "-$500")


for step in track(range(10), description="Loading..."):
    time.sleep(0.5)
console.print(table)
