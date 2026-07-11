# 🎤 Cẩm nang thuyết trình — Chia việc cho 4 người

> Mục tiêu: 4 người **hiểu phần mình + hiểu tổng thể**, trình bày mạch lạc, trả lời được câu hỏi.
> Giả định: tổng **~16–20 phút** (mỗi người ~4 phút) + 5 phút hỏi đáp. Điều chỉnh được.

---

## 🧩 PHÂN CÔNG TỔNG QUAN

| Người | Phụ trách | Phần rubric | Điểm | Vai trò |
|---|---|---|---|---|
| **P1** | Bối cảnh + EDA + các **điểm cài cắm** | Phần 1 | 1.0 | Người **mở màn** — kể câu chuyện, gây ấn tượng "team quan sát kỹ" |
| **P2** | Tiền xử lý + Feature Engineering | Phần 2 | 1.5 | Người **nền tảng** — chống rò rỉ, tạo feature cơ học |
| **P3** | **Distribution Shift** (trọng tâm) | Phần 3 | 2.0 | Người **chủ lực** — phần khó & nặng điểm nhất, chọn bạn tự tin nhất |
| **P4** | Mô hình + Đánh giá + Kết luận | Phần 4+5 | 2.5 | Người **chốt hạ** — kết quả, insight vận hành, hạn chế |

> 💡 Nguyên tắc vàng: **mỗi phần đều truy về EDA**. Câu trả lời chuẩn luôn có dạng:
> *"Vì trong EDA thấy [X] → nghĩa là [Y] → nên tôi làm [Z]."*

---

## 🌐 PHẦN CẢ TEAM PHẢI THUỘC (nói được trong 30 giây)

**Câu "thang máy" (elevator pitch):**
> *"Chúng em xây mô hình dự đoán hỏng máy phay CNC. Thách thức chính là **distribution shift**: dữ liệu huấn luyện lấy từ nhà máy A (mát), nhưng triển khai ở nhà máy B (nóng hơn, tải khác). Chúng em **phát hiện, định lượng và xử lý** shift đó, đồng thời nhận ra một số **điểm cài cắm** trong dữ liệu. Mô hình tốt nhất — RandomForest — đạt **F1 = 0.78, AUC-PR = 0.69** trên nhà máy B."*

**1 câu insight cốt lõi (ai cũng phải nói được):**
> *"Đây là **covariate shift** chứ không phải concept drift — quy luật vật lý gây hỏng KHÔNG đổi, chỉ điều kiện vận hành đổi. Vì vậy Feature Engineering theo cơ chế + Importance Reweighting + Threshold Calibration là hướng đúng."*

**6 điểm cài cắm (ai bị hỏi cũng liệt kê được vài cái):**
1. `toc_do_quay` cắt sàn nhân tạo tại 1180 (309 dòng trùng).
2. `do_mon_dao`/`momen_xoan` cắt biên (253/3.5).
3. Tỷ lệ hỏng thực ~7–8% ≠ đề ghi "3–5%".
4. `ca_lam_viec` là nhiễu thuần.
5. `loai_san_pham` biên phẳng nhưng có vai trò qua tương tác (OSF).
6. Test ngoại suy vượt biên Train.

---

# 👤 NGƯỜI 1 — Bối cảnh & EDA & Điểm cài cắm (Phần 1)

**🎯 Nhiệm vụ:** kể câu chuyện bài toán, chỉ ra bằng chứng distribution shift, và "khoe" các điểm cài cắm đã phát hiện (đây là điểm cộng lớn).

**📊 Trình 4 thứ:**
1. Bối cảnh: dự đoán hỏng, nhà máy A→B, imbalance ~7%.
2. So phân phối A vs B (biểu đồ KDE) → dấu hiệu shift.
3. Correlation heatmap → tương quan tuyến tính yếu.
4. Bảng 6 điểm cài cắm.

