#!/usr/bin/env python3
"""Render locked results as scientific figures; never refit a model.

Use --figures-only to preserve separately maintained table exports. Figures have
editable SVG/PDF, 600-dpi PNG/TIFF, and grayscale variants. Existing numeric
figure-source CSVs are checked and preserved byte-for-byte.
"""
import argparse
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.colors import to_rgba_array
import numpy as np
import pandas as pd
from analyze import ROOT, TARGETS

NAMES={'SWB_nn':'Negative affect','SWB_pp':'Positive affect','SWB_avg':'Life satisfaction'}
MODELS={'mean':'Training mean','ridge':'Ridge','single_rf':'Independent RF','single_et':'Independent ET','single_hgb':'Independent HGB','joint_rf':'Shared RF','joint_et':'Shared ET','multitask_en':'Multitask elastic net'}
COLORS=['#2878A4','#16867C','#C87828']
INK,MUTED,GRID='#26323D','#63717A','#E5E9EC'
OPAQUE={'A','B','D'}|{f'C{i}' for i in range(1,11)}
BASE,FIG,TAB=ROOT/'results/primary',ROOT/'figures',ROOT/'tables'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'text.color':INK,
    'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'axes.edgecolor':'#A6AFB5',
    'axes.linewidth':.65,'axes.spines.top':False,'axes.spines.right':False,
    'axes.titlesize':9.5,'axes.titleweight':'bold','axes.labelsize':8.3,
    'xtick.labelsize':7.6,'ytick.labelsize':8.2,'xtick.major.size':3,'ytick.major.size':0,
    'xtick.major.width':.6,'ytick.major.width':.6,'axes.axisbelow':True,
    'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','hatch.linewidth':.5,
    'savefig.bbox':'tight','savefig.pad_inches':.08})

def save(fig,name,gray=False):
    destination=FIG/'grayscale' if gray else FIG
    destination.mkdir(parents=True,exist_ok=True)
    if gray:
        # Convert artist colors before vector/raster export; preserve geometry,
        # alpha, hatching and markers while making every RGB channel neutral.
        for artist in fig.findobj():
            for property_name in ['color','facecolor','edgecolor','markerfacecolor','markeredgecolor']:
                getter=getattr(artist,f'get_{property_name}',None)
                setter=getattr(artist,f'set_{property_name}',None)
                if getter is None or setter is None: continue
                try:
                    rgba=to_rgba_array(getter())
                    if not len(rgba): continue
                    luminance=rgba[:,:3]@np.array([.2126,.7152,.0722])
                    rgba[:,:3]=luminance[:,None]
                    setter(rgba[0] if len(rgba)==1 else rgba)
                except (ValueError,TypeError):
                    pass  # Matplotlib sentinel colors such as 'auto' inherit the line color.
    for ext in ['svg','pdf','png','tiff']:
        extra={'pil_kwargs':{'compression':'tiff_lzw'}} if ext=='tiff' else {}
        fig.savefig(destination/f'{name}.{ext}',dpi=600,facecolor='white',**extra)
    plt.close(fig)

def preserve_source(name,frame):
    path=FIG/name; frame=frame.reset_index(drop=True).copy()
    if 'UID' in frame: frame['UID']=frame.UID.astype(str)
    if path.exists():
        old=pd.read_csv(path,dtype={'UID':str})
        pd.testing.assert_frame_equal(old,frame,check_dtype=False,check_exact=False,rtol=1e-12,atol=1e-14)
    else: frame.to_csv(path,index=False)

def panel(ax,letter,title):
    ax.set_title(title,loc='left',pad=10)
    ax.text(-.10,1.045,letter,transform=ax.transAxes,fontsize=10.5,fontweight='bold',ha='right',va='bottom',color=INK)

def interval(ax,center,lower,upper,y,color,marker='o',filled=True,strong=False):
    # Draw endpoints directly; percentile intervals need not enclose the estimate.
    ax.hlines(y,lower,upper,color=color,lw=1.5 if strong else 1.05,alpha=1 if strong else .74,zorder=2)
    ax.vlines([lower,upper],y-.07,y+.07,color=color,lw=.8,zorder=2)
    ax.scatter([center],[y],marker=marker,s=30 if strong else 21,facecolor=color if filled else 'white',edgecolor=color,linewidth=.9,zorder=3)

