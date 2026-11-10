# Quest catalog audit — version 7.2 baseline

## Scope
This audit covers two separate catalogs:

- **Archon Quests**: act and individual quest nodes, with stable IDs and prerequisite relationships.
- **World Quests**: quest-series and individual quest nodes, with region and prerequisite relationships.

Story Quests, Hangout Events, Commissions, and Event Quests are not silently mixed into either catalog. They require separate scope decisions and files.

## Source assessment

- The current `genshin-db` data-folder index documents characters, talents, weapons, artifacts, materials, and other categories, but does not expose a dedicated quest catalog in its documented query functions.
- The maintained technical source is [DimbreathBot/AnimeGameData](https://github.com/DimbreathBot/AnimeGameData), pinned to 7.2.0 snapshot commit `d54f6f0d423ded9d055bb740a3e5f3aa8f2667f1`.
- `ExcelBinOutput/MainQuestExcelConfigData.json` contains 4,075 main-quest definitions. This is a mixed pool, not a count of Archon or World Quests.
- `ExcelBinOutput/ChapterExcelConfigData.json` contains 436 chapter rows. `CHAPTER_STYLE_TYPE_AQ` identifies Archon act rows and `questType: WQ` identifies World Quest series rows. These are group metadata, not individual player-visible quests.
- `ExcelBinOutput/QuestExcelConfigData.json` stores individual quest steps linked by `mainId`; these steps must not be mistaken for separate main quests.
- Individual quest titles and their text-map hashes are cross-checked against pinned per-ID records in [GI-OnlineQuest](https://github.com/lzray-universe/GI-OnlineQuest). The importer reads only the title, description hash, and compact metadata; it does not import dialogue.
- Quest title hashes are resolved through `TextMapEN` and `TextMap_MediumEN`; the upstream source audit documents separate, non-overlapping hash spaces. Missing hashes must be counted and reported, not silently replaced with empty strings.

## Data model

Each record preserves the upstream identifier and identifies its node type (`act`, `series`, or `quest`). Where supported by the source, record parent, chapter/act/series IDs, sequence, region, prerequisite quest IDs, Adventure Rank gate, and version introduced. Unknown values must remain absent or null rather than guessed.

Arabic titles and concise summaries are original community drafts. Do not copy dialogue, long narrative descriptions, voice files, or artwork into this catalog.

## Current verified state

- `ar/quests_archon.json`: **63 records** — 51 act nodes and 12 individual quest nodes.
- `ar/quests_world.json`: **85 records** — 63 series nodes and 22 individual quest nodes.
- **148 total records** have unique catalog IDs and source title hashes.
- All parent and prerequisite references currently resolve within the two quest catalogs.
- Chapter/act/series metadata is pinned to AnimeGameData snapshot `d54f6f0d423ded9d055bb740a3e5f3aa8f2667f1`.
- Individual quest title/hash lookups use pinned GI-OnlineQuest per-ID JSON records. The importer does not request or download the 57.7 MB `TextMapEN.json`.
- The importer is `scripts/sync_quest_source_metadata.py`; its workflow is `.github/workflows/quest-source-metadata-sync.yml`.
- The sync workflow completed successfully and committed the catalog metadata. The 148 records remain community drafts or context-dependent records; none is automatically marked reviewed or approved.

## Remaining work

1. Expand the catalogs beyond the current 148-record sample by filtering the pinned main-quest table through validated chapter metadata.
2. Resolve additional text-map hashes only for IDs actually selected for import; report unresolved hashes rather than fabricating titles.
3. Complete Archon chapter hierarchy and World Quest series/quest coverage in reviewable batches.
4. Cross-check prerequisite graphs, Adventure Rank gates, and region assignments against versioned source tables and the Travel Log.
5. Write original Arabic titles and short summaries; leave ambiguous translations as `needs_context`.
6. Add importer integration tests that compare chapter/act membership and individual quest references against the pinned source tables, then publish coverage counts only after reconciling the complete roster.

**This is a validated partial quest catalog, not complete quest coverage or a completed translation.** The current 148 records are source-verified scaffolding; further roster extraction and editorial review remain outstanding.
