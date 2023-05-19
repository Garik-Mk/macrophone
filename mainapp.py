from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from phone.client import connect, send_command



class Kboard(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Button(text='Hello 1'))
        self.add_widget(Button(text='World 1'))
        self.add_widget(Button(text='Hello 2'))
        self.add_widget(Button(text='World 2'))
        self.add_widget(Button(text='Hello 1'))
        self.add_widget(Button(text='World 1'))
        self.add_widget(Button(text='Hello 2'))
        self.add_widget(Button(text='World 2'))
        self.add_widget(Button(text='Hello 1'))
        self.add_widget(Button(text='World 1'))
        self.add_widget(Button(text='Hello 2'))
        self.add_widget(Button(text='World 2'))

class MyApp(App):

    def build(self):
        # if(platform == 'android'):
        #     Window.maximize()
        # else:
        #     Window.size = (620, 1024)
        return Kboard(cols=4)
    
if __name__ == '__main__':
    
    MyApp.run()
