from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDFloatingActionButtonSpeedDial
from kivymd.toast import toast
from kivymd.uix.button import MDIconButton

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import platform
from kivy.uix.screenmanager import Screen, ScreenManager, FallOutTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout
from kivy.animation import Animation
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty

from kivy.uix.recycleview import RecycleView



import gesture_box as gesture
from functools import partial
import sqlite3
import collections
import plyer
import threading

from time import time
import re


connection = sqlite3.connect('reminder.db')

mycursor = connection.cursor()

class MainViewHandler():

    def program_loader(self):
        global all_lists
        mycursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        data = mycursor.fetchall()
        for a in data:
            if a[0] == 'sqlite_sequence':
                pass
            else:
                all_lists.append(a[0])
        all_lists.sort()
        MainViewHandler.first_list_loader(self)



    def first_list_loader(self):
        Mainscreenvar = self.runner_object.ids.screen_manager.get_screen("MainScreen")
        self.runner_object.bind(on_swipe_down = partial(MainViewHandler.slider, self, 0))
        self.list_content = ListContent()
        self.list_content.ids.heading.text = all_lists[0].replace("_"," ")
        self.list_content.ids.view_button.bind(on_press = partial(OpenListView.list_view_loader_transition, self))
        Mainscreenvar.ids.ele1.children[0].add_widget(self.list_content)
        mycursor.execute("SELECT * FROM {} ORDER BY creation_order DESC LIMIT 6".format(all_lists[0]))
        data = mycursor.fetchall()
        for a in data:
            self.list_reminder_element = ListReminderElement()
            self.list_reminder_element.ids.title.text = a[0]
            self.list_reminder_element.ids.check_box.bind(on_press = partial(MainViewHandler.reminder_complete_handler, self))
            self.list_reminder_element.name = a[4]
            if a[1] != None:
                self.list_reminder_element.ids.desc.text = a[1]
            self.list_content.ids.reminder_container.add_widget(self.list_reminder_element)

        self.action_button = DoActionButton()
        Mainscreenvar.add_widget(self.action_button)

    def slider(self,operation, ele):
        global counter, swiping
        if swiping == False:
            swiping = True
            Mainscreenvar = self.runner_object.ids.screen_manager.get_screen("MainScreen")
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
        Mainscreenvar = self.runner_object.ids.screen_manager.get_screen("MainScreen")
        if counter+1 == 4:
            card1_to_edit = 'ele1'
        else:
            card1_to_edit = 'ele{}'.format(counter+1)
        anim1 = Animation(pos_hint = {'center_x':.5, "center_y":.5}, elevation = 13, size_hint =(.85, .70),
                          duration = .3, md_bg_color = (50/255,49/255,61/255,1))
        anim2 = Animation(angle = 0, duration = .4)
        anim1.start(Mainscreenvar.ids[card1_to_edit].children[0])
        anim2.start(Mainscreenvar.ids[card1_to_edit].canvas.before.children[-1])
        if counter+2 == 4:
            card2_to_edit = 'ele1'
        elif counter+2 == 5:
            card2_to_edit = 'ele2'
        else:
            card2_to_edit = 'ele{}'.format(counter+2)

        anim3 = Animation(pos_hint = {'center_x':.45, "center_y":.5}, elevation = 0, size_hint =(.78, .70),
                          duration = .5, md_bg_color = (70/255,69/255,81/255,1))
        anim4 = Animation(angle = 3, duration = .5)
        anim3.start(Mainscreenvar.ids[card2_to_edit].children[0])
        anim4.start(Mainscreenvar.ids[card2_to_edit].canvas.before.children[-1])
        new_card_id = "ele{}".format(counter)
        new_card = Mainscreenvar.ids[new_card_id]
        new_card_blueprint = ListBlueprint()
        new_card_blueprint.pos_hint = {'center_x':.1, "center_y":.5}
        new_card_blueprint.size_hint = (.73,.70)
        new_card_blueprint.md_bg_color = (90/255,89/255,101/255,1)
        new_card_blueprint.opacity = 0
        anim5 = Animation(angle = 5, duration = .2)
        anim6 = Animation(opacity = 1, pos_hint = {'center_x':.42, "center_y":.5}, duration = .4, t= 'in_out_circ')
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
            Clock.schedule_once(partial(MainViewHandler.load_next_list_title,self, 0),.2)
        elif operation == 1:
            swiping = False
            Creator.create_new_list_load_ui(self)

    def load_next_list_title(self, delay, *args):
        mycursor.execute("SELECT * FROM {} ORDER BY creation_order DESC LIMIT 6".format(all_lists[0]))
        data = mycursor.fetchall()
        Mainscreenvar = self.runner_object.ids.screen_manager.get_screen("MainScreen")
        card_to_add_to = 'ele{}'.format(counter)
        self.list_content = ListContent()
        self.list_content.ids.heading.text = all_lists[0].replace('_', ' ')
        self.list_content.ids.view_button.bind(on_press = partial(OpenListView.list_view_loader_transition, self))
        Mainscreenvar.ids[card_to_add_to].children[0].add_widget(self.list_content)
        if delay == 0:
            event = Clock.schedule_once(partial(MainViewHandler.load_next_list_reminders,self,data), .2)
        else:
            event = Clock.schedule_once(partial(MainViewHandler.load_next_list_reminders, self, data), delay)


    def load_next_list_reminders(self, data, *args):
        global swiping
        if len(data) != 0:
            list_reminder_element = ListReminderElement()
            list_reminder_element.ids.check_box.bind(on_press = partial(MainViewHandler.reminder_complete_handler, self))
            list_reminder_element.opacity = 0
            list_reminder_element.ids.title.text = data[0][0]
            list_reminder_element.name = data[0][4]
            if data[0][1] != None:
                list_reminder_element.ids.desc.text = data[0][1]

            self.list_content.ids.reminder_container.add_widget(list_reminder_element)
            anim1 = Animation(opacity= 1, duration = .1, )
            anim1.start(list_reminder_element)
            del data[0]
            Clock.schedule_once(partial(MainViewHandler.load_next_list_reminders,self,data), .1)
        else:
            swiping = False


    def reminder_complete_handler(self, instance):
        if instance.parent.ids.title.strikethrough == False:
            instance.parent.ids.title.strikethrough = True
            instance.parent.ids.desc.strikethrough = True
            mycursor.execute("UPDATE {} SET state = 1 WHERE creation_order = {}".format(all_lists[0], instance.parent.name))
            connection.commit()
        else:
            instance.parent.ids.title.strikethrough = False
            instance.parent.ids.desc.strikethrough = False
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
        Mainscreenvar = self.runner_object.ids.screen_manager.get_screen("MainScreen")
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
        Mainscreenvar = self.runner_object.ids.screen_manager.get_screen("MainScreen")
        name = 'ele{}'.format(counter)
        self.list_view_banner = ListViewBanner()
        self.list_view_banner.ids.back_button.bind(on_press = partial(OpenListView.back_op, self))
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
        for a in data:
            if a[6] == 1:
                completed_reminders.append(a)
                data.remove(a)
        data.extend(completed_reminders)
        self.list_view_element = ListViewBlueprint()
        reminders_data_list = []
        print(completed_reminders)
        # for reminder in data:
        #     if reminder[1] != None:
        #         if reminder[6] == 0:
        #             ele = {'text_title':reminder[0], 'text_description':reminder[1],
        #                     'md_bg_color':(0,0,0,0), 'elevation':0}
        #         elif reminder[6] == 1:
        #             ele = {'text_title':reminder[0], 'text_description':reminder[1],
        #                     'md_bg_color':(0,0,0,0), 'elevation':0, 'completed':True}
        #     else:
        #         if reminder[6] == 0:
        #             ele = {'text_title':reminder[0],
        #                     'md_bg_color':(0,0,0,0), 'elevation':0}
        #         elif reminder[6] == 1:
        #             ele = {'text_title':reminder[0],
        #                     'md_bg_color':(0,0,0,0), 'elevation':0, 'completed':True}
        #     reminders_data_list.append(ele)

        self.list_view_element.data = reminders_data_list
        connection.close()


    def sort_by_date(self):
        data = mycursor.execute("SELECT * FROM {}".format(current_list))




    def back_op(self, caller):
        global swiping, current_app_location
        self.list_view_element.clear_widgets()
        Mainscreenvar = self.runner_object.ids.screen_manager.get_screen("MainScreen")
        anim1 = Animation(size_hint = (.85,.70), radius=(60,60,60,60), duration = .5, t = 'in_out_circ')
        anim2 = Animation(pos_hint = {'center_x':.45, 'center_y':.5}, duration = .7, t = 'in_out_circ')
        anim3 = Animation(pos_hint = {'center_x':.42, 'center_y':.5}, duration = .9, t = 'in_out_circ')
        name = 'ele{}'.format(counter)
        anim1.start(Mainscreenvar.ids[name].children[0])
        anim2.start(Mainscreenvar.children[2].children[0])
        anim3.start(Mainscreenvar.children[3].children[0])
        Mainscreenvar.ids[name].children[0].clear_widgets()
        MainViewHandler.load_next_list_title(self, 1)
        current_app_location = 'MainScreen'





