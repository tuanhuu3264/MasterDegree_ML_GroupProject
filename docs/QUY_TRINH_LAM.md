# 🧭 Tiến trình làm bài — kể lại từ đầu đến khi nâng cao F1

> Đọc như một câu chuyện: **mỗi bước làm gì → thấy gì (số cụ thể) → quyết định gì → vì sao**. Viết cho người mới cũng theo được.

---

## 🏁 Giai đoạn 0 — Hiểu đề & tìm dữ liệu
- **Làm gì:** đọc rubric, xác định phải làm 5 phần (EDA → Tiền xử lý → **Distribution Shift** (trọng tâm) → Mô hình → Báo cáo).
- **Thấy gì:** có `train.csv` (14000 dòng, nhà máy A) và `test.csv` (6000 dòng, nhà máy B, nóng hơn). Nhận ra đây là bộ **AI4I 2020** đổi tên tiếng Việt, nhãn hỏng sinh từ 4 cơ chế: mòn dao (TWF), tản nhiệt kém (HDF), quá tải công suất (PWF), quá tải căng thẳng (OSF).
- **Quyết định:** bám sát 4 cơ chế này khi làm feature.

## 🕵️ Giai đoạn 1 — Kiểm toán dữ liệu (soi "điểm cài cắm")
- **Làm gì:** trước khi mô hình hoá, soi kỹ dữ liệu tìm chỗ bất thường.
- **Thấy gì — 6 điểm cài cắm:**
  1. `toc_do_quay` có **309 dòng = đúng 1180.00** → bị **cắt sàn nhân tạo** (không phải tự nhiên).
  2. `do_mon_dao`/`momen_xoan` bị cắt biên (253/3.5).
  3. Tỷ lệ hỏng thực **7.4%/7.9%** ≠ đề ghi "3–5%".
  4. `ca_lam_viec` (ca sáng/chiều/đêm) tỷ lệ hỏng **phẳng** → nhiễu.
  5. `loai_san_pham` cũng phẳng **nhưng** quyết định ngưỡng OSF → *không được loại*.
  6. Test có 159 dòng **nóng hơn** máy nóng nhất của Train → vùng ngoại suy.
- **Quyết định:** dùng **số thực đo được** (không tin mô tả đề); ghi nhận clipping; xác định đây là **covariate shift** (quy luật vật lý không đổi, chỉ điều kiện vận hành đổi).

## 🔍 Giai đoạn 2 — EDA (khám phá dữ liệu)
- **Làm gì:** thống kê, vẽ phân phối A vs B, heatmap tương quan.
- **Thấy gì:** nhiệt độ B cao hơn ~2.5 độ, tốc độ cao hơn → shift rõ. Tương quan tuyến tính với target **yếu** (|r|<0.2) vì cơ chế hỏng theo **ngưỡng** (phi tuyến).
- **Bổ sung sau này (khi review):**
  - **Mutual Information** cạnh Pearson → phát hiện `momen_xoan` Pearson 0.006 nhưng có tín hiệu phi tuyến.
  - **Phân phối feature theo lớp 0/1** → thấy `do_mon_dao` tách rõ nhất (OK ~123 vs Hỏng ~177).
- **Quyết định:** phải làm **Feature Engineering** + dùng **mô hình cây** (không chỉ tuyến tính).

## 🛠️ Giai đoạn 3 — Tiền xử lý & Feature Engineering
- **Làm gì:**
  - Scaler **học thước đo chỉ từ Train** rồi áp cho cả hai (chống rò rỉ + giữ shift).
  - Tạo feature cơ học: `chenh_lech_nhiet` (tản nhiệt), `cong_suat_co` = mômen×tốc độ (công suất), `tich_mon_momen` (overstrain).
- **Thấy gì:** AUC 5-fold tăng **0.867 → 0.878** → feature có ích thật.
- **Quyết định:** giữ các feature cơ học, dùng `class_weight='balanced'` để xử lý imbalance.

## 🎯 Giai đoạn 4 — Phát hiện & Xử lý Distribution Shift (trọng tâm)
- **Làm gì (đo shift):** PSI + KS mỗi feature; huấn luyện "thám tử" (drift classifier) đoán A/B.
- **Thấy gì:** nhiệt độ PSI **1.08** (shift mạnh), mòn dao **0.001** (không shift); drift AUC **0.81** → shift thật, thủ phạm = nhiệt độ.
- **Làm gì (xử lý shift):** Importance Reweighting (cân lại mẫu Train cho giống Test) + Threshold Calibration.
- **Thấy gì:** reweighting cải thiện rất ít.
- **Quyết định + hiểu ra:** vì đây là **covariate shift** mà feature cơ chế **đã tự giảm shift** (PSI `chenh_lech_nhiet` 0.32 < nhiệt độ thô 1.08 ~3×) → baseline đã tốt.

## 🤖 Giai đoạn 5 — Xây mô hình & Đánh giá
- **Làm gì:** 3 mô hình (LogReg / RandomForest / XGBoost), tinh chỉnh RandomizedSearchCV + Stratified K-Fold, đánh giá AUC-ROC/AUC-PR/F1/PR-curve.
- **Thấy gì:** **RandomForest tốt nhất** (F1 ~0.78); LogReg kém (AUC-PR 0.25) → khẳng định cơ chế phi tuyến.

