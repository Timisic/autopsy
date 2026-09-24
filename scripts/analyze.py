#!/usr/bin/env python3
"""Auditable fixed-budget participant-level reanalysis. See docs/analysis_plan.md."""
import argparse
import hashlib
import itertools
import json
import os
import platform
import sys
import time
import traceback
import warnings
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import joblib
import numpy as np
import pandas as pd
import scipy
from scipy import stats
import sklearn
from sklearn.base import clone
from sklearn.compose import TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge, MultiTaskElasticNet
from sklearn.model_selection import KFold, ParameterGrid, train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from statsmodels.stats.multitest import multipletests
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT/'configs/analysis.json').read_text())
TARGETS = CONFIG['targets']
SEED = CONFIG['seed']

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def dump(obj, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False, default=lambda x: x.item() if isinstance(x, np.generic) else str(x)))

def finite_or_none(x):
    return float(x) if np.isfinite(x) else None

def estimator(family, params, seed=SEED, single_target=False):
    if family == 'mean':
        model = DummyRegressor(strategy='mean')
    elif family == 'ridge':
        model = Ridge(**params)
    elif family == 'multitask_en':
        model = MultiTaskElasticNet(**params, random_state=seed, max_iter=10000, tol=1e-5)
    elif family.endswith('_rf') or family.endswith('_et'):
        cls = RandomForestRegressor if family.endswith('_rf') else ExtraTreesRegressor
        model = cls(**params, n_estimators=CONFIG['n_estimators'], random_state=seed, n_jobs=1)
    elif family == 'single_hgb':
        model = HistGradientBoostingRegressor(**params, max_iter=150, learning_rate=.05,
            min_samples_leaf=20, early_stopping=False, random_state=seed)
    else:
        raise ValueError(family)
    if family.startswith('single_') and not single_target:
        model = MultiOutputRegressor(model, n_jobs=1)
    # Target standardizer and X preprocessors refit inside every training fold.
    return TransformedTargetRegressor(regressor=make_pipeline(SimpleImputer(strategy='median'), MinMaxScaler(), model), transformer=StandardScaler())