**🗣️ Kịch bản mẫu:**
> *"Bài toán là dự đoán máy hỏng trong ca kế tiếp. Chỉ ~7% máy hỏng nên đây là bài mất cân bằng mạnh — accuracy vô nghĩa, chúng em dùng F1 và AUC-PR. Khi so phân phối 2 nhà máy [chỉ biểu đồ], nhiệt độ nhà máy B cao hơn ~2.5 độ, tốc độ cao hơn — đúng bối cảnh khí hậu nóng hơn. Đặc biệt, chúng em phát hiện dữ liệu có vài điểm cài cắm: ví dụ tốc độ quay có 309 dòng trùng khít 1180 — dấu hiệu cắt biên nhân tạo..."*

**🔢 Số phải thuộc:** 7.36% hỏng (train) / 7.95% (test); tỷ lệ 12.6:1; nhiệt độ +2.5K; tốc độ +70rpm; spike 1180 có 309 dòng.

**❓ Có thể bị hỏi:**
- *"Vì sao tương quan yếu mà vẫn giữ feature?"* → Vì cơ chế hỏng theo **ngưỡng (phi tuyến)**, Pearson chỉ đo quan hệ thẳng → cần feature engineering + mô hình cây.
- *"Làm sao biết 1180 là cài cắm chứ không phải tự nhiên?"* → Phân phối liên tục thật không thể có 309 giá trị trùng **khít**; các giá trị khác chỉ xuất hiện 1–2 lần.

---

# 👤 NGƯỜI 2 — Tiền xử lý & Feature Engineering (Phần 2)

**🎯 Nhiệm vụ:** giải thích chống rò rỉ dữ liệu và feature cơ học + tinh chọn feature (đây là chỗ ghi điểm "hiểu bản chất").

**📊 Trình 3 thứ:**
1. Scaler **fit chỉ trên Train** → transform cả hai (chống leakage).
2. Feature cơ học: `chenh_lech_nhiet` (HDF), `cong_suat_co` (PWF), `tich_mon_momen` (OSF), và `osf_margin` = mòn×momen − ngưỡng(L/M/H) (OSF theo hạng SP).
3. Tinh chọn feature bằng permutation/ablation: **bỏ** `momen_tren_tocdo` (importance 0) & `ca_lam_viec` (nhiễu); **thêm** `osf_margin`.
4. Kiểm chứng: 3 feature cơ chế → AUC 0.867→0.878; `osf_margin` → AUC-PR 0.681→0.693.

**🗣️ Kịch bản mẫu:**
> *"Nguyên tắc quan trọng nhất là chống rò rỉ: chúng em học 'thước đo' chuẩn hoá CHỈ từ nhà máy A, rồi áp cho cả B — không nhìn trộm B. Điểm tinh tế: sau chuẩn hoá, dữ liệu B KHÔNG có trung bình 0 — đúng như vậy, vì đó chính là shift cần giữ. Về feature, thay vì để mô hình tự mò, chúng em tính sẵn các con số biết nói: công suất = mômen × tốc độ (quá tải công suất), và đặc biệt `osf_margin` = mòn×momen − ngưỡng theo hạng sản phẩm, mã hoá cơ chế quá tải căng thẳng. Sau đó tinh chọn feature bằng permutation importance: bỏ 2 feature nhiễu, thêm `osf_margin` — nâng AUC-PR từ 0.681 lên 0.693."*

**🔢 Số phải thuộc:** công thức công suất $P=\tau\times\frac{2\pi\cdot rpm}{60}$; AUC 0.867→0.878; `osf_margin` nâng AUC-PR 0.681→0.693; permutation: `do_mon_dao` 0.29, `chenh_lech_nhiet` 0.15 (top 2).

