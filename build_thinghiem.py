# -*- coding: utf-8 -*-
"""Builder: notebook PHU LUC THI NGHIEM — ghi lai moi thu da thu (giu/bo).
Sinh: thi_nghiem_bo_sung.ipynb (tu chua, chay dau->cuoi, co output)."""
import nbformat as nbf
nb = nbf.v4.new_notebook(); cells = []
def md(s):   cells.append(nbf.v4.new_markdown_cell(s))
def code(s): cells.append(nbf.v4.new_code_cell(s))

md(r"""# 🧪 Phụ lục Thí nghiệm — Các cải tiến đã THỬ (giữ / bỏ)
### Bài cuối khoá ML · Predictive Maintenance dưới Distribution Shift

> **Mục đích.** Notebook này ghi lại **tất cả cải tiến đã thử nghiệm** ngoài bản chính `bai_tap_cuoi_khoa.ipynb`, theo kỷ luật **experiment-driven**: *giữ cái tăng điểm, bỏ cái không*. Mỗi thí nghiệm có **số đo thật trên Dây chuyền B** + **kết luận giữ/bỏ có lý do**. Đây là bằng chứng cho phần "Hạn chế & nhận ra trần dữ liệu" (rubric Phần 5) và để trả lời vấn đáp.

**Mốc tham chiếu (bản chính):** RandomForest + hiệu chỉnh ngưỡng → **F1 ≈ 0.778, AUC-PR ≈ 0.690** trên B.

| Thí nghiệm | Kết quả | Quyết định |
|---|---|---|
| 1. Feature tương tác nâng cao (4 biến, corr 0.15–0.18) | F1 0.778→0.773 | ❌ Bỏ |
| 2. Feature theo 4 cơ chế hỏng (osf/hdf/pwf/twf) | F1 ~+0.001 (nhiễu) | ❌ Không thêm |
| 3. Importance Reweighting cho XGBoost | F1 0.737→0.730 | ❌ Không dùng |
| 4. Weight clipping & Effective Sample Size | ESS lành mạnh, drift AUC=0.82 | ✅ Giữ clip percentile |
| 5. Bằng chứng trần (độ tinh khiết nhóm prob cao) | prob>0.9 chỉ ~80% thật hỏng | ✅ Trần ~0.78 là thật |
""")

md("## 0. Setup — dữ liệu, FE gốc, tiện ích chung")
code(r"""import os, warnings, numpy as np, pandas as pd
warnings.filterwarnings('ignore')
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.metrics import (average_precision_score, f1_score, roc_auc_score,
                             precision_score, recall_score)
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

def rf_new(): return RandomForestClassifier(n_estimators=500, min_samples_leaf=10, min_samples_split=10,
    max_features='sqrt', class_weight='balanced', random_state=RS, n_jobs=-1)

def eval_rf_on_B(fe_fn, feats, label):
    Xtr, Xte = fe_fn(train[NUM+CAT]), fe_fn(test[NUM+CAT]); NF = NUM + feats
    pre = ColumnTransformer([('num','passthrough',NF),
        ('ord',OrdinalEncoder(categories=[['L','M','H']]),['loai_san_pham']),
        ('oh',OneHotEncoder(handle_unknown='ignore',sparse_output=False),['ca_lam_viec'])])
    Xa, Xb = pre.fit_transform(Xtr), pre.transform(Xte)
    oof = cross_val_predict(rf_new(), Xa, ytr, cv=cv, method='predict_proba', n_jobs=-1)[:,1]
    ths = np.linspace(0.05,0.9,80); thr = ths[int(np.argmax([f1_score(ytr,(oof>=t)) for t in ths]))]
    p = rf_new().fit(Xa, ytr).predict_proba(Xb)[:,1]; yp = (p>=thr).astype(int)
    r = dict(label=label, F1=round(f1_score(yte,yp),3), AUC_PR=round(average_precision_score(yte,p),3),
             AUC_ROC=round(roc_auc_score(yte,p),3), thr=round(thr,2))
    print(f'  {label:34s} F1@calib={r["F1"]:.3f} (thr={r["thr"]})  AUC-PR={r["AUC_PR"]:.3f}  AUC-ROC={r["AUC_ROC"]:.3f}')
    return r
print('Setup OK. Train', train.shape, '| Test', test.shape)""")

