from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

from kivymd.uix.card import MDCard

class tempstuff(BoxLayout):
    pass

class Mainapp(MDApp):

    def build(self):
        Builder.load_file('test.kv')
        return tempstuff()

Mainapp().run()
