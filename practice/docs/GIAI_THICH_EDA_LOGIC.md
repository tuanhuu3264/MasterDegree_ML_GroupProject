# 🔗 Từ EDA → Insight → Hướng xử lý: sợi chỉ logic của bài tập

> Câu hỏi cốt lõi: *"Nhìn dữ liệu xong thì làm sao biết phải xử lý thế nào?"*
> Trả lời: mỗi quan sát trong EDA **kích hoạt một quyết định**. Dưới đây là toàn bộ chuỗi suy luận.

## 🧭 Khung tư duy 3 câu hỏi (áp cho MỌI quan sát)
Mỗi khi thấy điều gì lạ trong EDA, hỏi lần lượt:
1. **Có THẬT không?** — là quy luật vật lý thật, hay artifact/điểm cài cắm/lỗi đo?
2. **ẢNH HƯỞNG gì?** — nó làm mô hình sai kiểu nào nếu bỏ qua?
3. **LÀM GÌ?** — hành động cụ thể, thuộc phần nào của rubric.

---

# PHẦN 1 — LÀM EDA THEO THỨ TỰ NÀO (và mỗi bước dẫn tới quyết định gì)

## Bước 1 — Nhìn biến mục tiêu trước tiên (`hong_hoc`)
**Thấy:** tỷ lệ hỏng = **7.36%** (Train), 7.95% (Test). Rất ít máy hỏng.

| 3 câu hỏi | Trả lời |
|---|---|
| ① Có thật? | Có — imbalance là bản chất bài (hỏng hiếm). *Nhưng đề ghi "3–5%", thực đo 7–8% → dùng số thật.* |
| ② Ảnh hưởng? | Mô hình lười sẽ "đoán tất cả OK" → accuracy 92.6% nhưng **bắt 0 máy hỏng**. Accuracy trở nên vô nghĩa. |
| ③ Làm gì? | **(a)** Xử lý imbalance: `class_weight='balanced'` hoặc SMOTE → *Phần 2*. **(b)** Đánh giá bằng **F1, AUC-PR** thay vì accuracy → *Phần 4*. **(c)** Chia fold bằng **Stratified K-Fold** để mỗi fold đủ máy hỏng → *Phần 4*. |

➡️ **Logic:** *thấy imbalance* → **suy ra** accuracy vô dụng & mô hình thiên lệch → **quyết định** class_weight + F1/AUC-PR + stratified.

## Bước 2 — So phân phối Train (A) vs Test (B) từng feature
**Thấy:** đường KDE của Test lệch phải ở nhiệt độ (nóng hơn ~2.5 K), tốc độ cao hơn, mômen thấp hơn.

| 3 câu hỏi | Trả lời |
|---|---|
| ① Có thật? | Có — khớp bối cảnh "nhà máy B nóng hơn, tải khác". Đây là **distribution shift thật**. |
| ② Ảnh hưởng? | Mô hình học ở A sẽ gặp vùng dữ liệu lạ ở B → dự đoán kém khi triển khai. |
| ③ Làm gì? | **Định lượng** shift (PSI/KS/drift classifier) rồi **xử lý** (reweighting + threshold calibration) → *toàn bộ Phần 3*. |

➡️ **Logic:** *thấy 2 phân phối lệch nhau* → **suy ra** có shift → **quyết định** cả Phần 3 tồn tại để đo & sửa.

## Bước 3 — Correlation heatmap (feature ↔ target)
**Thấy:** tương quan tuyến tính với target **rất yếu** (|r| < 0.2, cao nhất là `do_mon_dao` ~0.19). Đồng thời `nhiet_do_moi_truong` ↔ `nhiet_do_quy_trinh` tương quan ~**0.90**.

| 3 câu hỏi | Trả lời |
|---|---|
| ① Có thật? | Có. Tương quan yếu **không** nghĩa là feature vô dụng — vì cơ chế hỏng theo **ngưỡng (phi tuyến)**, mà Pearson chỉ đo quan hệ **tuyến tính**. |
| ② Ảnh hưởng? | **(a)** Mô hình tuyến tính (LogReg) sẽ yếu → cần mô hình **cây**. **(b)** Feature thô khó tách lớp → cần **feature engineering**. **(c)** 2 nhiệt độ trùng 0.90 → dư thừa, nhưng **hiệu của chúng** mới có nghĩa (tản nhiệt). |
| ③ Làm gì? | **(a)** Tạo feature cơ học lộ cơ chế ngưỡng → *Phần 2*. **(b)** Ưu tiên RandomForest/XGBoost → *Phần 4*. **(c)** Tạo `chenh_lech_nhiet = process − air` thay vì dùng 2 nhiệt độ riêng → *Phần 2*. |

➡️ **Logic:** *thấy r yếu + 2 nhiệt độ trùng* → **suy ra** cơ chế phi tuyến & cần biến hiệu → **quyết định** FE + mô hình cây.

## Bước 4 — Nhìn kỹ thống kê mô tả & histogram (săn "điểm cài cắm")
**Thấy:** `toc_do_quay` có **309 dòng = đúng 1180.00**; `do_mon_dao` chạm trần 253; `momen_xoan` chạm sàn 3.5.

| 3 câu hỏi | Trả lời |
|---|---|
| ① Có thật? | **KHÔNG** — phân phối liên tục thật không thể có 309 giá trị trùng khít. Đây là **clipping/censoring nhân tạo** (điểm cài cắm). |
| ② Ảnh hưởng? | **(a)** Spike ở biên có thể bị mô hình hiểu nhầm là "tín hiệu". **(b)** min/max bị bóp méo → scaler nhạy outlier (MinMax) sẽ lệch. |
| ③ Làm gì? | **(a)** Ghi nhận là artifact, **không diễn giải** spike là quy luật vật lý. **(b)** Cân nhắc **RobustScaler** (dùng median/IQR, ít bị biên kéo) → *Phần 2*. |

