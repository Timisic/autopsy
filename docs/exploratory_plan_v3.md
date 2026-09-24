# E4: bounded exploratory optimization

Locked 2026-09-24 before running any new configuration. The original holdout
performance is already known. All E4 analyses are exploratory, including its
nested development cross-validation; no previously used participant becomes a
new external validation sample. Original primary results remain unchanged.

Use the original earliest-record dataset, 120 features, 933 development IDs and
104 holdout IDs. Recreate these from raw data and verify the saved partition.
No metadata, other questionnaire scores, or repeated observations enter X.

Motivation: strong shrinkage toward the mean and weak generalization justify
testing regularized, smooth nonlinear, and low-dimensional alternatives with
fold-local preprocessing. No raw text is available, so embeddings cannot be
reconstructed. Do not infer scale transformations or remove outcome outliers.

Exactly 22 configurations: mean (1), the previously selected shared RF (1),
standardized ridge with alpha 10/100/1000 using raw or log1p features (6),
RBF support-vector regression with C 0.1/1/10 and epsilon 0.1 (3), shallow
histogram boosting with 7 leaves, 100 iterations, learning rate .05 and L2
10/100 (2), elastic net with alpha .01/.1 and L1 ratio .1/.5 (4), PLS with
2/5/10 components (3), independent forests with leaf size 30/60 and half
the predictors per split (2). Forests have 256 trees. All non-PLS outcomes
are standardized inside fitting; PLS performs its own training-only scaling.
Median imputation and any input scaling/log transform are inside each fold.

Selection minimizes macro RMSE divided by each training fold's outcome SD,
averaged across three outcomes and five folds, using one candidate for all
targets. Ties follow configuration order. Five outer development folds each
contain five inner folds (seed 20260924 + outer index); compare the selected
procedure with the fixed original shared RF and mean on identical outer rows.
Retain all inner scores, predictions, warnings, and failures. Then apply the
same 22-candidate five-fold selection to all development participants, freeze
the choice, and evaluate only that choice once on the already-seen holdout.
Report Pearson r, RMSE, R-squared, Fisher-z/participant-bootstrap intervals,
and paired exploratory differences from the original RF and mean; Holm-adjust
six paired comparisons. These tests are descriptive post-selection evidence,
not renewed confirmatory tests.

Stop after the fixed grid and one final evaluation, even if results disappoint.
A practically encouraging result requires at least 1% lower macro normalized
RMSE than the original fixed RF in outer development folds. This is a
decision heuristic, not a clinical threshold or a significance criterion.
Do not replace the primary headline results; report both versions. Refit the
frozen winner from raw data in a separate directory and verify predictions.
