from kivy.config import Config
# Config.set('modules', 'monitor', ' ')
# Config.set('graphics', 'maxfps', '100')
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.toast import toast
from kivymd.uix.button import MDIconButton
from kivymd.uix.picker import MDTimePicker, MDDatePicker
from kivymd.uix.chip import MDChipContainer, MDChip
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineAvatarIconListItem

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import platform
from kivy.uix.screenmanager import Screen, ScreenManager, CardTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.recycleview import RecycleView
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.behaviors import DragBehavior
from kivy.properties import BooleanProperty,StringProperty
from kivy.metrics import dp
from kivy.uix.label import Label

from theming import ThemeManager
from toolbar import AKToolbarLayout

from functools import partial
import sqlite3
import collections
import plyer
import threading

import time
from datetime import datetime,date,timedelta
import random
import re

if platform == 'android':
    from reminderscheduler import ReminderScheduler
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    mActivity = PythonActivity.mActivity

connection = sqlite3.connect('reminder.db')
mycursor = connection.cursor()

class MainViewHandler():

    def all_lists_loader(self,*args):
        global all_lists
        mycursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        data = mycursor.fetchall()
        all_lists = []
        for a in data:
            if a[0] == 'sqlite_sequence' or a[0] == 'android_metadata':
                pass
            else:
                all_lists.append(a[0])
        all_lists.sort()
        if len(all_lists) == 0: #There are no lists so we show special screen
            try:# No need to create the variables again if they exist
                a = Mainscreenvar.ids.ele1.size
                MainViewHandler.no_lists(self)
            except:
                MainViewHandler.card_setters(self)
                MainViewHandler.no_lists(self)
        else:
            MainViewHandler.card_setters(self)
            MainViewHandler.first_list_loader(self)

    def card_setters(self, *args):
        Mainscreenvar = sm.get_screen("MainScreen")
        #First get the three cards as objects and store in variables
        last_card = Mainscreenvar.ids.ele3
        middle_card = Mainscreenvar.ids.ele2
        front_card = Mainscreenvar.ids.ele1
        #Now set each cards size and then its position
        Mainscreenvar.ids.ele3.size = Window.width - Window.width/5, Window.height - Window.height/3
        Mainscreenvar.ids.ele3.pos = Window.center[0]-last_card.width/2, Window.center[1]-last_card.height/2 + dp(17.5)
        Mainscreenvar.ids.ele2.size = Window.width - Window.width/5.5, Window.height - Window.height/3
        Mainscreenvar.ids.ele2.pos = Window.center[0]-middle_card.width/2, Window.center[1]-middle_card.height/2 + dp(10)
        Mainscreenvar.ids.ele1.size = Window.width - Window.width/6, Window.height - Window.height/3
        Mainscreenvar.ids.ele1.pos = Window.center[0]-front_card.width/2, Window.center[1]-front_card.height/2

        #Set some basic variables for sizes that can be used everywhere in the program
        self.card1_pos = tuple(Mainscreenvar.ids.ele1.pos)
        self.card2_pos = tuple(Mainscreenvar.ids.ele2.pos)
        self.card3_pos = tuple(Mainscreenvar.ids.ele3.pos)
        self.card1_size = tuple(Mainscreenvar.ids.ele1.size)
        self.card2_size = tuple(Mainscreenvar.ids.ele2.size)
        self.card3_size = tuple(Mainscreenvar.ids.ele3.size)


    def first_list_loader(self):
        Mainscreenvar = sm.get_screen("MainScreen")
        #Load the first list content and display it
        self.list_content = ListContent()
        self.list_content.ids.heading.text = all_lists[0].replace("_"," ")
        self.list_content.ids.view_button.bind(on_press = partial(ListView.list_view_loader_transition, self,1))
        card_to_add = 'ele'+str(counter)
        Mainscreenvar.ids[card_to_add].add_widget(self.list_content)
        mycursor.execute("SELECT * FROM {} DESC LIMIT 4".format(all_lists[0]))
        data = mycursor.fetchall()
        for a in reversed(data):
            self.list_reminder_element = ListReminderElement()
            if a[1]:
                text_to = '[font=Roboto-Black.ttf][size=18sp][color=' +self.rgb2hex(self.text_color) + ']' + a[0] +  '[/color][/size][/font]' + '\n' + \
                '[font=Roboto-Regular.ttf][size=16sp][color=' +self.rgb2hex(self.secondary_text_color) +']' + a[1] + '[/color][/size][/font]'
            else:
                text_to = '[font=Roboto-Black.ttf][size=18sp][color=' +self.rgb2hex(self.text_color) + ']' + a[0] +  '[/color][/size][/font]'
            self.list_reminder_element.ids.text.text = text_to
            self.list_reminder_element.ids.check_box.bind(on_press = partial(MainViewHandler.reminder_complete_handler, self))
            self.list_reminder_element.name = a[6]
            if a[5] == 1:
                self.list_reminder_element.completed = True
                self.list_reminder_element.ids.text.strikethrough = True
            self.list_content.ids.reminder_container.add_widget(self.list_reminder_element)


    def slider(self,operation, ele, *args):
        self = Mainapp.get_running_app()
        global counter
        Mainscreenvar = sm.get_screen("MainScreen")
        card_to_drop = "ele{}".format(counter)
        if operation == 1 and not all_lists:
            Mainscreenvar.remove_widget(MainViewHandler.label1)
            Mainscreenvar.remove_widget(MainViewHandler.label2)
            MainViewHandler.swapper(self,operation,None,None)
        else:
            if all_lists:
                Mainscreenvar.ids[card_to_drop].clear_widgets()
                MainViewHandler.swapper(self, operation, None,None)
                try:
                    plyer.vibrator.vibrate(0.02)
                except:
                    pass

    def swapper(self,operation,anim,caller):
        global counter, all_lists
        Mainscreenvar = sm.get_screen("MainScreen")

        if counter+1 == 4:
            card1_to_edit = 'ele1'
        else:
            card1_to_edit = 'ele{}'.format(counter+1)
        #We get the card that we want to morph into so that we can access its properties
        previous_card = Mainscreenvar.ids['ele'+str(counter)]
        anim1 = Animation(pos = self.card1_pos,size = self.card1_size,
                                     duration = .3, md_bg_color = self.primary_color,opacity = 1,)
        anim1.start(Mainscreenvar.ids[card1_to_edit])

        if counter+2 == 4:
            card2_to_edit = 'ele1'
            previous_card = Mainscreenvar.ids['ele3']
        elif counter+2 == 5:
            card2_to_edit = 'ele2'
            previous_card = Mainscreenvar.ids['ele1']
        else:
            card2_to_edit = 'ele{}'.format(counter+2)
            previous_card = Mainscreenvar.ids['ele'+str(counter+1)]
        anim3 = Animation(pos = self.card2_pos, size = self.card2_size, duration = .3,
                                    md_bg_color = self.secondary_color,opacity = 1)
        anim3.start(Mainscreenvar.ids[card2_to_edit])
        new_card_id = "ele{}".format(counter)
        new_card = Mainscreenvar.ids[new_card_id]
        new_card.opacity = 0
        new_card.size = self.card3_size
        # new_card.pos = (Window.center[0] - new_card.width/1.5, Window.center[1]-new_card.height/3)
        new_card.pos = (Window.center[0] - new_card.width/2, Window.center[1]-new_card.height/3)
        new_card.swipable = False
        Mainscreenvar.remove_widget(new_card)
        new_card.md_bg_color = self.tertiary_color
        anim6 = Animation(opacity = 1, pos = self.card3_pos, duration = .3)
        anim6.start(new_card)

        #We set the action button opacity to 1 also in case user has swiped away from the create list card
        if not Mainscreenvar.ids.action_button.opacity:
            Mainscreenvar.ids.action_button.opacity = 1

        Mainscreenvar.add_widget(new_card, 4)
        if counter != 3:
            counter +=1
        else:
            counter = 1
        if operation == 0: #This is a normal swipe to next card
            ele = collections.deque(all_lists)
            ele.rotate(-1)
            all_lists = ele
            Clock.schedule_once(partial(MainViewHandler.load_next_list_title,self, 0),.4)
        elif operation == 1: # This is a create new list from the no lsit menue
            Clock.schedule_once(partial(Creator.create_new_list_load_ui,self),.65)
            Mainscreenvar.ids.action_button.opacity = 0
            Mainscreenvar.ids.action_button.pos_hint = {'center_x':.85, 'center_y':.08}
            Mainapp.creating_new_list = True #When this is true it will disable the peek behaviour
        elif operation == 2: #This is a normal create new list
            Mainscreenvar.ids[card1_to_edit].clear_widgets()
            Clock.schedule_once(partial(Creator.create_new_list_load_ui,self),.4)
            Mainscreenvar.ids[card1_to_edit].clear_widgets()
            Mainapp.creating_new_list = True #When this is true it will disable the peek behaviour

    def load_next_list_title(self, delay, *args):
        card_to_add_to = 'ele{}'.format(counter)
        Mainscreenvar = sm.get_screen("MainScreen")
        if not all_lists:
            pass
        elif all_lists and len(Mainscreenvar.ids[card_to_add_to].children) == 0:
            mycursor.execute("SELECT * FROM {} DESC LIMIT 4".format(all_lists[0]))
            data = mycursor.fetchall()
            self.list_content = ListContent()
            self.list_content.ids.heading.text = all_lists[0].replace('_', ' ')
            self.list_content.ids.view_button.bind(on_press = partial(ListView.list_view_loader_transition, self,1))
            Mainscreenvar.ids[card_to_add_to].add_widget(self.list_content)
            if delay == 0:
                event = Clock.schedule_once(partial(MainViewHandler.load_next_list_reminders,self,data),.4)
            else:
                event = Clock.schedule_once(partial(MainViewHandler.load_next_list_reminders, self, data), delay)
        else:
            mycursor.execute("SELECT * FROM {} DESC LIMIT 4".format(all_lists[0]))
            data = mycursor.fetchall()
            if delay == 0:
                event = Clock.schedule_once(partial(MainViewHandler.load_next_list_reminders,self,data),.4)
            else:
                event = Clock.schedule_once(partial(MainViewHandler.load_next_list_reminders, self, data), delay)

    def load_next_list_reminders(self, data, *args):
        Mainscreenvar = sm.get_screen("MainScreen")
        card = "ele"+str(counter)
        if not self.loaded_behind_reminders:
            self.list_content.ids.reminder_container.opacity = 0
            for a in reversed(data):
                list_reminder_element = ListReminderElement()
                list_reminder_element.ids.check_box.bind(on_press = partial(MainViewHandler.reminder_complete_handler, self))
                list_reminder_element.name = a[6]
                if a[1]:
                    text_to = '[font=Roboto-Black.ttf][size=18sp][color=' +self.rgb2hex(self.text_color) + ']' + a[0] +  '[/color][/size][/font]' + '\n' + \
                    '[font=Roboto-Regular.ttf][size=16sp][color=' +self.rgb2hex(self.secondary_text_color) +']' + a[1] + '[/color][/size][/font]'
                else:
                    text_to = '[font=Roboto-Black.ttf][size=18sp][color=' +self.rgb2hex(self.text_color) + ']' + a[0] +  '[/color][/size][/font]'
                list_reminder_element.ids.text.text = text_to
                if a[5]:
                    list_reminder_element.completed = True
                    list_reminder_element.ids.text.strikethrough = True

                self.list_content.ids.reminder_container.add_widget(list_reminder_element)
            anim1 = Animation(opacity = 1, duration = .3)
            anim1.start(self.list_content.ids.reminder_container)
        else:
            self.loaded_behind_reminders = False #Reset this varaiable
        Mainscreenvar.ids[card].swipable = True
    def load_behind_title(self,*args):
        self = Mainapp.get_running_app()
        Mainscreenvar = sm.get_screen("MainScreen")
        if counter+1 == 4:
            card_to_add_to = 'ele1'
        else:
            card_to_add_to = 'ele{}'.format(counter+1)
        if not len(Mainscreenvar.ids[card_to_add_to].children):
            self.list_content = ListContent()
            self.list_content.opacity = 0
            if len(all_lists)>1:
                self.list_content.ids.heading.text = all_lists[1].replace('_', ' ')
            else:
                self.list_content.ids.heading.text = all_lists[0].replace('_', ' ')
            self.list_content.ids.view_button.bind(on_press = partial(ListView.list_view_loader_transition, self,1))
            Animation(opacity = 1, duration = .3, s = 1/20).start(self.list_content)
            Mainscreenvar.ids[card_to_add_to].add_widget(self.list_content)

    def load_behind_reminder(self, *args):
        self = Mainapp.get_running_app()
        Mainscreenvar = sm.get_screen("MainScreen")
        if len(all_lists)>0:
            try:
                no = all_lists[1]
            except:
                no = all_lists[0] #In case of any error we default to the current list just in case
        else:
            no = all_lists[0]
        if counter+1 == 4:
            card_to_add_to = 'ele1'
        else:
            card_to_add_to = 'ele{}'.format(counter+1)
        mycursor.execute("SELECT * FROM {} DESC LIMIT 4".format(no))
        data = mycursor.fetchall()
        if not len(Mainscreenvar.ids[card_to_add_to].children[0].ids.reminder_container.children):
            for a in reversed(data):
                Mainscreenvar.ids[card_to_add_to].children[0].ids.reminder_container.opacity =0
                list_reminder_element = ListReminderElement()
                list_reminder_element.ids.check_box.bind(on_press = partial(MainViewHandler.reminder_complete_handler, self))
                list_reminder_element.name = a[6]
                if a[1]:
                    text_to = '[font=Roboto-Black.ttf][size=18sp][color=' +self.rgb2hex(self.text_color) + ']' + a[0] +  '[/color][/size][/font]' + '\n' + \
                    '[font=Roboto-Regular.ttf][size=16sp][color=' +self.rgb2hex(self.secondary_text_color) +']' + a[1] + '[/color][/size][/font]'
                else:
                    text_to = '[font=Roboto-Black.ttf][size=18sp][color=' +self.rgb2hex(self.text_color) + ']' + a[0] +  '[/color][/size][/font]'
                list_reminder_element.ids.text.text = text_to
                if a[5]:
                    list_reminder_element.completed = True
                    list_reminder_element.ids.text.strikethrough = True
                Mainscreenvar.ids[card_to_add_to].children[0].ids.reminder_container.add_widget(list_reminder_element)
            anim1 = Animation(opacity = 1, duration = .3, s = 1/20)
            anim1.start(Mainscreenvar.ids[card_to_add_to].children[0].ids.reminder_container)
        self.loaded_behind_reminders = True #THis varaiable is used to check to prevent app from crashing

    def reminder_complete_handler(self, instance):
        if instance.parent.completed == False:
            instance.parent.completed = True
            instance.parent.ids.text.strikethrough = True
            mycursor.execute("UPDATE {} SET state = 1 WHERE rem_id = {}".format(all_lists[0], instance.parent.name))
            connection.commit()
        else:
            instance.parent.completed = False
            instance.parent.ids.text.strikethrough = False
            mycursor.execute("UPDATE {} SET state = 0 WHERE rem_id = {}".format(all_lists[0], instance.parent.name))
            connection.commit()

    def no_lists(self):
        card_to_drop = "ele{}".format(counter)
        Mainscreenvar = sm.get_screen("MainScreen")
        Mainscreenvar.ids[card_to_drop].clear_widgets()
        anim1 = Animation(pos = (Window.center[0]-Mainscreenvar.ids[card_to_drop].width/2,-Window.height), duration = .6)
        anim1.start(Mainscreenvar.ids.ele1)
        anim1.start(Mainscreenvar.ids.ele2)
        anim1.start(Mainscreenvar.ids.ele3)
        Animation(pos_hint = {'center_x':.5, 'center_y':.40}, duration = .5, t = 'in_out_circ').start(Mainscreenvar.ids.action_button)
        MainViewHandler.label1 = MDLabel(text = 'Looks like you have no lists', pos_hint = {'center_x':.5,'center_y':.55},
                                                            font_style = 'H5',font_name = 'Roboto-Medium.ttf', halign = 'center',  theme_text_color = 'Custom',
                                                            text_color = (1,1,1,1),opacity = 0
                                                            )
        MainViewHandler.label2 = MDLabel(text = 'Create a new one here', pos_hint = {'center_x':.5,'center_y':.50},
                                                            font_style = 'H6',font_name = 'Roboto-Medium.ttf', halign = 'center',theme_text_color = 'Custom',
                                                            text_color = (1,1,1,.75), opacity = 0
                                                            )
        Mainscreenvar.add_widget(MainViewHandler.label1)
        Mainscreenvar.add_widget(MainViewHandler.label2)
        anim2 = Animation(opacity = 1, duration = .6)
        anim2.start(MainViewHandler.label1)
        anim2.start(MainViewHandler.label2)

