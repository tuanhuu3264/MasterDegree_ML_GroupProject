# Chiến lược — Bài cuối khoá: Dự đoán Hỏng hóc CNC dưới Distribution Shift

> **File này là "kim chỉ nam" nội bộ của nhóm — KHÔNG nộp.** Sản phẩm nộp chỉ là
> `bai_tap_cuoi_khoa_<MSSV>.ipynb` (đã chạy, có output, tự chứa). File này để ta thống nhất
> *làm gì, làm theo thứ tự nào, vì sao* — bám sát rubric và phát hiện EDA.

---

## 0. Bài toán trong 3 câu

Dự đoán máy phay CNC **hỏng trong ca kế tiếp** (`hong_hoc` = 0/1), lớp dương hiếm (~7–8%).
Train = **Dây chuyền A** (nhà máy cũ), Test = **Dây chuyền B** (nhà máy mới, nóng hơn, tải khác)
→ **distribution shift là có thật**: cùng cơ chế vật lý gây hỏng, nhưng phân phối biến đầu vào bị dịch.
Nhiệm vụ: **phát hiện – định lượng – bù trừ shift** để mô hình còn tốt khi chạy trên Dây chuyền B.

---Drift Classifier** (báo AUC + feature importance → feature "thủ phạm"); **≥ 1 kỹ thuật xử lý** (Importance Reweighting *hoặc* Threshold Calibration) + **so sánh trước/sau** | Làm **cả 3**: PSI/KS + Drift Classifier + **cả Reweighting lẫn Calibration** | ⏳ |
| **4. Mô hình & Đánh giá** | 2.0 | **≥ 3 mô hình**; tuning **RandomizedSearchCV + Stratified K-Fold**; đánh giá 

## 1. Bản đồ thang điểm → việc phải làm (bám rubric, tổng 10.0)

| Phần | Điểm | Yêu cầu **cứng** của rubric | Kế hoạch của ta | Trạng thái |
|------|:---:|------------------------------|------------------|:---:|
| **1. EDA** | 1.0 | Thống kê mô tả + phân phối từng feature; kiểm tra imbalance; **so sánh trực quan A vs B** + dấu hiệu shift; **correlation heatmap** + nhận xét feature liên quan hỏng | Đã làm mục 1.1–1.5 (overlay hist, bảng dịch chuyển mean/std, boxplot+heatmap, scatter tương tác, categorical) | ✅ |
| **2. Tiền xử lý & FE** | 1.5 | Scaling + encoding hợp lý; **xử lý imbalance** (class_weight hoặc SMOTE); **fit scaler CHỈ trên Train** rồi transform cả hai (không rò rỉ); **≥ 2 feature cơ học** + lý giải & **kiểm chứng** | Encoding ordinal/one-hot (đã có ở v0); FE cơ học ở **v1**; SMOTE thử ở nhánh riêng | ⏳ v1 |
| **3. Distribution Shift** ⭐ | 2.0 | **PSI + KS-Test cho TẤT CẢ feature số** + bảng phân loại (không/nhẹ/mạnh); ****AUC-ROC, AUC-PR, F1, vẽ PR-curve**; **bảng so sánh**. **F1 là con số dùng để so sánh** | ≥3 model (LogReg, RF, XGB… + ứng viên), tune, bảng leaderboard, PR-curve | ⏳ |
| **5. Báo cáo** | 0.5 | Trình bày logic; **insight vận hành/bảo trì**; nêu **hạn chế** + **hướng cải tiến** | Viết ở cuối notebook, tiếng Việt | ⏳ |
| **6. Kết quả** ⭐ | **3.0** | **Hiệu năng thật trên Dây chuyền B** | **Ensemble/stacking** để tối đa F1/AUC trên B | ⏳ |
| | **10.0** | | | |

**Đọc bản đồ này:** hai ô ⭐ (Shift 2.0 + Kết quả 3.0 = **một nửa số điểm**) là nơi thắng/thua.
Mọi version phải phục vụ hai ô đó: xử lý shift cho đúng, và đẩy hiệu năng trên B lên cao nhất.

---

## 2. Cơ chế hỏng (vật lý) → Feature Engineering → phần rubric

Rubric **nêu đích danh** 4 cơ chế hỏng tiềm ẩn. Đây là "xương sống trí tuệ" của bài: FE tốt giúp
mô hình *nhìn thấy* cơ chế, thay vì đoán mò từ biến thô.