**❓ Có thể bị hỏi:**
- *"Vì sao không fit scaler trên cả train+test?"* → Leakage: thông tin Test lọt vào → đánh giá ảo; ngoài ra sẽ xoá mất shift.
- *"Vì sao chọn class_weight thay vì SMOTE?"* → Dưới shift, SMOTE dễ tạo mẫu giả không thực tế; class_weight ổn định hơn (nhưng vẫn minh hoạ SMOTE để đối chứng).
- *"Feature nào quan trọng nhất?"* → `do_mon_dao` (0.29) và `chenh_lech_nhiet` (0.15) — feature tự tạo quan trọng thứ 2, chứng minh FE thành công.
- *"Vì sao bỏ `momen_tren_tocdo` và `ca_lam_viec`?"* → Permutation importance = 0.000 và 0.001 (nhiễu); bỏ đi F1 không giảm, model gọn hơn. Đo bằng số, không cảm tính.
- *"Vì sao chỉ thêm `osf_margin` mà không thêm cả loạt feature cơ chế?"* → Cây tự tìm ngưỡng trên 1 biến (công suất, mòn dao) nên margin của chúng thừa; chỉ `osf_margin` (tương tác mòn×momen vs ngưỡng theo hạng) là cây khó tự tạo → có ích. Thêm tất cả thì AUC-PR không tăng (đã thử).

---

# 👤 NGƯỜI 3 — Distribution Shift (Phần 3, TRỌNG TÂM)

**🎯 Nhiệm vụ:** phần nặng điểm & khó nhất. Trình bày **đo shift** (PSI/KS/Drift) và **xử lý shift** (Reweighting/Calibration).

**📊 Trình 4 thứ:**
1. Bảng PSI + KS → phân loại mức shift.
2. Drift classifier: AUC 0.81 + feature thủ phạm.
3. Importance Reweighting (density-ratio $w=p/(1-p)$).
4. Threshold Calibration + so sánh trước/sau.

**🗣️ Kịch bản mẫu:**
> *"Chúng em đo shift bằng 3 cách. PSI và KS cho từng biến: nhiệt độ môi trường PSI=1.08 (shift mạnh), còn độ mòn dao gần như không đổi. Sau đó huấn luyện một 'thám tử' phân biệt A/B — đạt AUC 0.81, khẳng định shift mạnh, thủ phạm chính là nhiệt độ. Để xử lý, chúng em cân lại mẫu Train bằng tỷ số mật độ — coi trọng hơn những mẫu A giống B — và hiệu chỉnh ngưỡng, giúp F1 tăng từ 0.721 lên 0.729."*

**🔢 Số phải thuộc:** PSI air 1.08, mòn dao 0.001; ngưỡng PSI 0.1/0.25; Drift AUC 0.81; F1 0.721→0.729; công thức $w=p/(1-p)$.

**❓ Có thể bị hỏi (phần này bị hỏi nhiều nhất):**
- *"Vì sao dùng $w=p/(1-p)$?"* → $p$ = xác suất "thuộc Test" từ drift classifier; theo Bayes, tỷ số odds $p/(1-p)$ tỷ lệ với density-ratio $P_{test}/P_{train}$ — chính là trọng số importance sampling.
- *"Reweighting cải thiện ít, vậy có vô ích không?"* → **Không** — đó là kết quả **đúng & trung thực**: vì là covariate shift mà mô hình cây + feature cơ học đã hấp thụ phần lớn shift. Reweighting hiệu quả rõ hơn với mô hình tuyến tính.
- *"Sao biết là covariate shift chứ không phải concept drift?"* → Vì $P(hỏng | cơ chế)$ ổn định giữa A/B (ví dụ tản nhiệt kém → xác suất hỏng 0.84 ở A và 0.83 ở B).
- *"PSI khác KS thế nào?"* → PSI cho **độ lớn** (mạnh/nhẹ); KS cho **kiểm định thống kê** (p-value). Dùng cả hai.

---

# 👤 NGƯỜI 4 — Mô hình, Đánh giá & Kết luận (Phần 4 + 5)

**🎯 Nhiệm vụ:** chốt kết quả, đọc metric đúng cách, rút insight vận hành & hạn chế.

**📊 Trình 4 thứ:**
1. 3 mô hình + tuning (RandomizedSearchCV + Stratified K-Fold).
2. Bảng so sánh (F1, AUC-PR, AUC-ROC) + PR-curve.
3. Ma trận nhầm lẫn của mô hình tốt nhất.
4. Kết luận: insight bảo trì + hạn chế + cải tiến.

