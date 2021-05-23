package org.org.remindy;

import android.content.BroadcastReceiver;
import android.content.Intent;
import android.content.Context;

import android.database.sqlite.SQLiteDatabase;
import android.content.ContentValues;
import androidx.core.app.NotificationManagerCompat;
import android.widget.Toast;


public class ReminderMarkComp extends BroadcastReceiver{

    @Override
    public void onReceive(Context context, Intent intent) {
    SQLiteDatabase db = SQLiteDatabase.openDatabase("/data/data/org.remindy.remindy/files/app/reminder.db",null,SQLiteDatabase.OPEN_READWRITE);
    db.beginTransaction();
    ContentValues cv = new ContentValues();
    cv.put("state",1);
    String id = String.valueOf(intent.getShortExtra("IDENTIFICATION", (short) 0));
    long result = db.update(intent.getExtras().getString("CURRENT_LIST"), cv, "rem_id ="+ id , null);
    db.setTransactionSuccessful();
    db.endTransaction();
    //Now remove the notification from panel
    NotificationManagerCompat notificationManager = NotificationManagerCompat.from(context);
    notificationManager.cancel(intent.getExtras().getInt("NOTIFICATION_ID"));
    //Show a toast to the user
    Toast toast = Toast.makeText(context, "Remider Marked Complete", Toast.LENGTH_SHORT);
    toast.show();
    }
}
