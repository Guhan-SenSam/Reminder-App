package org.org.remindy;

import android.content.BroadcastReceiver;
import android.content.Intent;
import android.content.Context;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Notification;
import android.app.PendingIntent;
import android.os.Build;
import android.os.Bundle;
import org.kivy.android.PythonActivity;
import android.media.RingtoneManager;
import android.net.Uri;
import android.media.AudioAttributes;
import org.remindy.remindy.R.drawable;
import java.util.Calendar;
import android.app.AlarmManager;

public class ReminderRepeatingAlarmReceiver extends BroadcastReceiver{

        private void createNotificationChannel(Context context, Intent intent) {


        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            Uri sound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);

            AudioAttributes att = new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_NOTIFICATION)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .build();

            CharSequence name = "CAR_LOCATOR_ALARM";
            String description = "Parking alarm";
            int importance = NotificationManager.IMPORTANCE_HIGH;
            NotificationChannel channel = new NotificationChannel("CAR_LOCATOR_ALARM", name, importance);
            channel.setDescription(description);
            channel.setSound(sound, att);
            channel.enableLights(true);
            channel.enableVibration(true);
            NotificationManager notificationManager = context.getSystemService(NotificationManager.class);
            notificationManager.createNotificationChannel(channel);

            Uri uri= RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);


            String contentTitle = intent.getExtras().getString("TITLE");
            String contentDescription =intent.getExtras().getString("DESCRIPTION");

            Notification n = new Notification.Builder(context, "CAR_LOCATOR_ALARM")
                    .setSmallIcon(drawable.icon)
                    .setContentTitle(contentTitle)
                    .setContentText(String.valueOf(contentDescription))
                    .setTicker(String.valueOf(contentDescription))
                    .setVibrate(new long[]{0, 300, 0, 400, 0, 500})
                    .setSound(uri)
                    .setAutoCancel(true)
                    .setOnlyAlertOnce(true).build();
            notificationManager.notify(0,n);

            // We then proceed to reschedule the alarm on the system level alarm manager

            PendingIntent newdaypending = PendingIntent.getBroadcast(context, intent.getExtras().getShort("IDENTIFICATION"), intent, PendingIntent.FLAG_CANCEL_CURRENT);
            Calendar calendar = Calendar.getInstance();
            Long timetoring = calendar.getTimeInMillis() + 7*24*60*60*1000;
            AlarmManager alarmManager=(AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
            alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,timetoring, newdaypending);
        }
    }


    @Override
    public void onReceive(Context context, Intent intent) {
        this.createNotificationChannel(context, intent);
    }
}