def raw_audit(out):
    d = pd.read_csv(ROOT/'data.csv', dtype={'UID':str})
    features = d.columns[d.columns.get_loc(CONFIG['feature_start']):].tolist()
    raw_columns = d.columns.tolist()
    duplicate = d.duplicated()
    d = d.copy()
    d['source_row'] = np.arange(len(d)) + 2
    unique = d.loc[~duplicate].copy()
    first = unique.sort_values(['UID','SWB_FillTime','source_row']).drop_duplicates('UID',keep='first')
    last = unique.sort_values(['UID','SWB_FillTime','source_row']).drop_duplicates('UID',keep='last')
    # Numerical UID sort makes partition independent of original row order.
    ids = sorted(first.UID, key=int)
    first = first.set_index('UID').loc[ids].reset_index()
    last = last.set_index('UID').loc[ids].reset_index()
    assert first.UID.is_unique and len(first)==len(last)
    assert np.isfinite(d[TARGETS+features].to_numpy()).all()
    assert first[TARGETS].std().gt(0).all()
    train_i,test_i=train_test_split(np.arange(len(first)),test_size=CONFIG['test_fraction'],random_state=SEED)
    foldids=np.full(len(first),-1,dtype=int)
    folds=list(KFold(n_splits=CONFIG['folds'],shuffle=True,random_state=SEED).split(train_i))
    for k,(_,vi) in enumerate(folds): foldids[train_i[vi]]=k
    train_uids=set(first.iloc[train_i].UID)
    part=first[['UID','source_row']].copy()
    part['partition']=np.where(first.UID.isin(train_uids),'train','test')
    part['cv_fold']=foldids
    part.to_csv(out/'partition.csv',index=False)
    cv_order=part.iloc[train_i].copy()
    cv_order.insert(0,'oof_array_row',np.arange(len(train_i)))
    cv_order.to_csv(out/'cv_row_order.csv',index=False)
    manifest=d[['UID','source_row']].copy()
    keep_rows=set(first.source_row)
    manifest['decision']=['primary_earliest' if r in keep_rows else ('exact_duplicate' if dup else 'later_unique_observation') for r,dup in zip(d.source_row,duplicate)]
    manifest['partition']=np.where(d.UID.isin(train_uids),'train','test')
    manifest.to_csv(out/'row_manifest.csv',index=False)
    first.to_csv(out/'cleaned_primary.csv',index=False)
    last.to_csv(out/'cleaned_latest.csv',index=False)
    ranges=d[raw_columns[1:]].agg(['min','max','mean','std']).T
    ranges['missing']=d[raw_columns[1:]].isna().sum()
    ranges['unique_values']=d[raw_columns[1:]].nunique()
    ranges.to_csv(out/'column_audit.csv')
    first[TARGETS].describe().T.to_csv(out/'target_descriptives.csv')
    first[TARGETS].corr().to_csv(out/'target_correlations.csv')
    counts=d.UID.value_counts()
    qgrid={t:float(np.max(np.abs(first[t].to_numpy()*den-np.round(first[t].to_numpy()*den)))) for t,den in zip(TARGETS,[40,40,30])}
    audit={'raw_rows':len(d),'columns':len(raw_columns),'unique_participants':len(first),'exact_duplicate_rows':int(duplicate.sum()),
        'repeated_uids':int((counts>1).sum()),'uid_multiplicity':counts.value_counts().to_dict(),
        'features':features,'feature_count':len(features),'excluded_columns':raw_columns[:16],
        'missing_cells':int(d[raw_columns].isna().sum().sum()),'constant_features':d[features].columns[d[features].nunique()<2].tolist(),
        'negative_feature_cells':int((d[features]<0).sum().sum()),'feature_above_one_counts':{k:int(v) for k,v in (d[features]>1).sum().items() if v},
        'primary_ind_above_one':int((first['ind']>1).sum()),'labels_stored_range':{t:[float(first[t].min()),float(first[t].max())] for t in TARGETS},
        'candidate_grid_rounding_residuals_NOT_conversion_proof':qgrid,
        'primary_latest_post_after_questionnaire_count':int((first.iloc[:,2]>first.SWB_FillTime).sum()),
        'train_n':len(train_i),'test_n':len(test_i),'input_sha256':sha(ROOT/'data.csv'),
        'scale_status':'Unknown transformation; stored CSV units only.',
        'timestamp_status':'Numeric ordering used; epoch/units and collection wave provenance unverified.',
        'unavailable':['raw posts','word counts by word','odd/even features','item responses','demographics','dictionary versions and mappings of A B C1-C10 D','verified label transformation']}
    dump(audit,out/'audit.json')
    return d,first,last,features,train_i,test_i,folds

def one_candidate(family, params, X, Y, folds, candidate, checkpoint_dir):
    start=time.time(); oof=np.full_like(Y,np.nan); rows=[]; warning_messages=[]
    failure=None
    try:
        for fold,(ti,vi) in enumerate(folds):
            independent=family.startswith('single_') or family=='ridge'
            spec={'mode':'independent','params':[params]*3} if independent else {'mode':'joint','params':params}
            with warnings.catch_warnings(record=True) as seen, threadpool_limits(limits=1):
                warnings.simplefilter('always')
                model=fit_selected(family,spec,X[ti],Y[ti]); pred=predict(model,X[vi])
            warning_messages.extend(str(w.message) for w in seen)
            oof[vi]=pred
            rmse=np.sqrt(np.mean((pred-Y[vi])**2,axis=0)); normalized=rmse/Y[ti].std(axis=0)
            for j,t in enumerate(TARGETS):
                rows.append({'family':family,'candidate':candidate,'fold':fold,'target':t,'rmse':rmse[j],'normalized_rmse':normalized[j],
                    'pearson_r':finite_or_none(stats.pearsonr(Y[vi,j],pred[:,j]).statistic) if np.ptp(pred[:,j])>1e-14 else None})
    except Exception:
        failure=traceback.format_exc()
    record={'family':family,'candidate':candidate,'params':params,'seconds':time.time()-start,'warnings':sorted(set(warning_messages)),
        'rows':rows,'status':'failed' if failure else 'success','failure':failure}
    dump(record,Path(checkpoint_dir)/f'{family}_{candidate}.json')
    np.save(Path(checkpoint_dir)/f'{family}_{candidate}_oof.npy',oof)
    return dict(record,oof=oof)

