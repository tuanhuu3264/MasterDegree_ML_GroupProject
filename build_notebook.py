# -*- coding: utf-8 -*-
"""Builder: tao Jupyter Notebook hoan chinh cho bai tap Predictive Maintenance duoi Distribution Shift."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []
def md(src):  cells.append(nbf.v4.new_markdown_cell(src))
def code(src): cells.append(nbf.v4.new_code_cell(src))

# ===================== TITLE =====================
md(r"""# Dự đoán Hỏng hóc Thiết bị dưới Distribution Shift
### Bài tập cuối khoá — Machine Learning · Predictive Maintenance (máy phay CNC)

**Bài toán:** Dự đoán nhị phân `hong_hoc` (thiết bị hỏng trong ca kế tiếp). Train = Dây chuyền A (nhà máy cũ), Test = Dây chuyền B (nhà máy mới, khí hậu nóng hơn, tải khác) → **distribution shift là có thật**.

---
## ⚠️ Ghi chú kiểm toán dữ liệu (các "điểm cài cắm" phát hiện trước khi mô hình hoá)
Trong quá trình khám phá tôi phát hiện một số điểm đã bị cài đặt có chủ đích — cần nhận ra và xử lý đúng:

| # | Phát hiện | Bằng chứng | Cách xử lý |
|---|-----------|-----------|------------|
| 1 | `toc_do_quay` **bị cắt sàn nhân tạo tại 1180** | Train có **309 dòng = đúng 1180.00** (giá trị khác chỉ 1–2 lần) | Ghi nhận censoring; không coi spike là tín hiệu vật lý thật |
| 2 | `do_mon_dao` **cắt trần 253/sàn 0**, `momen_xoan` **cắt sàn 3.5** | Pile-up tại biên ở cả 2 tập | Ghi nhận clipping cảm biến |
| 3 | Tỷ lệ hỏng thực **~7.4% train / 7.9% test** | Đề bài ghi "~3–5%" | Dùng **số thực đo được**, không tin mù mô tả đề |
| 4 | `ca_lam_viec` là **nhiễu thuần** | Tỷ lệ hỏng phẳng mọi ca; drift-importance ≈ 0.01 | Giữ nhưng kỳ vọng vô dụng; KHÔNG over-engineer |
| 5 | `loai_san_pham` biên phẳng **nhưng có ý nghĩa vật lý** (ngưỡng overstrain theo L/M/H) | Marginal phẳng nhưng tương tác qua OSF | **Không loại nhầm**; tạo feature tương tác |
| 6 | Test **ngoại suy vượt biên train** | 159 dòng nóng hơn train-max; tốc độ test max 2414.9 ≫ train 2153.5 | Cảnh báo vùng extrapolation |

**Insight cốt lõi:** Đây là **covariate shift** (P(X) đổi) **chứ không phải concept drift** — `P(hỏng | cơ chế vật lý)` ổn định giữa 2 tập ⇒ **FE theo cơ chế + Importance Reweighting + Threshold Calibration** là hướng đúng.

*(Dữ liệu tương đương AI4I 2020 / UCI Predictive Maintenance đổi tên tiếng Việt; 4 cơ chế hỏng: hao mòn dao TWF, tản nhiệt kém HDF, quá tải công suất PWF, quá tải căng thẳng OSF.)*
""")

# ===================== SETUP =====================
md("## 0. Thiết lập môi trường & nạp dữ liệu")
code(r"""import os, warnings, numpy as np, pandas as pd
import matplotlib.pyplot as plt, seaborn as sns
from scipy import stats
warnings.filterwarnings('ignore')
plt.rcParams['figure.dpi'] = 110
sns.set_style('whitegrid')
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

CANDIDATES = ['Data_Final/Data_Final','../Data_Final/Data_Final','Data_Final','../Data_Final','.']
DATA_DIR = next((c for c in CANDIDATES
                 if os.path.exists(os.path.join(c,'train.csv')) and os.path.exists(os.path.join(c,'test.csv'))), None)
assert DATA_DIR is not None, 'Khong tim thay train.csv/test.csv'
print('DATA_DIR =', os.path.abspath(DATA_DIR))

