# Experiment and implementation record

## Input audit and protocol lock

2026-09-23. The original four research input files were left unchanged. The CSV audit found repeated participant IDs, exact copies, two distinct observations for 195 participants, unverified outcome transformation, ind values above one, missing feature-code mappings, and post-questionnaire text coverage. The plan was fixed before any model comparison. No test-model performance had been inspected. See analysis_plan.md, independent_data_review.md and the machine-readable audit.

## E0 — Retained development-only implementation preflight

Motivation: execute the fixed 42-configuration grid and independently review leakage and mathematical consistency. The first implementation fitted independent-target candidate regressors with a vector outcome scaler, then assembled final target-specific estimators with scalar outcome scalers. Synthetic review found tiny rounding differences that could change exactly tied random-forest split choices. The distinction was numerical, not information sharing or test leakage.

Decision: retain the complete development-only preflight outputs and its original script in scripts/archive/analyze_preflight.py. Repeat the same grid with scalar target fitting in both tuning and final independent models. No holdout predictions were produced for E0, and no empirical significance or desired outcome motivated the refinement. Initial process log: logs/selection.log. Retained output is results/preflight; the process originally wrote it under results/primary before archival. Its normalized-RMSE rankings are implementation diagnostics and are not the reported final evaluation. The archived script is an exact historical snapshot; to execute it, restore a copy to the scripts directory so its original relative project-root resolution remains valid.

## E1 — Final frozen implementation

Changes before test evaluation: use scalar target pipelines for each independent outcome in every CV fold; record successful and failed candidates separately; preserve explicit OOF-array UID row order; bind final selections to input, script, configuration, protocol, split, and OOF-order SHA-256 values. The candidate grids, seeds, primary score, participants, train/test assignment, and search budget did not change. The final tuning process initially writes results/final; this directory is moved to results/primary after the preflight completes, before final evaluation. Process log: logs/final_selection.log.

The final grid is limited to 42 configurations and 210 composite CV fits. All candidate records, parameter values, warnings, runtime, fold predictions, and outcome-specific scores are retained. The locked family selection is determined only from development folds. Frozen-parameter repeated development CV is diagnostic, not a second optimization round.

## E2 — Holdout evaluation and planned sensitivity checks

After E1 selection is locked and independently reviewed, evaluate every retained family on the same participant holdout. Run the three previously specified sensitivity datasets without retuning. Save predictions and all metric/comparison calculations, including adverse or nonsignificant results. No test-driven optimization is permitted. Actual results are generated into results/primary/metrics.csv and paired_comparisons.csv; the manuscript and figures are compiled from these files.

## E3 — Reproduction from raw input

Repeat the final analysis in a separate results/reproduction directory with the same locked environment and seeds. Compare partition assignments, selected parameters, primary predictions and metric outputs; retain quantitative comparisons in verification/reproduction.json. Disclose any differences instead of replacing the first final evaluation. A reproduction is not an independent empirical replication.

## Interpretation and artifact checks

Training-only TreeSHAP selects features for heldout permutation diagnostics. The best tree family is identified separately from the overall winner when needed. Explainability outputs are descriptive model behavior and cannot be interpreted as causal effects or psychological importance significance tests. Original figure sources and high-resolution grayscale/vector exports are retained. Manuscript table numbers and text values are generated from the saved result files; document layout is rendered and visually reviewed.

## Excluded and unavailable analyses

Raw-word clouds, odd/even-post split-half reliability, questionnaire internal consistency, verified raw-unit score recovery, demographic subgroup checks, and a pre-questionnaire feature window are unsupported by supplied inputs. Repeated survey rows are not substitutes for split-half text features. No values were manufactured for these analyses.

## External-source boundary

The target published study was not sought or used. Sources retained for scholarly claims were independently acquired through authorized public publisher or author-hosted routes and stored through Zotero MCP. Official journal rules and general publisher policies are archived separately. No manuscript submission, public data release, or correspondence with other people was performed.

## Final execution outcomes

E1 completed all 42 candidates without failures or warnings. Shared random forest was selected by the frozen development metric (macro normalized RMSE 0.9963403962), marginally ahead of independent random forest (0.9964818332); this did not justify expanding the search. E2 retained all eight families across four datasets (32 prediction files and 96 outcome-metric rows). Primary winner correlations were 0.2467042330, 0.2844371940 and 0.1519207472 for negative affect, positive affect and life satisfaction; RMSEs were 0.1661067154, 0.1648669757 and 0.2024146798 in stored units. All six planned paired error-comparison Holm P values exceeded .10. These modest and negative comparison findings were retained without retuning.

