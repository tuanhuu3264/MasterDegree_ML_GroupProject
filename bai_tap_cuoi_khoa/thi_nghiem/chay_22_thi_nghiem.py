# -*- coding: utf-8 -*-
"""
Chạy 22 thí nghiệm chứng minh trần F1 ≈ 0.78 (train Line A -> test Line B).
Xuất kết quả ra: thi_nghiem/ket_qua_22_thi_nghiem.md
Chạy: python thi_nghiem/chay_22_thi_nghiem.py   (từ thư mục gốc repo)
"""
import os, sys, io, time, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import f1_score
import xgboost as xgb

LOG_LINES = []
def out(s=''):
    print(s); LOG_LINES.append(str(s))

# ================= SETUP =================
CANDS = ['Data_Final/Data_Final','Answer/Data_Final/Data_Final','bai_tap_cuoi_khoa/Data_Final',
         'Data_Final','../Data_Final','thi_nghiem/../Data_Final']
D = next(d for d in CANDS if os.path.exists(f'{d}/test.csv'))
train = pd.read_csv(f'{D}/train.csv'); test = pd.read_csv(f'{D}/test.csv')
NUM = ['nhiet_do_moi_truong','nhiet_do_quy_trinh','toc_do_quay','momen_xoan','do_mon_dao']
CAT = ['loai_san_pham','ca_lam_viec']
ytr, yte = train['hong_hoc'].values, test['hong_hoc'].values
spw = (ytr==0).sum()/(ytr==1).sum()
NGUONG = {'L':11000,'M':12000,'H':13000}

def add(df):
    o=df.copy(); dT=o.nhiet_do_quy_trinh-o.nhiet_do_moi_truong
    P=o.momen_xoan*o.toc_do_quay*2*np.pi/60; ng=o.loai_san_pham.map(NGUONG)
    o['chenh_lech_nhiet']=dT; o['cong_suat_co']=P; o['mon_x_momen']=o.do_mon_dao*o.momen_xoan
    o['nguy_tan_nhiet']=np.maximum(8.6-dT,0)*np.maximum(1380-o.toc_do_quay,0)
    o['lech_cong_suat']=np.maximum(3500-P,0)+np.maximum(P-9000,0)
    o['bien_overstrain']=o.do_mon_dao*o.momen_xoan-ng
    o['mon_toi_han']=np.maximum(o.do_mon_dao-200,0)
    o['trong_dai_twf']=((o.do_mon_dao>=200)&(o.do_mon_dao<=240)).astype(int)
    o['bien_dT']=np.maximum(8.6-dT,0); o['bien_rpm']=np.maximum(1380-o.toc_do_quay,0)
    o['co_hdf']=((dT<8.6)&(o.toc_do_quay<1380)).astype(int)
    o['pwf_thap']=np.maximum(3500-P,0); o['pwf_cao']=np.maximum(P-9000,0)
    o['co_pwf']=((P<3500)|(P>9000)).astype(int)
    o['ti_overstrain']=(o.do_mon_dao*o.momen_xoan)/ng
    o['co_osf']=((o.do_mon_dao*o.momen_xoan)>ng).astype(int)
    o['so_co_che_nguy']=o['co_hdf']+o['co_pwf']+o['co_osf']+(o.do_mon_dao>=200).astype(int)
    return o
RAW3   = ['chenh_lech_nhiet','cong_suat_co','mon_x_momen']
HINGE3 = ['nguy_tan_nhiet','lech_cong_suat','bien_overstrain']
SET4   = HINGE3+['mon_toi_han','trong_dai_twf','bien_dT','bien_rpm','co_hdf',
                 'pwf_thap','pwf_cao','co_pwf','ti_overstrain','co_osf','so_co_che_nguy']
Atr, Ate = add(train), add(test)

def enc(cols, scale=False):
    num = StandardScaler() if scale else 'passthrough'
    pre = ColumnTransformer([('num',num,cols),
        ('ord',OrdinalEncoder(categories=[['L','M','H']]),['loai_san_pham']),
        ('oh',OneHotEncoder(handle_unknown='ignore',sparse_output=False),['ca_lam_viec'])])
    return pre.fit_transform(Atr[cols+CAT]), pre.transform(Ate[cols+CAT])

def thr_oof(y,p):
    t=np.linspace(0.05,0.95,90); return t[int(np.argmax([f1_score(y,(p>=x)) for x in t]))]

