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

---

## 1. Bản đồ thang điểm → việc phải làm (bám rubric, tổng 10.0)

| Phần | Điểm | Yêu cầu **cứng** của rubric | Kế hoạch của ta | Trạng thái |
|------|:---:|------------------------------|------------------|:---:|
| **1. EDA** | 1.0 | Thống kê mô tả + phân phối từng feature; kiểm tra imbalance; **so sánh trực quan A vs B** + dấu hiệu shift; **correlation heatmap** + nhận xét feature liên quan hỏng | Đã làm mục 1.1–1.5 (overlay hist, bảng dịch chuyển mean/std, boxplot+heatmap, scatter tương tác, categorical) | ✅ |
| **2. Tiền xử lý & FE** | 1.5 | Scaling + encoding hợp lý; **xử lý imbalance** (class_weight hoặc SMOTE); **fit scaler CHỈ trên Train** rồi transform cả hai (không rò rỉ); **≥ 2 feature cơ học** + lý giải & **kiểm chứng** | Encoding ordinal/one-hot (đã có ở v0); FE cơ học ở **v1**; SMOTE thử ở nhánh riêng | ⏳ v1 |
| **3. Distribution Shift** ⭐ | 2.0 | **PSI + KS-Test cho TẤT CẢ feature số** + bảng phân loại (không/nhẹ/mạnh); **Drift Classifier** (báo AUC + feature importance → feature "thủ phạm"); **≥ 1 kỹ thuật xử lý** (Importance Reweighting *hoặc* Threshold Calibration) + **so sánh trước/sau** | Làm **cả 3**: PSI/KS + Drift Classifier + **cả Reweighting lẫn Calibration** | ⏳ |
| **4. Mô hình & Đánh giá** | 2.0 | **≥ 3 mô hình**; tuning **RandomizedSearchCV + Stratified K-Fold**; đánh giá **AUC-ROC, AUC-PR, F1, vẽ PR-curve**; **bảng so sánh**. **F1 là con số dùng để so sánh** | ≥3 model (LogReg, RF, XGB… + ứng viên), tune, bảng leaderboard, PR-curve | ⏳ |
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

> EDA đã xác nhận hướng này: máy hỏng có `momen_xoan`/`toc_do_quay` dồn về **hai đuôi** (36% máy
> hỏng nằm ngoài P10–P90 của mômen vs 20% nếu ngẫu nhiên) và bám **dải chéo** trong không gian
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
- Biến phân loại (loại SP, ca làm việc) **gần như vô ích** → giữ nhưng không over-engineer.

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
| **v2** ✅ | Tree models (RF, XGB) tuned (RandomizedSearchCV + StratifiedKFold) | Model 2.0 | **NHẢY VỌT: RF F1=0.776/AUC-PR=0.690; XGB F1=0.737/AUC-PR=0.656** (vs v1 F1=0.243) |
| **v3** | +Importance Reweighting (density-ratio) | Shift 2.0 | bù covariate shift |
| **v4** | +Threshold Calibration (chọn ngưỡng bằng IWV) | Shift 2.0 | tối ưu F1 trên B |
| **v5a** | **Voting** (weighted-average LogReg/RF/XGB, trọng số dò bằng IWV) | Kết quả 3.0 | mỏ neo đơn giản, khó overfit shift |
| **v5b** | **Stacking** (base=LogReg/RF/XGB, **meta=LogReg**, OOF + **importance-weighted**) | Kết quả 3.0 | học cách kết hợp "như thể ở phân phối B" |
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
| **XGB tune** | η nhỏ (0.05–0.1) + `n_estimators` lớn + **early stopping** với `eval_set` **tách từ Train** (lý tưởng đánh trọng số IWV). Thêm `reg_lambda`, `gamma`, `min_child_weight`, `subsample`, `colsample_bytree` | P35, P36 |
| **LogReg tune** | Quét `C` **về phía nhỏ** (`np.logspace(-3,1)`) — nhớ **C=1/λ, C nhỏ = phạt mạnh**; thử `penalty='l1'/elasticnet` (saga) để tự loại biến FE nhiễu | P30, P37 |
| **Feature importance** | Dùng **cả MDI lẫn Permutation**, chạy **chỉ trên Train/trong CV**; đối chiếu với "feature thủ phạm" của Drift Classifier | P12, P27 |
| **Kiểm chứng FE** | Định lượng: A/B leaderboard v0→v1 (F1/AUC-PR) + boxplot-theo-lớp + \|hệ số/importance\| + **PSI/KS của feature mới** | P29, P7 |
| **Phần 3 (ngoài khoá)** | Tự định nghĩa: **PSI** (10 bin phân vị Train, ngưỡng 0.1/0.25) · **KS** (`ks_2samp`, neo H₀/H₁, báo **statistic D** vì n lớn p≈0) · **Drift Classifier** (nhãn giả A=0/B=1, chỉ feature, AUC 0.5=no shift→1=mạnh) · **Reweighting** w=p/(1−p), **clip** trọng số | P9, P10, P12, P14, P4 |
| **Thuật ngữ** | "covariate shift" = train-vs-test (KHÁC *internal covariate shift* của BatchNorm trong neural-network.md) | P8 |

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
- [ ] **Phần 3 — Phát hiện shift**: PSI + KS (bảng phân loại) + Drift Classifier (AUC + importance).
- [ ] **v3 — Importance Reweighting** (density-ratio, clip trọng số) + IWV harness.
- [ ] **v4 — Threshold Calibration** (quét F1-max trên IWV).
- [ ] **v5a Voting / v5b Stacking** → chọn bằng IWV.
- [ ] **v6 — Bản chốt** + Phần 5 Báo cáo (insight vận hành + hạn chế + cải tiến).
- [ ] **Rà soát nộp bài** (mục 7).
