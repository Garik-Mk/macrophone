from functools import partial
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from phone.client import connect, send_command
from server.mkb_io import read_file, parse_commands


class Kboard(GridLayout, Screen):
    sock = None
    def __init__(self, mkb_path, **kwargs):
        super().__init__(**kwargs)
        Screen.__init__(self, name='Kboard')

        self.commands = parse_commands(read_file(mkb_path))
        self.buttons_list = []

        for i in range(12):
            text='Placeholder'
            if str(i) in self.commands.keys():
                text = self.commands[str(i)][1]
            self.buttons_list.append(Button(text=text))
            self.add_widget(self.buttons_list[i])
            self.buttons_list[i].bind(on_press=partial(self.button_press_event, i))

    def button_press_event(self, command_id, _):
        send_command(Kboard.sock, command_id)


class ConnectScreen(GridLayout, Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Screen.__init__(self, name='Connection_screen')
        self.cols = 3
        self.connect_ip = TextInput(multiline=False, hint_text='IP')
        self.add_widget(self.connect_ip)
        self.connect_port = TextInput(multiline=False, hint_text='Port')
        self.add_widget(self.connect_port)
        self.button = Button(text='Connect')
        self.add_widget(self.button)
        self.button.bind(on_press=self.button_press_event)

    def button_press_event(self, _):
        try:
            Kboard.sock = connect((self.connect_ip.text, int(self.connect_port.text)))
        except ConnectionRefusedError:
            ...     #TODO
        MainApp.sm.current = 'Kboard'


class MainApp(App):
    sm = ScreenManager()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        MainApp.sm.add_widget(ConnectScreen())
        MainApp.sm.add_widget(Kboard(mkb_path = '/kb_configs/test_keyboard.mkb', cols=4))
        return MainApp.sm

if __name__ == '__main__':
    app=MainApp()
    app.run()