def flow(audit,gray):
    accent='#454545' if gray else COLORS[0]
    fig,ax=plt.subplots(figsize=(7.05,4.0));ax.set(xlim=(0,10),ylim=(0,6.7));ax.axis('off')
    def box(x,y,w,h,title,body,accent_line=False):
        ax.add_patch(Rectangle((x,y),w,h,facecolor='white',edgecolor='#B7C0C6',linewidth=.7))
        if accent_line: ax.plot([x,x+w],[y+h,y+h],color=accent,lw=1.8)
        ax.text(x+.20,y+h-.23,title,fontweight='bold',fontsize=9.5,va='top')
        ax.text(x+.20,y+.17,body,fontsize=8.15,color=MUTED,va='bottom',linespacing=1.35)
    def arrow(a,b):ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'-|>','color':'#909090' if gray else '#87949D','lw':.9,'mutation_scale':9,'shrinkA':1,'shrinkB':2})
    box(.35,5.53,9.30,.84,f"{audit['raw_rows']:,} supplied records",f"{audit['unique_participants']:,} participant IDs  ·  {audit['feature_count']} supplied text features",True)
    box(.35,4.28,9.30,.84,f"{audit['unique_participants']:,} participant records retained",f"Earliest stored survey per ID; exclude {audit['exact_duplicate_rows']} exact copies and {audit['repeated_uids']} later records")
    arrow((5,5.53),(5,5.14));ax.text(5,3.94,'Participant-level random split',ha='center',fontsize=8,color=MUTED)
    box(.35,2.61,4.35,.87,'Development sample',f"n = {audit['train_n']} participants  ·  90% allocation",True)
    box(5.30,2.61,4.35,.87,'Holdout sample',f"n = {audit['test_n']} participants  ·  10% allocation",True)
    arrow((3.05,4.28),(2.52,3.50));arrow((6.95,4.28),(7.48,3.50))
    box(.35,.93,4.35,1.23,'Five-fold model selection','42 configurations; fold-local scaling\nSelect by normalized RMSE; lock models')
    box(5.30,.93,4.35,1.23,'Locked final evaluation','Pearson r, RMSE and 95% intervals\nPaired comparisons and fixed sensitivities')
    arrow((2.52,2.61),(2.52,2.18));arrow((7.48,2.61),(7.48,2.18));arrow((4.73,1.56),(5.27,1.56))
    ax.text(.35,.36,'Aggregate features support retrospective prediction; raw posts, word-level counts, odd/even features\nand questionnaire items were unavailable.',ha='left',va='center',fontsize=7.6,color=MUTED,linespacing=1.4)
    fig.subplots_adjust(left=.02,right=.98,bottom=.015,top=.99);save(fig,'figure1_analysis_flow',gray)

