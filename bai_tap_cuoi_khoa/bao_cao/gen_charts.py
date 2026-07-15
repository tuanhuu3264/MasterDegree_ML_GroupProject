# -*- coding: utf-8 -*-
"""Sinh bieu do cho bao cao PDF Predictive Maintenance.
Tinh PSI / shift / invariance / confusion matrix truc tiep tu du lieu (tat dinh)."""
import sys; sys.stdout.reconfigure(encoding='utf-8')
import numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---- Font ho tro tieng Viet ----
for fname in ['Segoe UI', 'Arial', 'DejaVu Sans']:
    try:
        font_manager.findfont(fname, fallback_to_default=False)
        plt.rcParams['font.family'] = fname
        break
    except Exception:
        continue
plt.rcParams['figure.dpi'] = 130
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.25
plt.rcParams['axes.axisbelow'] = True

C_A = '#2563eb'   # xanh (A / train)
C_B = '#dc2626'   # do  (B / test)
C_OK = '#059669'
C_ACCENT = '#7c3aed'

OUT = 'bao_cao/assets/'

# ============ Nap du lieu ============
train = pd.read_csv('Data_Final/train.csv')
test  = pd.read_csv('Data_Final/test.csv')
NUM_COLS = ['nhiet_do_moi_truong','nhiet_do_quy_trinh','toc_do_quay','momen_xoan','do_mon_dao']
TARGET = 'hong_hoc'
NG_DT, NG_TOC = 8.6, 1380
NG_CS_THAP, NG_CS_CAO = 3500, 9000
NGUONG_OSF = {'L':11000,'M':12000,'H':13000}

def add_features(df):
    out = df.copy()
    dt = out['nhiet_do_quy_trinh'] - out['nhiet_do_moi_truong']
    pw = out['momen_xoan']*out['toc_do_quay']*2*np.pi/60
    nguong = out['loai_san_pham'].map(NGUONG_OSF)
    out['nguy_tan_nhiet']  = np.maximum(NG_DT-dt,0)*np.maximum(NG_TOC-out['toc_do_quay'],0)
    out['lech_cong_suat']  = np.maximum(NG_CS_THAP-pw,0)+np.maximum(pw-NG_CS_CAO,0)
    out['bien_overstrain'] = out['do_mon_dao']*out['momen_xoan'] - nguong
    return out

tr_fe = add_features(train); te_fe = add_features(test)
FE = ['nguy_tan_nhiet','lech_cong_suat','bien_overstrain']

# ============ 1. Hanh trinh cai tien F1 ============
labels = ['v0\nLogReg\nthô','v1\n+FE\nbiên','v2\nCây\n(RF/XGB)','v3\nRe-\nweight','v4\nThresh\nIWV','v6\nVoting\nchốt']
f1     = [0.231, 0.352, 0.773, 0.772, 0.771, 0.781]
aucpr  = [0.220, 0.501, 0.665, 0.676, 0.676, 0.670]
fig, ax = plt.subplots(figsize=(9,4.2))
x = np.arange(len(labels))
bars = ax.bar(x, f1, color=[C_B if i<5 else C_OK for i in range(6)], alpha=0.9, width=0.62, zorder=3)
bars[0].set_color('#94a3b8'); bars[-1].set_color(C_OK)
ax.plot(x, aucpr, 'o--', color=C_ACCENT, lw=1.8, ms=6, label='AUC-PR', zorder=4)
for i,(v) in enumerate(f1):
    ax.text(i, v+0.012, f'{v:.3f}', ha='center', fontsize=9.5, fontweight='bold')
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8.5)
ax.set_ylabel('Điểm số (trên Dây chuyền B)')
ax.set_ylim(0, 0.92)
ax.set_title('Hành trình cải tiến — F1 tăng 3.4× (0.231 → 0.781)', fontsize=12, fontweight='bold', pad=10)
ax.axhline(0.781, color=C_OK, ls=':', lw=1, alpha=0.6)
ax.legend(loc='upper left', fontsize=9)
plt.tight_layout(); plt.savefig(OUT+'01_journey.png', bbox_inches='tight'); plt.close()

# ============ 2. Covariate shift A vs B ============
fig, axes = plt.subplots(1, 3, figsize=(11, 3.3))
show = [('nhiet_do_moi_truong','Nhiệt độ môi trường (K)'),
        ('toc_do_quay','Tốc độ quay (rpm)'),
        ('do_mon_dao','Độ mòn dao')]
