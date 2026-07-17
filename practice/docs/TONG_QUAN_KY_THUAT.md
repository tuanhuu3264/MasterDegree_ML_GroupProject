# 🏗️ Tổng quan kỹ thuật — Predictive Maintenance dưới Distribution Shift

Tài liệu tổng quan giải pháp: bài toán → kiến trúc → các giai đoạn → kết quả → quyết định → hạn chế.

---

## 1. Bài toán
- **Mục tiêu:** dự đoán nhị phân `hong_hoc` (máy phay CNC hỏng trong ca kế tiếp).
- **Thách thức:** Train = Dây chuyền A (nhà máy cũ, mát); Test = Dây chuyền B (mới, nóng hơn, tải khác) → **distribution shift**.
- **Đặc điểm:** imbalance mạnh (~7–8% hỏng); nhãn sinh từ 4 cơ chế vật lý (TWF/HDF/PWF/OSF); **covariate shift** (P(y|cơ chế) ổn định).

## 2. Kiến trúc giải pháp (pipeline)
```
   train.csv / test.csv (A / B)
            │
   ┌────────▼─────────┐   Kiểm toán dữ liệu → phát hiện 6 điểm cài cắm
   │  EDA + audit     │   (Pearson + Mutual Info + phân phối theo lớp)
   └────────┬─────────┘
   ┌────────▼─────────┐   Fit-on-Train scaler (chống leakage, giữ shift)
   │  Preprocess + FE │   One-Hot; class_weight; feature cơ học + osf_margin
   └────────┬─────────┘
   ┌────────▼─────────┐   PSI/KS → Drift classifier → Reweighting → Calibration
   │  Distribution    │   + so sánh phương án (Baseline / Reweight / CORAL)
   │  Shift handling  │
   └────────┬─────────┘
   ┌────────▼─────────┐   LogReg / RandomForest / XGBoost
   │  Model + tuning  │   RandomizedSearchCV + Stratified K-Fold (opt AUC-PR)
   └────────┬─────────┘
   ┌────────▼─────────┐   Feature selection (permutation + ablation)
   │  Refine + review │   Trần F1, phương án thay thế
   └────────┬─────────┘
        Đánh giá trên Test B (AUC-ROC / AUC-PR / F1 / PR-curve)
```

## 3. Các giai đoạn giải pháp
| # | Giai đoạn | Kỹ thuật chính | Đầu ra |
|---|---|---|---|
| 1 | EDA + Audit | thống kê, KDE, Pearson + **Mutual Info**, phân phối theo lớp | 6 điểm cài cắm, dấu hiệu shift |
| 2 | Preprocess + FE | StandardScaler (fit-Train), One-Hot, class_weight/SMOTE, feature cơ học | không gian đặc trưng sạch |
| 3 | Shift handling | PSI, KS, Drift classifier, Importance Reweighting, Threshold Calibration, CORAL (đối chứng) | shift được định lượng & xử lý |
| 4 | Modeling | 3 mô hình + RandomizedSearchCV + Stratified K-Fold | mô hình tối ưu |
| 5 | Refine + review | permutation importance, ablation, `osf_margin`, phân tích trần F1 | bộ feature tinh gọn 10 |

## 4. Bộ feature cuối (10)
| Nhóm | Feature |
|---|---|
| Thô (5) | `nhiet_do_moi_truong`, `nhiet_do_quy_trinh`, `toc_do_quay`, `momen_xoan`, `do_mon_dao` |
| Cơ học (3) | `chenh_lech_nhiet` (HDF), `cong_suat_co` (PWF), `tich_mon_momen` (OSF) |
| Domain (1) | **`osf_margin`** = mòn×momen − ngưỡng(L/M/H) |
| Phân loại (1) | `loai_san_pham` |
| ❌ Đã loại | `momen_tren_tocdo` (importance 0), `ca_lam_viec` (nhiễu) |

## 5. Xử lý Distribution Shift — so sánh phương án
| Phương án | AUC-PR | F1 | Kết luận |
|---|---|---|---|
| **Baseline** (FE + class_weight + calib) | **0.690** | **0.778** | 🏆 tốt nhất |
| Importance Reweighting (density-ratio) | 0.690 | 0.751 | ≈ ngang |
| CORAL (align covariance) | 0.658 | 0.743 | tệ hơn (sai loại shift) |

**Insight:** shift là **dịch trung bình** → Feature Engineering tự giảm shift (PSI `chenh_lech_nhiet` 0.32 vs nhiệt độ thô 1.08). Threshold Calibration giúp mô hình chưa cân bằng (LogReg F1 0.245→0.314) nhưng không giúp RandomForest (đã balanced).

## 6. Kết quả (Test B — Dây chuyền mới)
| Mô hình | AUC-ROC | AUC-PR | F1 |
|---|---|---|---|
| **RandomForest** (+`osf_margin`) | 0.88 | **0.693** | **0.781** |
| XGBoost | 0.88 | 0.673 | 0.761 |
| LogReg | 0.74 | 0.246 | 0.314 |

- Mô hình tốt nhất: Recall **75%**, Precision **81%** trên nhà máy B (dữ liệu bị shift).
- **F1 ~0.78 là trần tự nhiên** (nhãn có yếu tố ngẫu nhiên; in-distribution best ~0.76; trần tuyệt đối test 0.782).

## 7. Quyết định kỹ thuật chính
1. **Metric:** AUC-PR (chọn mô hình) + F1 (so sánh) — bỏ accuracy vì imbalance.
2. **Chống leakage:** scaler fit-Train-only, giữ shift cho Phần 3.
3. **Mô hình cây** > tuyến tính (cơ chế phi tuyến/ngưỡng).
4. **FE theo cơ chế** vừa tăng AUC vừa bền qua shift.
5. **Chọn feature bằng số** (permutation/ablation), không cảm tính.
6. **Chọn phương pháp shift theo loại shift** (dịch trung bình → không dùng CORAL).

## 8. Hạn chế & hướng phát triển
- **Hạn chế:** vùng ngoại suy của Test (dự đoán kém tin cậy); nhãn ngẫu nhiên → trần hiệu năng; trọng số reweighting đuôi nặng (đã clip 99%).
- **Cải tiến:** domain adaptation (subspace/adversarial); **conformal prediction** cho vùng ngoại suy; giám sát **PSI online** (drift monitoring); thêm feature cần dữ liệu mới (tốc độ mòn dao, năng lượng cắt riêng, cảm biến rung/âm).

---
*Chi tiết quy trình: [`QUY_TRINH_LAM.md`](QUY_TRINH_LAM.md) · Giải thích khái niệm: [`README.md`](README.md) · Code: [`../bai_tap_cuoi_khoa.ipynb`](../bai_tap_cuoi_khoa.ipynb).*
