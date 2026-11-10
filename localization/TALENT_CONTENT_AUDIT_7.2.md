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

The repository's GitHub Actions run #18 completed successfully on commit
`6304cd2b933a8b614ca4e504c813a46b141d5b96`: all 22 regression tests passed,
then the validator checked all 7 Arabic JSON catalogs and 828 records with
no errors. The added stale-review-note regression case passed as part of that
run. See [the run log](https://github.com/dark06fj-rgb/GenshinAutoAssistant/actions/runs/42864206952).

## Editorial policy

Keep all entries in `draft` until a human reviewer compares each name and
summary with reliable source data and actual gameplay. Never treat a green
validator result as approval or as evidence of an official HoYoverse Arabic
translation.


## Source-backed semantic and terminology follow-up — 2026-11-10

### Source snapshot and coverage

The 387 combat records were matched against the English combat talent files in
[genshin-db at commit `8e5badd60b5d894284ccc927a56c9683529d2592`](https://github.com/theBowja/genshin-db/tree/8e5badd60b5d894284ccc927a56c9683529/src/data/English/talents).
That upstream commit is dated 2026-11-05 and is labelled `7.2 actual`.

- 122 regular-character source files and all 7 Traveler element files were retrieved.
- All 387 expected `combat1` / `combat2` / `combat3` slots were found.
- All 387 English `source_name` values match the corresponding upstream talent name exactly.
- No source file or combat slot was missing in this comparison.
- This verifies source-name mapping and enables context checks; it does not establish that every Arabic summary is complete or linguistically approved.

### Confirmed source-backed corrections

A direct comparison of the relevant upstream descriptions showed that the following existing summaries contained factual mismatches or omitted important combat effects. The original wording is retained in the **Before** column so the edits are auditable.

| Talent ID | Before | After |
|---|---|---|
| `character.beidou.talent.skill` | ترفع سيفها لصد الهجمات ثم تطلق ضربة مضادة، وتزداد قوتها بحسب الضرر الذي امتصته. | تطلق ضربة إلكترو أمامية عند الضغط السريع؛ ويتيح الضغط المطول رفع سيفها كدرع لامتصاص الهجمات، ثم تنفيذ ضربة مضادة تزداد قوتها بحسب عدد مرات تعرضها للهجوم أثناء الصد. |
| `character.beidou.talent.burst` | تطلق قوة البرق حولها، مانحة درعاً كهربائياً وهجمات برق متسلسلة عند إصابة الأعداء. | تستحضر قوة البرق لتسبب ضرر إلكترو للأعداء القريبين، ثم تطلق هجماتها العادية والمشحونة تفريغات برق متسلسلة؛ كما تقلل الضرر المتلقى وتزيد مقاومة المقاطعة. |
| `character.hutao.talent.skill` | تستهلك جزءاً من صحتها للدخول في حالة تعزز هجماتها وتحول ضررها إلى ناري، وتضعف الأعداء بعلامة خاصة. | تستهلك جزءاً من صحتها للدخول في حالة تزيد هجومها وتحول ضرر هجماتها إلى بايرو؛ وتطبق الهجمات المشحونة علامة زهر الدم التي تسبب ضرر بايرو دورياً. |
| `character.razor.talent.burst` | يستدعي رايزر الذئب الداخلي ليقاتل إلى جانبه، مع تعزيز سرعة هجومه ومقاومته الكهربائية ومقاطعة الأعداء له. | يستدعي الذئب الداخلي ليقاتل إلى جانب رايزر ويطلق ضربات إلكترو معه؛ فيزيد سرعة هجومه ومقاومته لضرر إلكترو ومقاومته للمقاطعة، ويمنحه مناعة من ضرر حالة الشحن الكهربائي. |
| `character.noelle.talent.skill` | تنشئ درعاً من عنصر جيو وتسبب ضرراً للأعداء القريبين عند التفعيل. | تنشئ درعاً من عنصر جيو يسبب ضرراً للأعداء القريبين عند تفعيله؛ وتملك هجماتها العادية والمشحونة أثناء بقائه فرصة لاستعادة صحة جميع أعضاء الفريق. |
| `character.noelle.talent.burst` | تجمع القوة داخل سيفها وتوسع نطاق هجماتها وتحول ضررها إلى ضرر جيو. | تجمع قوة الحجر في سيفها، فتوسع نطاق هجماتها وتحول ضررها إلى ضرر جيو، كما تزيد هجومها بحسب دفاعها. |
| `character.ganyu.talent.normal` | تطلق سهاماً متتابعة، ويمكن شحن السهم لإحداث انفجار جليدي واسع. | تطلق سهاماً متتابعة، ويمكن شحن السهم لإحداث ضرر كرايو؛ وعند اكتمال الشحن تطلق سهماً إكليلياً ينفجر مسبباً ضرر كرايو واسعاً. |
| `character.ganyu.talent.burst` | تستدعي لؤلؤة جليدية تمطر شظايا على الأعداء داخل نطاق واسع. | تستدعي لؤلؤة كرايو مقدسة تمطر شظايا جليدية باستمرار على الأعداء ضمن نطاق، مسببة ضرر كرايو. |
| `character.nahida.talent.normal` | تنفذ هجمات نباتية متتابعة، مع هجوم مشحون وهجوم غطس تسبب ضرراً من عنصر دندرو ضمن نطاق. | تنفذ هجمات دندرو متتابعة، مع هجوم مشحون وهجوم غطس يسببان ضرر دندرو ضمن نطاق. |
| `character.prune.talent.normal` | تضرب برون بمطرقة العهد ضربات هوائية متتابعة، مع هجوم مشحون صاعدة وهجوم غطس. | تضرب برون بمطرقة العهد ضربات أنيمو متتابعة، مع هجوم مشحون صاعد وهجوم غطس. |
| `character.wanderer.talent.skill` | يطلق المتجول دفعة أنيمو ثم يحلّق في حالة الرياح المفضلة؛ وتتعزز هجماته العادية والمشحونة وتتحول إلى ضربات هوائية، مع استهلاك نقاط خاصة للحفاظ على التحليق. | يطلق المتجول دفعة أنيمو ثم يحلّق في حالة الرياح المفضلة؛ وتتعزز هجماته العادية والمشحونة وتتحول إلى ضربات أنيمو، مع استهلاك نقاط خاصة للحفاظ على التحليق. |
| `character.gorou.talent.normal` | يطلق غورو سهاماً متتابعة، ويمكنه شحن سهم جغرافي أو تنفيذ هجوم غطس. | يطلق غورو سهاماً متتابعة، ويمكنه شحن سهم جيو أو تنفيذ هجوم غطس. |
| `character.illuga.talent.burst` | يشعل إيلوغا مصباحه مسبباً ضرر جيو، ثم يمنح ضربات جيو لأعضاء الفريق تعزيزاً يتدرج عبر تراكمات؛ وتزداد فاعلية التعزيز مع المنشآت الجغرافية. | يشعل إيلوغا مصباحه مسبباً ضرر جيو، ثم يعزز ضرر ضربات جيو لأعضاء الفريق عبر تراكمات؛ وتمنحه إنشاءات جيو في الميدان تراكمات إضافية. |
| `character.linnea.talent.normal` | تطلق لينيا سهاماً متتابعة، ويمكنها شحن سهم جغرافي أو تنفيذ هجوم غطس. | تطلق لينيا سهاماً متتابعة، ويمكنها شحن سهم جيو أو تنفيذ هجوم غطس. |
| `character.navia.talent.skill` | تجمع نافيا شظايا الكريستال الناتجة عن التبلور، ثم تستهلكها لإطلاق طلقات روسولا الجغرافية من مظلتها المسلحة؛ ويزداد عدد الطلقات وقوتها مع التراكمات. | تجمع نافيا شظايا الكريستال الناتجة عن التبلور، ثم تستهلكها لإطلاق طلقات روسولا التي تسبب ضرر جيو وتخترق الأعداء؛ ويزداد عدد الطلقات وقوتها مع التراكمات. |
| `character.navia.talent.burst` | تستدعي نافيا قصفاً مدفعياً جغرافياً واسعاً، ثم يتواصل دعم المدافع لفترة ويمنحها شظايا كريستال عند إصابة الأعداء. | تستدعي نافيا قصفاً مدفعياً واسعاً يسبب ضرر جيو، ثم يواصل دعم المدافع إلحاق ضرر جيو بالأعداء القريبين ويمنحها شظايا كريستال عند إصابتهم. |
| `character.chiori.talent.skill` | تندفع شيوري للأمام وتستدعي دمية تاموتو التي تضرب الأعداء بضرر جيو؛ وقد تستدعي دمية إضافية عند وجود إنشاءات جغرافية. | تندفع شيوري للأمام وتستدعي دمية تاموتو التي تسبب ضرر جيو للأعداء؛ وقد تستدعي دمية إضافية عند وجود إنشاءات جيو قريبة. |

These edits correct Beidou's counter-scaling and Burst effects, Hu Tao's Blood Blossom behavior, Razor's separate Electro/interruption protections, Noelle's healing chance and DEF-based Burst ATK increase, and explicit element labels where the source clearly identifies Dendro, Anemo, or Geo damage/constructs. No long upstream descriptions were copied.

### Repeated and similar Arabic text

- Exact duplicate Arabic talent names: **0**.
- Exact duplicate summary groups: **4**; these are generic Normal Attack patterns shared by characters with the same basic attack sequence, including the Traveler's seven Normal Attack kits. They are not duplicate IDs.
- A same-talent-type character-bigram similarity scan found **172 pairs at or above 0.68**. The highest-scoring pairs are largely generic sword, claymore, and polearm Normal Attack templates. This heuristic is a review aid, not evidence of an error.
- Five near-similar talent-name pairs were detected. They correspond to shared technique-name stems or distinct named variants (including the Kamisato Kyouka/Hyouka pair); no exact duplicate label was found.

### Potential inconsistencies left unresolved

Several summaries still use descriptive forms such as `كهربائي`, `مائي`, `ناري`, or `جليدي` alongside canonical glossary element names. Some refer to visual objects or effects rather than the damage element, so they were **not** mass-replaced without a clear per-record basis. Examples requiring contextual editorial review include selected Electro projectile/attack descriptions and Hydro/Cryo visual descriptions. The current pass also found ordinary Normal Attack summaries that omit some secondary details (for example, optional targeting or hold behavior); such compression is not automatically an error.

### Structural and status recheck

- Characters: 123 total (122 regular plus one Traveler identity).
- Talents: 387 total (366 regular plus 21 Traveler).
- Glossary: 46 terms.
- Empty Arabic names/summaries: 0.
- Arabic talent-name duplicates: 0.
- Dangling character links, label mismatches, duplicate slots, and malformed talent IDs: 0 in the recheck.
- All 387 talent records remain `draft`; no status was promoted.

### Limits

This is a source-backed automated/editorial review, not a human linguistic or gameplay certification. The upstream comparison used genshin-db's English talent files; no independent line-by-line comparison against a second GenshinData snapshot or live in-game capture was completed. Every summary remains an original concise proposal and may omit secondary mechanics by design. Ambiguous wording remains unchanged pending contextual human review.


### CI verification

On commit `e1eb298e7a4f8c98b7c23a3ef897b1be1e418c17`, GitHub Actions workflow
[Localization validator tests #42877444585](https://github.com/dark06fj-rgb/GenshinAutoAssistant/actions/runs/42877444585)
completed successfully:

- Regression suite: **33 tests passed**.
- Catalog validator: **9 Arabic JSON catalogs, 2,418 records checked**.
- Result: **PASS** for JSON structure, IDs, source metadata, glossary links, and talent references.

The first run of the new regression test exposed one assertion-wording mismatch (`يزيد` versus the catalog's correct `تزيد`); the test assertion was corrected before the successful run above. No catalog translation status was changed.
