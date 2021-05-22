package org.org.remindy;

import android.content.BroadcastReceiver;
import android.content.Intent;
import android.content.Context;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;
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

            private void createNotificationChannel(Context context) {

                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                    Uri sound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);

                    AudioAttributes att = new AudioAttributes.Builder()
                            .setUsage(AudioAttributes.USAGE_NOTIFICATION)
                            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                            .build();

                    CharSequence name = "New Reminder";
                    String description = "New Reminder";
                    int importance = NotificationManager.IMPORTANCE_HIGH;
                    NotificationChannel channel = new NotificationChannel("REMINDY", name, importance);
                    channel.setDescription(description);
                    channel.setSound(sound, att);
                    channel.enableLights(true);
                    channel.enableVibration(true);
                    NotificationManager notificationManager = context.getSystemService(NotificationManager.class);
                    notificationManager.createNotificationChannel(channel);
                }
            }

            private void sendNotification(Context context, Intent intent) {
                Uri uri= RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
                Intent newintent = new Intent(context, PythonActivity.class);
                Short id = intent.getShortExtra("IDENTIFICATION", (short) 0);
                String current_list = intent.getStringExtra("CURRENT_LIST");
                newintent.putExtra("LAUNCH_APP_WITH_REMINDER", id);
                newintent.putExtra("CURRENT_LIST",current_list);
                PendingIntent pendingintent = PendingIntent.getActivity(context,id, newintent, PendingIntent.FLAG_ONE_SHOT);

                NotificationCompat.Builder builder = new NotificationCompat.Builder(context, "REMINDY")
                        .setSmallIcon(drawable.icon)
                        .setContentTitle(intent.getExtras().getString("TITLE"))
                        .setContentText(intent.getExtras().getString("DESCRIPTION"))
                        .setTicker("New Reminder")
                        .setVibrate(new long[]{0, 300, 0, 400, 0, 500})
                        .setSound(uri)
                        .setAutoCancel(true)
                        .setOnlyAlertOnce(false)
                        .setPriority(NotificationCompat.PRIORITY_HIGH)
                        .setContentIntent(pendingintent);

                NotificationManagerCompat notificationManager = NotificationManagerCompat.from(context);
                notificationManager.notify(192837, builder.build());

                    // We then proceed to reschedule the alarm on the system level alarm manager

                    PendingIntent newdaypending = PendingIntent.getBroadcast(context, intent.getExtras().getShort("IDENTIFICATION"), intent, PendingIntent.FLAG_CANCEL_CURRENT);
                    Calendar calendar = Calendar.getInstance();
                    Long timetoring = calendar.getTimeInMillis() + 7*24*60*60*1000;
                    AlarmManager alarmManager=(AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
                    alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,timetoring, newdaypending);

            }



    @Override
    public void onReceive(Context context, Intent intent) {
        this.createNotificationChannel(context);
        this.sendNotification(context, intent);
    }
}
