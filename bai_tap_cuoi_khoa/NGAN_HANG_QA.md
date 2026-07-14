# Ngân hàng câu hỏi & trả lời (Q&A) — Bảo trì dự đoán dưới Distribution Shift

> Chuẩn bị cho phần Hỏi & Đáp. Mỗi câu ghi **ai nên trả lời** (theo phần phụ trách) + **câu trả lời mẫu ngắn gọn**.
> Nguyên tắc: trả lời thẳng, có số, thừa nhận hạn chế khi cần (giám khảo đánh giá cao sự trung thực).

---

## A. Bài toán, dữ liệu & thước đo  *(Người 1)*

**A1. Vì sao không dùng accuracy?**
Lớp hỏng chỉ ~8%. Đoán "không hỏng" cho tất cả đã đúng 92% nhưng bắt được 0 máy hỏng → accuracy đánh lừa. Nhóm dùng **F1** (con số so sánh chính theo đề), kèm **AUC-PR** (hợp lớp hiếm) và AUC-ROC. Cơ sở "đoán tất cả hỏng" chỉ cho F1≈0,147; mô hình đạt 0,781.

**A2. F1, Precision, Recall khác nhau thế nào ở bài này?**
Precision = "trong các cảnh báo, bao nhiêu đúng" (0,81 → cứ 5 cảnh báo ~4 đúng). Recall = "bắt được bao nhiêu % máy hỏng" (0,75). F1 là trung bình điều hoà, cân bằng cả hai — chốt ở 0,781.

**A3. Vì sao chọn F1 làm số chính mà không phải AUC-PR?**
Đề yêu cầu rõ "F1 là con số dùng để so sánh giữa các nhóm". AUC-PR nhóm vẫn báo (0,670) như tham chiếu; thực tế v3/v4 có AUC-PR nhỉnh hơn v6 (0,676 vs 0,670) — nhóm nêu trung thực điều này.

**A4. Dữ liệu có sạch không? Xử lý thiếu/trùng thế nào?**
0 giá trị thiếu, **0 hàng trùng lặp** (đã kiểm `duplicated()`), nên giữ nguyên. Outlier ở đuôi được giữ vì là tín hiệu quá tải/thiếu tải (mô hình cây xử lý được), không cắt bỏ.

---

## B. Distribution shift — phát hiện  *(Người 2)*

**B1. Làm sao biết đây là *covariate* shift chứ không phải *label/concept* shift?**
Ba bằng chứng: (1) tỉ lệ hỏng gần như không đổi A→B (7,36%→7,95%) → prior nhãn ổn định; (2) `P(hỏng | vượt-ngưỡng)` gần như đứng yên (HDF 0,84→0,83) → quan hệ input→hỏng bất biến; (3) chỉ phân phối đầu vào dịch (PSI/KS/drift-AUC cao ở biến thô). Tức `P(x)` đổi, `P(y|x)` giữ nguyên = covariate shift.

**B2. PSI là gì? Ngưỡng bao nhiêu?**
Population Stability Index: chia 10 bin theo phân vị của Train, so % mẫu mỗi bin giữa A và B, cộng chênh lệch có trọng số log. Ngưỡng công nghiệp: <0,1 không đáng kể · 0,1–0,25 nhẹ · >0,25 mạnh. Nhiệt độ môi trường PSI 1,08 = rất mạnh.

**B3. (BẪY) Vì sao PSI của 2 đặc trưng vật lý ra đúng 0,0000? Nghi ngờ quá đẹp?**
*Câu quan trọng — trả lời trung thực:* Hai đặc trưng đó là **hinge, phần lớn giá trị = 0** (`nguy_tan_nhiet` ~98% số 0, `lech_cong_suat` ~88%). Khi phần lớn là 0, các mép bin theo phân vị trùng nhau → gộp còn 1–2 ô → PSI **bão hoà về 0 một cách máy móc**, không phản ánh đuôi. Thực tế vùng khác-0 vẫn dịch (+33% / −10%). **Vì vậy bằng chứng bất biến chính không phải PSI**, mà là **drift-AUC chỉ trên 3 đặc trưng = 0,51** (đo trên toàn phân phối) và **bảng P(hỏng|cờ)**. Nhóm hiểu rõ giới hạn của PSI ở feature thưa.

