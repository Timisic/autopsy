# Independent input and design review

Prepared 2026-09-23 from the three supplied text files and `data.csv`. This review inspected the raw data without fitting models, inspecting model outputs, or calculating test-set predictive performance. No published target-paper search was conducted. The primary analysis plan maintained by the main analyst is authoritative; the recommendations below are an independent check made before model evaluation.

## Source and row-unit findings

The SHA-256 of the inspected CSV is `c3565732297b972932a3b64ed20b95070a8de5b5269366ad78f699d3e24b2388`.

| Check | Observed finding | Consequence |
|---|---:|---|
| Raw rows | 1,427 | These are not 1,427 independent people. |
| Columns | 136 | The header is unique and every record has 136 fields. |
| Unique UID values | 1,037 | UID, stored as a string, is the participant grouping key. |
| UID multiplicity | 842 occur once; 195 occur three times | Participants must never cross development/test or CV folds. |
| Exact duplicate rows | 195 excess copies | Removing exact duplicate rows leaves 1,232 observations. |
| Distinct records per UID after exact deduplication | 842 have one; 195 have two | The second record is not a duplicate of the first measurement. |
| Repeated UIDs with differing outcome vector | 195/195 | Selecting or averaging repeated rows changes the estimand. |
| Repeated UIDs with differing text feature vector | 195/195 | These are not demonstrably identical text measurements. |
| Identical feature vectors belonging to different UIDs | 0 | No cross-UID exact feature duplicates were detected. |
| Missing/blank/nonfinite fields | 0 | All fields parse as finite numeric values; no imputation is currently needed. |
| Negative values anywhere | 0 | This does not independently prove all fields are correctly scaled. |
| Predictor columns | 120, from `AGENCY` through `Hate` inclusive | All 16 preceding fields must be excluded from the predictor matrix. |
| Constant or identical predictor columns | 0 | No all-constant or exact duplicate predictor columns were detected. |

The 16 excluded fields contain the UID, earliest/latest post timestamps, post count, additional scale scores, questionnaire completion duration, and questionnaire completion time. The three requested labels are selected from those preceding fields. Other scale scores must not be used as predictors or as stand-ins for unavailable raw questionnaire items.

### Recommended participant record rule

Deduplicate exact rows, then retain the observation with the smallest numeric `SWB_FillTime` for each UID, breaking any remaining ties by original CSV source-row number. This is an explicit new analysis decision because the supplied Method does not resolve repeated observations. It should be described as the earliest *stored questionnaire timestamp*, without claiming a verified date encoding. There are no ties between distinct rows at this minimum. All 1,037 selections equal the first occurrence of their UID in the CSV; the first 1,037 CSV data rows already contain 1,037 distinct UIDs.

The rule gives one feature/outcome observation per participant and avoids arbitrary averaging across changing questionnaire scores and changing text histories. The 195 later distinct records should be preserved, not discarded from the archive. A latest-record sensitivity analysis and a singleton-only sensitivity analysis are reasonable if specified before evaluation and run with frozen primary hyperparameters and the same UID partition. Do not use these repeated records to infer test–retest or split-half reliability: the measurement occasions, text-window overlap, and repeat-collection protocol are unverified.

## Labels and measurement units

The explicit data dictionary identifies `SWB_nn` as negative affect, `SWB_pp` as positive affect, and `SWB_avg` as life satisfaction. Its wording takes precedence over what the suffix `avg` might suggest. All three observed variables lie in [0, 1].

| Label | Distinct raw values | Raw-row mean | Raw-row SD | Observed spacing |
|---|---:|---:|---:|---|
| `SWB_nn` | 37 | 0.369569 | 0.160552 | Multiples of 0.025 |
| `SWB_pp` | 36 | 0.538980 | 0.152276 | Multiples of 0.025 |
| `SWB_avg` | 31 | 0.415837 | 0.208305 | Approximately multiples of 1/30, rounded to six decimals |