def fit_selected(family, spec, X, Y):
    if spec['mode']=='independent':
        fitted=[]
        for j,params in enumerate(spec['params']):
            model=estimator(family,params,single_target=True); model.fit(X,Y[:,j]); fitted.append(model)
        return fitted
    model=estimator(family,spec['params']); model.fit(X,Y); return model

def predict(model,X):
    return np.column_stack([m.predict(X) for m in model]) if isinstance(model,list) else model.predict(X)

def select_models(X,Y,folds,out):
    candidates=[]; meta=[]
    for family,grid in CONFIG['grids'].items():
        for i,params in enumerate(ParameterGrid(grid)):
            candidates.append((family,params,i))
    assert len(candidates)==42
    checkpoint_dir=out/'candidate_checkpoints'; checkpoint_dir.mkdir(exist_ok=True)
    all_results=joblib.Parallel(n_jobs=CONFIG['parallel_jobs'],verbose=10)(joblib.delayed(one_candidate)(f,p,X,Y,folds,i,checkpoint_dir) for f,p,i in candidates)
    score_rows=[]; specs={}; family_rows=[]; oof_selected={}
    for r in all_results:
        np.save(out/'cv_predictions'/f"{r['family']}_{r['candidate']}.npy",r['oof'])
        if r['status']=='success': score_rows.extend(r['rows'])
        meta.append({k:v for k,v in r.items() if k not in ['rows','oof']})
    scores=pd.DataFrame(score_rows); scores.to_csv(out/'cv_fold_scores.csv',index=False)
    dump(meta,out/'experiments.json')
    for family in CONFIG['grids']:
        group=[r for r in all_results if r['family']==family and r['status']=='success']
        if not group: raise RuntimeError(f'No valid candidates for {family}; inspect candidate_checkpoints')
        means=scores[scores.family==family].groupby(['candidate','target'],sort=True).normalized_rmse.mean().unstack().reindex(columns=TARGETS)
        by_id={r['candidate']:r for r in group}
        independent=family.startswith('single_') or family=='ridge'
        if independent:
            ids=[int(means[t].idxmin()) for t in TARGETS]
            specs[family]={'mode':'independent','candidate_ids':ids,'params':[by_id[k]['params'] for k in ids]}
            pred=np.column_stack([by_id[k]['oof'][:,j] for j,k in enumerate(ids)])
            score=float(np.mean([means.loc[k,t] for k,t in zip(ids,TARGETS)]))
        else:
            k=int(means.mean(axis=1).idxmin()); specs[family]={'mode':'joint','candidate_id':k,'params':by_id[k]['params']}
            pred=by_id[k]['oof']; score=float(means.loc[k].mean())
        oof_selected[family]=pred
        np.save(out/'cv_predictions'/f'{family}_selected.npy',pred)
        family_rows.append({'family':family,'macro_normalized_rmse':score})
    ranks=pd.DataFrame(family_rows).sort_values('macro_normalized_rmse',kind='stable')
    ranks.to_csv(out/'cv_model_ranking.csv',index=False)
    ordered=ranks.family.tolist()
    selections={'winner':ordered[0], 'best_shared':next(f for f in ordered if f in ['joint_rf','joint_et','multitask_en']),
        'best_independent_ensemble':next(f for f in ordered if f.startswith('single_')),
        'best_tree':next(f for f in ordered if f.endswith('_rf') or f.endswith('_et')),
        'models':specs,'selection_basis':'Training-only 5-fold CV; holdout not evaluated before this file is saved.',
        'protocol_sha256':sha(ROOT/'docs/analysis_plan.md'),'config_sha256':sha(ROOT/'configs/analysis.json'),
        'input_sha256':sha(ROOT/'data.csv'),'script_sha256':sha(__file__),
        'partition_sha256':sha(out/'partition.csv'),'cv_row_order_sha256':sha(out/'cv_row_order.csv')}
    dump(selections,out/'selection_locked.json')
    return selections

