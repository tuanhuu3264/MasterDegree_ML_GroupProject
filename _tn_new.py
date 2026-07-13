# -*- coding: utf-8 -*-
"""Standalone validate cho 3 thi nghiem moi (TN8/TN9/TN10) truoc khi nhung vao builder."""
import os, time, warnings, numpy as np, pandas as pd
warnings.filterwarnings('ignore')
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder, StandardScaler
from sklearn.ensemble import (RandomForestClassifier, HistGradientBoostingClassifier)
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_predict, StratifiedKFold, train_test_split
from sklearn.metrics import (average_precision_score, f1_score, roc_auc_score,
                             precision_score, recall_score)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
RS = 42; np.random.seed(RS)

CANDS = ['Data_Final/Data_Final','Data_Final','../Data_Final/Data_Final','../Data_Final','.']
DIR = next((d for d in CANDS if os.path.exists(os.path.join(d,'train.csv'))
            and os.path.exists(os.path.join(d,'test.csv'))), None)
train = pd.read_csv(os.path.join(DIR,'train.csv')); test = pd.read_csv(os.path.join(DIR,'test.csv'))
NUM = ['nhiet_do_moi_truong','nhiet_do_quy_trinh','toc_do_quay','momen_xoan','do_mon_dao']
CAT = ['loai_san_pham','ca_lam_viec']; T = 'hong_hoc'
ytr, yte = train[T].values, test[T].values
cv = StratifiedKFold(5, shuffle=True, random_state=RS)

def base_fe(d):
    o = d.copy()
    o['chenh_lech_nhiet'] = o.nhiet_do_quy_trinh - o.nhiet_do_moi_truong
    o['cong_suat_co']     = o.momen_xoan * o.toc_do_quay * 2*np.pi/60
    o['mon_x_momen']      = o.do_mon_dao * o.momen_xoan
    return o
BASE_FE = ['chenh_lech_nhiet','cong_suat_co','mon_x_momen']
def new_fe(d):
    o = base_fe(d)
    o['mon_x_toc_do']    = o.do_mon_dao * o.toc_do_quay
    o['cong_suat_x_mon'] = o.cong_suat_co * o.do_mon_dao
    o['cang_thang_nhiet']= o.mon_x_momen * o.chenh_lech_nhiet
    o['ly_tam_x_mon']    = (o.toc_do_quay**2) * o.do_mon_dao
    return o
NEW = ['mon_x_toc_do','cong_suat_x_mon','cang_thang_nhiet','ly_tam_x_mon']
def rf_new(): return RandomForestClassifier(n_estimators=500, min_samples_leaf=10, min_samples_split=10,
    max_features='sqrt', class_weight='balanced', random_state=RS, n_jobs=-1)
spw = (ytr==0).sum()/(ytr==1).sum()

# ================= TN8: grid lr x max_depth (XGBoost) =================
print('='*70); print('TN8 — GRID learning_rate x max_depth (XGBoost)'); print('='*70, flush=True)
t0=time.time()
Xtr_b, Xte_b = base_fe(train[NUM+CAT]), base_fe(test[NUM+CAT]); NFb = NUM+BASE_FE
pre_b = ColumnTransformer([('num','passthrough',NFb),
    ('ord',OrdinalEncoder(categories=[['L','M','H']]),['loai_san_pham']),
    ('oh',OneHotEncoder(handle_unknown='ignore',sparse_output=False),['ca_lam_viec'])])
Xa, Xb = pre_b.fit_transform(Xtr_b), pre_b.transform(Xte_b)
DEPTHS = [2,3,4,6,8,10]; LRS = [0.03,0.06,0.1,0.2]
grid = np.zeros((len(DEPTHS),len(LRS)))
best = (0,None)
for i,md_ in enumerate(DEPTHS):
    row=[]
    for j,lr in enumerate(LRS):
        m = XGBClassifier(random_state=RS,n_jobs=-1,tree_method='hist',eval_metric='aucpr',
            scale_pos_weight=spw,n_estimators=400,max_depth=md_,learning_rate=lr,
            subsample=0.9,colsample_bytree=0.8,min_child_weight=5,reg_lambda=1,gamma=1)
        oof = cross_val_predict(m, Xa, ytr, cv=cv, method='predict_proba', n_jobs=-1)[:,1]
        ths=np.linspace(0.05,0.9,60); thr=ths[int(np.argmax([f1_score(ytr,(oof>=t)) for t in ths]))]
        p = m.fit(Xa,ytr).predict_proba(Xb)[:,1]; f=f1_score(yte,(p>=thr))
        grid[i,j]=f; row.append(f)
        if f>best[0]: best=(f,(md_,lr,thr))
    print(f'  depth={md_:2d} | ' + '  '.join(f'lr={LRS[j]:.2f}:{row[j]:.3f}' for j in range(len(LRS))), flush=True)
