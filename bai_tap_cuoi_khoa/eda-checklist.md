# 🔍 EDA Checklist — Mọi phương pháp khám phá dữ liệu

> Checklist con của [[template-checklist]] **Bước 1 (EDA)**. Mục tiêu: **liệt kê ĐẦY ĐỦ mọi phương pháp** có thể áp dụng để khám phá dữ liệu → khi làm thật cứ quét từ trên xuống, **không sót**. Tick `[ ]` mục nào áp dụng cho bài đang làm.

**Cập nhật:** 2026-06-27 (bổ sung từ bài PharmaDist: **missing có cấu trúc** · **domain-bound năm/tuổi** · **cờ nhị phân trộn biểu diễn**) · **Cha:** [[template-checklist]] · [[SECOND_BRAIN]] · **Nền lý thuyết:** [[thong-ke]] · [[phan-loai-thong-ke]]

> 🎯 **EDA để làm gì? (3 mục đích — đừng EDA cho có)**
> 1. **Hiểu dữ liệu** → biết có gì trong tay (phân phối, đơn vị, ý nghĩa cột).
> 2. **Phát hiện vấn đề** → missing / outlier / nhiễu / sai logic → làm input cho [[xu-ly-du-lieu]] (Bước 2).
> 3. **Định hướng quyết định sau** → chọn cách điền thiếu, scale, encode, chọn model & **độ đo** ([[danh-gia-mo-hinh]]). EDA thấy lệch lớp → bỏ Accuracy ngay.

> ⚠️ **EDA chỉ NHÌN, chưa SỬA.** Phát hiện và ghi lại vấn đề ở đây; việc xử lý để sang Bước 2. Và mọi thống kê "học từ dữ liệu" để xử lý sau (median, μ/σ...) phải tính **chỉ trên train** → tránh [[overfitting]]/leakage.

> 🎯 **EDA phải được AIM bởi ràng buộc LOẠI 1 (đề ÉP) ở [[template-checklist]] Bước 0 — đừng soi tất cả như nhau.** Ràng buộc bật/tắt từng phần: cấm tree → **C2** (collinearity/phi tuyến) · time-split → **C4** (drift + mốc T) · target tự xây → **Phần B** (coverage/censoring) · >1 bảng → **toàn bộ Phần B**.
> 🔁 EDA chính là nơi **ràng buộc LOẠI 2 (data tự lộ)** xuất hiện — lệch lớp, đa cộng tuyến, leakage window, #censored → quay lại chỉnh quyết định kỹ thuật (vòng lặp, không thác đổ).

---

## 🅰️ PHẦN A — EDA mức TỪNG BẢNG (per-file / univariate)

### A0. Nhìn tổng quan (làm đầu tiên cho mỗi file)
- [ ] `df.shape` — số dòng × cột (khớp với đề chưa?)
- [ ] `df.head()` / `df.sample(5)` / `df.tail()` — mắt thường nhìn dữ liệu thật
- [ ] `df.info()` — dtype + non-null count + bộ nhớ
- [ ] `df.dtypes` — **cột nào bị sai kiểu?** (số đang là `object`, ngày đang là `string`...)
- [ ] `df.describe(include='all')` — thống kê số + đếm categorical một lượt
- [ ] `df.nunique()` — số giá trị duy nhất mỗi cột (dò ID, hằng số, high-cardinality)

### A1. Biến SỐ — mô tả 3 mặt → [[phan-loai-thong-ke]]
> ① Trung tâm · ② Độ biến thiên · ③ Hình dạng — **phải đi cùng nhau** (cùng mean vẫn khác hẳn).

- [ ] **① Trung tâm:** mean, **median** (lệch outlier thì median > mean), mode → [[ky-vong-trung-binh]]
- [ ] **② Biến thiên:** range (max−min), **IQR** (Q1/Q3), variance, std → [[phuong-sai]]
- [ ] **③ Hình dạng:** **skewness** (lệch → cân nhắc log/Box-Cox ở Bước 3), **kurtosis** (đuôi dày = nhiều cực đoan)
- [ ] **Histogram** mỗi cột số — nhìn phân phối (1 đỉnh / nhiều đỉnh / lệch)
- [ ] **Boxplot / violin** — lộ outlier + quartile cùng lúc
- [ ] **KDE / density** — phiên bản mượt của histogram
```python
df.describe()
df[num_cols].skew(); df[num_cols].kurt()
df[col].hist(bins=50); df.boxplot(column=col)
```

