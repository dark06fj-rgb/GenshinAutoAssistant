# Data sources and attribution

## Reference datasets

- [genshin-db](https://github.com/theBowja/genshin-db): structured reference data for characters, weapons, materials, artifacts, talents and other game categories. Its README states that it aggregates/parses data from GenshinData and the Fandom Wiki and supports the game's listed locales; Arabic is not among the listed locales. Check the upstream license and data provenance before redistributing any substantial copied dataset.
- [AnimeGameData](https://github.com/DimbreathBot/AnimeGameData): current GitHub mirror of Dimbreath's `animegamedata2` technical data. The 7.2.0 snapshot documented on 2026-11-04 is `d54f6f0d423ded9d055bb740a3e5f3aa8f2667f1`. Quest references include `ExcelBinOutput/MainQuestExcelConfigData.json`, `ChapterExcelConfigData.json`, `QuestExcelConfigData.json`, and the English `TextMap` plus `TextMap_Medium` files. Use as technical metadata only; verify the snapshot before each import and do not redistribute dialogue or proprietary assets.
- [Legacy GenshinData repository](https://github.com/Dimbreath/GenshinData): historical location; the maintained data moved to `AnimeGameData` as documented by the upstream data-source audit.
- [genshin.dev API source](https://github.com/genshindev/api): community static-data API; its documentation says it does not interact with the game and supports localized responses only where data exists.

## Project policy

This repository's Arabic strings are original community translation drafts, not official HoYoverse translations. Each entry must retain source attribution. Images should be linked by URL only when the source and usage terms are clear; do not mirror game artwork by default. Do not claim an entry is complete or verified until it has been reviewed.

## Current seed data

The first batch contains a small starter sample of character names, weapon names, and common materials. All Arabic translations are marked `draft`; they are not an exhaustive roster and must be reviewed before release.


## Quest catalog sources and boundaries

- [AnimeGameData](https://github.com/DimbreathBot/AnimeGameData): primary technical reference for quest/chapter identifiers. `MainQuestExcelConfigData` supplies main quest IDs and title hashes; `ChapterExcelConfigData` supplies chapter grouping and identifies World Quest chapters with `questType: WQ`; `QuestExcelConfigData` contains sub-quest steps. The 7.2.0 source snapshot is pinned in the quest audit. Treat extracted data as reference material; do not redistribute dialogue or proprietary assets.
- [GenshinScripts](https://github.com/ToaHartor/GenshinScripts): community parser documentation demonstrates extraction of World Quest records and Archon/Story/Event chapter structures from GenshinData, including lookup by `MainQuestExcelConfigData` IDs. Use as a parser/reference lead, not as an authority for Arabic wording.
- [Genshin Impact Wiki – Quest Menu](https://genshin-impact.fandom.com/wiki/Quest/Menu): reference for in-game grouping and the Travel Log's prerequisite graph. Verify individual quest titles and unlock conditions against versioned sources before adding them.
- [GenshinDialogueFetch](https://github.com/arrogant-R/GenshinDialogueFetch): documents separate Archon and World Quest indexes and hierarchy. This project will use index/hierarchy metadata only; it will not copy dialogue, voice files, or images.

Quest entries must preserve stable source IDs and distinguish chapter, act/series, and playable quest nodes. Archon Quests and World Quests are separate catalogs. Story Quests, Hangout Events, Commissions, and Event Quests are explicitly out of these two catalogs until separately scoped. Unlock requirements and region assignments must be source-backed; unknown values stay null/omitted with a review note. Arabic titles and summaries are original community drafts, not official translations. No quest dialogue is included.