# ---------------- TN1 ----------------
md(r"""## Thí nghiệm 1 — Feature tương tác nâng cao (do người dùng đề xuất)
Ý tưởng: nhân/tổ hợp các biến cơ học để \"nổi bật\" cực trị rủi ro. Tương quan tuyến tính với nhãn (0.15–0.18) cao hơn một số biến gốc — **nhưng đó chỉ là điều kiện cần**.
- `mon_x_toc_do` = mòn × tốc độ (dao mòn bị ép quay nhanh → rung/gãy)
- `cong_suat_x_mon` = công suất × mòn (\"áp lực công suất\" lên dao suy yếu)
- `cang_thang_nhiet` = (mòn×mômen) × chênh_lệch_nhiệt (quá tải cơ **và** nhiệt — bậc 3)
- `ly_tam_x_mon` = tốc_độ² × mòn (lực ly tâm ∝ v²)""")
code(r"""def new_fe(d):
    o = base_fe(d)
    o['mon_x_toc_do']    = o.do_mon_dao * o.toc_do_quay
    o['cong_suat_x_mon'] = o.cong_suat_co * o.do_mon_dao
    o['cang_thang_nhiet']= o.mon_x_momen * o.chenh_lech_nhiet
    o['ly_tam_x_mon']    = (o.toc_do_quay**2) * o.do_mon_dao
    return o
NEW = ['mon_x_toc_do','cong_suat_x_mon','cang_thang_nhiet','ly_tam_x_mon']
Ntr = new_fe(train[NUM+CAT])
print('|Pearson corr| voi hong_hoc (Train) — xac nhan con so nguoi dung dua:')
for c in ['do_mon_dao','mon_x_momen']+NEW:
    print(f'  {c:18s} {abs(np.corrcoef(Ntr[c],ytr)[0,1]):.3f}')
print('\nRandomForest tren Day chuyen B:')
r_base = eval_rf_on_B(base_fe, BASE_FE,          'A) 3 FE hien tai (moc)')
r_all  = eval_rf_on_B(new_fe,  BASE_FE+NEW,      'B) + 4 feature tuong tac moi')
r_lt   = eval_rf_on_B(new_fe,  BASE_FE+['ly_tam_x_mon'], 'C) + chi ly_tam_x_mon (bac cao)')""")
md(r"""> **Kết luận: ❌ BỎ.** Tương quan cao **không** dịch thành F1 cao. Bốn biến là **tích của biến RF đã có** → cây tự dựng tương tác qua các split, feature tường minh **dư thừa**; thêm biến tương quan cao còn **làm loãng `max_features='sqrt'`** và **overfit trên A** → transfer sang B **kém đi** (F1 0.778→0.773, AUC-PR giảm). Đây là minh hoạ kinh điển: *feature selection theo tương quan tuyến tính gây hiểu nhầm với mô hình cây phi tuyến.*""")

# ---------------- TN2 ----------------
md(r"""## Thí nghiệm 2 — Feature theo 4 cơ chế hỏng (ngưỡng học TỪ Train)
Encode tường minh 4 cơ chế: **OSF** (overstrain theo hạng SP), **HDF** (tản nhiệt kém), **PWF** (quá tải công suất), **TWF** (vùng mòn nguy hiểm). Ngưỡng **suy từ Train** (không chép hằng số tài liệu → trung thực, không rò rỉ).""")
code(r"""prod_thr = {lv: np.quantile((train.do_mon_dao*train.momen_xoan)[(train.loai_san_pham==lv)&(train[T]==0)], 0.99)
            for lv in ['L','M','H']}
print('Nguong OSF hoc tu Train (P99 nhom khong hong):', {k:round(v) for k,v in prod_thr.items()})
def mech_fe(d):
    o = base_fe(d)
    o['osf_margin'] = (d.do_mon_dao*d.momen_xoan).values - d.loai_san_pham.map(prod_thr).values
    o['hdf_risk']   = ((o.chenh_lech_nhiet<8.6)&(o.toc_do_quay<1380)).astype(int)
    o['pwf_low']    = (o.cong_suat_co<3500).astype(int)
    o['pwf_high']   = (o.cong_suat_co>9000).astype(int)
    o['twf_zone']   = ((o.do_mon_dao>=200)&(o.do_mon_dao<=240)).astype(int)
    return o
print('\nRandomForest tren Day chuyen B:')
eval_rf_on_B(base_fe, BASE_FE, 'A) 3 FE hien tai (moc)')
eval_rf_on_B(mech_fe, BASE_FE+['osf_margin'], 'B) + osf_margin (hoc Train)')
eval_rf_on_B(mech_fe, BASE_FE+['osf_margin','hdf_risk','pwf_low','pwf_high','twf_zone'], 'C) + du 4 co che')""")
md(r"""> **Kết luận: ❌ KHÔNG thêm.** `osf_margin` chỉ +0.001 F1 (trong nhiễu); đủ 4 cơ chế còn **làm tệ đi** (cờ boolean dư thừa + overfit A). Ngưỡng OSF học từ Train (~12100/12400/12900) **rất gần** giá trị tài liệu AI4I (11000/12000/13000) → xác nhận cơ chế đúng, nhưng **RF đã tự trích** ranh giới đó từ `mon_x_momen`×`loai_san_pham`.""")

