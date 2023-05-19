from functools import partial
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from phone.client import connect, send_command
from server.mkb_io import read_file, parse_commands 

class Kboard(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #TODO move to some utility function/method
        connect_ip = '192.168.1.212' # Temp, for testing. Ip and port menu will be added TODO
        connect_port = int(input())
        self.sock = connect((connect_ip, connect_port))
        mkb_path = r'\server\kb_configs\test_keyboard.mkb'
        self.commands = parse_commands(read_file(mkb_path))
        self.buttons_list = []

        for i in range(12):
            text='Placeholder'
            if str(i) in self.commands.keys():
                text = self.commands[str(i)][1]
            self.buttons_list.append(Button(text=text))
            self.add_widget(self.buttons_list[i])
            self.buttons_list[i].bind(partial(self.button_press_event, i))
    
    def button_press_event(self, command_id):
        send_command(self.sock, command_id)


class MyApp(App):

    def build(self):
        return Kboard(cols=4)

if __name__ == '__main__':

    MyApp.run()