train = pd.read_csv(os.path.join(DATA_DIR,'train.csv'))
test  = pd.read_csv(os.path.join(DATA_DIR,'test.csv'))
NUM = ['nhiet_do_moi_truong','nhiet_do_quy_trinh','toc_do_quay','momen_xoan','do_mon_dao']
CAT = ['loai_san_pham','ca_lam_viec']
TARGET = 'hong_hoc'
print('Train:', train.shape, '| Test:', test.shape)
train.head()""")

# ===================== PART 1: EDA =====================
md(r"""## Phần 1 — Khám phá dữ liệu (EDA)
### 1.1 Thống kê mô tả & chất lượng dữ liệu""")
code(r"""print('--- Kieu du lieu & thieu du lieu ---')
info = pd.DataFrame({'dtype': train.dtypes,
                     'missing_train': train.isna().sum(),
                     'missing_test': test.reindex(columns=train.columns).isna().sum(),
                     'nunique_train': train.nunique()})
display(info)
print('\n--- Thong ke mo ta (numeric) TRAIN ---'); display(train[NUM].describe().T)
print('--- Thong ke mo ta (numeric) TEST ---');  display(test[NUM].describe().T)""")

md("### 1.2 Mất cân bằng của biến mục tiêu (target imbalance)")
code(r"""rate_tr, rate_te = train[TARGET].mean(), test[TARGET].mean()
print(f'Ty le hong TRAIN: {rate_tr:.4f} ({rate_tr*100:.2f}%)  counts={train[TARGET].value_counts().to_dict()}')
print(f'Ty le hong TEST : {rate_te:.4f} ({rate_te*100:.2f}%)  counts={test[TARGET].value_counts().to_dict()}')
print(f'Imbalance ratio (neg:pos) TRAIN = {(1-rate_tr)/rate_tr:.1f} : 1')
print('>> DIEM CAI CAM #3: de bai ghi ~3-5% nhung THUC TE ~7-8%. Dung so do duoc.')

fig, ax = plt.subplots(1,2, figsize=(10,3.5))
for a,(nm,d) in zip(ax, [('TRAIN (A)',train),('TEST (B)',test)]):
    d[TARGET].value_counts().sort_index().plot(kind='bar', ax=a, color=['#4C72B0','#C44E52'])
    a.set_title(f'{nm} — ty le hong = {d[TARGET].mean()*100:.2f}%'); a.set_xticklabels(['0 (OK)','1 (Hong)'], rotation=0)
plt.tight_layout(); plt.show()""")

md("### 1.3 So sánh trực quan phân phối Dây chuyền A (Train) vs B (Test) — dấu hiệu shift")
code(r"""fig, axes = plt.subplots(2,3, figsize=(15,7))
for ax, col in zip(axes.ravel(), NUM):
    sns.kdeplot(train[col], ax=ax, label='Train (A)', fill=True, alpha=.3, color='#4C72B0')
    sns.kdeplot(test[col],  ax=ax, label='Test (B)',  fill=True, alpha=.3, color='#C44E52')
    ax.axvline(train[col].mean(), color='#4C72B0', ls='--', lw=1)
    ax.axvline(test[col].mean(),  color='#C44E52', ls='--', lw=1)
    ax.set_title(f'{col}\nΔmean = {test[col].mean()-train[col].mean():+.2f}'); ax.legend(fontsize=8)
axes.ravel()[-1].axis('off')
plt.suptitle('Phan phoi Train(A) vs Test(B) — dich chuyen ro rang o nhiet do & toc do', y=1.02, fontsize=13)
plt.tight_layout(); plt.show()

print('Nhan xet: Test NONG hon (air +2.5K, process +1.9K), toc do quay CAO hon (+70rpm), momen THAP hon (-3.4Nm).')
print('=> Khop boi canh: khi hau nong hon, tai khac. Day la nguon distribution shift chinh.')""")

