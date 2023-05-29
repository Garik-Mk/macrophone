from functools import partial
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.colorpicker import ColorPicker
from phone.client import connect, send_command
from server.mkb_io import parse_mkb, Command
from server.utils import split_list

OBJECTS_PER_SCREEN = 10

class Kboard(GridLayout, Screen):

    def __init__(self, name, commands: list[Command], **kwargs):
        GridLayout.__init__(self, cols=4, **kwargs)
        Screen.__init__(self, name=name)
        print(name)
        self.commands_list = commands
        if len(self.commands_list) > 10:
            print('KB size incorrect') #TODO, add pagination
            raise ValueError
        self.buttons_list = []

        for command in self.commands_list:
            button = Button(text=command.name)
            self.buttons_list.append(button)
            # button.background_normal = ''
            button.color = command.font_color
            button.background_color = command.background_color
            button.bind(on_press=partial(self.button_press_event, command.keys))
            self.add_widget(button)

        settings_button = Button(text='Settings')
        kb_selection_button = Button(text='Select KB')
        self.add_widget(settings_button)
        self.add_widget(kb_selection_button)
        kb_selection_button.bind(on_press=self.kb_selection_button_press_event)


    def button_press_event(self, command_id, _):
        send_command(MainApp.sock, command_id)

    def kb_selection_button_press_event(self, _):
        MainApp.sm.current = 'KbSelection'



class SettingsScreen(GridLayout, Screen):
    def __init__(self, **kwargs):
        GridLayout.__init__(self, **kwargs)
        Screen.__init__(self, name='SettingsScreen')

    def create_new_kboard(self):
        ...



class ButtonAddScreen(GridLayout, Screen):
    def __init__(self, **kwargs):
        GridLayout.__init__(self, **kwargs)
        Screen.__init__(self, name='ButtonAddScreen')



class ColorScreen(BoxLayout, Screen):
    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)
        Screen.__init__(self, name='ColorScreen')
        self.clr_picker = ColorPicker()
        self.clr_picker.bind(color=self.on_color)
        self.add_widget(self.clr_picker)
        self.button = Button(text='Select Color')
        self.add_widget(self.button)
        self.button.bind(on_press=self.on_button)

    def on_color(self, _, value):
        print("RGBA = ", str(value))
        self.button.background_normal = ''
        self.button.color = [1 - i for i in value[:3]]
        print([1 - i for i in value])
        self.button.background_color = value

    def on_button(self, instance):
        print('Color selected')



class KbSelection(PageLayout, Screen):
    def __init__(self, kb_names_list, **kwargs):
        PageLayout.__init__(self, **kwargs)
        Screen.__init__(self, name='KbSelection')
        splited_lists = split_list(kb_names_list, OBJECTS_PER_SCREEN)
        for each_list in splited_lists:
            self.add_widget(self.KbSelectionPage(kb_name_list=each_list))

    class KbSelectionPage(GridLayout):
        def __init__(self, kb_name_list, **kwargs):
            super().__init__(cols=4, **kwargs)
            self.buttons_list = []
            for name in kb_name_list:
                self.buttons_list.append(Button(text=str(name)))
                self.add_widget(self.buttons_list[-1])
                self.buttons_list[-1].bind(on_press=partial(self.button_press_event, str(name)))

        def button_press_event(self, name, _):
            MainApp.sm.current = name
            print(f'Kb swtiched to {name}')


class ConnectScreen(GridLayout, Screen):
    def __init__(self, **kwargs):
        GridLayout.__init__(self, **kwargs)
        Screen.__init__(self, name='ConnectScreen')
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
            MainApp.sock = connect((self.connect_ip.text, int(self.connect_port.text)))
        except ConnectionRefusedError:
            ...     #TODO
        MainApp.sm.current = 'KbSelection'




class MainApp(App):
    sock = None
    sm = ScreenManager()
    kb_dict = {}
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        MainApp.sm.add_widget(ConnectScreen())

        kb_dict_from_mkb = parse_mkb(r"server\kb_configs\new_format.mkb")
        kb_names_list_for_selection = []
        for kb_name, kb_value  in kb_dict_from_mkb.items():
            kb_names_list_for_selection.append(kb_name)
            MainApp.kb_dict[kb_name] = Kboard(name=kb_name, commands=kb_value)
            MainApp.sm.add_widget(MainApp.kb_dict[kb_name])

        MainApp.sm.add_widget(KbSelection(kb_names_list=kb_names_list_for_selection))

        return MainApp.sm

if __name__ == '__main__':
    app=MainApp()
    app.run()
