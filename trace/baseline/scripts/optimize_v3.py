#!/usr/bin/env python3
"""E4 exploratory, fixed-budget nested development CV; never overwrite E1-E3."""
import argparse
import json
import time
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from scipy import stats
from sklearn.compose import TransformedTargetRegressor
from sklearn.cross_decomposition import PLSRegression
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.model_selection import KFold
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from threadpoolctl import threadpool_limits
from analyze import ROOT, TARGETS, raw_audit, sha, dump, metric_rows, comparisons, estimator

SEED=20260924
SPECS=[{'id':'mean','kind':'mean'}, {'id':'original_rf','kind':'original_rf'}]
SPECS += [{'id':f'ridge_{mode}_{a}','kind':'ridge','log':mode=='log','alpha':a} for mode in ['raw','log'] for a in [10,100,1000]]
SPECS += [{'id':f'svr_{c}','kind':'svr','C':c} for c in [.1,1,10]]
SPECS += [{'id':f'hgb_{a}','kind':'hgb','l2':a} for a in [10,100]]
SPECS += [{'id':f'en_{a}_{l}','kind':'en','alpha':a,'l1':l} for a in [.01,.1] for l in [.1,.5]]
SPECS += [{'id':f'pls_{k}','kind':'pls','components':k} for k in [2,5,10]]
SPECS += [{'id':f'rf_{k}','kind':'rf','leaf':k} for k in [30,60]]
assert len(SPECS)==22

def model(s):
    kind=s['kind']
    if kind=='original_rf':
        return estimator('joint_rf',{'min_samples_leaf':15,'max_features':1.0})
    if kind=='mean':m=DummyRegressor()
    elif kind=='ridge':m=Ridge(alpha=s['alpha'])
    elif kind=='svr':
        from sklearn.svm import SVR
        m=MultiOutputRegressor(SVR(C=s['C'],epsilon=.1,gamma='scale'))
    elif kind=='hgb':m=MultiOutputRegressor(HistGradientBoostingRegressor(max_leaf_nodes=7,max_iter=100,learning_rate=.05,l2_regularization=s['l2'],early_stopping=False,random_state=SEED))
    elif kind=='en':m=MultiOutputRegressor(ElasticNet(alpha=s['alpha'],l1_ratio=s['l1'],max_iter=10000,tol=1e-6,random_state=SEED))
    elif kind=='rf':m=MultiOutputRegressor(RandomForestRegressor(n_estimators=256,min_samples_leaf=s['leaf'],max_features=.5,n_jobs=1,random_state=SEED))
    elif kind=='pls':return make_pipeline(SimpleImputer(strategy='median'),PLSRegression(n_components=s['components'],scale=True,max_iter=1000))
    else:raise ValueError(kind)
    steps=[SimpleImputer(strategy='median')]
    if s.get('log'):steps.append(FunctionTransformer(np.log1p,validate=True))
    steps += [StandardScaler(),m]
    return TransformedTargetRegressor(regressor=make_pipeline(*steps),transformer=StandardScaler())

def cv_candidate(s,X,Y,folds,folder):
    p=folder/(s['id']+'.json'); predpath=folder/(s['id']+'.npy')
    if p.exists():return json.loads(p.read_text())
    t=time.time();oof=np.full_like(Y,np.nan);rows=[];warn=[]
    try:
        for k,(ti,vi) in enumerate(folds):
            with warnings.catch_warnings(record=True) as w,threadpool_limits(limits=1):
                m=model(s);m.fit(X[ti],Y[ti]);pr=m.predict(X[vi])
            warn += [str(v.message) for v in w];oof[vi]=pr
            normalized=np.sqrt(np.mean((pr-Y[vi])**2,axis=0))/Y[ti].std(axis=0)
            rows.append({'fold':k,'normalized_rmse':normalized.tolist(),'macro':float(normalized.mean())})
        result={'spec':s,'status':'success','score':float(np.mean([r['macro'] for r in rows])),'folds':rows,'warnings':sorted(set(warn)),'seconds':time.time()-t}
    except Exception as e:result={'spec':s,'status':'failed','error':repr(e),'seconds':time.time()-t}
    np.save(predpath,oof);dump(result,p);return result

def select(X,Y,seed,folder):
    folder.mkdir(parents=True,exist_ok=True)
    folds=list(KFold(5,shuffle=True,random_state=seed).split(X))
    records=joblib.Parallel(n_jobs=4)(joblib.delayed(cv_candidate)(s,X,Y,folds,folder) for s in SPECS)
    good=[r for r in records if r['status']=='success']; winner=min(good,key=lambda r:r['score'])
    dump({'records':records,'winner':winner},folder/'selection.json')
    return winner

def datasets(out):
    rawdir=out/'raw_audit';rawdir.mkdir(parents=True,exist_ok=True)
    _,first,_,features,ti,vi,_=raw_audit(rawdir)
    assert sha(rawdir/'partition.csv')==sha(ROOT/'results/primary/partition.csv')
    X=first[features].to_numpy(float);Y=first[TARGETS].to_numpy(float)
    return first,X,Y,ti,vi

