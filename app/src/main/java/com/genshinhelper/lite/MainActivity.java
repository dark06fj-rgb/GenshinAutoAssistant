package com.genshinhelper.lite;

import android.content.ComponentName;
import android.content.Intent;
import android.provider.Settings;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.text.TextUtils;
import android.content.Context;

import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    private TextView status;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(0xFF17151D);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(22), dp(30), dp(22), dp(22));
        root.setBackgroundColor(0xFF17151D);

        TextView title = new TextView(this);
        title.setText("مترجم الألعاب التلقائي");
        title.setTextColor(0xFFFFFFFF);
        title.setTextSize(23);
        title.setGravity(Gravity.CENTER);
        root.addView(title, new LinearLayout.LayoutParams(-1, dp(64)));

        TextView intro = new TextView(this);
        intro.setText("يراقب نصوص Genshin Impact التي يتيحها نظام Android لخدمات إمكانية الوصول، ويتعرف على لغتها ثم يترجمها إلى العربية ويحفظها محلياً. لا يحتاج إلى صور أو نافذة عائمة.");
        intro.setTextColor(0xFFD8D2E2);
        intro.setTextSize(15);
        intro.setPadding(0, dp(18), 0, dp(20));
        root.addView(intro);

        status = new TextView(this);
        status.setTextColor(0xFFFFD18A);
        status.setTextSize(14);
        status.setPadding(0, 0, 0, dp(14));
        root.addView(status);

        Button enable = new Button(this);
        enable.setText("تفعيل التعرف التلقائي");
        enable.setOnClickListener(v -> startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)));
        root.addView(enable, new LinearLayout.LayoutParams(-1, dp(54)));

        Button history = new Button(this);
        history.setText("عرض الترجمات المحفوظة");
        history.setOnClickListener(v -> startActivity(new Intent(this, TranslationLogActivity.class)));
        LinearLayout.LayoutParams historyParams = new LinearLayout.LayoutParams(-1, dp(54));
        historyParams.topMargin = dp(10);
        root.addView(history, historyParams);

        TextView privacy = new TextView(this);
        privacy.setText("الخصوصية: الخدمة مقيّدة بحزم Genshin المعروفة، وتتجاهل حقول كلمات المرور. قد يلزم تنزيل نموذج اللغة والترجمة أول مرة. لا تغيّر نص اللعبة الأصلي؛ تعرض الترجمات داخل هذا التطبيق فقط إذا كانت اللعبة لا تكشف نصوصها للنظام.");
        privacy.setTextColor(0xFFB8E6C1);
        privacy.setTextSize(13);
        privacy.setPadding(0, dp(20), 0, 0);
        root.addView(privacy);
        setContentView(root);
    }

    @Override protected void onResume() {
        super.onResume();
        if (status != null) {
            status.setText(isObserverEnabled()
                    ? "الحالة: التعرف التلقائي مفعّل"
                    : "الحالة: يحتاج إلى تفعيل خدمة إمكانية الوصول");
        }
    }

    private boolean isObserverEnabled() {
        String expected = new ComponentName(this, GameTextAccessibilityService.class).flattenToString();
        String enabled = Settings.Secure.getString(getContentResolver(),
                Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);
        return !TextUtils.isEmpty(enabled) && enabled.toLowerCase().contains(expected.toLowerCase());
    }

    private int dp(int value) {
        return (int)(value * getResources().getDisplayMetrics().density + 0.5f);
    }
}
