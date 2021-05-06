from kivy.config import Config
Config.set('modules', 'monitor', ' ')
Config.set('graphics', 'maxfps', '100')
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDFloatingActionButtonSpeedDial
from kivymd.toast import toast
from kivymd.uix.button import MDIconButton
from kivymd.uix.picker import MDTimePicker, MDDatePicker
from kivymd.uix.chip import MDChipContainer, MDChip

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import platform
from kivy.uix.screenmanager import Screen, ScreenManager, CardTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.animation import Animation
from kivy.clock import Clock

import gesture_box as gesture
from functools import partial
import sqlite3
import collections
import plyer
import threading

import time
import datetime
import re


connection = sqlite3.connect('reminder.db')

mycursor = connection.cursor()

class MainViewHandler():

    def all_lists_loader(self, mode):
        global all_lists
        mycursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        data = mycursor.fetchall()
        all_lists = []
        for a in data:
            if a[0] == 'sqlite_sequence':
                pass
            else:
                all_lists.append(a[0])
        all_lists.sort()
        if mode==0:
            MainViewHandler.first_list_loader(self)
        elif mode == 1:
            pass

    def first_list_loader(self):
        Mainscreenvar = sm.get_screen("MainScreen")
        sm.bind(on_swipe_down = partial(MainViewHandler.slider, self, 0))
        self.list_content = ListContent()
        self.list_content.ids.heading.text = all_lists[0].replace("_"," ")
        self.list_content.ids.view_button.bind(on_press = partial(OpenListView.list_view_loader_transition, self))
        Mainscreenvar.ids.ele1.children[0].add_widget(self.list_content)
        mycursor.execute("SELECT * FROM {} ORDER BY creation_order DESC LIMIT 6".format(all_lists[0]))
        data = mycursor.fetchall()
        for a in data:
            self.list_reminder_element = ListReminderElement()
            if a[1].isspace():
                text_to = '[font=Roboto-Black.ttf][size=18sp]' + a[0] + '[/size][/font]'
            else:
                text_to = '[font=Roboto-Black.ttf][size=18sp]' + a[0] + '[/size][/font]' + '\n' + \
                '[font=Roboto-Regular.ttf][size=16sp][color=#808080]' + a[1] + '[/color][/size][/font]'
            self.list_reminder_element.ids.text.text = text_to
            self.list_reminder_element.ids.check_box.bind(on_press = partial(MainViewHandler.reminder_complete_handler, self))
            self.list_reminder_element.name = a[4]
            if a[6] == 1:
                self.list_reminder_element.completed = True
                self.list_reminder_element.ids.text.strikethrough = True
            self.list_content.ids.reminder_container.add_widget(self.list_reminder_element)


    def slider(self,operation, ele):
        global counter, swiping
        if swiping == False:
            swiping = True
            Mainscreenvar = sm.get_screen("MainScreen")
            anim1 = Animation(pos_hint = {'center_x':.5, "center_y":-1}, duration = .3, t= 'in_out_circ')
            card_to_drop = "ele{}".format(counter)
            anim1.start(Mainscreenvar.ids[card_to_drop].children[0])
            anim1.bind(on_complete = partial(MainViewHandler.swapper,self, operation))
            try:
                plyer.vibrator.vibrate(0.02)
            except:
                pass
            Mainscreenvar.ids[card_to_drop].children[0].clear_widgets()

    def swapper(self,operation,anim,caller):
        global counter, all_lists, swiping
        Mainscreenvar = sm.get_screen("MainScreen")
        if counter+1 == 4:
            card1_to_edit = 'ele1'
        else:
            card1_to_edit = 'ele{}'.format(counter+1)
        anim1 = Animation(pos_hint = {'center_x':.5, "center_y":.5}, elevation = 13, size_hint =(.85, .70),
                          duration = .3, md_bg_color = (50/255,49/255,61/255,1),  )
        anim2 = Animation(angle = 0, duration = .4,  )
        anim1.start(Mainscreenvar.ids[card1_to_edit].children[0])
        anim2.start(Mainscreenvar.ids[card1_to_edit].canvas.before.children[-1])
        if counter+2 == 4:
            card2_to_edit = 'ele1'
        elif counter+2 == 5:
            card2_to_edit = 'ele2'
        else:
            card2_to_edit = 'ele{}'.format(counter+2)

        anim3 = Animation(pos_hint = {'center_x':.45, "center_y":.5}, elevation = 0, size_hint =(.78, .70),
                          duration = .5, md_bg_color = (70/255,69/255,81/255,1),)
        anim4 = Animation(angle = 3, duration = .5,  )
        anim3.start(Mainscreenvar.ids[card2_to_edit].children[0])
        anim4.start(Mainscreenvar.ids[card2_to_edit].canvas.before.children[-1])
        new_card_id = "ele{}".format(counter)
        new_card = Mainscreenvar.ids[new_card_id]
        new_card_blueprint = ListBlueprint()
        new_card_blueprint.pos_hint = {'center_x':.1, "center_y":.5}
        new_card_blueprint.size_hint = (.73,.70)
        new_card_blueprint.md_bg_color = (90/255,89/255,101/255,1)
        new_card_blueprint.opacity = 0
        anim5 = Animation(angle = 5, duration = .2,  )
        anim6 = Animation(opacity = 1, pos_hint = {'center_x':.42, "center_y":.5}, duration = .4,  )
        anim5.start(Mainscreenvar.ids[new_card_id].canvas.before.children[-1])
        anim6.start(new_card_blueprint)
        Mainscreenvar.remove_widget(Mainscreenvar.ids[new_card_id])
        Mainscreenvar.add_widget(new_card, 4)
        new_card.add_widget(new_card_blueprint)
        if counter != 3:
            counter +=1
        else:
            counter = 1

        if operation == 0:
            ele = collections.deque(all_lists)
            ele.rotate(-1)
            all_lists = ele
            swiping = False
            Clock.schedule_once(partial(MainViewHandler.load_next_list_title,self, 0),.2)
        elif operation == 1:
            swiping = False
            Creator.create_new_list_load_ui(self)

    def load_next_list_title(self, delay, *args):
        mycursor.execute("SELECT * FROM {} ORDER BY creation_order DESC LIMIT 6".format(all_lists[0]))
        data = mycursor.fetchall()
        Mainscreenvar = sm.get_screen("MainScreen")
        card_to_add_to = 'ele{}'.format(counter)
        self.list_content = ListContent()
        self.list_content.ids.heading.text = all_lists[0].replace('_', ' ')
        self.list_content.ids.view_button.bind(on_press = partial(OpenListView.list_view_loader_transition, self))
        Mainscreenvar.ids[card_to_add_to].children[0].add_widget(self.list_content)
        if delay == 0:
            event = Clock.schedule_once(partial(MainViewHandler.load_next_list_reminders,self,data),.4)
        else:
            event = Clock.schedule_once(partial(MainViewHandler.load_next_list_reminders, self, data), delay)

    def load_next_list_reminders(self, data, *args):
        global swiping
        self.list_content.ids.reminder_container.opacity =0
        for a in data:
            list_reminder_element = ListReminderElement()
            list_reminder_element.ids.check_box.bind(on_press = partial(MainViewHandler.reminder_complete_handler, self))
            list_reminder_element.name = a[4]
            if not a[1].isspace():
                text_to = '[font=Roboto-Black.ttf][size=18sp]' + a[0] + '[/size][/font]' + '\n' + \
                '[font=Roboto-Regular.ttf][size=16sp][color=#808080]' + a[1] + '[/color][/size][/font]'
            else:
                text_to = '[font=Roboto-Black.ttf][size=18sp]' + a[0] + '[/size][/font]'
            list_reminder_element.ids.text.text = text_to
            if a[6] == 1:
                list_reminder_element.completed = True
                list_reminder_element.ids.text.strikethrough = True
            self.list_content.ids.reminder_container.add_widget(list_reminder_element)
            swiping = False

        anim1 = Animation(opacity = 1, duration = .5)
        anim1.start(self.list_content.ids.reminder_container)

    def reminder_complete_handler(self, instance):
        if instance.parent.completed == False:
            instance.parent.completed = True
            instance.parent.ids.text.strikethrough = True
            mycursor.execute("UPDATE {} SET state = 1 WHERE creation_order = {}".format(all_lists[0], instance.parent.name))
            connection.commit()
        else:
            instance.parent.completed = False
            instance.parent.ids.text.strikethrough = False
            mycursor.execute("UPDATE {} SET state = 0 WHERE creation_order = {}".format(all_lists[0], instance.parent.name))
            connection.commit()


    def vibration_handler(self,value,caller,anim_object):
        try:
            plyer.vibrator.vibrate(value)
        except:
            pass

