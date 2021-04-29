from kivy.lang import Builder
from kivymd.app import MDApp

root_kv = """
#:import CardStack

CardStack:
    size:800,800
    pos_hint:
"""


class MainApp(MDApp):
    def build(self):
        self.root = Builder.load_string(root_kv)


if __name__ == "__main__":
    MainApp().run()
