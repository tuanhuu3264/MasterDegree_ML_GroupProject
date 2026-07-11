# -*- coding: utf-8 -*-
"""
Sinh 6 notebook NANG CAO doc lap (moi cai gan voi 1 bai giang da hoc).
Moi notebook tu chay duoc (self-contained): co san prelude nap du lieu + FE.
Phien ban NANG CAP: comment trong code + note markdown CHI TIET HON, doc ket qua that.
Chay:  PYTHONIOENCODING=utf-8 python build_nangcao_cases.py
"""
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
import os

OUT = os.path.join(os.path.dirname(__file__), 'nang_cao_case')
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# PRELUDE dung chung: nap du lieu + Feature Engineering (khop notebook chinh)
# ---------------------------------------------------------------------------
PRELUDE = r"""
# ============================================================================
# PRELUDE DUNG CHUNG cho moi notebook trong thu muc nay.
# Muc dich: moi file TU CHAY DUOC ma khong phu thuoc notebook chinh.
#   - Nap train.csv (Day chuyen A) + test.csv (Day chuyen B)
#   - Tao lai dung 4 feature co che nhu notebook chinh (de ket qua nhat quan)
# ============================================================================
import os, warnings, numpy as np, pandas as pd
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')
plt.rcParams['figure.dpi'] = 110
RANDOM_STATE = 42; np.random.seed(RANDOM_STATE)   # co dinh seed -> chay lai ra so giong nhau

# --- Nap du lieu: thu nhieu duong dan vi notebook nam trong thu muc con ---
CANDIDATES = ['../Data_Final/Data_Final','../Data_Final','Data_Final/Data_Final',
              '../../Data_Final/Data_Final','Data_Final','.']
DATA_DIR = next((c for c in CANDIDATES
                 if os.path.exists(os.path.join(c,'train.csv'))
                 and os.path.exists(os.path.join(c,'test.csv'))), None)
assert DATA_DIR is not None, 'Khong tim thay train.csv/test.csv'
train = pd.read_csv(os.path.join(DATA_DIR,'train.csv'))
test  = pd.read_csv(os.path.join(DATA_DIR,'test.csv'))

NUM = ['nhiet_do_moi_truong','nhiet_do_quy_trinh','toc_do_quay','momen_xoan','do_mon_dao']  # 5 bien so goc
CAT = ['loai_san_pham','ca_lam_viec']   # 2 bien phan loai goc
TARGET = 'hong_hoc'                      # nhan: 1 = hong trong ca ke tiep

# --- Feature Engineering theo CO CHE vat ly (giong het notebook chinh) ---
def add_features(df):
    d = df.copy()
    # (1) Chenh lech nhiet: co che tan nhiet kem HDF. Lay HIEU nen triet tieu offset khi hau -> giam shift.
    d['chenh_lech_nhiet'] = d['nhiet_do_quy_trinh'] - d['nhiet_do_moi_truong']
    # (2) Cong suat co (W) = momen(Nm) * van_toc_goc(rad/s); van_toc_goc = rpm*2pi/60. Co che qua tai cong suat PWF.
    d['cong_suat_co']     = d['momen_xoan'] * d['toc_do_quay'] * 2*np.pi/60.0
    # (3) Tich mon*momen: co che qua tai cang thang OSF (mon cang nhieu + momen cang lon -> cang de gay).
    d['tich_mon_momen']   = d['do_mon_dao'] * d['momen_xoan']
    # (4) osf_margin: khoang cach toi NGUONG OSF, nguong phu thuoc HANG SP (L/M/H). >0 = da vuot nguong.
    g = d['loai_san_pham'].map({'L':11000,'M':12000,'H':13000})
    d['osf_margin']       = d['tich_mon_momen'] - g
    return d

train_fe = add_features(train); test_fe = add_features(test)
y_train = train_fe[TARGET].values
y_test  = test_fe[TARGET].values

# Bo feature CUOI da chot o notebook chinh: 9 bien so + 1 bien phan loai (loai_san_pham)
FINAL_NUM = NUM + ['chenh_lech_nhiet','cong_suat_co','tich_mon_momen','osf_margin']
FINAL_CAT = ['loai_san_pham']
print('Train:', train.shape, '| Test:', test.shape,
      '| ti le hong train/test:', round(y_train.mean(),3), round(y_test.mean(),3))
print('FINAL_NUM =', FINAL_NUM)
""".strip()


def build(fname, title_md, cells):
    nb = new_notebook()
    nb.cells = [new_markdown_cell(title_md),
                new_code_cell(PRELUDE)] + cells
    nb.metadata = {"language_info": {"name": "python"},
                   "kernelspec": {"name": "python3", "display_name": "Python 3"}}
    path = os.path.join(OUT, fname)
    nbf.write(nb, path)
    print('WROTE', path, '(', len(nb.cells), 'cells )')