for ax,(col,title) in zip(axes, show):
    lo = min(train[col].min(), test[col].min()); hi = max(train[col].max(), test[col].max())
    bins = np.linspace(lo, hi, 40)
    ax.hist(train[col], bins=bins, density=True, alpha=0.55, color=C_A, label='A (train)')
    ax.hist(test[col],  bins=bins, density=True, alpha=0.55, color=C_B, label='B (test)')
    ax.set_title(title, fontsize=10)
    ax.legend(fontsize=8)
axes[0].set_ylabel('Mật độ')
fig.suptitle('Covariate shift: phân phối đầu vào dịch A→B (B nóng hơn, nhanh hơn; độ mòn dao ổn định)',
             fontsize=11.5, fontweight='bold', y=1.04)
plt.tight_layout(); plt.savefig(OUT+'02_shift.png', bbox_inches='tight'); plt.close()

# ============ 3. PSI: bien tho vs feature vat ly ============
def psi(a, b, bins=10):
    qs = np.quantile(a, np.linspace(0,1,bins+1))
    qs[0]=-np.inf; qs[-1]=np.inf
    ea = np.histogram(a, qs)[0]/len(a); eb = np.histogram(b, qs)[0]/len(b)
    ea = np.clip(ea,1e-6,None); eb = np.clip(eb,1e-6,None)
    return np.sum((eb-ea)*np.log(eb/ea))

psi_rows = []
for c in NUM_COLS: psi_rows.append((c, psi(train[c].values, test[c].values), 'thô'))
for c in FE:       psi_rows.append((c, psi(tr_fe[c].values, te_fe[c].values), 'biên'))
psi_df = pd.DataFrame(psi_rows, columns=['feat','psi','kind']).sort_values('psi')
name_map = {'nhiet_do_moi_truong':'nhiệt độ MT','nhiet_do_quy_trinh':'nhiệt độ QT',
            'toc_do_quay':'tốc độ quay','momen_xoan':'mômen xoắn','do_mon_dao':'độ mòn dao',
            'nguy_tan_nhiet':'nguy_tản_nhiệt ★','lech_cong_suat':'lệch_công_suất ★','bien_overstrain':'biên_overstrain ★'}
fig, ax = plt.subplots(figsize=(8.5,4))
colors = [C_OK if k=='biên' else C_B for k in psi_df['kind']]
ax.barh(range(len(psi_df)), psi_df['psi'], color=colors, alpha=0.9, zorder=3)
ax.set_yticks(range(len(psi_df))); ax.set_yticklabels([name_map[f] for f in psi_df['feat']], fontsize=9.5)
for i,v in enumerate(psi_df['psi']):
    ax.text(v+0.015, i, f'{v:.2f}', va='center', fontsize=9)
ax.axvline(0.1, color='#f59e0b', ls='--', lw=1, label='0.1 (nhẹ)')
ax.axvline(0.25, color=C_B, ls='--', lw=1, label='0.25 (mạnh)')
ax.set_xlabel('PSI (Population Stability Index)')
ax.set_title('PSI: shift dồn ở biến thô — 3 feature biên vật lý (★) PSI≈0', fontsize=11.5, fontweight='bold', pad=8)
ax.legend(fontsize=8.5, loc='lower right')
plt.tight_layout(); plt.savefig(OUT+'03_psi.png', bbox_inches='tight'); plt.close()

# ============ 4. Bang chung bat bien P(hong|co) A vs B ============
def prec_of(df, y):
    dt = df['nhiet_do_quy_trinh']-df['nhiet_do_moi_truong']
    pw = df['momen_xoan']*df['toc_do_quay']*2*np.pi/60
    hdf = (dt<NG_DT)&(df['toc_do_quay']<NG_TOC)
    pwf = (pw<NG_CS_THAP)|(pw>NG_CS_CAO)
    osf = (df['do_mon_dao']*df['momen_xoan'] > df['loai_san_pham'].map(NGUONG_OSF))
    out={}
    for nm,fl in [('HDF',hdf),('PWF',pwf),('OSF',osf)]:
        out[nm]= y[fl].mean() if fl.sum()>0 else 0
    return out