def metric_rows(y,p,family,scenario,rng):
    rows=[]; B=CONFIG['bootstrap_replicates']; n=len(y)
    indices=rng.integers(0,n,size=(B,n))
    for j,t in enumerate(TARGETS):
        a,b=y[:,j],p[:,j]; constant=np.ptp(b)<1e-14
        r,pval=(np.nan,np.nan) if constant else stats.pearsonr(a,b)
        if constant: lo,hi=np.nan,np.nan
        else:
            z=np.arctanh(np.clip(r,-.999999999,.999999999)); dz=stats.norm.ppf(.975)/np.sqrt(n-3); lo,hi=np.tanh([z-dz,z+dz])
        sq=(a-b)**2; rmses=np.sqrt(sq[indices].mean(axis=1))
        rows.append({'scenario':scenario,'family':family,'target':t,'n':n,'pearson_r':r,'pearson_ci_low':lo,'pearson_ci_high':hi,
            'pearson_p':pval,'rmse':np.sqrt(sq.mean()),'rmse_ci_low':np.quantile(rmses,.025),'rmse_ci_high':np.quantile(rmses,.975),
            'r_squared':1-sq.sum()/((a-a.mean())**2).sum(), 'spearman_r':np.nan if constant else stats.spearmanr(a,b).statistic})
    return rows

def comparisons(y,preds,selection,out):
    rng=np.random.default_rng(SEED+90); rows=[]; n=len(y)
    pairs=[('winner_vs_mean',selection['winner'],'mean'),('shared_vs_independent',selection['best_shared'],selection['best_independent_ensemble'])]
    indices=rng.integers(0,n,size=(CONFIG['bootstrap_replicates'],n))
    signs=rng.choice([-1,1],size=(CONFIG['permutation_replicates'],n))
    for label,a,b in pairs:
        for j,t in enumerate(TARGETS):
            ea=(preds[a][:,j]-y[:,j])**2; eb=(preds[b][:,j]-y[:,j])**2
            deltas=np.sqrt(ea[indices].mean(axis=1))-np.sqrt(eb[indices].mean(axis=1))
            diff=ea-eb; null=(signs*diff).mean(axis=1)
            p=(1+np.sum(np.abs(null)>=abs(diff.mean())))/(1+len(null))
            rows.append({'comparison':label,'model_a':a,'model_b':b,'target':t,'n':n,
                'delta_rmse_a_minus_b':np.sqrt(ea.mean())-np.sqrt(eb.mean()),'ci_low':np.quantile(deltas,.025),'ci_high':np.quantile(deltas,.975),
                'delta_mse':diff.mean(),'swap_p':p})
    df=pd.DataFrame(rows); df['holm_p']=multipletests(df.swap_p,method='holm')[1]; df.to_csv(out/'paired_comparisons.csv',index=False)