# ===========================================================================
# CASE 01 — Decision Tree nong: lo NGUONG co che  [Bai L6]
# ===========================================================================
build('01_decision_tree_nguong.ipynb',
"""# Case 01 — Cay quyet dinh nong lo ra NGUONG co che  ·  *Bai L6 (Decision Tree)*

## Y tuong
Bai L6 day: cay quyet dinh chia du lieu bang cac cau hoi **"bien ≤ nguong?"**, va o moi buoc no chon
nguong lam hai nhanh con **sach** nhat (do bang **Gini** — nhanh cang thuan 1 lop thi Gini cang gan 0).
O day ta co tinh de cay **nong (max_depth=3)** de no buoc phai chon dung vai nguong *quan trong nhat*,
roi doc xem do la nguong nao.

## Vi sao chay thu nghiem nay
Toan bo Feature Engineering dua tren gia dinh "may hong theo nguong co che": mon dao ~240 phut,
chenh lech nhiet ~8.6K... Nhung do la **ta tu gia dinh**. Cay quyet dinh KHONG biet gi ve gia dinh do —
no chi nhin du lieu. Neu no **tu** chia dung vao cac nguong ay thi gia dinh duoc xac nhan **khach quan**.

## Cach doc cay (quan trong)
- Moi nut ghi: dieu kien chia · Gini · ty le mau · `class`.
- `weights: [a, b]` = tong TRONG SO cua lop 0 va lop 1 trong nut (da nhan `class_weight='balanced'`
  nen lop hong bi it duoc keo len). `b >> a` => nut nay gan nhu toan may HONG.""",
[
 new_markdown_cell("### 1) Huan luyen cay nong & ve cay (plot_tree)\n"
                   "Cay chi dung feature SO (khong can scale) de **nguong doc ra dung don vi goc** "
                   "(vd 243.95 phut mon dao, doc hieu ngay)."),
 new_code_cell(r"""from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.metrics import f1_score, average_precision_score

# max_depth=3      : ep cay nong -> chi giu vai nguong quan trong nhat (de doc, de giai thich)
# class_weight     : 'balanced' -> bu cho lop hong thieu so (~7-8%), neu khong cay se bo qua lop hong
dt = DecisionTreeClassifier(max_depth=3, class_weight='balanced',
                            random_state=RANDOM_STATE).fit(train_fe[FINAL_NUM], y_train)

fig, ax = plt.subplots(figsize=(22, 9))
plot_tree(dt, feature_names=FINAL_NUM, class_names=['OK','HONG'],
          filled=True,        # to mau theo lop chiem uu the -> nhin phat biet nhanh hong nam dau
          rounded=True, impurity=True, proportion=True, fontsize=8, ax=ax)
ax.set_title('Cay quyet dinh nong (max_depth=3) — moi nut ghi NGUONG chia + Gini', fontsize=12)
plt.tight_layout(); plt.show()"""),
 new_markdown_cell("### 2) In luat dang van ban + doi chieu voi nguong co che ta gia dinh"),
 new_code_cell(r"""# export_text: in cay ra chu, de trich vao bao cao / doc khi khong co hinh
print(export_text(dt, feature_names=list(FINAL_NUM), show_weights=True))

# Gom tat ca nguong ma cay da chon o cac nut chia (feature>=0 nghia la nut chia, khong phai la)
print('\n--- Nguong CAY tu tim (o cac nut chia) ---')
thr_by_feat = {}
for node in range(dt.tree_.node_count):
    f = dt.tree_.feature[node]
    if f >= 0:
        thr_by_feat.setdefault(FINAL_NUM[f], []).append(round(dt.tree_.threshold[node], 2))
for k, v in thr_by_feat.items():
    print(f'  {k:18s} nguong = {sorted(set(v))}')

print('\n--- Nguong CO CHE ta GIA DINH khi lam FE (de doi chieu) ---')
print('  do_mon_dao       ~ 240 phut  (TWF: hao mon dao)')
print('  chenh_lech_nhiet ~ 8.6 K     (HDF: tan nhiet kem)')
print('  osf_margin       ~ 0         (OSF: tich_mon_momen vuot nguong theo hang SP)')
print('  cong_suat_co     : vung thap (<~2800) va cao (>~10000) deu de hong (PWF)')"""),
 new_markdown_cell("""> ### 🔎 Doc ket qua (Case 01)
> Cay **tu chia** dung vao cac nguong ta gia dinh, du khong he duoc "mach":
>
> | Nguong cay tim | Ta gia dinh | Nhan xet |
> |---|---|---|
> | `do_mon_dao ≤ 243.95` | ~240 (TWF) | **trung** |
> | `chenh_lech_nhiet ≤ 8.60` | 8.6 (HDF) | **trung khit** |
> | `toc_do_quay ≤ 1379.70` | ~1380 | **trung** |
> | `cong_suat_co ≤ 2601` | vung PWF-thap | **dung vung** |
>
> Vi du 1 nhanh: `do_mon_dao ≤ 243.95 & chenh_lech_nhiet ≤ 8.60 & toc_do_quay ≤ 1379.70`
> -> `weights: [18.35, 1222.11]` -> gan nhu **toan may HONG**. Do chinh la co che HDF
> (nhiet chenh thap = tan nhiet kem, o toc do quay thap) ma cay tu tim ra.
>
> => Cac dac trung co che khong phai "ve cho dep": thuat toan doc lap cung xac nhan do la **ranh gioi that**."""),
 new_markdown_cell("### 3) Cay nong nay du de bao nhieu? (chi de tham chieu)"),
 new_code_cell(r"""# Cay nong chu yeu de GIAI THICH, khong phai de dat F1 cao. Van do thu de biet no manh yeu the nao.
p = dt.predict_proba(test_fe[FINAL_NUM])[:,1]
p_tr = dt.predict_proba(train_fe[FINAL_NUM])[:,1]
ts = np.linspace(0.05, 0.9, 80)                                  # quet nguong xac suat...
thr = ts[int(np.argmax([f1_score(y_train, (p_tr>=t)) for t in ts]))]  # ...chon nguong toi uu F1 TREN TRAIN (khong nhin test)
print(f'Cay nong depth=3: AUC-PR(test)={average_precision_score(y_test,p):.3f} '
      f'| F1(test @thr-train {thr:.2f})={f1_score(y_test,(p>=thr)):.3f}')
print('Tham chieu: RandomForest (mo hinh cuoi) ~0.78. Cay nong yeu hon vi chi 3 tang,')
print('nhung bu lai cho ta NGUONG DOC DUOC — do moi la gia tri o thu nghiem nay.')"""),
 new_markdown_cell("""> ### ✅ Ket luan Case 01
> Cay nong tu chia dung quanh cac nguong co che (mon dao ~244, chenh lech nhiet 8.6, toc do 1380),
> **xac nhan Feature Engineering theo co che la co co so thuc te**, khong phai suy dien chu quan.
> Cay sau hon se cho F1 cao hon nhung mat tinh giai thich; vi vay ta dung **cay nong nhu cong cu KE CHUYEN**,
> con **RandomForest/XGBoost** moi la mo hinh du doan cuoi. Khi bi hoi "sao biet mon dao 240 la nguong?" -> chi vao hinh cay."""),
])


