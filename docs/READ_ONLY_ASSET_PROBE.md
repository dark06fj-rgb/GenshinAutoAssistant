# Read-only Android asset probe

## Current scope

The Android app provides an in-app document picker for files the user is authorized to inspect. It reads selected files locally and reports only basic metadata:

- display name, byte size, and line count;
- whether the file is plain text, JSON, XML-like, or delimited text;
- the number of JSON string/key values when valid JSON is selected.

The app does not upload file contents, alter selected files, patch the game, unpack game containers, decrypt protected data, or interact with anti-cheat systems.

## Android use

1. Build and install the debug APK from the **Build Read-only Game Asset Probe APK** workflow artifact.
2. Open **مساعد تعريب الألعاب**.
3. Tap **اختيار ملفات التصدير وفحصها**.
4. Select one or more small, already-exported text files that you own or are authorized to inspect.
5. Review the on-device report.

The picker accepts multiple files. The current probe skips binary data and files larger than 2 MiB. It does not recursively scan app-private directories.

## Genshin Impact limitation

This is only a reconnaissance stage. It does not establish that Genshin Impact's Android installation exposes editable text assets. Do not attempt to bypass encryption, DRM, access controls, or anti-cheat protections. Do not overwrite the live game installation. Any later localization experiment must use a legally obtained, user-provided export and a reversible offline copy, and must be validated for compatibility before any game-side use.

## Next engineering milestone

Collect a metadata-only report from a permitted text export, then determine whether its schema can be mapped to the existing Arabic localization catalog. If no plain-text export is available, stop at that boundary rather than attempting protected-container extraction.
