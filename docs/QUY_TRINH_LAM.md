# 🧭 Quy trình làm bài — Nhật ký các bước & quyết định

> Ghi lại **trình tự thực tế** đã làm, kèm *lý do* mỗi quyết định. Đọc để hiểu "vì sao đi tới lời giải này", không chỉ "lời giải là gì".

---

## Giai đoạn 0 — Đọc đề & định vị dữ liệu
- Đọc rubric `FINAL_Rubric_PredictiveMaintenance.docx` → xác định 5 phần chấm điểm + trọng tâm **Distribution Shift**.
- Tìm dữ liệu: `train.csv` (14000 dòng, Dây chuyền A) và `test.csv` (6000 dòng, Dây chuyền B).
- Nhận diện: đây là bộ **AI4I 2020 (UCI Predictive Maintenance)** đổi tên tiếng Việt; nhãn sinh từ 4 cơ chế hỏng (TWF/HDF/PWF/OSF).

## Giai đoạn 1 — Kiểm toán dữ liệu (phát hiện "điểm cài cắm")
Trước khi mô hình hoá, rà chất lượng dữ liệu → phát hiện **6 điểm cài cắm có chủ đích**:
| # | Điểm cài cắm | Bằng chứng | Xử lý |
|---|---|---|---|
| 1 | `toc_do_quay` clip sàn 1180 | 309 dòng = đúng 1180.00 | Ghi nhận censoring |
| 2 | Clip biên `do_mon_dao`(253/0), `momen_xoan`(3.5) | Pile-up 2 tập | Cân nhắc RobustScaler |
| 3 | Imbalance thực 7.4%/7.9% ≠ đề "3–5%" | 1031/14000 | Dùng số thực |
| 4 | `ca_lam_viec` nhiễu thuần | Rate phẳng; drift-imp ≈0.01 | Không over-engineer → sau này loại |
| 5 | `loai_san_pham` phẳng nhưng chi phối OSF | Ngưỡng 11000/12000/13000 | Giữ + tạo `osf_margin` |
| 6 | Test ngoại suy vượt Train | 159 dòng > train-max; rpm 2414>2153 | Cảnh báo extrapolation |
- Xác nhận bản chất shift: **covariate shift** (P(y|cơ chế) ổn định A→B), **không** phải concept drift.

## Giai đoạn 2 — EDA
- Thống kê mô tả, imbalance, so phân phối A vs B (KDE), correlation heatmap.
- **Bổ sung sau review:** (a) **Mutual Information** cạnh Pearson — bắt quan hệ phi tuyến Pearson bỏ sót; (b) **phân phối feature theo lớp 0/1** — bước cốt lõi bài phân loại.
- Mỗi biểu đồ kèm ô **"Quan sát → Insight → Hành động"** để truy ngược mọi quyết định về EDA.

## Giai đoạn 3 — Tiền xử lý & Feature Engineering
- Scaler **fit chỉ trên Train** → transform cả hai (chống rò rỉ, giữ shift).
- Encoding one-hot; xử lý imbalance bằng `class_weight='balanced'` (+ minh hoạ SMOTE).
- Tạo feature cơ học: `chenh_lech_nhiet` (HDF), `cong_suat_co` (PWF), `tich_mon_momen` (OSF), `momen_tren_tocdo`.
- **Kiểm chứng:** AUC 5-fold 0.867 → 0.878 → feature có ích thật.

## Giai đoạn 4 — Phát hiện & Xử lý Distribution Shift (trọng tâm)
- **Đo:** PSI + KS mọi feature (nhiệt độ PSI 1.08 mạnh, mòn dao 0.001 không shift); Drift classifier **AUC 0.81**, thủ phạm = nhiệt độ.
- **Xử lý:** Importance Reweighting (density-ratio $w=p/(1-p)$) + Threshold Calibration.
- **Nhận định trung thực:** reweighting chỉ cải thiện biên vì shift đã được feature cơ chế hấp thụ.

## Giai đoạn 5 — Mô hình & Đánh giá
- 3 mô hình: LogReg / RandomForest / XGBoost; tuning **RandomizedSearchCV + Stratified K-Fold** (tối ưu AUC-PR).
- Metric đa chiều: AUC-ROC, AUC-PR, F1, PR-curve, confusion matrix.
- **RandomForest tốt nhất**; LogReg kém (AUC-PR 0.25) → khẳng định cơ chế phi tuyến.

## Giai đoạn 6 — Tinh chọn Feature (Phụ lục Phần 6)
- Đo **permutation importance** + **ablation** (thay vì cảm tính).
- **Bỏ** `momen_tren_tocdo` (importance = 0) và `ca_lam_viec` (nhiễu) → model gọn, F1 giữ ~0.78.
- **Không loại nhầm** feature thô (bỏ raw → F1 sập 0.544).
- **Thêm feature domain `osf_margin`** = mòn×momen − ngưỡng(hạng) → AUC-PR **0.681 → 0.693**.
- Rút quy tắc: *FE trên cây chỉ có ích khi mã hoá tương tác nhiều biến/ngưỡng theo điều kiện.*

## Giai đoạn 7 — Rà soát & Phương án thay thế
- **Phân tích trần F1:** in-distribution best ~0.76; trần tuyệt đối trên test 0.782 → **F1 ~0.78 là trần tự nhiên** (nhãn có yếu tố ngẫu nhiên), không phải xử lý kém.
- **Thử phương án shift khác:** Baseline (0.69/0.78) vs Reweight (≈ngang) vs **CORAL (0.66/0.74 — tệ hơn)**.
  → CORAL hỏng vì shift là **dịch trung bình**, không phải đổi covariance → *chọn method theo loại shift*.
- **Phát hiện:** FE tự giảm shift — PSI `chenh_lech_nhiet` (0.32) < nhiệt độ thô (1.08) ~3×.
- Sửa demo reweight sang RandomForest cho **nhất quán** con số báo cáo (0.78 thay vì GB 0.72).

---

## 🎯 Các quyết định then chốt & lý do
| Quyết định | Lý do (đo bằng số) |
|---|---|
| Dùng F1 & AUC-PR, bỏ accuracy | Imbalance 7% → accuracy vô nghĩa |
| Fit scaler chỉ trên Train | Chống leakage + **giữ shift** để phát hiện |
| Ưu tiên mô hình cây | Cơ chế hỏng phi tuyến (LogReg AUC-PR chỉ 0.25) |
| Reweighting nhưng không kỳ vọng nhiều | Covariate shift + FE đã hấp thụ shift |
| Bỏ 2 feature, thêm `osf_margin` | Permutation importance + ablation |
| Không dùng CORAL | Thử nghiệm cho thấy tệ hơn (sai loại shift) |
| Chấp nhận F1 ~0.78 | Đã chứng minh là trần tự nhiên của bài |

*Xem chi tiết kỹ thuật ở [`TONG_QUAN_KY_THUAT.md`](TONG_QUAN_KY_THUAT.md); code chạy thật ở [`../bai_tap_cuoi_khoa.ipynb`](../bai_tap_cuoi_khoa.ipynb).*