**B4. Drift classifier hoạt động thế nào? Vì sao dùng OOF?**
Gán nhãn giả A=0/B=1, huấn luyện phân loại chỉ từ số đo. AUC 0,5 = không phân biệt được (không shift), →1,0 = shift mạnh. Dùng **xác suất out-of-fold** (`cross_val_predict`) để không overfit khi lấy xác suất này làm trọng số reweighting. Kết quả: toàn bộ 0,82; chỉ đặc trưng vật lý 0,51.

**B5. Vì sao dùng KS statistic D mà không báo p-value?**
n rất lớn (A=14k, B=6k) → p-value ≈ 0 với hầu hết biến ("có ý nghĩa" ở đâu cũng thấy, vô dụng để so mức độ). Nên đọc **D** (khoảng cách CDF lớn nhất) để so *độ mạnh* shift.

---

## C. Feature Engineering  *(Người 2)*

**C1. Vì sao 3 đặc trưng "khoảng cách tới biên" chống shift tốt hơn tích thô (mòn×mômen, công suất)?**
Tích thô neo vào **biến đã dịch** (nhiệt độ, tốc độ) → nhập khẩu shift. Đặc trưng biên neo vào **hằng số cơ chế** (8,6K / 1380rpm / 3500–9000W / ngưỡng OSF theo loại SP) — là thuộc tính vật lý bất biến A↔B. Nên `P(hỏng|vượt-biên)` đứng yên qua shift.

**C2. Các ngưỡng 8,6K, 1380rpm… lấy từ đâu? Có phải "học lén" từ dữ liệu không?**
Là hằng số cơ chế sinh lỗi kiểu bộ dữ liệu **AI4I 2020** (HDF/PWF/OSF), KHÔNG ước lượng từ dữ liệu A hay B → không rò rỉ, không phụ thuộc phân phối. Đây chính là lý do chúng bất biến.

**C3. "Kiểm chứng" tác dụng đặc trưng bằng cách nào?**
Hai bằng chứng: (1) **ablation** giữ nguyên LogReg, chỉ thêm 3 đặc trưng → AUC-PR 0,22→0,50 (cô lập đúng đóng góp FE); (2) point-biserial corr với nhãn (0,18–0,24, ngang/hơn độ mòn dao) + |hệ số| LogReg xếp 3 đặc trưng lên nhóm đầu.

**C4. Vì sao `bien_overstrain` cần `loai_san_pham`?**
Ngưỡng OSF khác theo hạng SP ({L:11000, M:12000, H:13000}). Biến `mòn×mômen − ngưỡng(loại)` biến `loai_san_pham` (đơn biến trông vô dụng) thành **ngưỡng của luật** → có ý nghĩa.

---

## D. Xử lý shift & chống rò rỉ  *(Người 3)*

**D1. Importance Reweighting là gì? Vì sao phải clip trọng số?**
Trọng số `w(x)=P(B|x)/P(A|x)` (từ drift classifier) để mô hình "nhìn A như thể phân phối B". Vì `nhiet_do_moi_truong` dịch cực mạnh → vài mẫu có `w` thô tới ~57 → phải **clip [0,2; 10]** rồi chuẩn hoá mean=1, tránh vài mẫu cá biệt chi phối (high variance).

**D2. Reweighting chỉ tăng 0,669→0,672 — vậy có vô ích không?**
Ngược lại, đó là **kết quả có ý nghĩa**: nó chứng minh 3 đặc trưng vật lý đã hấp thụ gần hết shift (drift-AUC riêng chúng chỉ 0,51). Reweighting chỉ còn vá phần tín hiệu sót trong biến thô → dư địa nhỏ. "Làm đúng đặc trưng thì đỡ phải bù bằng thống kê."