### A2. Biến PHÂN LOẠI (categorical) → đếm
- [ ] `value_counts()` + `value_counts(normalize=True)` — tần suất & **tỷ lệ %**
- [ ] **Bar chart** (đừng pie nếu >5 nhóm) cho mỗi cột phân loại
- [ ] **Cardinality:** ít nhóm (one-hot được) hay quá nhiều (→ target encoding sau, [[encode-categorical]])?
- [ ] Dò **nhãn rác / trùng nghĩa**: khoảng trắng thừa, `"Net30"` vs `" net30 "`, hoa/thường, sai chính tả
- [ ] **Cột cờ nhị phân (0/1)** có bị trộn biểu diễn không? `Yes/No/True/TRUE/1/0/"1"` → `value_counts(dropna=False)` để lộ, rồi quy chuẩn về {0,1} ở Bước 2. *(dấu hiệu sớm: cột đáng lẽ số nhưng `dtype=object` — vd `is_responded`)*
- [ ] Cột thực ra là **ordinal** (Nhỏ<Vừa<Lớn, credit_tier A>B>C)? → đánh dấu để encode đúng

### A3. Biến THỜI GIAN (datetime) — ⭐ quan trọng vì bài split theo thời gian
> ⚠️ Mục này cho **cột ngày/giờ thật**. Cột **năm/tuổi lưu dạng SỐ** không parse datetime → xử ngay dưới đây:
- [ ] **Biến năm/tuổi lưu dạng SỐ** (`establishment_year`): chặn biên `[năm hợp lý, năm hiện tại]` **thay vì IQR**. Năm **tương lai** hoặc **sentinel** (2099, 9999) = disguised-missing dạng số → quy về NaN.
- [ ] **Parse được không?** Dò **nhiều định dạng** trong cùng cột (`18/03/2021` vs `2022-01-16` vs `12-28-2022`)
- [ ] `pd.to_datetime(..., errors='coerce')` rồi đếm **NaT** = số ngày parse hỏng
- [ ] **min / max / range** thời gian — dữ liệu trải từ bao giờ đến bao giờ?
- [ ] Ngày **vô lý**: tương lai, trước khi DN mở, `onboarding_date` < `establishment_year`...
- [ ] Tách thành phần: year/month/day/dow/quarter (dùng cho feature & time-split sau)
- [ ] Vẽ **số bản ghi theo thời gian** (theo tháng) — phát hiện khoảng trống / mùa vụ / xu hướng

### A4. DỮ LIỆU THIẾU (missing) → [[xu-ly-du-lieu-thieu]]
- [ ] `df.isnull().mean().sort_values()` — **tỷ lệ thiếu** mỗi cột (đề báo ~5%)
- [ ] `missingno.bar` (đếm) · `matrix` (vị trí thiếu theo dòng) · `heatmap` (thiếu **cùng nhau** không?)
- [ ] Đoán **cơ chế** — 4 loại (3 "bị mất" → ĐIỀN · 1 "vốn không có" → KHÔNG điền):
```
MCAR / MAR / MNAR        → ĐIỀN (median/mode/KNN/MICE, fit train)
STRUCTURAL / by-design   → KHÔNG điền — giá trị không tồn tại theo logic
```
- [ ] **Phân loại missing theo BẢN CHẤT, không chỉ cơ chế:**
  - **Structural / by-design** (giá trị *không tồn tại*): vd ticket `Pending`/`Escalated` ⇒ `satisfaction_score` trống → **KHÔNG impute**, để NaN hoặc tách cờ riêng.
  - **True-missing** (có tồn tại nhưng bị mất): Resolved mà thiếu điểm → mới impute.
  - ⚠️ Trộn 2 loại trong một cột (như 30% thiếu của `satisfaction_score`) → **tách bằng cột logic** (`groupby(status)`) trước khi quyết chiến lược.
- [ ] ⚠️ Thiếu "trá hình" (disguised): `0`, `-1`, `999`, năm `2099`, `"NA"`, chuỗi rỗng → quy về NaN (xem A7)
- [ ] **Chưa điền ở đây** — chỉ ghi nhận, chiến lược điền để Bước 2 (fit trên train!)

