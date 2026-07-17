# 📋 Template / Checklist — Plan xử lý dữ liệu ML

> Quy trình chuẩn "lần sau cứ theo đây mà làm" cho một bài ML. Trọng tâm **Lớp LÀM (90%)** — chọn + làm sạch + biến đổi dữ liệu đúng trước khi chạy thuật toán ([[dinh-huong-hoc]]). Tick `[x]` từng mục khi xong.

**Cập nhật:** 2026-06-28 (từ L6 Decision Tree: **Bước 6 workflow tune** siêu tham số (validation curve → Grid/Random/Bayesian, watch VALIDATION không Test) · **Bước 7 bảng khoảng khuyến nghị** DT/RF/Boosting + triết lý tune đổi theo họ) · 2026-06-27 (từ PharmaDist: **Bước 0 quét ràng buộc** chống dắt mũi · **Bước 2.5 Tích hợp** · **Bước 4.5 Xây nhãn + censoring** · **Bước 5 chọn time-split vs random** · structural missing · importance bằng hệ số khi cấm cây) · 2026-06-21 (scale theo ĐỘ LỚN · 4 nỗi sợ leakage · ensemble · chính quy hóa ≠ chuẩn hóa) · **Liên quan:** [[xu-ly-du-lieu]] · [[eda-checklist]] · [[SECOND_BRAIN]]

> 🥇 **Nguyên tắc xuyên suốt — CHỐNG RÒ RỈ (leakage):** mọi thứ "học từ dữ liệu" (μ/σ để scale, median để điền, danh mục để encode, cột để chọn) phải **fit CHỈ trên train** rồi transform test. Gói trong `Pipeline` để khỏi quên. Sai chỗ này = điểm test ảo cao, ra đời sụp.

---

## ✅ Bước 0 — Xác định vấn đề  → [[xac-dinh-van-de]]
- [ ] Mục tiêu là gì? **Hồi quy** (đoán số) hay **Phân loại** (đoán lớp)?
- [ ] Đâu là cột **nhãn (y)**? Đâu là đặc trưng (X)?
- [ ] Sai lầm nào **tốn kém hơn** (FP hay FN)? → chốt **độ đo** từ đầu ([[danh-gia-mo-hinh]]).
- [ ] Với bài "nhiều file + vài từ khóa": **chọn đúng file/cột liên quan** trước (giải sai bài = vứt).
- [ ] 🚩 **Quét RÀNG BUỘC LOẠI 1 — đề/rubric ÉP** (biết TRƯỚC khi đụng data, nằm sẵn trong text đề). Mỗi ràng buộc vừa **override default**, vừa **AIM cho EDA soi đúng chỗ** (bật/tắt từng phần [[eda-checklist]]):

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
- [ ] `df.shape`, `df.dtypes`, `df.head()`, `df.describe()`
- [ ] `df.isnull().mean()` — tỉ lệ thiếu mỗi cột · `missingno` (bar/matrix/heatmap)
- [ ] Phân phối từng cột (hist), phát hiện **lệch (skew)** & **outlier** (boxplot)
- [ ] Ma trận **tương quan** ([[tuong-quan]]) — phát hiện cột trùng/đa cộng tuyến
- [ ] Cân bằng lớp? (bài phân loại) → nếu lệch nặng xem [[class-imbalance]]

## ✅ Bước 2 — Làm sạch

### 2a. Dữ liệu thiếu  → [[xu-ly-du-lieu-thieu]]
- [ ] Nhận diện cơ chế: **MCAR** (ngẫu nhiên) / **MAR** (phụ thuộc cột khác) / **MNAR** (phụ thuộc chính nó)
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
- [ ] Imputer **fit trên train** rồi transform test (leakage!)
- [ ] 🔑 **Structural / by-design missing (loại thứ 4 ngoài MCAR/MAR/MNAR):** thiếu vì **logic nghiệp vụ** (vd ticket `Pending`/`Escalated` ⇒ `satisfaction_score` trống) → **KHÔNG impute**, để NaN/tách cờ. Chỉ **true-missing** mới điền. Trộn 2 loại trong 1 cột → tách bằng cột logic trước. → chi tiết [[eda-checklist]] A4
- [ ] 💻 Template code: `code-practice/missing-data-missingno.ipynb` → `handle_missing(df, ...)`