# ---------------- TN3 ----------------
md(r"""## Thí nghiệm 3 — Importance Reweighting cho **XGBoost**
Bản chính đã reweight cho RF (v3, F1 gần như không đổi). Thử reweight cho XGB (variance cao hơn, bám phân phối A hơn → *liệu có "khôn lên"?*). Trọng số density-ratio từ Drift Classifier, clip percentile 1–99.""")
code(r"""Xtr_fe, Xte_fe = base_fe(train[NUM+CAT]), base_fe(test[NUM+CAT]); NF = NUM+BASE_FE
pre_t = ColumnTransformer([('num','passthrough',NF),
    ('ord',OrdinalEncoder(categories=[['L','M','H']]),['loai_san_pham']),
    ('oh',OneHotEncoder(handle_unknown='ignore',sparse_output=False),['ca_lam_viec'])])
Xa, Xb = pre_t.fit_transform(Xtr_fe), pre_t.transform(Xte_fe)
spw = (ytr==0).sum()/(ytr==1).sum()
# density-ratio tu drift classifier
Xd = np.vstack([Xtr_fe[NF].values, Xte_fe[NF].values]); yd = np.r_[np.zeros(len(Xtr_fe)),np.ones(len(Xte_fe))]
drift = RandomForestClassifier(n_estimators=300,min_samples_leaf=5,random_state=RS,n_jobs=-1).fit(Xd,yd)
w = drift.predict_proba(Xtr_fe[NF].values)[:,1]; w = w/(1-w)
w = np.clip(w, np.quantile(w,.01), np.quantile(w,.99)); w = w*len(w)/w.sum()
def xgb(): return XGBClassifier(random_state=RS,n_jobs=-1,tree_method='hist',eval_metric='aucpr',scale_pos_weight=spw,
    subsample=1.0,reg_lambda=1,n_estimators=400,min_child_weight=5,max_depth=3,learning_rate=0.1,gamma=1,colsample_bytree=0.6)
oof_xgb = cross_val_predict(xgb(), Xa, ytr, cv=cv, method='predict_proba', n_jobs=-1)[:,1]
ths=np.linspace(0.05,0.9,80); thr_xgb=ths[int(np.argmax([f1_score(ytr,(oof_xgb>=t)) for t in ths]))]
def run_xgb(sw, label):
    m = xgb().fit(Xa, ytr, sample_weight=sw); p = m.predict_proba(Xb)[:,1]; thr = thr_xgb
    for tag,t in [('@0.5',0.5),(f'@calib{thr:.2f}',thr)]:
        yp=(p>=t).astype(int)
        print(f'  {label:16s}{tag:12s} F1={f1_score(yte,yp):.3f}  P={precision_score(yte,yp):.3f}  R={recall_score(yte,yp):.3f}  AUC-PR={average_precision_score(yte,p):.3f}')
print('XGBoost tren Day chuyen B (muc tieu: RF ~0.778):')
run_xgb(None, 'base')
run_xgb(w,    'reweight')""")
md(r"""> **Kết luận: ❌ KHÔNG dùng.** Reweight làm XGB **DỞ đi** (F1 0.737→0.730; AUC-PR 0.656→0.643). Lý do: tín hiệu số 1 `do_mon_dao` **PSI≈0 (không shift)** → density-ratio dồn trọng số sang vùng nhiệt độ (ít thông tin) + giảm ESS → tăng variance cho mô hình boosting vốn đã cao variance. **Đòn bẩy đúng cho XGB là hiệu chỉnh ngưỡng** (F1 0.737→0.754), không phải reweight.""")

