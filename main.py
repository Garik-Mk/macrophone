from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.core.window import Window
from kivy.utils import platform

class LoginScreen(GridLayout):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.cols = 2
        layout = BoxLayout(padding=10)
        button = Button(text='My first button')
        layout.add_widget(button)
        self.add_widget(layout)
        self.username = TextInput(multiline=False)
        self.add_widget(self.username)
        self.add_widget(Label(text='password'))
        self.password = TextInput(password=True, multiline=False)
        self.add_widget(self.password)


class Kboard(StackLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spacing = 50
        self.add_widget(Button(text='My 1 button', width=100, size_hint=(None, 0.15)))
        self.add_widget(Button(text='My 2 button', width=100, size_hint=(None, 0.15)))
        self.add_widget(Button(text='My 3 button', width=100, size_hint=(None, 0.15)))
        self.add_widget(Button(text='My 4 button', width=100, size_hint=(None, 0.15)))
        self.add_widget(Label(text="screen sizes= "+ str(Window.size)))

class MyApp(App):

    def build(self):
        # if(platform == 'android'):
        #     Window.maximize()
        # else:
        #     Window.size = (620, 1024)
        return Kboard()


if __name__ == '__main__':
    MyApp().run()