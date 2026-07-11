# 🔬 Giải thích 6 thử nghiệm nâng cao (`nang_cao_case/`)

Tài liệu này giải thích rõ 6 notebook trong thư mục [`../nang_cao_case/`](../nang_cao_case/).
Mỗi thử nghiệm bổ sung **một công cụ đã học trên lớp** nhưng notebook chính chưa dùng tới, nhằm hai mục tiêu:

1. Làm bài **chặt hơn về phương pháp** (dùng đúng kỹ thuật giáo trình thay vì làm cảm tính).
2. **Dễ bảo vệ khi bị hỏi** — Phần 5 rubric chấm "giải thích được các quyết định kỹ thuật".

Mỗi mục dưới đây trình bày theo cùng một mạch: **kỹ thuật là gì → chạy để trả lời câu hỏi gì → con số nói lên điều gì → liên hệ bài giảng**.

> ⚠️ Các con số F1 ~0.30 ở Case 05 và 06 là **của riêng mô hình LogReg tuyến tính** (vốn yếu ở bài này),
> chỉ dùng để *minh hoạ tác động của kỹ thuật*. Kết quả cuối của bài vẫn là **RandomForest, F1 ≈ 0.78**.

---

## Bảng tổng hợp nhanh

| # | File | Bài giảng | Câu hỏi trả lời | Kết luận một dòng |
|---|---|---|---|---|
| 01 | `01_decision_tree_nguong.ipynb` | **L6** | Cây có tự tìm ra ngưỡng cơ chế ta giả định không? | **Có** — cây chia đúng 240 / 8.6 / 1380 → xác nhận Feature Engineering |
| 02 | `02_learning_curve_tran_F1.ipynb` | **L6** | F1~0.78 là trần thật hay do thiếu dữ liệu? | Trần thật — thêm data vô ích (đường validation phẳng) |
| 03 | `03_feature_selection_nhieu_phuongphap.ipynb` | **L5** | Chọn feature bằng nhiều phương pháp thì sao? | 10 phương pháp bỏ phiếu; **Top-6 feature = F1 y hệt bộ 11** |
| 04 | `04_da_cong_tuyen_VIF.ipynb` | **L3+L5** | Feature phái sinh cộng tuyến có hại không? | Hại LogReg, **không** hại cây → vì sao RF bền |
| 05 | `05_regularization_logreg.ipynb` | **L5** | Nên dùng L1/L2/ElasticNet cho LogReg? | L1/ElasticNet nhỉnh hơn; L1 tự loại 3 feature |
| 06 | `06_scaler_robust_vs_standard.ipynb` | **L5** | Có nên đổi RobustScaler vì dữ liệu bị clip? | Robust có lý lẽ hơn; cây thì scale vô nghĩa |

---

## Case 01 — Cây quyết định nông "lộ" ngưỡng cơ chế · *Bài L6*

**Kỹ thuật là gì.** Cây quyết định chia dữ liệu bằng các câu hỏi nối tiếp dạng "biến này ≤ ngưỡng?".
Mỗi lần chia, nó chọn ngưỡng làm hai nhánh con **sạch** nhất — đo bằng **Gini** (nhánh càng thuần một lớp thì Gini càng thấp).
Ta cố tình để cây **nông (max_depth = 3)** để nó buộc phải chọn vài ngưỡng *quan trọng nhất*, rồi đọc ra đó là ngưỡng nào.

**Chạy để trả lời gì.** Toàn bộ Feature Engineering dựa trên giả định "máy hỏng theo ngưỡng cơ chế" (mòn dao ~240 phút,
chênh lệch nhiệt ~8.6...). Nhưng đó là **ta tự giả định**. Cây quyết định không biết gì về giả định đó — nó chỉ nhìn dữ liệu.
Nếu nó **tự** chia đúng vào các ngưỡng ấy, giả định được xác nhận một cách khách quan.

**Con số nói gì.** Cây tự tìm ra (không hề được "mách"):