These raw-row descriptives are diagnostic only: they include repeated and duplicated people, so they must not be copied into the paper's primary participant description. The earliest-record means (SDs) are respectively 0.366803 (0.160467), 0.543322 (0.155732), and 0.418901 (0.209958), each with n = 1,037.

The observed spacing is compatible with affine rescaling of PANAS sums from [10, 50] and SWLS sums from [5, 35], as those intervals have widths 40 and 30. Compatibility is not documentation of the actual transformation. No transformation script, raw item scores, scale-total record, response instructions, or conversion provenance was supplied. Therefore, retain the CSV units in every model, RMSE, table, and plot, and explicitly state that exact transformation provenance is unavailable. Do not relabel RMSE as PANAS or SWLS raw-score points. Pearson correlation would be unchanged by a known positive affine transform, but that fact does not establish the transform.

The supplied text also varies in scale-source attribution: the data dictionary names Watson et al. (1988) for PANAS and Wu and Yao (2006) for translated SWLS, whereas the Method cites Crawford and Henry (2004) for PANAS and several different Chinese adaptation sources. A paper must distinguish the established instruments from the exact translation/version actually administered; the latter is not fully identified by the available CSV. Item-level internal consistency and measurement invariance cannot be calculated from aggregate scores.

## Feature interpretation and distribution concerns

The data dictionary provides a reliable *column boundary* but not a category-level codebook or extraction implementation. The supplied Method names five lexicons. Labels such as `HarmVirtue`, `Funct`, and `Happy` make some mappings plausible, but plausibility alone is insufficient to certify dictionary version, translation, tokenization, denominator, weighting, overlap policy, or exact category definition.

- `AGENCY`/`COMM`, the 11 moral-foundation-like fields from `HarmVirtue` to `MoralityGeneral`, and `ind`/`col` have plausible family names, but a definitive family mapping should be flagged as inferred unless a verified dictionary source resolves it.
- `A`, `B`, `C1` through `C10`, and `D` are 13 opaque category codes. Include them as supplied numerical predictors if the primary plan retains all 120 features, but do not assign them psychological meanings or silently guess their dictionary family.
- `Anger`, `LIWC-Sad`, `Sad`, `Angery`, `Happy`, `Fear`, and `Hate` must remain distinct columns. In particular, do not merge apparently similar emotion names. Preserve the supplied spelling `Angery` in code and a clearly documented display-label mapping if desired.
- `ind` has a maximum of 1.901524 and exceeds 1 in 50 raw rows, 42 exact-deduplicated observations, and 34 earliest participant records. This conflicts with describing *every* feature as an ordinary count divided by total words. It could reflect another scale or computation, but its origin is unknown. Do not clamp it to 1 or divide it by 100 without evidence. Retain the supplied values in the main all-feature analysis and prespecify exclusion of `ind` and the 13 opaque codes as a sensitivity analysis.
- Every other feature is between 0 and 1, and no feature has a negative value. The maximum of `col` is 0.675504345. These range checks do not independently validate denominator consistency across dictionaries.
- The feature categories may overlap or form hierarchies. For example, `Body` never exceeds `Bio`, `PosEmo` and `NegEmo` individually never exceed `Affect`, and `Pronoun` never exceeds `Funct`. Do not force feature rows to sum to one or treat the 120 entries as a mutually exclusive composition.

Some feature distributions have long upper tails. Among earliest participant records, `Body` has median 0.014547 and maximum 0.153722; `Bio` has median 0.028167 and maximum 0.156406. Such high values can be genuine language concentration and do not by themselves justify deleting participants. Any optional winsorization or robust scaling must be fit on development folds only and labelled as a prespecified sensitivity analysis; it is not necessary simply because a value is far from the median. The post-count range is 598–16,042 (median 2,622) in the earliest sample. Questionnaire duration ranges up to 11,617 seconds and has a median of 384 seconds in that sample. Duration and post-count filters were not specified in the user Method beyond completion and eligibility conditions, so retrospectively inventing cutoffs would change the sample without a documented basis.

## Chronology and unsupported Method components

The numeric post timestamps and survey timestamps have an Excel-compatible form, but their encoding is not documented. Comparisons below only require a common increasing encoding, which itself should be described as an assumption rather than silently converted into confirmed dates.