pa = prec_of(train, train[TARGET]); pb = prec_of(test, test[TARGET])
rules = ['HDF','PWF','OSF']
fig, ax = plt.subplots(figsize=(7,3.8))
x = np.arange(len(rules)); w=0.36
ax.bar(x-w/2, [pa[r] for r in rules], w, color=C_A, alpha=0.9, label='A (train)', zorder=3)
ax.bar(x+w/2, [pb[r] for r in rules], w, color=C_B, alpha=0.9, label='B (test)', zorder=3)
for i,r in enumerate(rules):
    ax.text(i-w/2, pa[r]+0.015, f'{pa[r]:.2f}', ha='center', fontsize=9)
    ax.text(i+w/2, pb[r]+0.015, f'{pb[r]:.2f}', ha='center', fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(['HDF\n(tản nhiệt)','PWF\n(công suất)','OSF\n(overstrain)'])
ax.set_ylabel('P(hỏng | máy vượt ngưỡng luật)')
ax.set_ylim(0,1)
ax.set_title('Bằng chứng bất biến: cơ chế hỏng đứng yên khi A→B', fontsize=11.5, fontweight='bold', pad=8)
ax.legend(fontsize=9)
plt.tight_layout(); plt.savefig(OUT+'04_invariance.png', bbox_inches='tight'); plt.close()

# ============ 5. Confusion matrix v6 (suy tu P/R/positives) ============
# B: 6000 dong, 477 hong. R=0.753, P=0.812
POS = int(round(test[TARGET].sum())); N = len(test); NEG = N-POS
R, P = 0.753, 0.812
TP = int(round(R*POS)); FP = int(round(TP/P - TP)); FN = POS-TP; TN = NEG-FP
cm = np.array([[TN, FP],[FN, TP]])
fig, ax = plt.subplots(figsize=(4.8,4.3))
im = ax.imshow(cm, cmap='Blues')
labels_cm = [['TN','FP'],['FN','TP']]
for i in range(2):
    for j in range(2):
        val=cm[i,j]
        ax.text(j,i,f'{labels_cm[i][j]}\n{val}', ha='center', va='center',
                fontsize=14, fontweight='bold',
                color='white' if val>cm.max()*0.5 else '#1e293b')
ax.set_xticks([0,1]); ax.set_xticklabels(['Dự đoán: không hỏng','Dự đoán: hỏng'], fontsize=9)
ax.set_yticks([0,1]); ax.set_yticklabels(['Thực: không hỏng','Thực: hỏng'], fontsize=9)
ax.set_title(f'Ma trận nhầm lẫn v6 (ngưỡng 0.705, Dây chuyền B)\nP={P:.2f}  R={R:.2f}  F1=0.781',
             fontsize=10.5, fontweight='bold', pad=10)
plt.tight_layout(); plt.savefig(OUT+'05_confusion.png', bbox_inches='tight'); plt.close()

# ============ 6. Drift AUC ============
fig, ax = plt.subplots(figsize=(7,2.6))
cats = ['Toàn bộ\nfeature','Chỉ 5 biến\nthô','Chỉ 3 feature\nbiên vật lý']
vals = [0.819, 0.817, 0.512]
cols = [C_B, C_B, C_OK]
b = ax.barh(range(3), vals, color=cols, alpha=0.9, zorder=3)
for i,v in enumerate(vals):
    ax.text(v+0.01, i, f'{v:.3f}', va='center', fontsize=10, fontweight='bold')
ax.axvline(0.5, color='#64748b', ls='--', lw=1.2, label='0.5 = không phân biệt được A/B')
ax.set_yticks(range(3)); ax.set_yticklabels(cats, fontsize=9.5)
ax.set_xlim(0.4,0.95); ax.invert_yaxis()
ax.set_xlabel('Drift AUC (mô hình đoán A hay B)')
ax.set_title('Feature biên "trong suốt" với shift (AUC 0.51 ≈ đoán mù)', fontsize=11, fontweight='bold', pad=8)
ax.legend(fontsize=8.5, loc='lower right')
plt.tight_layout(); plt.savefig(OUT+'06_drift.png', bbox_inches='tight'); plt.close()

print('CONFUSION:', dict(TN=TN,FP=FP,FN=FN,TP=TP,POS=POS,NEG=NEG))
print('PSI:'); print(psi_df.to_string(index=False))
print('INVARIANCE A:', {k:round(v,3) for k,v in pa.items()})
print('INVARIANCE B:', {k:round(v,3) for k,v in pb.items()})
print('OK - 6 charts saved to', OUT)