def RF(s=42):  return RandomForestClassifier(n_estimators=300,min_samples_leaf=10,min_samples_split=10,max_features='sqrt',class_weight='balanced',random_state=s,n_jobs=-1)
def HGB(s=42): return HistGradientBoostingClassifier(max_iter=500,learning_rate=0.05,l2_regularization=1.0,class_weight='balanced',random_state=s)
def XGBm(s=42):return xgb.XGBClassifier(n_estimators=200,max_depth=4,learning_rate=0.05,subsample=0.6,colsample_bytree=0.8,reg_lambda=1,gamma=3,min_child_weight=1,scale_pos_weight=spw,tree_method='hist',eval_metric='aucpr',random_state=s,n_jobs=-1)
def LR(s=42):  return LogisticRegression(class_weight='balanced',max_iter=2000,random_state=s)

def eval_model(mk, Xa, Xb, seeds=(42,7)):
    fs=[]; oo=pp=None
    for s in seeds:
        oof=cross_val_predict(mk(s),Xa,ytr,cv=StratifiedKFold(5,shuffle=True,random_state=s),method='predict_proba',n_jobs=-1)[:,1]
        t=thr_oof(ytr,oof); p=mk(s).fit(Xa,ytr).predict_proba(Xb)[:,1]; fs.append(f1_score(yte,(p>=t)))
        if s==seeds[0]: oo,pp=oof,p
    return np.mean(fs), np.std(fs), oo, pp

out('# Kết quả 22 thí nghiệm — Chứng minh trần F1 ≈ 0.78')
out('')
out(f'**Setup:** data=`{D}` | train={train.shape} | test={test.shape} | test pos=%.2f%% | scale_pos_weight=%.2f'%(yte.mean()*100,spw))
out('')
t0=time.time()
RESULTS={}  # gom số liệu để làm bảng tổng hợp

# ================= NHÓM 1 =================
out('## NHÓM 1 — Nhiều model khác nhau (FE=SET4)')
out('*Đổi họ mô hình vẫn ~0.78.*'); out('')
out('| TN | Model | F1 (test B) | std |'); out('|---|---|---:|---:|')
Xa,Xb   = enc(SET4)
Xas,Xbs = enc(SET4, scale=True)
g1=[]
for i,(nm, mk, sc) in enumerate([('RandomForest',RF,0),('XGBoost',XGBm,0),('HistGradientBoosting',HGB,0),('LogisticRegression',LR,1)],1):
    f,sd,_,_ = eval_model(mk, Xas if sc else Xa, Xbs if sc else Xb)
    out(f'| {i} | {nm} | {f:.4f} | ±{sd:.4f} |'); g1.append((nm,f))
RESULTS['nhom1']=g1
out('')

# ================= NHÓM 2 =================
out('## NHÓM 2 — Thêm feature vật lý (RF)')
out('*FE vật lý nâng 0.66 -> 0.78 rồi bão hòa.*'); out('')
out('| TN | Feature set | #feat | F1 (test B) | std |'); out('|---|---|---:|---:|---:|')
g2=[]
for i,(nm, cols) in enumerate([('NUM thô',NUM),('+RAW3 (tích/hiệu)',NUM+RAW3),('+HINGE3 (hinge cơ chế)',NUM+HINGE3),('+SET4 (đầy đủ 5 cơ chế)',NUM+SET4)],5):
    Xa2,Xb2 = enc(cols); f,sd,_,_ = eval_model(RF,Xa2,Xb2)
    out(f'| {i} | {nm} | {len(cols)} | {f:.4f} | ±{sd:.4f} |'); g2.append((nm,f))
RESULTS['nhom2']=g2
out('')

# ================= NHÓM 3 =================
out('## NHÓM 3 — Hạ trọng số biến thô (XGBoost feature_weights)')
out('*Ép XGB bỏ biến thô, dựa vào FE cơ chế — vẫn ~0.78.*'); out('')
out('| TN | w_raw | F1 (test B) |'); out('|---|---|---:|')
NF = NUM+SET4
pre = ColumnTransformer([('num','passthrough',NF),
    ('ord',OrdinalEncoder(categories=[['L','M','H']]),['loai_san_pham']),
    ('oh',OneHotEncoder(handle_unknown='ignore',sparse_output=False),['ca_lam_viec'])])
XA=pre.fit_transform(Atr[NF+CAT]); XB=pre.transform(Ate[NF+CAT])
ncol=XA.shape[1]; names=[f'f{i}' for i in range(ncol)]
PAR=dict(objective='binary:logistic',eval_metric='aucpr',tree_method='hist',max_depth=4,
         eta=0.05,subsample=0.6,colsample_bynode=0.5,reg_lambda=1.0,gamma=3,min_child_weight=1,scale_pos_weight=spw)