def repeated_cv(selection,X,Y,out):
    rows=[]
    # Frozen selected configurations; not a second tuning round or nested validation.
    families=list(dict.fromkeys([selection['winner'],selection['best_shared'],selection['best_independent_ensemble'],'mean']))
    for repeat in range(3):
        folds=KFold(n_splits=5,shuffle=True,random_state=CONFIG['repeated_cv_seeds'][repeat])
        for fold,(ti,vi) in enumerate(folds.split(X)):
            for family in families:
                model=fit_selected(family,selection['models'][family],X[ti],Y[ti]); p=predict(model,X[vi])
                for j,t in enumerate(TARGETS):
                    rows.append({'repeat':repeat,'fold':fold,'family':family,'target':t,'n':len(vi),
                        'rmse':np.sqrt(np.mean((p[:,j]-Y[vi,j])**2)),
                        'normalized_rmse':np.sqrt(np.mean((p[:,j]-Y[vi,j])**2))/Y[ti,j].std(),
                        'spearman_r':np.nan if np.ptp(p[:,j])<1e-14 else stats.spearmanr(Y[vi,j],p[:,j]).statistic})
    pd.DataFrame(rows).to_csv(out/'repeated_cv_frozen.csv',index=False)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--out',default='results/primary'); parser.add_argument('--phase',choices=['audit','select','evaluate','all'],default='all'); parser.add_argument('--skip-robustness',action='store_true'); args=parser.parse_args()
    out=ROOT/args.out; out.mkdir(parents=True,exist_ok=True)
    if args.phase=='evaluate':
        locked=json.loads((out/'selection_locked.json').read_text())
        assert locked['input_sha256']==sha(ROOT/'data.csv'),'Input changed since selection'
        assert locked['script_sha256']==sha(__file__),'Analysis code changed since selection'
        assert locked['partition_sha256']==sha(out/'partition.csv'),'Saved partition altered'
        assert locked['cv_row_order_sha256']==sha(out/'cv_row_order.csv'),'Saved CV row order altered'
    for p in ['cv_predictions','models','predictions']: (out/p).mkdir(exist_ok=True)
    t0=time.time(); raw,first,last,features,ti,vi,folds=raw_audit(out)
    if args.phase=='audit': return
    X=first[features].to_numpy(float); Y=first[TARGETS].to_numpy(float)
    if args.phase in ['select','all']:
        selection=select_models(X[ti],Y[ti],folds,out)
        print('TRAINING SELECTION LOCKED',json.dumps({k:v for k,v in selection.items() if k!='models'}),flush=True)
        if not args.skip_robustness: repeated_cv(selection,X[ti],Y[ti],out)
        if args.phase=='select': return
    selection=json.loads((out/'selection_locked.json').read_text())
    assert selection['config_sha256']==sha(ROOT/'configs/analysis.json')
    assert selection['protocol_sha256']==sha(ROOT/'docs/analysis_plan.md')
    assert selection['input_sha256']==sha(ROOT/'data.csv')
    assert selection['partition_sha256']==sha(out/'partition.csv')
    assert selection['cv_row_order_sha256']==sha(out/'cv_row_order.csv')
    rows=[]; preds={}; rng=np.random.default_rng(SEED+60)
    singleton=raw.UID.value_counts().loc[lambda v:v==1].index
    ambiguous=['ind','A','B']+[f'C{i}' for i in range(1,11)]+['D']
    scenarios=[('primary',first,features),('latest_record',last,features),('singleton_uids',first[first.UID.isin(singleton)],features),('restricted_features',first,[f for f in features if f not in ambiguous])]
    if args.skip_robustness: scenarios=scenarios[:1]
    train_uids=set(first.iloc[ti].UID)
    for scenario,data,cols in scenarios:
        tr=data.UID.isin(train_uids).to_numpy(); Xt=data.loc[tr,cols].to_numpy(float); Yt=data.loc[tr,TARGETS].to_numpy(float)
        Xv=data.loc[~tr,cols].to_numpy(float); Yv=data.loc[~tr,TARGETS].to_numpy(float)
        for family,spec in selection['models'].items():
            print('fit and evaluate',scenario,family,len(Xt),len(Xv),flush=True)
            with threadpool_limits(limits=1): model=fit_selected(family,spec,Xt,Yt); p=predict(model,Xv)
            frame=data.loc[~tr,['UID','source_row']+TARGETS].copy()
            for j,t in enumerate(TARGETS): frame[f'pred_{t}']=p[:,j]
            frame.to_csv(out/'predictions'/f'{scenario}_{family}.csv',index=False,float_format='%.17g')
            rows.extend(metric_rows(Yv,p,family,scenario,rng))
            if scenario=='primary':
                preds[family]=p; joblib.dump(model,out/'models'/f'{family}.joblib',compress=3)
    metrics=pd.DataFrame(rows); metrics['winner_pearson_holm_p']=np.nan
    mask=(metrics.scenario=='primary')&(metrics.family==selection['winner']); pvals=metrics.loc[mask,'pearson_p'].to_numpy()
    if np.isfinite(pvals).all(): metrics.loc[mask,'winner_pearson_holm_p']=multipletests(pvals,method='holm')[1]
    metrics.to_csv(out/'metrics.csv',index=False,float_format='%.17g')
    # Data are in ascending UID order in the saved predictions and evaluation above.
    y_eval=first.loc[~first.UID.isin(train_uids),TARGETS].to_numpy(float)
    comparisons(y_eval,preds,selection,out)
    dump({'seed':SEED,'versions':{'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__,'joblib':joblib.__version__},
        'platform':platform.platform(),'input_sha256':sha(ROOT/'data.csv'),'script_sha256':sha(__file__),'protocol_sha256':sha(ROOT/'docs/analysis_plan.md'),
        'config_sha256':sha(ROOT/'configs/analysis.json'),'command':sys.argv,'runtime_seconds':time.time()-t0,
        'test_evaluation_after_selection':True},out/'run_manifest.json')
    print('COMPLETE',str(out),time.time()-t0,flush=True)

if __name__=='__main__': main()