class ListView():

    def list_view_loader_transition(self,op,caller):
        global current_list, current_app_location
        Mainscreenvar = sm.get_screen("MainScreen")
        current_list = all_lists[0]
        card = 'ele'+str(counter)
        Mainscreenvar.ids[card].swipable = False
        current_app_location = 'IndividualListView'
        if op == 1:
            anim1 = Animation(radius=(0,0,0,0), duration = .5, t = 'in_out_circ', size = (Window.width, Window.height), pos = (0,0))
            anim2 = Animation(pos = (Window.center[0]-Mainscreenvar.children[2].width/2, -dp(500)), duration = .4, t = 'in_out_circ')
            anim3 = Animation(pos = (Window.center[0]-Mainscreenvar.children[2].width/2, -dp(500)), duration = .4, t = 'in_out_circ')
            anim1.start(Mainscreenvar.children[1])
            anim2.start(Mainscreenvar.children[2])
            anim3.start(Mainscreenvar.children[3])
            name = 'ele{}'.format(counter)
            if counter+1 == 4:
                card_behind = 'ele1'
            else:
                card_behind = 'ele{}'.format(counter+1)
            Mainscreenvar.ids[name].clear_widgets()
            Mainscreenvar.ids[card_behind].clear_widgets()
            anim3.bind(on_complete = partial(ListView.load_screen_content,self))
        else:
            name = 'ele{}'.format(counter)
            Mainscreenvar.ids[name].clear_widgets()

    def load_screen_content(self, *args):
        self.list_view_content = ListViewContent()
        self.list_view_content.opacity = 0
        self.list_view_content.ids.title.text = current_list
        self.list_view_content.ids.back_button.bind(on_release = ListView.back_op)
        self.list_view_content.ids.delete_button.bind(on_release = ListView.delete_op)
        Mainscreenvar = sm.get_screen("MainScreen")
        card = 'ele'+str(counter)
        Mainscreenvar.ids[card].add_widget(self.list_view_content)
        ListView.sort_list_data(self)

    def sort_list_data(self):
        #First get data from the database
        mycursor.execute("SELECT * FROM {}".format(current_list))
        list_data = mycursor.fetchall()
        self.list_reminder_data=[]
        self.none_reminders = []
        for reminder in list_data:
            #Reminders that dont ring on any days or dates
            if reminder[2]=='[]':
                self.none_reminders.append([reminder[6],reminder[5]])
            # Reminder that will ring on a single date
            elif len(eval(reminder[2])) == 1 and not eval(reminder[2])[0].isalpha():
                self.list_reminder_data.append([reminder[6],eval(reminder[2])[0], reminder[6]])

            # Reminder that rings on multiple dates.
            elif not eval(reminder[2])[0].isalpha():
                for a in eval(reminder[2]):
                    self.list_reminder_data.append([reminder[6],a,reminder[5]])

            else:# Reminder that ring on a day or on multiple days
                start = date.today()
                date_array = (start + timedelta(days=x) for x in range(7))
                for date_object in date_array:
                    a = date_object.weekday()
                    if a == 0:
                        b = "Monday"
                    if a == 1:
                        b = "Tuesday"
                    if a == 2:
                        b = "Wednesday"
                    if a == 3:
                        b = "Thursday"
                    if a == 4:
                        b = "Friday"
                    if a == 5:
                        b = "Saturday"
                    if a == 6:
                        b = "Sunday"
                    for c in eval(reminder[2]):
                        if c == b:
                            self.list_reminder_data.append([reminder[6],date_object.strftime('%x'),reminder[5]])
        self.list_reminder_data.sort(key=lambda x: x[-2])

        #Parse data into a dictionary of lists grouped based on their dates
        data_element = []
        self.data_dict={'None':self.none_reminders}
        for a in range(len(self.list_reminder_data)):
            previous_date=self.list_reminder_data[a-1][1]
            if not a:
                data_element.append([self.list_reminder_data[a][0], self.list_reminder_data[a][2]])
                if len(self.list_reminder_data) == 1:
                #If there is only one element we directly append the element
                    self.data_dict[self.list_reminder_data[a][1]] = data_element

            elif a == len(self.list_reminder_data)-1: # we are at the last element of the list
                if self.list_reminder_data[a][1] == previous_date:
                    data_element.append([self.list_reminder_data[a][0], self.list_reminder_data[a][2]])
                    data_element.sort(key=lambda x: x[-1])
                    self.data_dict[previous_date] = data_element
                else:
                    data_element.sort(key=lambda x: x[-1])
                    self.data_dict[previous_date] = data_element

                    self.data_dict[self.list_reminder_data[a][1]] = [[self.list_reminder_data[a][0], self.list_reminder_data[a][2]]]
                    print(self.data_dict)

            elif previous_date == self.list_reminder_data[a][1]:
                data_element.append([self.list_reminder_data[a][0], self.list_reminder_data[a][2]])
                #If same element append to the data element

                if len(self.list_reminder_data) == 1:
                    self.data_dict[self.list_reminder_data[a][1]] = data_element

            else:
                data_element.sort(key=lambda x: x[-1])
                self.data_dict[previous_date] = data_element
                data_element = list()
                data_element.append([self.list_reminder_data[a][0],self.list_reminder_data[a][2]])
        ListView.heading_data_parser(self)

    def heading_data_parser(self):
        Mainscreenvar = sm.get_screen("MainScreen")
        date_list = []
        #Calculate today and tomorrow's date
        today = date.today().strftime('%x')
        tomorrow = date.today() + timedelta(days=1)
        tomorrow = tomorrow.strftime('%x')
        for date_obj in self.data_dict:
            if date_obj == today:
                text = 'Today'
                date_element = {'date':text,'active':True, 'name':today}
            elif date_obj == tomorrow:
                text = 'Tomorrow'
                date_element = {'date':text,'active':False,'name':tomorrow}
            elif date_obj == 'None':
                text = 'None'
                date_element = {'date':text,'active':False,'name':'None'}
            else:
                text = datetime.strptime(date_obj,'%x').strftime('%b\n%d')
                date_element = {'date':text,'active':False,'name':date_obj}
            date_list.append(date_element)
        # If not today element then set the none element as the selected one
        if ({'date':'None','active':False,'name':'None'} in date_list and
            {'date':'Today','active':True, 'name':today} not in date_list):
            i = date_list.index({'date':'None','active':False,'name':'None'})
            date_list[i]['active'] = True
        self.list_view_content.ids.date_stuff.data = date_list

        #Scroll so that the today element is centered on screen
        if {'date':'Today','active':True, 'name':today} in date_list:
            length = len(date_list)
            width = length*dp(100)
            pixel_count = 0
            for a in date_list:
                if a == {'date':'Today','active':True, 'name':today}:
                    break
                else:
                    pixel_count+=dp(100)
            self.list_view_content.ids.date_stuff.scroll_x = pixel_count/width


    def current_date_reminder_data_parser(self, date_2_disp):
        self = Mainapp.get_running_app()
        self.date_2_show = date_2_disp
        reminder_data_list=list()
        if len(self.data_dict['None'])>0:
            reminder_data_list.append({'text':' ','opacity':0,'completed':False,'disable_height':True,'height':dp(165)})
        if len(self.data_dict)>1:
            if not reminder_data_list:
                reminder_data_list.append({'text':' ','opacity':0,'completed':False,'disable_height':True,'height':dp(165)})
        added = False
        now = datetime.now()
        for reminder_id in self.data_dict[date_2_disp]:
            mycursor.execute('SELECT * FROM {} WHERE rem_id = {}'.format(current_list,reminder_id[0]))
            reminder_data = mycursor.fetchone()
            if reminder_data[2] != '[]':# Check if the reminder actually has a ring date
                reminder_dates = eval(reminder_data[2])

                #Calculate the date string for the reminder
                # The reminder rings on a single date or multiple
                dates = ''
                if not reminder_dates[0].isalpha():
                    if len(reminder_dates)>2:
                        dates = reminder_dates[0]+'  '+reminder_dates[1]+'...'
                    else:
                        for value in reminder_dates:
                            dates += value+'  '
                else: # The reminder repeats on a day or multiple days
                    if len(reminder_dates)>3:
                        dates = reminder_dates[0][0:3]+'  '+reminder_dates[1][0:3]+'  '+reminder_dates[2][0:3]+ '...'
                    else:
                        for value in reminder_dates:
                            dates += value[0:3]+'  '
            else:# This reminder doesnt ring on any day or date
                dates = ' '

            if dates == ' ': # This is reminder that doesnt ring on any dates or days
                text = (
                        "[font=Roboto-Black.ttf][size=23sp]"
                        + reminder_data[0]
                        + "[/size][/font]"
                        + "\n \n"
                        + "[font=Roboto-Regular.ttf][size=18sp]"
                        + reminder_data[1]
                        + "[/size][/font]"
                        + '\n \n'
                        )
                if reminder_data[6] == 1: # A completed Reminder
                    reminder_data_element ={
                                            'text':text,
                                            'opacity':1,
                                            'color':[20/255,148/255,20/255,1],
                                            'completed':True,
                                            'name':reminder_data[-2],
                                            'disable_height':False
                                            }
                else: # A not completed reminder
                    reminder_data_element ={
                                            'text':text,
                                            'opacity':1,
                                            'color':[20/255,148/255,20/255,1],
                                            'completed':False,
                                            'name':reminder_data[-2],
                                            'disable_height':False
                                            }
            else: # Normal reminder element
                #If reminder is not Completed
                completed_dates = reminder_data[-1]
                try:
                    completed_dates = eval(completed_dates)
                except:
                    completed_dates = []
                if date_2_disp not in completed_dates:

                    #Check if the reminder has already rang
                    if datetime.strptime(reminder_data[3] + ' ' + date_2_disp, '%I:%M %p %x') < now:
                        text = (
                                "[font=Roboto-Black.ttf][size=23sp]"
                                + reminder_data[0]
                                + "[/size][/font]"
                                + "\n \n"
                                + "[font=Roboto-Regular.ttf][size=18sp]"
                                + reminder_data[1]
                                + "[/size][/font]"
                                + '\n \n'
                                + "[font=icons.ttf]\U000F0020[/font][color=#DA4453]  "
                                + reminder_data[3]
                                + '[/color]    '
                                + "[font=icons.ttf]\U000F00ED[/font][color=#DA4453]  "
                                + dates
                                +"[/color]"
                                )
                        reminder_data_element = {
                                                'text':text,
                                                'opacity':1,
                                                'color':(218/255,68/255,83/255,1),
                                                'completed':False,
                                                'name':reminder_data[-2],
                                                'disable_height':False
                                                }
                    else:
                        text = (
                                "[font=Roboto-Black.ttf][size=23sp]"
                                + reminder_data[0]
                                + "[/size][/font]"
                                + "\n \n"
                                + "[font=Roboto-Regular.ttf][size=18sp]"
                                + reminder_data[1]
                                + "[/size][/font]"
                                + '\n \n'
                                + "[font=icons.ttf]\U000F0020[/font][color=#A9A0A0]  "
                                + reminder_data[3]
                                + '[/color]    '
                                + "[font=icons.ttf]\U000F00ED[/font][color=#A9A0A0]  "
                                + dates
                                +"[/color]"
                                )
                        reminder_data_element = {
                                                'text':text,
                                                'opacity':1,
                                                'color':(232/255,130/255,36/255,1),
                                                'completed':False,
                                                'name':reminder_data[-2],
                                                'disable_height':False
                                                }
                #If reminder is completed
                else:
                    #Check if the reminder has already rang
                    if datetime.strptime(reminder_data[3] + ' ' + date_2_disp, '%I:%M %p %x') < now:
                        text = (
                                "[font=Roboto-Black.ttf][size=23sp]"
                                + reminder_data[0]
                                + "[/size][/font]"
                                + "\n \n"
                                + "[font=Roboto-Regular.ttf][size=18sp]"
                                + reminder_data[1]
                                + "[/size][/font]"
                                + '\n \n'
                                + "[font=icons.ttf]\U000F0020[/font][color=#DA4453]  "
                                + reminder_data[3]
                                + '[/color]    '
                                + "[font=icons.ttf]\U000F00ED[/font][color=#DA4453]  "
                                + dates
                                +"[/color]"
                                )
                    else:
                        text = (
                                "[font=Roboto-Black.ttf][size=23sp]"
                                + reminder_data[0]
                                + "[/size][/font]"
                                + "\n \n"
                                + "[font=Roboto-Regular.ttf][size=18sp]"
                                + reminder_data[1]
                                + "[/size][/font]"
                                + '\n \n'
                                + "[font=icons.ttf]\U000F0020[/font][color=#A9A0A0]  "
                                + reminder_data[3]
                                + '[/color]    '
                                + "[font=icons.ttf]\U000F00ED[/font][color=#A9A0A0]  "
                                + dates
                                +"[/color]"
                                )
                    reminder_data_element = {
                                            'text':text,
                                            'opacity':1,
                                            'color':(71/255,218/255,68/255,1),
                                            'completed':True,
                                            'name':reminder_data[-2],
                                            'disable_height':False
                                            }

            reminder_data_list.append(reminder_data_element)
        self.list_view_content.ids.content.data = reminder_data_list
        self.list_view_content.ids.content.refresh_from_data()
        self.list_view_content.ids.content.scroll_y=0
        Animation(opacity=1, duration=.3).start(self.list_view_content)
        Animation(scroll_y =1,duration = .3).start(self.list_view_content.ids.content)


    def back_op(instance):
        global current_app_location,counter
        self = Mainapp.get_running_app()
        Mainscreenvar = sm.get_screen("MainScreen")
        name = 'ele{}'.format(counter)
        Mainscreenvar.ids[name].swipable = True
        if counter+1 == 4:
            card_behind = 'ele1'
        else:
            card_behind = 'ele{}'.format(counter+1)
        #Reset the position for the main card up front
        if all_lists:
            Mainscreenvar.ids[name].clear_widgets()
            anim1 = Animation(size = self.card1_size,pos = self.card1_pos, duration = .5, t = 'in_out_circ', radius = (40,40,40,40))
            anim1.start(Mainscreenvar.ids[name])
            anim2 = Animation(pos = self.card2_pos, duration = .7, t = 'in_out_circ')
            anim3 = Animation(pos = self.card3_pos, duration = .9, t = 'in_out_circ')
            anim2.start(Mainscreenvar.children[2])
            anim3.start(Mainscreenvar.children[3])
        else:
            Mainscreenvar.ids[name].radius = (40,40,40,40)
        current_app_location = 'MainScreen'
        Mainscreenvar.ids.action_button.data = {'New List':'format-list-checkbox'}
        self.loaded_behind_reminders = False
        if all_lists:
            MainViewHandler.load_next_list_title(self, 1)
        else:
            MainViewHandler.all_lists_loader(self)

    def delete_op(instance):
        global all_lists
        self = Mainapp.get_running_app()
        mycursor.execute("DROP TABLE {}".format(current_list))
        connection.commit()
        all_lists.remove(current_list)
        ListView.back_op(None)

    def mark_complete(instance):
        self = Mainapp.get_running_app()
        if instance.completed: #We need to mark reminder as not completed
            mycursor.execute("SELECT * FROM {} WHERE rem_id = {}".format(current_list,instance.name))
            data = mycursor.fetchone()
            if data[-1]: # If it not NONE value
                completed_dates = eval(data[-1])
                completed_dates.remove(self.date_2_show)
            mycursor.execute('UPDATE {} SET state=0,compdates ="{}" WHERE rem_id={}'.format(current_list,completed_dates,instance.name))
            connection.commit()
            instance.completed = False
        else:
            mycursor.execute("SELECT * FROM {} WHERE rem_id={}".format(current_list,instance.name))
            data = mycursor.fetchone()
            if data[-1]: # If it not NONE value
                completed_dates = eval(data[-1])
                str(completed_dates.append(self.date_2_show))
            else:
                completed_dates = str([self.date_2_show,])
            mycursor.execute('UPDATE {} SET compdates="{}",state=1 WHERE rem_id={}'.format(current_list,completed_dates,instance.name))
            connection.commit()
            instance.completed = True

