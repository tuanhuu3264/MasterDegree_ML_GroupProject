# 📖 Giải thích notebook theo từng cell

> File này giảng **tuần tự từng cell** của `bai_tap_cuoi_khoa.ipynb` — mỗi mục nói: cell đó **làm gì**,
> **vì sao**, và **kết quả thật** ra sao. Đọc dọc từ trên xuống là hiểu cả bài. Số trong `[ ]` là chỉ số cell.
>
> ℹ️ Notebook có **28 ô "💡 Hiểu đơn giản"** xen kẽ (ngay sau mỗi cell code EDA/FE/Shift/Model) — đó là bản
> giải thích lời-thường cho người mới; file này bổ sung thêm số liệu & mạch logic. Cell số đã cập nhật theo
> notebook 107 cells.

**Bài toán 1 câu:** dự đoán máy CNC **hỏng trong ca kế tiếp** (`hong_hoc`=0/1, ~8% hỏng). Train = **Dây chuyền A**
(nhà máy cũ), Test = **Dây chuyền B** (nhà máy mới, nóng hơn) → **distribution shift**: cùng cơ chế hỏng nhưng
phân phối đầu vào dịch. Nhiệm vụ: model học trên A vẫn tốt trên B.

**Ý tưởng xuyên suốt:** chế đặc trưng bám **ngưỡng vật lý bất biến** → ranh giới học trên A **dùng thẳng** trên B.

---

## PHẦN 0 — Setup `[0–2]`

- `[0]` Markdown mở đầu: giới thiệu bài toán, bảng A vs B, chiến lược "experiment-driven" (thử nhiều version v0,v1,… chấm bằng cùng 1 leaderboard).
- `[1]` Tiêu đề mục Setup.
- `[2] CODE` — nhập thư viện, `RANDOM_STATE=42` (để chạy lại ra y hệt), đọc `train.csv`/`test.csv`, khai báo cột:
  - **5 biến số** `NUM_COLS`: nhiệt độ môi trường, nhiệt độ quy trình, tốc độ quay, mômen xoắn, độ mòn dao.
  - **2 biến phân loại** `CAT_COLS`: loại sản phẩm (L/M/H), ca làm việc.
  - **Kết quả:** Train (14000, 8), Test (6000, 8), tỉ lệ hỏng **7.36% / 7.95%**, **0 giá trị thiếu**.

---

## PHẦN 1 — EDA (Phân tích khám phá) `[3–43]`

Mục tiêu: nhìn dữ liệu để **ra quyết định** (dùng metric gì, có shift không, biến nào quan trọng).

### 1.1 Mất cân bằng nhãn `[4–7]`
- `[5] CODE` vẽ tỉ lệ hỏng + số mẫu. **Kết quả:** A 7.36% (1031/14000), B 7.95% (477/6000).
- `[6]` 💡 ô Hiểu đơn giản.
- `[7]` Nhận xét: chỉ ~8% hỏng → **cấm dùng accuracy** (đoán "không hỏng" hết vẫn đúng 92%). Tỉ lệ hỏng **ổn định** A→B → shift là **covariate** (đầu vào dịch), không phải label shift → hợp với **reweighting**.

### 1.1b Thống kê mô tả `describe()` `[8–10]` 🆕
- `[9] CODE` in `describe()` đầy đủ (count/mean/std/min/quartile/max) cho 5 biến số ở **cả A và B** + đếm biến phân loại. Đóng đúng yêu cầu rubric "thống kê mô tả", đồng thời đọc sơ bộ shift qua so cột A↔B.

### 1.2 Covariate shift — chồng phân phối A vs B `[11–16]`
- `[12] CODE` vẽ histogram mỗi biến, chồng A (xanh) và B (đỏ).
- `[14] CODE` bảng dịch chuyển mean/std. **Kết quả then chốt:**
  | Biến | Δmean | Ý nghĩa |
  |------|:---:|--------|
  | nhiệt độ môi trường | **+2.5°** (std loe +29%) | B nóng hơn |
  | nhiệt độ quy trình | **+1.9°** (std loe +28%) | B nóng hơn |
  | tốc độ quay | **+70 rpm** | B quay nhanh hơn |
  | mômen xoắn | **−8%** | B tải thấp hơn |
  | độ mòn dao | ~0 | **ổn định** |
- `[16]` Nhận xét: shift **có thật, có hướng vật lý** (B nóng+nhanh hơn); nhiệt độ B còn **phân tán rộng hơn ~30%**.

