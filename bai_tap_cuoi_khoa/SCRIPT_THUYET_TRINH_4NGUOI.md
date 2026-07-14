# Script thuyết trình — chia 4 người (v5)

> Deck: `C:/Users/LEGION/AppData/Local/Temp/claude/D--studies-Master-s-Degree-MSE-Session-1-ML-GroupProject-bai-tap-cuoi-khoa/b0b6e863-aebc-4618-98e8-e039d29f16c9/scratchpad/v5_build.pptx`. Script này cũng nằm trong **speaker notes** của từng slide.
> Tổng ~13–14 phút + Q&A. Mỗi người ~3–3.5 phút. Chuyển người ở các slide "Divider".

## Thứ tự & phân công nhanh

| Người | Slide phụ trách | Nội dung | Thời lượng |
|---|---|---|---|
| — (chung) | 1–2 | Slide mở đầu + Agenda | ~0.5' |
| 1 | 3–9 | Bài toán, shift, bản đồ đề, EDA | ~3' |
| 2 | 10–14 | Tiền xử lý, 3 đặc trưng, PSI/KS, drift | ~3' |
| 3 | 15–20 | Reweighting, IWV, 4 mô hình, ensemble | ~3.5' |
| 4 | 21–29 | Kết quả, confusion matrix, bootstrap, báo cáo, quyết định kỹ thuật, kết luận, Q&A | ~4' |


---

## MC / chung

### ▸ Slide mở đầu

MC/Người 1: Kính chào thầy/cô và các bạn. Nhóm em trình bày bài toán dự đoán máy CNC sắp hỏng trong bối cảnh 'dữ liệu lúc học khác dữ liệu lúc dùng thật' (distribution shift). Kết quả chốt: F1 = 0.781 trên nhà máy B, gấp 3.4 lần baseline, notebook chạy full không lỗi. Bài chia làm 4 phần do 4 thành viên trình bày.

### ▸ Agenda

Người 1: Nhóm em chia 4 phần. Người 1 trình bày bài toán và khám phá dữ liệu; Người 2 phần tiền xử lý, tạo đặc trưng và phát hiện shift; Người 3 xử lý shift và xây mô hình; Người 4 kết quả, độ tin cậy và kết luận. Hai khối nhiều điểm nhất là xử lý shift và kết quả thực trên nhà máy B.


---

## NGƯỜI 1 — Mở đầu & EDA

### ▸ Divider Phần 1

Người 1: Em bắt đầu với bài toán và phần khám phá dữ liệu.

### ▸ Bài toán

Người 1: Mục tiêu là dự đoán nhị phân — máy có hỏng ở ca kế tiếp hay không — để bảo trì chủ động. Có 5 số đo cảm biến và 2 nhãn phân loại. Hai điểm khiến bài khó: thứ nhất máy hỏng chỉ ~8% nên rất hiếm, dùng accuracy là vô nghĩa, phải dùng F1 và AUC-PR; thứ hai, tập huấn luyện là nhà máy A còn tập chấm là nhà máy B với điều kiện vận hành khác — đó là distribution shift.

### ▸ Shift là gì

Người 1: Distribution shift nghĩa là dữ liệu lúc học khác lúc dùng thật. Giống như học lái ở quê rồi ra thành phố. Điểm mấu chốt: cơ chế vật lý gây hỏng thì giống nhau ở A và B, chỉ có các con số đầu vào bị lệch — đây là covariate shift. Và luật chơi khó nhất: bị chấm trên B nhưng không được nhìn nhãn B. Chiến lược của nhóm gồm 3 bước: đo mức lệch, tạo đặc trưng miễn nhiễm với lệch, rồi tinh chỉnh.

### ▸ Bản đồ đề

Người 1: Bài của nhóm bám đúng 5 phần chấm điểm. Lưu ý thang điểm: riêng xử lý shift 2 điểm và kết quả thật trên B 3 điểm — cộng lại là một nửa tổng điểm, nên nhóm đầu tư nặng nhất vào hai khối này.

### ▸ EDA 1.1

Người 1: Máy hỏng chỉ khoảng 7-8% ở cả hai nhà máy. Điều quan trọng: tỉ lệ hỏng gần như không đổi giữa A và B, nghĩa là cái lệch nằm ở số đo đầu vào chứ không phải ở nhãn — đây là covariate shift. Dữ liệu sạch: không thiếu, không trùng. Bảng bên phải cho thấy nhà máy B nóng hơn và quay nhanh hơn, riêng độ mòn dao gần như bằng nhau.

