# Arabic Localization Catalog

This directory stores a community-maintained Arabic reference catalog for Genshin Impact.

## Scope

- Arabic terminology and translation drafts.
- Structured names and descriptions for characters, weapons, items, regions, quests, and resources when reliable source data is available.
- Source attribution, game-version tracking, review status, and terminology consistency.

## Important limitations

This catalog is a translation/reference project. It does **not** modify the game, patch APK files, inject code, hook game functions, or bypass anti-cheat. It does not currently make Arabic appear inside the live game.

## Data rules

1. Never invent missing source text, IDs, item locations, or drop information.
2. Keep source text and translated text in separate fields.
3. Mark every unverified translation as `draft`.
4. Record the source URL or source repository and the game version where known.
5. Preserve stable source identifiers exactly; do not translate IDs.
6. Use UTF-8 JSON and validate files before committing.
7. Do not copy proprietary game databases wholesale unless their license permits redistribution. Prefer original translations, clearly attributed public sources, and small factual references.

## Translation conventions

- Use clear Modern Standard Arabic.
- Keep character and place names consistent in the glossary.
- Preserve placeholders such as `{0}`, `{name}`, and rich-text tags exactly.
- Do not reorder format placeholders.
- Arabic text should be stored in logical Unicode order. RTL display is the responsibility of any future viewer/exporter.

## Status values

- `draft`: initial translation, not reviewed.
- `reviewed`: checked by a human reviewer.
- `approved`: approved for this catalog release.
- `needs_context`: cannot be translated reliably without more context.

## Current state

The initial glossary is a small, explicitly unapproved terminology draft. No complete game text dataset has been imported.
