# -*- coding: utf-8 -*-
"""Bieu do KHAI NIEM ho tro phan ly luan: (7) co che hinge & bat bien rank, (8) reweighting."""
import sys; sys.stdout.reconfigure(encoding='utf-8')
import numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
for fname in ['Segoe UI','Arial','DejaVu Sans']:
    try:
        font_manager.findfont(fname, fallback_to_default=False)
        plt.rcParams['font.family']=fname; break
    except Exception: continue
plt.rcParams['figure.dpi']=130; plt.rcParams['axes.grid']=True
plt.rcParams['grid.alpha']=0.25; plt.rcParams['axes.axisbelow']=True
C_A='#2563eb'; C_B='#dc2626'; C_OK='#059669'; C_ACC='#7c3aed'; C_GRAY='#94a3b8'
OUT='bao_cao/assets/'

# ============ 7. Co che HINGE + bat bien rank ============
fig, axes = plt.subplots(1, 2, figsize=(11, 3.9))

# (a) Ham hinge: vung an toan bi nen phang ve 0
ax = axes[0]
x = np.linspace(4, 14, 400)
thr = 8.6
y1 = np.maximum(thr - x, 0)
y2 = np.maximum(6.0 - x, 0)   # nguong khac
ax.plot(x, y1, color=C_B, lw=2.4, label='ngưỡng = 8.6 (gốc)')
ax.plot(x, y2, color=C_ACC, lw=2.2, ls='--', label='ngưỡng = 6.0 (đổi)')
ax.axvline(thr, color=C_B, ls=':', lw=1, alpha=0.6)
ax.axvline(6.0, color=C_ACC, ls=':', lw=1, alpha=0.6)
ax.fill_between(x, 0, y1, where=(x<thr), color=C_B, alpha=0.08)
ax.annotate('vùng AN TOÀN\n(nén phẳng về 0)', xy=(11.5, 0.15), fontsize=8.5,
            ha='center', color='#475569')
ax.annotate('vùng NGUY\n(giữ tín hiệu)', xy=(5.2, 3.0), fontsize=8.5,
            ha='center', color=C_B)
ax.set_title('(a) Hinge max(ngưỡng − x, 0): đổi ngưỡng\nlàm ĐỔI nhóm bị nén → đổi rank',
             fontsize=10, fontweight='bold')
ax.set_xlabel('ΔT (chênh lệch nhiệt, K)'); ax.set_ylabel('giá trị feature')
ax.legend(fontsize=8, loc='upper right')

# (b) Bat bien rank: tru hang so khong doi thu tu
ax = axes[1]
machines = ['A','B','C','D','E']
val0 = np.array([-200,-50,50,200,500])   # bien_overstrain goc
val1 = val0 + 100                          # giam nguong 100 => +100
xpos = np.arange(5)
ax.plot(xpos, val0, 'o-', color=C_GRAY, lw=1.8, ms=8, label='ngưỡng gốc')
ax.plot(xpos, val1, 's--', color=C_OK, lw=1.8, ms=7, label='giảm ngưỡng 100 (+100 đều)')
for i in range(5):
    ax.annotate('', xy=(xpos[i], val1[i]-15), xytext=(xpos[i], val0[i]+15),
                arrowprops=dict(arrowstyle='->', color='#cbd5e1', lw=1))
ax.axhline(0, color='#64748b', lw=0.8, alpha=0.5)
ax.set_xticks(xpos); ax.set_xticklabels([f'máy {m}' for m in machines], fontsize=9)
ax.set_ylabel('bien_overstrain')
ax.set_title('(b) Không hinge: mọi máy +100 như nhau\n→ THỨ TỰ A<B<C<D<E giữ nguyên → RF y hệt',
             fontsize=10, fontweight='bold')
ax.legend(fontsize=8, loc='upper left')
plt.tight_layout(); plt.savefig(OUT+'07_hinge.png', bbox_inches='tight'); plt.close()

# ============ 8. Reweighting density-ratio ============
train = pd.read_csv('Data_Final/train.csv')
test  = pd.read_csv('Data_Final/test.csv')
fig, ax = plt.subplots(figsize=(8.5, 3.6))
col='nhiet_do_moi_truong'
lo=min(train[col].min(),test[col].min()); hi=max(train[col].max(),test[col].max())
bins=np.linspace(lo,hi,45)
ax.hist(train[col],bins=bins,density=True,alpha=0.45,color=C_A,label='A (train) — gốc')
ax.hist(test[col], bins=bins,density=True,alpha=0.45,color=C_B,label='B (test) — đích')
# minh hoa vung A "giong B" duoc up-weight
xhi = np.linspace(302, hi, 100)
ax.annotate('mẫu A ở đây "giống B"\n→ trọng số CAO (w = p/(1−p))',
            xy=(303.5, 0.15), xytext=(298, 0.42), fontsize=8.5, color=C_OK,
            arrowprops=dict(arrowstyle='->', color=C_OK, lw=1.5))
ax.set_xlabel('nhiệt độ môi trường (K)'); ax.set_ylabel('mật độ')
ax.set_title('Importance reweighting: kéo phân phối huấn luyện A về phía B\nbằng trọng số density-ratio (không cần nhãn B)',
             fontsize=10.5, fontweight='bold', pad=8)
ax.legend(fontsize=8.5)
plt.tight_layout(); plt.savefig(OUT+'08_reweight.png', bbox_inches='tight'); plt.close()

print('OK - charts 07_hinge, 08_reweight saved')
