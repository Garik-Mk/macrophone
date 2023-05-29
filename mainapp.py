from functools import partial
import asyncio
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
    last_used_kb = ''
    def __init__(self, name, commands: list[Command], **kwargs):
        GridLayout.__init__(self, cols=4, **kwargs)
        Screen.__init__(self, name=name)
        self.kb_name = name
        self.commands_list = commands
        if len(self.commands_list) > 10:
            print(f'KB size incorrect in "{name}"') #TODO, add pagination
            raise ValueError
        self.buttons_list = []

        for command in self.commands_list:
            button = Button(text=command.name)
            self.buttons_list.append(button)
            button.color = command.font_color
            button.background_color = command.background_color
            button.bind(on_press=partial(self.button_press_event, command.keys))
            self.add_widget(button)

        if len(self.commands_list) < 10:
            button = Button(text='Add new Button')
            button.bind(on_press=self.button_add_event)
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

    def button_add_event(self, _):
        Kboard.last_used_kb = self.kb_name
        MainApp.sm.current = 'ButtonAddScreen'

    def chroma_light_mode(self):
        ... # TODO add light (profiles) transitions



class SettingsScreen(GridLayout, Screen):
    def __init__(self, **kwargs):
        GridLayout.__init__(self, **kwargs)
        Screen.__init__(self, name='SettingsScreen')

    def create_new_kboard(self):
        ...


class ButtonAddScreen(Screen):
    def __init__(self, **kwargs):
        # FloatLayout.__init__(self, **kwargs)
        Screen.__init__(self, name='ButtonAddScreen', **kwargs)
        self.button = Button(text='Hello world', size_hint=(.3, .3),
                        pos_hint={'center_x':0.5, 'center_y':0.5})

        self.button_back_color_button = Button(text='Select Background color', size_hint=(.3, .3),
                                            pos_hint={'x':0.7, 'y':0.7})
        self.button_back_color_button.bind(on_press=self.bg_color_select_event)
        self.button_font_color_button = Button(text='Select Font color', size_hint=(.3, .3),
                                            pos_hint={'x':0.7, 'y':0.4})
        self.button_font_color_button.bind(on_press=self.ft_color_select_event)

        self.button_name = TextInput(multiline=False, hint_text='Name', size_hint=(.3, .5), pos_hint={'x':0, 'y':0.5})
        self.button_name.bind(text=self.on_text_event)
        self.button_keys = TextInput(multiline=False, hint_text='Hotkey Combination', size_hint=(.3, .5), pos_hint={'x':0, 'y':0})
        self.button_save = Button(text='Save', size_hint=(.3, .3),
                            pos_hint={'x':0.7, 'y':0})
        self.button_save.bind(on_press=self.save_event)

        self.add_widget(self.button)
        self.add_widget(self.button_keys)
        self.add_widget(self.button_name)
        self.add_widget(self.button_back_color_button)
        self.add_widget(self.button_font_color_button)
        self.add_widget(self.button_save)

    def bg_color_select_event(self, _):
        MainApp.sm.current = 'ColorScreen'
        asyncio.ensure_future(self.wait_for_switchback(True)) 

    def ft_color_select_event(self, _):
        MainApp.sm.current = 'ColorScreen'
        asyncio.ensure_future(self.wait_for_switchback(False)) 

    async def wait_for_switchback(self, change_bg: bool):
        print("HEREIAM")
        while MainApp.sm.current != 'ButtonAddScreen':
            await asyncio.sleep(0.1)
        self.update_color(change_bg)
    
    def update_color(self, change_bg):
        if change_bg:
            self.button.background_normal = ''
            self.button.background_color = ColorScreen.last_color_selected
        else:
            self.button.color = ColorScreen.last_color_selected

    def on_text_event(self, _, value):
        self.button.text = value

    def save_event(self, _):
        MainApp.sm.current = Kboard.last_used_kb
        # TODO add save functionality



class ColorScreen(BoxLayout, Screen):
    last_color_selected = [1, 1, 1, 1]
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
        self.button.background_normal = ''
        self.button.color = [1 - i for i in value[:3]]
        self.button.background_color = value

    def on_button(self, _):
        print('Color selected')
        ColorScreen.last_color_selected = self.button.background_color
        MainApp.sm.current = 'ButtonAddScreen'



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

        kb_dict_from_mkb = parse_mkb("server/kb_configs/new_format.mkb")
        kb_names_list_for_selection = []
        for kb_name, kb_value  in kb_dict_from_mkb.items():
            kb_names_list_for_selection.append(kb_name)
            MainApp.kb_dict[kb_name] = Kboard(name=kb_name, commands=kb_value)
            MainApp.sm.add_widget(MainApp.kb_dict[kb_name])

        MainApp.sm.add_widget(KbSelection(kb_names_list=kb_names_list_for_selection))
        MainApp.sm.add_widget(ButtonAddScreen())
        MainApp.sm.add_widget(ColorScreen())

        return MainApp.sm

if __name__ == '__main__':
    app=MainApp()
    asyncio.run(app.async_run())
