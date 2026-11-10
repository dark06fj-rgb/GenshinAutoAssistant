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

## Follow-up terminology findings — superseded by the normalization below

A targeted scan of the 387 talent summaries found the following remaining variants that differ from the glossary's canonical elemental labels:

| Canonical term | Remaining variant | Matching talent summaries |
|---|---|---:|
| Hydro / هيدرو | هايدرو | 5 |
| Cryo / كرايو | كريو | 18 |
| Dendro / دندرو | ديندرو | 7 |
| Anemo / أنيمو | "هوائي" used as a damage label in Xiao's Burst summary | 1 |

This table is the pre-normalization snapshot. The records were subsequently checked in context and corrected in the normalization section below. Generic descriptive adjectives remain untouched when they refer to visual effects rather than the game's elemental damage type.

## Talent source-traceability limitations

- All 387 talent records currently have `description_source: null`; this prevents a direct per-record description-source citation from that field.
- 30 talent records across 10 characters use the generic GenshinDB repository URL rather than a character-specific talent-data URL.
- A spot comparison with individual GenshinDB talent data confirmed matching English talent names for the sampled characters Xiao, Kaveh, Lauma, Vodyanitsa, and Sigewinne, and Traveler Cryo. This sample is not evidence that all 387 Arabic summaries have been semantically verified.
- The other checked source records and local catalog structure do not replace a complete source-by-source review of every Arabic summary.

## Structural checks

The automated validator reports no structural or cross-reference errors in the current catalogs. On commit `53446fda1eb7c4730693b682904acf1ab20be0cd`, GitHub Actions checked 7 Arabic JSON catalogs and 828 records; the validator test suite ran 21 tests successfully.

- No duplicate IDs were found within any catalog file.
- No missing Arabic name/translation fields were found in the checked catalogs.
- The talent matrix contains 366 regular-character talents and 21 Traveler talents.
- All regular characters have the expected three talent slots; the Traveler has seven element kits with three slots each.
- The materials/glossary comparison matches for all five material entries.
- The previous duplicate Arabic talent name was resolved.

## Limitations and review status

This is a consistency and structural audit, not a professional linguistic review or an official HoYoverse localization. The canonical element labels are project conventions proposed for consistency. Reviewers should still compare them with Arabic community usage and evaluate each talent name and summary in context. Automated replacements were limited to explicit elemental-damage phrases and known terminology variants; descriptive references to water, fire, ice, wind, and other visual effects were retained where they do not denote the game's element label.

No claim is made that this catalog displays Arabic inside the live game. No claim is made that all 387 talent summaries have been individually semantically verified or human-reviewed.


## Terminology normalization — 2026-11-10

A fresh scan of all 387 talent summaries found and normalized **31 records** with non-canonical elemental labels in clear element/damage contexts:

| Canonical glossary label | Original variant | Records corrected |
|---|---|---:|
| هيدرو | هايدرو | 5 |
| كرايو | كريو | 18 |
| دندرو | ديندرو | 7 |
| أنيمو | «ضررها إلى هوائي» in Xiao's Burst | 1 |

The earlier scan's counts (5 / 18 / 7 / 1) are confirmed by the record-level recheck. The corrected set contains 31 talent records. This is a terminology consistency correction, not a complete linguistic review of all summaries.

### Original-to-corrected record log