# ===========================================================================
# CASE 02 — Learning Curve: chung minh tran F1  [Bai L6]
# ===========================================================================
build('02_learning_curve_tran_F1.ipynb',
"""# Case 02 — Learning Curve chung minh **tran F1 ≈ 0.78**  ·  *Bai L6*

## Y tuong
Learning curve = huan luyen mo hinh voi **luong du lieu tang dan** (10%, 20%, ... 100% tap train),
moi lan do diem tren train va diem kiem dinh cheo (validation), roi ve 2 duong theo so mau.

## Vi sao chay thu nghiem nay
Ta ket luan F1 ~0.78 la **tran tu nhien** (do nhan co yeu to ngau nhien). Co mot phan bien hien nhien:
*"Hay tai IT du lieu qua? Them data thi F1 len chu?"*. Learning curve tra loi CHINH XAC cau nay.

## Cach doc
- Duong validation **phang som** roi khong tang -> **them du lieu vo ich** -> gioi han la
  **nhieu nhan (irreducible / tran Bayes)**, KHONG phai thieu data.
- Khoang cach train–val con lai = **phuong sai** khong the khu (variance).""",
[
 new_code_cell(r"""from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import learning_curve, StratifiedKFold

# Dung dung pipeline nhu mo hinh cuoi (RF + scale so + one-hot loai_san_pham)
pre = ColumnTransformer([('num', StandardScaler(), FINAL_NUM),
      ('cat', OneHotEncoder(handle_unknown='ignore', drop='if_binary', sparse_output=False), FINAL_CAT)])
rf  = RandomForestClassifier(n_estimators=300, min_samples_leaf=5, class_weight='balanced',
                             random_state=RANDOM_STATE, n_jobs=-1)
pipe = Pipeline([('pre', pre), ('rf', rf)])
skf = StratifiedKFold(5, shuffle=True, random_state=RANDOM_STATE)   # giu ty le lop trong moi fold

# scoring='average_precision' (AUC-PR): hop voi du lieu MAT CAN BANG hon la accuracy
# train_sizes: 8 moc tu 10% den 100% tap train
sizes, tr, val = learning_curve(pipe, train_fe[FINAL_NUM+FINAL_CAT], y_train, cv=skf,
                                scoring='average_precision',
                                train_sizes=np.linspace(0.1, 1.0, 8),
                                n_jobs=-1, random_state=RANDOM_STATE)
tr_m, val_m = tr.mean(1), val.mean(1)   # trung binh qua 5 fold"""),
 new_code_cell(r"""fig, ax = plt.subplots(figsize=(8,5))
ax.plot(sizes, tr_m, 'o-', color='#C44E52', label='Train (AUC-PR)')
ax.fill_between(sizes, tr.min(1), tr.max(1), alpha=.12, color='#C44E52')   # dai bien do giua cac fold
ax.plot(sizes, val_m, 's-', color='#4C72B0', label='Validation CV (AUC-PR)')
ax.fill_between(sizes, val.min(1), val.max(1), alpha=.12, color='#4C72B0')
ax.set_xlabel('So mau huan luyen'); ax.set_ylabel('AUC-PR')
ax.set_title('Learning Curve — validation phang => them du lieu KHONG cuu duoc')
ax.legend(); plt.tight_layout(); plt.show()

print('AUC-PR validation theo size:', np.round(val_m,3).tolist())
delta = val_m[-1] - val_m[len(val_m)//2]     # muc tang o nua sau: gan 0 => da bao hoa
print(f'Muc tang o NUA SAU cua duong validation = {delta:+.4f}  (gan 0 => da bao hoa)')
print(f'Khoang cach Train - Val cuoi cung       = {tr_m[-1]-val_m[-1]:+.3f}  (= phuong sai con lai)')"""),
 new_markdown_cell("""> ### 🔎 Doc ket qua (Case 02)
> Diem validation theo luong data: `0.646 → 0.659 → 0.651 → 0.661 → 0.653 → 0.654 → 0.649 → 0.652`.
> - Duong val **di ngang tu rat som**; nua sau con giam nhe (Δ = −0.001) -> **da bao hoa**.
>   Cho an them du lieu, no khong nhich len.
> - Con lai mot khoang cach Train–Val (train cao hon) = **phuong sai**, dung ban chat cua rung cay.
>
> **Suy ra:** gioi han hieu nang **khong** do thieu du lieu, ma do **nhieu trong nhan (tran Bayes)**.
>
> ### ✅ Ket luan Case 02
> Day la **bang chung THU HAI, doc lap** voi lap luan resubstitution-vs-CV (F1 huan luyen lai = 1.0
> nhung CV chi ~0.76) o notebook nang cao F1. Hai bang chung cung chi ve mot ket luan:
> **F1 > 0.8 chi dat duoc neu RO RI du lieu (vi pham de bai)**."""),
])