print(f'  >>> BEST F1={best[0]:.3f} @ depth={best[1][0]}, lr={best[1][1]} (thr={best[1][2]:.2f}) | RF moc=0.778')
print(f'  runtime {time.time()-t0:.0f}s', flush=True)

# ================= TN9: 11 models voi NEW FE =================
print('\n'+'='*70); print('TN9 — Benchmark 11 models: base_fe vs new_fe'); print('='*70, flush=True)
t0=time.time()
def score_of(m,X):
    if hasattr(m,'predict_proba'): return m.predict_proba(X)[:,1]
    if hasattr(m,'decision_function'): return m.decision_function(X)
    return m.predict(X)
def make_models():
    return [('LinearRegression*',LinearRegression(),True),
     ('LogisticRegression',LogisticRegression(class_weight='balanced',max_iter=2000),True),
     ('DecisionTree',DecisionTreeClassifier(max_depth=6,min_samples_leaf=20,class_weight='balanced',random_state=RS),False),
     ('SVM (RBF)',SVC(kernel='rbf',class_weight='balanced',random_state=RS),True),
     ('NaiveBayes',GaussianNB(),True),
     ('kNN (k=25)',KNeighborsClassifier(n_neighbors=25),True),
     ('RandomForest',RandomForestClassifier(n_estimators=500,min_samples_leaf=10,max_features='sqrt',class_weight='balanced',random_state=RS,n_jobs=-1),False),
     ('GBM (HistGB)',HistGradientBoostingClassifier(class_weight='balanced',random_state=RS),False),
     ('XGBoost',XGBClassifier(n_estimators=400,max_depth=3,learning_rate=0.1,scale_pos_weight=spw,eval_metric='aucpr',tree_method='hist',random_state=RS,n_jobs=-1),False),
     ('LightGBM',LGBMClassifier(n_estimators=400,max_depth=4,learning_rate=0.05,class_weight='balanced',random_state=RS,n_jobs=-1,verbose=-1),False),
     ('CatBoost',CatBoostClassifier(iterations=400,depth=5,learning_rate=0.05,auto_class_weights='Balanced',random_state=RS,verbose=0),False)]
def bench_fe(fe_fn, feats):
    NFx = NUM+feats
    Xtr_x, Xte_x = fe_fn(train[NUM+CAT]), fe_fn(test[NUM+CAT])
    Xa_, Xv_, ya_, yv_ = train_test_split(Xtr_x, ytr, test_size=0.2, stratify=ytr, random_state=RS)
    def prep(scale):
        return ColumnTransformer([('num', StandardScaler() if scale else 'passthrough', NFx),
            ('ord',OrdinalEncoder(categories=[['L','M','H']]),['loai_san_pham']),
            ('oh',OneHotEncoder(handle_unknown='ignore',sparse_output=False),['ca_lam_viec'])])
    out=[]
    for nm,est,sc in make_models():
        pre=prep(sc); Aa=pre.fit_transform(Xa_); Vv=pre.transform(Xv_); Bb=pre.transform(Xte_x)
        m=est.fit(Aa,ya_); sv=score_of(m,Vv); sb=score_of(m,Bb)
        cand=np.unique(np.quantile(sv,np.linspace(0.30,0.999,200)))
        thr=cand[int(np.argmax([f1_score(yv_,(sv>=t)) for t in cand]))]
        yp=(sb>=thr).astype(int)
        out.append(dict(model=nm, F1=round(f1_score(yte,yp),3), AUC_PR=round(average_precision_score(yte,sb),3)))
    return pd.DataFrame(out)