def performance(primary,selection,ranking,colors,gray):
    order=ranking.family.tolist();labels=[MODELS[f]+(' *' if f==selection['winner'] else '') for f in order]
    fig,axes=plt.subplots(2,3,figsize=(7.30,6.10))
    rlow=min(-.1,np.floor(primary.pearson_ci_low.min()*10)/10);rhigh=max(.5,np.ceil(primary.pearson_ci_high.max()*10)/10)
    rmse_low=np.floor(primary.rmse_ci_low.min()*100)/100-.005;rmse_high=np.ceil(primary.rmse_ci_high.max()*100)/100+.005
    for j,t in enumerate(TARGETS):
        d=primary[primary.target==t].set_index('family').loc[order]
        for row,metric in enumerate(['pearson','rmse']):
            ax=axes[row,j];ax.set_ylim(len(order)-.55,-.55);ax.set_yticks(np.arange(len(order)),labels if j==0 else ['']*len(order))
            ax.spines['left'].set_visible(False);ax.tick_params(axis='y',pad=6);ax.grid(axis='x',color=GRID,linewidth=.6)
            for y,f in enumerate(order):
                selected,baseline=f==selection['winner'],f=='mean';color=INK if baseline else colors[j]
                value=d.loc[f,'pearson_r' if metric=='pearson' else 'rmse']
                if not np.isfinite(value):
                    ax.text((rlow+rhigh)/2,y,'Undefined: constant',color=MUTED,fontsize=6.9,ha='center',va='center');continue
                interval(ax,value,d.loc[f,f'{metric}_ci_low'],d.loc[f,f'{metric}_ci_high'],y,color,marker='D' if selected else ('s' if baseline else 'o'),filled=not baseline,strong=selected)
            if row==0:
                ax.axvline(0,color='#A0AAB1',ls=(0,(3,3)),lw=.8,zorder=1);ax.set_xlim(rlow-.015,rhigh+.015)
                ax.xaxis.set_major_locator(MultipleLocator(.2));ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'));ax.set_xlabel('Pearson r');panel(ax,'ABC'[j],NAMES[t])
            else:
                ax.axvline(d.loc['mean','rmse'],color='#A0AAB1',ls=(0,(3,3)),lw=.8,zorder=1);ax.set_xlim(rmse_low,rmse_high)
                ax.xaxis.set_major_locator(MultipleLocator(.04));ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'));ax.set_xlabel('RMSE (stored score units)');panel(ax,'DEF'[j],'')
            if j==0:
                for label,f in zip(ax.get_yticklabels(),order):
                    if f in {selection['winner'],'mean'}:label.set_fontweight('bold')
    fig.text(.245,.963,f"Holdout n = {int(primary.n.iloc[0])}  ·  All intervals are 95% CIs",fontsize=8.3,color=MUTED)
    handles=[Line2D([],[],marker='D',lw=0,color=INK,markersize=4.5,label='* Selected by development CV'),Line2D([],[],marker='s',lw=0,markerfacecolor='white',markeredgecolor=INK,markersize=4.5,label='Training-mean baseline')]
    fig.legend(handles=handles,loc='lower left',bbox_to_anchor=(.23,.005),frameon=False,ncol=2,fontsize=7.6,handletextpad=.5,columnspacing=1.8)
    fig.subplots_adjust(left=.245,right=.985,top=.887,bottom=.11,wspace=.20,hspace=.42);save(fig,'figure2_model_performance',gray)

def observed_predicted(primary,pred,selection,colors,gray):
    fig,axes=plt.subplots(1,3,figsize=(7.05,2.72))
    low=min(0,pred[TARGETS].min().min(),pred[[f'pred_{t}' for t in TARGETS]].min().min())-.025
    high=max(1,pred[TARGETS].max().max(),pred[[f'pred_{t}' for t in TARGETS]].max().max())+.025
    for j,t in enumerate(TARGETS):
        ax=axes[j];ax.scatter(pred[t],pred[f'pred_{t}'],s=17,alpha=.64,facecolors=colors[j],edgecolors='white',linewidths=.25,zorder=3)
        ax.plot([low,high],[low,high],color='#98A3AA',ls=(0,(4,3)),lw=.9,zorder=1)
        m=primary[(primary.family==selection['winner'])&(primary.target==t)].iloc[0]
        ax.text(.04,.96,f"r = {m.pearson_r:.3f}\nRMSE = {m.rmse:.3f}",transform=ax.transAxes,fontsize=7.8,va='top',linespacing=1.45)
        ax.set(xlim=(low,high),ylim=(low,high),aspect='equal',xlabel='Observed score',ylabel='Predicted score' if j==0 else '')
        ax.set_xticks([0,.5,1]);ax.set_yticks([0,.5,1]);ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'));ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        ax.grid(color=GRID,linewidth=.55);panel(ax,'ABC'[j],NAMES[t])
    fig.text(.065,.955,f"{MODELS[selection['winner']]} selected by development CV  ·  Holdout n = {len(pred)}  ·  Stored score units",fontsize=8,color=MUTED)
    fig.subplots_adjust(left=.065,right=.985,top=.80,bottom=.16,wspace=.27);save(fig,'figure3_observed_predicted',gray)

