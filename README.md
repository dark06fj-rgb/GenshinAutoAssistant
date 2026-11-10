# Teyvat Companion

The repository contains two independently installable Android applications:

- `:app` — the existing companion utility.
- `:arabic-app` — a standalone Arabic localization catalog app. It has its own Android application ID and launcher, reads the repository's Arabic JSON catalogs as packaged offline assets, and does not modify or inject into the Genshin Impact game client.

Build the standalone Arabic app with:

```bash
./gradlew :arabic-app:assembleDebug
```

APK output: `arabic-app/build/outputs/apk/debug/arabic-app-debug.apk`.

The Arabic catalog entries are community drafts, not official HoYoverse translations. Quest dialogue is intentionally excluded.
