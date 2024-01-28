from prompt_toolkit import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import Frame, TextArea
from prompt_toolkit.layout import HSplit, VSplit
from prompt_toolkit.key_binding import KeyBindings

# Create the main content area (this will be dynamic)
main_content = TextArea(text="Welcome to the Bank System")

# Left and right static sidebars
left_sidebar = Frame(TextArea(text="Left Sidebar"))
right_sidebar = Frame(TextArea(text="Right Sidebar"))

# Arrange them in a horizontal split layout
body = HSplit([
    left_sidebar,
    main_content,
    right_sidebar
])

layout = Layout(container=Frame(body))
# Create the application
key_bindings = KeyBindings()

@key_bindings.add('c-q')
def exit_(event):
    " Quit application. "
    event.app.exit()

# Add more key bindings for different actions

application = Application(layout=layout, key_bindings=key_bindings, full_screen=True)

def run():
    application.run()

if __name__ == '__main__':
    run()

