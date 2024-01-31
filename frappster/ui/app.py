import time

from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.table import Table, box
from rich.text import Text
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from frappster.database import DatabaseManager
from frappster.auth import AuthService
from frappster.services import UserManager, AccountService, TransactionService
from frappster.types import AccessRole, AccountType
from frappster.errors import (AccountNotFoundError,
                              InvalidCommandError,
                              PermissionDeniedError)

class BankingApp:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.auth_service = AuthService(self.db_manager)
        self.user_manager = UserManager(self.db_manager, self.auth_service)
        self.account_service = AccountService(self.db_manager, self.auth_service)
        self.transaction_service = TransactionService(self.db_manager, 
                                                      self.user_manager,
                                                      self.auth_service,
                                                      self.account_service)
        self.console = Console()

    def main_menu(self):
        self.console.print("[bold cyan]Welcome to Frappster Bank CLI[/bold cyan]")
        options = ["Login", "Exit"]
        completer = WordCompleter(options)
        choice = prompt(f"Choose an option [{options}]: ",
                                     completer=completer,
                                     is_password=False)

        try:

            if choice == "Login":
                self.login_screen()
            elif choice == "Exit":
                self.console.print("Goodbye!")
            else:
                raise InvalidCommandError

        except InvalidCommandError as e:
            self.show_error(e)
            self.main_menu()

    def login_screen(self):
        user_id = prompt("Enter Login ID: ",
                                      is_password=False)
        password = prompt("Enter password: ", is_password=True)
        
        try:
            self.auth_service.login_user(user_id, password)
        except Exception as e:
            self.show_error(e)
            self.main_menu()

        else:
            self.user = self.auth_service.get_logged_in_user()
            self.accounts = self.account_service.get_user_accounts()
            self.account_options = [str(account.account_number) for account in self.accounts]
            self.show_user_profile()
            self.account_dashboard()

    def show_error(self, msg):
        self.console.print(f"[red]{msg}")
        time.sleep(0.5)

    def simulate_work(self, msg="Validating..."):
        for _ in track(range(10), description=msg):
            time.sleep(0.1)

    def is_administrative(self):
        # For employees and Admins only
        return self.user.access_role.value > 1 

    def account_dashboard(self):

        options = ["View Accounts", "Deposit", "Withdraw", "Wire Transfer", "Logout"]
        if self.is_administrative():
            options.insert(1, "User managment")

        completer = WordCompleter(options)
        prompt_msg = f"Choose an action [{options}]: "
        choice = prompt(prompt_msg,
                                     completer=completer,
                                     is_password=False)

        try:
            if choice == "View Accounts":
                self.view_accounts()
            elif choice == "User managment" and self.is_administrative():
                self.show_user_managment()
            elif choice == "Deposit":
                self.deposit()
            elif choice == "Withdraw":
                self.withdraw()
            elif choice == "Wire Transfer":
                self.wire_transfer()
            elif choice == "Logout":
                self.auth_service.logout_user()
                self.main_menu()
            else:
                raise InvalidCommandError

        except InvalidCommandError as e:
            self.show_error(e)
            self.account_dashboard()

    def show_user_profile(self):
        profile_text = Text()
        profile_text.append(f"Login ID: {self.user.login_id}\n", style="bold")
        profile_text.append(f"Name: {self.user.first_name} {self.user.middle_name} {self.user.last_name}\n")
        profile_text.append(f"Address: {self.user.address}\n")
        profile_text.append(f"Email: {self.user.email}\n")
        profile_text.append(f"Phone: {self.user.phone_number}\n")
        if self.is_administrative():
            profile_text.append(f"Role: {self.user.access_role}", style="italic")

        panel = Panel(profile_text, title="User Profile", expand=False)
        self.console.print(panel)

    def view_accounts(self):
        accounts = self.account_service.get_user_accounts()
        try:
            if not accounts:
                raise AccountNotFoundError
        except AccountNotFoundError:
            self.show_error("No account created yet")
            self.account_dashboard()

        try:

            table = Table(title="Account Details", show_header=True)
            table.add_column("Account number", justify="right")
            table.add_column("Account type")
            table.add_column("Balance", justify="right")

            for account in accounts:
                table.add_row(str(account.account_number),
                              str(account.account_type),
                              str(round(account.balance, 2)) + "kr")

            self.console.print(table)
            completer = WordCompleter(self.account_options)
            account_number = prompt("Show account: ", completer=completer)
            self.view_account_transactions(account_number)
            prompt("Press enter to return", default="")

            self.account_dashboard()

        except Exception as e:
            self.show_error(e)
            self.account_dashboard()

    def view_account_transactions(self, account_number):
        # Show tranaction history for chosen account
        transactions = self.transaction_service.get_history(account_number)
        try:
            if not transactions:
                raise AccountNotFoundError
        except AccountNotFoundError:
            self.show_error("No transactions yet")
            self.account_dashboard()

        table = Table(title=f"Transactin history for account: {account_number} ", show_header=True)
        table.add_column("Date", justify='center')
        table.add_column("Senders Number", justify='center')
        table.add_column("Recipients Number", justify='center')
        table.add_column("Transaction Type", justify='center')
        table.add_column("Amount", justify='center')

        for transaction in transactions:
            if transaction["recipient_number"] == int(account_number) or transaction["recipient_number"] == "-":
                amount_color = "green" 
                sign = '+'
            elif transaction["sender_number"] == int(account_number) or transaction["sender_number"] == "-":
                amount_color = "red" 
                sign = '-'
            else:
                sign = ''
                amount_color = "white"

            table.add_row(
                str(transaction["date"]),
                str(transaction["sender_number"]),
                str(transaction["recipient_number"]),
                str(transaction["type"]),
                str(f"[{amount_color}]{sign}{transaction['amount']}Kr [/]")
            )

        self.console.print(table)

    def deposit(self):

        try:
            if not self.accounts:
                raise AccountNotFoundError

            completer = WordCompleter(self.account_options)
            account_number = prompt("To account: ", completer=completer)
            amount = prompt("Enter amount to deposit: ")
            # self.simulate_work() 
            msg = self.transaction_service.make_deposit(account_number, amount)
        except AccountNotFoundError as e:
            self.show_error("No account created yet")
            self.account_dashboard()

        except Exception as e:
            self.show_error(e)
            self.deposit()
        else:
            self.console.print(f"[green]{msg['msg']}[/green]")
            self.account_dashboard()

    def withdraw(self):
        try:
            if not self.accounts:
                raise AccountNotFoundError
        except AccountNotFoundError:
            self.show_error("No account created yet")
            self.account_dashboard()

        try:    
            completer = WordCompleter(self.account_options)
            account_number = prompt("From account: ", completer=completer)
            amount = prompt("Enter amount to withdraw: ")
            # self.simulate_work() 
            msg = self.transaction_service.make_withdraw(account_number, amount)
        except AccountNotFoundError as e:
            self.show_error(e)
            self.account_dashboard()

        except Exception as e:
            self.show_error(e)
            self.withdraw()

        else:
            self.console.print(f"[green]{msg['msg']}[/green]")
            self.account_dashboard()

    def wire_transfer(self):
        try:
            if not self.accounts:
                raise AccountNotFoundError

            completer = WordCompleter(self.account_options)
            account_number = prompt("From account: ", completer=completer)
            recievers_account_number = prompt("To account: ", completer=completer)
            amount = prompt("Enter amount to transfer: ")
            # self.simulate_work() 
            msg = self.transaction_service.initiate_transaction(account_number,
                                                                recievers_account_number,
                                                                amount)
        except AccountNotFoundError as e:
            self.show_error(e)
            self.account_dashboard()

        except Exception as e:
            self.show_error(e)
            self.deposit()

        else:
            self.console.print(f"[green]{msg['msg']}[/green]")
            self.account_dashboard()

    def show_user_managment(self):
        try:
            if not self.is_administrative():
                raise PermissionDeniedError

        except PermissionDeniedError as e:
            self.show_error(e)
            self.account_dashboard()

        options = ["Create new user", "Edit User","Create account", "Show all users", "Main menu"]
        completer = WordCompleter(options)
        choice = prompt(f"Choose an action [{options}]: ", completer=completer)

        try:
            if choice == options[0]:
                self.create_user_screen()
            elif choice == options[1]:
                self.edit_user_screen()
            elif choice == options[2]:
                self.create_account_screen()
            elif choice == options[3]:
                self.show_all_users()
            elif choice == options[-1]:
                self.account_dashboard()
            else:
                raise InvalidCommandError


        except Exception as e:
            self.show_error(e)
            self.show_user_managment()

    def create_user_screen(self):
        user_data = {
        "first_name": "",
        "middle_name": "",
        "last_name": "",
        "address": "",
        "email": "",
        "phone_number": "",
        "password": "",
        "access_role": AccessRole.CUSTOMER
        }

        while True:
            for field in user_data:
                if field == "password":
                    while True:
                        password = prompt(f"Enter {field}: ", is_password=True)
                        password_verify = prompt("Verify password: ", is_password=True)
                        if password == password_verify:
                            user_data[field] = password
                            break
                        else:
                            self.console.print("[red]Passwords do not match. Please try again.[/red]")
                elif field == "access_role":
                    options = ["Admin", "Employee", "Customer"]
                    completer = WordCompleter(options, ignore_case=True)
                    choice = prompt(f"Choose access role [{options}]: ",
                                                 completer=completer,
                                                 default=user_data[field].name)
                    if choice == options[0]:
                        user_data[field] = AccessRole.ADMIN
                    elif choice == options[1]:
                        user_data[field] = AccessRole.EMPLOYEE
                    else:
                        user_data[field] = AccessRole.CUSTOMER
                else:
                    user_data[field] = prompt(f"Enter {field} [{user_data[field]}]: ",
                                                           default=user_data[field]
                                                           )

            try:
                self.user_manager.create_user(**user_data)
                self.console.print("[green]User created successfully![/green]")
                self.show_user_managment()
                break  
            except Exception as e:
                self.show_error(e)
                options = ['retry', 'abort']
                retry_field = prompt(f"Choose an action [{options}]: ")
                if retry_field == options[0]:
                    continue  
                elif retry_field == options[1]:
                    self.show_user_managment()

                if retry_field in user_data:
                    if retry_field == "access_role":
                        options = ["Admin", "Employee", "Customer"]
                        completer = WordCompleter(options, ignore_case=True)
                        choice = prompt(f"Choose access role: [{options}] (def: {options[-1]}",
                                                     completer=completer,
                                                     default=user_data[retry_field].name)
                        if choice == options[0]:
                            user_data[retry_field] = AccessRole.ADMIN
                        elif choice == options[1]:
                            user_data[retry_field] = AccessRole.EMPLOYEE
                        else:
                            user_data[retry_field] = AccessRole.CUSTOMER

                    user_data[retry_field] = prompt(f"Enter {retry_field}: ",
                                                                 default=user_data[retry_field])

    def edit_user_screen(self):
        options = [str(user.login_id) for user in self.user_manager.get_all_users()]
        completer = WordCompleter(options)
        choice = prompt("Which user to edit: ", completer=completer)
        if choice not in options:
            raise InvalidCommandError

        user = self.user_manager.get_user(int(choice)) 
        
        user_data = {
        "first_name": user.first_name,
        "middle_name": user.middle_name,
        "last_name": user.last_name,
        "address": user.address,
        "email": user.email,
        "phone_number": user.phone_number,
        "access_role": user.access_role
        }

        while True:
            for field in user_data:
                if field == "access_role":
                    options = ["Admin", "Employee", "Customer"]
                    completer = WordCompleter(options, ignore_case=True)
                    choice = prompt("Choose access role: ",
                                                 completer=completer,
                                                 default=user_data[field].name)
                    if choice == options[0]:
                        user_data[field] = AccessRole.ADMIN
                    elif choice == options[1]:
                        user_data[field] = AccessRole.EMPLOYEE
                    else:
                        user_data[field] = AccessRole.CUSTOMER
                else:
                    user_data[field] = prompt(f"Enter {field} [{user_data[field]}]: ",
                                                           default=user_data[field]
                                                           )

            try:
                msg = self.user_manager.update_user(user_data, user.login_id)
                self.console.print(f"[green]{msg['msg']}[/green]")
                self.show_user_managment()
                break  

            except Exception as e:
                self.show_error(e)
                options = ['retry', 'abort'] 
                retry_field = prompt(f"Choose an action [{options}]: ")
                if retry_field == options[0]:
                    continue # start from strach idk why lmao 
                elif retry_field == options[1]:
                    self.show_user_managment()

                if retry_field in user_data:
                    if retry_field == "access_role":
                        options = ["Admin", "Employee", "Customer"]
                        completer = WordCompleter(options, ignore_case=True)
                        choice = prompt("Choose access role: ",
                                                     completer=completer,
                                                     default=user_data[retry_field].name)
                        if choice == options[0]:
                            user_data[retry_field] = AccessRole.ADMIN
                        elif choice == options[1]:
                            user_data[retry_field] = AccessRole.EMPLOYEE
                        else:
                            user_data[retry_field] = AccessRole.CUSTOMER
                    user_data[retry_field] = prompt(f"Enter {retry_field}: ",
                                                                 default=user_data[retry_field])

    def show_all_users(self):
        table = Table(show_header=True, header_style="bold magenta")
        table.box = box.ROUNDED
        table.add_column("Login ID", style="dim")
        table.add_column("Full Name", justify="center")
        table.add_column("Email", justify="center")
        table.add_column("Role", justify="center")

        try:
            users = self.user_manager.get_all_users()

        except Exception as e:
            self.show_error(e)
            self.show_user_managment()

        else:
            for user in users:
                middle_name = user.middle_name if user.middle_name is not None else ""
                users_name = f"{user.first_name} {middle_name} {user.last_name}"

                table.add_row(str(user.login_id),
                              users_name,
                              str(user.email),
                              str(user.access_role)
                              )

            self.console.print(table)
            self.show_user_managment()

    def create_account_screen(self):
        options = [str(user.login_id) for user in self.user_manager.get_all_users()]
        completer = WordCompleter(options)
        user_id = prompt("To whom to create new account: ", completer=completer)
        try:
            if user_id == "":
                self.show_user_managment()

            if user_id not in options:
                raise InvalidCommandError

            options = ["Savings", "Checking", "Business"]
            completer = WordCompleter(options, ignore_case=True)
            choice = prompt(f"Choose account type [{options}]:  ",
                                         completer=completer,
                                         )
            if choice == options[0]:
                account_type = AccountType.SAVINGS
            elif choice == options[1]:
                account_type = AccountType.CHECKINGS
            else:
                account_type = AccountType.BUSINESS


            options = ["Yes", "No"]
            completer = WordCompleter(options, ignore_case=True)
            choice = prompt(f"Initial deposit [{options}]: ",
                                         completer=completer)
            account_data = {
                    'user_id': user_id,
                    'account_type': account_type,
                    }
            if choice == options[0]:
                account_data['balance'] = prompt(f"Amount: ")

            msg = self.account_service.create_account(**account_data)
            self.console.print(msg['msg']) 

        except Exception as e:
            self.show_error(e)
            self.create_account_screen()

        else:
            self.show_user_managment()

    def run(self):
        self.main_menu()