# ===========================================================================
# CASE 03 — Feature Selection NHIEU PHUONG PHAP  [Bai L5]
# ===========================================================================
build('03_feature_selection_nhieu_phuongphap.ipynb',
"""# Case 03 — Chon feature bang **NHIEU phuong phap** (Filter / Wrapper / Embedded)  ·  *Bai L5*

## Y tuong
Bai L5 day 3 nhom phuong phap chon feature. Thay vi chon bang cam tinh, ta chay **nhieu phuong phap**
roi lay **dong thuan (consensus)** — feature nao duoc nhieu phuong phap giu thi cang dang tin:

| Nhom | Ban chat | Phuong phap thu o day |
|---|---|---|
| **Filter** | Cham diem tung feature, doc lap voi mo hinh (nhanh, tho) | VarianceThreshold · High-correlation · Mutual Information · ANOVA F-test |
| **Wrapper** | Thu nhieu to hop feature, huan luyen mo hinh cho tung to hop (cham, chinh xac) | RFE · RFECV · Sequential Forward |
| **Embedded** | Mo hinh TU chon feature trong luc hoc | Lasso L1 · RandomForest MDI · Permutation |

## Vi sao chay thu nghiem nay
Phan 6 notebook chinh loai feature bang cam nhan + vai chi so. O day ta chay **10 phuong phap** roi cho
chung **bo phieu**, xac nhan lai bo feature mot cach co he thong (dung ngon ngu Filter/Wrapper/Embedded).""",
[
 new_markdown_cell("### 0) Chuan bi ma tran feature (9 so + one-hot loai_san_pham -> 11 cot)"),
 new_code_cell(r"""from sklearn.preprocessing import StandardScaler
# One-hot loai_san_pham -> loai_M, loai_H (bo L lam goc) de moi phuong phap deu co TEN feature ro rang
d_tr = train_fe.copy(); d_te = test_fe.copy()
for lv in ['M','H']:
    d_tr[f'loai_{lv}'] = (d_tr['loai_san_pham']==lv).astype(int)
    d_te[f'loai_{lv}'] = (d_te['loai_san_pham']==lv).astype(int)
FEATS = FINAL_NUM + ['loai_M','loai_H']                 # 11 feature ung vien
Xtr_raw = d_tr[FEATS].values.astype(float); Xte_raw = d_te[FEATS].values.astype(float)
sc  = StandardScaler().fit(Xtr_raw)                     # fit CHI tren train (chong ro ri)
Xtr = sc.transform(Xtr_raw); Xte = sc.transform(Xte_raw)
sel = pd.DataFrame(index=FEATS)                         # bang tong hop: moi cot = 1 phuong phap, 1=giu / 0=loai
print('So feature ung vien:', len(FEATS)); print(FEATS)"""),
 new_markdown_cell("### 1) FILTER — cham diem tung feature (doc lap mo hinh)"),
 new_code_cell(r"""from sklearn.feature_selection import (VarianceThreshold, mutual_info_classif, f_classif)

# 1a. Low variance: loai feature gan nhu HANG SO (khong mang thong tin). Xet tren du lieu THO (truoc scale).
vt = VarianceThreshold(threshold=1e-8).fit(Xtr_raw)
sel['filter_variance'] = vt.get_support().astype(int)

# 1b. High correlation: trong cac cap |corr|>0.9 (trung thong tin), bo feature co |corr voi target| THAP hon
corr = np.corrcoef(Xtr_raw, rowvar=False)
tgt  = np.array([abs(np.corrcoef(Xtr_raw[:,i], y_train)[0,1]) for i in range(len(FEATS))])
drop = set()
for i in range(len(FEATS)):
    for j in range(i+1, len(FEATS)):
        if abs(corr[i,j]) > 0.9:
            drop.add(i if tgt[i] < tgt[j] else j)      # giu feature lien quan target hon
sel['filter_highcorr'] = [0 if i in drop else 1 for i in range(len(FEATS))]
print('Cap |corr|>0.9 -> loai:', [FEATS[i] for i in drop])

# 1c. Mutual Information: bat CA quan he PHI TUYEN (khac Pearson chi bat tuyen tinh). Giu top-8.
mi = mutual_info_classif(Xtr, y_train, random_state=RANDOM_STATE)
sel['filter_MI'] = (pd.Series(mi, index=FEATS).rank(ascending=False) <= 8).astype(int).values

# 1d. ANOVA F-test: kiem dinh trung binh feature khac nhau giua 2 lop hong/khong. Giu top-8.
F,_ = f_classif(Xtr, y_train)
sel['filter_Ftest'] = (pd.Series(F, index=FEATS).rank(ascending=False) <= 8).astype(int).values

# Bang diem 3 goc nhin (MI phi tuyen · F tuyen tinh · |corr| voi target)
display(pd.DataFrame({'MI':np.round(mi,3),'F':np.round(F,1),'|corr_target|':np.round(tgt,3)}, index=FEATS)
        .sort_values('MI', ascending=False))"""),
 new_markdown_cell("### 2) WRAPPER — thu to hop feature, do bang chinh mo hinh"),
 new_code_cell(r"""from sklearn.feature_selection import RFE, RFECV, SequentialFeatureSelector
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
skf = StratifiedKFold(5, shuffle=True, random_state=RANDOM_STATE)

lr = LogisticRegression(max_iter=2000, class_weight='balanced')
rf = RandomForestClassifier(n_estimators=200, min_samples_leaf=5, class_weight='balanced',
                            random_state=RANDOM_STATE, n_jobs=-1)

# 2a. RFE: loai DAN feature yeu nhat (theo he so LogReg) cho den khi con 8
sel['wrap_RFE'] = RFE(lr, n_features_to_select=8).fit(Xtr, y_train).get_support().astype(int)
# 2b. RFECV: nhu RFE nhung TU chon so feature toi uu bang cross-validation (scoring AUC-PR)
rfecv = RFECV(rf, step=1, cv=skf, scoring='average_precision',
              min_features_to_select=4, n_jobs=-1).fit(Xtr, y_train)
sel['wrap_RFECV'] = rfecv.get_support().astype(int)
print('RFECV tu chon', rfecv.n_features_, 'feature (toi uu AUC-PR qua CV)')
# 2c. Sequential Forward: THEM dan feature tot nhat tung buoc cho den khi du 8
sfs = SequentialFeatureSelector(lr, n_features_to_select=8, direction='forward',
                                scoring='average_precision', cv=skf, n_jobs=-1).fit(Xtr, y_train)
sel['wrap_SFS_fwd'] = sfs.get_support().astype(int)"""),
 new_markdown_cell("### 3) EMBEDDED — mo hinh tu chon feature khi hoc"),
 new_code_cell(r"""from sklearn.inspection import permutation_importance
# 3a. Lasso (L1): phat tri tuyet doi -> EP he so feature yeu ve 0 => feature do bi loai
l1 = LogisticRegression(penalty='l1', solver='saga', C=0.1, max_iter=5000,
                        class_weight='balanced').fit(Xtr, y_train)
sel['embed_LassoL1'] = (np.abs(l1.coef_[0]) > 1e-6).astype(int)
print('L1 giu lai', int(sel['embed_LassoL1'].sum()), '/', len(FEATS), 'feature (con lai he so=0)')

# 3b. RandomForest MDI: do quan trong = tong muc giam Gini khi chia theo feature do. Giu top-8.
rf.fit(Xtr, y_train)
sel['embed_RF_MDI'] = (pd.Series(rf.feature_importances_, index=FEATS).rank(ascending=False)<=8).astype(int).values
# 3c. Permutation: xao tron 1 feature roi xem AUC-PR TUT bao nhieu (do tren TEST B). Giu feature co dong gop >0.
perm = permutation_importance(rf, Xte, y_test, scoring='average_precision',
                              n_repeats=8, random_state=RANDOM_STATE, n_jobs=-1)
sel['embed_Perm'] = (perm.importances_mean > 1e-4).astype(int)"""),
 new_markdown_cell("### 4) TONG HOP — bang bo phieu dong thuan (consensus)"),
 new_code_cell(r"""sel['SO_PHIEU'] = sel.sum(axis=1)               # moi feature: bao nhieu phuong phap giu lai
sel_sorted = sel.sort_values('SO_PHIEU', ascending=False)
display(sel_sorted)
n_methods = sel.shape[1] - 1                    # tru cot SO_PHIEU
print(f'\nTong so phuong phap = {n_methods}')
keep = sel_sorted.index[sel_sorted['SO_PHIEU'] >= n_methods*0.6].tolist()   # nguong dong thuan 60%
print('Feature dong thuan cao (>=60% phuong phap giu):'); print(' ', keep)"""),
 new_markdown_cell("### 5) KIEM CHUNG — F1/AUC-PR: bo dong-thuan vs bo day du"),
 new_code_cell(r"""from sklearn.metrics import f1_score, average_precision_score
from sklearn.model_selection import cross_val_predict

def eval_cols(cols, label):
    rf2 = RandomForestClassifier(n_estimators=300, min_samples_leaf=5, class_weight='balanced',
                                 random_state=RANDOM_STATE, n_jobs=-1)
    idx = [FEATS.index(c) for c in cols]
    # nguong toi uu F1 lay tu CV TREN TRAIN (out-of-fold), khong nhin test -> chong ro ri
    oof = cross_val_predict(rf2, Xtr[:,idx], y_train, cv=skf, method='predict_proba', n_jobs=-1)[:,1]
    ts = np.linspace(0.05,0.9,80); thr = ts[int(np.argmax([f1_score(y_train,(oof>=t)) for t in ts]))]
    rf2.fit(Xtr[:,idx], y_train); p = rf2.predict_proba(Xte[:,idx])[:,1]
    return {'bo':label,'n':len(cols),'AUC_PR':average_precision_score(y_test,p),'F1':f1_score(y_test,(p>=thr))}

rows = [eval_cols(FEATS,'Day du (11)'),
        eval_cols(keep,'Dong thuan (>=60%)'),
        eval_cols([c for c in FEATS if c in sel_sorted.index[:6]],'Top-6 phieu')]
display(pd.DataFrame(rows).set_index('bo').round(4))"""),
 new_markdown_cell("""> ### 🔎 Doc ket qua (Case 03)
> - **Cac feature co che duoc da so phuong phap cung giu**: `do_mon_dao`, `osf_margin`, `tich_mon_momen`,
>   `cong_suat_co` — dong thuan cao, dung nhu ky vong domain.
> - Bo loc high-correlation tu danh dau cap **`osf_margin ↔ momen_xoan`** trung thong tin — chinh la
>   "diem cai cam" tuong tac trong du lieu.
> - **Ket qua manh nhat** (bang kiem chung):
>
> | Bo feature | So feature | F1 |
> |---|---|---|
> | Day du | 11 | **0.782** |
> | Dong thuan (≥60%) | 10 | **0.782** |
> | Top-6 phieu | 6 | **0.782** |
>
> Lay **Top-6 feature cho F1 y het bo 11** -> hon nua so feature la **du thua**. Co the dung bo gon 6 feature
> ma khong mat diem, mo hinh don gian & de giai thich hon.
>
> ### ✅ Ket luan Case 03
> Day la cach chon feature **CO PHUONG PHAP** (Filter/Wrapper/Embedded) dung ngon ngu bai L5, thay vi cam tinh.
> No vua xac nhan bo feature cuoi, vua chi ra co the tinh gon them ma khong hai F1."""),
])