class OpenListView():

    def list_view_loader_transition(self, caller):
        global current_list
        current_list = all_lists[0]
        Mainscreenvar = sm.get_screen("MainScreen")
        anim1 = Animation(size_hint = (1,1), radius=(0,0,0,0), duration = .5, t = 'in_out_circ')
        anim2 = Animation(pos_hint = {'center_x':.5, 'center_y':-2}, duration = .7, t = 'in_out_circ')
        anim3 = Animation(pos_hint = {'center_x':.5, 'center_y':-2}, duration = .9, t = 'in_out_circ')
        anim3.bind(on_complete = partial(OpenListView.list_view_loader, self))
        anim1.start(Mainscreenvar.children[1].children[0])
        anim2.start(Mainscreenvar.children[2].children[0])
        anim3.start(Mainscreenvar.children[3].children[0])
        name = 'ele{}'.format(counter)
        Mainscreenvar.ids[name].children[0].clear_widgets()
        threading.Thread(target = partial(OpenListView.sort_by_creation, self), name = 'loader').start()



    def list_view_loader(self,anim_object,caller):
        global swiping, current_app_location
        Mainscreenvar = sm.get_screen("MainScreen")
        name = 'ele{}'.format(counter)
        self.list_view_banner = ListViewBanner()
        self.list_view_banner.ids.back_button.bind(on_press = partial(OpenListView.back_op, self))
        self.list_view_banner.ids.delete_button.bind(on_press = partial(OpenListView.list_deleter, self))
        self.list_view_banner.ids.list_title.text = current_list.replace("_", " ")
        Mainscreenvar.ids[name].children[0].add_widget(self.list_view_banner)
        Mainscreenvar.ids[name].children[0].add_widget(self.list_view_element)
        swiping = True
        current_app_location = 'IndividualListView'
    def sort_by_creation(self):
        connection = sqlite3.connect('reminder.db')
        mycursor = connection.cursor()
        mycursor.execute("SELECT * FROM {} ORDER BY creation_order DESC".format(current_list))
        data = mycursor.fetchall()
        completed_reminders = []
        not_completed_reminders = []
        for a in range(len(data)):
            if data[0][6] == 1 or data[0][6] == '1':
                ele = data.pop(0)
                completed_reminders.append(ele)
            else:
                ele = data.pop(0)
                not_completed_reminders.append(ele)
        data = not_completed_reminders + completed_reminders
        self.list_view_element = ListViewBlueprint()
        reminders_data_list = []
        count = 0
        for reminder in data:
            if reminder[1] != None:
                if reminder[6] == 0:
                    ele = {'text_title':reminder[0], 'text_description':reminder[1],
                            'md_bg_color':(0,0,0,0), 'elevation':0,'name':reminder[4]}

                elif reminder[6] == 1 and count == 0:
                    heading_ele = {'text_title':'Completed Reminders',
                            'md_bg_color':(218/255,68/255,83/255, 1), 'elevation':12,
                            'show_button':0,'padding':(50,0,50,0), 'alignment':'center',
                            'font':'Roboto-Black.ttf', 'fontsize':'22sp'}
                    reminders_data_list.append(heading_ele)
                    ele = {'text_title':reminder[0], 'text_description':reminder[1],
                            'md_bg_color':(0,0,0,0), 'elevation':0,'completed':True,
                            'name':reminder[4]}
                    count = 1

                elif reminder[6] == 1 and count == 1:
                    ele = {'text_title':reminder[0], 'text_description':reminder[1],
                            'md_bg_color':(0,0,0,0), 'elevation':0,'completed':True,
                            'name':reminder[4]}

            else:
                if reminder[6] == 0:
                    ele = {'text_title':reminder[0],
                            'md_bg_color':(0,0,0,0), 'elevation':0, 'name':reminder[4]}

                elif reminder[6] == 1 and count == 0:
                    heading_ele = {'text_title':'Completed Reminders',
                            'md_bg_color':(218/255,68/255,83/255, 1), 'elevation':12,
                            'show_button':0, 'padding':(50,0,50,0), 'alignment':'center',
                            'font':'Roboto-Black.ttf', 'fontsize':'22sp'}
                    reminders_data_list.append(heading_ele)
                    ele = {'text_title':reminder[0],'md_bg_color':(0,0,0,0),
                            'elevation':0, 'completed':True, 'name':reminder[4]}
                    count = 1

                elif reminder[6] == 1 and count == 1:
                    ele = {'text_title':reminder[0],'md_bg_color':(0,0,0,0),
                            'elevation':0, 'completed':True, 'name':reminder[4]}
            reminders_data_list.append(ele)
        self.list_view_element.data = reminders_data_list
        connection.close()


    def back_op(self,caller):
        global swiping, current_app_location
        Mainscreenvar = sm.get_screen("MainScreen")
        anim1 = Animation(size_hint = (.85,.70), radius=(60,60,60,60), duration = .5, t = 'in_out_circ')
        anim2 = Animation(pos_hint = {'center_x':.45, 'center_y':.5}, duration = .7, t = 'in_out_circ')
        anim3 = Animation(pos_hint = {'center_x':.42, 'center_y':.5}, duration = .9, t = 'in_out_circ')
        name = 'ele{}'.format(counter)
        anim1.start(Mainscreenvar.ids[name].children[0])
        anim2.start(Mainscreenvar.children[2].children[0])
        anim3.start(Mainscreenvar.children[3].children[0])
        Mainscreenvar.ids[name].children[0].clear_widgets()
        current_app_location = 'MainScreen'
        MainViewHandler.load_next_list_title(self, 1)


    def list_deleter(self, caller):
        mycursor.execute("DROP TABLE {}".format(current_list))
        MainViewHandler.all_lists_loader(self, 1)
        OpenListView.back_op(self,None)

