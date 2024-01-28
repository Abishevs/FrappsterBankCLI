from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Frame, TextArea

class MainScreen:
    def __init__(self) -> None:
        self.text_area = Window(content=FormattedTextControl(text='Welcome frappster bank! Enhanced with Vim motions ;)'))

    def create_layout(self):
        return Frame(HSplit([self.text_area]), title="CLI-BankingSYteme")