def attribution(ranks,manifest,colors,gray):
    fig,axes=plt.subplots(1,3,figsize=(7.05,3.80))
    top=[ranks[ranks.target==t].sort_values('mean_abs_shap',ascending=False).head(10).iloc[::-1] for t in TARGETS]
    xmax=max(r.mean_abs_shap.max() for r in top)*1.075
    for j,(t,d) in enumerate(zip(TARGETS,top)):
        ax=axes[j]
        for y,row in enumerate(d.itertuples()):
            unknown=row.feature in OPAQUE
            ax.barh(y,row.mean_abs_shap,height=.65,color='white' if unknown else colors[j],edgecolor=colors[j],linewidth=.65 if unknown else 0,hatch='////' if unknown else None)
        ax.set_yticks(np.arange(len(d)),[f+(' †' if f in OPAQUE else '') for f in d.feature]);ax.set(xlim=(0,xmax),ylim=(-.65,9.65))
        ax.spines['left'].set_visible(False);ax.grid(axis='x',color=GRID,linewidth=.55);ax.tick_params(axis='y',pad=4,labelsize=7.8)
        ax.xaxis.set_major_locator(MultipleLocator(.002));ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f'));panel(ax,'ABC'[j],NAMES[t])
    fig.text(.085,.966,f"{MODELS[manifest['family']]}  ·  Training n = {manifest['training_n']}  ·  Top 10 features per outcome",fontsize=8,color=MUTED)
    fig.supxlabel('Mean absolute SHAP value (stored score units)',x=.53,y=.095,fontsize=8.5)
    fig.text(.085,.025,'† Hatched bars mark unmapped dictionary codes; no psychological interpretation is assigned.',fontsize=7.5,color=MUTED)
    fig.subplots_adjust(left=.09,right=.985,top=.855,bottom=.20,wspace=.64);save(fig,'figure4_feature_attribution',gray)

def distributions(data,colors,gray):
    fig,axes=plt.subplots(1,3,figsize=(7.05,2.70));bins=np.arange(21,dtype=float)/20
    ymax=max(np.histogram(data[t],bins=bins)[0].max() for t in TARGETS)*1.12
    for j,t in enumerate(TARGETS):
        ax=axes[j];ax.hist(data[t],bins=bins,color=colors[j],edgecolor='white',linewidth=.45,alpha=.86)
        ax.set(xlim=(0,1),ylim=(0,ymax),ylabel='Participants' if j==0 else '');ax.set_xticks([0,.25,.5,.75,1]);ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax.grid(axis='y',color=GRID,linewidth=.55);panel(ax,'ABC'[j],NAMES[t])
    fig.text(.075,.955,f"Earliest record per participant  ·  n = {len(data):,}",fontsize=8,color=MUTED)
    fig.supxlabel('Questionnaire score (stored CSV units)',x=.53,y=.03,fontsize=8.5)
    fig.subplots_adjust(left=.075,right=.985,top=.80,bottom=.20,wspace=.26);save(fig,'figureS1_target_distributions',gray)

def sensitivity(metrics,selection,colors,gray):
    rows=metrics[metrics.family==selection['winner']];order=['primary','latest_record','singleton_uids','restricted_features'];names=['Earliest record','Latest record','Singleton IDs','Restricted features']
    counts=rows[rows.target==TARGETS[0]].set_index('scenario').n;labels=[f'{name} (n = {int(counts.loc[sc])})' for name,sc in zip(names,order)]
    low=np.floor(rows.rmse_ci_low.min()*100)/100-.005;high=np.ceil(rows.rmse_ci_high.max()*100)/100+.005
    fig,axes=plt.subplots(1,3,figsize=(7.05,2.75))
    for j,t in enumerate(TARGETS):
        ax=axes[j];d=rows[rows.target==t].set_index('scenario').loc[order]
        for y,sc in enumerate(order):
            r=d.loc[sc];interval(ax,r.rmse,r.rmse_ci_low,r.rmse_ci_high,y,colors[j],marker='D' if sc=='primary' else 'o',strong=sc=='primary')
        ax.set(xlim=(low,high),ylim=(3.5,-.5));ax.set_yticks(range(4),labels if j==0 else ['']*4);ax.spines['left'].set_visible(False)
        ax.grid(axis='x',color=GRID,linewidth=.55);ax.xaxis.set_major_locator(MultipleLocator(.04));ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'));panel(ax,'ABC'[j],NAMES[t])
    fig.text(.26,.955,f"{MODELS[selection['winner']]}  ·  Frozen hyperparameters  ·  95% CIs",fontsize=8,color=MUTED)
    fig.supxlabel('RMSE (stored score units)',x=.615,y=.035,fontsize=8.5)
    fig.subplots_adjust(left=.265,right=.985,top=.78,bottom=.21,wspace=.24);save(fig,'figureS2_sensitivity',gray)