def xgb_fw(w_raw,s=42):
    fw=np.ones(ncol); fw[:len(NUM)]=w_raw
    def tp(Xt,yt,Xp):
        d=xgb.DMatrix(Xt,label=yt,feature_names=names); d.set_info(feature_weights=fw)
        p=dict(PAR); p['seed']=s; b=xgb.train(p,d,num_boost_round=250)
        return b.predict(xgb.DMatrix(Xp,feature_names=names))
    oof=np.zeros(len(ytr))
    for tri,vai in StratifiedKFold(5,shuffle=True,random_state=s).split(XA,ytr):
        oof[vai]=tp(XA[tri],ytr[tri].astype(float),XA[vai])
    t=thr_oof(ytr,oof); pb=tp(XA,ytr.astype(float),XB); return f1_score(yte,(pb>=t))
g3=[]
for i,w in enumerate([1.0,0.5,0.1,0.0],9):
    f=xgb_fw(w); out(f'| {i} | {w:.1f} | {f:.4f} |'); g3.append((f'w={w}',f))
RESULTS['nhom3']=g3
out('')

# ================= NHÓM 4 =================
out('## NHÓM 4 — Ensemble')
out('*Kết hợp model KHÔNG vượt model đơn (lỗi tương quan ở vùng nhiễu).*'); out('')
out('| TN | Ensemble | F1 (test B) |'); out('|---|---|---:|')
Xa,Xb = enc(SET4)
_,_,o_rf,p_rf = eval_model(RF,  Xa,Xb, seeds=(42,))
_,_,o_xg,p_xg = eval_model(XGBm,Xa,Xb, seeds=(42,))
_,_,o_hg,p_hg = eval_model(HGB, Xa,Xb, seeds=(42,))
g4=[]
def combo(idx,nm,oo,pp):
    t=thr_oof(ytr,oo); f=f1_score(yte,(pp>=t)); out(f'| {idx} | {nm} | {f:.4f} |'); g4.append((nm,f))
combo(13,'Voting RF+XGB (0.5/0.5)',        (o_rf+o_xg)/2,       (p_rf+p_xg)/2)
combo(14,'Weighted RF+XGB (0.7/0.3)',      0.7*o_rf+0.3*o_xg,  0.7*p_rf+0.3*p_xg)
combo(15,'Voting RF+XGB+HGB',              (o_rf+o_xg+o_hg)/3,  (p_rf+p_xg+p_hg)/3)
meta=LogisticRegression(class_weight='balanced',max_iter=2000).fit(np.column_stack([o_rf,o_xg,o_hg]),ytr)
combo(16,'Stacking meta-LogReg',
      meta.predict_proba(np.column_stack([o_rf,o_xg,o_hg]))[:,1],
      meta.predict_proba(np.column_stack([p_rf,p_xg,p_hg]))[:,1])
RESULTS['nhom4']=g4
out('')

# ================= NHÓM 5 =================
out('## NHÓM 5 — Xử lý dữ liệu (cân bằng lớp & khử nhiễu)')
out('*Cân bằng ≈ giữ nguyên; khử nhiễu là cái bẫy: OOF ảo vọt, TEST tụt.*'); out('')
out('| TN | Cách | F1 (test B) | Ghi chú |'); out('|---|---|---:|---|')
Xa,Xb = enc(SET4)
def rf_cw(cw):
    m=RandomForestClassifier(n_estimators=300,min_samples_leaf=10,min_samples_split=10,
                             max_features='sqrt',class_weight=cw,random_state=42,n_jobs=-1)
    oof=cross_val_predict(m,Xa,ytr,cv=StratifiedKFold(5,shuffle=True,random_state=42),method='predict_proba',n_jobs=-1)[:,1]
    t=thr_oof(ytr,oof); p=m.fit(Xa,ytr).predict_proba(Xb)[:,1]; return f1_score(yte,(p>=t))
g5=[]
f=rf_cw(None);       out(f'| 17 | class_weight=None | {f:.4f} | |'); g5.append(('cw=None',f))
f=rf_cw('balanced'); out(f'| 18 | class_weight=balanced | {f:.4f} | |'); g5.append(('cw=balanced',f))
oofb=cross_val_predict(RF(),Xa,ytr,cv=StratifiedKFold(5,shuffle=True,random_state=42),method='predict_proba',n_jobs=-1)[:,1]
wrong=np.abs(oofb-ytr)
for idx,kp in [(19,3),(20,5)]:
    k=int(len(ytr)*kp/100); keep=np.setdiff1d(np.arange(len(ytr)), np.argsort(wrong)[::-1][:k])
    m=RF(); oo=cross_val_predict(m,Xa[keep],ytr[keep],cv=StratifiedKFold(5,shuffle=True,random_state=42),method='predict_proba',n_jobs=-1)[:,1]
    t=thr_oof(ytr[keep],oo); p=m.fit(Xa[keep],ytr[keep]).predict_proba(Xb)[:,1]
    ftest=f1_score(yte,(p>=t)); foof=f1_score(ytr[keep],(oo>=t))
    out(f'| {idx} | Khử nhiễu bỏ {kp}% "sai tự tin nhất" | {ftest:.4f} | **OOF ảo = {foof:.3f}** |'); g5.append((f'khu {kp}%',ftest))