### A5. NGOẠI LAI (outliers)
- [ ] **IQR rule:** ngoài `[Q1−1.5·IQR, Q3+1.5·IQR]`
- [ ] **z-score:** `|z| > 3` (chỉ hợp dữ liệu gần chuẩn)
- [ ] **Boxplot** từng cột + theo nhóm
- [ ] Phân biệt **outlier thật** (VIP chi cực nhiều — giữ) vs **lỗi nhập** (giá âm, tuổi 999 — sửa/bỏ)

### A6. TRÙNG LẶP & KHÓA
- [ ] `df.duplicated().sum()` — dòng trùng hoàn toàn
- [ ] Khóa chính (`order_id`, `pharmacy_id`...) có **unique** không? `df[key].is_unique`
- [ ] Trùng một phần (cùng pharmacy + ngày) — có phải double-count?

### A7. SANITY / RÀNG BUỘC MIỀN (domain validity)
> ⚠️ **Biên NGỮ NGHĨA ≠ outlier thống kê (A5):** IQR/z-score bắt giá trị *hiếm*; A7 bắt giá trị *vô lý về logic* dù không hiếm (vd năm `2099` nằm trong IQR vẫn vô nghĩa).
- [ ] Giá trị **âm** ở cột không thể âm: `quantity`, `unit_price`, `base_price`, `offer_value`
- [ ] Giá trị **ngoài miền**: tỷ lệ ngoài [0,1] (`discount_applied`), điểm hài lòng ngoài thang; năm/tuổi ngoài biên (→ A3)
- [ ] **Sai kiểu**: số lưu dạng `"1.800"` (dấu chấm ngăn nghìn), `quantity` lẻ thập phân vô lý
- [ ] Danh mục **ngoài từ điển hợp lệ**: `order_status`, `region`, `drug_type` có giá trị lạ?

---

## 🅱️ PHẦN B — EDA mức NHIỀU BẢNG (multi-table) ⭐ đặc thù bài PharmaDist

> Bài có 7 bảng nối nhau → **lỗi JOIN = sai cả bài**. EDA quan hệ trước khi tích hợp (Bước 3).

- [ ] **Vẽ/mô tả ERD** — khóa nối từng cặp bảng (đề đã cho quan hệ, xác nhận lại bằng data)
- [ ] **Cardinality** mỗi quan hệ: 1–1 / 1–n / n–n? (1 order có nhiều order_lines = 1–n)
- [ ] **Toàn vẹn khóa ngoài (orphan rows):** mọi `order_lines.order_id` có nằm trong `orders`? `orders.pharmacy_id` có trong `pharmacies`?
```python
set(order_lines.order_id) - set(orders.order_id)   # FK mồ côi → rỗng là tốt
```
- [ ] **Độ phủ JOIN:** bao nhiêu % nhà thuốc **không có đơn nào**? bao nhiêu chỉ **1 đơn**? → quyết định **LEFT vs INNER** + xử lý **censored** (Bước 5)
- [ ] **Grain (độ mịn) đích:** 1 dòng = 1 nhà thuốc hay 1 đơn? → chốt trước khi aggregate
- [ ] **Ràng buộc logic LIÊN BẢNG / liên cột** (đề nêu rõ):
  - `is_ordered ≤ is_responded` (không thể đặt mà chưa phản hồi)
  - ticket `Pending`/`Escalated` ⇒ `satisfaction_score` phải **trống**
  - `order_date` ≥ `onboarding_date` của nhà thuốc đó?
- [ ] **Đối chiếu trùng khái niệm:** `region` ở pharmacies vs warehouses có nhất quán không?

---

## 🅾️ PHẦN C — EDA hướng tới TARGET & MODEL (bivariate / multivariate)

> Sau khi hiểu từng cột → xem **quan hệ giữa các cột** và **với nhãn y**. Định hướng feature & model.

### C1. Quan hệ từng cặp (bivariate)
| Cặp kiểu | Công cụ | Xem gì |
|---|---|---|
| Số ↔ Số | scatter, **Pearson/Spearman corr** | tuyến tính? phi tuyến? → [[tuong-quan]] |
| Phân loại ↔ Số | `groupby().mean()`, boxplot theo nhóm | nhóm nào khác biệt? |
| Phân loại ↔ Phân loại | `crosstab`, stacked bar, chi-square | có liên hệ? |