def export_tables(metrics,primary,data,selection,ranks):
    TAB.mkdir(exist_ok=True);desc=[]
    for split in ['all','train','test']:
        d=data if split=='all' else data[data.partition==split]
        for t in TARGETS:desc.append({'sample':split,'target':t,'n':len(d),'mean':d[t].mean(),'sd':d[t].std(),'min':d[t].min(),'max':d[t].max()})
    pd.DataFrame(desc).to_csv(TAB/'table1_descriptives.csv',index=False);primary.to_csv(TAB/'table2_all_model_performance.csv',index=False)
    families=list(dict.fromkeys([selection['winner'],'mean',selection['best_shared'],selection['best_independent_ensemble']]))
    primary[primary.family.isin(families)].to_csv(TAB/'table2_main_performance.csv',index=False)
    pd.read_csv(BASE/'paired_comparisons.csv').to_csv(TAB/'table3_paired_comparisons.csv',index=False)
    metrics[metrics.scenario!='primary'].to_csv(TAB/'tableS2_sensitivity.csv',index=False)
    pd.read_csv(BASE/'cv_model_ranking.csv').to_csv(TAB/'tableS1_cv_ranking.csv',index=False)
    ranks.to_csv(TAB/'tableS3_shap_ranking.csv',index=False)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--figures-only',action='store_true',help='Do not overwrite table exports.');parser.add_argument('--no-grayscale',action='store_true');args=parser.parse_args()
    FIG.mkdir(exist_ok=True);metrics=pd.read_csv(BASE/'metrics.csv');primary=metrics[metrics.scenario=='primary']
    selection=json.loads((BASE/'selection_locked.json').read_text());audit=json.loads((BASE/'audit.json').read_text());manifest=json.loads((BASE/'interpretation/interpretation_manifest.json').read_text())
    ranking=pd.read_csv(BASE/'cv_model_ranking.csv');ranks=pd.read_csv(BASE/'interpretation/shap_ranking.csv')
    data=pd.read_csv(BASE/'cleaned_primary.csv',dtype={'UID':str}).copy();part=pd.read_csv(BASE/'partition.csv',dtype={'UID':str}).set_index('UID');data['partition']=data.UID.map(part.partition)
    pred=pd.read_csv(BASE/'predictions'/f"primary_{selection['winner']}.csv")
    if not args.figures_only:export_tables(metrics,primary,data,selection,ranks)
    sources={'figure1_source.csv':pd.DataFrame([{'stage':'input','n':audit['raw_rows']},{'stage':'participants','n':audit['unique_participants']},{'stage':'development','n':audit['train_n']},{'stage':'holdout','n':audit['test_n']}]),
        'figure2_source.csv':primary,'figure3_source.csv':pred,
        'figure4_source.csv':pd.concat([ranks[ranks.target==t].sort_values('mean_abs_shap',ascending=False).head(10).iloc[::-1] for t in TARGETS]),
        'figureS1_source.csv':data[['UID']+TARGETS],'figureS2_source.csv':metrics[metrics.family==selection['winner']]}
    for name,frame in sources.items():preserve_source(name,frame)
    for gray in [False]+([] if args.no_grayscale else [True]):
        colors=['#484848']*3 if gray else COLORS
        flow(audit,gray);performance(primary,selection,ranking,colors,gray);observed_predicted(primary,pred,selection,colors,gray)
        attribution(ranks,manifest,colors,gray);distributions(data,colors,gray);sensitivity(metrics,selection,colors,gray)
    print('Rendered six scientific figures; source CSVs preserved; grayscale variants:',not args.no_grayscale)

if __name__=='__main__':main()