**D3. (BẪY) Có nhìn nhãn Test B để chọn mô hình/ngưỡng không? Chứng minh?**
**Không.** Mọi lựa chọn (ngưỡng v4, trọng số voting, người thắng v6) chọn bằng **IWV trên OOF của Train** với trọng số density-ratio — không đụng `y_test`. `y_test` chỉ dùng trong `evaluate()` để *báo cáo* và đường "oracle" *chỉ để tham chiếu* (ghi rõ "KHÔNG dùng để chọn"). Nhãn B chấm đúng 1 lần cuối.

**D4. IWV là gì và vì sao đáng tin?**
Importance-Weighted Validation: đánh giá trên OOF của Train nhưng **đánh trọng số** để mô phỏng phân phối B → chọn model/ngưỡng "như thể ở B" mà không cần nhãn B. Kiểm định: đường F1-IWV bám sát đường F1-thật-trên-B (sát hơn hẳn đường A-thô). Lưu ý **ESS chỉ 25,5%** nên có nhiễu → coi các bản đầu bảng là ngang nhau.

**D5. (BẪY) Trọng số IWV tính một lần trên toàn A+B rồi dùng trong các fold — có rò rỉ không?**
Có một chút "circularity" (trọng số ước lượng từ model từng thấy fold validation), nhưng **chỉ ảnh hưởng trọng số, KHÔNG rò rỉ nhãn**; đây là thực hành chuẩn cho density-ratio. Giới hạn tin cậy thật sự đã phản ánh ở ESS 25,5%.

---

## E. Mô hình & Ensemble  *(Người 3)*

**E1. Vì sao Random Forest thắng XGBoost trên B dù XGB thường mạnh hơn?**
Đúng câu chuyện **bias–variance dưới shift**: bagging (RF, variance thấp) transfer sang phân phối mới tốt hơn boosting (XGB dễ khớp sát A). CV-trên-A: XGB nhỉnh (0,672 vs 0,664) nhưng trên B thì RF/gộp ổn hơn.

**E2. Tune siêu tham số thế nào? Có tune trên Test không?**
`RandomizedSearchCV` + `StratifiedKFold(5)`, scoring = `average_precision` (AUC-PR), **fit chỉ trên Train A**. Test B không tham gia tuning. Grid theo khoảng khuyến nghị (RF: max_features 'sqrt'/'log2'; XGB: max_depth 3–6, lr 0,03–0,1…).

**E3. Voting vs Stacking — vì sao chốt Voting?**
F1-IWV gần nhau (Voting 0,794 vs Stacking 0,791) — trong sai số. Chọn **Voting** vì đơn giản, khó overfit shift. Stacking nghiêng nặng XGB (hệ số meta ~4,6) — cái dễ gãy trên B → rủi ro hơn. Giữ cả hai để không đặt hết cược một cửa.

**E4. Vì sao gộp chỉ RF+XGB (50/50) mà bỏ LogReg, ExtraTrees?**
Trọng số do IWV tự chọn trên lưới simplex. LogReg/ExtraTrees yếu hơn hoặc trùng tín hiệu → IWV hạ về 0. Tương quan OOF: RF–XGB 0,95 (khá trùng) nhưng cặp này mạnh nhất; LogReg đa dạng (corr ~0,62) nhưng độ chính xác thấp.

---

## F. Đánh giá & độ tin cậy  *(Người 4)*

**F1. F1 = 0,781 có chắc chắn không?**
Chỉ 477 máy hỏng ở B → F1 có sai số. Bootstrap 2000 lần: **95% CI = [0,751; 0,809]**. Các bản đầu bảng (0,769–0,781) CI chồng lấn → không kết luận hơn-kém kiểu "0,781 > 0,773".

**F2. Vậy bản gộp có thật sự hơn mô hình đơn không?**
So **cặp** trên cùng resample: `P(F1_v6 > F1_xgb) = 99,8%`, delta +0,009 (CI [+0,003; +0,015], trọn phía dương) → nhỉnh **nhất quán về hướng** nhưng **biên độ nhỏ (~0,9%)**. Trung thực: hơn đáng tin nhưng không đáng kể.

