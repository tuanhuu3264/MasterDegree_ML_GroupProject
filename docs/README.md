# 📁 docs — Tài liệu giải thích bài tập Predictive Maintenance

Tài liệu bổ trợ cho 2 notebook: `../bai_tap_cuoi_khoa.ipynb` (giải pháp chính) và `../bai_tap_nang_cao_F1.ipynb` (phân tích trần F1). Đọc theo độ khó tăng dần:

| File | Dành cho | Nội dung |
|---|---|---|
| [`GIAI_THICH_TUNG_BUOC.md`](GIAI_THICH_TUNG_BUOC.md) | 🟢 Mới bắt đầu | Giảng từng bước: **câu chuyện → ví dụ số nhỏ → công thức**, dùng bộ đồ chơi 10 máy |
| [`GIAI_THICH_2_VERSION.md`](GIAI_THICH_2_VERSION.md) | 🟡 Ôn nhanh | 15 khái niệm, mỗi cái **2 phiên bản**: 🎓 học thuật ↔ 🍜 dễ hiểu |
| [`GIAI_THICH_EDA_LOGIC.md`](GIAI_THICH_EDA_LOGIC.md) | 🟡 Hiểu mạch | Logic **EDA → Insight → Hướng xử lý**: vì sao mỗi bước xử lý ra đời |
| [`GIAI_THICH_TU_KHOA_DE_BAI.md`](GIAI_THICH_TU_KHOA_DE_BAI.md) | 🔴 Tra cứu | Chi tiết từng từ khoá: định nghĩa → công thức → ví dụ số → lỗi thường gặp |
| [`THUYET_TRINH_PHAN_CONG.md`](THUYET_TRINH_PHAN_CONG.md) | 🎤 Thuyết trình | Chia việc 4 người + kịch bản nói + câu hỏi bảo vệ |

### 📋 Tài liệu tổng quan
| File | Nội dung |
|---|---|
| [`TONG_QUAN_KY_THUAT.md`](TONG_QUAN_KY_THUAT.md) | **Tổng quan kỹ thuật:** bài toán → kiến trúc pipeline → các giai đoạn → kết quả → hạn chế |
| [`QUY_TRINH_LAM.md`](QUY_TRINH_LAM.md) | **Nhật ký quy trình:** 8 giai đoạn từ đầu đến nâng cao F1 + lý do mỗi quyết định |
| [`GIAI_THICH_NANG_CAO_CASE.md`](GIAI_THICH_NANG_CAO_CASE.md) | **6 thử nghiệm nâng cao** (`../nang_cao_case/`): cây nông lộ ngưỡng · learning curve · chọn feature 10 cách · VIF · regularization · scaler — mỗi cái gắn 1 bài giảng |
| [`GIAI_THICH_CLASSWEIGHT_VS_SMOTE.md`](GIAI_THICH_CLASSWEIGHT_VS_SMOTE.md) | **Vì sao `class_weight` chứ không SMOTE:** bằng chứng đo được (F1 0.781 vs 0.759; SMOTE thổi phồng mật độ hỏng vùng an toàn 4.7%→39.4%) |
| [`GIAI_THICH_DOC_BIEU_DO_EDA.md`](GIAI_THICH_DOC_BIEU_DO_EDA.md) | **Đọc biểu đồ EDA** trong `bai_tap_FINAL.ipynb`: giải thích ô insight 1.1 (thiếu dữ liệu/imputation) & 1.3 (shift A↔B, covariate vs concept drift, triệt tiêu offset nhiệt) |
| [`GIAI_THICH_PEARSON_VS_MI.md`](GIAI_THICH_PEARSON_VS_MI.md) | **Pearson vs Mutual Information** (mục 1.5): vì sao quan hệ hỏng phi tuyến theo ngưỡng (momen corr 0.006 « MI 0.021; mòn dao nhảy 7%→57.5% ở mốc 240) + chỗ đã sửa cho đúng |
| [`GIAI_THICH_PHAN_PHOI_THEO_LOP.md`](GIAI_THICH_PHAN_PHOI_THEO_LOP.md) | **Phân phối feature theo lớp** (mục 1.6): soát 4 khẳng định; sửa "mômen cao"→"cả hai cực mômen (chữ U)"; phân biệt tỷ lệ vs số lượng |

> 💡 File tra cứu từ khoá còn có **Phần bổ sung** (B1–B10): Mutual Information, Permutation Importance, Ablation, Ensemble, CORAL, Resubstitution, **trần Bayes**, feature "sắc", khai phá ngưỡng, trần F1 tuyệt đối.

## Thông điệp nhất quán (khớp notebook)
- **Bộ feature cuối (10):** 5 raw + `chenh_lech_nhiet` + `cong_suat_co` + `tich_mon_momen` + **`osf_margin`** + `loai_san_pham`.
- **Đã loại:** `momen_tren_tocdo` (permutation importance = 0) & `ca_lam_viec` (nhiễu).
- **Kết quả:** RandomForest — AUC-PR **0.693**, **F1 ≈ 0.78** (đã ở trần tự nhiên do nhãn có yếu tố ngẫu nhiên).
- **6 điểm cài cắm** trong dữ liệu: clip 1180 · clip biên · imbalance 7–8% (≠ đề 3–5%) · `ca_lam_viec` nhiễu · `loai_san_pham` bẫy tương tác · Test ngoại suy.
- **Bản chất shift:** covariate shift (không phải concept drift) → FE theo cơ chế + Importance Reweighting + Threshold Calibration.