class IndividualReminderView():
    def screen_switcher(self,reminder):
        sm.current = 'ReminderScreen'
        Clock.schedule_once(partial(IndividualReminderView.heading_loader, self, reminder, 0),.4)

    def heading_loader(self, reminder, mode,instance):
        Remindervar = sm.get_screen('ReminderScreen')
        Remindervar.ids.scroll.scroll_y = 1
        Remindervar.ids.back_button.bind(on_release= IndividualReminderView.back_op)
        Remindervar.ids.delete_button.opacity = 1
        Remindervar.ids.delete_button.bind(on_release = IndividualReminderView.delete_op)
        mycursor.execute("SELECT * FROM {} WHERE rem_id = {}".format(current_list, reminder))
        self.reminder_data = mycursor.fetchone()
        self.current_reminder = reminder
        self.heading.opacity = 0
        if not self.reminder_data[0] == ' ':
            self.heading.ids.heading.text = self.reminder_data[0]
        Remindervar.ids.container.add_widget(self.heading)
        anim1 = Animation(opacity = 1, duration = .2)
        anim1.start(self.heading)
        Clock.schedule_once(partial(IndividualReminderView.description_loader, self, reminder),.2)

    def description_loader(self, reminder, instance):
        Remindervar = sm.get_screen('ReminderScreen')
        self.description.opacity = 0
        if self.reminder_data[1] :
            self.description.ids.description.text = self.reminder_data[1]
        else:
            self.description.ids.description.text = ''
        Remindervar.ids.container.add_widget(self.description)
        anim2 = Animation(opacity = 1, duration = .2)
        anim2.start(self.description)
        Clock.schedule_once(partial(IndividualReminderView.timing_loader, self, reminder),.3)

    def timing_loader(self, reminder, instance):
        Remindervar = sm.get_screen('ReminderScreen')
        Remindervar.ids.container.add_widget(self.timing)
        self.timing.opacity = 0
        self.timing.ids.type_picker.name = 'type_picker_viewer'
        self.reminder_dates=eval(self.reminder_data[2])
        self.timing.ids.time_picker.text = self.reminder_data[3]
        if not self.reminder_data[3] == 'Time': # Check to see if the reminder may not have a time
            self.time_picker.set_time(datetime.strptime(self.reminder_data[3], '%I:%M %p'))
        if not self.reminder_dates:
            #This means the reminder will not have any date to ring on
            Animation(opacity = 1,duration = .2).start(self.timing)
            Clock.schedule_once(partial(IndividualReminderView.save_adder, self), .2)
            self.created = True
            self.timing.ids.type_picker.text = 'None'

        elif self.reminder_dates[0].isalpha():
            #This means we have days for the reminder to ring on
            self.timing.ids.type_picker.text = 'Days'
            self.timing.ids.days_container.orientation = 'horizontal'
            tmp_data = [['M',"Monday"],['T',"Tuesday"],['W',"Wednesday"],
                   ['T',"Thursday"],['F',"Friday"],['S',"Saturday"],
                   ['S',"Sunday"]]
            data = []
            for a in tmp_data:
                if a[1] in self.reminder_dates:
                    data.append(a+[True,])
                else:
                    data.append(a+[False,])
            self.create_day_event = Clock.schedule_once(partial(IndividualReminderView.day_adder,self,data), 0)
            Clock.schedule_once(partial(IndividualReminderView.save_adder, self), .3)
        else:
            #This means we have dates for the reminder to ring on
            self.timing.ids.type_picker.text = 'Dates'
            self.timing.ids.days_container.orientation = 'vertical'
            data = list(self.reminder_dates)
            plus_button = MDIconButton(icon = 'plus', md_bg_color = self.accent_color,
                                                            pos_hint = {'center_x':.5})
            plus_button.bind(on_release = partial(IndividualReminderView.new_date_adder, self))
            self.timing.ids.holder.add_widget(plus_button)
            self.create_date_event = Clock.schedule_once(partial(IndividualReminderView.date_adder, self, data), 0)
            Clock.schedule_once(partial(IndividualReminderView.save_adder, self), .2)

    def save_adder(self,*args):
        Remindervar = sm.get_screen('ReminderScreen')
        self.saving.ids.save_button.bind(on_release = IndividualReminderView.changes_checker)
        self.saving.ids.cancel_button.bind(on_release = IndividualReminderView.back_op)
        Remindervar.ids.container.add_widget(self.saving)

    def day_adder(self, data, *args):
        Remindervar = sm.get_screen('ReminderScreen')
        if data:
            ele = MDChip(text = data[0][0],
                         selected_chip_color = self.accent_color,
                         color = self.primary_color,
                         icon = '',
                         name = data[0][1],
                         active = data[0][2]
                         )
            self.timing.ids.days_container.add_widget(ele)
            del data[0]
            self.create_day_event = Clock.schedule_once(partial(IndividualReminderView.day_adder, self, data), 0)
        else:
            self.create_day_event.cancel()
            self.created = True
            anim1 = Animation(opacity = 1, d = .3)
            anim1.start(self.timing)

    def date_adder(self, data, *args):
        for a in data:
            ele = ReminderDatesBlueprint()
            ele.ids.date_picker.text = a
            ele.ids.date_picker.bind(on_release = partial(IndividualReminderView.current_open_definer, self))
            ele.ids.remove_button.bind(on_release = partial(IndividualReminderView.date_remover, self))
            self.timing.ids.days_container.add_widget(ele)
        else:
            self.created = True
            anim1 = Animation(opacity = 1, d = .2)
            anim1.start(self.timing)

    def type_switcher(instance):
        self = MDApp.get_running_app()
        self.reminder_type_menu_viewer.dismiss()
        current_text = self.timing.ids.type_picker.text
        if 'Dates' == instance and current_text != instance:
            self.timing.ids.days_container.clear_widgets()
            self.timing.ids.days_container.orientation = 'vertical'
            # Add the reminders dates back from the database if user changes from days/none to dates again
            if self.reminder_dates and not self.reminder_dates[0].isalpha():
                data = list(self.reminder_dates)
                IndividualReminderView.date_adder(self,data)
            plus_button = MDIconButton(icon = 'plus', md_bg_color = self.accent_color,
                                                            pos_hint = {'center_x':.5})
            plus_button.bind(on_release = partial(IndividualReminderView.new_date_adder, self))
            self.timing.ids.holder.add_widget(plus_button)

        elif 'Days' == instance and current_text != instance:
            self.timing.ids.days_container.clear_widgets()
            if len(self.timing.ids.holder.children) == 5:
                self.timing.ids.holder.remove_widget(self.timing.ids.holder.children[0])
            self.timing.ids.days_container.orientation = 'horizontal'
            tmp_data = [['M',"Monday"],['T',"Tuesday"],['W',"Wednesday"],
                   ['T',"Thursday"],['F',"Friday"],['S',"Saturday"],
                   ['S',"Sunday"]]
            data = []
            for a in tmp_data:
                if a[1] in self.reminder_dates:
                    data.append(a+[True,])
                else:
                    data.append(a+[False,])
            self.create_day_event = Clock.schedule_once(partial(IndividualReminderView.day_adder,self,data), 0)

        elif 'None' == instance and self.created and current_text != instance:
            self.timing.ids.days_container.clear_widgets()
            if len(self.timing.ids.holder.children) == 5:
                self.timing.ids.holder.remove_widget(self.timing.ids.holder.children[0])

        self.timing.ids.type_picker.text= instance

    def back_op(instance, *args):
        self = Mainapp.get_running_app()
        Remindervar = sm.get_screen('ReminderScreen')
        Remindervar.ids.container.clear_widgets()
        self.timing.ids.days_container.clear_widgets()
        if len(self.timing.ids.holder.children) == 5:
            self.timing.ids.holder.remove_widget(self.timing.ids.holder.children[0])
        sm.current = 'MainScreen'
        sm.transition.direction = 'right'
        self.created = False
        Remindervar.ids.back_button.unbind(on_release= IndividualReminderView.back_op)
        Remindervar.ids.delete_button.unbind(on_release = IndividualReminderView.delete_op)
        self.saving.ids.save_button.unbind(on_release = IndividualReminderView.changes_checker)
        self.saving.ids.cancel_button.unbind(on_release = IndividualReminderView.back_op)

    def delete_op(instance,*args):
        self = Mainapp.get_running_app()
        Remindervar = sm.get_screen('ReminderScreen')
        mycursor.execute("DELETE FROM {} WHERE rem_id = {}".format(current_list,self.current_reminder))
        connection.commit()
        IndividualReminderView.back_op(self)
        ListView.sort_list_data(self)
        ListView.heading_data_parser(self)
        if datetime.now().strftime('%x') in self.data_dict:
            #Set the preference for today as the shown entry
            ListView.current_date_reminder_data_parser(self,datetime.now().strftime('%x'))
        else:
            #Set the preference for today as the shown entry
            ListView.current_date_reminder_data_parser(self,'None')

    def current_open_definer(self, instance):
        self.date_picker.open()
        self.current_editing = instance

    def time_setter(instance,time):
        self = MDApp.get_running_app()
        self.timing.ids.time_picker.text = time.strftime('%I:%M %p')

    def date_setter(self,date,date_range):
        self = MDApp.get_running_app()
        new_date = date.strftime('%x')
        for others in self.current_editing.parent.parent.children:
            if others.ids.date_picker.text == new_date:
                toast('This Reminder already rings on this date \n choose another date')
                break
        else:
            self.current_editing.text = new_date

    def new_date_adder(self, instance):
        ele = ReminderDatesBlueprint()
        ele.ids.date_picker.bind(on_release = partial(IndividualReminderView.current_open_definer, self))
        ele.ids.remove_button.bind(on_release = partial(IndividualReminderView.date_remover, self))
        ele.ids.date_picker.text = 'Choose a date'
        self.timing.ids.days_container.add_widget(ele)

    def date_remover(self, instance):
        instance.parent.parent.remove_widget(instance.parent)

    def save_reminder(self,caller):
        mycursor.execute("DELETE FROM {} WHERE rem_id = {}".format(current_list, self.current_reminder))
        if self.description.ids.description.text == '' or self.description.ids.description.text.isspace():
            insert_command = 'INSERT INTO {} (title,description,date,time,rem_id,alertlvl,state,compdates) VALUES("{}","","{}","{}",{},0, 0,"[]")'.format(
                                current_list, self.heading.ids.heading.text,
                                self.new_timings,
                                self.timing.ids.time_picker.text,
                                self.reminder_data[-2]
                                )
        else:
            insert_command = 'INSERT INTO {} (title,description,date,time,rem_id,alertlvl,state,compdates) VALUES("{}","{}","{}","{}", {},0, 0,"[]")'.format(
                                current_list, self.heading.ids.heading.text,
                                self.description.ids.description.text, self.new_timings,
                                self.timing.ids.time_picker.text,
                                self.reminder_data[-2]
                                )
        mycursor.execute(insert_command)
        connection.commit()

        # Update the previous view
        ListView.sort_list_data(self)
        ListView.heading_data_parser(self)
        if datetime.now().strftime('%x') in self.data_dict:
            #Set the preference for today as the shown entry
            ListView.current_date_reminder_data_parser(self,datetime.now().strftime('%x'))
        else:
            #Set the preference for today as the shown entry
            ListView.current_date_reminder_data_parser(self,'None')

        if not self.new_timings: #We are saving nothing into the database so clear all previous reminders
            if eval(self.reminder_data[2]): #Make sure that there was some data before that needs to cleared
                if eval(self.reminder_data[2])[0].isalpha():
                    AlarmDateTimeHandler.remove_all(self,self.reminder_data[-2], True)
                else:
                    AlarmDateTimeHandler.remove_all(self,self.reminder_data[-2], False)
        elif self.new_timings[0].isalpha():
            AlarmDateTimeHandler.days_handler(self,self.new_timings, self.timing.ids.time_picker.text, self.reminder_data[-2], 1)
        else:
            AlarmDateTimeHandler.dates_handler(self,self.new_timings,self.timing.ids.time_picker.text, self.reminder_data[-2], 1)

        if current_app_location != 'MainScreen':
            ListView.sort_list_data(self)
            IndividualReminderView.back_op(self, None)
        else:
            IndividualReminderView.back_op(self, None)

    def changes_checker(*args):
        self = MDApp.get_running_app()
        self.new_timings = []
        saveable = False
        if self.timing.ids.type_picker.text == 'Days':
            if self.timing.ids.time_picker.text == 'Time':
                toast('Please select a time')
            else:
                active = False
                for a in self.timing.ids.days_container.children:
                    if a.active:
                        self.new_timings.append(a.name)
                        active = True
                if not active:
                    toast('Please select a day for the reminder to ring on')
                else:
                    c = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    sorted(self.new_timings, key=c.index)
                    self.new_timings.reverse()
                    saveable = True
        elif self.timing.ids.type_picker.text == 'Dates':
            if self.timing.ids.time_picker.text == 'Time':
                toast("Please select a time")
            else:
                if not len(self.timing.ids.days_container.children):
                    toast('Please select a date for the reminder to ring on')
                else:
                    for a in self.timing.ids.days_container.children:
                        if a.ids.date_picker.text == 'Choose a date':
                            toast('Please select a date for the reminder to ring on')
                            break
                        else:
                            self.new_timings.append(a.ids.date_picker.text)
                            saveable = True
        else:
            if not self.timing.ids.time_picker == 'Time':
                self.timing.ids.time_picker.text = 'Time'
            saveable = True
        if saveable:
            if (self.reminder_data[0] == self.heading.ids.heading.text and
                self.reminder_data[1] == self.description.ids.description.text and
                self.reminder_data[3] == self.timing.ids.time_picker.text and
                self.reminder_dates == self.new_timings):
                    IndividualReminderView.back_op(self, None)
            else:
                IndividualReminderView.save_reminder(self, None)

