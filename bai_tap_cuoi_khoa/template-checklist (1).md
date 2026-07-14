# 📋 Template / Checklist — Plan xử lý dữ liệu ML

> Quy trình chuẩn "lần sau cứ theo đây mà làm" cho một bài ML. Trọng tâm **Lớp LÀM (90%)** — chọn + làm sạch + biến đổi dữ liệu đúng trước khi chạy thuật toán ([[dinh-huong-hoc]]). Tick `[x]` từng mục khi xong.

**Cập nhật:** 2026-06-28 (từ L6 Decision Tree: **Bước 6 workflow tune** siêu tham số (validation curve → Grid/Random/Bayesian, watch VALIDATION không Test) · **Bước 7 bảng khoảng khuyến nghị** DT/RF/Boosting + triết lý tune đổi theo họ) · 2026-06-27 (từ PharmaDist: **Bước 0 quét ràng buộc** chống dắt mũi · **Bước 2.5 Tích hợp** · **Bước 4.5 Xây nhãn + censoring** · **Bước 5 chọn time-split vs random** · structural missing · importance bằng hệ số khi cấm cây) · 2026-06-21 (scale theo ĐỘ LỚN · 4 nỗi sợ leakage · ensemble · chính quy hóa ≠ chuẩn hóa) · **Liên quan:** [[xu-ly-du-lieu]] · [[eda-checklist]] · [[SECOND_BRAIN]]

> 🥇 **Nguyên tắc xuyên suốt — CHỐNG RÒ RỈ (leakage):** mọi thứ "học từ dữ liệu" (μ/σ để scale, median để điền, danh mục để encode, cột để chọn) phải **fit CHỈ trên train** rồi transform test. Gói trong `Pipeline` để khỏi quên. Sai chỗ này = điểm test ảo cao, ra đời sụp.

---

## 🧾 ĐỐI CHIẾU với bài làm hiện tại — `bai_tap_cuoi_khoa.ipynb` (cập nhật 2026-07-13)

> Bài **Predictive Maintenance** (dự đoán CNC hỏng ca kế, lệch lớp ~8%, **distribution shift** A→B). Đối chiếu từng bước bên dưới đã tick + ghi cell. **Kết luận: ĐỦ và vượt chuẩn** — chỉ còn 2 gap nhỏ mang tính hình thức.

| Bước | Trạng thái | Ghi chú |
|---|---|---|
| 0 Xác định vấn đề | ✅ Đủ | PL nhị phân, y=`hong_hoc`, quét ràng buộc split A→B + metric lệch lớp |
| 1 EDA | ✅ Đủ | shape/describe, 0 thiếu, hist/box, corr heatmap, cân bằng lớp, +covariate shift A/B |
| 2 Làm sạch | ⚠️ Gần đủ | 0 thiếu (2a N/A) · outlier giữ có lý do · **thiếu `drop_duplicates()`** |
| 2.5 Tích hợp nhiều bảng | ➖ N/A | 1 bảng |
| 3 Biến đổi | ✅ Đủ | Scale LogReg / passthrough cây · Ordinal+OneHot(`handle_unknown='ignore'`) · fit-train |
| 4 Đặc trưng | ✅ Xuất sắc | 3 feature khoảng-cách-tới-biên vật lý · importance qua corr/|hệ số|/cây · corr trước hệ số |
| 4.5 Xây nhãn | ➖ N/A | y có sẵn |
| 5 Chia dữ liệu | ✅ Đủ | line-split A→B (không random) · class_weight thay stratify · Pipeline + CV trên train |
| 6 Train | ✅ Xuất sắc | baseline→cây→ensemble · ≥3 model cây · RandomizedSearchCV scoring AUC-PR · IWV không nhìn nhãn B |
| 7 Chống overfit | ✅ Đủ | reg + feature + ensemble (bagging+boosting+stacking) · CV chọn tham số |
| 8 Đánh giá | ⚠️ Gần đủ | AUC-PR/F1/ROC + bootstrap CI + PR-curve · **chưa vẽ confusion matrix tường minh** |

**2 gap nhỏ nên bổ sung (không bắt buộc, cho tròn checklist):**
1. `train.duplicated().sum()` — xác nhận không có hàng trùng (Bước 2b).
2. `ConfusionMatrixDisplay` cho v6 tại ngưỡng chốt — trực quan FP/FN (Bước 8). *(hiện đã có P/R + PR-curve thay thế thông tin.)*

---