E3 independently repeated the unchanged 42-candidate selection and all 32 final model/dataset evaluations from the original CSV. Participant manifests, all candidate OOF predictions, parameter selections, final predictions, metric estimates/intervals, and paired comparisons matched exactly (maximum absolute differences 0). Frozen repeated development CV was not repeated because it does not determine final predictions or selection; its original 15-fold diagnostics are preserved. An independent arithmetic reviewer then recomputed all candidate/holdout metrics and resampling comparisons from saved arrays: 9,175 checks passed, maximum numerical discrepancy 1.33e-15.

Document/figure revisions after evaluation were presentational only: shorten flowchart text to keep it inside boxes; use exact decimal histogram bin boundaries instead of accumulated floating-step boundaries; remove a redundant table page break; restore APA reference italics; clarify one criterion-provenance sentence. Initial flow/histogram exports and earlier document renders remain archived. No model, feature-selection rule, test prediction, or inferential analysis changed after final evaluation.

At the user's later request, an additional LaTeX package was generated from the same final Markdown. It preserves the 14 sources, all numerical content, and vector figures; no analysis was rerun to support the format change. The Tectonic bootstrap/cache and all compilation logs are retained. Layout fixes made signed decimals nonbreaking, kept supplementary headings with their figures, and enabled DOI line wrapping. The final PDFs have 24, 7 and 3 pages, with 405 table cells, 27 citation mentions, and 26 reference italic spans independently checked. The 13-entry data-free ZIP was then extracted into an independent directory and all three documents compiled successfully without original Markdown or participant data; extracted PDF text matched the delivery. Earlier failed or superseded layout/check artifacts remain archived.

## Editorial revision v2

The subsequent user request moved primary figures/tables into the paper's argument, requested more conventional scientific prose and improved display design, and asked for Zotero-grounded and Socratic review. Version 1 was archived in revisions/v1_before_inline_revision before modification. The Introduction/Methods/Results were reorganized and Discussion was rewritten in four evidence-linked sections. Live Zotero collection/fulltext checks, 15 Socratic questions, and 47 independent numeric/placement checks are retained under verification/revision_v2. All 14 scholarly sources remain in scope; 30 author-year mentions include narrative citations. Six displays were redesigned in colorblind-safe color and neutral grayscale. The 196 original analysis files and six figure-source CSVs remain byte-identical. No additional predictive-model search, fitting, hypothesis test, selection decision, or statistical estimate was introduced. Current page counts and display locations are given by the rebuilt document/LaTeX manifests; the earlier 24/7/3 counts above describe v1 only.

## E4 — Exploratory optimization and literature expansion (2026-09-24)

The user requested additional pre-August-2024 literature and permitted further optimization if the first results were weak. Before new fitting, docs/exploratory_plan_v3.md fixed 22 configurations and a five-by-five nested development design. The original 104-participant holdout was already known; all new results are exploratory. The 22 configurations were evaluated in five inner searches and one full-development search, producing 132 candidate records and 660 composite fold fits, all successful and without captured warnings. The full-development choice was independent RF with 256 trees, minimum leaf size 60 and max_features 0.5.

Nested development macro normalized RMSE was 1.0005804534 for the selected procedure, 1.0001397616 for fixed original shared RF, and 1.0007300981 for mean. The added search increased error by 0.044% relative to original RF and did not satisfy the fixed 1% improvement heuristic. On the reused holdout, r was 0.2445266302, 0.3320085544, 0.1644739087 and RMSE 0.1660839201, 0.1644711759, 0.2023240635. Positive affect versus mean yielded exploratory six-comparison Holm P = 0.0113988601; all new-versus-original RF adjusted P values were 1.0 and all corresponding difference intervals contained zero. Both favorable and unfavorable results were retained; no further grid was opened.

An independent arithmetic script verified 2,529 scalar quantities with maximum discrepancy 2.22e-16. A separate frozen-choice refit from data.csv reproduced all new holdout predictions exactly. The original 390 protected primary, reproduction and input files are unchanged. This is a computational refit, not independent-sample replication. Figures interpreting the original primary model remain tied to that model.

Sixteen full-text sources were added through Zotero MCP to S2S9AGIR, with source-location and applicability notes. The final bibliography contains 30 works, all before 2024-08-01, and no target published article. Local imported bytes match the retained sources. New manuscript paragraphs and exploratory supplementary tables were generated as 198 paired English/Chinese blocks; the 179-word English abstract preserves original headline results. The former manuscripts and all original analyses are archived or retained.