### 1.3 Biến nào phân tách hỏng/không? `[17–23]`
- `[18] CODE` boxplot mỗi biến theo nhãn + tương quan tuyến tính.
- `[20]` Nhận xét: **`do_mon_dao` là tín hiệu #1** (máy hỏng mòn ~177 vs lành ~123, corr +0.20). Các biến khác **tuyến tính yếu** (|corr|<0.07) → tín hiệu **phi tuyến/tương tác**.
- `[21] CODE` heatmap tương quan → `[23]` không có đa cộng tuyến, giữ cả 5 biến.

### 1.3b Soi tương tác `[24–30]`
- `[25] CODE` histogram theo nhãn (density) → `[27]` máy hỏng có **mômen** dồn về **hai đuôi** (rất cao HOẶC rất thấp), **tốc độ** dồn về **đuôi thấp** (quay chậm) → dấu hiệu quá tải/thiếu tải.
- `[28] CODE` scatter 2 biến tô màu nhãn → `[30]` máy hỏng bám **dải chéo** trong không gian tốc độ×mômen (≈ công suất bất thường) → gợi ý FE: `mòn×mômen` và `công suất`.

### 1.4 Biến phân loại `[31–34]`
- `[32] CODE` tỉ lệ hỏng theo loại SP & ca. **Kết quả:** đều ~7% (sát trung bình) → `[34]` 2 biến phân loại **gần như vô ích** đơn lẻ (theo tỉ lệ hỏng); không over-engineer.

### 1.4b Shift ở biến phân loại — Chi-square `[35–38]` 🆕
- `[36] CODE` so phân phối phân loại A vs B + Chi-square. **Kết quả:** `ca_lam_viec` **không dịch** (p=0.54) nhưng **`loai_san_pham` CÓ dịch** (p<0.001 — tỉ lệ hạng L/M/H khác giữa 2 dây chuyền).
- `[38]` Nhận xét: shift phân loại chủ yếu đổi *tỉ trọng*; vì `loai_san_pham` là ngưỡng luật OSF nên đã đưa vào `bien_overstrain` → tín hiệu vẫn bất biến ở mức từng máy.

### 1.4c Vùng ngoại suy `[39–42]` 🆕
- `[40] CODE` đếm dòng B nằm ngoài dải `[min,max]` Train A mỗi biến. **Kết quả:** **170 dòng B (2.8%)** ngoài dải (rõ nhất nhiệt độ MT 2.65%, tốc độ max B 2414 > A 2153).
- `[42]` Nhận xét: ở vùng này **cây dự đoán phẳng (không ngoại suy)** → nền cho hạn chế P2; lý do giữ LogReg trong ensemble + ưu tiên feature khoảng-cách-tới-biên.

### 1.5 Tổng kết EDA `[43]`
Bảng phát hiện → hành động: chấm bằng AUC-PR/F1; xử lý shift bằng reweighting+calibration; `do_mon_dao` là mỏ neo; cần cây (RF/XGB) + FE cơ học.

---

## PHẦN 2 — Harness + Baseline v0 `[44–48]`

### Harness (khung thí nghiệm) `[44–45]`
- `[45] CODE` định nghĩa 3 hàm dùng lại suốt bài:
  - `evaluate(name, y_true, y_prob, threshold)` — chấm 1 version trên B, ghi vào `LEADERBOARD` (AUC-ROC, AUC-PR, F1, P, R).
  - `leaderboard()` — bảng xếp hạng.
  - `best_threshold_f1()` — tìm ngưỡng tối đa F1 (dùng sau).
  - **Kỷ luật:** điểm trên B chỉ để *theo dõi*; việc **chọn** cấu hình sẽ dùng IWV (Phần sau), không nhìn nhãn B.

### v0 — Baseline LogReg thô `[46–48]`
- `[47] CODE` LogReg đơn giản, `class_weight='balanced'` (bù imbalance), encode tối thiểu, **scaler fit CHỈ trên Train** (chống rò rỉ), ngưỡng 0.5.
- **Kết quả:** F1=**0.231**, AUC-PR=0.220, P=0.137/R=0.736 → yếu (Precision thảm: 100 cảnh báo chỉ 14 đúng). Đây là **mốc tham chiếu** để đo mọi cải tiến.

---

## PHẦN 3 — Feature Engineering v1 `[49–58]`