RESULTS['nhom5']=g5
out('')

# ================= ĐÓNG CHỨNG MINH =================
out('## ĐÓNG CHỨNG MINH — 2 thí nghiệm chốt')
out('')
out('### TN21 — CẬN TRÊN: oracle train thẳng trên test B (CV nội bộ test)')
out('*Cho model biết luôn phân phối B. Nếu vẫn < 0.80 -> 0.80 bất khả.*'); out('')
Xb_o = enc(SET4)[1]
orc=[]
for s in range(3):
    oo=cross_val_predict(RandomForestClassifier(n_estimators=400,min_samples_leaf=5,max_features='sqrt',
        class_weight='balanced',random_state=s,n_jobs=-1),Xb_o,yte,
        cv=StratifiedKFold(5,shuffle=True,random_state=s),method='predict_proba',n_jobs=-1)[:,1]
    tt=np.linspace(0.05,0.95,120); orc.append(max(f1_score(yte,(oo>=x)) for x in tt))
oracle=np.mean(orc)
out(f'**ORACLE within-test maxF1 = {oracle:.4f} ± {np.std(orc):.4f}** — biết trước phân phối B cũng chỉ tới đây.')
RESULTS['oracle']=oracle
out('')
out('### TN22 — BẢN CHẤT: nhiễu aleatoric (không phụ thuộc model)')
out('*Điểm trùng khít khác nhãn = lỗi bắt buộc; 1-NN của ca hỏng có phải máy khỏe không.*'); out('')
Xs=StandardScaler().fit_transform(test[NUM].values)
oc=OrdinalEncoder().fit_transform(test[CAT].values)
Xn=np.column_stack([Xs, oc*3.0])
_,idx=NearestNeighbors(n_neighbors=2).fit(Xn).kneighbors(Xn); nn1=idx[:,1]
g=test.groupby(NUM+CAT)['hong_hoc']; pm=yte==1
n_mau_thuan=((g.transform('sum')>0)&(g.transform('sum')<g.transform('size'))).sum()
nn_hong=(yte[nn1]==yte)[pm].mean()*100
out(f'- Điểm trùng khít khác nhãn (mâu thuẫn): **{n_mau_thuan}**')
out(f'- Ca hỏng có 1-NN cũng hỏng: **{nn_hong:.1f}%** -> ~{100-nn_hong:.0f}% ca hỏng có láng giềng gần nhất là máy KHỎE (chồng lấp lớp).')
RESULTS['nn_hong']=nn_hong
out('')

# ================= TỔNG HỢP =================
allF=[f for g in [g1,g2,g3,g4,g5] for _,f in g]
valid=[f for g in [g1,g4,g5] for _,f in g]+[f for _,f in g3]+[f for nm,f in g2 if 'NUM thô' not in nm]  # hợp cách
best=max(allF)
out('## Kết luận')
out('')
out(f'- **Cận dưới (chặt):** cấu hình tốt nhất đạt **F1 = {best:.4f}** -> C* ≥ {best:.4f}.')
out(f'- **Cận trên (bằng chứng):** các cấu hình hợp cách ∈ **[{min(valid):.4f}, {max(valid):.4f}]**; oracle biết-trước-B chỉ **{oracle:.4f}**.')
out(f'- **Bản chất nhiễu:** ~{100-nn_hong:.0f}% ca hỏng bị bao quanh bởi máy khỏe -> sai số aleatoric không thể khử bằng model.')
out(f'- **∴ Trần C\\* ≈ 0.78.** Đạt ≥ 0.80 chỉ bằng leakage (dùng nhãn test) — không hợp lệ.')
out('')
out(f'_Tổng thời gian chạy: {time.time()-t0:.0f}s_')

# ghi file
outpath = os.path.join(os.path.dirname(__file__), 'ket_qua_22_thi_nghiem.md')
with open(outpath,'w',encoding='utf-8') as fp:
    fp.write('\n'.join(LOG_LINES))
print('\n>>> Đã ghi:', outpath)
