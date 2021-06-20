"""
Loading multiple instances of a widget over a period of time to prevent lag
"""

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.animation import Animation


KV = '''
GridLayout:
    id:container
    cols:5
    rows:20
'''


class MessengerApp(App):

    counter = 0

    def build(self):
        self.kv = Builder.load_string(KV)
        return self.kv

    def on_start(self):
        Clock.schedule_interval(self.btn_create,0.3)

    def btn_create(self,time):
        if self.counter<50:
            btn = Button(text = str(self.counter))
            btn.opacity = 0 # Set the opacity of the button to 0
            self.kv.add_widget(btn) # Add the button
            Animation(opacity = 1, duration = .25).start(btn) # Duration is < than clock duration
            self.counter +=1


if __name__ == '__main__':
    MessengerApp().run()