**Ý tưởng cốt lõi của cả bài.** Bộ dữ liệu (AI4I 2020) có **4 luật sinh lỗi với ngưỡng vật lý cố định**. Ta chế **3 feature "khoảng-cách-tới-biên"** — mỗi cái là một *hinge* (bản lề) chỉ >0 khi máy vào vùng nguy:

- `[50] CODE` hàm `add_features`:
  | Feature | Công thức | Cơ chế |
  |---------|-----------|--------|
  | `nguy_tan_nhiet` | `max(8.6−ΔT,0) × max(1380−tốc_độ,0)` | HDF (tản nhiệt) — tích 2 hinge = phép **AND** (chỉ >0 khi CẢ HAI vào vùng nguy) |
  | `lech_cong_suat` | `max(3500−P,0) + max(P−9000,0)`, P=mômen×tốc độ×2π/60 | PWF (công suất) — khoảng cách ra ngoài dải an toàn [3500,9000]W |
  | `bien_overstrain` | `độ_mòn×mômen − ngưỡng(loại)`, {L:11000,M:12000,H:13000} | OSF (overstrain) — biên có dấu theo loại SP (đây là chỗ `loai_san_pham` có ích!) |
  - **Vì sao mạnh:** hằng số 8.6/1380/3500/9000 là **thuộc tính vật lý, không đổi giữa A và B** → biên bất biến qua shift. Đây là "reweighting của người nghèo".
  - Giữ **nguyên LogReg như v0**, chỉ thêm 3 feature → cô lập đúng đóng góp của FE (yêu cầu "kiểm chứng" của rubric).
- **Kết quả v1:** F1 **0.231→0.352**, AUC-PR **0.220→0.501** (gấp ~2.3 lần!). → FE cứu LogReg.

### Kiểm chứng `[52–58]`
- `[53] CODE` corr feature mới với nhãn: `lech_cong_suat` +0.238, `nguy_tan_nhiet` +0.231, `bien_overstrain` +0.180 — **đều ≥ `do_mon_dao` (+0.195)**. → feature mới thật sự tách được nhãn.
- `[56] CODE` |hệ số| LogReg: 3 feature mới leo lên nhóm đầu → model **thật sự dựa vào** chúng.
- `[58]` Kết luận: LogReg giờ là base đa dạng thật; nền transfer sang B đã đặt.

---

## PHẦN 4 — Mô hình cây v2 `[59–65]`

- `[60] CODE` train **3 model cây** (đủ ≥3 model theo rubric), tất cả tune bằng `RandomizedSearchCV` + `StratifiedKFold(5)`, chấm bằng **`average_precision` (AUC-PR)** (không dùng accuracy):
  - **Random Forest** (bagging — nhiều cây độc lập, giảm variance). `max_features='sqrt'/'log2'` **KHÔNG None** (vì có biến trội `do_mon_dao`, nếu None mọi cây giống nhau).
  - **XGBoost** (boosting — cây nối tiếp sửa lỗi). `scale_pos_weight≈12.58` = "class_weight của XGB"; learning_rate nhỏ + nhiều regularization.
  - **ExtraTrees** (bagging chia ngưỡng ngẫu nhiên, variance còn thấp hơn RF).
  - Preprocessor `passthrough` (cây **không cần scale**), bọc `Pipeline` (encode fit-lại mỗi fold → không rò rỉ).
- **Kết quả (thr 0.5):** RF F1=0.769 · XGB F1=0.773 · ExtraTrees F1=0.693 (P cao 0.806/R thấp 0.608 → thận trọng, nhạy ngưỡng). **Cây vượt xa LogReg** (F1 0.35→0.77).
- `[63] CODE` feature importance của model cây tốt nhất (RF): `do_mon_dao` + feature biên dẫn đầu.
- `[65]` Kết luận: RF/XGB ~ngang nhau; ExtraTrees hưởng lợi từ threshold calibration sau. Chú thích trung thực: với cây, feature biên ~ngang FE cũ về F1 (cây tự cắt ngưỡng được) — giá trị thật của feature biên là **cứu LogReg + bất biến shift**.

---

## PHẦN 5 — Phát hiện & Xử lý Distribution Shift `[66–82]` ⭐ (2.0đ)

Chia 2 việc: **(A) đo** shift, **(B) xử lý** shift.

### 5.1 PSI + KS `[67–70]` — đo shift từng biến
- `[68] CODE` tính:
  - **PSI** = chia 10 bin theo phân vị Train, so tần suất A vs B. Ngưỡng: <0.1 không · 0.1–0.25 nhẹ · >0.25 mạnh.
  - **KS** = statistic D (báo D chứ không báo p vì n lớn p≈0).
