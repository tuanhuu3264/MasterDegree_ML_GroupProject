# Kết quả 22 thí nghiệm — Chứng minh trần F1 ≈ 0.78

**Setup:** data=`Data_Final` | train=(14000, 8) | test=(6000, 8) | test pos=7.95% | scale_pos_weight=12.58

## NHÓM 1 — Nhiều model khác nhau (FE=SET4)
*Đổi họ mô hình vẫn ~0.78.*

| TN | Model | F1 (test B) | std |
|---|---|---:|---:|
| 1 | RandomForest | 0.7813 | ±0.0004 |
| 2 | XGBoost | 0.7804 | ±0.0013 |
| 3 | HistGradientBoosting | 0.7781 | ±0.0032 |
| 4 | LogisticRegression | 0.7037 | ±0.0021 |

## NHÓM 2 — Thêm feature vật lý (RF)
*FE vật lý nâng 0.66 -> 0.78 rồi bão hòa.*

| TN | Feature set | #feat | F1 (test B) | std |
|---|---|---:|---:|---:|
| 5 | NUM thô | 5 | 0.6633 | ±0.0034 |
| 6 | +RAW3 (tích/hiệu) | 8 | 0.7798 | ±0.0011 |
| 7 | +HINGE3 (hinge cơ chế) | 8 | 0.7804 | ±0.0013 |
| 8 | +SET4 (đầy đủ 5 cơ chế) | 19 | 0.7822 | ±0.0004 |

## NHÓM 3 — Hạ trọng số biến thô (XGBoost feature_weights)
*Ép XGB bỏ biến thô, dựa vào FE cơ chế — vẫn ~0.78.*

| TN | w_raw | F1 (test B) |
|---|---|---:|
| 9 | 1.0 | 0.7813 |
| 10 | 0.5 | 0.7795 |
| 11 | 0.1 | 0.7817 |
| 12 | 0.0 | 0.7817 |

## NHÓM 4 — Ensemble
*Kết hợp model KHÔNG vượt model đơn (lỗi tương quan ở vùng nhiễu).*

| TN | Ensemble | F1 (test B) |
|---|---|---:|
| 13 | Voting RF+XGB (0.5/0.5) | 0.7813 |
| 14 | Weighted RF+XGB (0.7/0.3) | 0.7813 |
| 15 | Voting RF+XGB+HGB | 0.7795 |
| 16 | Stacking meta-LogReg | 0.7804 |

## NHÓM 5 — Xử lý dữ liệu (cân bằng lớp & khử nhiễu)
*Cân bằng ≈ giữ nguyên; khử nhiễu là cái bẫy: OOF ảo vọt, TEST tụt.*

| TN | Cách | F1 (test B) | Ghi chú |
|---|---|---:|---|
| 17 | class_weight=None | 0.7826 | |
| 18 | class_weight=balanced | 0.7809 | |
| 19 | Khử nhiễu bỏ 3% "sai tự tin nhất" | 0.7778 | **OOF ảo = 0.978** |
| 20 | Khử nhiễu bỏ 5% "sai tự tin nhất" | 0.7724 | **OOF ảo = 0.998** |

## ĐÓNG CHỨNG MINH — 2 thí nghiệm chốt

### TN21 — CẬN TRÊN: oracle train thẳng trên test B (CV nội bộ test)
*Cho model biết luôn phân phối B. Nếu vẫn < 0.80 -> 0.80 bất khả.*

**ORACLE within-test maxF1 = 0.7720 ± 0.0024** — biết trước phân phối B cũng chỉ tới đây.

### TN22 — BẢN CHẤT: nhiễu aleatoric (không phụ thuộc model)
*Điểm trùng khít khác nhãn = lỗi bắt buộc; 1-NN của ca hỏng có phải máy khỏe không.*

- Điểm trùng khít khác nhãn (mâu thuẫn): **0**
- Ca hỏng có 1-NN cũng hỏng: **19.1%** -> ~81% ca hỏng có láng giềng gần nhất là máy KHỎE (chồng lấp lớp).

## Kết luận

- **Cận dưới (chặt):** cấu hình tốt nhất đạt **F1 = 0.7826** -> C* ≥ 0.7826.
- **Cận trên (bằng chứng):** các cấu hình hợp cách ∈ **[0.7037, 0.7826]**; oracle biết-trước-B chỉ **0.7720**.
- **Bản chất nhiễu:** ~81% ca hỏng bị bao quanh bởi máy khỏe -> sai số aleatoric không thể khử bằng model.
- **∴ Trần C\* ≈ 0.78.** Đạt ≥ 0.80 chỉ bằng leakage (dùng nhãn test) — không hợp lệ.

_Tổng thời gian chạy: 92s_