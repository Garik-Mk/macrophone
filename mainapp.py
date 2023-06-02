from functools import partial
import asyncio
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.colorpicker import ColorPicker
from phone.client import connect, send_command
from server.kb_io import parse_json_kb, save_kb
from server.utils import split_list


class Kboard(GridLayout, Screen):
    last_used_kb = ''
    def __init__(self, name, layout: dict, **kwargs):
        GridLayout.__init__(self, cols=layout['cols'], **kwargs)
        Screen.__init__(self, name=name)
        self.kb_name = name
        self.layout = layout
        self.commands_list = []
        self.buttons_list = []
        self.objects_per_screen = layout['cols'] * layout['rows'] - 2
        self.reload_layout()

    def reload_layout(self):
        self.clear_widgets()
        self.commands_list = self.layout['Buttons']
        self.buttons_list = []
        if len(self.commands_list) > self.objects_per_screen:
            print(f'KB size incorrect in "{self.kb_name}"') #TODO, add pagination
            raise ValueError

        for new_button in self.commands_list:
            self.add_button(new_button)
            self.button_bind(new_button['hotkeys'])

        if len(self.commands_list) < self.objects_per_screen:
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
        self.button = Button(
            text=new_button['name'],
            background_normal = '',
            color=self.layout['def_text_color'] if not\
                  new_button['text_color'] else new_button['text_color'],
            background_color=self.layout['def_background_color'] \
                if not new_button['button_color'] else new_button['button_color']
        )
        self.add_widget(self.button)
        self.buttons_list.append(self.button)
        return self.button

    def button_bind(self, hotkeys):
        self.button.bind(on_press=partial(self.button_press_event, hotkeys))

    def button_press_event(self, hotkeys, _):
        print('Command:', hotkeys)
        if not MainApp.sock is None:
            send_command(MainApp.sock, hotkeys)

    def kb_selection_button_press_event(self, _):
        MainApp.sm.current = KbSelection.last_used_page

    def button_add_event(self, _):
        Kboard.last_used_kb = self.kb_name
        MainApp.sm.current = 'ButtonAddScreen'

    def open_setting_menu(self, _):
        Kboard.last_used_kb = self.kb_name
        MainApp.sm.current = 'ButtonSettingsScreen'

    def chroma_light_mode(self):
        ... # TODO add light (profiles) transitions


class ButtonSettingsScreen(GridLayout, Screen):
    editable_button = Button(text='Dummy')
    def __init__(self, **kwargs):
        GridLayout.__init__(self, cols=4, **kwargs)
        Screen.__init__(self, name='ButtonSettingsScreen')

        self.back_button = Button(text='Back')
        self.quit_button = Button(text='Quit')
        self.edit_button = Button(text='Edit Button')

        self.add_widget(self.back_button)
        self.add_widget(self.edit_button)
        self.add_widget(self.quit_button)

        self.back_button.bind(on_press=self.back_to_last_kb)
        self.quit_button.bind(on_press=self.close_app)
        self.edit_button.bind(on_press=self.select_button)

    def back_to_last_kb(self, _):
        MainApp.sm.current = Kboard.last_used_kb

    def close_app(self, _):
        quit()


    def edit_button_event(self, instance):
        MainApp.kb_dict[Kboard.last_used_kb].buttons_list = self.save_buttons_list
        MainApp.kb_dict[Kboard.last_used_kb].reload_layout()
        ButtonSettingsScreen.editable_button = instance
        MainApp.sm.current = 'ButtonEditScreen'
        MainApp.editor.run_editor()

    def select_button(self, _):
        self.save_buttons_list = MainApp.kb_dict[Kboard.last_used_kb].buttons_list.copy()
        MainApp.kb_dict[Kboard.last_used_kb].clear_widgets()
        for new_button in MainApp.kb_dict[Kboard.last_used_kb].commands_list:
            button = MainApp.kb_dict[Kboard.last_used_kb].add_button(new_button)
            button.bind(on_press=self.edit_button_event)
        MainApp.sm.current = Kboard.last_used_kb