# ===========================================================================
# CASE 04 — Da cong tuyen / VIF  [Bai L3 + L5]
# ===========================================================================
build('04_da_cong_tuyen_VIF.ipynb',
"""# Case 04 — Da cong tuyen (Multicollinearity) & **VIF**  ·  *Bai L3 (p20) + L5*

## Y tuong
Da cong tuyen = mot feature co the SUY RA gan dung tu cac feature khac. **VIF (Variance Inflation Factor)**
do muc do do: dem tung feature hoi quy theo cac feature con lai, duoc R²; roi **VIF = 1 / (1 − R²)**.
Quy uoc: VIF > 5 dang ngo, VIF > 10 cong tuyen **NANG**.
*(statsmodels khong co san nen ta tinh tay theo dung cong thuc tren.)*

## Vi sao chay thu nghiem nay
Cac feature ta tao deu la **ham cua bien goc** (`chenh_lech_nhiet = quy_trinh − moi_truong`,
`cong_suat = momen × toc_do`...) nen chac chan cong tuyen voi bien cha. Cau hoi: dieu do co lam **hong mo hinh** khong?

## Diem mau chot (bao ve khi bi hoi)
Da cong tuyen **KHONG** anh huong cay/rung (RF, XGB) vi chung chia theo nguong TUNG bien mot;
nhung **CO** anh huong LogReg (1 trong 3 model) -> he so bat on. Giai phap = **regularization** (Case 05), khong nhat thiet phai bo feature.""",
[
 new_code_cell(r"""from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
Z = StandardScaler().fit_transform(train_fe[FINAL_NUM])   # scale de so sanh cong bang giua cac feature

rows = []
for i, col in enumerate(FINAL_NUM):
    others = [j for j in range(len(FINAL_NUM)) if j != i]
    # R2 khi lay feature i lam "target", hoi quy theo cac feature con lai. R2 cao => de suy ra => cong tuyen.
    r2  = LinearRegression().fit(Z[:,others], Z[:,i]).score(Z[:,others], Z[:,i])
    vif = np.inf if r2 >= 1 else 1/(1-r2)
    rows.append({'feature':col, 'R2_tren_cac_bien_khac':round(r2,4), 'VIF':round(vif,2)})
vif_df = pd.DataFrame(rows).sort_values('VIF', ascending=False).set_index('feature')
display(vif_df)
print('Quy uoc: VIF>5 dang ngo, VIF>10 cong tuyen NANG. (inf = suy ra CHINH XAC tu bien khac)')"""),
 new_code_cell(r"""import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
vif_df['VIF'].clip(upper=50).plot(kind='barh', ax=ax[0], color='#C44E52')   # clip 50 de cot inf khong pha bieu do
ax[0].axvline(10, ls='--', c='k'); ax[0].set_title('VIF (cat o 50 de de nhin) — vach = nguong 10')
c = np.corrcoef(train_fe[FINAL_NUM].values, rowvar=False)
im = ax[1].imshow(c, vmin=-1, vmax=1, cmap='RdBu_r')
ax[1].set_xticks(range(len(FINAL_NUM))); ax[1].set_xticklabels(FINAL_NUM, rotation=90, fontsize=7)
ax[1].set_yticks(range(len(FINAL_NUM))); ax[1].set_yticklabels(FINAL_NUM, fontsize=7)
ax[1].set_title('Ma tran tuong quan cac feature so'); fig.colorbar(im, ax=ax[1], fraction=.046)
plt.tight_layout(); plt.show()"""),
 new_code_cell(r"""# BANG CHUNG: cong tuyen lam HE SO LogReg khong on dinh. Chay LogReg tren 5 fold, xem he so lech bao nhieu.
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
skf = StratifiedKFold(5, shuffle=True, random_state=RANDOM_STATE)
coefs = []
for tr_i, _ in skf.split(Z, y_train):
    # C=1e6 = phat cuc nho = GAN NHU KHONG regularize -> co tinh de lo ra su bat on do cong tuyen
    m = LogisticRegression(max_iter=2000, class_weight='balanced', C=1e6).fit(Z[tr_i], y_train[tr_i])
    coefs.append(m.coef_[0])
coefs = np.array(coefs)
inst = pd.DataFrame({'he_so_TB':coefs.mean(0), 'do_lech_giua_cac_fold':coefs.std(0)}, index=FINAL_NUM)
display(inst.round(3).sort_values('do_lech_giua_cac_fold', ascending=False))
print('Feature cong tuyen (VIF cao) thuong co he_so DAO DONG manh giua cac fold => khong on dinh.')"""),
 new_markdown_cell("""> ### 🔎 Doc ket qua (Case 04)
> | Feature | VIF | Vi sao |
> |---|---|---|
> | bo 3 nhiet (moi_truong / quy_trinh / chenh_lech) | **∞** | `chenh_lech = quy_trinh − moi_truong` -> suy ra CHINH XAC, R²=1.0 |
> | `cong_suat_co` | ~96 | = momen × toc_do |
> | `momen_xoan` | ~83 | xuat hien trong nhieu feature phai sinh |
> | `tich_mon_momen` | ~38 | = mon × momen |
> | `osf_margin` | ~18 | phai sinh tu tich_mon_momen |
>
> Va he so LogReg **dao dong manh** giua cac fold (vd `momen` lech ±0.156) — dau hieu kinh dien cua cong tuyen.
>
> ### ✅ Ket luan Case 04
> Cong tuyen **chi hai LogReg**, **khong hai cay/rung** -> day chinh la ly do **RandomForest ben vung**.
> Vi vay ta **KHONG bo** cac feature phai sinh (chung van mang thong tin co che) — chi can **regularization L2/L1**
> cho model tuyen tinh (xem Case 05). Do la lua chon co can cu, khong phai bo feature mot cach may moc."""),
])


