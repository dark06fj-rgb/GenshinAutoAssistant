# Talent Content Audit — Version 7.2

## Scope

This audit covers all records in `localization/ar/talents.json` on the
`arabic-localization-catalog` branch. It checks catalog completeness,
Arabic-script coverage, duplicate Arabic talent labels, summary presence,
character-label links, slot structure, translation status, and editorial-note
consistency. It is a data-quality audit, not an in-game linguistic certification.

## Verified inventory

| Check | Result |
|---|---:|
| Talent records | 387 |
| Non-Traveler character kits | 122 × 3 = 366 |
| Traveler kits | 7 elements × 3 = 21 |
| Total expected slots | 387 |
| Arabic talent names present | 387 / 387 |
| Arabic summaries present | 387 / 387 |
| Empty summaries | 0 |
| Duplicate Arabic talent names (normalized comparison) | 0 |
| Records with non-draft status | 0 |
| Missing source name/source metadata | 0 |
| Missing regular-character slots | 0 |
| Missing Traveler element/slot combinations | 0 |

The summary lengths range from 43 to 184 characters, with a median of 92.
All 387 records remain `draft`; no translation has been promoted based on
automated checks.

## Corrections made

Thirty early records still carried a review note saying that the description
had not yet been translated, even though each already contained a non-empty
Arabic summary. Those 30 notes were corrected to describe the actual state:
the Arabic name and concise summary are unofficial draft proposals and still
need linguistic, gameplay, and in-game comparison review.

The validator now rejects this contradictory stale note when a populated
Arabic summary exists. A regression test covers that failure case.

## Repeated summaries

A small number of identical summaries are shared across records with the same
basic-attack pattern. The largest repeated string is the generic sword
normal-attack summary shared by Albedo and the seven Traveler element kits.
Other repeated strings cover common sword and polearm attack patterns.
These are generic functional summaries, not duplicate talent IDs or duplicate
Arabic talent names. They should be reviewed if a future pass adds character-
specific combat details.

## Editorial risks still requiring human/gameplay review

- The catalog contains several natural phrasings for elemental damage, such as
  concise labels (`ضرر هيدرو`) and explanatory constructions
  (`ضرراً من عنصر هيدرو`). They are understandable, but a final editorial
  style guide should select one grammatical pattern before mass normalization.
- Transliteration and proper-name choices in talent names need comparison
  against a trusted Arabic in-game reference, if one becomes available.
- Concise summaries can omit edge cases, conditions, durations, multipliers,
  targeting details, and alternate hold/press behavior by design. They are
  reference summaries, not complete skill descriptions.
- Automated checks can prove field coverage and structural consistency; they
  cannot prove that every gameplay mechanic is described correctly.

## Validation status

The repository's GitHub Actions workflow has previously completed successfully
with 21 regression tests and a pass over 828 records. This audit adds a new
regression case for stale review notes; its result must be confirmed by the
new workflow run after these commits.

## Editorial policy

Keep all entries in `draft` until a human reviewer compares each name and
summary with reliable source data and actual gameplay. Never treat a green
validator result as approval or as evidence of an official HoYoverse Arabic
translation.
