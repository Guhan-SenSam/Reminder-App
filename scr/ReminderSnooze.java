package org.org.remindy;

import android.content.BroadcastReceiver;
import android.content.Intent;
import android.content.Context;
import android.app.PendingIntent;
import java.util.Calendar;
import android.app.AlarmManager;
import androidx.core.app.NotificationManagerCompat;
import android.widget.Toast;

public class ReminderSnooze extends BroadcastReceiver{

    @Override
    public void onReceive(Context context, Intent intent) {

      Intent snoozedrem = new Intent(context,ReminderAlarmReceiver.class);
      snoozedrem.putExtra("TITLE", intent.getExtras().getString("TITLE"));
      snoozedrem.putExtra("DESCRIPTION", intent.getExtras().getString("DESCRIPTION"));
      snoozedrem.putExtra("IDENTIFICATION", intent.getExtras().getShort("IDENTIFICATION"));
      snoozedrem.putExtra("CURRENT_LIST", intent.getExtras().getString("CURRENT_LIST"));
      snoozedrem.putExtra("INTENT_ID", intent.getExtras().getShort("INTENT_ID"));
      PendingIntent pendingsnoozedrem = PendingIntent.getBroadcast(context, intent.getExtras().getShort("INTENT_ID"), snoozedrem, PendingIntent.FLAG_CANCEL_CURRENT);
      Calendar calendar = Calendar.getInstance();
      Long timetoring = calendar.getTimeInMillis() + 10*60*60*1000;
      AlarmManager alarmManager=(AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
      alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,timetoring, pendingsnoozedrem);

      //Now clear the notification from the bar

      NotificationManagerCompat notificationManager = NotificationManagerCompat.from(context);
      notificationManager.cancel(intent.getExtras().getInt("NOTIFICATION_ID"));

      //Give a toast to the user
      Toast toast = Toast.makeText(context, "Snoozed for 10 mins", Toast.LENGTH_SHORT);
      toast.show();

    }
}
