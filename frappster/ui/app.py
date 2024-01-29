import sys

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters import Condition, FilterOrBool, ViMode
from prompt_toolkit.filters.app import vi_navigation_mode
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.key_binding.bindings.vi import load_vi_bindings
from prompt_toolkit.key_binding.key_processor import KeyProcessor
from prompt_toolkit.key_binding.vi_state import InputMode, ViState
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Float, FloatContainer, HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Button, Frame, Label, TextArea

from frappster.database import DatabaseManager
from frappster.auth import AuthService
from frappster.services import UserManager, AccountService, TransactionService
from frappster.types import AccessRole
from frappster.ui.components.dashboard import AdminDashboard, EmployeeDashboard, UserDashboard
from frappster.ui.components.login_screen import LoginScreen

def set_cursor_shape(shape):
    if shape == 'block':
        sys.stdout.write('\x1b[0 q')  # Block cursor
    elif shape == 'line':
        sys.stdout.write('\x1b[6 q')  # Line cursor

class AppState:
    def __init__(self) -> None:
        self.input_mode = InputMode.NAVIGATION # Normal, visual and insert modes
        self.focused_widget = None

class BankingApp:
    def __init__(self):
        self.key_bindings = KeyBindings()
        self.db_manager = DatabaseManager()
        self.auth_service = AuthService(self.db_manager)
        self.user_manager = UserManager(self.db_manager, self.auth_service)
        self.account_service = AccountService(self.db_manager, self.auth_service)
        self.transaction_service = TransactionService(self.db_manager)
        

        self.state = AppState()
        # self.state = ViState()
        self.top_bar = self.create_top_bar()
        self.bottom_bar = self.create_bottom_bar()
        self.main_content = self.create_initial_content()
        self.layout = self.create_layout()

        self.state.input_mode = InputMode.NAVIGATION
        self.set_mode('normal')

        normal_mode_filter = Condition(lambda: self.state.input_mode == InputMode.NAVIGATION)
        insert_mode_filter = Condition(lambda: self.state.input_mode == InputMode.INSERT)

        vim_bindings = load_vi_bindings()
        self.key_bindings = KeyBindings()

        @self.key_bindings.add('c-q')
        def exit_(event):
            event.app.exit()

        @self.key_bindings.add('i', filter=normal_mode_filter)
        def enter_insert_mode(event):
            # self.state.mode = 'insert'
            self.state.input_mode = InputMode.INSERT
            self.set_mode('insert')
            set_cursor_shape('line')

        @self.key_bindings.add('escape', filter=insert_mode_filter)
        def exit_insert_mode(event):
            # self.state.mode = 'normal'
            self.state.input_mode = InputMode.NAVIGATION
            self.set_mode('normal')
            set_cursor_shape('block')


        @self.key_bindings.add('n', filter=normal_mode_filter)
        def focus_next(event):
                event.app.layout.focus_next()

        @self.key_bindings.add('N', filter=normal_mode_filter)
        def focus_previous(event):
                event.app.layout.focus_previous()

        
        combinded_key_bindings = merge_key_bindings([self.key_bindings,
                                                     self.login_screen.get_key_bindings(),
                                                     # vim_bindings,
                                                     ])
        self.app = Application(layout=self.layout,
                               key_bindings=combinded_key_bindings, 
                               # editing_mode=EditingMode.VI,
                               full_screen=True)

    def create_top_bar(self):
        return Window(content=FormattedTextControl(text='BRe.inc'), height=1)

    def create_bottom_bar(self):
        return Window(content=FormattedTextControl(text='Mode: Normal'), height=1)

    def create_initial_content(self):
        self.login_screen = LoginScreen(self.handle_login, self.state) 
        layout = self.login_screen.create_layout()
        return Frame(layout)

    def show_error_dialog(self, error_message):
        def close_dialog():
            if self.app.layout.container.floats:
                self.app.layout.container.floats.pop()

            self.app.layout.focus_last()

        ok_button = Button(text="OK", handler=close_dialog)

        dialog_body = VSplit([
            Label(text=error_message, dont_extend_height=True),
            ok_button
        ], modal=True) # Disabled keybindings until closed

        dialog_frame = Frame(body=dialog_body, title="Error", style="bg:red")

        self.app.layout.container.floats.append(Float(dialog_frame))
        self.app.layout.focus(ok_button)

    def create_layout(self):
        self.root_container = FloatContainer(
            content=HSplit([
                self.top_bar,
                self.main_content,
                self.bottom_bar,
            ]),
            floats=[] # floaating elemeeents, like errors 
        )
        return Layout(self.root_container)

    def set_mode(self, mode):
        self.bottom_bar.content = FormattedTextControl(text=f'Mode: {mode}')

    def handle_login(self, credentials):
        login_id, password = credentials
        try:
            self.auth_service.login_user(login_id, password)
        except Exception as e:
            self.state.focused_widget = self.login_screen.login_id_field
            self.show_error_dialog(str(e))
            self.login_screen.password_field.text = ""
        else:
            self.dashboard_handler()

    def switch_to_login(self):
        login = self.create_initial_content()
        self.main_content = login
        self.app.layout = self.create_layout()

        self.app.invalidate()

    def refresh_ui(self):
        self.app.invalidate()

    def dashboard_handler(self):
        try:
            user = self.auth_service.get_logged_in_user()
            if user.access_role == AccessRole.ADMIN:
                # dashboard = AdminDashboard(self)
                dashboard = UserDashboard(self)

            elif user.access_role == AccessRole.EMPLOYEE:
                dashboard = EmployeeDashboard(self)

            else:
                dashboard = UserDashboard(self)

            self.switch_to_dashboard(dashboard)

        except Exception as e:
            self.show_error_dialog(str(e))

    def switch_to_dashboard(self, dashboard):
        self.app.invalidate()
        # dashboard_layout = self.main_screen.create_layout()
        dashboard_layout = dashboard.create_layout()
        self.main_content = dashboard_layout
        self.app.layout = self.create_layout()

        self.app.invalidate()

    def run(self):
        self.app.run()