> 🔑 **Keyword MICE** (`IterativeImputer`) = điền thiếu bằng cách **LẶP**: mỗi vòng huấn luyện một mô hình hồi quy cho từng cột, dùng các cột khác **dự đoán** cột thiếu, lặp đến hội tụ. Khác điền hằng số (median/mode) — đây là "**học một vùng rồi suy đoán thả vào**". Cùng họ model-based: **KNN Imputer** (theo lân cận). Nhận diện thiếu: thư viện **missingno**.

### 2b. Ngoại lai (outliers) & trùng lặp
- [ ] Phát hiện outlier: IQR / z-score / boxplot → xóa, cắt (clip), hoặc giữ + dùng **Robust scaling**
- [ ] `df.drop_duplicates()` — bỏ hàng trùng

## ✅ Bước 2.5 — Tích hợp nhiều bảng (CHỈ khi >1 file)  → [[eda-checklist]] Phần B
- [ ] 🚩 **Lọc theo STATUS trước khi tính bất cứ gì:** chỉ đếm "sự kiện thật" (vd `order_status='Completed'`) cho gap/RFM/monetary. Cancelled/Returned/Pending là đơn KHÔNG thành → loại, kẻo sai cả feature lẫn nhãn.
- [ ] Chốt **grain đích** (1 dòng = 1 nhà thuốc? 1 đơn?) **TRƯỚC** khi join/aggregate
- [ ] **Aggregate bảng con về grain đích** trước khi join (ticket/engagement → mức pharmacy)
- [ ] Tính **cột phái sinh** đề yêu cầu: `total_amount = SUM(qty×price)` rồi `×(1−discount)` — discount áp **SAU** khi SUM (trên tổng đơn, không phải từng dòng)
```
LEFT  → giữ TẤT CẢ bản ghi bảng gốc (giữ khách 0-đơn/censored để phân tích)
INNER → chỉ giữ bản ghi KHỚP (tập train cần đủ tín hiệu)
```
- [ ] `merge(indicator=True)` đếm match/orphan → xác nhận **không rớt dòng** ngoài ý muốn
- [ ] Báo cáo giải thích RÕ **vì sao LEFT vs INNER** mỗi join (tiêu chí chấm)

## ✅ Bước 3 — Biến đổi

### 3a. Chuẩn hóa (scaling)  → [[chuan-hoa-du-lieu]]
- [ ] **Có cần không?** 🔑 Quy tắc gốc: **cần khi thuật toán so sánh cột bằng ĐỘ LỚN** (khoảng cách: KNN/SVM/K-means · gradient: GD/NN · hệ số: Regularization · phương sai: PCA). **KHÔNG cần** khi chỉ xét THỨ TỰ trong từng cột (cây/RF/XGBoost).
```
mặc định            → Standardization (z-score)  ← phổ biến nhất, bền outlier "khá"
cần biên [0,1]      → Min-Max (ảnh, NN)           ← NHẠY outlier
nhiều outlier       → Robust (median/IQR)         ← bền outlier "tốt"
cột lệch nặng       → log/Box-Cox TRƯỚC rồi mới z-score
```
- [ ] Scaler **fit trên train** (leakage!) · chỉ scale cột số (đừng đụng nhãn / one-hot 0/1)
- [ ] 💻 Demo: `code-practice/feature-scaling-demo.ipynb`

### 3b. Mã hóa biến phân loại  → [[encode-categorical]]
```
danh nghĩa (không thứ tự)   → One-Hot
CÓ thứ tự (Nhỏ<Vừa<Lớn)     → Ordinal/Label
high-cardinality            → Target/Mean encoding (⚠️ rò rỉ → dùng CV)
nhãn đa lớp (output)        → one-hot cho softmax ([[softmax]])
```
- [ ] ⚠️ **One-hot + time-split:** mức mới chỉ xuất hiện ở test (khách/SP mới theo thời gian) → fit encoder **trên train**, `handle_unknown='ignore'`. High-cardinality (province 24, sub_category 24) + linear + ít dòng → **gộp mức hiếm** hoặc ưu tiên cột ít mức (region 3 thay province).

