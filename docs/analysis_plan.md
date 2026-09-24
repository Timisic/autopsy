# Analysis protocol fixed before model comparison

Date: 2026-09-23. Version 1.0. This is a prospective computational plan within a retrospective reanalysis, not a publicly preregistered protocol. Raw-data structure and ranges were inspected before fixing this plan; model predictions and holdout performance were not.

## Questions and estimands

1. How well do supplied participant-level language features estimate negative affect, positive affect and life satisfaction in held-out participants?
2. Does shared multi-output learning improve prediction over independently fitted targets under the specified search budget?
3. Which supplied categories contribute to fitted predictions, and how stable are conclusions under plausible record and feature-handling choices?

The estimand is retrospective between-participant prediction of stored questionnaire scores in this convenience sample. It is not prospective detection, diagnosis, causal influence, within-person change, or validation of a deployable instrument.

## Input and unit decisions

Preserve original files and SHA-256 hashes. Targets are SWB_nn, SWB_pp, SWB_avg; predictors are exactly AGENCY through Hate (120 columns). Never use UID, metadata, other questionnaire fields, or survey time as predictors. UID is used only for grouping and partitioning.

There are 1,427 rows, 1,037 UIDs, and 195 exact duplicate rows. Each of 195 repeated UIDs has two distinct observations and one repeated observation. Remove exact duplicates and retain the record with the smallest stored SWB_FillTime, breaking any ties by source row. This is the earliest recorded survey under the numerical ordering of the supplied timestamp field; timestamp encoding and the origin of repeated observations remain unverified. Do not average observations or select records based on outcomes. Keep a row-level inclusion manifest.

Scores are analyzed in CSV units. Decimal grids are consistent with possible scale transformations but do not identify the actual scoring rule. Do not reverse-transform to PANAS or SWLS totals. Retain finite feature values as delivered, including ind values above one; flag the proportion-definition conflict and examine exclusion sensitivity. Do not delete statistical outliers. Unknown A, B, C1-C10, D columns remain eligible predictors but receive no invented psychological interpretation.

Available aggregate data cannot support word clouds, odd/even-post reliability, item internal consistency, demographic subgroup validation, raw-text re-extraction, or removal of post-questionnaire text. Report these as unavailable, without fabricating substitutes.

## Partition and leakage prevention

Sort unique UIDs numerically, then make a shuffled 90/10 split with random_state=20260923 (933 training participants, 104 test participants). Save IDs and row assignments. Within training use shuffled 5-fold KFold with the same seed. All imputers, min-max input scalers and target standardizers are fit only on each training fold. No feature selection or clipping is used. Test rows are not used for model selection, tuning, interpretation-feature selection, or analysis revisions.

The full-data audit includes validation of schema/ranges and descriptive summaries, not model-based decisions. Full pre-aggregation provenance cannot be independently verified; supplied features may include posts after questionnaire completion. Participant separation prevents person overlap, not temporal leakage inherent in unavailable source text.

## Models, score and fixed budget

Baseline: training mean for each target. Linear baseline: independent ridge. Single-target ensemble families: random forest, extra trees, histogram gradient boosting. Shared models: native multi-output random forest and extra trees (shared split structures), plus MultiTaskElasticNet (shared sparsity). MultiOutputRegressor wrappers, when used, are independent targets, not shared learning.

Primary selection score is the mean across five folds of macro normalized RMSE: per-target RMSE divided by that fold's training-target population SD, averaged across three targets. Input min-max scaling follows the supplied Method; fold-local target standardization makes shared-output losses comparable across outcomes. Report all final errors in original CSV units. Pearson r is a secondary validity indicator and never the selection/stop criterion.

Exact grids are in configs/analysis.json. Forests have 256 trees; histogram boosting uses 150 iterations, learning_rate=.05, min_samples_leaf=20, early_stopping=False. MultiTaskElasticNet uses max_iter=10000 and tol=1e-5. There are 42 parameter configurations and 210 composite fold evaluations (each independent-target fit consists of three regressors). Independent families choose each target's parameters separately using its mean normalized RMSE; shared models choose one configuration by macro score. Each family's assembled score is compared to select the overall predictive winner (excluding the constant mean from interpretation); the best shared model and best independent ensemble are identified separately. Resolve ties by listed candidate order. No further search round is authorized by a favorable or unfavorable p value.

Save all fold predictions, per-fold scores, candidate tables, selected parameters, fitted estimators and runtimes. Training CV scores are tuning summaries and may be optimistic; only the untouched holdout estimates final performance. Stop after the fixed grid and planned diagnostics; preserve all negative/failure outcomes. A numerical failure is logged and excluded only with a reason.

## Final evaluation and uncertainty

After all selections and sensitivity specifications are saved, evaluate the same holdout once for every retained family. For each outcome/model report n, Pearson r, two-sided analytical Pearson p, Fisher-z 95% interval, RMSE, participant bootstrap percentile 95% interval (5,000 paired resamples), and R-squared. Correlations for constant predictions are undefined, not zero. All p values are descriptive in this single-sample reanalysis; additionally Holm-adjust the three primary winner correlations.

For winner vs training mean and best shared model vs best independent ensemble, report paired bootstrap RMSE differences (5,000 resamples) and a two-sided within-participant prediction-swap randomization test of mean squared-error differences (10,000 swaps, plus-one correction). Holm-adjust across the six planned outcome/comparison tests. Resampling conditions on fitted models and this split; it does not cover training-set or sampling-frame uncertainty. No claims of equivalence from nonsignificance.

## Prespecified robustness and interpretation

Before holdout evaluation, evaluate frozen primary-selected hyperparameters in training-only repeated CV (3 repetitions x 5 folds; seeds 20261023, 20261024, 20261025), with Spearman correlation as a monotonic robustness measure. These scores are diagnostics, not independently unbiased nested-CV estimates.

Three fixed-hyperparameter sensitivities are evaluated using unchanged train/test UID assignments: (a) latest unique survey record per UID; (b) single-observation UIDs only; (c) remove ind and unmapped A, B, C1-C10, D columns. Retrain each family's frozen configuration on the corresponding training data. These analyses assess ambiguity and do not replace the primary result or trigger optimization. No subgroup claim will be made for small samples.

Explain the best tree family selected using training CV (even if a linear model is the overall winner). Use TreeSHAP with explicit tree_path_dependent setting on training feature records; save per-person contributions and verify additivity. Explain independent estimators per target or native multi-output estimators as appropriate. Report mean absolute contributions in CSV units, not causal effects or significance. Complement these with permutation importance on held-out participants for the union of the top ten training-SHAP-ranked features per target, with 20 shuffles per feature. Correlated categories can split or substitute attribution; permutation spread is repeat variability, not a sampling-confidence interval. Unknown category labels are shown literally with their uncertainty.

## Reproducibility and deviations

Record input and code checksums, exact dependency versions, seeds, commands and runtime logs. Rebuild the final pipeline from original input into a separate verification run and compare primary selections and predictions numerically. Generate figure and manuscript numbers from saved machine-readable results. Any subsequent change motivated by final test results must be labeled exploratory and cannot overwrite this plan or the original result.