| Chronology check | Raw rows | Exact-deduplicated observations | Earliest participant records |
|---|---:|---:|---:|
| Latest post timestamp exceeds questionnaire timestamp | 1,417/1,427 | 1,222/1,232 | 1,027/1,037 |
| Latest post timestamp precedes questionnaire timestamp | 10 | 10 | 10 |
| Latest post timestamp equals questionnaire timestamp | 0 | 0 | 0 |

For the earliest participant sample, latest-post minus questionnaire timestamp has median 20.66319 and range −171.32569 to 74.93681 serial units. For the 195 repeated participants, the difference between later and earlier questionnaire timestamps ranges from 78.98194 to 103.22986 (median 94.82986) serial units. These would be day differences under an Excel-day convention, but the observed fact is the numeric difference. The earliest-post timestamp never exceeds the latest-post timestamp and never exceeds the questionnaire timestamp in the raw rows.

These findings preclude presenting the current aggregate dataset as verified prediction from language available strictly *before* questionnaire completion. The appropriate claim is retrospective estimation of contemporaneous self-reported scores from supplied aggregate language features. Without raw post timestamps or verified extraction-window records, the amount of post-questionnaire language cannot be isolated or removed. This is a temporal applicability limitation even when participant separation is perfect; grouping by UID fixes participant overlap, not chronology.

| Supplied Method element | Available input | Disposition |
|---|---|---|
| Recruitment invitations, consent, exclusions, remuneration, ethics approval | Narrative only | Attribute to user-provided study documentation; do not imply independently audited recruitment or consent records. |
| Age, gender, location, education | Not present in the CSV | No demographic summaries, subgroup fairness comparisons, or demographic adjustment can be performed. |
| Raw PANAS/SWLS item responses and language versions | Not present | No item reliability, exact rescoring, or version verification. |
| Text matching and dictionary extraction | Aggregated features only | Analyze supplied features; cannot reproduce tokenization or extraction from source text. |
| Word clouds of specific words | No words or word-level frequencies | Not executable; category labels do not substitute for original words. |
| Chronologically odd/even post documents/features | Not present | Split-half reliability is not executable; the repeated observations are not evidence of odd/even halves. |
| Native multi-output regression | Three targets and 120 features present | Executable after participant deduplication/selection and grouped isolation. |
| SHAP or prediction-based importance | Trainable numerical features present | Executable with compatible model/software; category semantics and causal interpretation remain limited. |

## Bounded model and evaluation recommendations