class Creator():
    def create_new_list_load_ui(self, time):
        Mainscreenvar = sm.get_screen("MainScreen")
        Mainscreenvar.ids.action_button.opacity = 0
        anim1 = Animation(pos_hint = {'center_x':.85, 'center_y':.08}, duration = .3, t = 'in_out_circ')
        anim1.start(Mainscreenvar.ids.action_button)
        newlist = NewListBlueprint()
        newlist.opacity = 0
        newlist.ids.confirm_button.bind(on_press = partial(Creator.create_new_list, self))
        newlist.ids.cancel_button.bind(on_press = partial(Creator.cancel_new_list, self))
        current_card = 'ele' + str(counter)
        Mainscreenvar.ids[current_card].add_widget(newlist)
        anim2 = Animation(opacity = 1, duration = .3)
        anim2.start(newlist)


    def create_new_list(self, caller):
        Mainscreenvar = sm.get_screen("MainScreen")
        new_name = caller.parent.children[2].text
        if len(new_name) > 0 or not new_name == '':
            try:
                new_name = re.sub(r"[^\w\s]", '', new_name)
                new_name = re.sub(r"\s+", '_', new_name)
                mycursor.execute('''CREATE TABLE {} (title BLOB,
                description BLOB,
                date BLOB,
                time BLOB,
                alertlvl INTEGER NOT NULL,
                state INTEGER NOT NULL,
                rem_id INTEGER NOT NULL UNIQUE PRIMARY KEY,
                compdates BLOB)'''.format(new_name))
                Creator.reset_list_create(self, new_name)
                try:
                    plyer.vibrator.pattern(pattern = (0,.02,0.1,0.04,0.1,0.02))
                except:
                    pass

            except:
                toast("This list already exists")
                try:
                    plyer.vibrator.pattern(pattern = (0,.04,0.06,0.03,0.04,0.02,0.02,0.01,))
                except:
                    pass

        else:
            toast("Please enter a proper list name")
            try:
                plyer.vibrator.pattern(pattern = (0,.04,0.06,0.03,0.04,0.02,0.02,0.01,))
            except:
                pass


    def reset_list_create(self, new_name):
        global all_lists
        themes = {'a':'Slate', 'b':'DeadWood', 'c':'SnowWhite', 'd':'Candy', 'e':'PureWhite', 'f':'PureBlack'}
        if new_name in themes.keys():
            self.set_theme(themes[new_name])
            toast("Set theme to "+ themes[new_name])
        Mainscreenvar = sm.get_screen("MainScreen")
        anim2 = Animation(opacity = 1, duration = .3, t = 'in_out_circ')
        anim2.start(Mainscreenvar.ids.action_button)
        all_lists = []
        mycursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        data = mycursor.fetchall()
        for a in data:
            if a[0] == 'sqlite_sequence' or a[0] == new_name:
                pass
            else:
                all_lists.append(a[0])

        all_lists.sort()
        all_lists.insert(1, new_name)
        MainViewHandler.slider(self, 0, None)

    def cancel_new_list(self, instance):
        Mainscreenvar = sm.get_screen("MainScreen")
        Mainscreenvar.ids.action_button.opacity = 1
        if all_lists:
            MainViewHandler.slider(self,0, None)
        else:
            MainViewHandler.no_lists(self)

    def screen_switcher(self):
        sm.current = 'ReminderScreen'
        Clock.schedule_once(partial(Creator.load_heading,self), .3)

    def load_heading(self, instance):
        Remindervar = sm.get_screen('ReminderScreen')
        Remindervar.ids.scroll.scroll_y = 1
        Remindervar.ids.back_button.bind(on_release = Creator.back_op)
        Remindervar.ids.delete_button.opacity = 0
        self.heading.opacity = 0
        self.heading.ids.heading.text = ''
        Remindervar.ids.container.add_widget(self.heading)
        anim1 = Animation(opacity = 1, duration = .2)
        anim1.start(self.heading)
        Clock.schedule_once(partial(Creator.load_description,self), .2)

    def load_description(self, instance):
        Remindervar = sm.get_screen('ReminderScreen')
        self.description.opacity = 0
        self.description.ids.description.text = ''
        Remindervar.ids.container.add_widget(self.description)
        anim2 = Animation(opacity = 1, duration = .2)
        anim2.start(self.description)
        Clock.schedule_once(partial(Creator.load_timing, self),.3)

    def load_timing(self,instance):
        Remindervar = sm.get_screen('ReminderScreen')
        self.timing.ids.time_picker.text = 'Time'
        self.timing.ids.type_picker.text = 'None'
        self.timing.ids.type_picker.name = 'type_picker_creator'
        Remindervar.ids.container.add_widget(self.timing)
        Clock.schedule_once(partial(Creator.load_saving, self), .2)

    def changer(instance):
        self = Mainapp.get_running_app()
        self.reminder_type_menu_creator.dismiss()
        current_text = self.timing.ids.type_picker.text
        if instance == 'Days' and current_text != instance:
            self.timing.ids.days_container.orientation = 'horizontal'
            self.timing.ids.days_container.clear_widgets()
            if len(self.timing.ids.holder.children) == 5:
                self.timing.ids.holder.remove_widget(self.timing.ids.holder.children[0])
            data = [['M','Monday'],['T','Tuesday'],['W','Wednesday'],['T','Thursday'],['F','Friday'],['S','Saturday'],['S','Sunday']]
            Creator.day_adder(self,data)
        elif instance == 'Dates' and current_text != instance:
            self.timing.ids.days_container.orientation = 'vertical'
            self.timing.ids.days_container.clear_widgets()
            Creator.date_adder(self)
        elif instance == 'None' and current_text != instance:
            self.timing.ids.days_container.clear_widgets()
            if len(self.timing.ids.holder.children) == 5:
                self.timing.ids.holder.remove_widget(self.timing.ids.holder.children[0])

        self.timing.ids.type_picker.text = instance

    def day_adder(self, data, *args):
        Remindervar = sm.get_screen('ReminderScreen')
        if data:
            ele = MDChip(text = data[0][0],
                         selected_chip_color = (218/255,68/255,83/255,1),
                         color = (50/255,49/255,61/255,1),
                         icon = '',
                         name = data[0][1],
                         )
            self.timing.ids.days_container.add_widget(ele)
            del data[0]
            self.create_day_event = Clock.schedule_once(partial(Creator.day_adder, self, data), 0)
        else:
            self.create_day_event.cancel()
            self.created = True
            anim1 = Animation(opacity = 1, d = .3)
            anim1.start(self.timing)

    def date_adder(self,*args):
        Remindervar = sm.get_screen('ReminderScreen')
        plus_button = MDIconButton(icon = 'plus', md_bg_color = (218/255,68/255,83/255,1),
                                                        pos_hint = {'center_x':.5})
        plus_button.bind(on_release = partial(Creator.new_date_adder, self))
        self.timing.ids.holder.add_widget(plus_button)

    def new_date_adder(self, instance):
        ele = ReminderDatesBlueprint()
        ele.ids.date_picker.bind(on_release = partial(Creator.current_open_definer, self))
        ele.ids.remove_button.bind(on_release = partial(Creator.date_remover, self))
        ele.ids.date_picker.text = 'Choose a date'
        self.timing.ids.days_container.add_widget(ele)

    def date_remover(self, instance):
        instance.parent.parent.remove_widget(instance.parent)

    def current_open_definer(self, instance):
        self.date_picker.open()
        self.current_editing = instance


    def date_setter(self,date,date_range):
        self = MDApp.get_running_app()
        new_date = date.strftime('%x')
        for others in self.current_editing.parent.parent.children:
            if others.ids.date_picker.text == new_date:
                toast('This Reminder already rings on this date \n choose another date')
                break
        else:
            self.current_editing.text = new_date

    def load_saving(self, instance):
        Remindervar = sm.get_screen('ReminderScreen')
        self.saving.ids.save_button.bind(on_release = Creator.save)
        self.saving.ids.cancel_button.bind(on_release = Creator.back_op)
        Remindervar.ids.container.add_widget(self.saving)

    def save(instance):
        self = Mainapp.get_running_app()
        if self.heading.ids.heading.text.isspace() or self.heading.ids.heading.text == '':
            toast("Please enter a title")
            try:
                plyer.vibrator.pattern(pattern = (0,.04,0.06,0.03,0.04,0.02,0.02,0.01,))
            except:
                pass
        else:
            if self.timing.ids.type_picker == 'Days':
                if self.timing.ids.days_container.selected== [] or self.timing.ids.time_picker.text == 'Time':
                    toast('Please choose some days and time')
                    try:
                        plyer.vibrator.pattern(pattern = (0,.04,0.06,0.03,0.04,0.02,0.02,0.01,))
                    except:
                        pass
                else:
                    Creator.saver(self)
            elif self.timing.ids.type_picker == 'Dates':
                if not len(self.timing.ids.days_container.children) or self.timing.ids.time_picker.text == 'Time':
                    toast("Please select a date and a time")
                    try:
                        plyer.vibrator.pattern(pattern = (0,.04,0.06,0.03,0.04,0.02,0.02,0.01,))
                    except:
                        pass
                else:
                    Creator.saver(self)
            else:
                Creator.saver(self)
    def saver(self):
        new_dates = []
        new_reminder_id = random.randint(-32768, 32768)
        if self.timing.ids.type_picker.text == 'Days':
            for day in self.timing.ids.days_container.children:
                if day.active == True:
                    new_dates.append(day.name)
        elif self.timing.ids.type_picker.text == 'Dates':
            for dates in self.timing.ids.days_container.children:
                new_dates.append(dates.ids.date_picker.text)
        else:
            new_dates = []
        text = self.description.ids.description.text
        if text.isspace() or text == '' and False:
            mycursor.execute( 'INSERT INTO {} (title,description,date,time,rem_id,compdates,alertlvl,state) VALUES("{}","{}","{}","{}",{},"[]",0,0)'.format(
                    current_list,
                    self.heading.ids.heading.text,
                    None,
                    new_dates,
                    self.timing.ids.time_picker.text,
                    new_reminder_id
            ))
        else:
            mycursor.execute( 'INSERT INTO {} (title,description,date,time,rem_id,compdates,alertlvl,state) VALUES("{}","{}","{}","{}",{},"[]",0,0)'.format(
                    current_list,
                    self.heading.ids.heading.text,
                    text,
                    new_dates,
                    self.timing.ids.time_picker.text,
                    new_reminder_id
            ))
        connection.commit()

        #Update the timing in the alarm manager
        if platform == 'android':
            if new_dates:
                 #Make sure we dont run the code if the reminder type is none
                if new_dates[0].isalpha():
                    AlarmDateTimeHandler.days_handler(self,new_dates, self.timing.ids.time_picker.text, new_reminder_id, 0)
                else:
                    AlarmDateTimeHandler.dates_handler(self,new_dates, self.timing.ids.time_picker.text,new_reminder_id, 0)
        try:
            plyer.vibrator.pattern(pattern = (0,.02,0.1,0.04,0.1,0.02))
        except:
            pass
        ListView.sort_list_data(self)
        Creator.back_op(self,None)
        ListView.heading_data_parser(self)
        if datetime.now().strftime('%x') in self.data_dict:
            ListView.current_date_reminder_data_parser(self,datetime.now().strftime('%x'))
        else:
            ListView.current_date_reminder_data_parser(self,'None')



    def back_op(instance, *args):
        self = Mainapp.get_running_app()
        Remindervar = sm.get_screen('ReminderScreen')
        Remindervar.ids.container.clear_widgets()
        self.timing.ids.days_container.clear_widgets()
        if len(self.timing.ids.holder.children) == 5:
            self.timing.ids.holder.remove_widget(self.timing.ids.holder.children[0])
        sm.current = 'MainScreen'
        sm.transition.direction = 'right'
        Remindervar.ids.back_button.unbind(on_release = Creator.back_op)
        self.saving.ids.save_button.unbind(on_release = Creator.save)
        self.saving.ids.cancel_button.unbind(on_release = Creator.back_op)

