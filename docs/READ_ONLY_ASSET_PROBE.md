# Automatic game text recognition prototype

## What this milestone does

The Android app now has an opt-in AccessibilityService prototype for Genshin Impact Android package variants:

- `com.miHoYo.GenshinImpact`
- `com.miHoYo.ys.mi`

When the user explicitly enables the service in Android Accessibility settings, it listens only to those package names, reads text exposed through Android accessibility nodes, skips password fields, detects the source language with ML Kit, translates detected strings to Arabic, and stores up to 80 recent pairs locally in app preferences.

The translation history is viewed inside the app. There are no screenshots, MediaProjection prompts, floating windows, or overlay permissions. The service does not upload captured text to our servers. ML Kit may download its on-device language and translation models; that requires network access on first use.

## Important platform boundary

This does **not** replace the rendered text inside Genshin Impact. Android accessibility services can observe accessible text nodes, but cannot rewrite arbitrary text rendered by another app's Unity/game canvas. Genshin may expose little or no game UI text through the Android accessibility tree. If no text is exposed, the observer cannot translate it.

In-place replacement without an overlay requires an official game localization/customization interface or a permitted, offline, reversible asset workflow. Do not bypass encryption, DRM, access controls, or anti-cheat, and do not patch the live game installation.

## Test

1. Install the debug APK.
2. Open the app and tap **تفعيل التعرف التلقائي**.
3. In Android Accessibility settings, enable **التعرف التلقائي على نصوص Genshin**.
4. Open Genshin Impact and visit a screen with visible text.
5. Return to the app and open **عرض الترجمات المحفوظة**.

A blank history can mean the game does not expose its Unity-rendered text to Android accessibility. It does not mean the translation model is broken.

## Next milestone

Validate whether the supported Genshin Android build exposes any accessible text. If it does, improve language filtering, deduplication, and the in-app translation history. If it does not, stop the accessibility path and investigate only official or user-authorized plain-text localization exports.