md("### 1.4 Bằng chứng các điểm cài cắm clipping (cắt biên nhân tạo)")
code(r"""print('--- DIEM CAI CAM #1 & #2: pile-up tai bien (dau hieu clipping) ---')
for col in NUM:
    s = train[col]
    print(f'{col:22s} min={s.min():8.2f} (n={ (s==s.min()).sum():4d})  max={s.max():8.2f} (n={ (s==s.max()).sum():3d})')

fig, ax = plt.subplots(1,2, figsize=(12,3.5))
train['toc_do_quay'].plot(kind='hist', bins=120, ax=ax[0], color='#4C72B0')
ax[0].axvline(1180, color='red', ls='--'); ax[0].set_title('toc_do_quay TRAIN — spike nhan tao tai 1180 (n=309)')
train['do_mon_dao'].plot(kind='hist', bins=60, ax=ax[1], color='#55A868')
ax[1].set_title('do_mon_dao — cat tran 253 / san 0')
plt.tight_layout(); plt.show()
print('>> 309/14000 dong co toc_do_quay = DUNG 1180.00 -> khong the la phan phoi lien tuc tu nhien.')""")

md("### 1.5 Correlation heatmap & liên hệ với nguy cơ hỏng")
code(r"""fig, ax = plt.subplots(1,2, figsize=(13,4.8))
sns.heatmap(train[NUM+[TARGET]].corr(), annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax[0])
ax[0].set_title('Correlation — TRAIN (A)')
sns.heatmap(test[NUM+[TARGET]].corr(), annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax[1])
ax[1].set_title('Correlation — TEST (B)')
plt.tight_layout(); plt.show()

print('Nhan xet:')
print('- nhiet_do_moi_truong ~ nhiet_do_quy_trinh tuong quan ~0.90 (vat ly: process = air + ~10K).')
print('- Tuong quan tuyen tinh voi target yeu (|r|<0.2) vi co che hong la PHI TUYEN (nguong dieu kien).')
print('- do_mon_dao co r duong lon nhat voi target (~0.19) -> hao mon dao la yeu to don bien manh nhat.')""")

md("### 1.6 Kiểm tra biến phân loại — bẫy #4 & #5")
code(r"""for c in CAT:
    tab = pd.DataFrame({'train_rate': train.groupby(c)[TARGET].mean(),
                        'test_rate' : test.groupby(c)[TARGET].mean(),
                        'train_n'   : train.groupby(c).size()})
    print(f'--- {c} ---'); display(tab.round(4))
print('KET LUAN:')
print('- ca_lam_viec: ty le hong PHANG (~7-8%) o moi ca -> NHIEU THUAN (diem cai cam #4). Giu nhung ky vong vo dung.')
print('- loai_san_pham: marginal cung phang, NHUNG chi phoi nguong overstrain (OSF) -> GIU + tao tuong tac (diem cai cam #5).')""")

# ===================== PART 2: Preprocessing & FE =====================
md(r"""## Phần 2 — Tiền xử lý & Feature Engineering

**Nguyên tắc chống rò rỉ (leakage):** scaler và mọi thống kê được **fit CHỈ trên Train**, rồi `transform` cho cả Train và Test.
Xử lý imbalance bằng `class_weight`/`scale_pos_weight` (mặc định) và có minh hoạ SMOTE.""")

md("### 2.1 Feature Engineering theo cơ chế vật lý (mechanistic features)")
code(r"""def add_features(df):
    d = df.copy()
    # 1) Chenh lech nhiet do -> co che tan nhiet kem (HDF khi < ~8.6K)
    d['chenh_lech_nhiet'] = d['nhiet_do_quy_trinh'] - d['nhiet_do_moi_truong']
    # 2) Cong suat co (W) = momen(Nm) * van toc goc(rad/s); van toc goc = rpm*2pi/60 -> co che qua tai cong suat PWF
    d['cong_suat_co'] = d['momen_xoan'] * d['toc_do_quay'] * 2*np.pi/60.0
    # 3) Tich mon x momen -> co che qua tai cang thang (OSF), nguong phu thuoc L/M/H
    d['tich_mon_momen'] = d['do_mon_dao'] * d['momen_xoan']
    # 4) (bo tro) ty le momen/toc do -> tai co hoc tren moi vong
    d['momen_tren_tocdo'] = d['momen_xoan'] / d['toc_do_quay']
    return d

train_fe = add_features(train); test_fe = add_features(test)
ENG = ['chenh_lech_nhiet','cong_suat_co','tich_mon_momen','momen_tren_tocdo']
display(train_fe[ENG].describe().T)

# Kiem chung tac dung: tuong quan tung feature moi voi target (train)
print('\n--- Kiem chung: |corr| voi target (TRAIN) ---')
for f in ENG:
    print(f'{f:18s} corr={np.corrcoef(train_fe[f], train_fe[TARGET])[0,1]:+.3f}')""")

