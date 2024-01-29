from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import VSplit, HSplit, Window
from prompt_toolkit.widgets import Frame, TextArea, Button


class LoginScreen:
    def __init__(self, on_login, app_state):
        self.app_state = app_state
        self.login_id_field = TextArea(prompt='Login ID: ', multiline=False)
        self.password_field = TextArea(prompt='Password: ', multiline=False, password=True)
        self.login_button = Button(text='Login', handler=lambda: on_login(self.get_credentials()))
        
        self.key_bindings = KeyBindings()
        @self.key_bindings.add('enter')
        def handle_enter(event):
                if event.app.layout.current_control == self.login_id_field:
                    event.app.layout.focus(self.password_field)
                elif event.app.layout.current_control == self.password_field:
                    on_login(self.get_credentials())

    def get_key_bindings(self):
        return self.key_bindings

    def create_layout(self):
        login_form = VSplit([
            Window(width=2),  # Left padding
            self.login_id_field,
            self.password_field,
            self.login_button,
            Window(width=2),  # Right padding
        ])

        return HSplit([
            Window(height=1),  # Top padding
            login_form,
            Window(height=1),  # Bottom padding
        ])

    def get_credentials(self):
        return self.login_id_field.text, self.password_field.text