**🗣️ Kịch bản mẫu:**
> *"Chúng em thử 3 mô hình, tinh chỉnh bằng RandomizedSearch với Stratified K-Fold để mỗi fold đủ mẫu hỏng. RandomForest tốt nhất: AUC-PR 0.69, F1 0.78. Điều thú vị: LogReg kém hẳn (AUC-PR 0.25) — khẳng định cơ chế hỏng là phi tuyến. Ma trận nhầm lẫn cho thấy bắt được 75% máy hỏng với 81% độ chính xác. Về vận hành: nên giám sát tản nhiệt và công suất, thay dao theo chỉ số mòn×mômen, và hiệu chỉnh lại ngưỡng cảnh báo khi chuyển sang nhà máy B. Hạn chế lớn nhất là vùng ngoại suy của B..."*

**🔢 Số phải thuộc:** RandomForest F1 0.78, AUC-PR 0.686, AUC-ROC 0.885; Recall 75%, Precision 81%; TP=358, FN=119, FP=85; LogReg AUC-PR 0.25.

**❓ Có thể bị hỏi:**
- *"Vì sao dùng AUC-PR thay AUC-ROC?"* → Với imbalance mạnh, AUC-ROC lạc quan; AUC-PR tập trung vào lớp thiểu số (hỏng).
- *"Vì sao F1 là số so sánh chính?"* → Cân bằng Precision & Recall, không cho "ăn gian" bằng cách hi sinh một trong hai; đề cũng yêu cầu.
- *"Nếu muốn bỏ sót ít hơn thì sao?"* → Hạ ngưỡng → Recall tăng (bù lại báo oan tăng); chọn theo chi phí thực (dừng máy vs bảo trì thừa).
- *"Hạn chế lớn nhất?"* → Test ngoại suy vượt biên train → dự đoán vùng đó kém tin cậy; đề xuất thu thêm dữ liệu B + conformal prediction.

---

## ⏱️ LUỒNG THUYẾT TRÌNH (gợi ý 16 phút)

```
0:00  P1  Bối cảnh + EDA + điểm cài cắm            (4')
4:00  P2  Tiền xử lý + Feature Engineering         (4')
8:00  P3  Distribution Shift (trọng tâm)           (5')
13:00 P4  Mô hình + Kết luận                        (3')
16:00     Hỏi đáp — mỗi người trả lời phần mình
```

**Chuyển tiếp mượt (nói khi trao mic):**
- P1→P2: *"Đã thấy dữ liệu có shift và điểm cài cắm, giờ [P2] sẽ nói cách xử lý & tạo feature."*
- P2→P3: *"Có feature tốt rồi, [P3] sẽ trình phần trọng tâm — đo và xử lý shift."*
- P3→P4: *"Xử lý shift xong, [P4] tổng kết mô hình và kết luận."*

---

## ✅ CHECKLIST TRƯỚC BUỔI
- [ ] Mỗi người **chạy notebook 1 lần**, xem output phần mình.
- [ ] Thuộc **6 điểm cài cắm** + **1 câu insight covariate shift**.
- [ ] Thuộc **số của phần mình** (bảng trên).
- [ ] Tập nói phần mình **1 lần bấm giờ**.
- [ ] Thống nhất ai trả lời câu hỏi "lấn sân" (mặc định: ai phụ trách phần đó).
- [ ] Chuẩn bị mở sẵn notebook để chỉ trực tiếp biểu đồ khi bị hỏi.

## 🛡️ NGUYÊN TẮC TRẢ LỜI CÂU HỎI
1. **Không biết → không bịa.** Nói: *"Chỗ này em chưa kiểm chứng kỹ, nhưng hướng em nghĩ là…"*.
2. **Luôn quy về EDA:** "Vì em thấy [X] nên làm [Z]".
3. **Trung thực về hạn chế** (reweighting cải thiện ít, vùng ngoại suy) — giám khảo đánh giá cao sự thành thật hơn là khoe số đẹp.

---
*Đọc kèm: `bai_tap_cuoi_khoa.ipynb` (có ô 🔎 diễn giải cạnh mỗi biểu đồ) · `GIAI_THICH_TUNG_BUOC.md` (ví dụ dễ hiểu) · `GIAI_THICH_2_VERSION.md` (học thuật ↔ dễ hiểu).*