def run(out):
    out.mkdir(parents=True,exist_ok=False)
    dump({'specs':SPECS,'protocol_sha256':sha(ROOT/'docs/exploratory_plan_v3.md'),'script_sha256':sha(__file__),'input_sha256':sha(ROOT/'data.csv'),'seed':SEED,'status':'locked-before-new-candidates'},out/'plan_locked.json')
    first,X,Y,ti,vi=datasets(out);Xt,Yt=X[ti],Y[ti]
    pd.DataFrame({'UID':first.iloc[ti].UID.to_numpy(),'oof_row':np.arange(len(ti))}).to_csv(out/'development_order.csv',index=False)
    preds={k:np.empty_like(Yt) for k in ['selected','original_rf','mean']};rows=[]
    for k,(a,b) in enumerate(KFold(5,shuffle=True,random_state=SEED).split(Xt)):
        selected=select(Xt[a],Yt[a],SEED+k+1,out/f'outer_{k}/inner')
        print('outer',k,'selected',selected['spec']['id'],flush=True)
        for name,spec in [('selected',selected['spec']),('original_rf',SPECS[1]),('mean',SPECS[0])]:
            with threadpool_limits(limits=1):m=model(spec);m.fit(Xt[a],Yt[a]);p=m.predict(Xt[b])
            preds[name][b]=p
            for j,target in enumerate(TARGETS):
                rmse=np.sqrt(np.mean((p[:,j]-Yt[b,j])**2))
                rows.append({'outer_fold':k,'procedure':name,'target':target,'candidate':spec['id'],'n':len(b),'rmse':rmse,'normalized_rmse':rmse/Yt[a,j].std(),'r':None if np.ptp(p[:,j])<1e-14 else stats.pearsonr(p[:,j],Yt[b,j]).statistic})
        pd.DataFrame({'oof_row':b,'UID':first.iloc[ti[b]].UID.to_numpy()}).to_csv(out/f'outer_{k}/validation_ids.csv',index=False)
    for name,p in preds.items():np.save(out/f'nested_{name}.npy',p)
    frame=pd.DataFrame(rows);frame.to_csv(out/'nested_fold_metrics.csv',index=False)
    summary=frame.groupby('procedure').normalized_rmse.mean().to_dict()
    summary['relative_improvement_vs_original']=1-summary['selected']/summary['original_rf'];dump(summary,out/'nested_summary.json')
    winner=select(Xt,Yt,SEED,out/'full_development')
    locked={'winner':winner['spec'],'cv_score':winner['score'],'nested_summary':summary,'exploratory':True,'test_previously_seen':True,'input_sha256':sha(ROOT/'data.csv'),'script_sha256':sha(__file__),'protocol_sha256':sha(ROOT/'docs/exploratory_plan_v3.md')}
    dump(locked,out/'selection_locked.json');print('final selection locked',winner['spec'],flush=True)
    evaluate(out,first,X,Y,ti,vi,locked)

def evaluate(out,first,X,Y,ti,vi,locked):
    # Ascending participant ID order matches primary predictions.
    mask=~first.UID.isin(set(first.iloc[ti].UID));xi=X[mask];yi=Y[mask]
    with threadpool_limits(limits=1):m=model(locked['winner']);m.fit(X[ti],Y[ti]);p=m.predict(xi)
    joblib.dump(m,out/'selected_model.joblib',compress=3)
    f=first.loc[mask,['UID','source_row']+TARGETS].copy()
    for j,t in enumerate(TARGETS):f['pred_'+t]=p[:,j]
    f.to_csv(out/'holdout_predictions.csv',index=False,float_format='%.17g')
    pd.DataFrame(metric_rows(yi,p,'exploratory_selected','previously_seen_holdout',np.random.default_rng(SEED+100))).to_csv(out/'holdout_metrics.csv',index=False,float_format='%.17g')
    old={}
    for key,family in [('original_rf','joint_rf'),('mean','mean')]:
        z=pd.read_csv(ROOT/f'results/primary/predictions/primary_{family}.csv',dtype={'UID':str})
        assert z.UID.tolist()==f.UID.tolist();np.testing.assert_allclose(z[TARGETS],yi,rtol=0,atol=1e-15)
        old[key]=z[['pred_'+t for t in TARGETS]].to_numpy()
    comparisons(yi,dict(old,selected=p),{'winner':'selected','best_shared':'selected','best_independent_ensemble':'original_rf'},out)
    dump({'input_sha256':sha(ROOT/'data.csv'),'script_sha256':sha(__file__),'predictions_sha256':sha(out/'holdout_predictions.csv'),'exploratory':True,'holdout_n':len(yi),'development_n':len(ti)},out/'run_manifest.json')
    print('completed',out,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='results/exploratory_v3');p.add_argument('--refit',action='store_true');args=p.parse_args();out=ROOT/args.out
    if args.refit:
        out.mkdir(parents=True,exist_ok=False);first,X,Y,ti,vi=datasets(out)
        locked=json.loads((ROOT/'results/exploratory_v3/selection_locked.json').read_text())
        assert locked['script_sha256']==sha(__file__)
        evaluate(out,first,X,Y,ti,vi,locked)
    else:run(out)