class AlarmDateTimeHandler():

    def dates_handler(self,dates,time, id, mode):
        intent_id = id
        reminder_id = id
        for alarm_date in dates:
            if mode == 0: #Just creating a new reminder no need to clear previous alarms
                ReminderScheduler.schedule(reminder_id, self.heading.ids.heading.text, self.description.ids.description.text, alarm_date, time, current_list, intent_id)
            else: #Old reminder is being edited so we have to clear older data and run new data
                if not eval(self.reminder_data[2]): #There is an empty list so we just continue to only add the new rings to the alarm manager
                    ReminderScheduler.schedule(reminder_id, self.heading.ids.heading.text, self.description.ids.description.text, alarm_date, time, current_list, intent_id)
                elif eval(self.reminder_data[2])[0].isalpha():
                    AlarmDateTimeHandler.remove_all(self,intent_id, True)
                    ReminderScheduler.schedule(reminder_id, self.heading.ids.heading.text, self.description.ids.description.text, alarm_date, time, current_list, intent_id)
                else:
                    AlarmDateTimeHandler.remove_all(self,intent_id,False)
                    ReminderScheduler.schedule(reminder_id, self.heading.ids.heading.text, self.description.ids.description.text, alarm_date, time, current_list, intent_id)
            intent_id+=1
        pass

    def remove_all(self, id, repeating):
        if repeating:
            ReminderScheduler.deschedule_repeating(id)
        else:
            ReminderScheduler.deschedule(id)

    def days_handler(self,days, time,id, mode):
        intent_id = id
        reminder_id = id
        #Now we convert the days into number values
        for alarm_day in days:
            if alarm_day == 'Monday':
                day_number = 2
            elif alarm_day == 'Tuesday':
                day_number = 3
            elif alarm_day == 'Wednesday':
                day_number = 4
            elif alarm_day == 'Thursday':
                day_number = 5
            elif alarm_day == 'Friday':
                day_number = 6
            elif alarm_day == 'Saturday':
                day_number = 7
            else:
                day_number = 1
            if mode ==0:
                ReminderScheduler.schedule_repeating(reminder_id, self.heading.ids.heading.text, self.description.ids.description.text, day_number,time, current_list, intent_id)
            else:
                if not eval(self.reminder_data[2]): #There is an empty list so we just continue to only add the new rings to the alarm manager
                    ReminderScheduler.schedule_repeating(reminder_id, self.heading.ids.heading.text, self.description.ids.description.text, day_number, time, current_list, intent_id)
                elif eval(self.reminder_data[2])[0].isalpha():
                    AlarmDateTimeHandler.remove_all(self,intent_id, True)
                    ReminderScheduler.schedule_repeating(reminder_id, self.heading.ids.heading.text, self.description.ids.description.text, day_number, time, current_list, intent_id)
                else:
                    AlarmDateTimeHandler.remove_all(self,intent_id, False)
                    ReminderScheduler.schedule_repeating(reminder_id, self.heading.ids.heading.text, self.description.ids.description.text, day_number, time, current_list, intent_id)
            intent_id+=1