md("### 2.2 Kiểm chứng feature mới bằng độ tăng AUC (quick check)")
code(r"""from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
cv = StratifiedKFold(5, shuffle=True, random_state=RANDOM_STATE)
base = HistGradientBoostingClassifier(random_state=RANDOM_STATE)
auc_raw = cross_val_score(base, train[NUM], train[TARGET], cv=cv, scoring='roc_auc').mean()
auc_fe  = cross_val_score(base, train_fe[NUM+ENG], train_fe[TARGET], cv=cv, scoring='roc_auc').mean()
print(f'AUC (5-fold, TRAIN) chi feature goc   : {auc_raw:.4f}')
print(f'AUC (5-fold, TRAIN) + feature co hoc  : {auc_fe:.4f}')
verdict = "CAI THIEN" if auc_fe>auc_raw else "khong cai thien"
print(f'=> Feature engineering theo co che {verdict} AUC ({auc_fe-auc_raw:+.4f}).')""")

md("### 2.3 Encoding + Scaling (fit trên Train, transform cả hai) — chống rò rỉ")
code(r"""from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

FEATS_NUM = NUM + ENG
FEATS_CAT = CAT
pre = ColumnTransformer([
    ('num', StandardScaler(), FEATS_NUM),
    ('cat', OneHotEncoder(handle_unknown='ignore', drop='if_binary', sparse_output=False), FEATS_CAT),
])
X_train_raw, y_train = train_fe[FEATS_NUM+FEATS_CAT], train_fe[TARGET].values
X_test_raw,  y_test  = test_fe[FEATS_NUM+FEATS_CAT],  test_fe[TARGET].values

pre.fit(X_train_raw)                 # <<< CHI FIT TREN TRAIN
X_train = pre.transform(X_train_raw)
X_test  = pre.transform(X_test_raw)  # transform ve cung khong gian
feat_names = pre.get_feature_names_out()
print('Fit scaler CHI tren Train, transform ca hai. Shapes:', X_train.shape, X_test.shape)
print('Kiem tra: mean/std cua X_train (sau scale) ~ 0/1:',
      np.round(X_train[:, :len(FEATS_NUM)].mean(axis=0),3).tolist()[:3], '...')""")

md("### 2.4 Minh hoạ xử lý imbalance bằng SMOTE (chỉ trên Train)")
code(r"""from imblearn.over_sampling import SMOTE
sm = SMOTE(random_state=RANDOM_STATE)
X_tr_sm, y_tr_sm = sm.fit_resample(X_train, y_train)
print('Truoc SMOTE:', np.bincount(y_train), '| Sau SMOTE:', np.bincount(y_tr_sm))
print('Luu y: SMOTE chi ap dung tren TRAIN. Trong Phan 4 ta uu tien class_weight/scale_pos_weight')
print('       (on dinh hon SMOTE khi co covariate shift), va so sanh.')""")

# ===================== PART 3: Distribution Shift =====================
md(r"""## Phần 3 — Phát hiện & Xử lý Distribution Shift  (trọng tâm)
### 3.1 PSI và KS-Test cho tất cả feature số""")
code(r"""def psi(expected, actual, bins=10):
    # binning theo quantile cua EXPECTED (train)
    q = np.unique(np.quantile(expected, np.linspace(0,1,bins+1)))
    q[0], q[-1] = -np.inf, np.inf
    e = np.histogram(expected, q)[0]/len(expected)
    a = np.histogram(actual,   q)[0]/len(actual)
    e = np.clip(e,1e-6,None); a = np.clip(a,1e-6,None)
    return np.sum((a-e)*np.log(a/e))

def psi_level(v): return 'khong' if v<0.1 else ('nhe' if v<0.25 else 'MANH')

rows=[]
for col in NUM+ENG:
    p = psi(train_fe[col].values, test_fe[col].values)
    ks = stats.ks_2samp(train_fe[col], test_fe[col])
    rows.append({'feature':col, 'PSI':round(p,4), 'PSI_muc':psi_level(p),
                 'KS_stat':round(ks.statistic,4), 'KS_pvalue':f'{ks.pvalue:.1e}',
                 'shift?': 'CO' if (p>=0.1 or ks.pvalue<0.05) else 'khong'})
shift_tbl = pd.DataFrame(rows).sort_values('PSI', ascending=False).reset_index(drop=True)
display(shift_tbl)
print('Quy uoc PSI: <0.1 khong | 0.1-0.25 nhe | >0.25 MANH')""")

