from prompt_toolkit.layout.dimension import AnyDimension
from rich.console import Console
from rich.table import Table
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Button, Frame, TextArea


class MainScreen:
    def __init__(self) -> None:
        self.text_area = Window(content=FormattedTextControl(text='Welcome frappster bank! Enhanced with Vim motions ;)'))

    def create_layout(self):
        return Frame(HSplit([self.text_area]), title="CLI-BankingSYteme")

class BaseDashboard:
    def __init__(self, app):
        self.app = app
        self.title = "CLI-Bankgsysteeeme"
        self.user = self.app.auth_service.get_logged_in_user()
        self.main_content = Window(content=FormattedTextControl(text=f'Welcome: {self.user.first_name}  frappster bank! Enhanced with Vim motions ;)'))

    def show_error_dialog(self, message):
        self.app.show_error_dialog(message)

    def create_layout(self):
        self.root = HSplit([self.main_content])
        return Frame(self.root, title=self.title)

class UserDashboard(BaseDashboard):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.user = self.app.auth_service.get_logged_in_user()
        self.accounts = self.app.account_service.get_user_accounts(self.user)

        self.account_clickable_list = [self.create_account_button(account) for account in self.accounts]

        self.deposit_button = Button('')
        self.withdraw_button = Button('')
        self.wire_transfer_button = Button('')
        self.action_buttons = VSplit([self.deposit_button,
                                      self.withdraw_button,
                                      self.wire_transfer_button
                                      ])

        self.account_details = TextArea(read_only=True)

    def create_account_button(self, account):
        fields = f"Account ID: {account.id}, Balance: ${account.balance}"
        return Button(fields, width=(len(fields) + 2), handler=lambda: self.on_account_select(account))

    def on_account_select(self, account):
        details = f"ID: {account.id}\nType: {account.account_type}\nBalance: ${account.balance}"
        self.account_details.text = details
        self.action_buttons = VSplit([self.deposit_button,
                                      self.withdraw_button,
                                      self.wire_transfer_button
                                      ])
        self.deposit_button.text = 'Deposit'
        self.deposit_button.handler = lambda: self.on_deposit(account)
        self.withdraw_button.text = 'Witdraw'
        self.withdraw_button.handler = lambda: self.on_withdraw(account)

        self.wire_transfer_button.text = 'Wire transfer'
        self.wire_transfer_button.handler = lambda: self.on_wire_transfer(account)

    def create_layout(self):
        # left_panel_content = FormattedTextControl(text="User info")
        # left_panel = Frame(Window(content=left_panel_content), title="User Info")

        accounts_area = HSplit(self.account_clickable_list)
        accounts_buttons_frame = Frame(accounts_area, title="Accounts")
        account_details = VSplit([self.account_details, self.action_buttons])
        account_details_frame = Frame(account_details, title="Account Details")
        right_panel = HSplit([accounts_buttons_frame,
                              account_details_frame])
        
        root = HSplit([right_panel])
        # return Frame(root, title=self.title)
        return root

    def on_deposit(self, account):
        self.show_error_dialog(f"selected: {account}")
        pass

    def on_withdraw(self, account):
        pass

    def on_wire_transfer(self, account):
        pass

class EmployeeDashboard(BaseDashboard):
    def __init__(self, app):
        super().__init__(app)
        self.show_error_dialog("Hello Employee")


class AdminDashboard(BaseDashboard):
    def __init__(self, app):
        super().__init__(app)
        self.show_error_dialog("Helloo Admin")