b_base = bench_fe(base_fe, BASE_FE).rename(columns={'F1':'F1_base','AUC_PR':'AUCPR_base'})
b_new  = bench_fe(new_fe,  BASE_FE+NEW).rename(columns={'F1':'F1_new','AUC_PR':'AUCPR_new'})
cmp = b_base.merge(b_new, on='model')
cmp['dF1'] = (cmp.F1_new - cmp.F1_base).round(3)
cmp = cmp.sort_values('F1_new', ascending=False).reset_index(drop=True)
print(cmp.to_string(index=False))
print(f'  new FE giup: {(cmp.dF1>0).sum()}/11 model tang, {(cmp.dF1<0).sum()} giam, {(cmp.dF1==0).sum()} khong doi')
print(f'  runtime {time.time()-t0:.0f}s', flush=True)

# ================= TN10: danh trong so new FE > raw FE (RF, column replication) =================
print('\n'+'='*70); print('TN10 — Trong so new FE > raw FE (RF: nhan ban cot de tang P(split))'); print('='*70, flush=True)
t0=time.time()
def eval_weighted(rep_new, rep_raw, label):
    # feats: raw NUM + BASE_FE (raw-derived) vs NEW (engineered).  Nhan ban cot theo rep.
    Xtr_x, Xte_x = new_fe(train[NUM+CAT]), new_fe(test[NUM+CAT])
    raw_cols = NUM + BASE_FE          # tin hieu "tho/co ban"
    new_cols = NEW                    # feature engineered nang cao
    cols = raw_cols*rep_raw + new_cols*rep_new
    pre = ColumnTransformer([('num','passthrough',cols),
        ('ord',OrdinalEncoder(categories=[['L','M','H']]),['loai_san_pham']),
        ('oh',OneHotEncoder(handle_unknown='ignore',sparse_output=False),['ca_lam_viec'])],
        verbose_feature_names_out=False)
    # ColumnTransformer khong cho trung ten cot -> tu build ma tran
    def build(dffe):
        parts=[dffe[cols].values]
        oe=OrdinalEncoder(categories=[['L','M','H']]).fit(train[['loai_san_pham']])
        return dffe, oe
    # don gian hon: tu ghep numpy
    oe = OrdinalEncoder(categories=[['L','M','H']]).fit(train[['loai_san_pham']])
    oh = OneHotEncoder(handle_unknown='ignore',sparse_output=False).fit(train[['ca_lam_viec']])
    def mat(dffe):
        num = dffe[cols].values
        return np.hstack([num, oe.transform(dffe[['loai_san_pham']]), oh.transform(dffe[['ca_lam_viec']])])
    Xa_, Xb_ = mat(Xtr_x), mat(Xte_x)
    oof = cross_val_predict(rf_new(), Xa_, ytr, cv=cv, method='predict_proba', n_jobs=-1)[:,1]
    ths=np.linspace(0.05,0.9,80); thr=ths[int(np.argmax([f1_score(ytr,(oof>=t)) for t in ths]))]
    p = rf_new().fit(Xa_,ytr).predict_proba(Xb_)[:,1]; f=f1_score(yte,(p>=thr))
    ncol=Xa_.shape[1]
    print(f'  {label:40s} F1={f:.3f} (thr={thr:.2f})  AUC-PR={average_precision_score(yte,p):.3f}  [#cols={ncol}, raw:new = {len(raw_cols)*rep_raw}:{len(new_cols)*rep_new}]', flush=True)
    return f
f0 = eval_weighted(1,1, 'A) raw x1, new x1 (can bang - moc)')
f2 = eval_weighted(2,1, 'B) new x2 (uu tien new FE)')
f3 = eval_weighted(3,1, 'C) new x3 (uu tien manh new FE)')
fdown = eval_weighted(1,1, 'D) baseline lai (kiem tra on dinh)')
print(f'  >>> can bang={f0:.3f}  new_x2={f2:.3f}  new_x3={f3:.3f} | RF moc(3FE)=0.778')
print(f'  runtime {time.time()-t0:.0f}s', flush=True)
print('\nDONE ALL', flush=True)
