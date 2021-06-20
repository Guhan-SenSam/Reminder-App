package org.org.remindy;

import android.app.Activity;
import android.os.Bundle;
import org.remindy.remindy.R;
import android.os.Build;
import android.view.WindowManager;
import android.content.Context;
import android.app.KeyguardManager;

public class FullScreenNotify extends Activity {

  public void onCreate(Bundle savedInstanceState) {
    //Set parameters to ensure device is woken up
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O_MR1) {
        setShowWhenLocked(true);
        setTurnScreenOn(true);
        this.getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        KeyguardManager keyguardManager = (KeyguardManager) getSystemService(Context.KEYGUARD_SERVICE);
            keyguardManager.requestDismissKeyguard(this, null);


    } else {
      this.getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN |
                        WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED |
                        WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON,
                WindowManager.LayoutParams.FLAG_FULLSCREEN |
                        WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED |
                        WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON |
                        WindowManager.LayoutParams.FLAG_DISMISS_KEYGUARD);

    };
    super.onCreate(savedInstanceState);
    // Load xml file
    setContentView(R.layout.fullscreenalarm);

  }

}
