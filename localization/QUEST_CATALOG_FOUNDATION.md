# Archon and World Quest catalog foundation

## Status

**Structure established; quest records are not populated yet.** The two expected catalog files now exist as empty, valid JSON catalogs. This is an explicit placeholder state, not a claim that the game's quests have been translated.

- `ar/quests_archon.json`: Archon (main story) quest catalog.
- `ar/quests_world.json`: World Quest catalog.

All future Arabic titles and summaries must start as `draft`. Do not add guessed IDs, guessed names, or inferred chapter relationships.

## Source inspection

The inspected public GenshinData mirror is [gmh5225/Genshin-GenshinData](https://github.com/gmh5225/Genshin-GenshinData), branch snapshot `20c05dbbcc6e69445815d6a0bd3bd718f47bc810`. The repository describes itself as game data for the live version, but this mirror's snapshot/version is not sufficient to claim coverage of the current game release.

Files inspected:

- [MainQuestExcelConfigData.json](https://github.com/gmh5225/Genshin-GenshinData/blob/20c05dbbcc6e69445815d6a0bd3bd718f47bc810/ExcelBinOutput/MainQuestExcelConfigData.json) — main quest records, numeric IDs, type codes, title/description TextMap hashes, chapter references and suggested quest links.
- [ChapterExcelConfigData.json](https://github.com/gmh5225/Genshin-GenshinData/blob/20c05dbbcc6e69445815d6a0bd3bd718f47bc810/ExcelBinOutput/ChapterExcelConfigData.json) — chapter IDs, begin/end quest IDs, chapter title/number TextMap hashes and presentation metadata.
- [QuestExcelConfigData.json](https://github.com/gmh5225/Genshin-GenshinData/blob/20c05dbbcc6e69445815d6a0bd3bd718f47bc810/ExcelBinOutput/QuestExcelConfigData.json) — child quest/step records; the inspected file is very large and was not imported or redistributed.

The main-quest table in this snapshot contains **1,469 rows**:
- `WQ`: 864
- `LQ`: 225
- `IQ`: 169
- `EQ`: 101
- no explicit `type` field: 110

The chapter table contains **118 rows**. These counts describe this source snapshot only; they are not a current-game completeness claim and must not be presented as the total number of player-visible quests.

## Classification rules

- World Quest catalog: only records positively classified as `WQ` after validating their visible title and parent/step relationships.
- Archon catalog: determine membership from verified chapter hierarchy and linked quest IDs; the inspected source does not provide an explicit `AQ` type in the sampled main-quest rows, so do not classify every untyped row as an Archon Quest.
- Exclude `LQ` (Story Quests), `IQ` (commissions), and `EQ` (event quests) from these two catalogs unless a later scope decision explicitly adds them.
- Preserve upstream numeric IDs exactly as strings in stable catalog IDs. Keep chapter IDs, parent IDs, order, and TextMap hashes as provenance/relationship metadata.
- Do not mix a parent quest, its child steps, and its displayed objectives into one record. Their relationships must be explicit.
- Do not import dialogue, voice assets, long descriptions, or bulk proprietary text. Write original concise Arabic summaries.

## Required fields for populated quest records

In addition to the shared entity fields, each quest record should eventually carry:

- `quest_type`: `archon` or `world`
- `source_quest_id`: original numeric ID, preserved as a string
- `chapter_id` and `parent_quest_id` when present and verified
- `order` when available
- `region` only when confirmed from source metadata
- `source_textmap_hashes` for title/description/step references where available
- `arabic_name`, plus an original concise `description_ar`
- `translation_status` and a note describing unresolved context

The validator and quest-specific schema must be extended to check these relationships before the first populated batch is committed.

## Next data work

1. Resolve TextMap hashes to visible English source labels from the same source snapshot.
2. Identify Archon chapter membership using chapter boundaries and linked quest IDs, not guesswork.
3. Build the World Quest parent/step tree, excluding commissions and event quests.
4. Compare the resulting catalog IDs and visible titles against a current quest index to identify stale or missing content.
5. Import small batches, add original Arabic titles/summaries, and run regression tests after each batch.

## Limitations

This foundation does not contain translated quest records, dialogue, full quest objectives, prerequisites, or rewards. The source mirror's license/provenance and redistribution permissions must be checked before any substantial data is copied. All future Arabic strings are unofficial community drafts.