class IndividualReminderView():
    def screen_switcher(self,reminder):
        sm.current = 'ReminderScreen'
        Clock.schedule_once(partial(IndividualReminderView.heading_loader, self, reminder),.4)

    def heading_loader(self, reminder, instance):
        Remindervar = sm.get_screen('ReminderScreen')
        self.current_reminder = reminder
        Remindervar.ids.back_button.bind(on_press= partial(IndividualReminderView.back_op, self))
        mycursor.execute("SELECT * FROM {} WHERE creation_order = {}".format(current_list, reminder))
        self.reminder_data = mycursor.fetchone()
        self.heading.opacity = 0
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
        self.timing.ids.type.bind(selected = IndividualReminderView.type_switcher)
        self.reminder_dates=eval(self.reminder_data[2])
        self.timing.ids.time_picker.text = self.reminder_data[3]
        self.time_picker.set_time(datetime.datetime.strptime(self.reminder_data[3], '%I:%M %p'))
        if not self.reminder_dates[0]:
            #This means the reminder will not have any date to ring on
            self.timing.ids.days.active = False
            self.timing.ids.dates.active = False
            self.timing.ids.none.active = True

        elif self.reminder_dates[0].isalpha():
            #This means we have days for the reminder to ring on
            self.timing.ids.days.active = True
            self.timing.ids.dates.active = False
            self.timing.ids.none.active = False
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
            self.timing.ids.dates.active = True
            self.timing.ids.days.active = False
            self.timing.ids.none.active = False
            self.timing.ids.days_container.orientation = 'vertical'
            data = list(self.reminder_dates)
            plus_button = MDIconButton(icon = 'plus', md_bg_color = (218/255,68/255,83/255,1),
                                                            pos_hint = {'center_x':.5})
            plus_button.bind(on_release = partial(IndividualReminderView.new_date_adder, self))
            self.timing.ids.holder.add_widget(plus_button)
            self.create_date_event = Clock.schedule_once(partial(IndividualReminderView.date_adder, self, data), 0)
            Clock.schedule_once(partial(IndividualReminderView.save_adder, self), .2)

    def save_adder(self,*args):
        Remindervar = sm.get_screen('ReminderScreen')
        self.saving.ids.save_button.bind(on_release = IndividualReminderView.changes_checker)
        self.saving.ids.cancel_button.bind(on_release = partial(IndividualReminderView.back_op,self))
        Remindervar.ids.container.add_widget(self.saving)

    def day_adder(self, data, *args):
        Remindervar = sm.get_screen('ReminderScreen')
        if data:
            ele = MDChip(text = data[0][0],
                         selected_chip_color = (218/255,68/255,83/255,1),
                         color = (50/255,49/255,61/255,1),
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

    def type_switcher(instance, value):
        self = MDApp.get_running_app()
        if 'Dates' in value and self.created:
            self.timing.ids.days_container.clear_widgets()
            self.timing.ids.days_container.orientation = 'vertical'
            plus_button = MDIconButton(icon = 'plus', md_bg_color = (218/255,68/255,83/255,1),
                                                            pos_hint = {'center_x':.5})
            plus_button.bind(on_release = partial(IndividualReminderView.new_date_adder, self))
            self.timing.ids.holder.add_widget(plus_button)

        elif 'Days' in value and self.created:
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

        elif 'None' in value and self.created:
            self.timing.ids.days_container.clear_widgets()
            if len(self.timing.ids.holder.children) == 5:
                self.timing.ids.holder.remove_widget(self.timing.ids.holder.children[0])

    def back_op(self, caller):
        Remindervar = sm.get_screen('ReminderScreen')
        self.timing.ids.type.unbind(selected = IndividualReminderView.type_switcher)
        Remindervar.ids.container.clear_widgets()
        self.timing.ids.days_container.clear_widgets()
        if len(self.timing.ids.holder.children) == 5:
            self.timing.ids.holder.remove_widget(self.timing.ids.holder.children[0])
        sm.current = 'MainScreen'
        sm.transition.direction = 'right'
        self.created = False

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
        mycursor.execute("DELETE FROM {} WHERE creation_order = {}".format(current_list, self.current_reminder))
        if self.description.ids.description.text == '' or self.description.ids.description.text.isspace():
            insert_command = 'INSERT INTO {} (title,description,date, time, color, state) VALUES("{}"," ","{}","{}", 0, 0)'.format(
                                current_list, self.heading.ids.heading.text,
                                self.new_timings,
                                self.timing.ids.time_picker.text
                                )
        else:
            insert_command = 'INSERT INTO {} (title,description,date, time, color, state) VALUES("{}","{}","{}","{}", 0, 0)'.format(
                                current_list, self.heading.ids.heading.text,
                                self.description.ids.description.text, self.new_timings,
                                self.timing.ids.time_picker.text
                                )
        mycursor.execute(insert_command)
        connection.commit()
        IndividualReminderView.back_op(self, None)

    def changes_checker(*args):
        self = MDApp.get_running_app()
        self.new_timings = []
        saveable = False
        if self.timing.ids.days.active:
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
        elif self.timing.ids.dates.active:
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
        if saveable:
            if (self.reminder_data[0] == self.heading.ids.heading.text and
                self.reminder_data[1] == self.description.ids.description.text and
                self.reminder_data[3] == self.timing.ids.time_picker.text and
                self.reminder_dates == self.new_timings):
                    IndividualReminderView.back_op(self, None)
            else:
                IndividualReminderView.save_reminder(self, None)

class Creator():
    def create_new_list_load_ui(self):
        Mainscreenvar = sm.get_screen("MainScreen")
        Mainscreenvar.ids.action_button.close_stack()
        anim1 = Animation(opacity = 0, duration = .3, t = 'in_out_circ')
        anim1.start(Mainscreenvar.ids.action_button)
        newlist = NewListBlueprint()
        newlist.ids.confirm_button.bind(on_press = partial(Creator.create_new_list, self))
        newlist.ids.cancel_button.bind(on_press = partial(Creator.cancel_new_list, self))
        current_card = 'ele' + str(counter)
        Mainscreenvar.ids[current_card].children[0].add_widget(newlist)

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
                creation_order INTEGER PRIMARY KEY AUTOINCREMENT,
                color INTEGER NOT NULL,
                state INTEGER NOT NULL)'''.format(new_name))

            except:
                toast("This list already exists")

            Creator.reset_list_create(self, new_name)

        else:
            toast("Please enter a proper list name")

    def reset_list_create(self, new_name):
        Mainscreenvar = sm.get_screen("MainScreen")
        anim1 = Animation(size_hint = (.85,.70), radius=(60,60,60,60), pos_hint = {'center_x':.5, 'center_y':.5}, duration = .5, t = 'in_out_circ')
        anim2 = Animation(opacity = 1, duration = .3, t = 'in_out_circ')
        anim2.start(Mainscreenvar.ids.action_button)
        card_to_edit = 'ele' + str(counter)
        global all_lists
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
        MainViewHandler.slider(self,0, None)

    def screen_switcher(self):
        sm.current = 'ReminderScreen'
        Clock.schedule_once(partial(Creator.load_heading,self), .3)

    def load_heading(self, instance):
        Remindervar = sm.get_screen('ReminderScreen')
        Remindervar.ids.back_button.bind(on_press= partial(IndividualReminderView.back_op, self))
        self.heading.opacity = 0
        Remindervar.ids.container.add_widget(self.heading)
        anim1 = Animation(opacity = 1, duration = .2)
        anim1.start(self.heading)
        Clock.schedule_once(partial(Creator.load_description,self), .2)

    def load_description(self, instance):
        Remindervar = sm.get_screen('ReminderScreen')
        self.description.opacity = 0
        Remindervar.ids.container.add_widget(self.description)
        anim2 = Animation(opacity = 1, duration = .2)
        anim2.start(self.description)
        Clock.schedule_once(partial(Creator.load_timing, self),.3)

    def load_timing(self,instance):
        Remindervar = sm.get_screen('ReminderScreen')
        Remindervar.ids.container.add_widget(self.timing)
        Clock.schedule_once(partial(Creator.load_saving, self),.3)

    def changer(self, instance, value):
        print(value)
        if value == ['Days']:
            data = [['M','Monday'],['T','Tuesday'],['W','Wednesday'],['T','Thursday'],['F','Friday'],['S','Saturday'],['S','Sunday']]
            Creator.day_adder(self,data)
        elif value == ['Dates']:
            Creator.date_adder(self)

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
            self.create_day_event = Clock.schedule_once(partial(IndividualReminderView.day_adder, self, data), 0)
        else:
            self.create_day_event.cancel()
            self.created = True
            anim1 = Animation(opacity = 1, d = .3)
            anim1.start(self.timing)


    def load_saving(self, instance):
        Remindervar = sm.get_screen('ReminderScreen')
        Remindervar.ids.container.add_widget(self.saving)

class AndroidHandler():

    def back_operation_handler(self):
        global current_app_location, back_counter
        if current_app_location == 'IndividualListView':
            OpenListView.back_op(self, None)
        elif current_app_location == 'MainScreen':
            if back_counter == 1:
                toast("Press the back button once more to exit")
                back_counter+=1
            else:
                self.stop()

class ListReminderElement(BoxLayout):
    pass

class ListContent(RelativeLayout):
    pass

class ListBlueprint(MDCard):
    pass

class ListViewBanner(MDCard):
    pass

class ListViewBlueprint(RecycleView):
    pass

class IndivualReminderElementBlueprint(BoxLayout):
    def on_touch_down(self, touch):
        if super(IndivualReminderElementBlueprint, self).collide_point(*touch.pos):
            if not self.ids.check_box.collide_point(*touch.pos):
                app = MDApp.get_running_app()
                sm.transition.direction = 'left'
                IndividualReminderView.screen_switcher(app,self.name)

class IndividualListViewContentBlueprint(BoxLayout):
    pass

class NewListBlueprint(RelativeLayout):
    pass

class SelectableRecycleBoxLayout(RecycleBoxLayout):
    pass

class MainScreen(Screen):
    pass

class ReminderScreen(Screen):
    pass

class ReminderTitleBlueprint(MDCard):
    pass

class ReminderDescriptionBlueprint(MDCard):
    pass

class ReminderTimingBlueprint(MDCard):
    pass

class ReminderDaySelector(MDChipContainer):
    pass

class ReminderDatesBlueprint(GridLayout):
    pass

class ReminderSaveBlueprint(MDCard):
    pass

class ScreenManagerMain(ScreenManager, gesture.GestureBox):
    pass

counter = 1
all_lists = []
current_list = None
swiping = False
current_app_location = 'MainScreen'
back_counter = 1
sm = ScreenManagerMain(transition = CardTransition(direction = 'left'))
class Mainapp(MDApp):
    def build(self):
        Builder.load_file("reminder.kv")
        self.data = {'New Reminder':'alarm',
                'New List':'format-list-checkbox'}
        Window.bind(on_keyboard=self.on_key)
        sm.add_widget(MainScreen(name = 'MainScreen'))
        sm.add_widget(ReminderScreen(name = 'ReminderScreen'))
        return sm


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
        self.saving = ReminderSaveBlueprint()
        MainViewHandler.all_lists_loader(self, 0)



    def plus_button_callback(self, instance):
        if instance.icon == 'alarm':
            Creator.screen_switcher(self,)
        elif instance.icon == 'format-list-checkbox':
            MainViewHandler.slider(self, 1, None)

    def on_key(self, window, key, scancode, codepoint, modifier):
        if key == 27:  # the esc key
            AndroidHandler.back_operation_handler(self)
            return True
        else:
            return False


if platform != 'android':
    Window.size = (360,640)
Mainapp().run()