## ✂️ Giai đoạn 6 — Tinh chọn Feature (đo bằng số)
- **Làm gì:** đo **permutation importance** + **ablation** thay vì loại theo cảm tính.
- **Thấy gì:** `momen_tren_tocdo` importance **0.000** (vô dụng), `ca_lam_viec` nhiễu → **loại cả hai**. Thêm feature domain **`osf_margin`** (mòn×momen − ngưỡng theo hạng) → AUC-PR **0.681 → 0.693**.
- **Quyết định:** bộ feature gọn 10 cái, mỗi feature đều có lý do.
- **Quy tắc rút ra:** *FE trên cây chỉ có ích khi mã hoá tương tác nhiều biến/ngưỡng theo điều kiện.*

## 🔬 Giai đoạn 7 — Rà soát & thử phương án khác
- **Làm gì:** thử các cách xử lý shift khác (CORAL) và phân tích trần F1.
- **Thấy gì:** **CORAL làm TỆ hơn** (0.778→0.743) vì shift là dịch trung bình, không phải đổi covariance → *chọn method theo loại shift*.

## 🚀 Giai đoạn 8 — Nâng cao F1 (câu hỏi: có thể > 0.8 không?)
Đây là giai đoạn "cố phá mốc 0.8" theo đúng vòng lặp: khai phá → thử feature → train → kiểm trần.

**Bước 8.1 — Khai phá lại ngưỡng cơ chế** (đo tỷ lệ hỏng theo bin của chính bộ này):
- `do_mon_dao`: `(220,240]` → 7% rồi **`(240,255]` → 57%** ⇒ ngưỡng TWF thật ở **240** (không phải 200 như AI4I).
- `cong_suat`: hỏng cao khi **< 2800** (78%) hoặc **> 10000** (23%).

**Bước 8.2 — Kiểm tra nhãn có nhiễu không** (resubstitution vs cross-validation):
- RandomForest **ghi nhớ** Train được (resub F1 = **1.000**) nhưng **tổng quát** chỉ **0.755** → chênh 0.25 = **nhiễu bản chất**.
- Bằng chứng: vùng nguy hiểm nhất (`wear>240`) cũng chỉ hỏng **57.5%**, không phải 100% → **không thể đoán chắc**.

**Bước 8.3 — Tạo feature "sắc"** dựa trên ngưỡng khai phá:
- `twf_margin = wear − 240`, `pwf_low`, `pwf_high`, `hdf_score`.
- Kiểm chứng: **corr 0.18–0.25** (cao) + **PSI ≈ 0** (phân phối đều, không shift) — đúng tiêu chí feature tốt.

**Bước 8.4 — Train lại 3 model (yếu/vừa/mạnh) + ensemble:**
| Model | Bộ cũ | Bộ sắc |
|---|---|---|
| LogReg (yếu) | 0.305 | **0.582** ⬆️ |
| RandomForest (vừa) | 0.782 | 0.781 |
| XGBoost (mạnh) | 0.748 | **0.773** ⬆️ |
- Feature sắc **nâng mạnh model yếu/vừa**; RF giữ 0.78 (cây tự tìm ngưỡng rồi).

**Bước 8.5 — Kiểm trần F1:** ngay cả khi *chọn ngưỡng bằng nhãn Test* (gian lận để đo trần), F1 tối đa = **0.783**.
- ⇒ **Mốc 0.80 nằm ngoài tầm.** Không cách hợp lệ nào đạt được.

**Kết luận giai đoạn 8:** F1 ~0.78 là **trần Bayes** của bài. Đẩy lên 0.8 chỉ được bằng **rò rỉ dữ liệu** (vi phạm đề). Muốn tăng thật phải **có dữ liệu mới** (cảm biến rung/âm, tốc độ mòn dao theo thời gian), không phải xử lý thêm.

---

## 🎯 Tổng kết các quyết định & lý do
| Quyết định | Vì sao (đo bằng số) |
|---|---|
| Dùng F1 & AUC-PR, bỏ accuracy | Imbalance 7% → accuracy vô nghĩa |
| Fit scaler chỉ trên Train | Chống rò rỉ + giữ shift để phát hiện |
| Ưu tiên mô hình cây | Cơ chế phi tuyến (LogReg AUC-PR chỉ 0.25) |
| Reweighting nhưng không kỳ vọng nhiều | Covariate shift + FE đã hấp thụ shift |
| Bỏ 2 feature, thêm `osf_margin` | Permutation importance + ablation |
| Không dùng CORAL | Thử nghiệm cho thấy tệ hơn (sai loại shift) |
| Thêm feature sắc (twf/pwf/hdf) | Nâng model yếu/vừa; corr cao + PSI≈0 |
| Chấp nhận F1 ~0.78 | Đã chứng minh là trần Bayes (nhiễu nhãn 57–78%) |

*Chi tiết kỹ thuật: [`TONG_QUAN_KY_THUAT.md`](TONG_QUAN_KY_THUAT.md) · Khái niệm: [`GIAI_THICH_TU_KHOA_DE_BAI.md`](GIAI_THICH_TU_KHOA_DE_BAI.md) · Code: [`../bai_tap_cuoi_khoa.ipynb`](../bai_tap_cuoi_khoa.ipynb) & [`../bai_tap_nang_cao_F1.ipynb`](../bai_tap_nang_cao_F1.ipynb).*