## ✅ Bước 4 — Đặc trưng

### 4a. Tạo đặc trưng  → [[feature-engineering]]
- [ ] Dùng **domain knowledge** tạo cột mới hữu ích (tỉ lệ, ngày→thứ/mùa, gộp nhóm...)
- [ ] 📅 **Năm → tuổi/thâm niên:** `establishment_year` → `tuoi = year(T) − establishment_year` (năm thô vô nghĩa tuyến tính với y; gộp luôn clip biên 1800/2099 → A7).

### 4b. Chọn đặc trưng  → [[feature-selection]]
```
Filter (nhanh)    → bỏ low-variance · bỏ cột tương quan cao · MI (bắt phi tuyến)
Wrapper (chính xác) → RFE / RFECV
Embedded          → Lasso (L1) tự bỏ cột · RF importance + Permutation
```
- [ ] Chọn đặc trưng **trong CV / chỉ trên train** (leakage!)
- [ ] ⚠️ **Nếu đề CẤM cây/SHAP** → bỏ "RF importance + Permutation" cho bài đó; importance = **|hệ số chuẩn hóa|** + odds ratio (logistic), **PHẢI StandardScaler trước** (không scale thì so độ lớn hệ số vô nghĩa).
- [ ] ⚠️ **VIF / corr TRƯỚC khi đọc hệ số:** feature collinear (vd Freq~Monetary 0.92) làm hệ số **lật dấu → importance thành rác**. Drop/gộp 1 trong cặp, hoặc **Ridge (L2)** co cụm hệ số collinear cho ổn định rồi mới rank.

## ✅ Bước 4.5 — Xây nhãn mục tiêu (khi y KHÔNG có sẵn cột)  → churn/reorder/survival
- [ ] **Chốt UNIT trước:** per-order (mỗi đơn = 1 hàng) hay **per-pharmacy snapshot tại T** (mỗi đối tượng = 1 hàng). UNIT đổi class balance **3% ↔ 25%** → chọn theo ngữ nghĩa đề ("đoán mỗi nhà thuốc" → per-pharmacy).
- [ ] Định nghĩa **mốc cắt T**; feature chỉ dùng dữ liệu **≤ T** (chống leakage)
- [ ] 🚩 **Gate MỌI bảng theo T, không riêng orders** — ticket/engagement sau T cũng rò tương lai (`is_ordered=1` gần T = rò nhãn thẳng).
- [ ] Chỉ tính "sự kiện thật" (status `Completed`) cho cả feature lẫn nhãn (xem Bước 2.5).
- [ ] Hồi quy: `days_until_next_event` = ngày từ sự kiện cuối ≤T → sự kiện kế
- [ ] Phân loại: `event_within_k_days` = có sự kiện trong (T, T+k]?  ⚠️ chọn `k` hợp **median gap** (gap dài mà k ngắn → lệch cực nặng)
- [ ] ⚠️ **Censoring** — phân nhóm & xử lý rõ:
```
≥2 sự kiện       → nhãn đầy đủ
đúng 1 sự kiện   → right-censored (loại/censor cho hồi quy; vẫn dùng cho phân loại nếu cửa sổ k đã quan sát đủ)
0 sự kiện        → ngoài quần thể model (giữ cho EDA/khuyến nghị)
```
- [ ] ⚠️ **Censoring bias NGƯỢC:** drop right-censored = drop **đúng nhóm gap dài / sắp ngủ đông** → E[gap quan sát] < E[gap thật], model lạc quan giả. **Báo cáo nêu rõ bias này**; để classification + khuyến nghị bắt nhóm ngủ đông.
- [ ] Kiểm **cân bằng lớp** ngay sau khi tạo nhãn → chốt độ đo (lệch nặng → F1/PR-AUC, `class_weight`, tune threshold)