class AndroidHandler():

    def back_operation_handler(self):
        global current_app_location, back_counter
        if current_app_location == 'IndividualListView':
            ListView.back_op(self, None)
        elif current_app_location == 'MainScreen':
            if back_counter == 1:
                toast("Press the back button once more to exit")
                back_counter+=1
            else:
                self.stop()

class NotificationHandler():

    def open_reminder(self,list,id):
        global current_list, current_app_location
        current_list = list
        current_app_location = 'MainScreen'
        sm.current = 'ReminderScreen'
        IndividualReminderView.heading_loader(self,id,1,None)

class ListReminderElement(BoxLayout):
    pass

class ListContent(RelativeLayout):
    pass

class ListBlueprint(DragBehavior ,MDCard):

    t = 0

    start_d = 0

    end_d = 0

    v_x = 0

    v_y = 0

    swipable = BooleanProperty(False)

    def on_touch_down(self, touch):
        # MainViewHandler.slider(self,0,None)
        if self.collide_point(*touch.pos):
            if self.swipable:
                self.clock = Clock.schedule_interval(self.time_ticker, .01)
                self.start_d = touch.pos
        return super(ListBlueprint, self).on_touch_down(touch)

    def time_ticker(self,*args):
        self.t+=1
        if self.t == 50:
            threading.Thread(target = MainViewHandler.load_behind_title(self), name = 'behind_title').start()
        if self.t == 100:
            threading.Thread(target = MainViewHandler.load_behind_reminder(self), name = 'behind_reminder').start()

    def on_touch_up(self, touch):
        # MainViewHandler.slider(self,0,None)
        if self.collide_point(*touch.pos):
            if self.swipable:
                try:
                    self.clock.cancel()
                    self.end_d= touch.pos
                    v_x = (self.start_d[0]-self.end_d[0])/self.t
                    v_y = (self.start_d[1]-self.end_d[1])/self.t
                    if abs(v_x)>40 or abs(v_y)>40 and all_lists:
                        if v_x<0:
                            anim1 = Animation(x = Window.width*2, d = .5)
                            anim1.start(self)
                            if v_y<0:
                                Animation(y = Window.height*2, d = .5).start(self)
                            else:
                                Animation(y = -Window.height*2, d= .5).start(self)
                        else:
                            anim1 = Animation(x = -Window.width*2, d = .5)
                            anim1.start(self)
                            if v_y<0:
                                Animation(y = Window.height*2, d = .5).start(self)
                            else:
                                Animation(y = -Window.height*2, d= .5).start(self)
                        Clock.schedule_once(partial(MainViewHandler.slider, self,0,None), .3)
                    else:
                        Animation(pos=(Window.center[0]-self.width/2,Window.center[1]-self.height/2), d = .25, t = 'in_out_circ').start(self)
                except:
                    pass

            self.t = 0
        return super(ListBlueprint, self).on_touch_up(touch)