class ButtonAddScreen(Screen):
    def __init__(self, name='ButtonAddScreen', **kwargs):
        # FloatLayout.__init__(self, **kwargs)
        Screen.__init__(self, name=name, **kwargs)

        self.button = Button(text='Hello world', size_hint=(.3, .3),
                        pos_hint={'center_x':0.5, 'center_y':0.5})

        self.button_back_color_button = Button(text='Select Background color', size_hint=(.3, .3),
                                            pos_hint={'x':0.7, 'y':0.7})
        self.button_back_color_button.bind(on_press=self.bg_color_select_event)
        self.button_font_color_button = Button(text='Select Font color', size_hint=(.3, .3),
                                            pos_hint={'x':0.7, 'y':0.4})
        self.button_font_color_button.bind(on_press=self.ft_color_select_event)

        self.button_name = TextInput(
            multiline=False,
            hint_text='Name',
            size_hint=(.3, .5),
            pos_hint={'x':0, 'y':0.5}
        )
        self.button_name.bind(text=self.on_text_event)
        self.button_keys = TextInput(
            multiline=False,
            hint_text='Hotkey Combination',
            size_hint=(.3, .5),
            pos_hint={'x':0, 'y':0}
        )
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

    def bg_color_select_event(self, _, name='ButtonAddScreen'):
        MainApp.sm.current = 'ColorScreen'
        ColorScreen.requester = name
        asyncio.ensure_future(self.wait_for_switchback(True, name))

    def ft_color_select_event(self, _,  name='ButtonAddScreen'):
        MainApp.sm.current = 'ColorScreen'
        ColorScreen.requester = name
        asyncio.ensure_future(self.wait_for_switchback(False, name))

    async def wait_for_switchback(self, change_bg: bool, name='ButtonAddScreen'):
        while MainApp.sm.current != name:
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
        background_color = [] if self.button.background_color\
              == [1, 1, 1, 1] else self.button.background_color
        new_button = {
            'name': self.button.text,
            'hotkeys': self.button_keys.text,
            'text_color': text_color,
            'button_color': background_color
        }
        MainApp.kb_dict[Kboard.last_used_kb].layout['Buttons'].append(new_button)
        MainApp.kb_dict[Kboard.last_used_kb].reload_layout()
        self.button_name.text = ''
        self.button_keys.text = ''
        self.button.text = 'Hello World!'
        save_kb("layouts.json", MainApp.kb_json)


class ButtonEditScreen(ButtonAddScreen):
    def __init__(self, **kwargs):
        super().__init__(name='ButtonEditScreen', **kwargs)
        self.remove_button = Button(text='Remove Button', size_hint=(.3, .2),
                                            pos_hint={'center_x':0.5, 'center_y':.1})
        self.button_back_color_button.unbind(on_press=self.bg_color_select_event)
        self.button_font_color_button.unbind(on_press=self.ft_color_select_event)
        self.button_back_color_button.bind(
            on_press=partial(self.bg_color_select_event, name='ButtonEditScreen')
        )
        self.button_font_color_button.bind(
            on_press=partial(self.ft_color_select_event, name='ButtonEditScreen')
        )
        self.remove_button.bind(on_press=self.del_button)
        self.add_widget(self.remove_button)

    def run_editor(self):
        editable_button = ButtonSettingsScreen.editable_button
        self.button.background_normal = ''
        self.button.text = editable_button.text
        self.button.background_color = editable_button.background_color
        self.button.color = editable_button.color
        self.button_name.text = editable_button.text
        # self.button_keys =

    def save_event(self, _):
        ...

    def del_button(self, _):
        ...


class ColorScreen(BoxLayout, Screen):
    last_color_selected = [1, 1, 1, 1]
    requester = ''
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
        MainApp.sm.current = ColorScreen.requester


class LayoutSettings(GridLayout, Screen):
    def __init__(self, **kwargs):
        GridLayout.__init__(self, cols=4)
        Screen.__init__(self, name='LayoutSettings', **kwargs)
        self.button_quit = Button(text='Quit')
        self.button_quit.bind(on_press=quit)
        self.button_back = Button(text='Back')
        self.button_back.bind(on_press=self.back)
        self.button_create_new_layout = Button(text='Create new Layout')
        self.button_create_new_layout.bind(on_press=self.switch_layout_creator)

        self.add_widget(self.button_create_new_layout)
        self.add_widget(self.button_back)
        self.add_widget(self.button_quit)

    def back(self, _):
        MainApp.sm.current = KbSelection.last_used_page

    def switch_layout_creator(self, _):
        MainApp.sm.current = 'NewLayoutCreator'


