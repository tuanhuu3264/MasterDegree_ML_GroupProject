# 📚 Giải thích chi tiết từ khoá trong đề — Dự đoán Hỏng hóc Thiết bị dưới Distribution Shift

> Tài liệu học tập: quét **mọi thuật ngữ** trong `FINAL_Rubric_PredictiveMaintenance.docx`. Mỗi từ khoá gồm:
> **① Định nghĩa · ② Công thức (giải thích từng ký hiệu) · ③ Ví dụ tính tay bằng số THẬT của bộ dữ liệu · ④ Vì sao dùng trong bài · ⑤ Lỗi thường gặp.**
> Mọi con số ví dụ đều lấy trực tiếp từ `train.csv`/`test.csv` (14000/6000 dòng).

---

# PHẦN 0 — BỐI CẢNH & NỀN TẢNG

## 0.1 Predictive Maintenance (bảo trì dự đoán)
- **① Định nghĩa:** dự đoán *trước* khi máy hỏng để can thiệp chủ động, thay cho **run-to-failure** (chạy đến hỏng mới sửa).
- **④ Trong bài:** ta dự đoán `hong_hoc` của **ca sản xuất kế tiếp** → chuyển từ bị động sang chủ động.
- **Ba mức độ bảo trì:** *Reactive* (sửa khi hỏng) → *Preventive* (theo lịch cố định) → *Predictive* (theo tình trạng thực, dùng ML — mức bài này hướng tới).

## 0.2 Distribution Shift (dịch chuyển phân phối)
- **① Định nghĩa:** phân phối dữ liệu lúc triển khai (Test = Dây chuyền B) **khác** lúc huấn luyện (Train = Dây chuyền A). Mô hình "học ở A" dễ kém khi chạy ở B.
- **② Ký hiệu:** gọi $P_{train}(x,y)$ và $P_{test}(x,y)$ là phân phối chung của đặc trưng $x$ và nhãn $y$. Shift nghĩa là $P_{train}\neq P_{test}$.
- **Ba loại shift:**

| Loại | Cái gì đổi | Cái gì giữ nguyên | Có phải trường hợp của bài? |
|---|---|---|---|
| **Covariate shift** | $P(x)$ | $P(y\mid x)$ | ✅ **ĐÚNG** — cơ chế vật lý gây hỏng không đổi, chỉ điều kiện vận hành (nhiệt độ, tải) đổi |
| **Label/Prior shift** | $P(y)$ | $P(x\mid y)$ | Một phần nhỏ (tỷ lệ hỏng 7.36%→7.95%) |
| **Concept drift** | $P(y\mid x)$ | — | ❌ Không — nếu có thì reweighting sẽ vô hiệu |
- **③ Ví dụ số:** nhiệt độ môi trường trung bình Train = **299.99 K** → Test = **302.51 K** (nóng hơn ~2.5 K); tốc độ quay 1540 → 1610 rpm. Đây là $P(x)$ đổi = covariate shift.
- **⑤ Lỗi thường gặp:** đánh giá mô hình bằng cross-val trên Train rồi tưởng sẽ tốt trên B — **sai**, vì shift làm hiệu năng tụt khi triển khai.

## 0.3 Các biến & 4 cơ chế hỏng (nền tảng để làm Feature Engineering)

| Cột | Đơn vị | Ý nghĩa vật lý |
|---|---|---|
| `nhiet_do_moi_truong` | K | Nhiệt độ môi trường (air temp) |
| `nhiet_do_quy_trinh` | K | Nhiệt độ quy trình (process temp) |
| `toc_do_quay` | rpm | Tốc độ quay trục chính |
| `momen_xoan` | Nm | Mômen xoắn (torque) |
| `do_mon_dao` | phút | Độ mòn dao tích luỹ |
| `loai_san_pham` | L/M/H | Hạng sản phẩm → **chi phối ngưỡng overstrain** |
| `ca_lam_viec` | Sáng/Chiều/Đêm | Ca (trong dữ liệu này là **nhiễu**) |
| `hong_hoc` | 0/1 | **Mục tiêu** (lớp thiểu số) |

**4 cơ chế hỏng** (dữ liệu tương đương AI4I 2020 / UCI) — đây là "nhãn không ngẫu nhiên" đề nhắc:

| Viết tắt | Cơ chế | Điều kiện kích hoạt điển hình |
|---|---|---|
| **TWF** | Hao mòn dao | `do_mon_dao` ∈ [200, 240] phút |
| **HDF** | Tản nhiệt kém | (process − air) < 8.6 K **VÀ** rpm < 1380 |
| **PWF** | Quá tải công suất | công suất cơ ∉ [3500, 9000] W |
| **OSF** | Quá tải căng thẳng | `do_mon_dao × momen_xoan` > {L:11000, M:12000, H:13000} |