class NewListBlueprint(RelativeLayout):
    pass

class MainScreen(Screen):
    pass

class ReminderScreen(Screen):
    pass

class ListViewContent(AKToolbarLayout):
    pass

class ListViewDateCards(RelativeLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.size_setter, 0)

    def size_setter(self, time):
        if self.active:
            self.size = (dp(120),dp(80))
            ListView.current_date_reminder_data_parser(self,self.name)

    def selected(self):
        #We have to reset the size for all other widgets
        app = Mainapp.get_running_app()
        for widget in self.parent.parent.data:
            if self.date != widget['date']: #Check to see if widget is the selected one
                widget['size'] = (dp(80),dp(80))
                widget['active'] = False
            else:
                widget['size'] = (dp(120),dp(80))
                widget['active'] = True
                ListView.current_date_reminder_data_parser(self,self.name)

        self.parent.parent.refresh_from_data()
        pass

class ListViewListContentCardBlueprint(RecycleView):
    pass

class ListViewReminderElement(MDCard):

    def on_touch_down(self, touch):
        if super(ListViewReminderElement, self).collide_point(*touch.pos):
            if self.text == ' ' or self.text == 'Completed \nReminders':
                pass
            else:
                x = self.ids.container.to_local(*touch.pos)
                app = Mainapp.get_running_app()
                if not self.ids.check_box.collide_point(x[0],x[1]):
                    app = Mainapp.get_running_app()
                    IndividualReminderView.screen_switcher(app,self.name)
                else:
                    ListView.mark_complete(self)

