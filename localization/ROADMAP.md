# Localization roadmap

1. Establish stable IDs, JSON schema, provenance, and review states. (established)
2. Expand character, weapon, artifact, and material indexes from permitted reference data. (ongoing editorial review)
3. Add original Arabic names and descriptions in small reviewable batches; preserve explicit draft/review states. (ongoing)
4. Maintain resource taxonomy (local specialties, ores, enemy drops, boss drops) and source-backed locations. (ongoing)
5. Maintain separate **Main Story / Archon Quest** and **World Quest** catalogs with stable source IDs, chapter/act/series hierarchy, region, prerequisites, Adventure Rank gates, and version provenance. (verified source sync: 1,579 records—51 Archon acts, 208 Archon quests, 90 World Quest series, and 1,230 World Quests. The importer report records 79 AQ/WQ source files held back for unresolved English titles; 1,198 World Quest titles and 38 series titles currently have Arabic title drafts.)
6. Resolve the 79 held-back AQ/WQ titles by bounded per-hash lookup; complete the 52 World Quest series titles still lacking Arabic titles; review the four prerequisite edges omitted to prevent cycles. Re-check Archon act coverage against the current pinned source. Never download the 57.7 MB TextMapEN file wholesale.
7. Arabic title drafts now cover all 1,579 imported records: 51 Archon acts, 208 Archon quests, 90 World Quest series, and 1,230 World Quests. Continue writing concise, original Arabic summaries in reviewable batches; 17 new Archon summaries were added in the first batch, while the rest of the summary backlog remains. Preserve existing Arabic editorial text; keep untranslated records as needs_translation until actual Arabic text is added, then draft pending human review.
8. Cross-check quest region, Adventure Rank, chapter/series membership, and prerequisites against versioned source data and the in-game Travel Log; do not invent missing metadata or dialogue.
9. Add source-roster coverage assertions and regression tests so future updates expose additions/removals instead of silently accepting partial imports.
10. Build an offline searchable Arabic glossary/catalog viewer.
11. Keep any future game integration separate; this catalog alone does not alter the game client.

## Quest scope (required)

- **Main story:** Archon Quest chapters, acts, and individual player-facing main quests.
- **World content:** World Quest series and individual player-facing World Quests, including multi-part chains.
- Track Story Quests (character quests), Hangout Events, Commissions, and Event Quests separately; do not silently mix them into the Archon/World Quest totals.
- Dialogue, voice data, and long narrative text are outside the current catalog scope. Quest titles and short original summaries are in scope.

## Quality gates

- No invented IDs, source text, translations, or unverified locations.
- No copied bulk text unless redistribution rights are confirmed.
- All new translations start as `draft`; untranslated records remain `needs_translation`.
- Keep placeholders and markup intact.
- A reviewer must approve terminology consistency before a release.
- Run the regression suite and full localization validator after each import or translation batch.