1. **Estimand and primary question.** Predict the three supplied questionnaire-derived scores for unseen participants sampled from this convenience cohort. Treat this as an internal predictive validation, not instrument replacement, clinical assessment, causal explanation, or prospective screening. The same [0, 1] displayed range does not imply equal measurement reliability.
2. **Partition once.** Freeze one random 90%/10% UID split, giving 933 development and 104 test participants if the standard ceiling rule is used for the test size. Save the UID lists and seed. Since the primary dataset has one row per UID, ordinary shuffled five-fold CV is participant-disjoint; explicitly assert that property. Repeated-record sensitivities must reuse the UID allocation.
3. **Freeze the plan before fitting.** Save research questions, primary model-selection criterion, family comparisons, grids, seeds, search budget, stopping rule, and all planned sensitivity analyses. Do not choose the final model from the test results. If the plan selects one model per label, disclose that selection rule; if it selects one overall system, macro-average the predeclared per-label loss consistently.
4. **Baselines and estimators.** Include a development-fold mean predictor and a regularized linear baseline. A native multi-output Ridge call alone does not learn a shared sparse structure or correlated-output loss and should not be marketed as evidence of multi-task benefit. Random forests and extremely randomized trees can be compared as three independent single-target estimators versus native multi-output estimators with shared tree splits. A boosting model can be added as a bounded single-target comparator if included in the initial plan. Avoid claiming that fitting `MultiOutputRegressor` creates a joint multi-task objective.
5. **Search budget.** A small fixed grid is defensible for roughly 933 development participants and 120 correlated predictors. For example, fix tree count and vary a few `min_samples_leaf` values and `max_features` values; use a log-spaced Ridge alpha grid. Keep the total number of parameter combinations explicit, count independent per-target searches, and use the same CV folds across candidates. More trials should require a documented training-only reason and an amended plan recorded before test access. Never stop because a desired P value was obtained.
6. **Preprocessing.** Put median imputation (if retained for robustness), min–max normalization, feature selection, and any outcome scaling inside each training-fold pipeline. No current observations need imputation. Min–max scaling should not clip validation/test values unless clipping is separately specified; values outside a fitted training range are possible. Native tree regression does not require normalization, but a within-fold scaler can preserve the supplied Method without leaking held-out values. If target standardization is used to equalize joint split objectives, it must be learned only from training targets and reversed for scoring; document it as a Method adjustment.
7. **Selection criterion.** A predeclared macro-average RMSE in supplied score units is a straightforward primary criterion, with per-target Pearson r as a secondary predictive-association measure. Because observed target variances differ, also show performance relative to the corresponding training-mean baseline or standardized RMSE descriptively. A different predeclared primary criterion is permissible, but do not alternate between RMSE and correlation to select preferred results.
8. **One final test evaluation.** Save per-participant observed targets and predictions for every locked comparator. Report each target's test Pearson r and RMSE. A mean predictor's Pearson r is undefined, not zero: retain a missing value with an explanation. Use two-sided Pearson tests for nonconstant predictions and state that these test association with the observed criterion, not causal or practical validity.
9. **Uncertainty and multiplicity.** Use participant bootstrap resampling for RMSE intervals and, preferably, r intervals; retain the same resampled participant indices across models for paired differences. Fisher-z r intervals can additionally be reported with their assumptions. Fix a bootstrap budget (for example 5,000) and random seed, and count degenerate replicates explicitly. Pearson tests across the three primary targets can use Holm correction. For a declared multi-task versus single-task contrast, compare paired participant losses or paired differences in RMSE/r; a common-participant paired bootstrap is preferable to subtracting independent intervals. A sign-flip/permutation test of squared-error differences requires its exchangeability/symmetry conditions and should be described accordingly; it does not test that every metric or population property is equal. Do not treat overlapping CV folds as independent experimental replications in a t test.
10. **Feature interpretation.** Use a SHAP method compatible with the selected estimator or validation-fold permutation importance. Save explainer settings, background data, software versions, output shapes, and additivity checks. If a linear model wins, use an appropriate linear explanation rather than forcing TreeExplainer onto it. Prefer a locked training subset or development-fold explanations for pattern discovery; any test-set explanation is descriptive and must not drive refitting. Correlated features can redistribute SHAP credit and weaken permutation importance. No feature importance establishes a causal effect or a statistically significant psychological mechanism. Interpret opaque categories by their codes only.
11. **Planned robustness.** Retain the primary earliest observation rule; then evaluate latest observations, singleton participants, and omission of `ind` plus the 13 opaque categories with fixed primary hyperparameters and unchanged train/test UID membership. Keep separate result labels and sample sizes. A change in sample membership or outcome occasion changes the estimand, so the sensitivity estimates are not extra independent replications and should not replace a weak primary finding.
12. **Small held-out sample.** A 104-participant test set is appropriate to the supplied ratio but produces imprecise correlations and paired contrasts. Report the intervals and avoid a confident ranking when uncertainty is wide. Internal test performance cannot establish transportability to other years, platforms, age groups, or contemporary Weibo users.

## Independent review conclusion

The supplied numerical data support a bounded participant-level predictive analysis, including honest single-task/multi-task comparison and cautious feature interpretation. The most consequential corrections are recognizing 1,037 participants rather than 1,427 independent rows, selecting a documented observation per UID, keeping label units untransformed, acknowledging probable post-questionnaire text windows, and declining to manufacture word clouds or split-half reliability. A complete manuscript can report these limitations; it cannot claim that unavailable analyses or unverified collection details were independently reproduced.