| Ngưỡng cây tìm | Ta giả định | Nhận xét |
|---|---|---|
| `do_mon_dao ≤ 243.95` | ~240 (TWF hao mòn dao) | trùng |
| `chenh_lech_nhiet ≤ 8.60` | 8.6 (HDF tản nhiệt kém) | trùng khít |
| `toc_do_quay ≤ 1379.70` | 1380 | trùng |
| `cong_suat_co ≤ 2601` | vùng công suất thấp (PWF) | đúng vùng |

Các đặc trưng cơ chế không phải "vẽ cho đẹp" — chính thuật toán độc lập cũng xác nhận đó là ranh giới thật.
Cây nông này chỉ đạt F1 = 0.752 (yếu hơn RandomForest vì quá cạn), nhưng **giá trị của nó là để *giải thích*, không phải để *dự đoán***.
Khi thầy hỏi "sao biết mòn dao 240 là ngưỡng?", ta chỉ tay vào hình cây.

**Liên hệ bài giảng.** L6: Gini/Entropy, cách chọn ngưỡng chia khi feature là số, overfitting theo `max_depth`.

---

## Case 02 — Learning Curve chứng minh F1 chạm trần · *Bài L6*

**Kỹ thuật là gì.** Learning curve = huấn luyện mô hình với lượng dữ liệu tăng dần (10%, 20%, ... 100% tập train),
mỗi lần đo điểm trên train và điểm kiểm định chéo (validation), rồi vẽ hai đường theo số mẫu.

**Chạy để trả lời gì.** Ta kết luận F1~0.78 là "trần tự nhiên do nhãn có yếu tố ngẫu nhiên". Có một phản biện hiển nhiên:
*"Hay tại ít dữ liệu quá? Thêm data thì F1 lên chứ?"*. Learning curve trả lời chính xác câu này.

**Con số nói gì.** Điểm validation (AUC-PR) theo lượng data:
`0.646 → 0.659 → 0.651 → 0.661 → 0.653 → 0.654 → 0.649 → 0.652`.
Đường **đi ngang từ rất sớm**, nửa sau còn giảm nhẹ (Δ = −0.001) → đã **bão hòa**. Cho ăn thêm dữ liệu, nó không nhích lên.
Kết luận: giới hạn hiệu năng **không** đến từ thiếu dữ liệu, mà từ **nhiễu trong nhãn (trần Bayes)**.

Đây là **bằng chứng thứ hai, độc lập** với lập luận resubstitution-vs-CV (F1 huấn luyện lại = 1.0 nhưng CV chỉ ~0.76) đã dùng ở notebook nâng cao F1.
Hai bằng chứng cùng chỉ về một kết luận: **F1 > 0.8 chỉ đạt được nếu rò rỉ dữ liệu (vi phạm đề)**.

**Liên hệ bài giảng.** L6: Learning Curve & Validation Curve; L5: Bias–Variance (đường phẳng, gap nhỏ = high-bias/irreducible).

---

## Case 03 — Chọn feature bằng 10 phương pháp · *Bài L5*

**Kỹ thuật là gì.** L5 dạy ba nhóm cách chọn feature:

| Nhóm | Ý tưởng | Phương pháp thử ở đây |
|---|---|---|
| **Filter** | Chấm điểm từng feature độc lập với mô hình (nhanh, thô) | VarianceThreshold · High-correlation · Mutual Information · ANOVA F-test |
| **Wrapper** | Thử nhiều tổ hợp, huấn luyện mô hình cho từng tổ hợp (chậm, chính xác) | RFE · RFECV · Sequential Forward |
| **Embedded** | Mô hình tự chọn feature trong lúc học | Lasso L1 · RandomForest MDI · Permutation |

**Chạy để trả lời gì.** Phần 6 notebook chính loại feature bằng cảm nhận + vài chỉ số. Ở đây ta chạy **cả 10 phương pháp**
rồi cho chúng **bỏ phiếu**: feature nào được nhiều phương pháp giữ thì càng đáng tin. Đây là cách chọn feature *có phương pháp*, đúng ngôn ngữ giáo trình.

