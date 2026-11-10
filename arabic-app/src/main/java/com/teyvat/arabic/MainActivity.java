package com.teyvat.arabic;

import android.app.Activity;
import android.graphics.Typeface;
import android.graphics.Color;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class MainActivity extends Activity {
    private static final int BG = Color.rgb(17, 21, 34);
    private static final int PANEL = Color.rgb(29, 36, 55);
    private static final int GOLD = Color.rgb(235, 196, 112);
    private static final int WHITE = Color.rgb(245, 246, 250);

    private static final Catalog[] CATALOGS = {
        new Catalog("الشخصيات", "characters.json"),
        new Catalog("المواهب", "talents.json"),
        new Catalog("الأسلحة", "weapons.json"),
        new Catalog("الآثار", "artifacts.json"),
        new Catalog("المواد", "materials.json"),
        new Catalog("الموارد", "resources.json"),
        new Catalog("مهام الآركون", "quests_archon.json"),
        new Catalog("مهام العالم", "quests_world.json"),
        new Catalog("المصطلحات", "glossary.json")
    };

    private final List<JSONObject> records = new ArrayList<>();
    private LinearLayout list;
    private TextView count;
    private EditText search;
    private int selected = 0;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(BG);
        getWindow().setNavigationBarColor(BG);
        buildScreen();
        showCatalog(0);
    }

    private void buildScreen() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(16), dp(18), dp(16), dp(8));
        root.setBackgroundColor(BG);
        root.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);

        TextView title = new TextView(this);
        title.setText("تعريب تيفات");
        title.setTextColor(GOLD);
        title.setTextSize(27);
        title.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        title.setGravity(Gravity.RIGHT);
        root.addView(title, new LinearLayout.LayoutParams(-1, dp(44)));

        TextView subtitle = new TextView(this);
        subtitle.setText("مرجع عربي مستقل يعمل دون اتصال بالإنترنت");
        subtitle.setTextColor(WHITE);
        subtitle.setTextSize(14);
        subtitle.setGravity(Gravity.RIGHT);
        root.addView(subtitle, new LinearLayout.LayoutParams(-1, dp(32)));

        HorizontalScrollView tabsScroll = new HorizontalScrollView(this);
        tabsScroll.setHorizontalScrollBarEnabled(false);
        LinearLayout tabs = new LinearLayout(this);
        tabs.setOrientation(LinearLayout.HORIZONTAL);
        for (int i = 0; i < CATALOGS.length; i++) {
            final int index = i;
            Button tab = new Button(this);
            tab.setText(CATALOGS[i].label);
            tab.setTextSize(12);
            tab.setOnClickListener(v -> showCatalog(index));
            LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-2, dp(48));
            p.setMargins(dp(3), dp(4), dp(3), dp(4));
            tabs.addView(tab, p);
        }
        tabsScroll.addView(tabs);
        root.addView(tabsScroll, new LinearLayout.LayoutParams(-1, dp(58)));

        search = new EditText(this);
        search.setSingleLine(true);
        search.setTextSize(15);
        search.setHint("ابحث بالاسم العربي أو الإنجليزي");
        search.setHintTextColor(Color.LTGRAY);
        search.setTextColor(WHITE);
        search.setPadding(dp(12), 0, dp(12), 0);
        search.setBackgroundColor(PANEL);
        root.addView(search, new LinearLayout.LayoutParams(-1, dp(50)));

        count = new TextView(this);
        count.setTextColor(GOLD);
        count.setTextSize(13);
        count.setGravity(Gravity.RIGHT | Gravity.CENTER_VERTICAL);
        root.addView(count, new LinearLayout.LayoutParams(-1, dp(38)));

        ScrollView scroll = new ScrollView(this);
        list = new LinearLayout(this);
        list.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(list);
        root.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));

        TextView footer = new TextView(this);
        footer.setText("ترجمات مجتمعية أولية غير رسمية • لا تعدّل ملفات اللعبة");
        footer.setTextColor(Color.GRAY);
        footer.setTextSize(11);
        footer.setGravity(Gravity.CENTER);
        root.addView(footer, new LinearLayout.LayoutParams(-1, dp(30)));

        search.addTextChangedListener(new TextWatcher() {
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            public void onTextChanged(CharSequence s, int start, int before, int count) { render(); }
            public void afterTextChanged(Editable e) {}
        });
        setContentView(root);
    }

    private void showCatalog(int index) {
        selected = index;
        search.setText("");
        records.clear();
        try {
            String json = readAsset(CATALOGS[index].file);
            if (!json.trim().isEmpty()) {
                JSONObject root = new JSONObject(json);
                JSONArray entries = root.optJSONArray("entries");
                if (entries != null) {
                    for (int i = 0; i < entries.length(); i++) {
                        JSONObject item = entries.optJSONObject(i);
                        if (item != null) records.add(item);
                    }
                }
            }
        } catch (Exception ignored) {
            // An empty or temporarily unavailable catalog is shown as an empty state.
        }
        render();
    }

    private void render() {
        if (list == null) return;
        list.removeAllViews();
        String query = search == null ? "" : search.getText().toString().trim().toLowerCase(Locale.ROOT);
        int shown = 0;
        for (JSONObject item : records) {
            String arabic = item.optString("arabic_name", item.optString("translation", ""));
            String english = item.optString("source_name", item.optString("source_term", ""));
            String haystack = (arabic + " " + english).toLowerCase(Locale.ROOT);
            if (!query.isEmpty() && !haystack.contains(query)) continue;
            addRecord(item, arabic, english);
            shown++;
        }
        count.setText("المعروض: " + shown + " من " + records.size() + " • " + CATALOGS[selected].label);
        if (shown == 0) {
            TextView empty = new TextView(this);
            empty.setText(records.isEmpty()
                ? "لا توجد سجلات في هذا القسم بعد. ستظهر المهام هنا عند استيرادها."
                : "لا توجد نتائج مطابقة لبحثك.");
            empty.setTextColor(WHITE);
            empty.setTextSize(16);
            empty.setGravity(Gravity.CENTER);
            empty.setPadding(dp(16), dp(32), dp(16), dp(32));
            list.addView(empty);
        }
    }

    private void addRecord(JSONObject item, String arabic, String english) {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setPadding(dp(14), dp(12), dp(14), dp(12));
        card.setBackgroundColor(PANEL);
        card.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        LinearLayout.LayoutParams cp = new LinearLayout.LayoutParams(-1, -2);
        cp.setMargins(0, dp(4), 0, dp(5));
        list.addView(card, cp);

        TextView ar = new TextView(this);
        ar.setText(arabic.isEmpty() ? "ترجمة قيد الإعداد" : arabic);
        ar.setTextColor(GOLD);
        ar.setTextSize(18);
        ar.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        card.addView(ar);

        if (!english.isEmpty()) {
            TextView en = new TextView(this);
            en.setText(english);
            en.setTextColor(WHITE);
            en.setTextSize(13);
            en.setPadding(0, dp(3), 0, 0);
            card.addView(en);
        }

        String description = item.optString("description_ar", "");
        if (description.isEmpty()) description = item.optString("notes", "");
        if (description.isEmpty()) description = item.optString("review_notes", "");
        if (!description.isEmpty() && !"null".equals(description)) {
            TextView detail = new TextView(this);
            detail.setText(description);
            detail.setTextColor(Color.LTGRAY);
            detail.setTextSize(12);
            detail.setPadding(0, dp(7), 0, 0);
            card.addView(detail);
        }

        String status = item.optString("translation_status", item.optString("status", "draft"));
        TextView state = new TextView(this);
        state.setText("الحالة: " + statusLabel(status));
        state.setTextColor(Color.rgb(180, 205, 190));
        state.setTextSize(10);
        state.setPadding(0, dp(6), 0, 0);
        card.addView(state);
    }

    private String statusLabel(String status) {
        switch (status) {
            case "approved": return "معتمد";
            case "reviewed": return "مراجع";
            case "draft": return "مسودة";
            case "needs_context": return "بحاجة إلى سياق";
            case "needs_translation": return "بانتظار الترجمة";
            default: return status;
        }
    }

    private String readAsset(String name) throws Exception {
        try (InputStream in = getAssets().open(name);
             ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[8192];
            int n;
            while ((n = in.read(buffer)) != -1) out.write(buffer, 0, n);
            return out.toString(StandardCharsets.UTF_8.name());
        }
    }

    private int dp(int value) {
        return (int) (value * getResources().getDisplayMetrics().density + 0.5f);
    }

    private static final class Catalog {
        final String label;
        final String file;
        Catalog(String label, String file) { this.label = label; this.file = file; }
    }
}