- **Kết quả:**
  | Feature | PSI | Mức |
  |---------|:---:|-----|
  | nhiệt độ môi trường | **1.08** | mạnh |
  | nhiệt độ quy trình | 0.55 | mạnh |
  | tốc độ quay / mômen | 0.16 / 0.12 | nhẹ |
  | **3 feature biên vật lý** | **≈0** | **không shift** |
  | do_mon_dao | 0.001 | không |
- `[70]` Nhận xét ⭐: **shift dồn ở biến thô; 3 feature biên PSI≈0 dù dựng từ chính nhiệt độ/tốc độ dịch mạnh** → FE đã "hấp thụ" shift.

### 5.2 Bằng chứng bất biến `[71–74]`
- `[72] CODE` so **Precision** (P(hỏng|cờ luật)) của mỗi luật trên A vs B. **Kết quả:** HDF 0.84→0.83, PWF 0.17→0.18, OSF 0.40→0.37 → **gần như đứng yên**.
- `[74]` Nhận xét: `P(x)` dịch mạnh nhưng `P(y|cơ_chế)` **không dịch** = covariate shift "sạch" → feature biên là cách bù shift **chuẩn nhất**.

### 5.3 Drift Classifier `[75–78]`
- `[76] CODE` gán **nhãn giả** A=0/B=1, train model **chỉ bằng feature** đoán "đây là A hay B". AUC 0.5=không shift, 1.0=shift mạnh. Lưu `drift_p_train` = P(B|x) trên Train (nguyên liệu cho reweighting).
- **Kết quả quyết định:** Drift AUC = **0.819** (toàn bộ) · **0.512** (chỉ 3 feature biên) · **0.817** (chỉ 5 biến thô).
- `[78]` Nhận xét: **shift nằm TRỌN trong biến thô; feature biên "trong suốt" với shift** (AUC 0.51≈đoán mù). 3 lát cắt (PSI, bảng bất biến, Drift AUC) cùng 1 kết luận.

### v3 — Importance Reweighting `[79–82]` (xử lý shift)
- `[80] CODE` đánh trọng số mỗi dòng Train: `w = p/(1−p)` với p=P(B|x). Dòng "giống B" → w cao → model "nhìn A như thể B".
  - **Clip [0.2, 10]:** vì vài dòng có p≈1 → w thô nổ tới ~57. Clip + chuẩn hoá mean=1 (chỉ 0.5% mẫu chạm trần).
  - Fit lại RF với `sample_weight=w`.
- **Kết quả:** F1=0.773, AUC-PR **0.669→0.672** (gain **nhỏ**).
- `[82]` Nhận xét: gain nhỏ **là tin tốt** — feature biên đã hấp thụ phần lớn shift (Drift AUC biên chỉ 0.512), reweighting chỉ vá phần sót. → "FE vật lý đúng làm giảm nhu cầu bù shift bằng thống kê".

---

## PHẦN 6 — Hướng-về-B không nhìn nhãn Test `[83–101]` (v4·v5·v6)

**Nghịch lý (P0):** chấm trên B nhưng không được nhìn nhãn B để chọn. **Lời giải: IWV.**

### 6.1 IWV harness `[84–86]`
- `[85] CODE` 3 hàm:
  - `oof_prob` — xác suất **out-of-fold** (mỗi dòng do model KHÔNG train trên nó đoán → trung thực).
  - `weighted_prf` — Precision/Recall/F1 **có trọng số mẫu**.
  - `iwv_best_threshold` — quét ngưỡng tối đa F1-có-trọng-số.
  - Trọng số = `w_train` (density-ratio từ v3) → validation "giả B".
- **Kết quả:** ESS = **25.5%** (effective sample size — độ tin IWV có giới hạn vì vài mẫu trọng số lớn).

### 6.2 v4 — Threshold Calibration `[87–90]`
- `[88] CODE` lấy **OOF của RF-reweighted** (tự lập fold để truyền `sample_weight` đúng), chọn ngưỡng tối đa **F1-IWV**. So với ngưỡng-trên-A-thô (đối chứng) và ngưỡng-oracle-trên-B (chỉ để biết trần, **không dùng**).
- **Kết quả:** ngưỡng IWV=0.625, ngưỡng oracle=0.551 (gần nhau → IWV đáng tin). F1=**0.774**, P=0.807/R=0.744 (đổi Recall lấy Precision).
- `[90]` Đồ thị: đường **F1-IWV bám đường F1-thật-B sát hơn** đường F1-A-thô → density-ratio kéo validation về phía B (bằng chứng shift).