**Con số nói gì.**
- Các feature cơ chế (`do_mon_dao`, `osf_margin`, `tich_mon_momen`, `cong_suat_co`) được **đa số phương pháp cùng giữ** → đồng thuận cao, đúng kỳ vọng domain.
- Bộ lọc high-correlation tự đánh dấu cặp **`osf_margin ↔ momen_xoan`** trùng thông tin — chính là "điểm cài cắm" tương tác trong dữ liệu.
- Điểm mạnh nhất: **lấy Top-6 feature theo phiếu cho F1 = 0.782, đúng bằng bộ đầy đủ 11 feature (0.782)**.

| Bộ feature | Số feature | F1 |
|---|---|---|
| Đầy đủ | 11 | 0.782 |
| Đồng thuận (≥60% phương pháp) | 10 | 0.782 |
| Top-6 phiếu | 6 | 0.782 |

Nghĩa là **hơn nửa số feature là dư thừa** — dùng bộ gọn 6 feature vẫn giữ nguyên F1, mô hình đơn giản và dễ giải thích hơn.

**Liên hệ bài giảng.** L5: toàn bộ khung Filter / Wrapper / Embedded (RFE/RFECV, Mutual Information, Lasso, Permutation).

---

## Case 04 — Đa cộng tuyến (Multicollinearity) & VIF · *Bài L3 + L5*

**Kỹ thuật là gì.** Đa cộng tuyến = một feature có thể suy ra gần đúng từ các feature khác.
**VIF (Variance Inflation Factor)** đo mức độ đó: đem từng feature hồi quy theo các feature còn lại, được R²; rồi **VIF = 1 / (1 − R²)**.
Quy ước: VIF > 5 đáng ngờ, VIF > 10 cộng tuyến **nặng**. (statsmodels không có sẵn nên ta tính tay bằng công thức này.)

**Chạy để trả lời gì.** Các feature ta tạo đều là **hàm của biến gốc** (`chenh_lech_nhiet = nhiet_quy_trinh − nhiet_moi_truong`,
`cong_suat = momen × tốc_độ`...) nên chắc chắn cộng tuyến với biến cha. Câu hỏi: điều đó có làm hỏng mô hình không?

**Con số nói gì.**

| Feature | VIF | Vì sao |
|---|---|---|
| bộ 3 nhiệt (môi trường / quy trình / chênh lệch) | **∞** | chênh lệch là hiệu tuyến tính chính xác → R² = 1.0 |
| `cong_suat_co` | 96 | = momen × tốc độ |
| `momen_xoan` | 83 | xuất hiện trong nhiều feature phái sinh |
| `tich_mon_momen` | 38 | = mòn × momen |
| `osf_margin` | 18 | phái sinh từ tích mòn×momen |

Và khi chạy LogReg trên từng fold, **hệ số dao động mạnh** (ví dụ `momen` lệch ±0.156 giữa các fold) — dấu hiệu kinh điển của cộng tuyến làm mô hình bất ổn.

**Điểm mấu chốt:** chuyện này **chỉ hại mô hình tuyến tính (LogReg)**. Cây và rừng chia theo ngưỡng *từng biến một* nên
**không quan tâm** feature có trùng nhau hay không → đây chính là lời giải thích vì sao **RandomForest bền vững**.
Vì thế ta **không cần bỏ** các feature cộng tuyến (chúng vẫn mang thông tin cơ chế) — chỉ cần dùng **regularization** cho LogReg (→ Case 05).

**Liên hệ bài giảng.** L3: Đa cộng tuyến, phân tích phần dư; L5: vì sao cần regularization.

---

## Case 05 — Regularization L1 / L2 / ElasticNet cho LogReg · *Bài L5*

**Kỹ thuật là gì.** Regularization = thêm "hình phạt" lên độ lớn hệ số để mô hình không quá khớp và ổn định hơn:

| Loại | Cách phạt | Tác dụng đặc trưng |
|---|---|---|
| **L2 (Ridge)** | bình phương hệ số | co nhỏ đều mọi hệ số — hợp khi có cộng tuyến (Case 04) |
| **L1 (Lasso)** | trị tuyệt đối hệ số | **ép hẳn một số hệ số về 0** → tự loại feature (Embedded) |
| **ElasticNet** | trộn L1 + L2 | vừa co vừa loại |

