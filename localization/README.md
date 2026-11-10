# Arabic Localization Catalog

This directory stores a community-maintained Arabic reference catalog for Genshin Impact.

## Catalog files

- `ar/glossary.json`: terminology and shared translations.
- `ar/characters.json`: character name records.
- `ar/talents.json`: initial combat talent names for the 10 seed characters; descriptions are intentionally pending review.
- `ar/weapons.json`: weapon name records and compact weapon metadata.\n- `scripts/import_weapon_catalog.py`: imports the public weapon roster from genshin-db while preserving existing Arabic translations.
- `ar/artifacts.json`: artifact set name records.
- `ar/materials.json`: common currencies and wish items.
- `ar/resources.json`: gatherable plants, fruits, and ores.
- `schema/entity.schema.json`: shared entity format.
- `SOURCES.md`: data provenance and attribution.
- `CONTRIBUTING.md`: translation contribution rules.
- `ROADMAP.md`: project stages.

## Validation

Run `python scripts/validate_localization.py` to check JSON syntax and duplicate IDs within each catalog file. GitHub Actions runs this check when localization files change.

## Scope and limitations

This is a translation/reference catalog. It does **not** modify the game, patch APK files, inject code, hook game functions, or bypass anti-cheat. It does not currently make Arabic appear inside the live game.

## Quality rules

1. Never invent missing source text, IDs, item locations, or drop information.
2. Keep source text and translated text in separate fields.
3. Mark every unverified translation as `draft`.
4. Record source URLs and game version where known.
5. Preserve stable source identifiers exactly; do not translate IDs.
6. Use UTF-8 JSON and validate files before committing.
7. Do not copy proprietary game databases wholesale unless redistribution rights are confirmed.
8. Store Arabic in logical Unicode order; any future viewer must handle RTL and Arabic shaping.

All seed translations are drafts, not official HoYoverse translations.
