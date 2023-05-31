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
from server.kb_io import parse_json_kb, save_kb
from server.utils import split_list

OBJECTS_PER_SCREEN = 10
COLS_PER_SCREEN = 4

class Kboard(GridLayout, Screen):
    last_used_kb = ''
    def __init__(self, name, layout: dict, **kwargs):
        GridLayout.__init__(self, cols=COLS_PER_SCREEN, **kwargs)
        Screen.__init__(self, name=name)
        self.kb_name = name
        self.layout = layout
        self.commands_list = []
        self.buttons_list = []
        self.reload_layout()

    def reload_layout(self):
        self.clear_widgets()
        self.commands_list = self.layout['Buttons']
        self.buttons_list = []
        if len(self.commands_list) > OBJECTS_PER_SCREEN:
            print(f'KB size incorrect in "{self.kb_name}"') #TODO, add pagination
            raise ValueError

        for command in self.commands_list:
            self.add_button(command)

        if len(self.commands_list) < OBJECTS_PER_SCREEN:
            button = Button(text='Add new Button')
            self.add_widget(button)
            button.bind(on_press=self.button_add_event)

        self.settings_button = Button(text='Settings')
        self.kb_selection_button = Button(text='Select KB')
        self.add_widget(self.settings_button)
        self.add_widget(self.kb_selection_button)
        self.kb_selection_button.bind(on_press=self.kb_selection_button_press_event)
        self.settings_button.bind(on_press=self.open_setting_menu)


    def add_button(self, new_button):
        button = Button(text=new_button['name'])
        if new_button['text_color'] == []:
            button.color = self.layout['def_text_color']
        else:
            button.color = new_button['text_color']
        button.background_normal = ''
        if new_button['button_color'] == []:
            button.background_color = self.layout['def_background_color']
        else:
            button.background_color = new_button['button_color']
        self.add_widget(button)
        button.bind(on_press=partial(self.button_press_event, new_button['hotkeys']))
        self.buttons_list.append(button)

    def button_press_event(self, command_id, _):
        send_command(MainApp.sock, command_id)

    def kb_selection_button_press_event(self, _):
        MainApp.sm.current = 'KbSelection'

    def button_add_event(self, _):
        Kboard.last_used_kb = self.kb_name
        MainApp.sm.current = 'ButtonAddScreen'

    def open_setting_menu(self, _):
        Kboard.last_used_kb = self.kb_name
        MainApp.sm.current = 'SettingsScreen'

    def chroma_light_mode(self):
        ... # TODO add light (profiles) transitions



class SettingsScreen(GridLayout, Screen):
    def __init__(self, **kwargs):
        GridLayout.__init__(self, cols=COLS_PER_SCREEN, **kwargs)
        Screen.__init__(self, name='SettingsScreen')
        self.new_kb_button = Button(text='Create new kb layout')
        self.back_button = Button(text='Back')
        self.quit_button = Button(text='Quit')
        self.remove_button = Button(text='Remove Button')


        self.add_widget(self.new_kb_button)
        self.add_widget(self.back_button)
        self.add_widget(self.remove_button)
        self.add_widget(self.quit_button)

        self.new_kb_button.bind(on_press=self.create_new_kboard)
        self.back_button.bind(on_press=self.back_to_last_kb)
        self.quit_button.bind(on_press=self.close_app)
        self.remove_button.bind(on_press=self.remove_button_event)


    def back_to_last_kb(self, _):
        MainApp.sm.current = Kboard.last_used_kb

    def create_new_kboard(self, _):
        ...

    def close_app(self, _):
        quit() # TODO

    def remove_button_event(self, _):
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
        self.button_save = Button(text='Save', size_hint=(.15, .3),
                            pos_hint={'x':0.7, 'y':0})
        self.button_save.bind(on_press=self.save_event)
        self.button_back = Button(text='Back', size_hint=(.15, .3),
                            pos_hint={'x':0.85, 'y':0})
        self.button_back.bind(on_press=self.back)

        self.add_widget(self.button)
        self.add_widget(self.button_keys)
        self.add_widget(self.button_name)
        self.add_widget(self.button_back_color_button)
        self.add_widget(self.button_font_color_button)
        self.add_widget(self.button_save)
        self.add_widget(self.button_back)

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

    def back(self, _):
        MainApp.sm.current = Kboard.last_used_kb

    def save_event(self, _):
        MainApp.sm.current = Kboard.last_used_kb
        text_color = [] if self.button.color == [1, 1, 1, 1] else self.button.color
        background_color = [] if self.button.background_color == [1, 1, 1, 1] else self.button.background_color
        new_button = {
            'name': self.button.text,
            'hotkeys': self.button_keys.text,
            'text_color': text_color,
            'button_color': background_color
        }
        MainApp.kb_dict[Kboard.last_used_kb].layout['Buttons'].append(new_button)
        MainApp.kb_dict[Kboard.last_used_kb].reload_layout()
        save_kb("layouts.json", MainApp.kb_json)




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
    def __init__(self, **kwargs):
        PageLayout.__init__(self, **kwargs)
        Screen.__init__(self, name='KbSelection')
        splited_lists = split_list(list(MainApp.kb_dict.keys()), OBJECTS_PER_SCREEN)
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
        self.button.bind(on_press=self.connect_button_press_event)

    def connect_button_press_event(self, _):
        try:
            MainApp.sock = connect((self.connect_ip.text, int(self.connect_port.text)))
        except ValueError:
            ...     #TODO add button for run app without connection
        MainApp.sm.current = 'KbSelection'


class MainApp(App):
    sock = None
    sm = ScreenManager()
    kb_dict = {}
    kb_json = {}

    def build(self):
        MainApp.sm.add_widget(ConnectScreen())

        MainApp.kb_json = parse_json_kb("layouts.json")
        for kb_name, kb_value in MainApp.kb_json.items():
            MainApp.kb_dict[kb_name] = Kboard(kb_name, kb_value)
            MainApp.sm.add_widget(MainApp.kb_dict[kb_name])

        MainApp.sm.add_widget(KbSelection())
        MainApp.sm.add_widget(ButtonAddScreen())
        MainApp.sm.add_widget(ColorScreen())
        MainApp.sm.add_widget(SettingsScreen())

        return MainApp.sm

if __name__ == '__main__':
    app=MainApp()
    asyncio.run(app.async_run())