### 6.3 v5 — Ensemble `[91–98]`
- `[92] CODE` chuẩn bị **4 base** (LogReg/RF/ExtraTrees/XGB): ma trận **OOF (14000×4)** để chọn + **TEST (6000×4)** để đoán. Tương quan OOF: RF↔XGB 0.95 (cao), LogReg↔khác ~0.62 (thấp = đa dạng).
- `[94] CODE` **v5a Voting** — trung bình có trọng số. Quét lưới trọng số (bước 0.25), chọn bộ tối đa F1-IWV.
  - **Kết quả:** trọng số `RF 0.5 / XGB 0.5` (LogReg & ExtraTrees bị loại), ngưỡng 0.705 → F1=**0.781**.
- `[96] CODE` **v5b Stacking** — meta-LogReg học trên OOF, `sample_weight=density-ratio`.
  - **Hệ số meta:** XGB 4.60 · RF 2.03 · ExtraTrees −0.44 · LogReg 0.06 (meta tin XGB nhất).
  - **Kết quả:** F1=0.781, ngưỡng 0.92 (cao vì `class_weight=balanced` đẩy xác suất lên).
- `[98]` Nhận xét: giữ **cả hai** để không đặt hết cược; meta nghiêng XGB đúng là bẫy P42 → nên có Voting làm đối trọng.

### 6.4 v6 — Chốt `[99–101]`
- `[100] CODE` chọn Voting vs Stacking bằng **F1-IWV** (Voting 0.794 > Stacking 0.791) → **v6 = Voting**. Chấm 1 lần trên B + vẽ PR-curve tổng hợp.
- **KẾT QUẢ CHỐT:** **F1=0.781 · AUC-ROC=0.872 · AUC-PR=0.670 · P=0.812 · R=0.753** — mốc F1 cao nhất leaderboard.

---

## PHẦN 7 — Báo cáo (Phần 5 rubric) `[102]`

Markdown báo cáo: hành trình 0.231→0.781; insight vận hành (độ mòn dao là kim chỉ nam, khuyến nghị **2 mức cảnh báo**); hạn chế (cây không ngoại suy, giả định covariate shift, ESS thấp, trần dữ liệu); 5 hướng cải tiến.

---

## PHẦN 8 — Đánh giá độ tin cậy F1 `[103–106]`

- `[104] CODE` **bootstrap 2000 lần** (vì chỉ 477 mẫu hỏng → F1 nhiễu, P17).
- **Kết quả:**
  - F1 = 0.781, **95% CI [0.751, 0.809]** (rộng ±0.03) → giá trị tuyệt đối kém chắc chắn.
  - **So cặp: P(v6 > XGB) = 99.8%**, delta +0.009, CI [+0.003, +0.015] **trọn phía dương** → ensemble nhỉnh **nhất quán về hướng** dù nhỏ về độ lớn.
- `[106]` Kết luận: các bản đầu bảng (0.769–0.781) có CI chồng lấn (coi như ngang), nhưng bootstrap cặp cho thấy v6 tốt hơn base đơn một cách đáng tin. F1 và AUC-PR không cùng người thắng (AUC-PR cao nhất là v3/v4).

---

## 🔑 Ghi nhớ 6 khái niệm cốt lõi

| Khái niệm | 1 câu |
|-----------|-------|
| **Distribution shift** | Train (A) và Test (B) khác phân phối → model dễ gãy khi triển khai |
| **Covariate shift** | Đầu vào `P(x)` dịch nhưng quan hệ `P(y\|x)` không đổi → reweighting cứu được |
| **Feature khoảng-cách-tới-biên** | Neo vào hằng số vật lý → bất biến qua shift (đòn mạnh nhất) |
| **PSI / Drift Classifier** | Hai cách đo shift (PSI theo bin; Drift = model phân biệt A/B) |
| **Reweighting (density-ratio)** | `w=p/(1−p)` — dòng "giống B" đếm nặng hơn để model học lệch về B |
| **IWV** | Chọn model/ngưỡng "như thể ở B" mà chỉ dùng A → không rò rỉ nhãn Test |

---
*File này chỉ để học/giảng — KHÔNG nộp. Sản phẩm nộp là `bai_tap_cuoi_khoa_<MSSV>.ipynb`.*