- `character.xiao.talent.burst` (Xiao): «يرتدي قناع اليكشا لتعزيز قفزاته وهجمات الغطس وتحويل ضررها إلى هوائي، مقابل استنزاف صحته تدريجياً.» → «يرتدي قناع اليكشا لتعزيز قفزاته وهجمات الغطس وتحويل ضررها إلى أنيمو، مقابل استنزاف صحته تدريجياً.»
- `character.aloy.talent.normal` (Aloy): «تطلق سهاماً متتابعة، ويمكنها شحن سهم جليدي لإحداث ضرر كريو.» → «تطلق سهاماً متتابعة، ويمكنها شحن سهم جليدي لإحداث ضرر كرايو.»
- `character.aloy.talent.burst` (Aloy): «تطلق خلية طاقة جليدية تنفجر مسببة ضرراً كريو ضمن نطاق.» → «تطلق خلية طاقة جليدية تنفجر مسببة ضرراً كرايو ضمن نطاق.»
- `character.charlotte.talent.normal` (Charlotte): «تنفذ شارلوت هجمات كريو متتابعة؛ ويمكنها شحن هجوم يصيب مساحة، أو تنفيذ هجوم غطس.» → «تنفذ شارلوت هجمات كرايو متتابعة؛ ويمكنها شحن هجوم يصيب مساحة، أو تنفيذ هجوم غطس.»
- `character.charlotte.talent.skill` (Charlotte): «تلتقط صورة بكاميرتها لإلحاق ضرر كريو وتطبيق تأثير على الأعداء؛ ويتيح الضغط المطول تحديد أهداف أكثر وتأثيراً أقوى.» → «تلتقط صورة بكاميرتها لإلحاق ضرر كرايو وتطبيق تأثير على الأعداء؛ ويتيح الضغط المطول تحديد أهداف أكثر وتأثيراً أقوى.»
- `character.charlotte.talent.burst` (Charlotte): «تنشئ شارلوت مجالاً إخبارياً يسبب ضرر كريو دورياً ويستعيد صحة أعضاء الفريق.» → «تنشئ شارلوت مجالاً إخبارياً يسبب ضرر كرايو دورياً ويستعيد صحة أعضاء الفريق.»
- `character.chongyun.talent.skill` (Chongyun): «يضرب الأرض لينشئ انفجار كريو ومجالاً يعزز أسلحة مستخدمي السيف والسيف العظيم والرمح بعنصر كريو.» → «يضرب الأرض لينشئ انفجار كرايو ومجالاً يعزز أسلحة مستخدمي السيف والسيف العظيم والرمح بعنصر كرايو.»
- `character.chongyun.talent.burst` (Chongyun): «يستدعي ثلاثة أنصال روحية ضخمة تسقط تباعاً وتنفجر، مسببة ضرر كريو وقاذفة الأعداء.» → «يستدعي ثلاثة أنصال روحية ضخمة تسقط تباعاً وتنفجر، مسببة ضرر كرايو وقاذفة الأعداء.»
- `character.citlali.talent.normal` (Citlali): «تنفذ سيتلالي ضربات كريو متتابعة، ويمكنها إطلاق نجمة صقيع مشحونة أو تنفيذ هجوم غطس.» → «تنفذ سيتلالي ضربات كرايو متتابعة، ويمكنها إطلاق نجمة صقيع مشحونة أو تنفيذ هجوم غطس.»
- `character.citlali.talent.burst` (Citlali): «تستدعي عاصفة جليدية تصيب مساحة، وتستدعي جماجم وعاء الروح قرب الأعداء لتنفجر وتسبب ضرر كريو.» → «تستدعي عاصفة جليدية تصيب مساحة، وتستدعي جماجم وعاء الروح قرب الأعداء لتنفجر وتسبب ضرر كرايو.»
- `character.diona.talent.skill` (Diona): «تطلق ديونا كفوفاً جليدية تسبب ضرر كريو وتنشئ درعاً؛ ويمنح الضغط المطول درعاً أقوى عند إصابة عدة أهداف.» → «تطلق ديونا كفوفاً جليدية تسبب ضرر كرايو وتنشئ درعاً؛ ويمنح الضغط المطول درعاً أقوى عند إصابة عدة أهداف.»
- `character.diona.talent.burst` (Diona): «ترمي ديونا شراباً بارداً ينشئ ضباباً يسبب ضرر كريو للأعداء ويستعيد صحة الشخصيات داخله.» → «ترمي ديونا شراباً بارداً ينشئ ضباباً يسبب ضرر كرايو للأعداء ويستعيد صحة الشخصيات داخله.»
- `character.eula.talent.skill` (Eula): «تضرب يولا بضرر كريو وتجمع تراكمات القلب القاتم؛ ويمكنها استهلاكها بهجوم واسع يقلل مقاومة الأعداء للضرر الفيزيائي والكريو.» → «تضرب يولا بضرر كرايو وتجمع تراكمات القلب القاتم؛ ويمكنها استهلاكها بهجوم واسع يقلل مقاومة الأعداء للضرر الفيزيائي والكرايو.»
- `character.eula.talent.burst` (Eula): «تسبب ضرر كريو وتستدعي سيف سقوط الضوء الذي يشحن مع هجماتها قبل أن ينفجر مسبباً ضرراً فيزيائياً.» → «تسبب ضرر كرايو وتستدعي سيف سقوط الضوء الذي يشحن مع هجماتها قبل أن ينفجر مسبباً ضرراً فيزيائياً.»
- `character.escoffier.talent.skill` (Escoffier): «تفعّل آلة الطهي متعددة الاستخدامات لتتبع الشخصية النشطة وإطلاق حلوى مثلجة تسبب ضرر كريو؛ ويمكن للضغط المطول تفعيل نمط طهي آخر.» → «تفعّل آلة الطهي متعددة الاستخدامات لتتبع الشخصية النشطة وإطلاق حلوى مثلجة تسبب ضرر كرايو؛ ويمكن للضغط المطول تفعيل نمط طهي آخر.»
- `character.escoffier.talent.burst` (Escoffier): «تطلق إسكوفير ضربة كريو واسعة وتستعيد صحة أعضاء الفريق القريبين وفقاً لهجومها.» → «تطلق إسكوفير ضربة كرايو واسعة وتستعيد صحة أعضاء الفريق القريبين وفقاً لهجومها.»
- `character.freminet.talent.skill` (Freminet): «يدخل فريمينيه حالة مؤقتة تتدرج فيها قوة الضغط؛ ويطلق بعدها ضربة كريو أو مزيجاً من الضرر الكريو والفيزيائي بحسب مستوى الضغط.» → «يدخل فريمينيه حالة مؤقتة تتدرج فيها قوة الضغط؛ ويطلق بعدها ضربة كرايو أو مزيجاً من الضرر الكرايو والفيزيائي بحسب مستوى الضغط.»
- `character.kaveh.talent.skill` (Kaveh): «يستخدم كافيه قدرة مهرَك على المسح لإطلاق موجة ديندرو واسعة، فتفجّر نوى ديندرو الموجودة ضمن نطاقها فوراً.» → «يستخدم كافيه قدرة مهرَك على المسح لإطلاق موجة دندرو واسعة، فتفجّر نوى دندرو الموجودة ضمن نطاقها فوراً.»
- `character.lauma.talent.normal` (Lauma): «تنفذ لاوما هجمات ديندرو متتابعة؛ ويمكنها التحول إلى مبعوثة الغابة والاندفاع والقفز، أو إطلاق صلاة روحية تسبب ضرراً واسعاً.» → «تنفذ لاوما هجمات دندرو متتابعة؛ ويمكنها التحول إلى مبعوثة الغابة والاندفاع والقفز، أو إطلاق صلاة روحية تسبب ضرراً واسعاً.»
- `character.lauma.talent.skill` (Lauma): «تنشد لاوما ترنيمة تستدعي ملاذاً غابياً؛ والضغط المطول يستهلك قطرات الندى الخضراء لإطلاق ضرر دندرو إضافي من نوع إزهار قمري ويقلل مقاومتي ديندرو وهيدرو لدى الأعداء.» → «تنشد لاوما ترنيمة تستدعي ملاذاً غابياً؛ والضغط المطول يستهلك قطرات الندى الخضراء لإطلاق ضرر دندرو إضافي من نوع إزهار قمري ويقلل مقاومتي دندرو وهيدرو لدى الأعداء.»
- `character.layla.talent.skill` (Layla): «تنشئ ليلى درع ستار السبات الذي يمتص الضرر الكريو بفاعلية أكبر؛ وتتجمع حوله نجوم ليلية تتحول إلى نجوم ساقطة تطارد الأعداء وتسبب ضرر كريو.» → «تنشئ ليلى درع ستار السبات الذي يمتص الضرر الكرايو بفاعلية أكبر؛ وتتجمع حوله نجوم ليلية تتحول إلى نجوم ساقطة تطارد الأعداء وتسبب ضرر كرايو.»
- `character.lohen.talent.burst` (Lohen): «ينفذ لوهن سلسلة سريعة من الضربات الأمامية ويستهلك جميع تراكمات إرادة الفوز لزيادة ضرر كريو؛ ويطيل وضع الضربة الحاسمة إن كان نشطاً.» → «ينفذ لوهن سلسلة سريعة من الضربات الأمامية ويستهلك جميع تراكمات إرادة الفوز لزيادة ضرر كرايو؛ ويطيل وضع الضربة الحاسمة إن كان نشطاً.»
- `character.nefer.talent.normal` (Nefer): «توجه نيفر ركلات ديندرو متتابعة؛ ويمكنها الانزلاق بسرعة في حالة خاصة ثم تنفيذ ضربة ديندرو عند إنهائها.» → «توجه نيفر ركلات دندرو متتابعة؛ ويمكنها الانزلاق بسرعة في حالة خاصة ثم تنفيذ ضربة دندرو عند إنهائها.»
- `character.tighnari.talent.normal` (Tighnari): «يطلق تيغناري سهاماً متتابعة، ويمكنه شحن سهم ديندرو أو سهماً إكليلياً ينشطر عند إصابة الهدف إلى أربعة أسهم تتعقب الأعداء.» → «يطلق تيغناري سهاماً متتابعة، ويمكنه شحن سهم دندرو أو سهماً إكليلياً ينشطر عند إصابة الهدف إلى أربعة أسهم تتعقب الأعداء.»
- `character.tighnari.talent.skill` (Tighnari): «يقذف تيغناري قلب عاصفة ديندرو ينشئ حقلاً من الأوهام يجذب هجمات الأعداء، ويقلل زمن شحن السهم الإكليلي لثلاث طلقات.» → «يقذف تيغناري قلب عاصفة دندرو ينشئ حقلاً من الأوهام يجذب هجمات الأعداء، ويقلل زمن شحن السهم الإكليلي لثلاث طلقات.»
- `character.10000077.talent.burst` (Yaoyao): «تطلق قوة يويغوي الكاملة، فتحسن الفجل العلاجي وتستدعي نسخاً إضافية منه، كما تزيد سرعة حركة ياوياو ومقاومتها لديندرو خلال الحالة.» → «تطلق قوة يويغوي الكاملة، فتحسن الفجل العلاجي وتستدعي نسخاً إضافية منه، كما تزيد سرعة حركة ياوياو ومقاومتها لدندرو خلال الحالة.»
- `character.10000140.talent.normal` (Vodyanitsa): «تؤدي أنشودة مائية قديمة عبر سلسلة هجمات تسبب ضرر هايدرو، مع هجوم مشحون وهجوم غطس.» → «تؤدي أنشودة مائية قديمة عبر سلسلة هجمات تسبب ضرر هيدرو، مع هجوم مشحون وهجوم غطس.»
- `character.10000140.talent.skill` (Vodyanitsa): «تكشف هيئتها الحقيقية كجنية ماء وتسبب ضرر هايدرو واسعاً، ثم تستدعي بوق الربيع ليهاجم الأعداء دورياً؛ كما تقلل مقاومتي هايدرو وكرايو وتدعم الشخصية النشطة بمقاومة المقاطعة واستعادة الصحة.» → «تكشف هيئتها الحقيقية كجنية ماء وتسبب ضرر هيدرو واسعاً، ثم تستدعي بوق الربيع ليهاجم الأعداء دورياً؛ كما تقلل مقاومتي هيدرو وكرايو وتدعم الشخصية النشطة بمقاومة المقاطعة واستعادة الصحة.»
- `character.10000140.talent.burst` (Vodyanitsa): «تقود أنشودة تستدرج الأعداء وتسبب لهم ضرر هايدرو واسعاً، ويزداد الضرر أثناء تأثير أغنية العصور الماضية.» → «تقود أنشودة تستدرج الأعداء وتسبب لهم ضرر هيدرو واسعاً، ويزداد الضرر أثناء تأثير أغنية العصور الماضية.»
- `character.10000095.talent.skill` (Sigewinne): «تطلق فقاعة علاجية ترتد بين الأعداء وتسبب ضرر هايدرو، وتعالج أعضاء الفريق القريبين عند ارتدادها؛ ويزداد حجمها وفعاليتها عند الضغط المطول.» → «تطلق فقاعة علاجية ترتد بين الأعداء وتسبب ضرر هيدرو، وتعالج أعضاء الفريق القريبين عند ارتدادها؛ ويزداد حجمها وفعاليتها عند الضغط المطول.»
- `character.10000095.talent.burst` (Sigewinne): «تستخدم حقنة خاصة لإطلاق موجات علاجية هجومية أمامها تسبب ضرر هايدرو واسعاً بحسب صحتها القصوى، وتمتص قطرات ماء قريبة.» → «تستخدم حقنة خاصة لإطلاق موجات علاجية هجومية أمامها تسبب ضرر هيدرو واسعاً بحسب صحتها القصوى، وتمتص قطرات ماء قريبة.»

Only elemental labels in talent summaries were changed. Generic visual descriptions such as «تيار هوائي» and «هجمات هوائية» were retained. Xiao's source data explicitly says his attack damage is converted to Anemo DMG; the Arabic label was therefore changed to «أنيمو». Source: https://github.com/theBowja/genshin-db/blob/main/src/data/English/talents/xiao.json

### Regression protection

The validator now rejects the four known non-canonical elemental labels in talent summaries. Regression tests cover each label, while a separate test confirms that ordinary visual wording such as «تيار هوائي» remains valid. No translation status was changed; all affected records remain drafts.
