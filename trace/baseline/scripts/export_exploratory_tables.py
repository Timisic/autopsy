#!/usr/bin/env python3
"""Export E4 table source data without fitting models or modifying predictions."""
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'results/exploratory_v3';T=ROOT/'tables'
folds=pd.read_csv(P/'nested_fold_metrics.csv')
folds.groupby(['procedure','target']).normalized_rmse.agg(['mean','std']).reset_index().to_csv(T/'tableS3_exploratory_nested.csv',index=False)
records=json.loads((P/'full_development/selection.json').read_text())['records']
pd.DataFrame([{'candidate':r['spec']['id'],'parameters':json.dumps(r['spec']),'macro_normalized_rmse':r['score']} for r in records]).to_csv(T/'tableS4_exploratory_grid.csv',index=False)
pd.read_csv(P/'holdout_metrics.csv',float_precision='round_trip').to_csv(T/'tableS5_exploratory_holdout.csv',index=False)
c=pd.read_csv(P/'paired_comparisons.csv',float_precision='round_trip');c['comparison']=c.model_b.map({'mean':'new_vs_mean','original_rf':'new_vs_original_shared_rf'});c.to_csv(T/'tableS6_exploratory_comparisons.csv',index=False)
print('Exported supplementary tables S3-S6.')