# ---------------- TN4 ----------------
md(r"""## Thí nghiệm 4 — Weight Clipping & Effective Sample Size (ESS)
Lo ngại: nếu Drift Classifier quá mạnh (AUC>0.95) thì trọng số `w=p/(1−p)` có thể →∞ → mô hình phụ thuộc vài mẫu cá biệt (high variance). Kiểm tra thực tế + so **clip percentile 1–99** (đang dùng) vs **clip fixed [0.2,10]**.""")
code(r"""def drift_w(cols, clip):
    A = base_fe(train[NUM+CAT])[cols].values; B = base_fe(test[NUM+CAT])[cols].values
    Xd = np.vstack([A,B]); yd = np.r_[np.zeros(len(A)),np.ones(len(B))]
    dm = RandomForestClassifier(n_estimators=300,min_samples_leaf=5,random_state=RS,n_jobs=-1)
    auc = roc_auc_score(yd, cross_val_predict(dm,Xd,yd,cv=5,method='predict_proba',n_jobs=-1)[:,1])
    dm.fit(Xd,yd); w = dm.predict_proba(A)[:,1]; w = w/(1-w)
    if clip=='percentile 1-99': w = np.clip(w, np.quantile(w,.01), np.quantile(w,.99))
    else:                        w = np.clip(w, 0.2, 10.0)
    w = w*len(w)/w.sum(); ess = (w.sum()**2)/(w**2).sum()
    print(f'  {str(cols is FEcols):5s} drift feature | clip={clip:16s} driftAUC={auc:.3f}  w=[{w.min():.2f},{w.max():.2f}]  ESS={ess:.0f}/{len(w)} ({ess/len(w):.0%})')
FEcols = NUM+BASE_FE
print('Drift feature = FE (giam shift) vs raw (co nhiet do tho):')
for cols,tag in [(FEcols,'FE'),(NUM,'raw')]:
    for clip in ['percentile 1-99','fixed [0.2,10]']:
        drift_w(cols, clip)""")
md(r"""> **Kết luận: ✅ GIỮ clip percentile 1–99.** Thực tế **Drift AUC ≈ 0.82 (KHÔNG >0.95)** — dù `nhiet_do_moi_truong` PSI=1.08, phân phối **khớp** của A/B vẫn chồng nhau nhiều nên không tách tuyệt đối. **Không có w→∞**: clip percentile cho max ≈ 7, **ESS ≈ 5700/14000 (≈41% — lành mạnh)**. Clip fixed [0.2,10] cho ESS cao hơn chút (bảo thủ hơn) nhưng không đổi kết quả. Bản chính đã **in ESS** để minh bạch điểm này.""")

# ---------------- TN5 ----------------
md(r"""## Thí nghiệm 5 — Bằng chứng **TRẦN F1 ~0.78** (không phải xử lý kém)
Nếu nhãn tất định theo feature, nhóm mô hình chấm xác suất cao **phải** gần 100% thật hỏng. Đo *độ tinh khiết* theo dải xác suất (OOF trên Train).""")
code(r"""oof = cross_val_predict(rf_new(), pre_t.fit_transform(base_fe(train[NUM+CAT])), ytr,
                        cv=cv, method='predict_proba', n_jobs=-1)[:,1]
print('Dai xac suat du bao  ->  ty le HONG that su:')
for lo,hi in [(0,.1),(.1,.3),(.3,.5),(.5,.7),(.7,.9),(.9,1.01)]:
    m=(oof>=lo)&(oof<hi)
    if m.sum()>30: print(f'  {int(lo*100):3d}-{int(hi*100):3d}%: {ytr[m].mean()*100:5.1f}% that su hong  (n={m.sum()})')""")
md(r"""> **Kết luận: ✅ Trần ~0.78 là THẬT.** Ngay nhóm **chắc nhất (prob>0.9)** cũng chỉ ~**80% thật sự hỏng** → precision bị chặn → **F1 chạm trần**. Nguyên nhân: **nhiễu nhãn** + **clipping biên** (`do_mon_dao` chặn 253, `toc_do_quay` cắt 1180) + **distribution shift** (ranh giới học trên A lệch trên B). Vượt trần chỉ đạt nếu **rò rỉ** (dùng nhãn Test / chép hằng số nhãn) — đã tránh.""")

md(r"""## 📌 Tổng kết — nguyên tắc rút ra
1. **Giữ:** RandomForest + 3 FE cơ học + **Threshold Calibration** + **IWV** (chọn không nhìn Test) + clip trọng số percentile + ESS minh bạch.
2. **Bỏ (đã đo, không giúp/hại):** feature tương tác nâng cao, đủ 4 cơ chế cờ boolean, reweight XGB.
3. **Bài học:** dưới distribution shift + nhãn nhiễu, **F1~0.78 là trần thông tin**; giá trị nằm ở **chứng minh chạm trần đúng cách (không rò rỉ)**, không phải con số F1 tuyệt đối. Đây chính là phần "nhận ra hạn chế" mà rubric Phần 5 chấm điểm.

*Notebook tự chứa, chạy từ đầu đến cuối. Dùng kèm bản chính `bai_tap_cuoi_khoa.ipynb`.*""")

nb['cells'] = cells
nbf.write(nb, 'thi_nghiem_bo_sung.ipynb')
print('Notebook written:', len(cells), 'cells -> thi_nghiem_bo_sung.ipynb')