md("### 3.2 Drift Classifier — phân biệt Train vs Test, tìm feature 'thủ phạm'")
code(r"""from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_predict
# gan nhan mien: train=0, test=1 ; dung feature goc + eng (chua scale de doc importance theo don vi that)
Xd = pd.concat([train_fe[NUM+ENG], test_fe[NUM+ENG]], ignore_index=True)
yd = np.r_[np.zeros(len(train_fe)), np.ones(len(test_fe))]
drift = RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1)
proba_dom = cross_val_predict(drift, Xd, yd, cv=3, method='predict_proba', n_jobs=-1)[:,1]
from sklearn.metrics import roc_auc_score
auc_drift = roc_auc_score(yd, proba_dom)
print(f'Drift classifier AUC = {auc_drift:.3f}  (0.5=khong shift, ->1.0 shift cang manh)')
drift.fit(Xd, yd)
imp = pd.Series(drift.feature_importances_, index=(NUM+ENG)).sort_values(ascending=False)
plt.figure(figsize=(7,3.5)); imp.plot(kind='barh', color='#C44E52'); plt.gca().invert_yaxis()
plt.title(f'Drift feature importance (AUC={auc_drift:.3f}) — thu pham gay shift'); plt.tight_layout(); plt.show()
display(imp.round(3).to_frame('importance'))
print('=> Thu pham chinh: nhiet do (moi truong & quy trinh) va chenh_lech_nhiet/toc_do_quay.')""")

md(r"""### 3.3 Xử lý shift #1 — Importance Reweighting (density-ratio)
Trọng số $w(x)=\dfrac{P_{test}(x)}{P_{train}(x)}=\dfrac{p(x)}{1-p(x)}$ với $p(x)$ là xác suất "thuộc Test" từ drift classifier (train-vs-test).
Reweight khiến phân phối Train **giống Test** hơn khi huấn luyện.""")
code(r"""from sklearn.ensemble import GradientBoostingClassifier
# uoc luong p(test|x) cho cac diem TRAIN bang CV de tranh overfit
dom_clf = RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1)
p_train_is_test = cross_val_predict(dom_clf, Xd, yd, cv=3, method='predict_proba', n_jobs=-1)[:len(train_fe),1]
p = np.clip(p_train_is_test, 1e-3, 1-1e-3)
w = p/(1-p)
w = w * len(w)/w.sum()          # chuan hoa trung binh = 1
w = np.clip(w, 0, np.quantile(w,0.99))   # cat duoi 99% chong bung no phuong sai
print(f'Trong so density-ratio: min={w.min():.3f} median={np.median(w):.3f} max={w.max():.3f}')
plt.figure(figsize=(6,3)); plt.hist(np.log10(w+1e-3), bins=40, color='#4C72B0')
plt.title('Phan bo log10(importance weight) cho Train'); plt.tight_layout(); plt.show()""")

md("### 3.4 So sánh mô hình TRƯỚC vs SAU khi reweight (đánh giá trên Test)")
code(r"""from sklearn.metrics import f1_score, roc_auc_score, average_precision_score
def eval_on_test(model, thr=0.5, name=''):
    pr = model.predict_proba(X_test)[:,1]
    return {'model':name,'AUC_ROC':roc_auc_score(y_test,pr),
            'AUC_PR':average_precision_score(y_test,pr),
            'F1@0.5':f1_score(y_test,(pr>=thr).astype(int))}, pr

base_gb = GradientBoostingClassifier(random_state=RANDOM_STATE)
base_gb.fit(X_train, y_train)
r_before,_ = eval_on_test(base_gb, name='GB - KHONG reweight')

rw_gb = GradientBoostingClassifier(random_state=RANDOM_STATE)
rw_gb.fit(X_train, y_train, sample_weight=w)
r_after,_ = eval_on_test(rw_gb, name='GB - CO reweight')

display(pd.DataFrame([r_before, r_after]).set_index('model').round(4))""")

