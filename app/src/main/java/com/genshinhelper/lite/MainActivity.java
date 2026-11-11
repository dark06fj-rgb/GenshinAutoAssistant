package com.genshinhelper.lite;

import android.content.Intent;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(0xFF17151D);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(22), dp(30), dp(22), dp(22));
        root.setBackgroundColor(0xFF17151D);

        TextView title = new TextView(this);
        title.setText("مساعد تعريب الألعاب");
        title.setTextColor(0xFFFFFFFF);
        title.setTextSize(23);
        title.setGravity(Gravity.CENTER);
        root.addView(title, new LinearLayout.LayoutParams(-1, dp(64)));

        TextView intro = new TextView(this);
        intro.setText("المرحلة الأولى: فحص ملفات نصية تختارها بنفسك من الجهاز.\n\nالفحص محلي وقراءة فقط؛ لا يلتقط الشاشة، ولا يعرض نافذة عائمة، ولا يغيّر ملفات اللعبة.");
        intro.setTextColor(0xFFD8D2E2);
        intro.setTextSize(16);
        intro.setPadding(0, dp(18), 0, dp(22));
        root.addView(intro);

        Button probe = new Button(this);
        probe.setText("اختيار ملفات التصدير وفحصها");
        probe.setOnClickListener(v -> startActivity(new Intent(this, AssetProbeActivity.class)));
        root.addView(probe, new LinearLayout.LayoutParams(-1, dp(56)));

        TextView status = new TextView(this);
        status.setText("لا يتم إرسال الملفات إلى أي خادم.");
        status.setTextColor(0xFFB8E6C1);
        status.setTextSize(14);
        status.setPadding(0, dp(22), 0, 0);
        root.addView(status);
        setContentView(root);
    }

    private int dp(int value) {
        return (int)(value * getResources().getDisplayMetrics().density + 0.5f);
    }
}