class Creator():

    def create_new_list_load_ui(self):
        self.action_button.close_stack()
        anim1 = Animation(opacity = 0, duration = .3, t = 'in_out_circ')
        anim1.start(self.action_button)
        Mainscreenvar = self.runner_object.ids.screen_manager.get_screen("MainScreen")
        newlist = NewListBlueprint()
        newlist.ids.confirm_button.bind(on_press = partial(Creator.create_new_list, self))
        newlist.ids.cancel_button.bind(on_press = partial(Creator.cancel_new_list, self))
        current_card = 'ele' + str(counter)
        Mainscreenvar.ids[current_card].children[0].add_widget(newlist)

    def create_new_list(self, caller):
        Mainscreenvar = self.runner_object.ids.screen_manager.get_screen("MainScreen")
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
        Mainscreenvar = self.runner_object.ids.screen_manager.get_screen("MainScreen")
        anim1 = Animation(size_hint = (.85,.70), radius=(60,60,60,60), pos_hint = {'center_x':.5, 'center_y':.5}, duration = .5, t = 'in_out_circ')
        anim2 = Animation(opacity = 1, duration = .3, t = 'in_out_circ')
        anim2.start(self.action_button)
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
        self.action_button.opacity = 1
        MainViewHandler.slider(self,0, None)



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






class Runner(gesture.GestureBox):
    pass

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


class NewListBlueprint(RelativeLayout):
    pass

class DoActionButton(MDFloatingActionButtonSpeedDial):
    pass

class MainScreen(Screen):
    pass

class ListViewScreen(Screen):
    pass


counter = 1
all_lists = []
current_list = None
swiping = False
current_app_location = 'MainScreen'
back_counter = 1

class Mainapp(MDApp):

    def build(self):
        Builder.load_file("reminder.kv")
        self.data = {'alarm': 'New Reminder',
                'format-list-checkbox': 'New List',}
        Window.bind(on_keyboard=self.on_key)
        self.runner_object = Runner()
        return self.runner_object


    def on_start(self):
        MainViewHandler.program_loader(self)

    def plus_button_callback(self, instance):
        if instance.icon == 'alarm':
            pass
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
