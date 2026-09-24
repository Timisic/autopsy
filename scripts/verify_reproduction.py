#!/usr/bin/env python3
"""Compare independent reruns without accepting hidden mismatches."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from analyze import ROOT, sha, dump

def compare(reference,candidate):
    report={'reference':str(reference.relative_to(ROOT)),'candidate':str(candidate.relative_to(ROOT)),'checks':{},'max_primary_prediction_difference':0.0}
    for f in ['partition.csv','cv_row_order.csv','row_manifest.csv','cleaned_primary.csv','cleaned_latest.csv']:
        report['checks'][f]=sha(reference/f)==sha(candidate/f)
    left=json.loads((reference/'selection_locked.json').read_text()); right=json.loads((candidate/'selection_locked.json').read_text())
    for k in ['winner','best_shared','best_independent_ensemble','best_tree','models','input_sha256','script_sha256','protocol_sha256','config_sha256']:
        report['checks']['selection_'+k]=left[k]==right[k]
    cv1=pd.read_csv(reference/'cv_fold_scores.csv').sort_values(['family','candidate','fold','target']).reset_index(drop=True)
    cv2=pd.read_csv(candidate/'cv_fold_scores.csv').sort_values(['family','candidate','fold','target']).reset_index(drop=True)
    report['checks']['cv_scores_equal']=bool(np.allclose(cv1.select_dtypes('number'),cv2.select_dtypes('number'),equal_nan=True,rtol=0,atol=1e-12))
    report['checks']['cv_score_keys_equal']=cv1[['family','candidate','fold','target']].equals(cv2[['family','candidate','fold','target']])
    oof_differences={}
    for f in sorted((reference/'cv_predictions').glob('*.npy')):
        other=candidate/'cv_predictions'/f.name
        if not other.exists():
            report['checks']['oof_'+f.stem]=False
            continue
        a=np.load(f); b=np.load(other)
        oof_differences[f.name]=float(np.max(np.abs(a-b)))
        report['checks']['oof_'+f.stem]=bool(np.allclose(a,b,rtol=0,atol=1e-12,equal_nan=True))
    report['max_oof_difference']=max(oof_differences.values()) if oof_differences else None
    prediction_checks=[]
    for f in sorted((reference/'predictions').glob('*.csv')):
        other=candidate/'predictions'/f.name
        if not other.exists(): continue
        a=pd.read_csv(f,dtype={'UID':str});b=pd.read_csv(other,dtype={'UID':str})
        keys_equal=a[['UID','source_row']].equals(b[['UID','source_row']])
        cols=[c for c in a if c.startswith('pred_')]
        delta=float(np.max(np.abs(a[cols].to_numpy()-b[cols].to_numpy())))
        if f.name.startswith('primary_'): report['max_primary_prediction_difference']=max(report['max_primary_prediction_difference'],delta)
        prediction_checks.append({'file':f.name,'n':len(a),'keys_equal':keys_equal,'max_abs_prediction_difference':delta,'pass':keys_equal and delta<=1e-12})
    report['prediction_checks']=prediction_checks
    report['checks']['all_primary_families_reproduced']=sum(r['file'].startswith('primary_') for r in prediction_checks)==len(left['models'])
    a=pd.read_csv(reference/'metrics.csv'); b=pd.read_csv(candidate/'metrics.csv');key=['scenario','family','target']
    merged=a.merge(b,on=key,suffixes=('_original','_repeat'),validate='one_to_one')
    numcols=a.select_dtypes('number').columns
    metric_diffs={}
    for c in numcols:
        x=merged[c+'_original'].to_numpy(); y=merged[c+'_repeat'].to_numpy();mask=np.isfinite(x)&np.isfinite(y)
        metric_diffs[c]=float(np.max(np.abs(x[mask]-y[mask]))) if mask.any() else 0.0
        report['checks']['metric_'+c]=bool(np.allclose(x,y,rtol=0,atol=1e-12,equal_nan=True))
    report['metric_max_differences']=metric_diffs
    pairs_a=pd.read_csv(reference/'paired_comparisons.csv');pairs_b=pd.read_csv(candidate/'paired_comparisons.csv')
    report['checks']['paired_comparisons_match']=bool(pairs_a[['comparison','model_a','model_b','target']].equals(pairs_b[['comparison','model_a','model_b','target']]) and np.allclose(pairs_a.select_dtypes('number'),pairs_b.select_dtypes('number'),rtol=0,atol=1e-12,equal_nan=True))
    report['scope']='All shared scenario outputs compared. Missing non-primary scenarios are explicitly listed.'
    report['missing_prediction_files']=[f.name for f in (reference/'predictions').glob('*.csv') if not (candidate/'predictions'/f.name).exists()]
    report['passed']=all(report['checks'].values()) and all(r['pass'] for r in prediction_checks)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--reference',default='results/primary');p.add_argument('--candidate',default='results/reproduction');args=p.parse_args()
    report=compare(ROOT/args.reference,ROOT/args.candidate)
    dump(report,ROOT/'verification/reproduction.json')
    print(json.dumps(report,indent=2))
    if not report['passed']: raise SystemExit('Reproduction mismatch: inspect verification/reproduction.json')
