# Localization roadmap

1. Establish stable IDs, JSON schema, provenance, and review states. (established)
2. Expand character, weapon, artifact, and material indexes from permitted reference data. (ongoing editorial review)
3. Add original Arabic names and descriptions in small reviewable batches; preserve explicit draft/review states. (ongoing)
4. Maintain resource taxonomy (local specialties, ores, enemy drops, boss drops) and source-backed locations. (ongoing)
5. Maintain separate **Main Story / Archon Quest** and **World Quest** catalogs with stable source IDs, chapter/act/series hierarchy, region, prerequisites, Adventure Rank gates, and version provenance. (current branch inspection: 259 Archon nodes are present—51 acts and 208 quests—but the World Quest catalog was a zero-byte file; it has now been initialized as valid JSON with 0 entries. The earlier 1,590-record figure is not verified against this branch snapshot and must not be treated as current.)
6. Re-run the pinned, bounded quest-source importer and regenerate its report before quoting any AQ/WQ totals. Then resolve held-back titles, missing act/series titles, and prerequisite gaps using the current report. Never download the 57.7 MB TextMapEN file wholesale.
7. Translate the verified quest backlog in reviewable batches: Arabic quest titles plus concise, original Arabic summaries for both the main story (Archon Quests) and World Quests. Preserve existing reviewed Arabic text; keep new records as needs_translation until actual Arabic text is added, then draft pending human review.
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