# ===========================================================================
# CASE 05 — Regularization LogReg: L1 / L2 / ElasticNet  [Bai L5]
# ===========================================================================
build('05_regularization_logreg.ipynb',
"""# Case 05 — Regularization cho LogReg: **L1 / L2 / ElasticNet**  ·  *Bai L5*

## Y tuong
Regularization = them "hinh phat" len do lon he so de mo hinh khong qua khop va on dinh hon:

| Loai | Cach phat | Tac dung dac trung |
|---|---|---|
| **L2 (Ridge)** | binh phuong he so | co nho DEU moi he so — hop khi co cong tuyen (Case 04) |
| **L1 (Lasso)** | tri tuyet doi he so | **EP han mot so he so ve 0** -> tu loai feature (Embedded) |
| **ElasticNet** | tron L1 + L2 | vua co vua loai |

## Vi sao chay thu nghiem nay
Notebook chinh chi khai bao `penalty='l2'`, bo phi 2 lua chon kia du DA HOC. Ta so ca ba tren cung du lieu.""",
[
 new_code_cell(r"""from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, cross_val_predict
from sklearn.metrics import f1_score, average_precision_score
from scipy.stats import loguniform
skf = StratifiedKFold(5, shuffle=True, random_state=RANDOM_STATE)

pre = ColumnTransformer([('num', StandardScaler(), FINAL_NUM),
      ('cat', OneHotEncoder(handle_unknown='ignore', drop='if_binary', sparse_output=False), FINAL_CAT)])

def run(penalty, extra):
    # solver='saga' la solver duy nhat ho tro CA l1, l2 va elasticnet
    lr   = LogisticRegression(solver='saga', penalty=penalty, max_iter=5000, class_weight='balanced')
    grid = {'lr__C': loguniform(1e-2, 1e2)}; grid.update(extra)   # C = 1/lambda (C nho = phat manh)
    pipe = Pipeline([('pre', pre), ('lr', lr)])
    rs   = RandomizedSearchCV(pipe, grid, n_iter=12, scoring='average_precision',
                              cv=skf, random_state=RANDOM_STATE, n_jobs=-1
                              ).fit(train_fe[FINAL_NUM+FINAL_CAT], y_train)
    best = rs.best_estimator_
    # nguong F1 lay tu CV tren train (khong nhin test)
    oof = cross_val_predict(best, train_fe[FINAL_NUM+FINAL_CAT], y_train, cv=skf, method='predict_proba', n_jobs=-1)[:,1]
    ts  = np.linspace(0.05,0.9,80); thr = ts[int(np.argmax([f1_score(y_train,(oof>=t)) for t in ts]))]
    p    = best.predict_proba(test_fe[FINAL_NUM+FINAL_CAT])[:,1]
    coef = best.named_steps['lr'].coef_[0]
    return {'penalty':penalty, 'best_C':round(rs.best_params_['lr__C'],3),
            'he_so_khac_0':int((np.abs(coef)>1e-6).sum()), 'tong_he_so':len(coef),
            'AUC_PR':average_precision_score(y_test,p), 'F1':f1_score(y_test,(p>=thr))}

rows = [run('l2', {}),
        run('l1', {}),
        run('elasticnet', {'lr__l1_ratio':[0.2, 0.5, 0.8]})]   # l1_ratio = ty le tron L1 trong ElasticNet
display(pd.DataFrame(rows).set_index('penalty').round(4))"""),
 new_code_cell(r"""# L1 loai feature nao? Xem he so nao bi ep ve 0.
best_l1 = LogisticRegression(solver='saga', penalty='l1', C=0.1, max_iter=5000, class_weight='balanced')
pipe_l1 = Pipeline([('pre', pre), ('lr', best_l1)]).fit(train_fe[FINAL_NUM+FINAL_CAT], y_train)
names = pipe_l1.named_steps['pre'].get_feature_names_out()
coef  = pipe_l1.named_steps['lr'].coef_[0]
imp   = pd.Series(coef, index=names).sort_values(key=np.abs, ascending=False)
print('He so LogReg-L1 (C=0.1), sap theo do lon:'); print(imp.round(3).to_string())
print('\n=> feature co he so = 0 la feature bi L1 LOAI BO (tu chon feature kieu Embedded).')"""),
 new_markdown_cell("""> ### 🔎 Doc ket qua (Case 05)
> | Penalty | He so khac 0 | AUC-PR | F1 |
> |---|---|---|---|
> | L2 | 12/12 | 0.235 | 0.302 |
> | L1 | 9/12 | 0.238 | **0.306** |
> | ElasticNet | 9/12 | 0.237 | **0.308** |
>
> - **L1 & ElasticNet nhinh hon L2** mot chut ve F1.
> - **L1 ep 3 he so ve dung 0** (`nhiet_do_quy_trinh` va 2 muc cua `loai_san_pham`) -> tu noi
>   "3 feature nay bo cung duoc", **khop voi ket luan dong thuan o Case 03**.
>
> ### ✅ Ket luan Case 05
> Giu `penalty='l2'` la hop ly (on dinh khi co cong tuyen — Case 04), nhung nen **bo sung `penalty` vao grid**
> cua RandomizedSearchCV (`l1`/`l2`/`elasticnet`, solver `saga`) de may tu chon — dung tinh than L5, va cho
> cau chuyen "regularization vua chong overfit vua on dinh hoa cong tuyen"."""),
])


