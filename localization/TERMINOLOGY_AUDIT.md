# Arabic Terminology Consistency Audit

Audit date: 2026-11-10  
Branch: `arabic-localization-catalog`

## Scope

Reviewed the Arabic glossary and the character, talent, weapon, material, resource, and artifact catalogs for duplicate IDs, missing Arabic names, inconsistent elemental terminology, repeated Arabic talent names, and conflicts between catalog entries and glossary terms.

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

When a talent summary explicitly describes elemental damage, the catalog uses these names rather than descriptive alternatives such as "ضرر كهربائي", "ضرر جغرافي", "ضرر نباتي", "ضرر مائي", "ضرر ناري", "ضرر جليدي", or "ضرر هوائي". Descriptive words for visual objects or effects (for example, a water bubble or an ice flower) are retained when they do not label the damage element.

## Corrections made

- Added 7 canonical elemental terms to `ar/glossary.json`; all remain `draft`.
- Standardized elemental-damage wording in 45 talent records, using each character's element and the Traveler's element-specific kit as context.
- Standardized 44 instances of "ضربة غطس" to the glossary-aligned "هجوم غطس".
- Standardized 2 instances of "ضربة مشحونة" to "هجوم مشحون".
- Resolved one duplicate Arabic talent name: Kamisato Art: Kyouka remains "فن كاميساتو: كيوكا", while Kamisato Art: Hyouka is now "فن كاميساتو: هيوكا".
- Aligned the material name for Acquaint Fate from "القدر المألوف" to the glossary translation "قدر التعارف".

## Structural checks

At the time of this audit:

| Catalog | Records |
|---|---:|
| Glossary | 35 |
| Characters | 123 |
| Talents | 387 |
| Weapons | 253 |
| Materials | 5 |
| Resources | 8 |
| Artifacts | 6 |
| **Total** | **817** |

- No duplicate IDs were found within any catalog file.
- No missing Arabic name/translation fields were found.
- All 817 entries remain `draft`; no translation was promoted to `reviewed` or `approved`.
- The materials/glossary comparison now matches for all five material entries.
- The previously detected duplicate Arabic talent name was resolved.

## Limitations and review status

This is a consistency and structural audit, not a professional linguistic review or an official HoYoverse localization. The canonical element labels are project conventions proposed for consistency. Reviewers should still compare them with Arabic community usage and evaluate each talent name and summary in context. Automated replacements were limited to explicit elemental-damage phrases and known terminology variants; descriptive references to water, fire, ice, wind, and other visual effects were retained where they do not denote the game's element label.

No claim is made that this catalog displays Arabic inside the live game.