**F3. (BẪY) So sánh bootstrap có công bằng không khi v6 dùng ngưỡng 0,705 còn XGB dùng 0,50?**
Đúng là chưa hoàn toàn like-for-like: v6 được chỉnh ngưỡng, XGB để mặc định 0,50 (điểm vận hành tự nhiên với `scale_pos_weight`). Nên phần chênh có phần đến từ chỉnh ngưỡng; nếu chỉnh ngưỡng cho cả hai, khoảng cách thu hẹp. Đây là hạn chế nhóm ghi nhận.

**F4. Confusion matrix nói gì?**
Ở ngưỡng 0,705: Recall ~75% (bắt đúng ~75% máy hỏng), Precision ~81%. FN (bỏ sót) là ô tốn kém nhất; FP (báo động giả) rẻ hơn. Vì FN đắt → thực tế có thể hạ ngưỡng để tăng Recall.

---

## G. Câu hỏi vận hành & mở rộng  *(Người 4)*

**G1. Đưa mô hình vào nhà máy thì dùng thế nào?**
Đề xuất **2 mức cảnh báo**: mức cao (Precision cao) → dừng máy kiểm tra ngay; mức thấp (Recall cao) → theo dõi/ lên lịch bảo trì. Vì model độc-lập-ngưỡng (AUC-PR/PR-curve), chọn 2 mốc theo chi phí thực tế.

**G2. Đổi sang dây chuyền C mới thì có phải train lại không?**
Nhờ đặc trưng neo ngưỡng vật lý bất biến, phần lõi transfer được mà **không cần train lại từ đầu** — chỉ cần kiểm PSI/drift-AUC trên C và tinh chỉnh ngưỡng bằng IWV. Đây là giá trị vận hành chính.

**G3. Hạn chế lớn nhất của bài?**
(1) Cây không ngoại suy → 2,8% máy B ngoài dải A dễ sai; (2) giả định covariate-shift-thuần **không kiểm chứng được** vì thiếu nhãn B — nếu B có concept drift thật thì reweighting/IWV vô hiệu; (3) ESS 25,5% → IWV nhiễu; (4) chỉ 5 số đo, nhãn gần tất định → có trần hiệu năng.

**G4. Nếu có thêm thời gian/dữ liệu sẽ làm gì?**
Hiệu chỉnh lại ngưỡng PWF (precision luật chỉ ~0,17); thêm đặc trưng chuỗi thời gian (xu hướng mòn dao) để cảnh báo sớm; domain adaptation nâng cao (CORAL, adversarial); thu thập một ít nhãn B (active learning) để kiểm chứng giả định; conformal prediction để kèm khoảng tin cậy mỗi cảnh báo.

**G5. Vì sao không dùng SMOTE cho lớp hiếm?**
Đề cho phép "class_weight HOẶC SMOTE". Nhóm chọn `class_weight`/`scale_pos_weight` vì: (a) không tạo mẫu tổng hợp giả trong bối cảnh đã có shift (SMOTE nội suy có thể sinh điểm phi vật lý); (b) đơn giản, không thêm siêu tham số; (c) kết hợp tự nhiên với tuning theo AUC-PR + chỉnh ngưỡng.

---

## H. Câu "chốt hạ" nếu bị hỏi dồn

**H1. Một câu, đâu là ý tưởng cốt lõi?**
"Dựng đặc trưng trên **hằng số vật lý bất biến** thay vì vá mô hình đã học trên biên dịch chuyển — nên biên học ở A dùng thẳng được trên B."

**H2. Điều nhóm tự tin nhất & điều lo nhất?**
Tự tin: phương pháp chống rò rỉ chặt chẽ (IWV, fit-train-only) + đặc trưng bất biến có bằng chứng số. Lo nhất: không có nhãn B để kiểm chứng giả định covariate-shift-thuần — đã ghi rõ trong Hạn chế.
