package com.genshinhelper.lite;

import android.os.Bundle;
import android.view.Gravity;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import org.json.JSONArray;
import org.json.JSONObject;

import java.text.DateFormat;
import java.util.Date;

public class TranslationLogActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(18), dp(20), dp(18), dp(20));
        root.setBackgroundColor(0xFF17151D);

        TextView title = new TextView(this);
        title.setText("الترجمات المكتشفة");
        title.setTextColor(0xFFFFFFFF);
        title.setTextSize(22);
        title.setGravity(Gravity.CENTER);
        root.addView(title, new LinearLayout.LayoutParams(-1, dp(58)));

        ScrollView scroll = new ScrollView(this);
        LinearLayout list = new LinearLayout(this);
        list.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(list);
        root.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));

        try {
            JSONArray entries = new JSONArray(getSharedPreferences("game_translation_log", MODE_PRIVATE)
                    .getString("entries", "[]"));
            if (entries.length() == 0) {
                add(list, "لا توجد ترجمات بعد. فعّل خدمة التعرف، ثم افتح اللعبة المدعومة.", 0xFFD8D2E2);
            }
            for (int i = 0; i < entries.length(); i++) {
                JSONObject entry = entries.getJSONObject(i);
                long time = entry.optLong("time", 0);
                add(list, entry.optString("arabic"), 0xFFFFFFFF);
                add(list, entry.optString("original"), 0xFFB9B1C7);
                add(list, entry.optString("language", "").toUpperCase()
                        + " • " + DateFormat.getTimeInstance(DateFormat.SHORT).format(new Date(time)),
                        0xFF8F879C);
                TextView spacer = new TextView(this);
                spacer.setHeight(dp(10));
                list.addView(spacer);
            }
        } catch (Exception ignored) {
            add(list, "تعذر قراءة سجل الترجمات.", 0xFFFFB4AB);
        }
        setContentView(root);
    }

    private void add(LinearLayout parent, String value, int color) {
        TextView text = new TextView(this);
        text.setText(value);
        text.setTextColor(color);
        text.setTextSize(15);
        text.setTextIsSelectable(true);
        text.setPadding(dp(8), dp(7), dp(8), dp(7));
        parent.addView(text);
    }

    private int dp(int value) {
        return (int) (value * getResources().getDisplayMetrics().density + 0.5f);
    }
}