class NewLayoutCreator(Screen):
    def __init__(self, **kwargs):
        super().__init__(name='NewLayoutCreator', **kwargs)
        self.layout_name = TextInput(
            multiline=False,
            hint_text='Name',
            size_hint=(.33333, .5),
            pos_hint={'x':0, 'y':0.5}
        )
        self.cols_count = TextInput(
            multiline=False,
            hint_text='Cols, default = 4',
            size_hint=(.33333, .5),
            pos_hint={'x':0.33333, 'y':0.5}
        )
        self.rows_count = TextInput(
            multiline=False,
            hint_text='Rows, default = 3',
            size_hint=(.33333, .5),
            pos_hint={'x':0.66666, 'y':0.5}
        )
        self.button_save = Button(text='Save', size_hint=(.16666, .5),
                            pos_hint={'x':0.6666, 'y':0})
        self.button_back = Button(text='Back', size_hint=(.16666, .5),
                            pos_hint={'x':0.83333, 'y':0})
        self.color_select = Button(text='Select Button Color', size_hint=(.33333, .5),
                            pos_hint={'x':0, 'y':0})
        self.text_color_select = Button(text='Select Text Color', size_hint=(.33333, .5),
                            pos_hint={'x':.33333, 'y':0})

        self.button_save.bind(on_press=self.save_event)
        self.button_back.bind(on_press=self.back)
        self.color_select.bind(on_press=partial(self.select_color, True))
        self.text_color_select.bind(on_press=partial(self.select_color, False))

        self.add_widget(self.button_save)
        self.add_widget(self.button_back)
        self.add_widget(self.color_select)
        self.add_widget(self.text_color_select)
        self.add_widget(self.layout_name)
        self.add_widget(self.cols_count)
        self.add_widget(self.rows_count)

    def select_color(self, change_bg, _):
        MainApp.sm.current = 'ColorScreen'
        ColorScreen.requester = 'NewLayoutCreator'
        asyncio.ensure_future(self.wait_for_switchback(change_bg))

    async def wait_for_switchback(self, change_bg):
        while MainApp.sm.current != 'NewLayoutCreator':
            await asyncio.sleep(0.1)
        self.update_color(change_bg)

    def update_color(self, change_bg):
        if change_bg:
            self.color_select.background_normal = ''
            self.color_select.background_color = ColorScreen.last_color_selected
            self.text_color_select.background_normal = ''
            self.text_color_select.background_color = ColorScreen.last_color_selected
        else:
            self.text_color_select.color = ColorScreen.last_color_selected
            self.color_select.color = ColorScreen.last_color_selected


    def save_event(self, _):
        if self.layout_name.text == '':
            print('No name specified')
        else:
            new_layout = {
                'cols': 4 if not self.cols_count.text else self.cols_count.text,
                'rows': 3 if not self.cols_count.text else self.cols_count.text,
                'def_background_color': self.color_select.background_color,
                'def_text_color': self.text_color_select.color,
                'Buttons': []
            }
            name = self.layout_name.text
            MainApp.kb_json[name] = new_layout
            new_kb = Kboard(name, new_layout)
            MainApp.sm.add_widget(new_kb)
            MainApp.kb_dict[name] = new_kb
            last_page = KbSelection.all_pages[-1]
            if len(last_page.buttons_list) < 4:
                counter = len(last_page.buttons_list)
                new_button = Button(text=str(name), size_hint=(.18, 1),\
                                        pos_hint={'x':0.14+counter%4*0.18, 'y':0})
                new_button.bind(on_press=self.kb_selection)
                if self.color_select.background_color != [1, 1, 1, 1]:
                    new_button.background_normal = ''
                new_button.background_color = self.color_select.background_color
                new_button.color = self.text_color_select.color
                last_page.buttons_list.append(new_button)
                last_page.add_widget(new_button)
            else:
                new_page = KbSelectionPage(len(KbSelection.all_pages), [name])
                KbSelection.all_pages.append(new_page)
                KbSelection.max_screen_counter += 1
                MainApp.sm.add_widget(new_page)

            save_kb("layouts.json", MainApp.kb_json)
            MainApp.sm.current = KbSelection.last_used_page
    
    def kb_selection(self, _):
        MainApp.sm.current = self.layout_name.text


    def back(self, _):
        MainApp.sm.current = 'LayoutSettings'



