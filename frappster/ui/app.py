import sys

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Float, FloatContainer, HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Button, Frame, Label, TextArea

from frappster.database import DatabaseManager
from frappster.auth import AuthService
from frappster.services import UserManager, AccountService, TransactionService
from frappster.ui.components.login_screen import LoginScreen
from frappster.ui.components.main_screen import MainScreen

def set_cursor_shape(shape):
    if shape == 'block':
        sys.stdout.write('\x1b[0 q')  # Block cursor
    elif shape == 'line':
        sys.stdout.write('\x1b[6 q')  # Line cursor

class AppState:
    def __init__(self) -> None:
        self.mode = 'normal' # Normal, visual and insert modes
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
        self.top_bar = self.create_top_bar()
        self.bottom_bar = self.create_bottom_bar()
        self.main_screen = MainScreen()
        self.main_content = self.create_initial_content()
        self.layout = self.create_layout()
        self.key_bindings = KeyBindings()

        @self.key_bindings.add('c-q')
        def exit_(event):
            event.app.exit()

        @self.key_bindings.add('i')
        def enter_insert_mode(event):
            self.state.mode = 'insert'
            self.set_mode('insert')
            set_cursor_shape('line')

        @self.key_bindings.add('escape')
        def exit_insert_mode(event):
            self.state.mode = 'normal'
            self.set_mode('normal')
            set_cursor_shape('block')

        @self.key_bindings.add('n')
        def focus_next(event):
            if self.state.mode == 'normal':
                event.app.layout.focus_next()

        @self.key_bindings.add('N')
        def focus_previous(event):
            if self.state.mode == 'normal':
                event.app.layout.focus_previous()

        
        combinded_key_bindings = merge_key_bindings([self.key_bindings, self.login_screen.get_key_bindings()])
        self.app = Application(layout=self.layout, key_bindings=combinded_key_bindings, full_screen=True)

    def create_top_bar(self):
        return Window(content=FormattedTextControl(text='Top Bar Content'), height=1)

    def create_bottom_bar(self):
        return Window(content=FormattedTextControl(text='Bottom Bar Content (Mode: Normal)'), height=1)

    def create_initial_content(self):
        self.login_screen = LoginScreen(self.handle_login) 
        layout = self.login_screen.create_layout()
        return Frame(layout)

    def show_error_dialog(self, error_message):
        def close_dialog():
            if self.app.layout.container.floats:
                self.app.layout.container.floats.pop()

            self.app.layout.focus(self.state.focused_widget)

        ok_button = Button(text="OK", handler=close_dialog)

        dialog_body = VSplit([
            Label(text=error_message, dont_extend_height=True),
            ok_button
        ])

        dialog_frame = Frame(body=dialog_body, title="Error", style="bg:red")

        self.app.layout.container.floats.append(Float(dialog_frame))
        self.state.focused_widget = dialog_frame

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
        self.bottom_bar.content = FormattedTextControl(text=f'Bottom Bar Content (Mode: {mode})')

    def handle_login(self, credentials):
        login_id, password = credentials
        try:
            self.auth_service.login_user(login_id, password)
        except Exception as e:
            self.state.focused_widget = self.login_screen.login_id_field
            self.show_error_dialog(str(e))
            # self.switch_to_login()
            # self.switch_to_dashboard()
            # self.login_screen.login_id_field.text = ""
            self.login_screen.password_field.text = ""
        else:
            self.switch_to_dashboard()

    def switch_to_login(self):
        login = self.create_initial_content()
        self.main_content = login
        self.app.layout = self.create_layout()

        self.app.invalidate()

    def switch_to_dashboard(self):
        dashboard_layout = self.main_screen.create_layout()
        self.main_content = dashboard_layout
        self.app.layout = self.create_layout()

        self.app.invalidate()

    def run(self):
        self.app.run()

