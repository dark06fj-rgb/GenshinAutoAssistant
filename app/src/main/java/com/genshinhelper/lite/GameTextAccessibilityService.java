package com.genshinhelper.lite;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import android.content.SharedPreferences;
import android.os.Build;
import android.text.TextUtils;
import android.util.Log;

import com.google.mlkit.nl.languageid.LanguageIdentification;
import com.google.mlkit.nl.languageid.LanguageIdentifier;
import com.google.mlkit.nl.translate.TranslateLanguage;
import com.google.mlkit.nl.translate.Translation;
import com.google.mlkit.nl.translate.Translator;
import com.google.mlkit.nl.translate.TranslatorOptions;
import com.google.mlkit.common.model.DownloadConditions;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

public class GameTextAccessibilityService extends AccessibilityService {
    private static final String TAG = "GameTextObserver";
    private static final String PREFS = "game_translation_log";
    private static final String LOG_KEY = "entries";
    private static final int MAX_NODES_PER_EVENT = 350;
    private static final int MAX_LOG_ENTRIES = 80;
    private static final Set<String> SUPPORTED_PACKAGES = new HashSet<String>() {{
        add("com.miHoYo.GenshinImpact");
        add("com.miHoYo.ys.mi");
    }};

    private final Set<String> pending = new HashSet<>();
    private LanguageIdentifier languageIdentifier;

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        AccessibilityServiceInfo info = new AccessibilityServiceInfo();
        info.eventTypes = AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED
                | AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED
                | AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED;
        info.feedbackType = AccessibilityServiceInfo.FEEDBACK_GENERIC;
        info.flags = AccessibilityServiceInfo.FLAG_RETRIEVE_INTERACTIVE_WINDOWS
                | AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS
                | AccessibilityServiceInfo.FLAG_INCLUDE_NOT_IMPORTANT_VIEWS;
        info.notificationTimeout = 350;
        info.packageNames = SUPPORTED_PACKAGES.toArray(new String[0]);
        setServiceInfo(info);
        languageIdentifier = LanguageIdentification.getClient();
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event == null || event.getPackageName() == null) return;
        String packageName = event.getPackageName().toString();
        if (!SUPPORTED_PACKAGES.contains(packageName)) return;

        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root == null) return;
        int[] visited = new int[]{0};
        collectVisibleText(root, visited);
        root.recycle();
    }

    private void collectVisibleText(AccessibilityNodeInfo node, int[] visited) {
        if (node == null || visited[0] >= MAX_NODES_PER_EVENT) return;
        visited[0]++;
        if (!node.isPassword()) {
            CharSequence value = node.getText();
            if (value != null) considerText(value.toString());
            CharSequence description = node.getContentDescription();
            if (description != null) considerText(description.toString());
        }
        for (int i = 0; i < node.getChildCount() && visited[0] < MAX_NODES_PER_EVENT; i++) {
            AccessibilityNodeInfo child = node.getChild(i);
            if (child != null) {
                collectVisibleText(child, visited);
                child.recycle();
            }
        }
    }

    private void considerText(String raw) {
        if (raw == null) return;
        String value = raw.trim();
        if (value.length() < 3 || value.length() > 500 || TextUtils.isDigitsOnly(value)) return;
        if (value.indexOf('\n') >= 0 && value.length() > 350) return;
        synchronized (pending) {
            if (pending.contains(value)) return;
            pending.add(value);
        }
        if (languageIdentifier == null) {
            synchronized (pending) { pending.remove(value); }
            return;
        }
        languageIdentifier.identifyLanguage(value)
                .addOnSuccessListener(language -> {
                    if (language == null || "und".equals(language)
                            || "ar".equals(language) || "en".equals(language) && value.length() < 4) {
                        finishPending(value);
                        return;
                    }
                    String source = TranslateLanguage.fromLanguageTag(language);
                    if (source == null || TranslateLanguage.ARABIC.equals(source)) {
                        finishPending(value);
                        return;
                    }
                    translate(value, source, language);
                })
                .addOnFailureListener(error -> finishPending(value));
    }

    private void translate(String value, String sourceLanguage, String detectedTag) {
        TranslatorOptions options = new TranslatorOptions.Builder()
                .setSourceLanguage(sourceLanguage)
                .setTargetLanguage(TranslateLanguage.ARABIC)
                .build();
        Translator translator = Translation.getClient(options);
        DownloadConditions conditions = new DownloadConditions.Builder().build();
        translator.downloadModelIfNeeded(conditions)
                .addOnSuccessListener(unused -> translator.translate(value)
                        .addOnSuccessListener(arabic -> {
                            if (arabic != null && !arabic.trim().isEmpty()
                                    && !arabic.trim().equals(value)) {
                                saveTranslation(value, arabic, detectedTag);
                            }
                            translator.close();
                            finishPending(value);
                        })
                        .addOnFailureListener(error -> {
                            translator.close();
                            finishPending(value);
                        }))
                .addOnFailureListener(error -> {
                    Log.w(TAG, "Translation model unavailable", error);
                    translator.close();
                    finishPending(value);
                });
    }

    private void saveTranslation(String original, String translated, String language) {
        try {
            SharedPreferences prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
            JSONArray old = new JSONArray(prefs.getString(LOG_KEY, "[]"));
            JSONArray updated = new JSONArray();
            JSONObject entry = new JSONObject();
            entry.put("original", original);
            entry.put("arabic", translated);
            entry.put("language", language);
            entry.put("package", "Genshin Impact");
            entry.put("time", System.currentTimeMillis());
            updated.put(entry);
            int start = Math.max(0, old.length() - (MAX_LOG_ENTRIES - 1));
            for (int i = start; i < old.length(); i++) updated.put(old.get(i));
            prefs.edit().putString(LOG_KEY, updated.toString()).apply();
        } catch (Exception error) {
            Log.w(TAG, "Could not save translation", error);
        }
    }

    private void finishPending(String value) {
        synchronized (pending) { pending.remove(value); }
    }

    @Override
    public void onInterrupt() {
        if (languageIdentifier != null) {
            languageIdentifier.close();
            languageIdentifier = null;
        }
        synchronized (pending) { pending.clear(); }
    }
}
