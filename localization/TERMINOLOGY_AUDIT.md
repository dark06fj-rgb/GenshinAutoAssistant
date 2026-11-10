# Arabic Terminology Consistency Audit

Audit date: 2026-11-10  
Branch: `arabic-localization-catalog`

## Scope

Reviewed the Arabic glossary and the character, talent, weapon, material, resource, and artifact catalogs for duplicate IDs, missing Arabic names, inconsistent elemental terminology, repeated Arabic talent names, and conflicts between catalog entries and glossary terms. The follow-up verification below is a structural and terminology scan; it is not a complete sentence-by-sentence linguistic review of all talent summaries.

## Canonical elemental terminology

The glossary now contains one draft canonical Arabic label for each playable element:

| English source term | Canonical Arabic draft |
|---|---|
| Anemo | أنيمو |
| Geo | جيو |
| Electro | إلكترو |
| Dendro | دندرو |
| Hydro | هيدرو |
| Pyro | بايرو |
| Cryo | كرايو |

When a talent summary explicitly describes elemental damage, the intended project convention is to use these names rather than descriptive alternatives such as "ضرر كهربائي", "ضرر جغرافي", "ضرر نباتي", "ضرر مائي", "ضرر ناري", "ضرر جليدي", or "ضرر هوائي". Descriptive words for visual objects or effects (for example, a water bubble or an ice flower) are retained when they do not label the damage element.

## Corrections made in the earlier audit

- Added 7 canonical elemental terms to `ar/glossary.json`; all remain `draft`.
- Standardized elemental-damage wording in 45 talent records, using each character's element and the Traveler's element-specific kit as context.
- Standardized 44 instances of "ضربة غطس" to the glossary-aligned "هجوم غطس".
- Standardized 2 instances of "ضربة مشحونة" to "هجوم مشحون".
- Resolved one duplicate Arabic talent name: Kamisato Art: Kyouka remains "فن كاميساتو: كيوكا", while Kamisato Art: Hyouka is now "فن كاميساتو: هيوكا".
- Aligned the material name for Acquaint Fate from "القدر المألوف" to the glossary translation "قدر التعارف".

These bullets describe earlier changes and are not a claim that every remaining talent summary has since received a full semantic review.

## Current structural snapshot

The previous snapshot in this document reported 35 glossary entries and 817 total records. A fresh count of all seven current Arabic JSON catalogs gives:

| Catalog | Current records |
|---|---:|
| Glossary | 46 |
| Characters | 123 |
| Talents | 387 |
| Weapons | 253 |
| Materials | 5 |
| Resources | 8 |
| Artifacts | 6 |
| **Total** | **828** |

All 828 records remain in draft status: 782 catalog records use `translation_status: "draft"`, while the 46 glossary records use `status: "draft"`. No record was promoted to `reviewed` or `approved` in this follow-up.

The earlier audit snapshot of 35 glossary entries / 817 total records is superseded by the current counts above.

## Follow-up terminology findings — unresolved

A targeted scan of the 387 talent summaries found the following remaining variants that differ from the glossary's canonical elemental labels:

| Canonical term | Remaining variant | Matching talent summaries |
|---|---|---:|
| Hydro / هيدرو | هايدرو | 5 |
| Cryo / كرايو | كريو | 18 |
| Dendro / دندرو | ديندرو | 7 |
| Anemo / أنيمو | "هوائي" used as a damage label in Xiao's Burst summary | 1 |

These are recorded as unresolved terminology findings, not automatically accepted translation errors. Their surrounding Arabic wording should be checked before any edit. In particular, descriptive Arabic adjectives must not be changed when they refer to a visual effect rather than the game's elemental damage type.

## Talent source-traceability limitations

- All 387 talent records currently have `description_source: null`; this prevents a direct per-record description-source citation from that field.
- 30 talent records across 10 characters use the generic GenshinDB repository URL rather than a character-specific talent-data URL.
- A spot comparison with individual GenshinDB talent data confirmed matching English talent names for the sampled characters Xiao, Kaveh, Lauma, Vodyanitsa, and Sigewinne, and Traveler Cryo. This sample is not evidence that all 387 Arabic summaries have been semantically verified.
- The other checked source records and local catalog structure do not replace a complete source-by-source review of every Arabic summary.

## Structural checks

The automated validator reports no structural or cross-reference errors in the current catalogs. The GitHub Actions validator run checked 7 Arabic JSON catalogs and 828 records. Its regression suite ran 19 tests successfully.

- No duplicate IDs were found within any catalog file.
- No missing Arabic name/translation fields were found in the checked catalogs.
- The talent matrix contains 366 regular-character talents and 21 Traveler talents.
- All regular characters have the expected three talent slots; the Traveler has seven element kits with three slots each.
- The materials/glossary comparison matches for all five material entries.
- The previous duplicate Arabic talent name was resolved.

## Limitations and review status

This is a consistency and structural audit, not a professional linguistic review or an official HoYoverse localization. The canonical element labels are project conventions proposed for consistency. Reviewers should still compare them with Arabic community usage and evaluate each talent name and summary in context. Automated replacements were limited to explicit elemental-damage phrases and known terminology variants; descriptive references to water, fire, ice, wind, and other visual effects were retained where they do not denote the game's element label.

No claim is made that this catalog displays Arabic inside the live game. No claim is made that all 387 talent summaries have been individually semantically verified or human-reviewed.
