import os
import time
from datetime import datetime
from string import Template
try:
    from jnius import cast, autoclass

except KeyError:
     os.environ['JDK_HOME'] = "/usr/lib/jvm/java-1.8.0-openjdk-amd64"
     os.environ['JAVA_HOME'] = "/usr/lib/jvm/java-1.8.0-openjdk-amd64"
     from jnius import autoclass

#Import necessary Java classes

mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
Intent = autoclass('android.content.Intent')
AlarmManager = autoclass('android.app.AlarmManager')
PendingIntent = autoclass('android.app.PendingIntent')
Context = autoclass('android.content.Context')
ReminderAlarmReceiver = autoclass('org.org.remindy.ReminderAlarmReceiver')
ReminderRepeatingAlarmReceiver = autoclass('org.org.remindy.ReminderRepeatingAlarmReceiver')
context = mActivity.getApplicationContext()
String = autoclass('java.lang.String')
mapping = {'Y': 'yyyy', 'm': 'MM', 'd': 'dd', 'H': 'HH', 'M': 'mm'}
Calendar = autoclass('java.util.Calendar')
TimeZone = autoclass('java.util.TimeZone')
SimpleDateFormat = autoclass('java.text.SimpleDateFormat')
ParsePosition = autoclass('java.text.ParsePosition')
Date = autoclass('java.util.Date')

#Create alarm manager object


class ReminderScheduler():
    #To update a reminder just overwrite existing reminder

    def schedule(reminder_id,title,description,date_to_ring,time_to_ring,current_list,intent_id):
        #Create Intent and add required properties to it
        newdate = Intent()
        newdate.setClass(context, ReminderAlarmReceiver)
        newdate.setAction('org.org.remindy.ACTION_START_REMINDER')
        newdate.putExtra("TITLE", String(title))
        newdate.putExtra("DESCRIPTION", String(description))
        newdate.putExtra("IDENTIFICATION", reminder_id)
        newdate.putExtra("INTENT_ID", intent_id)
        newdate.putExtra("CURRENT_LIST", String(current_list))
        newdatepending = PendingIntent.getBroadcast(context,intent_id,newdate,PendingIntent.FLAG_CANCEL_CURRENT)

        #Create datetime string in python in the format for date object of java
        datetime_string = datetime.strptime(date_to_ring+ ' '+time_to_ring, "%x %I:%M %p").strftime("%Y-%m-%d %H:%M")

        #Calculate time for reminder to ring
        formatted_string = Template(datetime_string.replace('%', '$')).substitute(**mapping)
        formatted_string +=":00"
        convertor = SimpleDateFormat("yyyy-MM-dd HH:mm:ss") #Convert to java data type
        parsed_object = convertor.parse(formatted_string, ParsePosition(0))

        #Create alarm manager
        cast(AlarmManager, context.getSystemService(Context.ALARM_SERVICE)).setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,parsed_object.getTime(), newdatepending)


    def deschedule(id):
        deletedate = Intent()
        deletedate.setClass(context, ReminderAlarmReceiver)
        deletedate.setAction('org.org.remindy.ACTION_START_REMINDER')
        newdatepending = PendingIntent.getBroadcast(context,id,deletedate,  PendingIntent.FLAG_CANCEL_CURRENT)
        cast(AlarmManager, context.getSystemService(Context.ALARM_SERVICE)).cancel(newdatepending)

    def schedule_repeating(reminder_id,title,description,day_to_ring, time_to_ring, current_list, intent_id):

        #Create Intent and add required properties to it
        newday = Intent()
        newday.setClass(context, ReminderRepeatingAlarmReceiver)
        newday.setAction('org.org.remindy.ACTION_START_REMINDER_REPEATING')
        newday.putExtra("TITLE", String(title))
        newday.putExtra("DESCRIPTION", String(description))
        newday.putExtra("IDENTIFICATION", reminder_id)
        newday.putExtra("INTENT_ID", intent_id)
        newday.putExtra("CURRENT_LIST", String(current_list))
        newdaypending = PendingIntent.getBroadcast(context,reminder_id,newday,  PendingIntent.FLAG_CANCEL_CURRENT)

        time = datetime.strptime(time_to_ring,"%I:%M %p").strftime("%H:%M")

        calender= Calendar.getInstance()
        calender.set(Calendar.DAY_OF_WEEK, day_to_ring)
        calender.set(Calendar.HOUR_OF_DAY, int(time[0:2]))
        calender.set(Calendar.MINUTE, int(time[3:]))
        calender.set(Calendar.SECOND, 0)
        calender.set(Calendar.MILLISECOND, 0)
        if Calendar.getInstance().getTimeInMillis() > calender.getTimeInMillis():
            calender.add(Calendar.DATE, 7)
        #We have to reset the alarm every time it rings as there is no other way to set an exact repeating alarm
        cast(AlarmManager, context.getSystemService(Context.ALARM_SERVICE)).setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,calender.getTimeInMillis(), newdaypending)

    def deschedule_repeating(id):
        deleteday = Intent()
        deleteday.setClass(context, ReminderRepeatingAlarmReceiver)
        deleteday.setAction('org.org.remindy.ACTION_START_REMINDER_REPEATING')
        newdaypending = PendingIntent.getBroadcast(context,id,deleteday,  PendingIntent.FLAG_CANCEL_CURRENT)
        cast(AlarmManager, context.getSystemService(Context.ALARM_SERVICE)).cancel(newdaypending)