class KbSelection(Screen):
    last_used_page = 'layoutScreen0'
    max_screen_counter = -1
    all_pages = []
    def __init__(self, **kwargs):
        Screen.__init__(self, name='KbSelection', **kwargs)
        kb_names_list = ['LayoutSettings']
        kb_names_list += list(MainApp.kb_dict.keys())
        splited_lists = split_list(kb_names_list, 4)
        for i, each_list in enumerate(splited_lists):
            page = KbSelectionPage(i, kb_name_list=each_list)
            KbSelection.all_pages.append(page)
            MainApp.sm.add_widget(page)


class KbSelectionPage(Screen):
    def __init__(self, kb_id: int, kb_name_list: list[str], **kwargs):
        super().__init__(name='layoutScreen'+str(kb_id), **kwargs)
        KbSelection.max_screen_counter += 1
        self.buttons_list = []
        for i, name in enumerate(kb_name_list):
            self.buttons_list.append(
                Button(text=str(name),
                size_hint=(.18, 1),
                pos_hint={'x':0.14+i%4*0.18, 'y':0})
            )
            if name != 'LayoutSettings':
                color = MainApp.kb_json[name]['def_background_color']
                if color != [1, 1, 1, 1]:
                    self.buttons_list[-1].background_normal = ''
                    self.buttons_list[-1].background_color = color
            self.buttons_list[-1].bind(on_press=partial(self.button_press_event, str(name)))
            self.add_widget(self.buttons_list[-1])

        self.perv_button = (Button(text='<', size_hint=(.14, 1), pos_hint={'x':0, 'y':0}))
        self.next_button = (Button(text='>', size_hint=(.14, 1), pos_hint={'x':0.86, 'y':0}))
        self.perv_button.bind(on_press=partial(self.switch_next_screen, kb_id-1, transition='right'))
        self.next_button.bind(on_press=partial(self.switch_next_screen, kb_id+1, transition='left'))
        self.add_widget(self.perv_button)
        self.add_widget(self.next_button)
        # self.layout_settings_button = Button(text='Settings')
        # self.add_widget(self.layout_settings_button)

    def switch_next_screen(self, screen_id: int, _, transition: str):
        MainApp.sm.transition.direction = transition
        if screen_id > KbSelection.max_screen_counter or screen_id < 0:
            print('Screen not found')
        else:
            KbSelection.last_used_page = 'layoutScreen'+str(screen_id)
            MainApp.sm.current = 'layoutScreen'+str(screen_id)

    def button_press_event(self, name: str, _):
        MainApp.sm.current = name
        print(f'Kb swtiched to {name}')


class ConnectScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, name='ConnectScreen', **kwargs)
        self.connect_ip = TextInput(multiline=False, hint_text='IP', size_hint=(.3333, 1), pos_hint={'x':0, 'y':0})
        self.connect_port = TextInput(multiline=False, hint_text='Port', size_hint=(.3333, 1), pos_hint={'x':0.3333, 'y':0})
        self.connect_button = Button(text='Connect', size_hint=(.3333, 0.5), pos_hint={'x':0.6666, 'y':0.5})
        self.run_button = Button(text='Run without connection', size_hint=(.3333, 0.5), pos_hint={'x':0.6666, 'y':0})
        self.connect_button.bind(on_press=self.connect_button_press_event)
        self.run_button.bind(on_press=self.run_without_connection)
        self.add_widget(self.connect_port)
        self.add_widget(self.connect_ip)
        self.add_widget(self.connect_button)
        self.add_widget(self.run_button)

    def connect_button_press_event(self, _):
        try:
            MainApp.sock = connect((self.connect_ip.text, int(self.connect_port.text)))
        except ValueError:
            print('Connection Failed')

    def run_without_connection(self, _):
        MainApp.sm.current = KbSelection.last_used_page


class MainApp(App):
    sock = None
    sm = ScreenManager()
    editor = ButtonEditScreen()
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
        MainApp.sm.add_widget(ButtonSettingsScreen())
        MainApp.sm.add_widget(LayoutSettings())
        MainApp.sm.add_widget(NewLayoutCreator())
        MainApp.sm.add_widget(MainApp.editor)

        return MainApp.sm

if __name__ == '__main__':
    app=MainApp()
    asyncio.run(app.async_run())