### C2. Đa biến / đa cộng tuyến → [[tuong-quan]] · [[feature-selection]]
- [ ] **Ma trận tương quan** (heatmap) — phát hiện cột **trùng tín hiệu** (corr > 0.9)
- [ ] **VIF** nếu nghi đa cộng tuyến (hại hồi quy tuyến tính/logistic — model chính của bài)
- [ ] **Pairplot** cho nhóm cột số quan trọng

### C3. Quan hệ với NHÃN y (khi đã có target — phối hợp Bước 5)
- [ ] Phân phối feature **theo từng lớp y** (reorder vs không) — feature nào tách lớp tốt?
- [ ] Với target hồi quy: scatter feature vs `days_until_next_order` + corr
- [ ] **Cân bằng lớp** (nếu phân loại): tỷ lệ `will_reorder_within_45_days` → lệch nặng? → [[class-imbalance]], chốt metric F1/PR-AUC ngay

### C4. EDA THỜI GIAN (vì split theo thời gian) ⭐
- [ ] Vẽ **target / số đơn theo thời gian** — có **xu hướng / mùa vụ** không?
- [ ] So phân phối **giai đoạn train (cũ) vs test (mới)** — có **drift** không? (phân phối đổi → model hết thiêng)
- [ ] Xác định **mốc cắt thời gian** hợp lý để chia train/test (Bước 6)

### C5. Tỉnh táo chống tự lừa → playbook "4 nỗi sợ"
- [ ] **Leakage check:** có cột nào "tương lai" rò vào feature không? (vd thông tin sau khi đặt đơn)
- [ ] Cột **tương quan gần như hoàn hảo với y** → nghi rò rỉ trước khi mừng

---

## 🧰 Bảng tra nhanh: phương pháp → công cụ

| Cần làm | pandas / thư viện |
|---|---|
| Tổng quan | `shape` `info()` `describe()` `dtypes` `nunique()` |
| Phân phối số | `hist()` `boxplot()` `.skew()` `.kurt()` · seaborn `histplot/kdeplot` |
| Phân loại | `value_counts(normalize=True)` · seaborn `countplot` |
| Thiếu | `isnull().mean()` · **missingno** `bar/matrix/heatmap` |
| Outlier | IQR thủ công · `zscore` (scipy) · boxplot |
| Tương quan | `df.corr()` · seaborn `heatmap` · `pairplot` |
| Cat↔num | `groupby().agg()` · boxplot theo nhóm |
| Cat↔cat | `pd.crosstab()` · `chi2_contingency` (scipy) |
| Thời gian | `pd.to_datetime(errors='coerce')` · resample theo tháng |
| Khóa/JOIN | `is_unique` · phép trừ tập hợp · `merge(indicator=True)` |

---

## 📤 Đầu ra kỳ vọng của EDA (mang sang Bước 2–6)
- [ ] **Bảng "Vấn đề dữ liệu phát hiện được"**: cột | loại lỗi (thiếu/âm/outlier/sai ngày/vi phạm logic) | mức độ | hướng xử lý dự kiến
- [ ] **ERD + mô tả khóa nối** (cho Bước 3 tích hợp)
- [ ] **Danh sách feature tiềm năng** + cột nghi bỏ (cho Bước 4)
- [ ] **Quyết định độ đo** (lệch lớp? → F1/PR-AUC) + **mốc cắt thời gian** (cho Bước 6)

## 🧭 Tóm tắt 1 dòng
**Tổng quan → từng cột (số/phân loại/ngày) → thiếu/outlier/trùng/sanity → quan hệ NHIỀU BẢNG (khóa/cardinality/logic) → quan hệ với y + thời gian + leakage → chốt bảng vấn đề & độ đo.**

## 🔗 Liên kết
- **Cha:** [[template-checklist]] (Bước 1) · **Nền:** [[thong-ke]] · [[phan-loai-thong-ke]] · [[tu-vung-thong-ke]]
- **Dẫn sang:** [[xu-ly-du-lieu]] · [[xu-ly-du-lieu-thieu]] (Bước 2) · [[feature-engineering]] (Bước 4) · [[danh-gia-mo-hinh]] · [[class-imbalance]]
- **Tương quan/chọn cột:** [[tuong-quan]] · [[feature-selection]]

## 📚 Nguồn
- Tổng hợp slide L1 (Thống kê mô tả — TS. Cao Tiến Dũng) + các note atomic trong [[SECOND_BRAIN]].
