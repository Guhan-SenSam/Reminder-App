from kivy.gesture import GestureDatabase
from kivy.uix.boxlayout import BoxLayout
from kivy.gesture import Gesture

gesture_strings = {'swipe_down':'eNp1ln1ME2cYwA9FsBtO2Fwk6Dbix8SJiEvmjGTjothWs4QKQ5hKoB8H11Hb0l5pmSs9R1ZJdlOjpwMkyh/qnMYAf2DEKK0YlbEt8ZMwIYFpsjG/cNlm2HTr2pe73r173/f+edvf73nued7nLm+OTzzgeJECl5BSY62rz6lm3JzHxYhCsk76tV9culP0i1nCDK/VwrGijs6WMpJYxlrNclHyWdMUmS2lVzhdDovHHFOaVeK2wmyvkOzmXI4axi2WiywlzJLuXgygUiPJ6bDauVhQVjQqRYoyxKASlOATdflNkWrjH4fDQkJ99M+9367k/WId8pjYtKkYdo4uv668f+OyHop9VZd/d32wtMlZRPQ/fbvynOWQn+jHHi4NHuz4iOhHF7fUbBjpI/qRfxJ/vfpSFdEPLyne0eVrJfohruXHH56eIPrBwbd8p4bvEv3t+RlpqdPbiP6m/2THo/E7sPdrNeOHMoC/fqlVX5S6l+i/u3i/t+rmCNEPJN/ZPPCMnH854NBev3eL6Pu65hzmjm4j+nNfre3eSk8Sfbc1rWHX2XSiP/60qmTP6v/lf/6Fdt/5x3TMtz5Of9f2ZifJhxpsocZpz8JEf2yiILeglyXVD3XVVrSdHNCTnk+oZ9U39vG5AuztD2aV+jqAD3fnnQ4ur4V8qCRlsleXA/zl945fCKxfCXv3Kxdtzt3A93ddFc78Cfcfqn8+/YXRCeC/F22e220W2POuBR9+fQL4a66B89vbviT6G9nDizTcIOwbf163cLQsHPO3Xl/e3NyfBftdW8y/z9WA+Q1q+zLmHWz0mBghxW12MYxdOSd0tC8XnD7RY6gZ/AhGjx1fpsx8CkuVmR7DUuPM+0RiO9sxrAzD0lHGD2EY5n68E8P0GIbpL9CJsoYxDMPU8F/DsDcisQtin9Jo3I5CNO4TAxpXXxlbE8CcKYn5KpXZy8zrRFldJprraUfjOAMa5+bROBcmt/YJmlubi8Y5A/H9xpmDV3Lld82uzC/ObBUoqzmCso9HUWYNozWsFMrYTLTnagyrwsyewbyTFsw7ZFG9B2MSMyt7izOTMhdvWGJGSsntlFhFWGHtEitXnpt3r8S2grhpENuiuh8vsTIeZaW00ovMSkDL/wLmlJky0zgrVtWVWRGNxm1SzUVmhny0RiFYZ0Dsg4ASVymxjaDRRIjpVXuTmY5CmZZSepZZAY+ydaDuc5hhctdSaC90BO2ZVs1PZu+DdSbE8kDu3xBbg9nHarAmQewdkPsXYAaJvQ3YJMRWADYBsWWqujLLUtWQ2SKwvgyx+WDNhNjUUfyamoEnHokcDYqMx2QUNJzDxriMdjMT/TrtaYldrUKi3bg9+mVNiR5Tzn9685bk'
}

#This database can compare gestures the user makes to its stored     gestures
#and tell us if the user input matches any of them.
gestures = GestureDatabase()
for name, gesture_string in gesture_strings.items():
    gesture = gestures.str_to_gesture(gesture_string)
    gesture.name = name
    gestures.add_gesture(gesture)

class GestureBox(BoxLayout):

    def __init__(self, **kwargs):
        self.register_event_type('on_swipe_down')
        super(GestureBox, self).__init__(**kwargs)

    def on_swipe_down(self):
        pass


#To recognize a gesture, you’ll need to start recording each individual event in the
#touch_down handler, add the data points for each call to touch_move , and then do the
#gesture calculations when all data points have been received in the touch_up handler.

    def on_touch_down(self, touch):
        #create an user defined variable and add the touch coordinates
        touch.ud['gesture_path'] = [(touch.x, touch.y)]
        super(GestureBox, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        touch.ud['gesture_path'].append((touch.x, touch.y))
        super(GestureBox, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if 'gesture_path' in touch.ud:
            #create a gesture object
            gesture = Gesture()
            #add the movement coordinates
            gesture.add_stroke(touch.ud['gesture_path'])
            #normalize so thwu willtolerate size variations
            gesture.normalize()
            #minscore to be attained for a match to be true
            match = gestures.find(gesture, minscore=0.4)
            if match:
                print("{} happened".format(match[1].name))
                self.dispatch('on_{}'.format(match[1].name))
        super(GestureBox, self).on_touch_up(touch)
