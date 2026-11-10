# Artifact Set Names and Terminology Audit

Audit date: 2026-11-10  
Branch: `arabic-localization-catalog`  
Catalog source snapshot: genshin-db 7.2

## Scope

Reviewed all six artifact-set name records in `ar/artifacts.json`. Checks covered source metadata, stable IDs, Arabic-name presence, duplicate IDs, duplicate Arabic labels, translation status, and semantic fidelity of the Arabic set names.

## Inventory

| Source name | Arabic draft |
|---|---|
| Blizzard Strayer | متجوّل العاصفة الثلجية |
| Bloodstained Chivalry | الفروسية الملطخة بالدم |
| Crimson Witch of Flames | ساحرة اللهب القرمزي |
| Gladiator's Finale | ختام المصارع |
| Noblesse Oblige | واجب النبلاء |
| Wanderer's Troupe | فرقة المتجولين |

## Corrections and terminology

- Refined `Bloodstained Chivalry` from `فروسية الدم` to `الفروسية الملطخة بالدم` to preserve the explicit meaning of “bloodstained” rather than reducing it to a general reference to blood.
- Added the shared glossary term `Artifact Set` = `مجموعة الآثار`.
- Retained the other five Arabic names. Their current renderings are plausible draft choices, but proper-name nuance and community preference require contextual human review; no unsupported claim of official terminology is made.
- All source IDs and source names remain unchanged.

## Structural findings

- 6 artifact-set records reviewed.
- 0 duplicate IDs.
- 0 duplicate Arabic names after Unicode NFC normalization.
- 0 missing Arabic names.
- 6 of 6 records remain `draft`.
- All records retain source metadata identifying genshin-db and version 7.2.

## Review limitations

This is a focused terminology and structural audit, not a professional localization certification. Arabic names are unofficial community drafts. No entry was promoted to `reviewed` or `approved`. The catalog does not display Arabic inside the live game.
