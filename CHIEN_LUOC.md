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
| **2. Tiền xử lý & FE** | 1.5 | Scaling + encoding hợp lý; **xử lý imbalance** (class_weight hoặc SMOTE); **fit scaler CHỈ trên Train** rồi transform cả hai (không rò rỉ); **≥ 2 feature cơ học** + lý giải & **kiểm chứng** | Scaling+encoding trong Pipeline (fit CHỈ Train); 3 FE cơ học + **kiểm chứng 4 loại** (Δv0→v1, boxplot/point-biserial, \|hệ số\|, PSI/KS) + VIF; imbalance=class_weight/scale_pos_weight | ✅ *(SMOTE: bỏ, dùng class_weight — hợp shift)* |
| **3. Distribution Shift** ⭐ | 2.0 | **PSI + KS-Test cho TẤT CẢ feature số** + bảng phân loại (không/nhẹ/mạnh); **Drift Classifier** (báo AUC + feature importance → feature "thủ phạm"); **≥ 1 kỹ thuật xử lý** (Importance Reweighting *hoặc* Threshold Calibration) + **so sánh trước/sau** | PSI+KS mọi feature số + **Chi²/PSI phân loại**; Drift AUC=**0.82**+importance; **Reweighting + Threshold Calib + IWV** (chọn không nhìn Test) + so sánh trước/sau; định lượng ngoại suy 2.9% | ✅ |
| **4. Mô hình & Đánh giá** | 2.0 | **≥ 3 mô hình**; tuning **RandomizedSearchCV + Stratified K-Fold**; đánh giá **AUC-ROC, AUC-PR, F1, vẽ PR-curve**; **bảng so sánh**. **F1 là con số dùng để so sánh** | **5 model tuned** (LogReg v1b l1, RF, XGB, XGB-earlystop, ensemble); RandomizedSearchCV+StratKFold + **RepeatedKFold 5×3** (mean±std); AUC-ROC/PR/F1/**PR-curve có baseline**; leaderboard 11 dòng | ✅ |
| **5. Báo cáo** | 0.5 | Trình bày logic; **insight vận hành/bảo trì**; nêu **hạn chế** + **hướng cải tiến** | Mục 7.2/7.3: insight vận hành + giả định covariate + hạn chế (trần F1, ngoại suy) + cải tiến (conformal, CORAL) | ✅ |
| **6. Kết quả** ⭐ | **3.0** | **Hiệu năng thật trên Dây chuyền B** | Chốt **RandomForest+calib F1=0.778, AUC-PR=0.690** trên B; ensemble/IWV corroborate | ✅ |
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
| **v3** ✅ | +Importance Reweighting (density-ratio, clip 1–99%) | Shift 2.0 | **F1=0.777** (≈v2, đúng dự đoán: `do_mon_dao` không nằm vùng shift) |
| **v4** ✅ | +Threshold Calibration (ngưỡng trên OOF-Train) | Shift 2.0 | **F1=0.778 @thr=0.58** — top leaderboard |
| **v5a** ✅ | **Voting** (TB xác suất LogReg/RF/XGB) | Kết quả 3.0 | **F1=0.774** — ≈RF, mỏ neo đơn giản |
| **v5b** ✅ | **Stacking** (meta=LogReg, OOF) + **v5c meta đánh trọng số density-ratio** | Kết quả 3.0 | **F1=0.777 / v5c=0.774** — không vượt RF (ensemble <1%) |
| **v6** ✅ | Chốt **RandomForest** (top F1, bền dưới shift); **IWV** chọn không nhìn Test | tất cả | **F1=0.778, AUC-PR=0.690** trên B |
| **+IWV** ✅ | Importance-Weighted Validation: bảng IWV vs CV (AP_IWV>AP_CV = bằng chứng shift) | chống rò rỉ P0 | RF/XGB đứng đầu; LogReg yếu |

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

- [x] Đủ 5 phần rubric + phần Kết quả có hiệu năng thật trên B. *(coverage 15/15)*
- [x] Phần 3: **PSI + KS đầy đủ** (+ Chi²/PSI phân loại), **Drift Classifier (AUC=0.82 + importance)**, **Reweighting + Threshold Calib + IWV + so sánh trước/sau**.
- [x] Phần 4: **5 model tuned**, **RandomizedSearchCV + StratifiedKFold (+RepeatedKFold)**, **PR-curve có baseline**, **leaderboard 11 dòng**, F1 là số so sánh.
- [x] Phần 5: insight vận hành/bảo trì + giả định covariate + hạn chế + cải tiến (mục 7.2/7.3).
- [x] Notebook chạy từ đầu đến cuối **không lỗi** (83 cells, 0 error).  ⬜ **CHỜ: đổi tên `bai_tap_cuoi_khoa_<MSSV>.ipynb`.**
- [x] Không wikilink, không đường dẫn cá nhân.  ⬜ **CHỜ: điền `<điền tên/MSSV>` ở cell 0.**

---

## 8. Nhật ký tiến độ (checklist chạy)

> Cập nhật mỗi khi xong một mốc. Notebook hiện tại: xem `bai_tap_cuoi_khoa.ipynb`.

- [x] **Setup + Harness** — `evaluate()`/`leaderboard()`/`best_threshold_f1()`, `LEADERBOARD` ghi đè theo version. *(+ psi()/shift_level() dùng chung)*
- [x] **Phần 1 — EDA** (1.0đ): 1.1 imbalance · 1.2 overlay hist + bảng dịch chuyển · 1.3 boxplot+heatmap · 1.3b tương tác · 1.4 categorical · 1.5 tổng kết.
- [x] **v0 — Baseline LogReg** (no FE): F1=0.231 · AUC-PR=0.220 · AUC-ROC=0.732 (thr 0.5).
- [x] **v1 — Feature Engineering** (Phần 2): +`chenh_lech_nhiet`, `cong_suat_co`, `mon_x_momen`; giữ nguyên LogReg để cô lập. **F1=0.243 · AUC-PR=0.242 · AUC-ROC=0.740** (mọi metric ↑). **Kiểm chứng 4 loại:** Δv0→v1 (F1 +0.013) + boxplot/point-biserial + \|hệ số\| + **PSI/KS feature mới** (`chenh_lech_nhiet` PSI=0.32 giảm từ ~1.0; `cong_suat_co`/`mon_x_momen` PSI≈0.02).
- [x] **Hoàn tất Phần 2**: scaling/encoding trong Pipeline (fit CHỈ Train) ✅; imbalance = `class_weight`/`scale_pos_weight` ✅; **VIF** phát hiện đa cộng tuyến FE (nhiệt ≈∞) ✅. *(SMOTE: quyết định BỎ — class_weight hợp covariate shift hơn, đúng P24.)*
- [x] **v2 — Tree models** (Phần 4): RF + XGBoost, `scale_pos_weight=12.58`/`class_weight='balanced'`, RandomizedSearchCV(`average_precision`, **RF 35 / XGB 45 iter**) + StratifiedKFold(5). **RF F1=0.776 · AUC-PR=0.690 · AUC-ROC=0.880; XGB F1=0.737.** → RF transfer sang B tốt hơn (bias-variance). Chọn cây tốt nhất theo **CV-trên-A** (không nhìn Test). + **v2b XGB early-stopping** (best_iter=174, eval_set từ Train) + **RepeatedKFold 5×3** báo mean±std.
- [x] **v1b — Tune LogReg** (Phần 4, đủ tuning cả 3 model): `C=1/λ` quét nhỏ + l1/elasticnet (saga) → best l1 C=0.002. F1=0.217 (LogReg yếu vì phi tuyến — đúng kỳ vọng).
- [x] **Phần 3 — Phát hiện shift**: PSI + KS (bảng phân loại số) + **Chi²/PSI biến phân loại** (không shift) + **Drift Classifier AUC=0.82 + importance** (nhiệt độ thủ phạm) + **định lượng ngoại suy 2.9%**.
- [x] **v3 — Importance Reweighting** (density-ratio, clip 1–99%): F1=0.777 (≈v2 — vì `do_mon_dao` không nằm vùng shift, kết luận trung thực).
- [x] **v4 — Threshold Calibration** (F1-max trên OOF-Train, thr=0.58): **F1=0.778 — top leaderboard**.
- [x] **IWV harness** ⭐: bảng IWV (mô phỏng B) vs CV thường → **AP_IWV > AP_CV** = bằng chứng shift; chọn model/ngưỡng KHÔNG nhìn Test (P0/P45).
- [x] **v5a Voting** (F1=0.774) / **v5b Stacking** meta=LogReg OOF (F1=0.777) + **v5c meta đánh trọng số density-ratio** (F1=0.774) → ensemble ≈ RF, không vượt (<1%).
- [x] **v6 — Bản chốt**: **RandomForest+calib F1=0.778, AUC-PR=0.690** trên B + Phần 5 Báo cáo (insight + giả định covariate + hạn chế + cải tiến).
- [ ] **Rà soát nộp bài** (mục 7): notebook 0 lỗi ✅ · wikilink/path sạch ✅ · **CHỜ điền MSSV (cell 0) + đổi tên file**.
