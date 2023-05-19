from functools import partial
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from phone.client import connect, send_command
from server.mkb_io import read_file, parse_commands 

class Kboard(GridLayout):

    def __init__(self, mkb_path, sock, **kwargs):
        super().__init__(**kwargs)

        self.commands = parse_commands(read_file(mkb_path))
        self.buttons_list = []
        self.sock = sock

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
        connect_ip = '192.168.1.212' # Temp, for testing. Ip and port menu will be addede TODO
        connect_port = int(input())
        sock = connect((connect_ip, connect_port))
        return Kboard(mkb_path=r'server\kb_configs\test_keyboard.mkb', sock=sock, cols=4)

if __name__ == '__main__':

    MyApp.run()