## ✅ Bước 5 — Chia dữ liệu  → [[cross-validation]] · [[overfitting]]
- [ ] **Chọn KIỂU split theo bản chất dữ liệu:**
```
i.i.d / không trục thời gian → train_test_split(stratify=y)
CÓ trục thời gian            → TIME-SPLIT: sort theo ngày, cũ=train / mới=test. KHÔNG random
```
- [ ] ⚠️ time-split **mất stratify** → lệch lớp xử bằng `class_weight`/đổi threshold/chọn metric (KHÔNG phải stratified random)
- [ ] Chia **TRƯỚC** mọi bước fit ở trên · cân nhắc **K-Fold** (hoặc TimeSeriesSplit) để đánh giá ổn định
- [ ] Gói toàn bộ tiền xử lý + model vào **`Pipeline`** → fit/transform đúng chỗ

## ✅ Bước 6 — Chọn & Huấn luyện mô hình  → [[chon-mo-hinh]]
- [ ] Bắt đầu **baseline đơn giản** ([[linear-regression]] / [[logistic-regression]]) rồi nâng dần ([[random-forest]] → [[xgboost]])
- [ ] Bài đoán SỐ → hồi quy · bài đoán LỚP → phân loại
- [ ] Dữ liệu bảng → cây/boosting thường thắng; phi tuyến rõ → đừng dùng tuyến tính thuần
- [ ] ⚠️ **Nếu bị KHÓA model tuyến tính** (đề cấm cây) mà data phi tuyến → **MUA phi tuyến bằng FEATURE** (binning / interaction / log / poly), **ĐỪNG đổi sang cây**. Importance = |hệ số chuẩn hóa| + odds ratio (xem 4b).
- [ ] **Tinh chỉnh siêu tham số** ([[hyperparameter-tuning]]) — *prior khoanh vùng · curve định hướng · CV chấm điểm · Test chỉ 1 lần cuối*:
```
① baseline đơn giản → ② VALIDATION CURVE trên tham số quan trọng nhất → ③ chọn ĐỈNH validation
→ ④ Grid/RandomSearchCV quanh vùng đó (CV chấm, KHÔNG chạm Test) → ⑤ Test 1 lần cuối
```
- [ ] ⚠️ Bước ②③ nhìn điểm **VALIDATION** (CV/fold riêng), **KHÔNG** phải Test — "dừng khi *Test* giảm" = tune trên Test → điểm ảo. Không gian lớn → **Random/Halving/Bayesian (Optuna)** thay Grid (Grid vét cạn = kém thông minh nhất, chỉ hợp ≤2–3 tham số).

## ✅ Bước 7 — Chống Overfitting  → [[overfitting]] · [[bias-variance]]
```
Hướng 1: Regularization ([[regularization]]) — Ridge/Lasso/ElasticNet (GIỮ feature, CO hệ số → "đưa vào khung")
Hướng 2: Feature selection ([[feature-selection]]) — BỎ BỚT feature (nhiễu/trùng/ít liên quan y)
Ensemble: Bagging↓variance ([[random-forest]]) · Boosting↓bias ([[xgboost]]) · Stacking gộp nhiều model
Khác: thêm dữ liệu · đơn giản hóa model · early stopping · cross-validation
```
- [ ] Chọn λ / độ phức tạp tối ưu bằng **cross-validation** (RidgeCV/LassoCV) — tìm **đáy chữ U** của tổng lỗi ([[bias-variance]]: tổng lỗi GIẢM rồi mới TĂNG, không phải đi lên thẳng)
- [ ] ⚠️ **Đừng nhầm tên:** Chính quy hóa (regularization, chống overfit) ≠ Chuẩn hóa (scaling, tiền xử lý — Bước 3a)

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
- [ ] Chỉ đánh giá trên **tập test** (dữ liệu model chưa thấy)
- [ ] Nhìn confusion matrix + chốt theo chi phí FP/FN của bài toán

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