## ✅ Bước 0 — Xác định vấn đề  → [[xac-dinh-van-de]]
- [x] Mục tiêu là gì? **Hồi quy** (đoán số) hay **Phân loại** (đoán lớp)? → **Phân loại nhị phân** `hong_hoc`=0/1 (máy hỏng ca kế). `[0][2]`
- [x] Đâu là cột **nhãn (y)**? Đâu là đặc trưng (X)? → y=`hong_hoc`; X = 5 biến số + 2 biến phân loại. `[2]`
- [x] Sai lầm nào **tốn kém hơn** (FP hay FN)? → chốt **độ đo** từ đầu ([[danh-gia-mo-hinh]]). → FN (bỏ sót hỏng) đắt → ưu tiên Recall nhưng chốt **F1 / AUC-PR** (lệch lớp); báo cáo bàn chi phí + đề xuất 2 mức cảnh báo. `[7][102]`
- [x] Với bài "nhiều file + vài từ khóa": **chọn đúng file/cột liên quan** trước (giải sai bài = vứt). → ➖ 1 bộ dữ liệu (train A / test B) đã cho, dùng đủ cột. `[2]`
- [x] 🚩 **Quét RÀNG BUỘC LOẠI 1 — đề/rubric ÉP** → đã quét: **split ÉP A→B** (line-split, KHÔNG random) · metric **cấm accuracy** (lệch lớp) · y **có sẵn** (không tự xây) · **1 bảng** (không cần Bước 2.5) · **không cấm cây** (dùng RF/XGB). `[7][43]` (biết TRƯỚC khi đụng data, nằm sẵn trong text đề). Mỗi ràng buộc vừa **override default**, vừa **AIM cho EDA soi đúng chỗ** (bật/tắt từng phần [[eda-checklist]]):

  | Ràng buộc loại 1 (từ đề) | Override default | → Bật phần EDA | Nếu KHÔNG có |
  |---|---|---|---|
  | **Cấm tree, chỉ linear/logistic** | importance = \|hệ số\| (4b/6), khóa "cây thắng" | **C2** đa cộng tuyến + phi tuyến (hệ số là importance hợp lệ DUY NHẤT) | dùng RF → kệ collinearity |
  | **Time-split bắt buộc** | KHÔNG random (Bước 5) | **C4** drift train-cũ/test-mới + chọn mốc T | i.i.d → random stratified, khỏi vẽ drift |
  | **Target phải TỰ XÂY** | bật **Bước 4.5** | **Phần B** coverage + censoring | y có sẵn → bỏ qua |
  | **>1 bảng** | bật **Bước 2.5** | **toàn bộ Phần B** (FK/cardinality/grain/logic) | 1 bảng → skip Phần B |
  | **Metric đề ÉP** | ghi ra TRƯỚC khi train | (định hướng C3 cân bằng lớp) | — |

