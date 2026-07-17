import os, warnings, numpy as np, pandas as pd
warnings.filterwarnings('ignore')
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder
from sklearn.model_selection import cross_val_predict, StratifiedKFold, RandomizedSearchCV
from sklearn.metrics import average_precision_score, f1_score
from scipy.stats import loguniform, randint
from xgboost import XGBClassifier
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
def full_fe(d):
    o = new_fe(d)
    o['nhiet_x_tocdo']     = o.chenh_lech_nhiet * o.toc_do_quay
    o['ty_le_nhiet_do']    = o.nhiet_do_quy_trinh / o.nhiet_do_moi_truong
    o['ty_le_momen_tocdo'] = o.momen_xoan / o.toc_do_quay
    return o
WEAK = ['nhiet_x_tocdo','ty_le_nhiet_do','ty_le_momen_tocdo']
ALL_NEW = NEW + WEAK
spw = (ytr==0).sum()/(ytr==1).sum()

def xgb_push(feats, label, n_iter=50):
    Xtr, Xte = full_fe(train[NUM+CAT]), full_fe(test[NUM+CAT]); NF = NUM+feats
    pre = ColumnTransformer([('num','passthrough',NF),
        ('ord',OrdinalEncoder(categories=[['L','M','H']]),['loai_san_pham']),
        ('oh',OneHotEncoder(handle_unknown='ignore',sparse_output=False),['ca_lam_viec'])])
    Xa, Xb = pre.fit_transform(Xtr), pre.transform(Xte)
    dist = {'n_estimators':randint(600,1600),'max_depth':randint(6,20),'learning_rate':loguniform(3e-3,1e-1),
            'subsample':[0.7,0.85,1.0],'colsample_bytree':[0.6,0.8,1.0],'reg_lambda':[1,5,10],
            'reg_alpha':[0,0.5,1],'min_child_weight':[1,3,5],'gamma':[0,1,3]}
    s = RandomizedSearchCV(XGBClassifier(random_state=RS,n_jobs=-1,tree_method='hist',eval_metric='aucpr',scale_pos_weight=spw),
        dist, n_iter=n_iter, scoring='average_precision', cv=cv, n_jobs=-1, random_state=RS, refit=True).fit(Xa, ytr)
    oof = cross_val_predict(s.best_estimator_, Xa, ytr, cv=cv, method='predict_proba', n_jobs=-1)[:,1]
    ths=np.linspace(0.05,0.9,80); thr=ths[int(np.argmax([f1_score(ytr,(oof>=t)) for t in ths]))]
    p = s.predict_proba(Xb)[:,1]; fcal=f1_score(yte,(p>=thr))
    bp = s.best_params_
    mark = '  <-- VUOT 0.78!' if fcal>0.78 else ''
    print(f'  {label:26s} F1@0.5={f1_score(yte,(p>=0.5)):.3f}  F1@calib{thr:.2f}={fcal:.3f}  AUC-PR={average_precision_score(yte,p):.3f}  (CV-AP={s.best_score_:.3f})  [depth={bp["max_depth"]},lr={bp["learning_rate"]:.3f},n={bp["n_estimators"]}]{mark}', flush=True)
    return fcal, s
print('KIEM CHUNG: cay sau hon (depth 6-20) + lr nho hon (0.003-0.1) + n 600-1600', flush=True)
r1,_ = xgb_push(BASE_FE,             '1) 3 FE goc')
r2,_ = xgb_push(BASE_FE+NEW,         '2) + 4 tuong tac manh')
r3,sf = xgb_push(BASE_FE+ALL_NEW,    '3) + tat ca 7 feature moi')
imp = pd.Series(sf.best_estimator_.feature_importances_[:len(NUM+BASE_FE+ALL_NEW)], index=(NUM+BASE_FE+ALL_NEW))
keep = [c for c in (BASE_FE+ALL_NEW) if c in imp.sort_values(ascending=False).head(12).index]
r4,_ = xgb_push(keep,               '4) feature-selected (top-12)')
print(f'\n>>> XGB tot nhat = {max(r1,r2,r3,r4):.3f}  |  RF (moc) = 0.778  |  Vuot 0.78? {"CO" if max(r1,r2,r3,r4)>0.78 else "KHONG"}', flush=True)