> 🔑 Vì nhãn sinh ra từ **điều kiện ngưỡng phi tuyến**, các feature thô có tương quan tuyến tính yếu với target → **bắt buộc Feature Engineering** để lộ cơ chế.

---

# PHẦN 1 — KHÁM PHÁ DỮ LIỆU (EDA)

## 1.1 EDA (Exploratory Data Analysis)
- **① Định nghĩa:** giai đoạn khám phá — thống kê, vẽ đồ thị, phát hiện bất thường **trước khi** mô hình hoá.
- **④ Trong bài:** dùng EDA để (a) đo imbalance, (b) so phân phối A vs B tìm shift, (c) phát hiện các "điểm cài cắm" clipping.

## 1.2 Thống kê mô tả (descriptive statistics)
- **② Các đại lượng:** mean $\mu=\frac1n\sum x_i$; độ lệch chuẩn $\sigma=\sqrt{\frac1n\sum(x_i-\mu)^2}$; quartile Q1/Q2(median)/Q3 (25/50/75%); min/max.
- **③ Ví dụ số (momen_xoan, Train):** mean 39.94 Nm, std 9.96, min 3.50, Q1 33.30, median 39.89, Q3 46.66, max 76.02.
- **⑤ Dùng để phát hiện điểm cài cắm:** min `toc_do_quay` = **đúng 1180.00** lặp lại **309 lần** → dấu hiệu **clipping** (một phân phối liên tục thật không thể có 309 giá trị trùng khít).