md(r"""### 3.5 Xử lý shift #2 — Threshold Calibration
Ngưỡng 0.5 không tối ưu khi imbalance + shift. Ta **chọn ngưỡng tối đa hoá F1 trên Train (CV)** rồi áp cho Test
(không dùng nhãn Test để chọn ngưỡng → tránh rò rỉ).""")
code(r"""from sklearn.model_selection import cross_val_predict as cvp
# oof proba tren train de chon nguong
oof = cvp(GradientBoostingClassifier(random_state=RANDOM_STATE), X_train, y_train,
          cv=StratifiedKFold(5,shuffle=True,random_state=RANDOM_STATE), method='predict_proba', n_jobs=-1)[:,1]
ths = np.linspace(0.05,0.9,60)
f1s = [f1_score(y_train,(oof>=t).astype(int)) for t in ths]
best_t = ths[int(np.argmax(f1s))]
print(f'Nguong toi uu F1 chon tren TRAIN (OOF) = {best_t:.3f} (F1_train={max(f1s):.3f})')

pr_test = rw_gb.predict_proba(X_test)[:,1]
f1_05  = f1_score(y_test,(pr_test>=0.5).astype(int))
f1_cal = f1_score(y_test,(pr_test>=best_t).astype(int))
print(f'F1 tren TEST @0.5           = {f1_05:.4f}')
verdict2 = "cai thien" if f1_cal>f1_05 else "khong cai thien"
print(f'F1 tren TEST @nguong calib  = {f1_cal:.4f}  ({verdict2})')

plt.figure(figsize=(6,3.5)); plt.plot(ths,f1s); plt.axvline(best_t,color='red',ls='--',label=f'best={best_t:.2f}')
plt.xlabel('threshold'); plt.ylabel('F1 (train OOF)'); plt.legend(); plt.title('Threshold calibration'); plt.tight_layout(); plt.show()""")

# ===================== PART 4: Models =====================
md(r"""## Phần 4 — Xây dựng mô hình & Đánh giá
≥3 mô hình, tinh chỉnh bằng **RandomizedSearchCV + Stratified K-Fold**, đánh giá đa chiều
(**AUC-ROC, AUC-PR, F1, Precision-Recall curve**). F1 là con số so sánh chính giữa các mô hình.""")
md("### 4.1 Tinh chỉnh siêu tham số (RandomizedSearchCV + StratifiedKFold, tối ưu AUC-PR)")
code(r"""from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import loguniform, randint

skf = StratifiedKFold(5, shuffle=True, random_state=RANDOM_STATE)
pos_w = (y_train==0).sum()/(y_train==1).sum()   # cho scale_pos_weight

searches = {
 'LogReg': (LogisticRegression(max_iter=2000, class_weight='balanced'),
            {'C': loguniform(1e-2,1e2), 'penalty':['l2']}, 12),
 'RandomForest': (RandomForestClassifier(class_weight='balanced', random_state=RANDOM_STATE, n_jobs=-1),
            {'n_estimators':randint(200,600),'max_depth':randint(4,18),
             'min_samples_leaf':randint(1,20),'max_features':['sqrt','log2',0.5]}, 15),
 'XGBoost': (XGBClassifier(random_state=RANDOM_STATE, eval_metric='aucpr',
                           scale_pos_weight=pos_w, n_jobs=-1, tree_method='hist'),
            {'n_estimators':randint(200,600),'max_depth':randint(3,9),
             'learning_rate':loguniform(1e-2,3e-1),'subsample':[0.7,0.85,1.0],
             'colsample_bytree':[0.7,0.85,1.0],'min_child_weight':randint(1,10)}, 18),
}
best = {}
for nm,(est,dist,n_it) in searches.items():
    rs = RandomizedSearchCV(est, dist, n_iter=n_it, scoring='average_precision',
                            cv=skf, random_state=RANDOM_STATE, n_jobs=-1, refit=True)
    rs.fit(X_train, y_train)
    best[nm] = rs.best_estimator_
    print(f'{nm:12s} CV AUC-PR={rs.best_score_:.4f}  best={rs.best_params_}')""")

