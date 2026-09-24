#!/usr/bin/env python3
"""Prespecified training TreeSHAP and held-out permutation diagnostics."""
import os
os.environ.setdefault('OMP_NUM_THREADS','1')
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import shap
from analyze import ROOT, CONFIG, SEED, TARGETS, predict, dump

def main():
    root=ROOT/'results/primary'; out=root/'interpretation'; out.mkdir(exist_ok=True)
    selection=json.loads((root/'selection_locked.json').read_text()); family=selection['best_tree']
    data=pd.read_csv(root/'cleaned_primary.csv',dtype={'UID':str})
    part=pd.read_csv(root/'partition.csv',dtype={'UID':str}).set_index('UID')
    features=json.loads((root/'audit.json').read_text())['features']
    tr=data.UID.map(part.partition).eq('train').to_numpy(); X=data.loc[tr,features].to_numpy(float); Xtest=data.loc[~tr,features].to_numpy(float)
    Ytest=data.loc[~tr,TARGETS].to_numpy(float)
    model=joblib.load(root/'models'/f'{family}.joblib')
    values=np.empty((len(X),len(features),3)); expected=np.empty((len(X),3))
    if isinstance(model,list):
        for j,m in enumerate(model):
            pipe=m.regressor_; xt=pipe[:-1].transform(X)
            explainer=shap.TreeExplainer(pipe[-1],feature_perturbation='tree_path_dependent',model_output='raw')
            sv=np.asarray(explainer.shap_values(xt,check_additivity=True))
            values[:,:,j]=sv*m.transformer_.scale_[0]
            expected[:,j]=np.asarray(explainer.expected_value).item()*m.transformer_.scale_[0]+m.transformer_.mean_[0]
    else:
        pipe=model.regressor_; xt=pipe[:-1].transform(X)
        explainer=shap.TreeExplainer(pipe[-1],feature_perturbation='tree_path_dependent',model_output='raw')
        sv=np.asarray(explainer.shap_values(xt,check_additivity=True))
        assert sv.shape==values.shape,sv.shape
        values=sv*model.transformer_.scale_[None,None,:]
        expected[:]=np.asarray(explainer.expected_value)*model.transformer_.scale_+model.transformer_.mean_
    err=np.max(np.abs(values.sum(axis=1)+expected-predict(model,X)))
    assert err<1e-7,err
    np.savez_compressed(out/'training_shap_values.npz',values=values,expected=expected,features=np.array(features),targets=np.array(TARGETS),UID=data.loc[tr,'UID'].to_numpy(dtype=str),X=X)
    rows=[]
    for j,t in enumerate(TARGETS):
        for i,f in enumerate(features):
            rows.append({'family':family,'target':t,'feature':f,'mean_abs_shap':np.abs(values[:,i,j]).mean(),
                'mean_shap':values[:,i,j].mean(),'feature_shap_spearman':pd.Series(X[:,i]).corr(pd.Series(values[:,i,j]),method='spearman')})
    ranks=pd.DataFrame(rows); ranks['rank']=ranks.groupby('target').mean_abs_shap.rank(ascending=False,method='first').astype(int)
    ranks.to_csv(out/'shap_ranking.csv',index=False)
    top=ranks[ranks['rank']<=CONFIG['interpretation_top_features_per_target']].feature.unique().tolist()
    # Top features are selected exclusively from training SHAP, never holdout importance.
    dump({'family':family,'training_n':len(X),'test_n':len(Xtest),'top_features':top,
        'selection':'Union of top 10 mean absolute training SHAP per target',
        'shap_version':shap.__version__,'perturbation':'tree_path_dependent',
        'max_additivity_error':err,'units':'stored CSV target units'},out/'interpretation_manifest.json')
    baseline=np.sqrt(np.mean((predict(model,Xtest)-Ytest)**2,axis=0)); rng=np.random.default_rng(SEED+120)
    records=[]
    for f in top:
        col=features.index(f)
        for rep in range(CONFIG['permutation_importance_repeats']):
            xp=Xtest.copy(); xp[:,col]=xp[rng.permutation(len(xp)),col]
            delta=np.sqrt(np.mean((predict(model,xp)-Ytest)**2,axis=0))-baseline
            for j,t in enumerate(TARGETS): records.append({'feature':f,'target':t,'repeat':rep,'delta_rmse':delta[j]})
    pd.DataFrame(records).to_csv(out/'permutation_importance_repeats.csv',index=False)
    pd.DataFrame(records).groupby(['target','feature']).delta_rmse.agg(['mean','std','min','max']).reset_index().to_csv(out/'permutation_importance_summary.csv',index=False)
    print('Interpretation complete',family,'additivity error',err,flush=True)

if __name__=='__main__': main()