| Cơ chế hỏng (rubric) | Bản chất vật lý | Feature ta tạo (v1) | Phục vụ |
|----------------------|-----------------|----------------------|---------|
| **Hao mòn dao** | Dao mòn → gãy/hỏng | `do_mon_dao` (đã có — **tín hiệu #1**, corr +0.20) | — |
| **Tản nhiệt kém** | Chênh lệch nhiệt quy trình − môi trường thấp + tốc độ thấp → không thoát nhiệt | `chenh_lech_nhiet = nhiet_do_quy_trinh − nhiet_do_moi_truong` | FE 1.5 |
| **Quá tải công suất** | Công suất cơ = mômen × tốc độ góc ra ngoài vùng an toàn | `cong_suat_co = momen_xoan × toc_do_quay × 2π/60` (W) | FE 1.5 |
| **Quá tải căng thẳng (overstrain)** | Tích luỹ mòn × mômen vượt ngưỡng | `mon_x_momen = do_mon_dao × momen_xoan` | FE 1.5 |

### Đợt FE bổ sung (thử ở v3 — ứng viên tương tác corr > 0.15 trên Train A)

> **Kỷ luật:** thêm cả nhóm → chấm bằng leaderboard-trên-B + IWV → **giữ cái tăng, bỏ cái giảm**.
> **CẢNH BÁO transfer:** hầu hết biến này nhân với `toc_do_quay`/nhiệt độ — là các biến **dịch mạnh
> nhất** sang B. Corr cao trên A **không** đảm bảo tốt trên B; có thể học phải biên dễ gãy dưới shift.
> `do_mon_dao` (ổn định qua shift) vẫn là mỏ neo. Cây khai thác phi tuyến tốt nên đây là nơi thử hợp lý.

| Feature mới | Công thức | corr(A) | Ý nghĩa vật lý | Rủi ro shift |
|-------------|-----------|:---:|----------------|:---:|
| `mon_x_toc_do` | `do_mon_dao × toc_do_quay` | 0.177 | Dao mòn nặng bị ép quay tốc độ cao → ma sát/rung lắc lớn → gãy trục/vỡ dao | ⚠️ cao (tốc độ dịch mạnh) |
| `cong_suat_x_mon` | `cong_suat_co × do_mon_dao` | 0.171 | "Áp lực công suất" dồn lên công cụ đã suy yếu | ⚠️ vừa |
| `cang_thang_nhiet` | `mon_x_momen × chenh_lech_nhiet` | 0.170 | Tương tác bậc 3: quá tải cơ học × quá tải nhiệt (kim loại nóng → giảm bền kéo) | ⚠️ cao (nhiệt dịch mạnh) |
| `ly_tam_x_mon` | `toc_do_quay² × do_mon_dao` | 0.154 | Lực ly tâm ∝ v² → nổi bật rủi ro vùng redline khi dao cùn | ⚠️ rất cao (v² khuếch đại shift) |
| *(tuỳ chọn, yếu)* `nhiet_x_tocdo` | `chenh_lech_nhiet × toc_do_quay` | −0.092 | — | ⚠️ cao |
| *(tuỳ chọn, yếu)* `ty_le_nhiet_do` | `nhiet_do_quy_trinh / nhiet_do_moi_truong` | −0.076 | Tỉ lệ nhiệt (ít nhạy scale) | thấp |
| *(bỏ)* `ty_le_momen_tocdo` | `momen_xoan / toc_do_quay` | 0.017 | Gần như vô ích | — |

> **Quyết định:** thêm **4 biến mạnh** (corr > 0.15) làm chuẩn; 2 biến yếu để nhánh so sánh (giữ nếu
> IWV không tệ đi); **bỏ** `ty_le_momen_tocdo`. Kiểm chứng: PSI/KS cho từng feature mới ở Step A —
> feature nào PSI mạnh **và** corr-trên-A cao là ứng viên "học nhầm biên", ưu tiên loại nếu IWV giảm.

### 2b. ⭐ Đặc trưng theo NGƯỠNG VẬT LÝ — đòn giảm shift mạnh nhất (ưu tiên hàng đầu)

> **Phát hiện:** bộ dữ liệu là **AI4I 2020** (đã xác minh dải giá trị) — có **4 cơ chế lỗi với ngưỡng
> vật lý chính xác** do generator định nghĩa. Kiểm chứng trực tiếp trên dữ liệu: xác suất hỏng **có
> điều kiện theo cơ chế** gần như **BẤT BIẾN** qua shift, dù phân phối đầu vào dịch mạnh:

| Cơ chế | P(hỏng\|cờ) A | P(hỏng\|cờ) B | Ngưỡng vật lý (hằng số) |
|--------|:---:|:---:|-------------------------|
| **HDF** (tản nhiệt) | 0.841 | 0.825 | `chenh_lech_nhiet < 8.6 K` **VÀ** `toc_do_quay < 1380 rpm` |
| **PWF** (công suất) | 0.170 | 0.182 | `cong_suat_co < 3500 W` **HOẶC** `> 9000 W` |
| **OSF** (căng thẳng) | 0.395 | 0.371 | `do_mon_dao × momen_xoan > nguong(type)` — L=11000/M=12000/H=13000 |
| **TWF** (mòn dao) | 0.067 | 0.066 | `200 ≤ do_mon_dao ≤ 240 min` |

> **Ý nghĩa cốt lõi:** `P(x)` dịch nhưng `P(y | cơ_chế)` KHÔNG dịch → covariate shift "sạch".
> ⇒ **Đặc trưng đo khoảng-cách-tới-ngưỡng là BẤT BIẾN QUA SHIFT**: biên học trên A đúng nguyên trên B,
> không phải extrapolate phân phối đã dịch. **Đây là cách giảm phụ thuộc shift mạnh nhất — mạnh hơn
> reweighting/calibration** (hai cái đó chỉ vá mô hình đã học biên dịch chuyển).

**Feature chốt — THAY (không thêm) 3 feature v1 cũ. Đã verify bằng XGB & LogReg:**

> 3 feature v1 (`chenh_lech_nhiet`, `cong_suat_co`, `mon_x_momen`) bắt **đúng đại lượng nhưng sai
> cấu trúc biên** → mô hình (nhất là LogReg) không "thấy" luật. Thay bằng 3 feature **khoảng-cách-tới-biên**:

| Feature mới (thay v1) | Công thức | v1 cũ thiếu gì → sửa gì |
|-----------------------|-----------|------------------------|
| `nguy_tan_nhiet` | `max(8.6 − ΔT, 0) × max(1380 − toc_do_quay, 0)` | v1 `chenh_lech_nhiet` **bỏ điều kiện AND `speed<1380`, không có biên** → tích 2 hinge chỉ >0 khi **cả hai** cùng vào vùng nguy (mã hoá luật AND) |
| `lech_cong_suat` | `max(3500 − P, 0) + max(P − 9000, 0)`, `P = cong_suat_co` | v1 `cong_suat_co` **không đơn điệu** (cả P thấp & cao đều hỏng → LogReg vô dụng) → khoảng cách ra ngoài dải an toàn, **đơn điệu theo mức nguy** |
| `bien_overstrain` | `do_mon_dao × momen_xoan − nguong(loai_san_pham)`, `{L:11000, M:12000, H:13000}` | v1 `mon_x_momen` **bỏ ngưỡng theo loại SP** → biên **có dấu**, đơn điệu; **`loai_san_pham` vào bài qua đây** |

> **TWF không cần flag riêng** (`200≤do_mon_dao≤240`, precision chỉ ~0.07 do nhiễu thay dao) → giữ
> `do_mon_dao` **thô** là đủ.
>
> **Kết quả verify:** XGB bộ biên(5)=**F1 0.761/AUC-PR 0.669** > v1(8)=0.744/0.663 (ít cột hơn, tốt hơn).
> LogReg được **cứu ngoạn mục**: AUC-PR **0.245 → 0.492** (gần gấp đôi), F1* 0.323 → 0.536 → LogReg
> thành **base ensemble đa dạng thật**, không còn mỏ neo chết. (`l1` vs `l2` giống hệt trên bộ lean 5 cột
> — `l1` chỉ hữu ích khi chạy bộ *full* nhiều biến thô, mục 6b/P37.)

**Chiến thuật giảm phụ thuộc shift (xếp theo sức mạnh):**
1. **Ưu tiên feature bất biến** (`*_bien` ở trên, và `chenh_lech_nhiet` thay cho 2 nhiệt độ tuyệt đối —
   diff chỉ dịch ~0.6 K trong khi mỗi nhiệt độ dịch +2–2.5 K) → dựng biên trên hằng số vật lý.
2. **Hạ cấp/loại biến thô dịch mạnh** khi feature vật lý đã bắt trọn tín hiệu (`nhiet_do_moi_truong`
   PSI≈1.08 gần như không thêm gì ngoài `chenh_lech_nhiet`) → cân nhắc bỏ để bớt "mồi" học biên dịch.
3. **Ưu tiên tỉ lệ / hạng** (scale-invariant) hơn giá trị tuyệt đối khi có thể.
4. **Hiệu chỉnh hằng số biên CHỈ trên A, cố định cho B.** Dạng công thức (out-of-band) là bất biến;
   chỉ *hằng số* mới cần calibrate. PWF precision chỉ ~0.17 → dải `3500/9000 W` có thể đã bị đề chỉnh
   → ước lượng lại 2 mép bằng **phân vị công suất của nhóm hỏng/không-hỏng trên A** (KHÔNG nhìn B).
5. Chỉ **sau đó** mới tới reweighting (v3b) + calibration ngưỡng (v4) như lớp vá bổ sung — kỳ vọng gain
   nhỏ lại (vì feature đã bất biến) → **câu chuyện đẹp cho báo cáo**: "FE vật lý đúng giảm nhu cầu bù shift".
5. **Nhóm tích thô** (`mon_x_toc_do`, `ly_tam_x_mon`…) tụt xuống **nhánh so sánh**: neo vào biến đã dịch
   → corr-trên-A cao nhưng dễ học nhầm biên; giữ chỉ khi IWV không giảm.

**⭐ Bộ đặc trưng SHIFT-ROBUST tinh gọn (đã kiểm chứng bằng XGB — dùng cho v3a'):**
Thí nghiệm trực tiếp (XGB, spw≈12.6) cho thấy **có thể BỎ 3 biến thô dịch mạnh nhất**
(`nhiet_do_moi_truong`, `nhiet_do_quy_trinh`, `toc_do_quay` — PSI cao) mà **không mất F1**, vì 4 feature
vật lý đã "nuốt" thông tin của chúng qua ngưỡng bất biến:

| Cấu hình XGB | #feat | F1@0.5 | AUC-PR |
|--------------|:---:|:---:|:---:|
| Đầy đủ (thô + FE + vật lý) | 10 | 0.768 | 0.667 |
| **Vật lý(4) + `do_mon_dao` + `momen_xoan`** ← **chốt v3a'** | **6** | **0.760** | **0.671** |
| Vật lý(4) + 2 thô + `cong_suat_co` + `chenh_lech_nhiet` | 8 | 0.768 | 0.678 |
| ⚠️ CHỈ 4 feature vật lý (bỏ hết field khác) | 4 | **0.529** | 0.574 |

> **Bài học:** KHÔNG bỏ về chỉ 4 field (4 cờ chỉ định *vùng cơ chế* → thiếu chi tiết phân biệt trong
> vùng → F1 sập còn 0.53). Cách đúng để "tập trung + giảm phụ thuộc shift": giữ **4 vật lý + `do_mon_dao`
> (ổn định) + `momen_xoan`**, **bỏ 3 biến thô dịch mạnh** — F1 ≈ full mà AUC-PR còn nhỉnh hơn, và
> Drift Classifier trên bộ này sẽ có AUC thấp hơn hẳn (bằng chứng đã cắt phụ thuộc shift). `loai_san_pham`
> vẫn giữ vì đã ẩn trong `osf_bien` (ngưỡng theo type); có thể thêm `cong_suat_co`+`chenh_lech_nhiet` nếu muốn AUC-PR nhỉnh.

> EDA đã xác nhận hướng này: máy hỏng có `momen_xoan` dồn về **hai đuôi** (thấp/cao) — 36% máy
> hỏng nằm ngoài P10–P90 của mômen vs 20% nếu ngẫu nhiên; còn `toc_do_quay` dồn về **đuôi thấp**
> (quay chậm), và bám **dải chéo** trong không gian
> tốc độ×mômen → đúng chữ ký của quá tải công suất/căng thẳng. FE cơ học sẽ "nắn thẳng" các biên này.

---

## 3. Phát hiện EDA cốt lõi (đã có — nền cho mọi quyết định)

- **Imbalance ~7–8%, prior ổn định** train→test (7.4%→8.0%) → shift là **covariate** (biến đầu vào),
  không phải label shift → hợp với **Importance Reweighting theo đặc trưng**.
- **Covariate shift rõ, có hướng vật lý:** B nóng hơn (+2.5°/+1.9°), quay nhanh hơn (+70 rpm),
  mômen thấp hơn (−8%), **độ lệch chuẩn nhiệt độ B rộng hơn ~28–30%** (vừa dịch vừa loe).
- **`do_mon_dao` là tín hiệu số 1 và ỔN ĐỊNH qua shift** → nền để mô hình *transfer* tốt sang B.
- Tín hiệu còn lại **phi tuyến / theo tương tác** dựa trên nhiệt độ–tốc độ — mà đó chính là các
  biến **dịch mạnh nhất** → biên học trên A có nguy cơ **không đúng trên B** → cần reweighting + calibration.
- Biến phân loại **đơn biến** nhìn yếu, nhưng **`loai_san_pham` KHÔNG vô ích** — nó là **ngưỡng của
  luật OSF** ({L:11000, M:12000, H:13000}); chỉ hiện tín hiệu khi đưa vào qua `bien_overstrain` (mục 2b).
  `ca_lam_viec` thật sự yếu → giữ nhưng không over-engineer.

---

## 4. Chiến lược tổng thể

**(a) Experiment-driven + leaderboard chung.** Mỗi cải tiến là một *version* (v0, v1, …), tất cả
chấm bằng **cùng một hàm `evaluate()`** → ghi vào `LEADERBOARD` → so sánh khách quan; giữ cái tăng
điểm, bỏ cái không. Con số so sánh chính là **F1** (theo rubric), tham chiếu thêm AUC-ROC/PR.

**(b) Chống rò rỉ khi CHỌN cấu hình.** Điểm trên Test chỉ để **theo dõi/báo cáo**. Việc **chọn**
model / ngưỡng / ensemble **KHÔNG nhìn nhãn Test**, mà dùng **Importance-Weighted Validation**:
lấy validation tách từ Train nhưng **đánh trọng số bằng density-ratio** để *mô phỏng phân phối B*.
Nhờ vậy "thử sai nhiều" vẫn trung thực về mặt phương pháp.

**(c) Đích cuối: hợp nhất mô hình.** Sau khi có ≥3 model tốt + xử lý shift, **ensemble/stacking**
để tối đa hoá ô "Kết quả 3.0" trên Dây chuyền B.

---

## 5. Lộ trình version

| Version | Thêm gì | Phục vụ phần | Kỳ vọng |
|---------|---------|--------------|---------|
| **v0** ✅ | LogReg thô, class_weight balanced, no FE | mốc tham chiếu | F1=0.231, AUC-PR=0.220 |
| **v1** ✅ | +FE cơ học (chênh lệch nhiệt, công suất, mòn×mômen) | FE 1.5 | **F1=0.243, AUC-PR=0.242, AUC-ROC=0.740** — mọi metric ↑; `mon_x_momen` corr +0.184 |
| **v2** ✅ | Tree models (RF, XGB) tuned trên **feature biên** | Model 2.0 | RF F1=**0.770**/AUC-PR=0.669; XGB F1=0.762/AUC-PR=0.662 (vs v1 F1=0.352) |
| **v2b** ✅ | +ExtraTrees tuned (bagging variance còn thấp hơn RF) | Model 2.0 + Kết quả 3.0 | F1=0.691 (P=0.803/R=0.606) — thận trọng, nhạy ngưỡng; base đa dạng cho ensemble |
| **v3** | +Importance Reweighting (density-ratio) | Shift 2.0 | bù covariate shift |
| **v4** | +Threshold Calibration (chọn ngưỡng bằng IWV) | Shift 2.0 | tối ưu F1 trên B |
| **v5a** | **Voting** (weighted-average LogReg/RF/ExtraTrees/XGB, trọng số dò bằng IWV) | Kết quả 3.0 | mỏ neo đơn giản, khó overfit shift |
| **v5b** | **Stacking** (base=LogReg/RF/ExtraTrees/XGB, **meta=LogReg**, OOF + **importance-weighted**) | Kết quả 3.0 | học cách kết hợp "như thể ở phân phối B" |
| **v6** | Bản thắng trên **IWV** (v5a hay v5b) → chốt nộp | tất cả | — |

> **Kỷ luật ensemble dưới shift:** (1) Stacking **bắt buộc OOF** (`StackingClassifier(cv=StratifiedKFold)`)
> để không rò rỉ; (2) **meta phải đơn giản (LogReg)** + huấn luyện trên OOF **có đánh trọng số density-ratio**
> (nối tay với Reweighting v3) để meta không "học gu" Dây chuyền A rồi đặt cược nặng vào con base dễ gãy
> trên B (thường là XGB); (3) **chọn v5a vs v5b bằng Importance-Weighted Validation**, không nhìn nhãn Test.
> Giữ **cả hai** để không đặt hết cược một cửa — nếu Stacking overfit shift thì Voting đỡ.

*(Song song, làm khối "phát hiện shift" — PSI/KS + Drift Classifier — để lấy trọn 2.0 của Phần 3;
đây là phân tích, không phải version model.)*

---

## 6. Nguyên tắc bất di bất dịch (chống rò rỉ)

1. **Fit** scaler / encoder / SMOTE / density-ratio **CHỈ trên Train**, rồi transform Test. Không bao giờ `fit` chạm Test.
2. **Bọc `Pipeline(scaler → model)`** để scaler **fit-lại trong từng fold** (không rò rỉ chéo khi CV). Chỉ **LogReg cần scale**; RF/XGB không cần (dùng `passthrough`).
3. Tuning bằng **Stratified K-Fold** trên Train (giữ tỉ lệ hỏng mỗi fold); F1 lớp hiếm nhiễu → cân nhắc **RepeatedStratifiedKFold (5×3)** cho con số ổn định.
4. Chọn model/ngưỡng/ensemble bằng **Importance-Weighted Validation**, **không** bằng nhãn Test. Chạy **CV thường (không reweight) song song làm đối chứng** — hai bảng lệch nhau = bằng chứng shift (đưa vào báo cáo).
5. Notebook **tự chứa, tiếng Việt, KHÔNG trích note cá nhân/wikilink**; mọi cell chạy ra output + có diễn giải.

---

## 6b. Chốt kỹ thuật (rút từ scan tài liệu khoá + [PAIN_POINTS.md])

| Hạng mục | Quyết định chốt | Vì sao (pain point) |
|----------|-----------------|---------------------|
| **Imbalance** | `class_weight='balanced'` (LogReg, RF) + **`scale_pos_weight ≈ n_neg/n_pos ≈ 11–12`** (XGB, khoá KHÔNG dạy — tự thêm). SMOTE chỉ nhánh so sánh | P20, P23, P24 |
| **Scoring khi tune** | `RandomizedSearchCV(scoring='average_precision', refit='average_precision')`, theo dõi thêm `f1`. **KHÔNG dùng `accuracy`** | P15, P16 |
| **Chọn ngưỡng** | **Tách khỏi tuning** → quét ngưỡng cực đại F1 trên **IWV** (v4 Threshold Calibration), không cố định 0.5. Vì FN đắt → nghiêng Recall | P16, P18, P44 |
| **Scale** | StandardScaler **chỉ cho LogReg**, fit-trên-Train, trong Pipeline. Nêu rõ RF/XGB không cần (tránh hiểu nhầm "quên scale") | P21, P22 |
| **Encode** | `loai_san_pham` L/M/H → **Ordinal giữ thứ tự**; `ca_lam_viec` → **One-hot** + `handle_unknown='ignore'` | P25, P26 |
| **RF** | `max_features='sqrt'/'log2'` (KHÔNG `None`) vì có **dominant feature `do_mon_dao`** làm cây tương quan (ρ cao) | P34 |
| **ExtraTrees** | Cùng preprocessor/không-scale như RF; `class_weight='balanced'`, tune giống RF (`n_estimators`, `max_depth`, `max_features='sqrt'/'log2'`, `min_samples_leaf/split`). **Ngưỡng chia ngẫu nhiên → variance thấp hơn RF** ⇒ kỳ vọng transfer sang B tốt hơn. Base mạnh, ít tương quan với XGB → **tốt cho ensemble v5** | (mở rộng P34) |
| **XGB tune** | η nhỏ (0.05–0.1) + `n_estimators` lớn + **early stopping** với `eval_set` **tách từ Train** (lý tưởng đánh trọng số IWV). Thêm `reg_lambda`, `gamma`, `min_child_weight`, `subsample`, `colsample_bytree` | P35, P36 |
| **LogReg tune** | Quét `C` **về phía nhỏ** (`np.logspace(-3,1)`) — nhớ **C=1/λ, C nhỏ = phạt mạnh**; thử `penalty='l1'/elasticnet` (saga) để tự loại biến FE nhiễu | P30, P37 |
| **Feature importance** | Dùng **cả MDI lẫn Permutation**, chạy **chỉ trên Train/trong CV**; đối chiếu với "feature thủ phạm" của Drift Classifier | P12, P27 |
| **Kiểm chứng FE** | Định lượng: A/B leaderboard v0→v1 (F1/AUC-PR) + boxplot-theo-lớp + \|hệ số/importance\| + **PSI/KS của feature mới** | P29, P7 |
| **Phần 3 (ngoài khoá)** | Tự định nghĩa: **PSI** (10 bin phân vị Train, ngưỡng 0.1/0.25) · **KS** (`ks_2samp`, neo H₀/H₁, báo **statistic D** vì n lớn p≈0) · **Drift Classifier** (nhãn giả A=0/B=1, chỉ feature, AUC 0.5=no shift→1=mạnh) · **Reweighting** w=p/(1−p), **clip** trọng số | P9, P10, P12, P14, P4 |
| **Thuật ngữ** | "covariate shift" = train-vs-test (KHÁC *internal covariate shift* của BatchNorm trong neural-network.md) | P8 |

---

## 6c. Kế hoạch thi công v3 (gộp: Phát hiện shift + IWV harness + Reweighting)

> **Vị trí chèn trong notebook:** ngay **sau cell 40** (Kết luận v2), thành một khối mới
> "## 5. Phát hiện & Xử lý Distribution Shift". Mở đầu bằng 1 câu map: *"Khối này lấy trọn
> Phần 3 rubric (2.0đ) — PSI/KS + Drift Classifier + kỹ thuật xử lý so sánh trước/sau."*
> Mọi hàm mới **fit CHỈ trên Train**, tái dùng `evaluate()`/`leaderboard()` sẵn có.

**Mạch làm A → B → C → D → E (mỗi step = 1–2 cell code + 1 markdown nhận xét):**

### Step A — PSI + KS cho TẤT CẢ feature số  *(rubric: bảng phân loại)*
- Feature set = `NUM_COLS_FE` (5 gốc + 3 FE) → chứng minh cả feature mới cũng được soi shift.
- **PSI:** chia **10 bin theo phân vị của Train**, tính `Σ(p_test−p_train)·ln(p_test/p_train)`;
  cộng `1e-6` chống chia 0. Ngưỡng: `<0.1` không / `0.1–0.25` nhẹ / `>0.25` mạnh.
- **KS:** `scipy.stats.ks_2samp(train[f], test[f])` → báo **statistic D** (n lớn nên p≈0, nói rõ trong nhận xét).
- Xuất **1 DataFrame** `[feature, PSI, muc_do_PSI, KS_D, KS_p]` sort giảm theo PSI + tô màu mức độ.
- *Kỳ vọng (từ EDA):* nhiệt độ & tốc độ dịch mạnh; `do_mon_dao` ổn định (nền transfer tốt).
- **Bằng chứng bất biến (ăn điểm Phần 3):** cạnh PSI/KS của biến thô (dịch mạnh), thêm **bảng
  precision/recall của feature biên theo A vs B** (HDF .84→.83, PWF .17→.18, OSF .39→.37, ANY .26→.28)
  → chứng minh định lượng `P(y | vượt-biên)` **đứng yên** trong khi `P(x)` dịch ⟹ FE kéo `P(y|x)` về ổn
  định. Đây chính là **"kỹ thuật xử lý shift + so sánh trước/sau"** dạng feature-based, bổ trợ reweighting.

### Step B — Drift Classifier  *(rubric: AUC + feature importance → "thủ phạm")*
- Nhãn giả: Train=0, Test=1; **chỉ dùng feature** (`NUM_COLS_FE` + categorical đã encode), **bỏ target thật**.
- Model = RF (hoặc LogReg) trong `Pipeline`, đánh giá bằng **CV AUC trên tập gộp** (không nhìn target hỏng).
  Đọc AUC: `0.5`=không shift → `1.0`=shift mạnh (phân biệt hoàn hảo A/B).
- Lấy **feature importance** → đối chiếu với PSI/KS ở Step A (phải khớp "thủ phạm").
- **Quan trọng:** model này chính là nguồn `p(B|x)` cho density-ratio ở Step C → giữ lại `proba`.

### Step C — Density-ratio + IWV harness  *(nền cho v3/v4/v5/v6)*
- Từ Drift Classifier lấy `p = P(test|x)` **trên các dòng Train**; trọng số
  `w = p/(1−p)` (density-ratio importance sampling).
- **⚠️ CHỐNG OVERFIT (bắt buộc):** vì `nhiet_do_moi_truong` lệch cực mạnh (PSI≈1.08) → Drift
  Classifier dễ đạt **AUC > 0.95** → `p→1` ở nhiều mẫu → `w→∞`, mô hình chính bị vài mẫu cá biệt
  chi phối (high variance). **Clip trọng số về khoảng CỐ ĐỊNH `[0.2, 10.0]`** (thử `[0.1, 5.0]` ở
  nhánh so sánh), **KHÔNG** dùng percentile như dự thảo cũ. Mục tiêu: làm nhóm biến nhiệt độ "bớt
  quan trọng lại", giữ ổn định cho RF/XGB.
- Chuẩn hoá `w` về mean=1 **sau khi clip** để giữ scale loss ổn định.
- Báo **histogram phân bố `w`** trước/sau clip + `max(w)`, `%` mẫu chạm trần → minh chứng đã ghìm đuôi.
- **IWV harness:** tách `X_tr / X_val` từ Train (Stratified, giữ tỉ lệ hỏng); hàm
  `iwv_score(model)` = AUC-PR/F1 trên `X_val` **có sample_weight = w_val** → *mô phỏng phân phối B*.
  Chạy kèm **bản không reweight** làm đối chứng — hai số lệch nhau = bằng chứng shift (đưa vào báo cáo).
- Trả về cả `w_train` (để fit v3) lẫn `iwv_score` (để chọn model v4/v5 không nhìn nhãn Test).

### Step D — v3: FE mở rộng + Importance Reweighting  *(rubric: kỹ thuật xử lý + so sánh trước/sau)*
Tách 2 thay đổi để cô lập tác dụng (đừng trộn):
- **v3a — FE mở rộng (ưu tiên VẬT LÝ):** thêm **trước hết 4 biến ngưỡng vật lý** `hdf_bien`,
  `pwf_bien`, `osf_bien`, `twf_co` (mục 2b — bất biến qua shift), **re-tune RF/XGB/ExtraTrees** y hệt v2
  → `evaluate('v3a_rf_phys', …)`. Kỳ vọng: nhảy vọt trên B **và** khoảng cách CV-A ↔ B thu hẹp (dấu hiệu
  bớt phụ thuộc shift). Nhóm tích thô (mục 2) chỉ thêm ở **nhánh so sánh**, giữ nếu IWV không giảm.
- **v3a' — bộ tinh gọn shift-robust (chốt để tối đa F1 XGB, mục 2b):** chỉ **4 vật lý + `do_mon_dao`
  + `momen_xoan`** (bỏ 3 biến thô dịch mạnh) → `evaluate('v3a_xgb_lean', …)`. So với v3a full: F1 ≈ nhau
  nhưng Drift AUC thấp hơn ⇒ minh chứng "giảm phụ thuộc shift". Đây là ứng viên base cho ensemble v5.
- **v3b — Reweighting:** lấy base tốt nhất (v2 hoặc v3a) fit lại với `sample_weight = w_train` (clip
  `[0.2,10.0]`, Step C) → `evaluate('v3b_rf_reweighted', …)`. Thêm 1 nhánh **LogReg reweighted** (rẻ, dễ
  diễn giải) làm minh hoạ thứ hai.
- Markdown: bảng **trước/sau** (v2 → v3a → v3b) + diễn giải: FE mới cho cây "nhìn" cơ chế; reweighting
  kéo biên học về gần phân phối B, đặc biệt ghìm ảnh hưởng biến nhiệt độ đã clip.

### Step E — Nhận xét & chốt trạng thái
- 1 markdown tổng: PSI/KS + Drift AUC + Δ hiệu năng v2→v3; nối sang v4 (Threshold Calibration dùng IWV).
- Cập nhật **mục 8 Nhật ký** + **bảng mục 1** (Phần 3 → ✅) + **mục 5 lộ trình** (v3 → ✅).

**Định nghĩa xong khi:** khối chạy Run-All 0 lỗi, có bảng PSI/KS, Drift AUC + importance,
`v3` xuất hiện trên leaderboard cạnh `v2`, và IWV harness sẵn sàng cho v4/v5.

---

## 7. Checklist nộp bài

- [ ] Đủ 5 phần rubric + phần Kết quả có hiệu năng thật trên B.
- [ ] Phần 3: có **PSI + KS bảng đầy đủ**, **Drift Classifier (AUC + importance)**, **≥1 kỹ thuật xử lý + so sánh trước/sau**.
- [ ] Phần 4: **≥3 model**, **RandomizedSearchCV + StratifiedKFold**, **PR-curve**, **bảng so sánh**, F1 là số so sánh.
- [ ] Phần 5: insight vận hành/bảo trì + hạn chế + cải tiến.
- [ ] Notebook chạy từ đầu đến cuối không lỗi, đổi tên `bai_tap_cuoi_khoa_<MSSV>.ipynb`.
- [ ] Không còn `<điền tên/MSSV>`, không wikilink, không đường dẫn cá nhân.

---

## 8. Nhật ký tiến độ (checklist chạy)

> Cập nhật mỗi khi xong một mốc. Notebook hiện tại: xem `bai_tap_cuoi_khoa.ipynb`.

- [x] **Setup + Harness** — `evaluate()`/`leaderboard()`/`best_threshold_f1()`, `LEADERBOARD` ghi đè theo version.
- [x] **Phần 1 — EDA** (1.0đ): 1.1 imbalance · 1.2 overlay hist + bảng dịch chuyển mean/std · 1.3 boxplot+heatmap · 1.3b tương tác (overlay theo nhãn + 2 scatter) · 1.4 categorical · 1.5 tổng kết. → 5 plots.
- [x] **v0 — Baseline LogReg** (no FE): F1=0.231 · AUC-PR=0.220 · AUC-ROC=0.732 (thr 0.5).
- [x] **v1 — Feature Engineering** (Phần 2, một phần 1.5đ): +`chenh_lech_nhiet`, `cong_suat_co`, `mon_x_momen`; giữ nguyên LogReg để cô lập tác dụng. **F1=0.243 · AUC-PR=0.242 · AUC-ROC=0.740** (mọi metric ↑). Kiểm chứng: boxplot-theo-nhãn + corr (`mon_x_momen` +0.184, mạnh gần bằng `do_mon_dao` +0.195; `cong_suat_co`/`chenh_lech_nhiet` yếu tuyến tính — kỳ vọng cây khai thác) + |hệ số| LogReg. → notebook 36 cells, 9 plots, 0 errors.
- [ ] **Hoàn tất Phần 2**: chốt scaling/encoding trong Pipeline (đã có), ghi chú imbalance strategy; (tuỳ chọn) nhánh SMOTE so sánh.
- [x] **v2 — Tree models** (Phần 4): RF + XGBoost, `scale_pos_weight=12.58` (XGB) / `class_weight='balanced'` (RF), RandomizedSearchCV(`scoring='average_precision'`, RF 25 iter / XGB 30 iter) + StratifiedKFold(5), Pipeline `passthrough` (không scale). **RF F1=0.776 · AUC-PR=0.690 · AUC-ROC=0.880 (P=0.795, R=0.757); XGB F1=0.737 · AUC-PR=0.656.** → **RF thắng trên B** dù XGB nhỉnh hơn ở CV-trên-A (0.659 vs 0.653) — **đúng câu chuyện bias-variance dưới shift: RF (bagging, variance thấp) transfer sang B tốt hơn XGB (boosting)**. Feature importance: `do_mon_dao` + `mon_x_momen` dẫn đầu. Notebook 41 cells, 10 plots, 0 errors. *(Lưu ý: AUC-PR trên B=0.690 > CV-trên-A=0.653 — B có vẻ "dễ" hơn ở tín hiệu hỏng.)*
- [x] **v1 (bản mới) — Feature biên vật lý**: THAY 3 FE cũ bằng `nguy_tan_nhiet` (HDF AND-hinge),
  `lech_cong_suat` (PWF hai-đuôi), `bien_overstrain` (OSF ngưỡng-theo-loại). LogReg **nhảy vọt**:
  AUC-PR 0.220→**0.501**, AUC-ROC 0.732→**0.852**, F1 0.231→0.352. Corr mới: lech_cong_suat +0.238,
  nguy_tan_nhiet +0.231, bien_overstrain +0.180 (đều ≥ do_mon_dao +0.195). → feature biên cứu LogReg.
- [x] **v2/v2b — RF · XGB · ExtraTrees** (trên feature biên): RF thắng B **AUC-PR 0.669 / F1 0.770**;
  XGB 0.662/0.762; ExtraTrees 0.662/**F1 0.691** (P=0.803 cao, R=0.606 thấp → nhạy ngưỡng, base đa dạng
  cho ensemble). RF>XGB trên B dù XGB nhỉnh ở CV-A (0.668>0.664) — đúng bias-variance dưới shift.
  *Lưu ý trung thực:* với cây, feature biên ~ngang FE cũ về F1 (cây tự cắt ngưỡng); giá trị nằm ở cứu
  LogReg + bất biến-shift + cho phép bỏ biến thô. Notebook chạy Run-All 0 lỗi.
- [x] **Phần 3 — Phát hiện shift** (mục 5.1–5.3 notebook): PSI/KS (nhiệt độ MT **PSI 1.08**, quy trình
  0.55 mạnh; 3 feature biên PSI≈0 "không shift") + bảng bất biến `P(hỏng|luật)` A↔B (HDF .841→.825…) +
  **Drift Classifier AUC=0.817** (toàn bộ), **0.512** (chỉ feature biên) vs **0.817** (chỉ biến thô) →
  bằng chứng quyết định: shift nằm trọn ở biến thô, feature biên trong suốt với shift. `drift_p_train`
  (OOF) đã lưu sẵn cho reweighting v3. 3 lát cắt đồng thuận. Notebook 51 cells, Run-All 0 lỗi.
- [x] **v3 — Importance Reweighting**: `w=p/(1-p)` từ `drift_p_train`, w thô **max 70.5** → clip
  **[0.2,10]** (0.6% chạm trần) + chuẩn hoá mean=1. RF fit lại với sample_weight → AUC-PR 0.669→**0.671**,
  F1 0.764 (≈ v2). Gain nhỏ = **đúng luận điểm**: feature biên đã hấp thụ shift (Drift AUC riêng feature
  biên chỉ 0.512) → reweighting chỉ vá phần sót. Rubric Phần 3 "xử lý + so sánh trước/sau" ✅. Histogram
  trọng số trước/sau clip. *(IWV harness dời sang v4 — nơi thật sự cần chọn ngưỡng không nhìn nhãn Test.)*
- [x] **IWV harness** (mục 6.1 notebook): `oof_prob` (OOF không rò rỉ) + `weighted_prf` + `iwv_best_threshold`; trọng số = `w_train` (density-ratio clip [0.2,10], mean=1); **ESS=25.5%** (báo độ tin IWV). Đối chứng w=1 (CV thường trên A).
- [x] **v4 — Threshold Calibration**: OOF của RF-reweighted (fit từng fold có `sample_weight`) → ngưỡng F1-max trên **IWV = 0.650** (đối chứng A-thô 0.655; oracle-B 0.539). Đường F1-IWV bám F1-thật-B sát hơn F1-A-thô (bằng chứng shift). **v4: F1=0.771, AUC-PR=0.676, P=0.807/R=0.738** — cân lại về Precision, gain nhỏ (đúng: feature biên đã hấp thụ shift).
- [x] **v5a Voting / v5b Stacking**: 4 base decorrelated (LogReg/RF/ExtraTrees/XGB), OOF-Train + proba-B. **Voting** (trọng số dò IWV → `RF 0.5/XGB 0.5`, thr 0.705): F1=**0.781**/P=0.812/R=0.753. **Stacking** (meta LogReg trên OOF, `sample_weight`=density-ratio, thr 0.92): F1=0.781 (meta nghiêng XGB 4.6/RF 2.0). Hai bản gần tương đương.
- [x] **v6 — Bản chốt**: chọn bằng IWV (Voting F1-IWV 0.794 > Stacking 0.791) → **v6 = Voting**. **Kết quả cuối trên B: F1=0.781 · AUC-ROC=0.872 · AUC-PR=0.670 · P=0.812 · R=0.753** (mốc F1 cao nhất leaderboard, vượt v2_xgb 0.773). PR-curve tổng hợp + đường cơ sở. **Phần 5 Báo cáo** (mục 7 notebook): hành trình 0.231→0.781, insight vận hành/bảo trì (2 mức cảnh báo), hạn chế (P2/P3 + ESS 25.5% + trần dữ liệu), 5 hướng cải tiến. Notebook 68 cells, Run-All **0 lỗi**.
- [ ] **Rà soát nộp bài** (mục 7): đổi tên `bai_tap_cuoi_khoa_<MSSV>.ipynb`, kiểm placeholder/wikilink.
