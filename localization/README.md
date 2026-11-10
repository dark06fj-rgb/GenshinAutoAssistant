# Arabic Localization Catalog

This directory stores a community-maintained Arabic reference catalog for Genshin Impact.

## Catalog files

- `ar/glossary.json`: terminology and shared translations.
- `TERMINOLOGY_AUDIT.md`: Arabic terminology consistency audit and normalization log.
- `ar/characters.json`: character name records.
- `CHARACTER_ROSTER_AUDIT_7.2.md`: Version 7.2 playable-roster completeness audit.
- `ar/talents.json`: combat talent names and concise Arabic draft summaries; includes seven element-specific Traveler kits (Anemo, Geo, Electro, Dendro, Hydro, Pyro, Cryo).
- `TALENT_CONTENT_AUDIT_7.2.md`: completeness, Arabic-label uniqueness, summary coverage, and editorial-note audit for all 387 talent records.
- `ar/weapons.json`: weapon name records and compact weapon metadata.
- `WEAPON_TERMINOLOGY_AUDIT.md`: weapon-name structure and terminology audit.
- `scripts/import_weapon_catalog.py`: imports the public weapon roster from genshin-db while preserving existing Arabic translations.
- `ar/artifacts.json`: artifact set name records.
- `ar/quests_archon.json`: imported Archon Quest act and individual-quest records, with Arabic draft titles and source metadata.
- `ar/quests_world.json`: imported World Quest chapter, series, and individual-quest records, with Arabic draft titles and source metadata.
- `schema/quest.schema.json`: quest-specific metadata and hierarchy contract.
- `QUEST_CATALOG_AUDIT.md`: quest source assessment, scope, and completeness status.
- `ARTIFACT_TERMINOLOGY_AUDIT.md`: artifact-set name and terminology audit.
- `MATERIALS_RESOURCES_AUDIT.md`: materials and gatherable-resource terminology audit.
- `ar/materials.json`: common currencies and wish items.
- `ar/resources.json`: gatherable plants, fruits, and ores.
- `schema/entity.schema.json`: shared entity format.
- `VALIDATOR_GUIDE.md`: automated validator and regression-test documentation.
- `SOURCES.md`: data provenance and attribution.
- `CONTRIBUTING.md`: translation contribution rules.
- `ROADMAP.md`: project stages and current quest-localization backlog.

## Validation

Run `python scripts/validate_localization.py` to check JSON syntax, required fields, source URLs, translation statuses, duplicate IDs (within and across catalogs), glossary consistency for shared terms and item types, canonical element/weapon terminology, talent-to-character references, a complete normal/skill/burst talent matrix for every non-Traveler character, and the complete seven-element Traveler talent matrix (normal, skill, and burst for each element); required quest catalogs are also checked for presence and valid entity records. Warnings (such as untranslated Arabic-script labels) are reported separately; structural and cross-reference errors fail the check. GitHub Actions runs this validator and its regression tests when relevant files change.

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

## Automatic weapon metadata import

The weapon importer uses the public `genshin-db` API and stores a compact roster
(name, rarity, and weapon type where available). It preserves existing Arabic
translations by stable catalog ID and does not copy long passive descriptions.

Run locally with Python 3:

```bash
python scripts/import_weapon_catalog.py
python scripts/validate_localization.py
```

A GitHub Actions workflow is also available at
`.github/workflows/weapon-catalog-import.yml`. It can be started manually from
the Actions tab, and commits an updated weapon catalog to
`arabic-localization-catalog` when the imported data changes. The importer
requires network access to the upstream public API. Imported Arabic names remain
drafts or `needs_context`; they are not official translations.


## Scheduled DeepSeek quest-summary drafts

The `.github/workflows/deepseek-quest-summary-drafts.yml` workflow can be started
manually from the Actions tab and also runs daily at 03:15 UTC. It checks out
only `gemini-arabic-work`, drafts at most 15 summaries per run, validates the
catalog, and pushes changes only to that work branch.

Configure the repository Actions secret `DEEPSEEK_API_KEY` with a DeepSeek API
key before enabling translation. The key is read only by the workflow and is
never written into the repository. The worker translates only when a record
contains an explicit English source-description field
(`source_description_en`, `description_en`, `source_description`, or
`description_source`). It skips records without source text rather than
inventing a summary from a title or metadata. Machine-generated summaries stay
at `draft` status and require human review. The daily run is capped at 15
records to limit API usage.