### ▸ EDA 1.2

Người 1: Định lượng mức lệch: nhà máy B nóng hơn 2-2.5 độ và độ dao động nhiệt rộng hơn gần 30%, quay nhanh hơn 70 vòng/phút, lực xoắn thấp hơn 8.5%. Riêng độ mòn dao gần như bằng nhau — đây là biến ổn định để mô hình bám vào. Trên histogram, phân phối A và B không trùng nhau, đó là shift nhìn thấy bằng mắt.

### ▸ EDA 1.3-1.4

Người 1: Về dấu hiệu hỏng: độ mòn dao tách rõ nhất. Các biến khác nhìn riêng thì yếu, nhưng máy hỏng có tốc độ và lực xoắn dồn về hai đầu — hỏng do quá tải hoặc thiếu tải, tức tín hiệu phi tuyến theo tổ hợp, nên cần mô hình cây và feature engineering. Kiểm tra thêm bằng chi-square: ca làm việc không lệch, nhưng loại sản phẩm có lệch. Và 2.8% máy B nằm ngoài dải giá trị của A — vùng này mô hình cây dễ sai, nhóm ghi vào phần hạn chế. Em xin chuyển cho bạn Người 2.


---

## NGƯỜI 2 — Tiền xử lý, FE & Phát hiện shift

### ▸ Divider Phần 2

Người 2: Cảm ơn bạn. Em trình bày phần tiền xử lý, tạo đặc trưng và phát hiện shift.

### ▸ Phần 2.1

Người 2: Tiền xử lý gồm chuẩn hoá số đo và mã hoá nhãn chữ. Quy tắc vàng chống rò rỉ dữ liệu: chỉ học tham số chuẩn hoá trên nhà máy A rồi áp cho cả hai, tuyệt đối không fit trên B. Nếu vi phạm sẽ có điểm ảo cao nhưng triển khai thật thất bại. Loại sản phẩm mã hoá theo thứ tự L<M<H, ca làm việc one-hot. Lớp hiếm xử lý bằng class_weight và scale_pos_weight khoảng 12.6. Tất cả gói trong Pipeline nên trong mỗi fold cross-validation đều fit lại đúng cách.

### ▸ Phần 2.2 — ý tưởng cốt lõi

Người 2: Đây là ý tưởng cốt lõi của cả bài. Thay vì tạo tích thô, nhóm mã hoá 'khoảng cách tới ngưỡng hỏng' cho 3 cơ chế: tản nhiệt kém, quá/thiếu công suất, và quá tải căng thẳng. Điểm hay là các ngưỡng này là hằng số vật lý của máy, không đổi giữa A và B, nên 3 đặc trưng miễn nhiễm với shift. Kiểm chứng: chỉ thêm 3 đặc trưng này, mô hình LogReg đơn giản đã mạnh gần gấp đôi, AUC-PR từ 0.22 lên 0.50.

### ▸ Phần 3.1 — PSI + caveat

Người 2: Nhóm dùng PSI và KS đo mức lệch từng biến. Hai biến nhiệt độ lệch rất mạnh, PSI 1.08 và 0.55. Ngược lại, 3 đặc trưng vật lý có PSI xấp xỉ 0, dù chúng được tạo từ chính nhiệt độ và tốc độ đang lệch — đây là bằng chứng số cho ý tưởng chính. Một lưu ý trung thực nhóm chủ động nêu: hai đặc trưng hinge phần lớn bằng 0 nên PSI bị bão hoà về 0; vì vậy bằng chứng bất biến mạnh hơn là drift-AUC 0.51 và bảng P(hỏng|cờ) ở slide sau, chứ không chỉ dựa vào PSI. Nêu điều này cho thấy nhóm hiểu sâu công cụ.

### ▸ Phần 3.2 — drift classifier

