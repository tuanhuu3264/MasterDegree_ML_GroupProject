# 📁 docs — Tài liệu giải thích bài tập Predictive Maintenance

Tài liệu bổ trợ cho notebook `../bai_tap_cuoi_khoa.ipynb`. Đọc theo độ khó tăng dần:

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
| [`QUY_TRINH_LAM.md`](QUY_TRINH_LAM.md) | **Nhật ký quy trình:** trình tự 7 giai đoạn đã làm + lý do mỗi quyết định |

## Thông điệp nhất quán (khớp notebook)
- **Bộ feature cuối (10):** 5 raw + `chenh_lech_nhiet` + `cong_suat_co` + `tich_mon_momen` + **`osf_margin`** + `loai_san_pham`.
- **Đã loại:** `momen_tren_tocdo` (permutation importance = 0) & `ca_lam_viec` (nhiễu).
- **Kết quả:** RandomForest — AUC-PR **0.693**, **F1 ≈ 0.78** (đã ở trần tự nhiên do nhãn có yếu tố ngẫu nhiên).
- **6 điểm cài cắm** trong dữ liệu: clip 1180 · clip biên · imbalance 7–8% (≠ đề 3–5%) · `ca_lam_viec` nhiễu · `loai_san_pham` bẫy tương tác · Test ngoại suy.
- **Bản chất shift:** covariate shift (không phải concept drift) → FE theo cơ chế + Importance Reweighting + Threshold Calibration.
