package com.genshinhelper.lite;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.media.projection.MediaProjectionManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    private static final int REQUEST_CAPTURE = 41;
    private TextView status;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(0xFF17151D);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(22), dp(30), dp(22), dp(22));
        root.setBackgroundColor(0xFF17151D);
        TextView title = new TextView(this);
        title.setText("Genshin Resource & Translate"); title.setTextColor(0xFFFFFFFF); title.setTextSize(23); title.setGravity(Gravity.CENTER);
        root.addView(title, new LinearLayout.LayoutParams(-1, dp(64)));
        TextView intro = new TextView(this);
        intro.setText("نسخة جديدة وخفيفة\n1) قراءة النص الظاهر وترجمته للعربية\n2) تجهيز أساس آمن لميزة كشف الموارد المرئي\n\nلن يبدأ التقاط الشاشة إلا بعد موافقتك.");
        intro.setTextColor(0xFFD8D2E2); intro.setTextSize(16); intro.setPadding(0, dp(18), 0, dp(22));
        root.addView(intro);
        Button probe = new Button(this); probe.setText("فحص ملفات التصدير دون نوافذ عائمة");
        probe.setOnClickListener(v -> startActivity(new Intent(this, AssetProbeActivity.class)));
        root.addView(probe, new LinearLayout.LayoutParams(-1, dp(54)));
        Button overlay = new Button(this); overlay.setText("السماح بالنافذة العائمة");
        overlay.setOnClickListener(v -> { if (!Settings.canDrawOverlays(this)) { Intent i = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:" + getPackageName())); startActivity(i); } else setStatus("إذن النافذة العائمة مفعل."); });
        root.addView(overlay, new LinearLayout.LayoutParams(-1, dp(52)));
        Button start = new Button(this); start.setText("بدء الترجمة المباشرة");
        start.setOnClickListener(v -> requestCapture());
        LinearLayout.LayoutParams bp = new LinearLayout.LayoutParams(-1, dp(56)); bp.topMargin = dp(12); root.addView(start, bp);
        Button stop = new Button(this); stop.setText("إيقاف"); stop.setOnClickListener(v -> { stopService(new Intent(this, CaptureService.class)); setStatus("تم إرسال أمر الإيقاف."); });
        root.addView(stop, bp);
        status = new TextView(this); status.setTextColor(0xFFB8E6C1); status.setTextSize(14); status.setPadding(0, dp(22), 0, 0); status.setText("الحالة: جاهز"); root.addView(status);
        setContentView(root);
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission("android.permission.POST_NOTIFICATIONS") != android.content.pm.PackageManager.PERMISSION_GRANTED) requestPermissions(new String[]{"android.permission.POST_NOTIFICATIONS"}, 42);
    }

    private void requestCapture() {
        if (!Settings.canDrawOverlays(this)) { setStatus("فعّل إذن النافذة العائمة أولاً."); startActivity(new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:" + getPackageName()))); return; }
        MediaProjectionManager manager = (MediaProjectionManager) getSystemService(Context.MEDIA_PROJECTION_SERVICE);
        startActivityForResult(manager.createScreenCaptureIntent(), REQUEST_CAPTURE);
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_CAPTURE) {
            if (resultCode == Activity.RESULT_OK && data != null) {
                Intent service = new Intent(this, CaptureService.class).putExtra("resultCode", resultCode).putExtra("data", data);
                if (Build.VERSION.SDK_INT >= 26) startForegroundService(service); else startService(service);
                setStatus("بدأ التقاط الشاشة. افتح اللعبة واترك الإشعار ظاهراً.");
            } else setStatus("لم تمنح إذن التقاط الشاشة.");
        }
    }
    private void setStatus(String value) { if (status != null) status.setText("الحالة: " + value); }
    private int dp(int v) { return (int)(v * getResources().getDisplayMetrics().density + 0.5f); }
}