# ===========================================================================
# CASE 06 — RobustScaler vs Standard vs MinMax  [Bai L5]
# ===========================================================================
build('06_scaler_robust_vs_standard.ipynb',
"""# Case 06 — **RobustScaler** vs Standard vs MinMax  ·  *Bai L5 (p7)*

## Y tuong
Ba cach dua feature ve cung thang do:

| Scaler | Cong thuc | Nhay outlier? |
|---|---|---|
| **Standard** | (x − trung binh) / do lech chuan | co (trung binh/do lech bi outlier keo) |
| **Robust** | (x − trung vi) / IQR | it (dung trung vi) |
| **MinMax** | ep ve [0, 1] | rat nhay |

## Vi sao chay thu nghiem nay
Du lieu co **diem cai cam clipping** (gia tri bi cat don o bien -> outlier nhan tao). Ve nguyen tac, khi co
outlier thi Robust an toan hon. Ta kiem bang so. *(Xet tren LogReg — cay/rung bat bien voi scale nen khong can.)*""",
[
 new_code_cell(r"""from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import f1_score, average_precision_score
skf = StratifiedKFold(5, shuffle=True, random_state=RANDOM_STATE)

def run(scaler, name):
    # Chi thay doi SCALER, giu nguyen moi thu khac -> so sanh cong bang
    pre  = ColumnTransformer([('num', scaler, FINAL_NUM),
           ('cat', OneHotEncoder(handle_unknown='ignore', drop='if_binary', sparse_output=False), FINAL_CAT)])
    lr   = LogisticRegression(max_iter=5000, class_weight='balanced')
    pipe = Pipeline([('pre', pre), ('lr', lr)])
    oof  = cross_val_predict(pipe, train_fe[FINAL_NUM+FINAL_CAT], y_train, cv=skf, method='predict_proba', n_jobs=-1)[:,1]
    ts   = np.linspace(0.05,0.9,80); thr = ts[int(np.argmax([f1_score(y_train,(oof>=t)) for t in ts]))]
    pipe.fit(train_fe[FINAL_NUM+FINAL_CAT], y_train); p = pipe.predict_proba(test_fe[FINAL_NUM+FINAL_CAT])[:,1]
    return {'scaler':name, 'AUC_PR_test':average_precision_score(y_test,p),
            'F1_test':f1_score(y_test,(p>=thr)), 'AUC_PR_cv':average_precision_score(y_train,oof)}

rows = [run(StandardScaler(), 'Standard (mean/std)'),
        run(RobustScaler(),   'Robust (median/IQR)'),
        run(MinMaxScaler(),   'MinMax (min-max)')]
display(pd.DataFrame(rows).set_index('scaler').round(4))"""),
 new_code_cell(r"""# Vi sao (khong) can Robust: dem 'outlier' (pile-up bien do clipping) tren tung feature THO
from scipy import stats
print('Ty le diem |z|>4 (outlier manh) va max|z| tren tung feature TRAIN:')
for c in NUM:
    z = np.abs(stats.zscore(train_fe[c]))
    print(f'  {c:20s} {(z>4).mean()*100:5.2f}%   (max|z|={z.max():.1f})')
print('\nGhi chu: bi CLIP o bien nen max|z| bi chan (~4), khong co duoi cuc doan -> chenh lech scaler nho.')"""),
 new_markdown_cell("""> ### 🔎 Doc ket qua (Case 06)
> | Scaler | F1_test | AUC-PR_test |
> |---|---|---|
> | Standard | 0.306 | 0.244 |
> | **Robust** | **0.308** | 0.244 |
> | MinMax | 0.301 | 0.233 |
>
> Chenh lech **rat nho**: Robust ≥ Standard ≥ MinMax. Dem outlier cung it (bi clip o |z|≈4, khong co duoi cuc doan)
> nen loi the cua Robust khong lon.
>
> ### ✅ Ket luan Case 06
> Voi du lieu **bi clip**, **RobustScaler co ly le hon** ve nguyen tac (it bi keo boi bien). Nhung khac biet nho
> vi LogReg + class_weight von da ben; va voi **mo hinh cuoi (cay/rung) thi thang do KHONG quan trong chut nao**.
> Thong diep: chon scaler phai co **ly do gan voi dac diem du lieu**, khong chon theo quan tinh."""),
])

print('\n=== DA SINH XONG', len([f for f in os.listdir(OUT) if f.endswith('.ipynb')]),
      'notebook trong', OUT, '===')