Người 2: Kỹ thuật drift classifier: huấn luyện một mô hình đoán mẫu thuộc nhà máy A hay B, chỉ từ số đo. Nếu đoán dễ nghĩa là hai nhà máy khác nhau nhiều. Dùng toàn bộ số đo thô thì AUC 0.82 — lệch mạnh, thủ phạm là hai biến nhiệt độ. Nhưng chỉ dùng 3 đặc trưng vật lý thì AUC rơi về 0.51, gần như tung đồng xu — chúng tàng hình với shift. Củng cố thêm: tỉ lệ hỏng khi máy vượt ngưỡng nguy hiểm gần như giống nhau ở A và B, 0.84 so với 0.83, chứng tỏ cơ chế hỏng bất biến. Em chuyển cho bạn Người 3.


---

## NGƯỜI 3 — Xử lý shift & Mô hình

### ▸ Divider Phần 3

Người 3: Cảm ơn bạn. Em trình bày cách xử lý shift và xây dựng mô hình.

### ▸ Phần 3.3 — reweighting

Người 3: Kỹ thuật xử lý shift thứ nhất là Importance Reweighting. Ý tưởng: máy A nào trông giống máy B thì cho trọng số cao hơn khi học, để mô hình học nghiêng về phân phối B. Trọng số lấy từ drift classifier, và phải chặn ≤ 10 để vài mẫu cá biệt không chi phối. Kết quả chỉ nhích nhẹ — và đây là tin tốt: nó chứng minh 3 đặc trưng vật lý đã gánh gần hết việc chống lệch, reweighting chỉ vá phần nhỏ còn lại.

### ▸ Phần 3.4 — IWV

Người 3: Vấn đề đạo đức: bị chấm trên B nhưng không được nhìn nhãn B. Giải pháp là IWV — Importance-Weighted Validation. Ta dùng dữ liệu A nhưng đánh trọng số density-ratio để nó giống phân phối B, tạo thành một bộ validation giả lập B mà không cần nhãn B. Nhờ đó mọi lựa chọn model và ngưỡng đều trung thực. Ngưỡng mặc định 0.5 không tối ưu cho lớp hiếm nên nhóm chỉnh lại để F1 cao nhất. Kiểm định cho thấy đường IWV bám sát đường thật trên B, nên harness đáng tin. Lưu ý ESS chỉ 25.5% nên có nhiễu, các bản đầu bảng coi như ngang nhau.

### ▸ Phần 4.1 — models

Người 3: Nhóm thử 4 mô hình thuộc 3 trường phái: Logistic Regression làm mốc; Random Forest và ExtraTrees kiểu bagging nhiều cây bỏ phiếu, ổn định; và XGBoost kiểu boosting nhiều cây sửa lỗi nối tiếp, mạnh nhưng dễ overfit nhà máy A. Siêu tham số dò tự động bằng RandomizedSearchCV với StratifiedKFold 5 fold giữ đúng tỉ lệ hỏng, chấm theo AUC-PR. Việc chọn mô hình dùng IWV chứ không nhìn nhãn B.

### ▸ Phần 4.2 — bảng so sánh

Người 3: Bảng so sánh toàn bộ hành trình trên nhà máy B. Baseline LogReg thô F1 chỉ 0.231. Thêm 3 đặc trưng vật lý lên 0.352. Chuyển sang mô hình cây nhảy vọt lên ~0.77. Reweighting và chỉnh ngưỡng giữ nguyên mức đó. Bản gộp cuối cùng đạt F1 0.781 — cao nhất. F1 là con số chính theo yêu cầu đề. Cột 'báo đúng' là Precision, 'bắt được' là Recall.

### ▸ Phần 4.3 — ensemble

Người 3: Bước cuối là gộp mô hình. Vì mỗi mô hình sai ở chỗ khác nhau, gộp lại sẽ bù trừ và ổn định hơn. Nhóm thử hai cách: Voting là trung bình Random Forest và XGBoost, mỗi cái 50%; Stacking là mô hình nhỏ học cách trộn. Chọn bằng IWV và chốt Voting vì đơn giản, khó overfit shift. Stacking nghiêng nặng XGBoost, cái dễ gãy trên B, nên giữ nhưng không chốt. Em xin chuyển cho bạn Người 4 trình bày kết quả.


---

## NGƯỜI 4 — Kết quả, Độ tin cậy & Kết luận

### ▸ Divider Phần 4

Người 4: Cảm ơn bạn. Em trình bày kết quả cuối, độ tin cậy và bài học.

### ▸ Kết quả cuối