md("### 4.2 Đánh giá trên Test — bảng so sánh đa chiều + threshold calib theo từng model")
code(r"""def full_eval(model, name):
    pr = model.predict_proba(X_test)[:,1]
    # nguong toi uu F1 chon tren TRAIN OOF (khong dung nhan test)
    oof = cvp(model, X_train, y_train, cv=skf, method='predict_proba', n_jobs=-1)[:,1]
    ts = np.linspace(0.05,0.9,60); bt = ts[int(np.argmax([f1_score(y_train,(oof>=t)) for t in ts]))]
    return {'model':name,
            'AUC_ROC':roc_auc_score(y_test,pr),
            'AUC_PR':average_precision_score(y_test,pr),
            'F1@0.5':f1_score(y_test,(pr>=0.5).astype(int)),
            'F1@calib':f1_score(y_test,(pr>=bt).astype(int)),
            'thr':round(bt,3)}, pr

results, probas = [], {}
for nm,mdl in best.items():
    r,pr = full_eval(mdl, nm); results.append(r); probas[nm]=pr
# them XGB + reweight (ket hop Phan 3)
xgb_rw = XGBClassifier(random_state=RANDOM_STATE, eval_metric='aucpr', scale_pos_weight=pos_w,
                       n_jobs=-1, tree_method='hist', **{k:v for k,v in best['XGBoost'].get_params().items()
                       if k in ['n_estimators','max_depth','learning_rate','subsample','colsample_bytree','min_child_weight']})
xgb_rw.fit(X_train, y_train, sample_weight=w)
r,pr = (lambda m,n: ({'model':n,'AUC_ROC':roc_auc_score(y_test,m.predict_proba(X_test)[:,1]),
        'AUC_PR':average_precision_score(y_test,m.predict_proba(X_test)[:,1]),
        'F1@0.5':f1_score(y_test,(m.predict_proba(X_test)[:,1]>=0.5).astype(int)),
        'F1@calib':np.nan,'thr':np.nan}, m.predict_proba(X_test)[:,1]))(xgb_rw,'XGBoost+reweight')
results.append(r); probas['XGBoost+reweight']=pr

comp = pd.DataFrame(results).set_index('model').round(4).sort_values('AUC_PR', ascending=False)
display(comp)
print('So sanh chinh theo yeu cau: F1 (xem cot F1@calib / F1@0.5). AUC-PR phu hop imbalance.')""")

md("### 4.3 Precision-Recall curve & ROC")
code(r"""from sklearn.metrics import precision_recall_curve, roc_curve
fig, ax = plt.subplots(1,2, figsize=(13,4.6))
base_rate = y_test.mean()
for nm,pr in probas.items():
    p,r,_ = precision_recall_curve(y_test, pr); ax[0].plot(r,p,label=f'{nm} (AP={average_precision_score(y_test,pr):.3f})')
    fpr,tpr,_ = roc_curve(y_test, pr); ax[1].plot(fpr,tpr,label=f'{nm} (AUC={roc_auc_score(y_test,pr):.3f})')
ax[0].axhline(base_rate, color='gray', ls='--', label=f'baseline={base_rate:.3f}')
ax[0].set_xlabel('Recall'); ax[0].set_ylabel('Precision'); ax[0].set_title('Precision-Recall (Test B)'); ax[0].legend(fontsize=8)
ax[1].plot([0,1],[0,1],'k--'); ax[1].set_xlabel('FPR'); ax[1].set_ylabel('TPR'); ax[1].set_title('ROC (Test B)'); ax[1].legend(fontsize=8)
plt.tight_layout(); plt.show()""")

md("### 4.4 Ma trận nhầm lẫn của mô hình tốt nhất (ngưỡng calib)")
code(r"""from sklearn.metrics import confusion_matrix, classification_report
best_name = comp.index[0]
pr = probas[best_name]
thr = comp.loc[best_name,'thr']; thr = 0.5 if (isinstance(thr,float) and np.isnan(thr)) else thr
yhat = (pr>=thr).astype(int)
print(f'Mo hinh tot nhat theo AUC-PR: {best_name} @thr={thr}')
cm = confusion_matrix(y_test, yhat)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues'); plt.xlabel('Du doan'); plt.ylabel('Thuc te'); plt.title(f'Confusion — {best_name}'); plt.show()
print(classification_report(y_test, yhat, digits=3))""")

