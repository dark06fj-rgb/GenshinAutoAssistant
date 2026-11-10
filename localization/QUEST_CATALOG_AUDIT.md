# Quest catalog audit — version 7.2 baseline

## Scope

This audit establishes the missing quest-data work as two independent catalogs:

- **Archon Quests**: chapter, act, and individual quest nodes, with stable IDs and prerequisite relationships.
- **World Quests**: quest-series and individual quest nodes, with region and prerequisite relationships.

Story Quests, Hangout Events, Commissions, and Event Quests are not silently mixed into either catalog. They require separate scope decisions and files.

## Source assessment

- The current `genshin-db` data-folder index documents characters, talents, weapons, artifacts, materials, and other categories, but does not expose a dedicated quest catalog in its documented query functions. It is therefore not sufficient by itself for quest coverage.
- The maintained technical source is now identified: [DimbreathBot/AnimeGameData](https://github.com/DimbreathBot/AnimeGameData), the GitHub mirror of `Dimbreath/animegamedata2`. Its documented 7.2.0 snapshot is commit `d54f6f0d423ded9d055bb740a3e5f3aa8f2667f1` (2026-11-04). The legacy `Dimbreath/GenshinData` GitHub path is no longer the maintained location.
- `ExcelBinOutput/MainQuestExcelConfigData.json` contains 4,075 main-quest definitions in that snapshot, including `id`, `chapterId`, `series`, `titleTextMapHash`, `descTextMapHash`, `mainQuestTag`, and `recommendLevel`. This is a mixed pool, not a count of Archon or World Quests; it must be filtered against chapter metadata.
- `ExcelBinOutput/ChapterExcelConfigData.json` contains 436 chapter rows in this snapshot: 53 use `CHAPTER_STYLE_TYPE_AQ`, 132 have `questType: WQ`, 99 have `questType: LQ`, 151 have `questType: EQ`, and 54 have no `questType`. These are chapter/group metadata counts, not counts of individual player-visible quests. The source uses `CHAPTER_STYLE_TYPE_AQ` to identify Archon chapter groups and `questType: WQ` for World Quest chapter groups. `ExcelBinOutput/QuestExcelConfigData.json` stores individual steps linked by `mainId`; these steps must not be mistaken for separate main quests.
- Quest title hashes are resolved through both `TextMapEN` and `TextMap_MediumEN`; the upstream audit documents separate, non-overlapping hash spaces. Missing hashes must be counted and reported, not silently replaced with empty strings.
- Community parsers such as GenshinScripts document extraction of World Quest IDs from `MainQuestExcelConfigData` and chapter structures for Archon Quests. They are leads for extraction logic, not translation authorities.
- The Genshin Impact Wiki quest index and Travel Log are useful cross-checks for titles, hierarchy, and prerequisite graphs. Individual records still need version-aware verification.

## Data model

Each record should preserve the upstream identifier and identify its node type (`chapter`, `act`, `series`, or `quest`). Where supported by the source, record parent, chapter/act/series IDs, sequence, region, prerequisite quest IDs, Adventure Rank gate, and version introduced. Unknown values must remain absent or null rather than guessed.

Arabic titles and concise summaries are original community drafts. Do not copy dialogue, long narrative descriptions, voice files, or artwork into this catalog.

## Current state

- `ar/quests_archon.json`: initialized, **0 records imported**.
- `ar/quests_world.json`: initialized, **0 records imported**.
- `schema/quest.schema.json`: quest metadata contract added.
- Automated validator requires both catalogs and validates generic entity fields plus quest type, node type, source IDs, parent/prerequisite references, sequence and Adventure Rank values, and parent/prerequisite cycles.
- No quest has been marked reviewed or approved.
- The validator regression suite has 30 passing tests, including quest-specific checks for catalog type, node type, source-ID uniqueness, missing parent/prerequisite references, malformed hierarchy values, and relationship cycles.

## Remaining work

1. Build a reproducible importer pinned to AnimeGameData snapshot `d54f6f0d423ded9d055bb740a3e5f3aa8f2667f1`; verify the table layout against that exact commit before relying on it.
2. Resolve title hashes using both English TextMap files, filter Archon and World Quest records through chapter metadata, and preserve the original numeric quest IDs.
3. Build and test an importer that preserves source IDs and hierarchy without importing dialogue.
4. Populate Archon Quest chapter/act/quest nodes and World Quest series/quest nodes in reviewable batches.
5. Cross-check prerequisite graphs and Adventure Rank gates against the Travel Log and versioned source tables.
6. Write original Arabic titles and short summaries; leave ambiguous translations as `needs_context`.
7. Extend quest validation to compare chapter and act membership against the pinned source tables and add importer integration tests, then publish coverage counts only after reconciling the imported roster against the source index. The 4,075-row main-quest table is not itself a valid Archon/World Quest coverage denominator.

**This is scaffolding, not a completed quest translation.** Empty catalogs deliberately make the missing coverage visible rather than presenting a fabricated or partial list as complete.