class ReminderTitleBlueprint(MDCard):
    pass

class ReminderDescriptionBlueprint(MDCard):
    pass

class ReminderTimingBlueprint(MDCard):
    pass

class CustomListObject(OneLineAvatarIconListItem):
    left_icon = StringProperty()


class ReminderDaySelector(MDChipContainer):
    pass

class ReminderDatesBlueprint(BoxLayout):
    pass

class ReminderAlertBlueprint(MDCard):
    pass

class ReminderSaveBlueprint(MDCard):
    pass

class CustomButton(Label):

    def on_touch_down(self,touch):
        if super(CustomButton, self).collide_point(*touch.pos):
            app = Mainapp.get_running_app()
            if self.name == 'type_picker_viewer':
                app.reminder_type_menu_viewer.open()
            elif self.name == 'type_picker_creator':
                app.reminder_type_menu_creator.open()
            elif self.name == 'time_picker':
                app.time_picker.open()
            elif self.name == 'date_element':
                app.date_picker.open()
    pass

class ScreenManagerMain(ScreenManager):
    pass

counter = 1
all_lists = []
current_list = None
current_app_location = 'MainScreen'
back_counter = 1
sm = ScreenManagerMain(transition = CardTransition(direction = 'left'))

class Mainapp(MDApp, ThemeManager):

    def build(self):
        Builder.load_file("reminder.kv")
        Window.bind(on_keyboard=self.on_key)
        sm.add_widget(MainScreen(name = 'MainScreen'))
        sm.add_widget(ReminderScreen(name = 'ReminderScreen'))
        return sm

    def on_receive(self):
        if platform != 'android':
            return
        intent = mActivity.getIntent()
        start = intent.getShortExtra("LAUNCH_APP_WITH_REMINDER",0)
        if start == 0:
            return
        else: # This means we need to show that reminder screen
            list = intent.getStringExtra("CURRENT_LIST")
            id = intent.getShortExtra("LAUNCH_APP_WITH_REMINDER", 0)
            NotificationHandler.open_reminder(self,list,id)

    def on_start(self):
        #Create this widgets ahead of time to increase performance
        self.heading = ReminderTitleBlueprint()
        self.description = ReminderDescriptionBlueprint()
        self.time_picker = MDTimePicker()
        self.date_picker = MDDatePicker(min_year = 2021, max_year = 2022)
        self.timing = ReminderTimingBlueprint()
        self.time_picker.primary_color = (50/255,49/255,61/255,1)
        self.time_picker.selector_color = (218/255,68/255,83/255,1)
        self.time_picker.accent_color = (50/255,49/255,61/255,1)
        self.time_picker.bind(on_save = IndividualReminderView.time_setter)
        self.date_picker.bind(on_save = IndividualReminderView.date_setter)
        self.timing.ids.time_picker.bind(on_press = self.time_picker.open)
        self.created = False
        self.timing.opacity = 1
        self.menu_items_viewer = [
        {
            "text": "None",
            "viewclass": "CustomListObject",
            "on_release": partial(IndividualReminderView.type_switcher, "None"),
            "text_color": self.accent_color,
            "theme_text_color": "Custom",
            'left_icon':'close-circle-outline'
        },
        {
            "text": "Dates",
            "viewclass": "CustomListObject",
            "on_release": partial(IndividualReminderView.type_switcher, "Dates"),
            "text_color": self.accent_color,
            "theme_text_color": "Custom",
            'left_icon':'calendar'
        },
        {
            "text": "Days",
            "viewclass": "CustomListObject",
            "on_release": partial(IndividualReminderView.type_switcher, "Days"),
            "text_color": self.accent_color,
            "theme_text_color": "Custom",
            'left_icon':'calendar-refresh'
        },
        ]

        self.reminder_type_menu_viewer = MDDropdownMenu(
            caller=self.timing.ids.type_picker,
            items=self.menu_items_viewer,
            width_mult=4,
            background_color = self.primary_color,
        )
        self.menu_items_creator = [
        {
            "text": "None",
            "viewclass": "CustomListObject",
            "on_release": partial(Creator.changer, "None"),
            "text_color": self.accent_color,
            "theme_text_color": "Custom",
            'left_icon':'close-circle-outline'
        },
        {
            "text": "Dates",
            "viewclass": "CustomListObject",
            "on_release": partial(Creator.changer, "Dates"),
            "text_color": self.accent_color,
            "theme_text_color": "Custom",
            'left_icon':'calendar'
        },
        {
            "text": "Days",
            "viewclass": "CustomListObject",
            "on_release": partial(Creator.changer, "Days"),
            "text_color": self.accent_color,
            "theme_text_color": "Custom",
            'left_icon':'calendar-refresh'
        },
        ]
        self.reminder_type_menu_creator = MDDropdownMenu(
            caller=self.timing.ids.type_picker,
            items=self.menu_items_creator,
            width_mult=4,
            background_color = self.primary_color,
        )
        self.alertness_level = ReminderAlertBlueprint()
        self.saving = ReminderSaveBlueprint()
        self.on_receive()
        self.loaded_behind_reminders = False
        MainViewHandler.all_lists_loader(self)

    def plus_button_callback(self):
        if current_app_location == 'MainScreen':
            if all_lists:
                MainViewHandler.slider(self, 2, None)
            else:
                MainViewHandler.slider(self, 1, None)
        else:
            Creator.screen_switcher(self,)

    def on_key(self, window, key, scancode, codepoint, modifier):
        if key == 27:  # the esc key
            AndroidHandler.back_operation_handler(self)
            return True
        else:
            return False

    def checker(self, instance):
        ListView.reminder_complete_handler(self,instance)

if platform != 'android':
    Window.size = (360,640)

if __name__ == '__main__':
    Mainapp().run()
