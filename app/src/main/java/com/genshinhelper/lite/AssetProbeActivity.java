package com.genshinhelper.lite;

import android.content.ClipData;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

public class AssetProbeActivity extends AppCompatActivity {
    private static final int PICK_FILES = 71;
    private static final int MAX_BYTES = 2 * 1024 * 1024;
    private LinearLayout results;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(20), dp(24), dp(20), dp(20));
        root.setBackgroundColor(0xFF17151D);

        TextView title = new TextView(this);
        title.setText("فحص ملفات التصدير");
        title.setTextColor(0xFFFFFFFF);
        title.setTextSize(22);
        title.setGravity(Gravity.CENTER);
        root.addView(title, new LinearLayout.LayoutParams(-1, dp(56)));

        TextView note = new TextView(this);
        note.setText("اختر ملفات نصية صدّرتها أو تملك حق فحصها. الفحص محلي للقراءة فقط: لا يرفع الملفات ولا يعدّلها ولا يفك الحزم أو التشفير.");
        note.setTextColor(0xFFD8D2E2);
        note.setTextSize(15);
        note.setPadding(0, dp(12), 0, dp(18));
        root.addView(note);

        Button choose = new Button(this);
        choose.setText("اختيار ملفات للفحص");
        choose.setOnClickListener(v -> chooseFiles());
        root.addView(choose, new LinearLayout.LayoutParams(-1, dp(54)));

        ScrollView scroll = new ScrollView(this);
        results = new LinearLayout(this);
        results.setOrientation(LinearLayout.VERTICAL);
        results.setPadding(0, dp(14), 0, dp(12));
        scroll.addView(results);
        root.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));
        setContentView(root);
        addResult("لم يتم اختيار ملفات بعد.");
    }

    private void chooseFiles() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.setType("*/*");
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
        startActivityForResult(intent, PICK_FILES);
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != PICK_FILES || resultCode != RESULT_OK || data == null) return;
        ArrayList<Uri> selected = new ArrayList<>();
        ClipData clip = data.getClipData();
        if (clip != null) {
            for (int i = 0; i < clip.getItemCount(); i++) selected.add(clip.getItemAt(i).getUri());
        } else if (data.getData() != null) selected.add(data.getData());
        results.removeAllViews();
        int readable = 0;
        for (Uri uri : selected) {
            String name = queryName(uri);
            addResult(inspect(uri, name));
            readable++;
        }
        addResult("انتهى الفحص: " + readable + " ملف محدد. لم تُرسل أي بيانات إلى الإنترنت.");
    }

    private String inspect(Uri uri, String name) {
        try (InputStream input = getContentResolver().openInputStream(uri);
             ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            if (input == null) return name + "\nتعذر فتح الملف.";
            byte[] buffer = new byte[8192];
            int total = 0, count;
            while ((count = input.read(buffer)) != -1) {
                total += count;
                if (total > MAX_BYTES) return name + "\nتم تجاوزه: الحجم أكبر من 2 MB.";
                output.write(buffer, 0, count);
            }
            byte[] raw = output.toByteArray();
            if (raw.length == 0) return name + "\nملف فارغ.";
            if (hasBinaryData(raw)) return name + "\nمحتوى ثنائي؛ تم تجاهله بأمان.";
            String text;
            if (raw.length >= 2 && raw[0] == (byte)0xFF && raw[1] == (byte)0xFE)
                text = new String(raw, 2, raw.length - 2, java.nio.charset.StandardCharsets.UTF_16LE);
            else if (raw.length >= 2 && raw[0] == (byte)0xFE && raw[1] == (byte)0xFF)
                text = new String(raw, 2, raw.length - 2, java.nio.charset.StandardCharsets.UTF_16BE);
            else text = new String(raw, StandardCharsets.UTF_8);
            String trimmed = text.trim();
            String format = "نص عادي";
            int strings = 0;
            if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
                try {
                    Object json = trimmed.startsWith("{") ? new JSONObject(trimmed) : new JSONArray(trimmed);
                    strings = countJsonStrings(json);
                    format = "JSON صالح";
                } catch (Exception ignored) { format = "نص يشبه JSON لكنه غير صالح"; }
            } else if (trimmed.startsWith("<?xml") || name.toLowerCase().endsWith(".xml")) format = "مرشح XML";
            else if (name.toLowerCase().endsWith(".csv") || name.toLowerCase().endsWith(".tsv")) format = "نص جدولي";
            int lines = text.split("\\R", -1).length;
            return name + "\nالنوع: " + format + "\nالحجم: " + raw.length + " بايت | الأسطر: " + lines
                    + (format.equals("JSON صالح") ? " | القيم النصية: " + strings : "");
        } catch (Exception e) {
            return name + "\nتعذر الفحص: " + e.getClass().getSimpleName();
        }
    }

    private boolean hasBinaryData(byte[] bytes) {
        if (bytes.length >= 2 && ((bytes[0] == (byte)0xFF && bytes[1] == (byte)0xFE) || (bytes[0] == (byte)0xFE && bytes[1] == (byte)0xFF))) return false;
        int limit = Math.min(bytes.length, 4096);
        for (int i = 0; i < limit; i++) if (bytes[i] == 0) return true;
        return false;
    }

    private int countJsonStrings(Object value) {
        int count = 0;
        if (value instanceof String) return 1;
        if (value instanceof JSONObject) {
            JSONObject object = (JSONObject)value;
            java.util.Iterator<String> keys = object.keys();
            while (keys.hasNext()) {
                String key = keys.next();
                count += 1 + countJsonStrings(object.opt(key));
            }
        } else if (value instanceof JSONArray) {
            JSONArray array = (JSONArray)value;
            for (int i = 0; i < array.length(); i++) count += countJsonStrings(array.opt(i));
        }
        return count;
    }

    private String queryName(Uri uri) {
        try (android.database.Cursor cursor = getContentResolver().query(uri, null, null, null, null)) {
            if (cursor != null && cursor.moveToFirst()) {
                int index = cursor.getColumnIndex(android.provider.OpenableColumns.DISPLAY_NAME);
                if (index >= 0) return cursor.getString(index);
            }
        } catch (Exception ignored) {}
        return uri.getLastPathSegment() == null ? "ملف محدد" : uri.getLastPathSegment();
    }

    private void addResult(String message) {
        TextView item = new TextView(this);
        item.setText(message);
        item.setTextColor(0xFFE9E3F0);
        item.setTextSize(14);
        item.setPadding(dp(10), dp(12), dp(10), dp(12));
        results.addView(item);
    }

    private int dp(int value) {
        return (int)(value * getResources().getDisplayMetrics().density + 0.5f);
    }
}