Người 4: Kết quả chốt trên nhà máy B: F1 = 0.781, cao nhất trong mọi phiên bản. Bản chốt là gộp Random Forest và XGBoost bằng Voting, ngưỡng 0.705 chọn bằng IWV. Mô hình bắt được khoảng 75% máy sắp hỏng, và cứ 5 cảnh báo thì khoảng 4 đúng. So với baseline 0.231, đây là tiến bộ 3.4 lần. Đường PR-curve nằm cao hơn hẳn đường đoán bừa nên mô hình thực sự có giá trị.

### ▸ Confusion matrix (slide MỚI)

Người 4: Đây là ma trận nhầm lẫn của bản chốt, giúp nhìn tường minh 4 ô. TP là bắt đúng máy hỏng — mục tiêu chính. FN là bỏ sót máy hỏng, tốn kém nhất vì máy dừng đột ngột. FP là báo động giả, chi phí chỉ là kiểm tra thừa nên rẻ hơn. Ở ngưỡng 0.705, Recall khoảng 75% và Precision khoảng 81%. Vì bỏ sót đắt hơn báo động giả, trong thực tế nhà máy có thể hạ ngưỡng để tăng Recall. Lưu ý: số cụ thể mỗi ô sẽ hiện sau khi chạy full notebook.

### ▸ Bootstrap

Người 4: Vì chỉ có 477 máy hỏng ở B nên F1 có sai số, nhóm dùng bootstrap 2000 lần để báo khoảng tin cậy. F1 = 0.781 với khoảng tin cậy 95% từ 0.751 đến 0.809. Các bản đầu bảng chênh nhau rất nhỏ nên nhóm coi như ngang nhau, không thổi phồng hơn kém. Khi so cặp trực tiếp thì bản gộp thắng bản đơn 99.8% số lần nhưng biên độ nhỏ. Đây là cách trình bày trung thực về mặt thống kê.

### ▸ Phần 5.1 — insight

Người 4: Bài học vận hành: thứ nhất, theo dõi độ mòn dao là quan trọng nhất vì nó vừa báo hỏng tốt vừa can thiệp được bằng cách thay dao. Thứ hai, đặt cảnh báo theo ngưỡng vật lý thì dùng lại được khi đổi máy hay đổi nhà máy, không cần huấn luyện lại. Thứ ba, vì bỏ sót đắt hơn báo động giả, nhóm đề xuất hai mức cảnh báo: mức cao thì dừng máy kiểm tra ngay, mức thấp thì theo dõi và lên lịch bảo trì.

### ▸ Phần 5.2 — hạn chế

Người 4: Nhóm trung thực nêu hạn chế: mô hình cây đoán kém ở 2.8% máy B nằm ngoài dải A; giả định cơ chế hỏng bất biến chưa kiểm chứng 100% vì không có nhãn B; độ tin IWV giới hạn với ESS 25.5%; và dữ liệu chỉ 5 số đo nên có trần hiệu năng. Hướng cải tiến: hiệu chỉnh lại ngưỡng công suất, thêm dữ liệu chuỗi thời gian, dùng domain adaptation nâng cao, và thu thập một ít nhãn B để kiểm chứng.

### ▸ Quyết định kỹ thuật & lý do

Người 4: Slide này tổng hợp mọi quyết định kỹ thuật và lý do, cho thấy bài làm có mạch logic chặt chẽ — không quyết định nào là tuỳ tiện. Đây cũng là bảng tra để nhóm trả lời nhanh khi thầy/cô hỏi 'vì sao chọn cái này'. Ví dụ: dùng F1 vì lớp hiếm; 3 đặc trưng vật lý vì ngưỡng cơ chế bất biến qua shift; chọn model bằng IWV để không rò rỉ nhãn B; clip trọng số vì w thô nổ tới 57; chốt Voting vì đơn giản và khó overfit shift.

### ▸ Kết luận

Người 4: Tóm lại, chìa khoá của bài là bám vào quy luật vật lý không đổi thay vì các con số thô đã lệch; nhờ đó mô hình học ở A vẫn chạy tốt trên B. Mọi lựa chọn đều trung thực qua IWV, không nhìn đáp án B. Kết quả F1 0.781, gấp 3.4 lần baseline. Nhóm em xin cảm ơn và sẵn sàng trả lời câu hỏi.

### ▸ Q&A

Cả nhóm: mời thầy/cô đặt câu hỏi. Phân công trả lời theo phần phụ trách; xem ngân hàng câu hỏi kèm theo.