## 1.3 Target Imbalance (mất cân bằng lớp)
- **① Định nghĩa:** lớp cần dự đoán (hỏng) chiếm tỷ lệ rất nhỏ → mô hình "đoán toàn 0" vẫn đạt accuracy cao nhưng vô dụng.
- **② Đo bằng:** tỷ lệ dương $\pi_+ = \frac{\#(y=1)}{n}$; hoặc tỷ lệ mất cân bằng $\frac{\#(y=0)}{\#(y=1)}$.
- **③ Ví dụ số:** Train $\pi_+ = 1031/14000 = 7.36\%$ → tỷ lệ **12.6 : 1**. Test = 7.95%.
- **⑤ Điểm cài cắm #3:** đề ghi "~3–5%" nhưng **thực đo ~7–8%** → phải dùng số thực khi đặt `class_weight`/ngưỡng, đừng tin mô tả đề.
- **Hệ quả:** **accuracy vô nghĩa** ở đây (đoán toàn 0 → 92.6% accuracy nhưng recall = 0). Phải dùng F1/AUC-PR.

## 1.4 Phân phối & so sánh A vs B
- **① Công cụ:** histogram (đếm theo bins) và **KDE** (Kernel Density Estimate — làm mượt histogram thành đường cong mật độ).
- **③ Ví dụ shift:** vẽ KDE `nhiet_do_moi_truong` hai tập → đường Test lệch phải ~2.5 K. Đây là "dấu hiệu shift sơ bộ" đề yêu cầu.

## 1.5 Correlation Heatmap
- **① Định nghĩa:** ma trận hệ số tương quan Pearson giữa các cặp biến, tô màu.
- **② Công thức Pearson:** $r_{XY}=\dfrac{\text{cov}(X,Y)}{\sigma_X\sigma_Y}=\dfrac{\sum(x_i-\bar x)(y_i-\bar y)}{\sqrt{\sum(x_i-\bar x)^2}\sqrt{\sum(y_i-\bar y)^2}}\in[-1,1]$.
- **③ Ví dụ số:** `nhiet_do_moi_truong` ↔ `nhiet_do_quy_trinh` có $r\approx 0.90$ (vật lý: process = air + ~10 K). Còn $r$ giữa các feature thô với target chỉ ~0.19 (do_mon_dao) — rất yếu.
- **④ Vì sao yếu:** cơ chế hỏng theo **ngưỡng** (phi tuyến) → Pearson (đo quan hệ *tuyến tính*) không bắt được → lý do phải FE + dùng mô hình cây.
- **⑤ Lỗi thường gặp:** thấy $r$ nhỏ rồi kết luận "feature vô dụng" — sai với quan hệ phi tuyến.

---

# PHẦN 2 — TIỀN XỬ LÝ & FEATURE ENGINEERING

## 2.1 Scaling (chuẩn hoá thang đo)
- **① Định nghĩa:** đưa các feature khác đơn vị (K, rpm, Nm, phút) về cùng thang để mô hình không thiên vị feature biên độ lớn.
- **② StandardScaler (z-score):** $z=\dfrac{x-\mu}{\sigma}$ — kết quả mean≈0, std≈1.
- **③ Ví dụ số:** `toc_do_quay` train $\mu=1540.3,\ \sigma=174.6$. Một điểm 1900 rpm → $z=(1900-1540.3)/174.6=+2.06$.
- **④ Loại nào cần?** Bắt buộc cho LogReg/SVM/KNN (dựa hệ số & khoảng cách); **cây (RF/XGBoost) KHÔNG cần** (bất biến với biến đổi đơn điệu).
- **Các scaler thay thế:**

| Scaler | Công thức | Khi nào |
|---|---|---|
| StandardScaler | $(x-\mu)/\sigma$ | mặc định; nhạy outlier |
| **RobustScaler** | $(x-\text{median})/\text{IQR}$ | **tốt hơn cho bài này** vì có clip đuôi |
| MinMax | $(x-\min)/(\max-\min)$ | cần [0,1]; rất nhạy min/max (mà min/max ở đây bị clip) |
- **⑤ Lỗi kinh điển:** xem mục 2.3.

## 2.2 Encoding (mã hoá biến phân loại)
- **① Định nghĩa:** biến chữ → số để mô hình xử lý.
- **② One-Hot Encoding:** mỗi giá trị thành 1 cột 0/1. `loai_san_pham` (L/M/H) → 3 cột; `ca_lam_viec` → 3 cột. `drop='if_binary'` bỏ 1 cột với biến nhị phân để tránh dư thừa.
- **⑤ Lỗi:** dùng **Label Encoding** (L=0,M=1,H=2) cho biến **danh nghĩa** → áp đặt thứ tự giả (H > M > L) mà mô hình tuyến tính hiểu nhầm là "gấp đôi".

## 2.3 Data Leakage & "Fit scaler trên Train → transform cả hai"
- **① Data leakage:** thông tin từ Test lọt vào lúc huấn luyện → hiệu năng ước lượng **lạc quan giả**, không tái lập được khi triển khai.
- **② Quy trình đúng:**
  ```
  scaler.fit(X_train)          # học μ, σ CHỈ từ Train
  X_train = scaler.transform(X_train)
  X_test  = scaler.transform(X_test)   # dùng lại μ, σ của Train
  ```
- **③ Điểm tinh tế dưới shift:** sau khi scale bằng $\mu,\sigma$ của Train, **Test KHÔNG có mean 0** — đúng và cố ý:
  - air temp Test sau scale: mean $\approx (302.5-300.0)/1.99 = +1.26$ (không phải 0).
  - 👉 Scaler **không xoá shift**, chỉ đổi đơn vị → shift vẫn còn để Phần 3 phát hiện.
- **⑤ Lỗi kinh điển:** `scaler.fit(pd.concat([train, test]))` hoặc `fit(X_test)` → vừa **leakage** vừa **xoá một phần shift** (ép mean Test về 0) → sai bản chất đề.

## 2.4 Xử lý Imbalance
### class_weight
- **① Định nghĩa:** gán trọng số lớn hơn cho lớp thiểu số trong hàm mất mát, **không** tạo dữ liệu giả.
- **② `balanced`:** $w_c=\dfrac{n}{K\cdot n_c}$ (n = tổng mẫu, K = số lớp, $n_c$ = số mẫu lớp c).
- **③ Ví dụ số:** lớp 1: $w_1=14000/(2\times1031)=6.79$; lớp 0: $w_0=14000/(2\times12969)=0.54$ → mỗi ca hỏng "nặng" gấp ~12.6 lần.
### SMOTE (Synthetic Minority Over-sampling Technique)
- **① Định nghĩa:** sinh mẫu thiểu số **nhân tạo** bằng nội suy tuyến tính giữa 1 điểm và láng giềng k-NN cùng lớp: $x_{new}=x_i+\lambda(x_{nn}-x_i),\ \lambda\sim U(0,1)$.
- **③ Ví dụ số:** Train trước SMOTE `[12969, 1031]` → sau `[12969, 12969]`.
- **⑤ Lỗi:** SMOTE **trên toàn bộ trước khi split** → mẫu giả rò rỉ sang fold validation. Đúng: chỉ trên **Train**, trong pipeline CV. Ở bài có shift, class_weight/`scale_pos_weight` thường **ổn định hơn** SMOTE.

## 2.5 Feature Engineering (lộ cơ chế vật lý)
- **① Định nghĩa:** tạo feature mới có ý nghĩa để mô hình "nhìn thấy" cơ chế hỏng.

| Feature giữ lại | Công thức | Cơ chế | Ví dụ số (row 0 Train, hạng H) |
|---|---|---|---|
| **chênh lệch nhiệt** | `nhiet_do_quy_trinh − nhiet_do_moi_truong` | HDF (tản nhiệt) | 311.80 − 301.21 = **10.59 K** |
| **công suất cơ** | $P=\tau\cdot\omega=\text{momen}\times\dfrac{2\pi\cdot\text{rpm}}{60}$ (W) | PWF (quá tải công suất) | $47.52\times1864.3\times\frac{2\pi}{60}=$ **9277 W** |
| **tích mòn×mômen** | `do_mon_dao × momen_xoan` | OSF (quá tải căng thẳng) | 210.9 × 47.52 = **10022** |
| **`osf_margin`** ⭐ | `tích mòn×mômen − ngưỡng(L/M/H)` | OSF **theo hạng SP** (tương tác 3 biến) | 10022 − 13000 = **−2978** (chưa vượt ngưỡng) |

> ❌ **Đã loại** `momen_xoan/toc_do_quay` (permutation importance = **0.000**) và `ca_lam_viec` (nhiễu). **Bộ feature cuối: 5 raw + 3 cơ chế + `osf_margin` + `loai_san_pham` = 10 feature** (xem Phụ lục Phần 6 trong notebook).

- **③ Diễn giải ví dụ:** row 0 có công suất **9277 W > 9000 W** → **kích hoạt PWF** (vượt biên công suất). Đây chính là "cơ chế" mà mô hình cần thấy.
- **② Chú ý đơn vị:** $\omega$ (rad/s) $=\dfrac{2\pi\cdot\text{rpm}}{60}$. Bỏ hệ số $2\pi/60$ vẫn tỷ lệ đúng nhưng sai đơn vị Watt.
- **④ Kiểm chứng (bắt buộc):** thêm 3 feature cơ chế → AUC 5-fold **0.867 → 0.878**; thêm `osf_margin` → **AUC-PR (Test) 0.681 → 0.693**. Đo bằng permutation importance + ablation, không loại theo cảm tính.
- **⑤ Điểm cài cắm #5 → `osf_margin`:** `loai_san_pham` biên phẳng **nhưng** quyết định **ngưỡng OSF** (L:11000/M:12000/H:13000). `osf_margin = mòn×momen − ngưỡng(hạng)` là cách khai thác nó. **Quy tắc FE cho mô hình cây:** chỉ thêm feature khi nó **mã hoá tương tác nhiều biến / ngưỡng theo điều kiện** (cây tự tìm ngưỡng trên 1 biến rồi).

---

# PHẦN 3 — PHÁT HIỆN & XỬ LÝ DISTRIBUTION SHIFT (TRỌNG TÂM)

## 3.1 PSI (Population Stability Index)
- **① Định nghĩa:** đo mức dịch phân phối của **một** feature giữa Train (kỳ vọng $e$) và Test (thực tế $a$) theo từng bin.
- **② Công thức:** $\text{PSI}=\sum_{i=1}^{B}(a_i-e_i)\cdot\ln\dfrac{a_i}{e_i}$ — $e_i,a_i$ = tỷ lệ mẫu rơi vào bin $i$ (bins thường chia theo **quantile của Train**, B=10).
- **③ Ví dụ tính tay — `momen_xoan` (10 bins, số thật):**

| bin | khoảng | e% (Train) | a% (Test) | đóng góp $(a-e)\ln\frac{a}{e}$ |
|---|---|---|---|---|
| 0 | (−∞, 27.14] | 9.99 | 16.63 | 0.0338 |
| 1 | (27.14, 31.62] | 10.00 | 13.68 | 0.0116 |
| 2 | (31.62, 34.80] | 9.98 | 11.92 | 0.0034 |
| … | … | … | … | … |
| 8 | (48.34, 52.67] | 10.00 | 6.03 | 0.0200 |
| 9 | (52.67, +∞) | 10.00 | 4.65 | 0.0410 |
| | | | **PSI** | **= 0.1195** |

→ Test có **nhiều mômen thấp hơn** (bin 0: 16.6% vs 10%) và **ít mômen cao** (bin 9: 4.65% vs 10%) → PSI = 0.12 = **shift nhẹ**.
- **② Quy ước:** `PSI < 0.1` không shift · `0.1–0.25` **nhẹ** · `> 0.25` **mạnh**.
- **③ Bảng thật của bài:** `nhiet_do_moi_truong` PSI = **1.08 (MẠNH)** > `nhiet_do_quy_trinh` 0.55 > `chenh_lech_nhiet` 0.32 > … > `do_mon_dao` **0.001 (không shift)**.
- **⑤ Lỗi:** chia bin trên **Test** thay vì Train; hoặc bin có 0 mẫu → $\ln 0=-\infty$ (phải kẹp $\epsilon=10^{-6}$).

## 3.2 KS-Test (Kolmogorov–Smirnov)
- **① Định nghĩa:** kiểm định thống kê so **2 phân phối liên tục** (không giả định dạng phân phối).
- **② Công thức:** thống kê $D=\sup_x\lvert F_{train}(x)-F_{test}(x)\rvert$ — khoảng cách **lớn nhất** giữa 2 hàm phân phối tích luỹ (CDF). Kèm **p-value**: p < 0.05 → khác biệt có ý nghĩa thống kê.
- **③ Ví dụ số:** `nhiet_do_moi_truong`: $D=0.4277$, $p\approx 0$ → hai CDF cách nhau tối đa 42.8% → shift rất mạnh (khớp PSI 1.08). `do_mon_dao`: $D=0.009$, $p=0.86$ → **không** khác → không shift.
- **④ PSI vs KS:** PSI cho **độ lớn** (mạnh/nhẹ) theo ngưỡng thực nghiệm; KS cho **kiểm định có ý nghĩa** (p-value). Dùng cả hai để chắc chắn.
- **⑤ Lỗi:** với n lớn (14000), KS **luôn** ra p rất nhỏ dù khác biệt nhỏ → **đừng chỉ nhìn p**, phải xem $D$ và PSI.

## 3.3 Drift Classifier (bộ phân loại trôi / domain classifier)
- **① Định nghĩa:** gán nhãn miền `Train=0 / Test=1`, huấn luyện classifier phân biệt → nếu phân biệt được tốt nghĩa là 2 tập khác nhau (có shift).
- **② Đo bằng AUC:** **0.5** = không phân biệt được = **không shift**; **→1.0** = shift càng mạnh.
- **③ Ví dụ số:** Drift AUC = **0.813** (shift mạnh, có thật).
- **Feature importance:** mức đóng góp mỗi feature → chỉ **"thủ phạm"**. Ở bài: `nhiet_do_moi_truong` (0.33) > `nhiet_do_quy_trinh` (0.20) > `chenh_lech_nhiet`/`toc_do_quay`.
- **④ Vì sao mạnh hơn PSI/KS:** PSI/KS xét **từng feature riêng**; drift classifier bắt cả shift **đa biến/tương tác**.

## 3.4 Importance Reweighting & Density-Ratio
- **① Ý tưởng:** cân lại mẫu Train sao cho phân phối Train "giống" Test khi huấn luyện → mô hình tối ưu cho B.
- **② Nền tảng (importance sampling):**
$$R_{test}(\theta)=\mathbb E_{x\sim P_{test}}[\ell]=\mathbb E_{x\sim P_{train}}\Big[\underbrace{\tfrac{P_{test}(x)}{P_{train}(x)}}_{w(x)}\ell\Big]$$
→ cân mỗi mẫu Train bằng $w(x)$ thì loss-có-trọng-số trên Train ước lượng **không chệch** loss trên Test.
- **② Ước lượng density-ratio bằng classifier (Bayes):**
$$\frac{p(x)}{1-p(x)}=\frac{P_{test}(x)}{P_{train}(x)}\cdot\frac{\pi_{train}}{\pi_{test}}\ \Rightarrow\ w(x)\propto\frac{p(x)}{1-p(x)}$$
với $p(x)$ = xác suất "thuộc Test" từ drift classifier; hằng số $\pi$ bị nuốt khi chuẩn hoá trung bình = 1.
- **③ Ví dụ số:** trọng số density-ratio thật: min 0.002, median 0.294, max 8.545 → mẫu Train "giống Test" được cân nặng hơn.
- **④ Điều kiện hợp lệ:** phải là **covariate shift** ($P(y\mid x)$ ổn định) — đã kiểm chứng ở bài (HDF 0.84→0.83…).
- **Phương pháp thay thế:** KMM (Kernel Mean Matching), KLIEP, uLSIF/RuLSIF (bị chặn, ít phương sai).
- **⑤ Lỗi:** đuôi trọng số nặng → phương sai bùng nổ. Khắc phục: **clip phân vị 99%** + chuẩn hoá (đã làm).

## 3.5 Threshold Calibration (hiệu chỉnh ngưỡng)
- **① Định nghĩa:** thay ngưỡng phân loại mặc định 0.5 bằng ngưỡng tối ưu F1 — cần thiết khi imbalance + shift.
- **② Cách chọn:** quét ngưỡng $t\in[0.05, 0.9]$, chọn $t^\ast=\arg\max_t F1(y_{train}, \mathbb 1[p\ge t])$ trên **OOF của Train** (không dùng nhãn Test → tránh leakage), rồi áp cho Test.
- **③ Ví dụ số:** $t^\ast=0.324$ (GB) → F1 Test: **0.721 → 0.729** (cải thiện). Với RandomForest $t^\ast=0.655$.
- **⑤ Lỗi:** chọn ngưỡng **trên nhãn Test** → leakage; hoặc giữ 0.5 cứng nhắc → recall thấp cho lớp hỏng.

---

# PHẦN 4 — XÂY DỰNG MÔ HÌNH & ĐÁNH GIÁ

## 4.1 Hyperparameter Tuning
### RandomizedSearchCV
- **① Định nghĩa:** dò siêu tham số bằng **lấy mẫu ngẫu nhiên** trong không gian phân phối tham số, mỗi cấu hình đánh giá qua cross-validation. Nhanh hơn GridSearchCV khi không gian lớn.
- **③ Ví dụ:** XGBoost dò 18 cấu hình (`n_estimators` 200–600, `max_depth` 3–9, `learning_rate` log-uniform 0.01–0.3…) → chọn theo AUC-PR.
### Stratified K-Fold
- **① Định nghĩa:** chia dữ liệu K phần, **giữ nguyên tỷ lệ lớp** trong mỗi fold.
- **④ Vì sao bắt buộc:** imbalance 7% → K-Fold thường có thể tạo fold **thiếu mẫu hỏng** → ước lượng nhiễu. Stratified đảm bảo mỗi fold ~7% hỏng.

## 4.2 Các metric đánh giá
### Ma trận nhầm lẫn (Confusion Matrix) — số thật của RandomForest @0.655

| | Dự đoán 0 | Dự đoán 1 |
|---|---|---|
| **Thực tế 0** | TN = 5438 | FP = 85 |
| **Thực tế 1** | FN = 119 | TP = 358 |

### Precision & Recall
- **② Precision** $=\dfrac{TP}{TP+FP}=\dfrac{358}{358+85}=\mathbf{0.808}$ — trong các ca *báo hỏng*, 80.8% đúng (ít báo động giả).
- **② Recall** $=\dfrac{TP}{TP+FN}=\dfrac{358}{358+119}=\mathbf{0.751}$ — bắt được 75.1% ca *thực hỏng* (bỏ sót 119).
- **④ Trong bảo trì:** **Recall quan trọng** (bỏ sót hỏng = dừng máy đột ngột, tốn kém), nhưng Precision cao tránh bảo trì thừa.
### F1-score
- **② Công thức:** $F1=\dfrac{2\cdot P\cdot R}{P+R}$ (trung bình điều hoà). $=\dfrac{2\times0.808\times0.751}{0.808+0.751}=\mathbf{0.778}$.
- **④ Vì sao trung bình điều hoà:** phạt nặng khi một trong hai (P hoặc R) thấp → không thể "ăn gian" bằng cách hi sinh cái kia. **Đề dùng F1 làm số so sánh chính.**
### AUC-ROC
- **② Định nghĩa:** diện tích dưới đường ROC (TPR theo FPR khi quét ngưỡng); TPR=Recall, FPR$=\frac{FP}{FP+TN}$. = xác suất mô hình xếp 1 mẫu dương ngẫu nhiên **cao hơn** 1 mẫu âm ngẫu nhiên. 0.5 = ngẫu nhiên, 1.0 = hoàn hảo.
- **③ Ví dụ:** RandomForest AUC-ROC = 0.885.
- **⑤ Cạm bẫy:** với imbalance mạnh, AUC-ROC **lạc quan** (FPR bị "pha loãng" bởi rất nhiều mẫu âm).
### AUC-PR (Average Precision)
- **② Định nghĩa:** diện tích dưới đường Precision–Recall. **Baseline = tỷ lệ dương** (ở đây ~0.08).
- **③ Ví dụ:** RandomForest AUC-PR = 0.686 (so baseline 0.08 → rất tốt).
- **④ Vì sao ưu tiên:** tập trung vào lớp thiểu số → **phù hợp imbalance hơn AUC-ROC**. Notebook tuning theo `average_precision`.
### Bảng so sánh mô hình (số thật)

| Mô hình | AUC-ROC | AUC-PR | F1@calib |
|---|---|---|---|
| **RandomForest** | 0.885 | **0.686** | **0.778** |
| XGBoost | 0.876 | 0.673 | 0.761 |
| XGBoost+reweight | 0.864 | 0.660 | — |
| LogReg | 0.745 | 0.246 | 0.314 |

→ **LogReg kém** (AUC-PR 0.25) vì tuyến tính không bắt được cơ chế ngưỡng → **bằng chứng** vì sao cần mô hình cây + FE.

---

# PHẦN 5 — TRÌNH BÀY BÁO CÁO

| Từ khoá | Ý nghĩa & ví dụ áp dụng cho bài |
|---|---|
| **Insight vận hành/bảo trì** | Kết luận hành động: *giám sát tản nhiệt (chênh lệch nhiệt thấp) & biên công suất*; *thay dao theo `tich_mon_momen` thay vì chỉ theo giờ*; *recalibrate ngưỡng khi chuyển sang Dây chuyền B nóng hơn*. |
| **Hạn chế (limitations)** | Test **ngoại suy** vượt biên Train (159 dòng nóng hơn train-max); nhãn có yếu tố ngẫu nhiên → trần hiệu năng hữu hạn; trọng số reweighting đuôi nặng. |
| **Hướng cải tiến** | Domain adaptation (CORAL/adversarial); conformal prediction để định lượng bất định vùng ngoại suy; thêm cảm biến rung/âm; giám sát PSI **online** (drift monitoring). |

---

# 🎯 BẢNG TỔNG: TỪ KHOÁ ↔ "ĐIỂM CÀI CẮM" TRONG DỮ LIỆU

| # | Điểm cài cắm | Bằng chứng số | Từ khoá liên quan | Cách xử lý |
|---|---|---|---|---|
| 1 | `toc_do_quay` clip sàn 1180 | 309 dòng = đúng 1180.00 | Thống kê mô tả, EDA | Ghi nhận censoring, không diễn giải nhầm |
| 2 | Clip biên `do_mon_dao`(253/0), `momen_xoan`(3.5) | Pile-up 2 tập | Scaling | Cân nhắc RobustScaler |
| 3 | Imbalance thực 7.36%/7.95% ≠ đề "3–5%" | 1031/14000 | Target imbalance | Dùng số thực đặt class_weight/ngưỡng |
| 4 | `ca_lam_viec` nhiễu thuần | Drift-importance ≈0.01; rate phẳng | Feature importance | Không over-engineer |
| 5 | `loai_san_pham` phẳng nhưng chi phối OSF | Ngưỡng 11000/12000/13000 | Feature engineering | Giữ + tạo `osf_margin` (AUC-PR 0.681→0.693) |
| 6 | Test ngoại suy vượt Train | 159 dòng > train-max; rpm 2414>2153 | Distribution shift | Cảnh báo extrapolation |
| — | Covariate shift (không phải concept drift) | HDF 0.84→0.83 ổn định | Importance reweighting | Reweighting + calibration hợp lệ |

---

# PHẦN BỔ SUNG — KHÁI NIỆM NÂNG CAO (feature selection · shift · trần F1)

> Các từ khoá xuất hiện ở giai đoạn tinh chỉnh feature và phân tích trần F1 (notebook `bai_tap_nang_cao_F1.ipynb`).

## B1. Mutual Information (thông tin tương hỗ)
- **① Định nghĩa:** đo mức phụ thuộc giữa feature X và target y — **kể cả phi tuyến** (khác Pearson chỉ đo tuyến tính). MI = 0 ⇔ độc lập; càng lớn càng liên quan.
- **② Ý tưởng:** $MI(X;y)=\sum P(x,y)\log\dfrac{P(x,y)}{P(x)P(y)}$ — "biết X giảm được bao nhiêu độ bất định của y".
- **③ Ví dụ thật:** `momen_xoan` có Pearson **0.006** (nhìn như vô dụng) nhưng **MI > 0** → có tín hiệu **phi tuyến**. → chỉ nhìn Pearson sẽ loại nhầm feature.
- **④ Khi nào dùng:** cơ chế phi tuyến/ngưỡng (đúng bài này) → dùng MI bổ sung cho heatmap Pearson.

## B2. Permutation Importance (tầm quan trọng bằng hoán vị)
- **① Định nghĩa:** đo feature quan trọng thế nào bằng cách **xáo trộn ngẫu nhiên** cột đó rồi xem hiệu năng **tụt** bao nhiêu. Tụt nhiều = quan trọng.
- **② Ưu điểm:** đo trên **mô hình đã huấn luyện + dữ liệu Test** → phản ánh tầm quan trọng *thực tế khi triển khai* (khác feature_importance nội bộ của cây dễ thiên vị).
- **③ Ví dụ thật:** `do_mon_dao` giảm AUC-PR **0.288** (trụ cột), `momen_tren_tocdo` giảm **0.000** (vô dụng → loại).
- **④ Dùng để:** chọn/loại feature bằng số, không cảm tính.

## B3. Ablation study (thử bỏ/giữ)
- **① Định nghĩa:** huấn luyện lại với **các bộ feature khác nhau** (bỏ nhóm này, giữ nhóm kia) để xem nhóm nào thực sự đóng góp.
- **③ Ví dụ thật:** bỏ feature thô → F1 **sập 0.544**; bỏ FE → F1 **0.690**; đủ bộ → **0.778**. → chứng minh cả feature thô lẫn FE đều cần.
- **④ Dùng để:** ra quyết định "giữ/bỏ" có bằng chứng.

## B4. Ensemble · Soft Voting (kết hợp mô hình)
- **① Định nghĩa:** gộp nhiều mô hình để dự đoán chung. **Soft voting:** trung bình *xác suất* (có trọng số) của các model.
- **③ Ví dụ thật:** LogReg + RF + XGBoost (trọng số 1:2:2) → F1 ~0.775 (không vượt RF đơn lẻ 0.78 vì đã chạm trần).
- **④ Khi nào giúp:** khi các model **sai khác nhau** (bổ khuyết nhau); ít giúp khi đã chạm trần Bayes.

## B5. CORAL (CORrelation ALignment) — một cách xử lý shift
- **① Định nghĩa:** căn chỉnh **hiệp phương sai** (cấu trúc tương quan) của Train cho khớp Test, bằng phép "tẩy trắng rồi tô màu lại" tuyến tính. Không cần nhãn Test.
- **③ Ví dụ thật:** ở bài này CORAL **làm TỆ hơn** (F1 0.778→0.743) vì shift là **dịch trung bình** chứ không phải đổi covariance → CORAL làm méo feature cơ chế.
- **④ Bài học:** **chọn phương pháp shift theo LOẠI shift**; CORAL hợp khi khác biệt nằm ở cấu trúc tương quan.

## B6. Resubstitution vs Cross-validation (phát hiện nhiễu nhãn)
- **① Định nghĩa:** **Resubstitution** = huấn luyện rồi dự đoán lại **chính Train** (đo khả năng *ghi nhớ*). **CV** = đo trên phần *chưa thấy* (khả năng *tổng quát*).
- **② Chẩn đoán:** nếu resub F1 ≈ 1.0 nhưng CV F1 thấp → **khoảng cách = nhiễu không khử được**.
- **③ Ví dụ thật:** RF resub **1.000** vs CV **0.755** → chênh 0.25 = nhiễu bản chất của nhãn.

## B7. Trần Bayes · Irreducible Error (trần tự nhiên)
- **① Định nghĩa:** mức hiệu năng **tối đa** mọi mô hình có thể đạt, do bản thân nhãn có **thành phần ngẫu nhiên** (cùng một đầu vào X có thể ra y khác nhau).
- **③ Bằng chứng thật:** vùng nguy hiểm nhất (`do_mon_dao>240`) chỉ hỏng **57.5%** (không phải 100%) → không thể đoán chắc → **trần F1 ~0.78**.
- **④ Ý nghĩa:** F1 ~0.78 **không phải xử lý kém** mà là trần. F1=0.99 mới đáng nghi rò rỉ nhãn.

## B8. Feature "sắc" · Margin theo ngưỡng khai phá
- **① Định nghĩa:** feature mã hoá **trực tiếp biên cơ chế** đã khai phá được, dạng `giá trị − ngưỡng` hoặc cờ 0/1.
- **③ Ví dụ thật:** `twf_margin = do_mon_dao − 240`, `pwf_low = max(2800 − công_suất, 0)`, `hdf_score`. Đạt **corr 0.18–0.25** (cao) + **PSI ≈ 0** (phân phối đều, không shift).
- **④ Giá trị:** nâng mạnh **model yếu** (LogReg F1 0.31→0.58) — vì tuyến tính không tự tìm ngưỡng; ít giúp cây (cây tự tìm).

## B9. Khai phá ngưỡng (Threshold Discovery)
- **① Định nghĩa:** tìm ngưỡng thật của cơ chế bằng cách **đo tỷ lệ hỏng theo bin** của một đại lượng, tìm chỗ tỷ lệ **nhảy vọt**.
- **③ Ví dụ thật:** tỷ lệ hỏng theo `do_mon_dao`: `(220,240]`→7% rồi `(240,255]`→**57%** ⇒ ngưỡng TWF ở **240** (không phải 200 mặc định AI4I).
- **④ Dùng để:** tạo feature sắc đúng với *chính bộ dữ liệu này*.

## B10. Trần F1 tuyệt đối (Absolute F1 ceiling)
- **① Định nghĩa:** F1 cao nhất khi được **chọn ngưỡng tối ưu bằng chính nhãn Test** (gian lận có kiểm soát, chỉ để *đo trần* — KHÔNG dùng để báo cáo).
- **③ Ví dụ thật:** trần tuyệt đối = **0.783** → mục tiêu 0.80 nằm ngoài tầm ⇒ *không cách hợp lệ nào* đạt 0.8.
- **⑤ Cảnh báo:** đây là công cụ chẩn đoán; báo cáo hiệu năng **phải** dùng ngưỡng chọn trên Train (tránh rò rỉ).

---
*Tài liệu đi kèm `bai_tap_cuoi_khoa.ipynb` (giải pháp chính) và `bai_tap_nang_cao_F1.ipynb` (phân tích trần F1) — mọi con số ví dụ đều tái lập được bằng code.*
