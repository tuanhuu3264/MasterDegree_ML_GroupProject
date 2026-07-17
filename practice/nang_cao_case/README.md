# 📂 nang_cao_case — 6 thử nghiệm nâng cao (mỗi cái gắn 1 bài giảng)

Đây là 6 notebook **độc lập, tự chạy được** (mỗi file có sẵn phần nạp dữ liệu + Feature Engineering).
Mục đích: bổ sung những **công cụ đã học trên lớp nhưng notebook chính chưa dùng**, để bài chặt hơn
và **dễ bảo vệ khi bị hỏi** (Phần 5 rubric). Mỗi file thử một hướng, có ghi chú kết luận ở cuối.

> Cách chạy 1 file: mở trong Jupyter và Run All, hoặc
> `PYTHONIOENCODING=utf-8 python -m nbconvert --to notebook --execute --inplace <ten_file>.ipynb`
> *(Trên Windows có thể thấy một dòng `KeyError ...joblib_memmapping...` lúc kernel tắt — vô hại,
> không ảnh hưởng kết quả các cell.)*

---

## Bảng tổng hợp kết quả

| File | Bài giảng | Câu hỏi trả lời | Kết quả chính |
|---|---|---|---|
| `01_decision_tree_nguong.ipynb` | **L6** Decision Tree | Cây có tự tìm ra ngưỡng cơ chế ta giả định không? | **Có.** Cây `depth=3` tự chia đúng: `do_mon_dao ≤ 243.95` (≈240 TWF), `chenh_lech_nhiet ≤ 8.60` (HDF), `toc_do_quay ≤ 1379.7` (≈1380), `cong_suat_co ≤ 2601` (vùng PWF-thấp) → xác nhận FE theo cơ chế. |
| `02_learning_curve_tran_F1.ipynb` | **L6** | F1 ~0.78 là trần thật hay do thiếu dữ liệu? | Đường validation **phẳng sớm** (AUC-PR ~0.65, Δ nửa sau = −0.001) → thêm dữ liệu vô ích → giới hạn là **nhiễu nhãn / trần Bayes**, không phải thiếu data. |
| `03_feature_selection_nhieu_phuongphap.ipynb` | **L5** | Chọn feature bằng nhiều phương pháp thì đồng thuận ra sao? | Chạy **10 phương pháp** (Filter/Wrapper/Embedded). Feature cơ chế được đa số giữ. **Top-6 feature cho F1 = 0.782 = y hệt bộ đầy đủ 11 feature** → có thể tinh gọn không mất điểm. |
| `04_da_cong_tuyen_VIF.ipynb` | **L3+L5** | Các feature phái sinh có đa cộng tuyến không? Ảnh hưởng gì? | VIF rất cao: bộ nhiệt = **∞** (vì `chenh_lech = quy_trinh − moi_truong` tuyến tính chính xác), `cong_suat` 96, `momen` 83. Hệ số **LogReg dao động mạnh** giữa các fold → cây/rừng **miễn nhiễm** (giải thích vì sao RF bền). Cách xử lý = **regularization** (Case 05). |
| `05_regularization_logreg.ipynb` | **L5** | Nên dùng L1/L2/ElasticNet cho LogReg? | **L1 & ElasticNet ≥ L2** (F1 0.306/0.308 vs 0.302). **L1 ép 3 hệ số về 0** (tự chọn feature kiểu Embedded). Khuyến nghị: thêm `penalty` vào grid của LogReg trong notebook chính. |
| `06_scaler_robust_vs_standard.ipynb` | **L5** | Có nên đổi sang RobustScaler vì dữ liệu bị clip? | Chênh lệch nhỏ (F1 Robust 0.308 ≥ Standard 0.306 ≥ MinMax 0.301); outlier rất ít (clip ở \|z\|=4). **Robust có lý lẽ hơn về nguyên tắc**; với cây/rừng thì scale **không quan trọng**. |

---

## Nên đưa gì vào notebook chính (đề xuất)

1. **Case 01 (cây nông + `plot_tree`)** — giá trị cao nhất, thêm 1 hình "đắt" chứng minh toàn bộ FE. Nên đưa vào Phần 1/2.
2. **Case 02 (learning curve)** — 1 cell, củng cố lập luận trần F1 ở phần kết luận / notebook nâng cao F1.
3. **Case 05 (mở `penalty` L1/L2/elasticnet)** — sửa ~1 dòng grid LogReg ở Phần 4.
4. **Case 04 (bảng VIF)** — 1 cell + 1 câu ở Phần 2, giải thích vì sao giữ feature phái sinh mà vẫn ổn (nhờ regularization / dùng cây).
5. **Case 03** — có thể trích bảng bỏ phiếu vào Phần 6 (Feature Selection) để "nói đúng ngôn ngữ Filter/Wrapper/Embedded".
6. **Case 06** — tùy chọn; ít nhất thêm 1 câu lý giải vì sao chọn scaler.

> Các con số nhỏ (F1 ~0.30 ở LogReg/scaler) là **của riêng mô hình LogReg tuyến tính** dùng để *minh hoạ kỹ thuật*,
> không phải kết quả cuối. Mô hình cuối vẫn là **RandomForest (F1 ≈ 0.78)**.