> ⚠️ **2 LOẠI ràng buộc, đừng gộp:** **Loại 1** = đề ÉP (biết trước → quét ở đây). **Loại 2** = data TỰ LỘ (lệch lớp, collinearity, leakage window, #censored) — **chỉ EDA mới phát hiện**. Loại 1 **quyết định EDA soi gì** để loại 2 lộ ra → cắn đúng chỗ.
> 🔁 **Không phải thác đổ — là VÒNG LẶP:** peek nhỏ **A0** (shape/dtypes/head → "có cột ngày = time-series") → chốt **loại 1** → **EDA targeted** (lộ **loại 2**) → feedback về quyết định kỹ thuật. Bước 0 là cái **AIM cho cả khẩu súng**; thiếu nó EDA thành "nhìn cho có", còn bài có ràng buộc thì dắt thẳng vào **RF + random split** như default.

## ✅ Bước 1 — Nạp & Khám phá (EDA)  → [[eda-checklist]] (chi tiết mọi phương pháp) · [[thong-ke]] · [[phan-loai-thong-ke]]
- [x] `df.shape`, `df.dtypes`, `df.head()`, `df.describe()` → shape (14000,8)/(6000,8) + `describe()` A & B. `[2][9]`
- [x] `df.isnull().mean()` — tỉ lệ thiếu mỗi cột · `missingno` → `isna().sum()` = **0 thiếu** cả train/test → khỏi impute (missingno ➖ N/A). `[2]`
- [x] Phân phối từng cột (hist), phát hiện **lệch (skew)** & **outlier** (boxplot) → hist chồng A/B + boxplot theo nhãn + hist theo density. `[12][18][25]`
- [x] Ma trận **tương quan** ([[tuong-quan]]) — phát hiện cột trùng/đa cộng tuyến → heatmap, **không đa cộng tuyến**, giữ cả 5 biến. `[21][23]`
- [x] Cân bằng lớp? (bài phân loại) → nếu lệch nặng xem [[class-imbalance]] → **~8% hỏng** (A 7.36% / B 7.95%) → cấm accuracy. `[5][7]`

## ✅ Bước 2 — Làm sạch

### 2a. Dữ liệu thiếu  → [[xu-ly-du-lieu-thieu]]
- [x] Nhận diện cơ chế: **MCAR** / **MAR** / **MNAR** → ➖ N/A cả mục 2a: **0 giá trị thiếu** nên toàn bộ phần điền/impute không áp dụng. `[2]`
```
ĐIỀN là mặc định (giữ data) — chỉ XÓA trong 2 case hẹp:
thiếu >50–60% (cột)  → XÓA cột   (điền 70% = BỊA 70% → variance/tín hiệu giả → bỏ trung thực hơn)
thiếu <5% & MCAR     → xóa vài hàng đó (mất ~2%, không lệch) HOẶC điền đơn giản
─ còn lại thì ĐIỀN: ─
số gần chuẩn         → mean    ·  số lệch/outlier → median ✅
phân loại            → mode (most_frequent)
có quan hệ giữa cột  → KNN     ·  muốn chính xác → MICE (học→suy đoán, fill TỪNG ô)
MNAR                 → thêm cờ is_missing RỒI mới điền
dùng XGBoost         → để model tự lo
```
> 📌 Điền (mean/median/KNN/MICE) = **lấp từng ô trống** bằng giá trị đại diện — KHÔNG phải gom nhiều hàng. Cột thiếu 70% thì điền cũng vô nghĩa → vẫn xóa.
- [x] Imputer **fit trên train** rồi transform test (leakage!) → ➖ N/A (0 thiếu).
- [x] 🔑 **Structural / by-design missing (loại thứ 4 ngoài MCAR/MAR/MNAR):** thiếu vì **logic nghiệp vụ** (vd ticket `Pending`/`Escalated` ⇒ `satisfaction_score` trống) → **KHÔNG impute**, để NaN/tách cờ. Chỉ **true-missing** mới điền. Trộn 2 loại trong 1 cột → tách bằng cột logic trước. → chi tiết [[eda-checklist]] A4
- [x] 💻 Template code: `code-practice/missing-data-missingno.ipynb` → `handle_missing(df, ...)` → ➖ N/A (0 thiếu).

> 🔑 **Keyword MICE** (`IterativeImputer`) = điền thiếu bằng cách **LẶP**: mỗi vòng huấn luyện một mô hình hồi quy cho từng cột, dùng các cột khác **dự đoán** cột thiếu, lặp đến hội tụ. Khác điền hằng số (median/mode) — đây là "**học một vùng rồi suy đoán thả vào**". Cùng họ model-based: **KNN Imputer** (theo lân cận). Nhận diện thiếu: thư viện **missingno**.

### 2b. Ngoại lai (outliers) & trùng lặp
- [x] Phát hiện outlier: IQR / z-score / boxplot → xóa, cắt (clip), hoặc giữ + dùng **Robust scaling** → boxplot đã soi; **giữ outlier** (đuôi cao/thấp = tín hiệu quá tải/thiếu tải, cây xử được). `[18][25][27]`
- [ ] ⚠️ `df.drop_duplicates()` — bỏ hàng trùng → **CHƯA chạy/kiểm** trùng lặp trong notebook. *(Gap nhỏ — nên thêm 1 dòng `train.duplicated().sum()` để xác nhận.)*

## ✅ Bước 2.5 — Tích hợp nhiều bảng (CHỈ khi >1 file)  → [[eda-checklist]] Phần B
> ➖ **N/A toàn bộ Bước 2.5** — bài chỉ có 1 bảng (train A + test B cùng schema), không join/aggregate.
- [x] 🚩 **Lọc theo STATUS trước khi tính bất cứ gì:** chỉ đếm "sự kiện thật" (vd `order_status='Completed'`) cho gap/RFM/monetary. Cancelled/Returned/Pending là đơn KHÔNG thành → loại, kẻo sai cả feature lẫn nhãn.
- [x] Chốt **grain đích** (1 dòng = 1 nhà thuốc? 1 đơn?) **TRƯỚC** khi join/aggregate → ➖ N/A (grain sẵn: 1 dòng = 1 máy/ca).
- [x] **Aggregate bảng con về grain đích** trước khi join → ➖ N/A.
- [x] Tính **cột phái sinh** đề yêu cầu → ➖ N/A (không có bảng con).
```
LEFT  → giữ TẤT CẢ bản ghi bảng gốc (giữ khách 0-đơn/censored để phân tích)
INNER → chỉ giữ bản ghi KHỚP (tập train cần đủ tín hiệu)
```
- [x] `merge(indicator=True)` đếm match/orphan → ➖ N/A (không join).
- [x] Báo cáo giải thích RÕ **vì sao LEFT vs INNER** mỗi join → ➖ N/A.

## ✅ Bước 3 — Biến đổi

### 3a. Chuẩn hóa (scaling)  → [[chuan-hoa-du-lieu]]
- [x] **Có cần không?** → LogReg **CẦN** → `StandardScaler`; cây (RF/XGB/ET) **KHÔNG** → `passthrough`. `[47][60][1182]` 🔑 Quy tắc gốc: **cần khi thuật toán so sánh cột bằng ĐỘ LỚN** (khoảng cách: KNN/SVM/K-means · gradient: GD/NN · hệ số: Regularization · phương sai: PCA). **KHÔNG cần** khi chỉ xét THỨ TỰ trong từng cột (cây/RF/XGBoost).
```
mặc định            → Standardization (z-score)  ← phổ biến nhất, bền outlier "khá"
cần biên [0,1]      → Min-Max (ảnh, NN)           ← NHẠY outlier
nhiều outlier       → Robust (median/IQR)         ← bền outlier "tốt"
cột lệch nặng       → log/Box-Cox TRƯỚC rồi mới z-score
```
- [x] Scaler **fit trên train** (leakage!) · chỉ scale cột số → `StandardScaler` chỉ trên `NUM_COLS`, bọc trong `Pipeline`/`ColumnTransformer` (fit-lại mỗi fold). `[1182][1368]`
- [x] 💻 Demo: `code-practice/feature-scaling-demo.ipynb` → ➖ N/A (demo tham khảo).

### 3b. Mã hóa biến phân loại  → [[encode-categorical]]
```
danh nghĩa (không thứ tự)   → One-Hot
CÓ thứ tự (Nhỏ<Vừa<Lớn)     → Ordinal/Label
high-cardinality            → Target/Mean encoding (⚠️ rò rỉ → dùng CV)
nhãn đa lớp (output)        → one-hot cho softmax ([[softmax]])
```
- [x] ✅ Encode: `loai_san_pham` (L<M<H, **có thứ tự**) → `OrdinalEncoder`; `ca_lam_viec` (danh nghĩa) → `OneHotEncoder`. `[1182]`
- [x] ⚠️ **One-hot + time-split:** mức mới chỉ xuất hiện ở test → dùng `OneHotEncoder(handle_unknown='ignore')`, fit trong Pipeline trên train. `[1184][1370][1753]` (khách/SP mới theo thời gian) → fit encoder **trên train**, `handle_unknown='ignore'`. High-cardinality (province 24, sub_category 24) + linear + ít dòng → **gộp mức hiếm** hoặc ưu tiên cột ít mức (region 3 thay province).

## ✅ Bước 4 — Đặc trưng

### 4a. Tạo đặc trưng  → [[feature-engineering]]
- [x] Dùng **domain knowledge** tạo cột mới hữu ích → **3 feature "khoảng-cách-tới-biên"** neo ngưỡng vật lý bất biến: `nguy_tan_nhiet` (HDF), `lech_cong_suat` (PWF), `bien_overstrain` (OSF). Đây là ý tưởng cốt lõi cả bài. `[50]`
- [x] 📅 **Năm → tuổi/thâm niên:** → ➖ N/A (không có cột năm). `establishment_year` → `tuoi = year(T) − establishment_year` (năm thô vô nghĩa tuyến tính với y; gộp luôn clip biên 1800/2099 → A7).

### 4b. Chọn đặc trưng  → [[feature-selection]]
```
Filter (nhanh)    → bỏ low-variance · bỏ cột tương quan cao · MI (bắt phi tuyến)
Wrapper (chính xác) → RFE / RFECV
Embedded          → Lasso (L1) tự bỏ cột · RF importance + Permutation
```
- [x] Chọn đặc trưng **trong CV / chỉ trên train** (leakage!) → xét corr với nhãn + RF importance + |hệ số| LogReg, đều trên train. `[53][56][63]`
- [x] ⚠️ **Nếu đề CẤM cây/SHAP** → importance = |hệ số chuẩn hóa| → ➖ N/A (không cấm cây); tuy vậy vẫn báo cáo cả |hệ số| LogReg (có StandardScaler) LẪN importance cây. `[56][63]`
- [x] ⚠️ **VIF / corr TRƯỚC khi đọc hệ số:** → heatmap corr, xác nhận không đa cộng tuyến nặng trước khi đọc hệ số. `[21][23]` feature collinear (vd Freq~Monetary 0.92) làm hệ số **lật dấu → importance thành rác**. Drop/gộp 1 trong cặp, hoặc **Ridge (L2)** co cụm hệ số collinear cho ổn định rồi mới rank.

## ✅ Bước 4.5 — Xây nhãn mục tiêu (khi y KHÔNG có sẵn cột)  → churn/reorder/survival
> ➖ **N/A toàn bộ Bước 4.5** — nhãn `hong_hoc` đã có sẵn dạng cột (không phải tự xây từ event/censoring).
- [x] **Chốt UNIT trước:** per-order (mỗi đơn = 1 hàng) hay **per-pharmacy snapshot tại T** (mỗi đối tượng = 1 hàng). UNIT đổi class balance **3% ↔ 25%** → chọn theo ngữ nghĩa đề ("đoán mỗi nhà thuốc" → per-pharmacy).
- [x] Định nghĩa **mốc cắt T** → ➖ N/A.
- [x] 🚩 **Gate MỌI bảng theo T, không riêng orders** — ticket/engagement sau T cũng rò tương lai (`is_ordered=1` gần T = rò nhãn thẳng).
- [x] Chỉ tính "sự kiện thật" (status `Completed`) → ➖ N/A.
- [x] Hồi quy: `days_until_next_event` → ➖ N/A (bài phân loại, nhãn có sẵn).
- [x] Phân loại: `event_within_k_days` → ➖ N/A.
- [x] ⚠️ **Censoring** — phân nhóm & xử lý rõ: → ➖ N/A.
```
≥2 sự kiện       → nhãn đầy đủ
đúng 1 sự kiện   → right-censored (loại/censor cho hồi quy; vẫn dùng cho phân loại nếu cửa sổ k đã quan sát đủ)
0 sự kiện        → ngoài quần thể model (giữ cho EDA/khuyến nghị)
```
- [x] ⚠️ **Censoring bias NGƯỢC:** → ➖ N/A. drop right-censored = drop **đúng nhóm gap dài / sắp ngủ đông** → E[gap quan sát] < E[gap thật], model lạc quan giả. **Báo cáo nêu rõ bias này**; để classification + khuyến nghị bắt nhóm ngủ đông.
- [x] Kiểm **cân bằng lớp** ngay sau khi tạo nhãn → đã kiểm ở Bước 1 (8% hỏng → F1/PR-AUC + `class_weight`/`scale_pos_weight` + tune threshold). `[5][7]`

## ✅ Bước 5 — Chia dữ liệu  → [[cross-validation]] · [[overfitting]]
- [x] **Chọn KIỂU split theo bản chất dữ liệu:** → **split theo dây chuyền A→B đã cho sẵn** (giống time/group-split, KHÔNG random) — đúng bản chất distribution shift. `[2][43]`
```
i.i.d / không trục thời gian → train_test_split(stratify=y)
CÓ trục thời gian            → TIME-SPLIT: sort theo ngày, cũ=train / mới=test. KHÔNG random
```
- [x] ⚠️ time-split **mất stratify** → xử bằng `class_weight`/threshold/metric → `class_weight='balanced'` (LogReg/RF), `scale_pos_weight` (XGB) + tune threshold + F1/PR-AUC. `[47][60]`
- [x] Chia **TRƯỚC** mọi bước fit · cân nhắc **K-Fold** → train A / test B tách sẵn; tune bằng `StratifiedKFold(5)` **trên train A**; OOF cho ensemble/IWV. `[60][85]`
- [x] Gói toàn bộ tiền xử lý + model vào **`Pipeline`** → fit/transform đúng chỗ → tất cả model bọc `Pipeline`/`ColumnTransformer` (encode+scale fit-lại mỗi fold). `[47][60]`

## ✅ Bước 6 — Chọn & Huấn luyện mô hình  → [[chon-mo-hinh]]
- [x] Bắt đầu **baseline đơn giản** rồi nâng dần → v0 LogReg thô (F1 0.231) → +FE v1 (0.352) → cây RF/XGB/ET v2 (~0.77) → reweight v3 → threshold v4 → ensemble v5/v6 (0.781). `[47][50][60][80][88][94][100]`
- [x] Bài đoán SỐ → hồi quy · bài đoán LỚP → phân loại → phân loại (đúng). `[47]`
- [x] Dữ liệu bảng → cây/boosting thường thắng; phi tuyến rõ → đừng tuyến tính thuần → xác nhận: cây vượt xa LogReg (0.35→0.77); EDA thấy tín hiệu phi tuyến/2-đuôi. `[27][60]`
- [x] ⚠️ **Nếu bị KHÓA model tuyến tính** → **MUA phi tuyến bằng FEATURE** → ➖ không bị khóa; nhưng vẫn áp dụng tinh thần này (3 feature hinge cứu LogReg từ 0.23→0.35). `[50]`
- [x] **Tinh chỉnh siêu tham số** ([[hyperparameter-tuning]]) → `RandomizedSearchCV` + `StratifiedKFold(5)`, scoring=`average_precision` (AUC-PR). `[60]` — *prior khoanh vùng · curve định hướng · CV chấm điểm · Test chỉ 1 lần cuối*:
```
① baseline đơn giản → ② VALIDATION CURVE trên tham số quan trọng nhất → ③ chọn ĐỈNH validation
→ ④ Grid/RandomSearchCV quanh vùng đó (CV chấm, KHÔNG chạm Test) → ⑤ Test 1 lần cuối
```
- [x] ⚠️ Bước ②③ nhìn điểm **VALIDATION**, KHÔNG phải Test → **kỷ luật IWV**: chọn model/ngưỡng/trọng số bằng F1-IWV trên OOF của train (không nhìn nhãn B); điểm B chỉ theo dõi. Dùng **RandomizedSearchCV** (không gian lớn → hợp lý hơn Grid). *(Lưu ý: không có ô `validation_curve` riêng bước ②③ — thay bằng Random search + IWV threshold sweep, chấp nhận được.)* `[85][88][100]` — "dừng khi *Test* giảm" = tune trên Test → điểm ảo. Không gian lớn → **Random/Halving/Bayesian (Optuna)** thay Grid (Grid vét cạn = kém thông minh nhất, chỉ hợp ≤2–3 tham số).

## ✅ Bước 7 — Chống Overfitting  → [[overfitting]] · [[bias-variance]]
```
Hướng 1: Regularization ([[regularization]]) — Ridge/Lasso/ElasticNet (GIỮ feature, CO hệ số → "đưa vào khung")
Hướng 2: Feature selection ([[feature-selection]]) — BỎ BỚT feature (nhiễu/trùng/ít liên quan y)
Ensemble: Bagging↓variance ([[random-forest]]) · Boosting↓bias ([[xgboost]]) · Stacking gộp nhiều model
Khác: thêm dữ liệu · đơn giản hóa model · early stopping · cross-validation
```
- [x] Chọn λ / độ phức tạp tối ưu bằng **cross-validation** → RandomizedSearchCV chọn `max_depth`/`min_samples_leaf`/`max_features` (cây), reg XGB, `C` LogReg; **Ensemble** (bagging RF/ET ↓variance + boosting XGB ↓bias + stacking). `[60][94][96]`
- [x] ⚠️ **Đừng nhầm tên:** Chính quy hóa ≠ Chuẩn hóa → đã phân biệt đúng (StandardScaler cho tiền xử lý vs regularization trong model).

> 📋 **KHOẢNG KHUYẾN NGHỊ siêu tham số (tree-based) — tra nhanh, KHÔNG đoán bừa** (= default sklearn + benchmark *tunability* Probst 2019 + đồng thuận Kaggle + scale theo n,p):
> | Model | Tham số | Khoảng | Ghi chú |
> |---|---|---|---|
> | **Decision Tree** | `max_depth` | **3–10** (khởi đầu 3–6) | mỗi tầng ×2 số lá (2ᵈ); >10 ~ overfit |
> | | `min_samples_leaf` | **10–50** hoặc 0.5–5% của n | =1 → học vẹt; n lớn → tăng |
> | | `min_samples_split` | thường để **mặc định 2** | phụ; nếu tune thì ~2× min_samples_leaf |
> | | `ccp_alpha` | từ `cost_complexity_pruning_path()` | pruning, CV chọn |
> | | `class_weight` | **'balanced'** | khi lệch lớp ([[class-imbalance]]) |
> | **Random Forest** | `n_estimators` | 100–500+ | nhiều = tốt, **KHÔNG overfit thêm** (chỉ chậm) |
> | | `max_features` | **'sqrt'** (PL) · **~p/3** (HQ) | ⭐ knob CHÍNH của RF (tạo đa dạng cây) |
> | | `max_depth` | thường **None** | bagging tự kìm variance → cây sâu OK |
> | **Boosting / [[xgboost]]** | `learning_rate` | **0.01–0.3** | ⭐ núm chính, ghép NGHỊCH n_estimators |
> | | `n_estimators` | 100–1000+ | + **early stopping**; lr thấp → cần nhiều cây |
> | | `max_depth` | **3–8 (NÔNG)** | weak learner — khác hẳn RF |
> | | `subsample` / `colsample_bytree` | 0.5–1.0 | lấy mẫu hàng/cột chống overfit |
> 💡 **Triết lý tune đổi theo HỌ:** cây đơn & boosting → **SIẾT độ sâu (3–8)** chống overfit · Random Forest → cây **SÂU vô tư**, chỉ chỉnh `max_features` + thêm cây. Khoảng **co giãn theo n** (`min_samples_leaf` ~ %n) **và p** (`max_features` ~ √p) → suy ra, đừng học vẹt.

> 🔥 **4 NỖI SỢ "ảo tưởng thành công" (con số đẹp nhưng dối trá) — kiểm trước khi tin kết quả:**
> | Nỗi sợ | Trông thì | Thật ra | Phòng thủ |
> |---|---|---|---|
> | **Overfitting** | train ~100% | học thuộc nhiễu → test tệ | CV · regularization · feature selection |
> | **Data leakage** ⚠️ đáng sợ NHẤT | cả **test** cũng cao | hỏng luôn thước đo → không biết mình sai | fit (scale/impute/encode/select) **chỉ trên train** |
> | **Lệch lớp** | Accuracy 99% | Recall 0% | F1/PR-AUC ([[class-imbalance]]) |
> | **Sampling bias** | giỏi trên mẫu | mẫu không đại diện | mẫu đủ lớn & đại diện ([[lay-mau]]) |
> 💡 *Kết quả đẹp bất thường → nghi RÒ RỈ trước tiên.*

> 🕵️ **BẪY ÂM THẦM — code chạy ngon, metric đẹp, nhưng SAI GỐC** (đặc biệt bài **tích hợp nhiều bảng + nhãn theo thời gian**). Độc hơn 4 nỗi sợ vì không nổ lỗi. **Verify trên data thật**, đừng tin default:
> | Bẫy | Chết âm thầm thế nào | Fix |
> |---|---|---|
> | **Status ≠ "sự kiện thật"** | đơn Cancelled/Returned/Pending lẫn vào gap/label/RFM → sai cả Target | chỉ **Completed** cho gap/label/monetary; loại Cancelled/Returned |
> | **Censoring bias NGƯỢC** | drop right-censored → train chỉ còn khách gap ngắn → "ai cũng đặt lại nhanh", **mù đúng nhóm sắp rời** | ý thức E[gap quan sát] < E[gap thật]; báo cáo bias; nhóm ngủ đông để classification bắt |
> | **Leakage qua MỌI bảng** | nhớ gate orders ≤T nhưng quên ticket/engagement → rò tương lai (`is_ordered=1` = rò nhãn thẳng) | gate **mọi bảng** theo T, không riêng orders |
> | **Collinearity phá hệ số** | corr cao (vd Freq~Monetary 0.92) → hệ số **lật dấu/vô nghĩa**, importance thành rác mà vẫn "có số" | **VIF TRƯỚC khi đọc hệ số**; drop/gộp hoặc Ridge co cụm |
> | **Lệch lớp + time-split** | Accuracy 97% = vô dụng; time-split **mất stratify** | F1/PR-AUC/Recall; `class_weight`+tune threshold (KHÔNG stratified random) |
> | **One-hot lệch cột train/test** | mức mới chỉ xuất hiện ở test → train thiếu cột → predict mismatch | fit encoder trên **train**, `handle_unknown='ignore'`; ưu tiên cột ít mức (region 3 thay province 24) |
> 💡 *UNIT phân tích (per-order vs per-pharmacy) đổi class balance từ **3% → 25%** — chốt UNIT trước khi build nhãn.*

## ✅ Bước 8 — Đánh giá  → [[danh-gia-mo-hinh]] · [[metric-hoi-quy]]
```
Phân loại cân bằng   → Accuracy
Phân loại lệch       → Precision/Recall/F1 · PR-AUC (KHÔNG Accuracy)
So sánh model        → AUC-ROC
Hồi quy              → MAE/RMSE/R²/Adjusted R²
```
- [x] ✅ Metric đúng: **AUC-PR / F1 / AUC-ROC / P / R** (KHÔNG accuracy) — leaderboard + PR-curve + **bootstrap 95% CI** cho F1. `[45][100][104]`
- [x] Chỉ đánh giá trên **tập test** (dữ liệu model chưa thấy) → chấm cuối trên B, chọn cấu hình bằng IWV (không rò nhãn B). `[100]`
- [ ] ⚠️ Nhìn **confusion matrix** + chốt theo chi phí FP/FN → có **P/R + PR-curve + chi phí FP/FN trong báo cáo** (đề xuất 2 mức cảnh báo), nhưng **CHƯA vẽ confusion matrix tường minh**. *(Gap nhỏ — nên thêm `ConfusionMatrixDisplay` cho v6 ở ngưỡng chốt.)* `[100][102]`

---

## 🎓 Bài học từ bài tích hợp lớn (PharmaDist) — *verify trước khi phán*

> 🔑 **Nguyên tắc số 1:** mọi con số/giả định phải **kiểm trên data thật TRƯỚC khi tin** — kể cả khi chính mình tự tin. Phiên PharmaDist, verify bắt được 5 lỗi mà chạy-cho-có thì trôi thẳng vào bài.

| Lỗi suýt mắc | Bài học |
|---|---|
| Bỏ feature **categorical** bằng trực giác (giữ noise, bỏ signal) | **Test CẢ categorical** (chi² vs nhãn), không chỉ numeric (point-biserial). Đừng chọn cột bằng cảm tính. |
| Tin `interval_std` là feature mạnh nhất | **Feature degeneracy:** feature cần ≥3 điểm (std khoảng cách giữa đơn) thoái hóa cho entity 1–2 đơn (NaN / std=0 giả) → ra nhiễu. Check % thoái hóa trước khi tin. |
| **AUC thấp → tưởng model kém** | AUC thấp bất thường → **nghi cách CHIA** (covariate shift do split trên feature mạnh, vd `last_order` ↔ `recency`) — đối xứng với *AUC cao → nghi leakage*. Đo lại bằng split matched / đa snapshot. |
| Đổ `R²<0` cho "tín hiệu yếu" | Regression **conditional-on-event** + target chặn cứng (cửa sổ [1,k] ngày) → R² thấp là **CẤU TRÚC** (trần by design + mẫu nhỏ + selection bias), không phải model dở. Nêu rõ đánh đổi. |
| Chặn invalid bằng `<0` | **Xác định THANG thật từ phân phối trước** (1–5 không phải 1–9 → lọt 0/7/9). Nhìn histogram rồi mới chặn miền. |
| Sửa ràng buộc 2 vế (vd `is_ordered ≤ is_responded`) | Biện minh **chọn vế nào & VÌ SAO** (không adjudicate được từ ngoài → giữ tín hiệu hiếm), không chỉ phát biểu lại ràng buộc. |

> 📌 **Single-T vs multi-snapshot:** single-T snapshot làm "time-split" thành holdout-theo-cohort (lệch recency → AUC giả thấp). **Multi-snapshot** (train mốc cũ → test mốc mới, `GroupKFold` theo entity) = forward-test thật + matched distribution + tăng mẫu → báo đúng năng lực.
> 📌 **Nộp notebook:** làm sạch *tất định* ngay; **hoãn điền median/mode vào `Pipeline` fit-train**. Fresh-run (Restart & Run All) trước khi nộp. PDF qua VS Code/Chromium (đừng LaTeX) để render Mermaid/ảnh.

---

## 🧭 Tóm tắt 1 dòng
**0 xác định vấn đề (+quét ràng buộc) → 1 EDA → 2 làm sạch → 2.5 tích hợp (nếu >1 bảng) → 3 biến đổi → 4 đặc trưng → 4.5 xây nhãn (nếu y chưa có) → 5 chia (time/iid, chống leakage) → 6 train → 7 chống overfit → 8 đánh giá đúng độ đo.**
> 🔗 Khớp 1-1 với 7 nhóm rubric của bài tích hợp dữ liệu — không còn điểm nào "mồ côi" (Tích hợp 1.5 → Bước 2.5 · Xây nhãn 1.0 → Bước 4.5).

## 📚 Nguồn
- Tổng hợp slide L1–L6 (TS. Cao Tiến Dũng) + các note atomic trong [[SECOND_BRAIN]].
- Template code: `code-practice/` (missing-data-missingno · logistic/softmax demos).