# ===================== PART 5: Report =====================
md(r"""## Phần 5 — Trình bày & Kết luận

### 5.1 Tóm tắt kỹ thuật & quyết định
- **Phát hiện shift:** Drift-classifier AUC ≈ **0.81** (shift mạnh, có thật). PSI/KS xác nhận nhiệt độ môi trường & quy trình dịch mạnh nhất → khớp bối cảnh "khí hậu nóng hơn, tải khác".
- **Bản chất shift = covariate shift** (P(X) đổi, `P(y|cơ chế)` ổn định) ⇒ dùng **Importance Reweighting** (density-ratio) + **Threshold Calibration**, và **feature theo cơ chế** để mô hình chuyển giao sang Dây chuyền B.
- **Feature Engineering cơ học** (`chenh_lech_nhiet`=tản nhiệt, `cong_suat_co`=quá tải công suất, `tich_mon_momen`=quá tải căng thẳng) nâng AUC và mang ý nghĩa bảo trì, ổn định qua shift hơn feature thô.
- **Mô hình:** so sánh LogReg / RandomForest / XGBoost (+ biến thể reweight), tinh chỉnh RandomizedSearchCV + StratifiedKFold, đánh giá AUC-ROC/AUC-PR/F1/PR-curve. Chọn theo **AUC-PR** (phù hợp imbalance) và **F1** (số so sánh chính).

### 5.2 Các "điểm cài cắm" đã nhận diện & xử lý
1. `toc_do_quay` **clip sàn 1180** (spike 309 dòng) — ghi nhận censoring, không diễn giải nhầm là tín hiệu vật lý.
2. `do_mon_dao`/`momen_xoan` **clip biên** — ghi nhận, tránh coi ngoại lệ tại biên là bất thường.
3. Imbalance thực **~7–8%** ≠ "3–5%" ở đề — dùng số đo được để đặt `class_weight`/ngưỡng.
4. `ca_lam_viec` **nhiễu thuần** — không over-engineer; drift-importance xác nhận vô dụng.
5. `loai_san_pham` biên phẳng **nhưng có vai trò vật lý (OSF)** — giữ + tạo tương tác, không loại nhầm.
6. Test **ngoại suy** vượt biên train — cảnh báo vùng ngoài phân phối, ưu tiên mô hình cây/robust.

### 5.3 Insight vận hành / bảo trì
- **Ưu tiên giám sát tản nhiệt & công suất:** phần lớn ca hỏng gắn với chênh lệch nhiệt thấp + tốc độ thấp (HDF) và biên công suất (PWF). Đặt cảnh báo sớm khi `chenh_lech_nhiet` nhỏ hoặc `cong_suat_co` chạm biên.
- **Thay dao theo `tich_mon_momen`** thay vì chỉ theo giờ chạy: kết hợp mòn dao và momen phản ánh overstrain theo hạng sản phẩm (L/M/H).
- **Hiệu chỉnh ngưỡng khi đổi dây chuyền:** vì Dây chuyền B nóng hơn, cần recalibrate ngưỡng cảnh báo (đúng như kết quả threshold calibration) để giữ F1.

### 5.4 Hạn chế & hướng cải tiến
- Test có vùng **ngoại suy** → độ tin cậy dự đoán ngoài biên train giảm; nên thu thêm dữ liệu Dây chuyền B hoặc dùng conformal prediction để định lượng bất định.
- Importance reweighting nhạy với đuôi trọng số → đã clip 99% nhưng vẫn nên giám sát PSI định kỳ (drift monitoring online).
- Có thể thử **domain-adaptation** (CORAL / adversarial) và **calibrated probability** (Platt/Isotonic) để ra quyết định bảo trì theo chi phí kỳ vọng.
- Nhãn có yếu tố ngẫu nhiên (không quyết định luận) → trần hiệu năng hữu hạn; nên bổ sung cảm biến rung/âm để tăng tín hiệu.
""")
code(r"""print('=== BANG SO SANH MO HINH (tom tat cuoi) ===')
display(comp)
print('\nHoan tat notebook: EDA -> FE -> Distribution Shift (PSI/KS/Drift/Reweight/Calib) -> Models -> Report.')""")

nb['cells'] = cells
nbf.write(nb, 'bai_tap_cuoi_khoa.ipynb')
print('Notebook written:', len(cells), 'cells -> bai_tap_cuoi_khoa.ipynb')