➡️ **Logic:** *thấy pile-up bất thường ở biên* → **suy ra** clipping → **quyết định** dùng scaler robust + không over-interpret.

## Bước 5 — Kiểm tra biến phân loại (`loai_san_pham`, `ca_lam_viec`)
**Thấy:** tỷ lệ hỏng gần **phẳng** ở mọi giá trị của cả hai biến (~7–8%).

Đây là chỗ dễ **quyết định sai** nếu chỉ nhìn bề mặt → phải phân biệt 2 trường hợp:

| Biến | Nhìn bề mặt | Sự thật | Quyết định |
|---|---|---|---|
| `ca_lam_viec` | phẳng | **nhiễu thật** — ca sáng/chiều/đêm không ảnh hưởng cơ học. Drift-importance ≈ 0.01 xác nhận. | **Loại khỏi mô hình** (permutation ≈ 0) — đã minh hoạ ở EDA rằng nó vô dụng. |
| `loai_san_pham` | phẳng | **KHÔNG vô dụng** — nó quyết định **ngưỡng overstrain** (L:11000/M:12000/H:13000). Vai trò nằm ở **tương tác**, không ở marginal. | **Giữ + tạo `osf_margin`** = mòn×momen − ngưỡng(hạng) → nâng AUC-PR 0.681→0.693 (*Phần 2 & Phụ lục 6*). |

➡️ **Logic:** *thấy marginal phẳng* → **hỏi thêm** "có vai trò qua tương tác không?" → **quyết định** khác nhau cho 2 biến. Đây là bẫy tinh vi nhất.

## Bước 6 — So min/max Train vs Test (vùng ngoại suy)
**Thấy:** Test có 159 dòng **nóng hơn** máy nóng nhất của Train; tốc độ Test max 2414 ≫ Train max 2153.

| 3 câu hỏi | Trả lời |
|---|---|
| ① Có thật? | Có — hệ quả của shift (B vận hành ở vùng cực trị A chưa thấy). |
| ② Ảnh hưởng? | Ở vùng **ngoài phân phối train**, mọi mô hình đều đoán bấp bênh (phải **ngoại suy**). |
| ③ Làm gì? | **(a)** Ưu tiên mô hình **cây** (an toàn hơn khi ngoại suy so với đa thức). **(b)** Ghi vào **Hạn chế** + đề xuất conformal prediction → *Phần 5*. |

---

# 🗺️ SƠ ĐỒ TỔNG: QUAN SÁT → INSIGHT → HÀNH ĐỘNG

```
EDA quan sát                    Insight (suy ra)                 Hành động (rubric)
─────────────────────────────────────────────────────────────────────────────────
Target 7% hỏng           →  accuracy vô dụng, mô hình lệch  →  class_weight + F1/AUC-PR + Stratified  (P2,P4)
KDE A≠B, nhiệt lệch      →  distribution shift THẬT         →  PSI/KS/Drift + Reweight + Calibrate     (P3)
r tuyến tính yếu         →  cơ chế hỏng PHI TUYẾN            →  Feature engineering + mô hình cây       (P2,P4)
2 nhiệt độ corr 0.90     →  hiệu mới có nghĩa (tản nhiệt)    →  tạo chenh_lech_nhiet                    (P2)
Spike 1180 (309 dòng)    →  clipping nhân tạo (điểm cài cắm)        →  RobustScaler, không over-interpret      (P2)
ca_lam_viec phẳng        →  nhiễu thật                       →  giữ nhưng không over-engineer            (P2)
loai_san_pham phẳng      →  có vai trò qua TƯƠNG TÁC (OSF)   →  tạo osf_margin (mòn×momen−ngưỡng hạng)  (P2)
Test vượt biên train     →  vùng ngoại suy                   →  mô hình cây + ghi Hạn chế               (P4,P5)
```

---

# 🎓 QUY TẮC RÚT RA (áp cho mọi bài, không chỉ bài này)

1. **Luôn nhìn target trước** → quyết định metric & cách chia dữ liệu.
2. **Tương quan yếu ≠ vô dụng** → nghĩ tới quan hệ phi tuyến/tương tác trước khi loại feature.
3. **Marginal phẳng ≠ bỏ được** → kiểm tra vai trò qua tương tác (như `loai_san_pham`).
4. **Pile-up/giá trị lặp bất thường = nghi ngờ artifact** → đừng để mô hình học nhầm điểm cài cắm.
5. **Feature dư thừa (corr cao) → tìm phép biến đổi có nghĩa** (hiệu, tỷ số) thay vì bỏ bừa.
6. **So min/max 2 tập** → phát hiện ngoại suy → chọn mô hình & ghi hạn chế.
7. **Mọi quyết định xử lý phải truy ngược về 1 quan sát EDA cụ thể** — nếu không, đó là làm theo cảm tính.

> 💡 Điểm mấu chốt khi bảo vệ: giám khảo sẽ hỏi *"Vì sao bạn làm bước này?"*. Câu trả lời tốt luôn có dạng:
> **"Vì trong EDA tôi thấy [quan sát X], nghĩa là [insight Y], nên tôi [hành động Z]."**

---
*Đọc kèm: `bai_tap_cuoi_khoa.ipynb` (Phần 1 EDA có đủ biểu đồ cho từng quan sát trên).*