**Chạy để trả lời gì.** Notebook chính chỉ khai báo `penalty='l2'`, bỏ phí hai lựa chọn kia dù đã học. Ta so cả ba.

**Con số nói gì.**

| Penalty | Hệ số khác 0 | AUC-PR | F1 |
|---|---|---|---|
| L2 | 12/12 | 0.235 | 0.302 |
| L1 | 9/12 | 0.238 | 0.306 |
| ElasticNet | 9/12 | 0.237 | 0.308 |

L1 và ElasticNet nhỉnh hơn L2 một chút. Đáng chú ý hơn: **L1 ép 3 hệ số về đúng 0**
(`nhiet_do_quy_trinh` và hai mức của `loai_san_pham`) — tức nó tự nói "ba feature này bỏ đi cũng được",
**khớp với kết luận đồng thuận ở Case 03**.

**Khuyến nghị thực dụng:** trong `RandomizedSearchCV` của LogReg, thêm `penalty` vào lưới tìm kiếm
(`l1`/`l2`/`elasticnet`, solver `saga`) để máy tự chọn — vừa đúng tinh thần L5, vừa cho câu chuyện
"regularization vừa chống overfit vừa ổn định hóa cộng tuyến".

**Liên hệ bài giảng.** L5: Ridge / Lasso / Elastic Net, hình học L1/L2, Embedded selection bằng LASSO.

---

## Case 06 — RobustScaler vs Standard vs MinMax · *Bài L5*

**Kỹ thuật là gì.** Ba cách đưa feature về cùng thang đo:

| Scaler | Công thức | Nhạy outlier? |
|---|---|---|
| **Standard** | (x − trung bình) / độ lệch chuẩn | có (trung bình/độ lệch bị outlier kéo) |
| **Robust** | (x − trung vị) / IQR | ít (dùng trung vị) |
| **MinMax** | ép về [0, 1] | rất nhạy |

**Chạy để trả lời gì.** Dữ liệu có "điểm cài cắm clipping" (giá trị bị cắt dồn ở biên → outlier nhân tạo).
Về nguyên tắc, khi có outlier thì Robust an toàn hơn. Ta kiểm bằng số.

**Con số nói gì.** Chênh lệch rất nhỏ: Robust F1 = 0.308 ≥ Standard 0.306 ≥ MinMax 0.301.
Đếm outlier cũng ít (bị clip ở |z| = 4 nên không có đuôi cực đoan). Kết luận: Robust **có lý lẽ hơn** cho dữ liệu bị clip,
nhưng khác biệt không lớn vì LogReg + class_weight vốn đã khá bền; và với **mô hình cuối (cây/rừng) thì thang đo hoàn toàn không quan trọng**.
Thông điệp: chọn scaler phải có **lý do gắn với đặc điểm dữ liệu**, không chọn theo quán tính.

**Liên hệ bài giảng.** L5: Standardization vs Min-Max vs Robust; Feature Scaling.

---

## Nên đưa gì vào notebook chính (đề xuất ưu tiên)

1. **Case 01 (cây nông + `plot_tree`)** — giá trị cao nhất; thêm một hình "đắt" chứng minh toàn bộ FE. → Phần 1 hoặc 2.
2. **Case 02 (learning curve)** — 1 cell, củng cố lập luận trần F1. → Kết luận / notebook nâng cao F1.
3. **Case 05 (mở `penalty` L1/L2/elasticnet)** — sửa ~1 dòng grid LogReg. → Phần 4.
4. **Case 04 (bảng VIF)** — 1 cell + 1 câu giải thích vì sao giữ feature phái sinh mà vẫn ổn. → Phần 2.
5. **Case 03** — trích bảng bỏ phiếu vào Phần 6 để "nói đúng ngôn ngữ Filter/Wrapper/Embedded".
6. **Case 06** — tùy chọn; ít nhất thêm 1 câu lý giải vì sao chọn scaler.

> Xem thêm bảng kết quả gọn ở [`../nang_cao_case/README.md`](../nang_cao_case/README.md).
