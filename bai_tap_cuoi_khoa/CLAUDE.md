# CLAUDE.md — Đồ án ML: Predictive Maintenance (bai_tap_cuoi_khoa)

> Bộ nhớ dự án cho các phiên sau. Cập nhật: 2026-07-13.

## Bài toán
- **Dự đoán máy CNC hỏng ở ca kế tiếp** — phân loại nhị phân `hong_hoc` (0/1), **lệch lớp ~8%**.
- **Distribution shift A→B:** Train = Dây chuyền A (nhà máy cũ), Test = Dây chuyền B (mới, nóng+nhanh hơn).
  Là **covariate shift** (P(x) dịch, P(y|x) ổn định) → cấm dùng accuracy, xử bằng feature bất biến + reweighting.
- Dữ liệu: `Data_Final/train.csv` (14000,8) · `test.csv` (6000,8) · **0 giá trị thiếu**.
  - 5 biến số (`NUM_COLS`): nhiệt độ MT/quy trình, tốc độ quay, mômen xoắn, độ mòn dao.
  - 2 biến phân loại (`CAT_COLS`): `loai_san_pham` (L<M<H, có thứ tự), `ca_lam_viec` (danh nghĩa).
- Rubric: `FINAL_Rubric_PredictiveMaintenance.docx`.

## File chính
- `bai_tap_cuoi_khoa.ipynb` — **notebook nộp** (107 cells). Tên nộp: `bai_tap_cuoi_khoa_<MSSV>.ipynb`.
- `GIAI_THICH_NOTEBOOK.md` — giảng từng cell (CHỈ để học, KHÔNG nộp).
- `template-checklist (1).md` — checklist 8 bước ĐÃ tick đối chiếu bài làm (có bảng tổng kết ở đầu).
- `eda-checklist.md`, `CHIEN_LUOC.md`, `PAIN_POINTS.md`, `thi_nghiem/` (22 thí nghiệm), slide PPTX, `BAO_CAO_TOM_TAT.docx`.

## Ý tưởng cốt lõi của bài
- **4 feature "khoảng-cách-tới-biên"** neo ngưỡng KHÔI PHỤC TỪ LUẬT SINH NHÃN trên A (HDF/PWF/OSF/TWF):
  `nguy_tan_nhiet`, `lech_cong_suat`, `bien_overstrain`, `mon_twf` — PWF [2600,11500], OSF
  {L:12800,M:13900,H:14500}, TWF mòn>244 → biên học trên A dùng thẳng trên B (PSI≈0, Drift AUC 0.53).
- Hành trình: v0 LogReg thô (F1 0.231) → +FE v1 (0.716) → cây RF/XGB/ET v2 (0.783) → reweight v3 →
  threshold v4 → ensemble v5/v6. **Chốt v6 Voting RF.25/ET.25/XGB.5 thr 0.585: F1=0.783, AUC-ROC=0.872,
  AUC-PR=0.666.** Từ v2 mọi bản hội tụ 0.783 = trần (Phụ lục A: ~25% ca hỏng nhiễu ngẫu nhiên,
  precision luật 0.26→0.81).
- **IWV (Importance-Weighted Validation):** chọn model/ngưỡng "như thể ở B" mà KHÔNG nhìn nhãn Test.
- Metric: AUC-PR / F1 / AUC-ROC (KHÔNG accuracy) + bootstrap 95% CI cho F1.

## Trạng thái checklist (2026-07-13): ĐỦ & vượt chuẩn
- Bước 2.5 (tích hợp nhiều bảng) và 4.5 (xây nhãn) = **N/A** (1 bảng, y có sẵn).
- **2 gap nhỏ hình thức còn thiếu:**
  1. `train.duplicated().sum()` — chưa kiểm hàng trùng (Bước 2b).
  2. `ConfusionMatrixDisplay` cho v6 — chưa vẽ tường minh (Bước 8; đã có P/R + PR-curve thay thế).

## Lưu ý khi nộp
- Làm sạch **tất định** ngay; điền/scale/encode gói trong `Pipeline` fit-CHỈ-trên-train (chống leakage).
- **Restart & Run All** (fresh-run) trước khi nộp. Xuất PDF qua VS Code/Chromium (không LaTeX) để render ảnh.
