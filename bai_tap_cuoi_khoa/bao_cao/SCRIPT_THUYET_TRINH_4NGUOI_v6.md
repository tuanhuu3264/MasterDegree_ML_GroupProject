# Script thuyết trình — 4 người (deck `SLIDE_THUYET_TRINH_v6.pptx`, 28 slide)

> Tổng **~13–14 phút** + Q&A. Chuyển người ở 4 slide **Divider**: **S3, S9, S14, S20**.
> Ký hiệu: **[mở]** câu mở phần · **[chuyển]** câu bàn giao người kế · *(cue: …)* động tác/nhấn mạnh ·
> **⇒** câu chốt "vì sao" (nói chậm, ăn điểm tiêu chí *trình bày logic*).
> Kỷ luật lặp lại xuyên suốt cho ăn điểm Phần 5: *"mọi lựa chọn chọn bằng IWV — không nhìn nhãn Test B."*

## Phân công nhanh

| Người | Slide | Nội dung | Thời lượng |
|---|---|---|---|
| — (chung) | 1–2 | Title + Agenda | ~0,5' |
| **Người 1** | 3–8 | Bài toán · distribution shift · EDA (Phần 1) | ~3' |
| **Người 2** | 9–13 | Tiền xử lý · 3 đặc trưng · PSI+KS · drift classifier (Phần 2 + 3.1–3.2) | ~3,5' |
| **Người 3** | 14–19 | Reweighting · IWV · 4 mô hình · so sánh · ensemble (Phần 3.3–3.4 + Phần 4) | ~3,5' |
| **Người 4** | 20–28 | Kết quả · confusion · bootstrap · insight · hạn chế · quyết định · kết luận · Q&A | ~3,5' |

---

## NGƯỜI 1 — Mở đầu & Khám phá dữ liệu (S1–S8, ~3')

**S1 — Title.** **[mở]** "Kính chào thầy/cô và các bạn. Nhóm em trình bày bài toán **dự đoán máy CNC sắp hỏng khi dữ liệu lúc học khác lúc dùng thật**. Kết quả chốt: **F1 = 0,781** trên nhà máy B, gấp **3,4 lần** mô hình ban đầu, và notebook chạy full **không lỗi**. Bài gồm 4 phần do 4 thành viên trình bày."

**S2 — Nội dung.** "Mạch trình bày 4 khối: em — bài toán & khám phá dữ liệu; Người 2 — tiền xử lý, tạo đặc trưng & phát hiện shift; Người 3 — xử lý shift & xây mô hình; Người 4 — kết quả, độ tin cậy & kết luận. *(cue: chỉ bảng)* Hai khối nặng điểm nhất là **xử lý shift (2đ)** và **kết quả thật (3đ)**."

**S3 — Divider Phần 1.** "Em bắt đầu Phần 1 — Mở đầu và khám phá dữ liệu."

**S4 — Bài toán.** "Nhà máy có đội máy phay CNC; ta muốn đoán **máy nào sẽ hỏng ở ca kế tiếp** để sửa trước, tức chuyển từ bảo trì bị động sang chủ động. Dữ liệu gồm 5 số đo cảm biến và 2 nhãn phân loại. Có **hai thách thức cốt lõi**: một là máy hỏng chỉ **~8%** — rất hiếm, nên **accuracy vô nghĩa**, phải dùng F1/AUC-PR; hai là học ở nhà máy A nhưng chạy ở nhà máy B nóng hơn, nhanh hơn — đó là **distribution shift**. ⇒ Hai thách thức này định hình mọi quyết định phía sau."

**S5 — Vì sao khó.** "Distribution shift nghĩa là phân phối đầu vào ở B lệch khỏi A — ví như học lái ở đường quê rồi phải chạy trong phố. **May mắn** là *nguyên nhân* gây hỏng vẫn theo cùng quy luật vật lý ở cả A và B; chỉ có *các con số* bị lệch. Cái khó nhất: **bị chấm trên B nhưng không được xem đáp án của B** — xem là rò rỉ. ⇒ Chiến lược 3 bước: **đo** mức lệch, **tạo đặc trưng miễn nhiễm** lệch, rồi **tinh chỉnh** thêm."

**S6 — Phần 1.1 Máy hỏng hiếm cỡ nào.** "Nhà máy A có 7,36% hỏng, B có 7,95% — **tỉ lệ hỏng gần như không đổi**. Đây là chi tiết quan trọng: cái lệch nằm ở **số đo đầu vào**, không phải ở nhãn — nên đây là *covariate shift*, hợp với importance reweighting. Dữ liệu sạch: 0 thiếu, 0 trùng. ⇒ Vì hỏng quá hiếm nên nhóm chốt dùng **F1** ngay từ đầu."

**S7 — Phần 1.2 Hai nhà máy lệch thế nào.** "Đo bằng số: từ A sang B, **nhiệt độ môi trường +2,5°, nhiệt độ máy +1,9°, tốc độ +70 vòng/phút**, lực xoắn thấp hơn ~8,5%, riêng **độ mòn dao gần như không đổi**. *(cue: chỉ histogram)* Nhìn biểu đồ, hai màu A–B **không trùng nhau** — đó là shift thấy tận mắt. ⇒ Độ mòn dao là chỗ **neo tin cậy** vì nó ổn định qua hai nhà máy."

**S8 — Phần 1.3–1.4 Dấu hiệu hỏng & vùng lạ.** "Về tương quan: **độ mòn dao rõ nhất** — máy hỏng mòn ~177 phút so với máy lành ~123. Các biến khác nhìn riêng gần như không tách được, nhưng tốc độ và lực xoắn của máy hỏng **dồn về hai đầu** (rất cao hoặc rất thấp) — tức quá tải hoặc thiếu tải. Về phân loại: ca làm việc không lệch, nhưng loại sản phẩm **có lệch**; và **2,8% máy B nằm ngoài dải A** — nhóm ghi vào Hạn chế vì mô hình cây dễ sai ở vùng lạ. ⇒ Tín hiệu hỏng **phức tạp theo tổ hợp** → cần mô hình mạnh và đặc trưng khéo. **[chuyển]** Mời Người 2 trình bày cách xử lý dữ liệu và tạo đặc trưng."

---

## NGƯỜI 2 — Tiền xử lý, Đặc trưng & Phát hiện shift (S9–S13, ~3,5')

**S9 — Divider Phần 2.** **[mở]** "Cảm ơn bạn. Em là Người 2, trình bày tiền xử lý, ba đặc trưng vật lý, và phần đo shift."

**S10 — Phần 2.1 Chuẩn bị dữ liệu.** "Số đo được đưa về cùng thang cho mô hình tuyến tính; mô hình cây thì không cần. **Quy tắc vàng chống rò rỉ**: chỉ học cách chuẩn hoá **trên A**, rồi áp cho cả A và B — không bao giờ nhìn lén B. Nhãn chữ đổi thành số: loại sản phẩm L<M<H giữ thứ tự nên dùng Ordinal; ca làm việc không thứ tự nên One-Hot. Lớp hiếm xử bằng **phạt nặng khi bỏ sót** (class_weight ≈ 12,6), **không dùng SMOTE**. Tất cả gói trong Pipeline, fit lại đúng trong từng fold. ⇒ Nếu nhìn lén B, điểm cao trên giấy nhưng triển khai thật sẽ sụp — đây là điều đề nhấn mạnh nhất ở Phần 2."

**S11 — Phần 2.2 Ba đặc trưng vật lý.** "Đây là **ý tưởng cốt lõi cả bài**. Nhóm tạo 3 đặc trưng đo *'máy còn cách ngưỡng hỏng bao xa'*: **nguy_tan_nhiet** (tản nhiệt kém), **lech_cong_suat** (quá/thiếu công suất), **bien_overstrain** (quá tải theo loại sản phẩm). Điểm hay: các ngưỡng — 8,6 độ, 1380 vòng/phút, dải 3500–9000W — là **hằng số vật lý**, không đổi giữa A và B, nên 3 đặc trưng **miễn nhiễm với shift**. Kiểm chứng bằng số theo yêu cầu đề: chỉ thêm 3 đặc trưng, mô hình đơn giản mạnh gần **gấp đôi** — AUC-PR từ 0,22 lên 0,50. ⇒ Cả ba tương quan với hỏng ngang hoặc hơn độ mòn dao, chứng tỏ không phải thêm cho có."

**S12 — Phần 3.1 PSI + KS.** "Bước đầu của xử lý shift là **đo** mức lệch từng biến bằng hai thước đo: **PSI** và **KS**. *(cue: chỉ bảng)* Hai biến nhiệt độ lệch mạnh — PSI 1,08 và 0,55, KS 0,43 và 0,31; tốc độ và lực xoắn lệch nhẹ; còn **3 đặc trưng vật lý PSI ≈ 0 và KS ≈ 0,01** — gần như không lệch, dù chúng được dựng từ chính các biến nhiệt độ đang lệch mạnh. **Lưu ý trung thực** (điểm cộng): hai đặc trưng hinge phần lớn bằng 0 nên PSI bị bão hoà về 0; nên bằng chứng bất biến **chính** là drift-AUC 0,51 ở slide sau, chứ không chỉ dựa PSI. ⇒ Shift dồn ở biến thô, đặc trưng biên đã hấp thụ nó."

**S13 — Phần 3.2 Drift Classifier.** "Cách xác định **shift nằm ở đâu**: huấn luyện một mô hình đoán *'máy này thuộc A hay B'* chỉ từ số đo — đoán càng dễ thì hai nhà máy càng khác. Dùng **tất cả số đo → AUC 0,82** (lệch mạnh); nhưng chỉ dùng **3 đặc trưng vật lý → AUC 0,51**, tức gần như tung đồng xu. *(cue: chỉ dòng importance)* **Feature importance** của mô hình này cho thấy hai biến nhiệt độ chiếm **~54%** — đúng là **thủ phạm chính** gây shift. Thêm bằng chứng: khi máy vượt ngưỡng nguy hiểm thì tỉ lệ hỏng **giống nhau** ở A và B (0,84 so với 0,83). ⇒ Ba lát cắt — PSI, drift-AUC, importance — cùng một kết luận. **[chuyển]** Mời Người 3 trình bày cách xử lý shift và xây mô hình."

---

## NGƯỜI 3 — Xử lý shift & Xây mô hình (S14–S19, ~3,5')

**S14 — Divider Phần 3.** **[mở]** "Cảm ơn bạn. Em là Người 3, trình bày xử lý shift và bốn mô hình."

**S15 — Phần 3.3 Reweighting.** "Kỹ thuật xử lý lệch thứ nhất — **Importance Reweighting**: máy A nào **trông giống B** thì cho *'điểm chú ý'* cao hơn khi học, để mô hình học nghiêng về B. Điểm chú ý = mức giống B chia mức giống A, lấy từ drift classifier. Phải **chặn điểm quá lớn** (giới hạn 10) để vài máy lạ không chi phối toàn bộ. Kết quả trước–sau: AUC-PR chỉ nhích nhẹ 0,669 lên 0,672. ⇒ **Nhích nhẹ là tin tốt**: ba đặc trưng vật lý đã lo gần hết việc chống lệch, kỹ thuật này chỉ vá phần nhỏ — làm đúng đặc trưng thì đỡ phải bù bằng thống kê."

**S16 — Phần 3.4 IWV & ngưỡng.** "Kỹ thuật thứ hai giải **nghịch lý chấm điểm**: bị chấm trên B nhưng cấm xem đáp án B — vậy chọn mô hình bằng gì? Câu trả lời là **IWV — Importance-Weighted Validation**: dùng dữ liệu A nhưng đánh trọng số cho phần *'giống B'*, tạo một bộ chấm thử **giả lập B** mà không cần nhãn B. Nhờ đó thử–sai bao nhiêu cũng không gian lận; nhãn B chỉ dùng **một lần cuối** để báo cáo. Ta cũng chỉnh **ngưỡng báo hỏng** cho F1 cao nhất thay vì để mặc định 0,5. *(cue: chỉ đồ thị)* Đường chấm-thử-giả-lập bám sát đường kết-quả-thật-trên-B → harness đáng tin. ⇒ Đây là chốt kỷ luật của cả bài: **chọn mọi thứ bằng IWV, không nhìn nhãn B**."

**S17 — Phần 4.1 Thử 4 mô hình.** "Nhóm thử **4 mô hình thuộc 3 trường phái** để lát gộp cho đa dạng: Logistic Regression làm mốc; Random Forest và ExtraTrees kiểu *nhiều cây bỏ phiếu*, ổn định; XGBoost kiểu *nhiều cây sửa lỗi nối tiếp*, mạnh nhưng dễ học thuộc A. Dò siêu tham số **tự động bằng RandomizedSearchCV** với **StratifiedKFold 5** giữ đúng tỉ lệ hỏng. Chấm bằng F1/AUC-PR, chọn model bằng IWV. ⇒ Đủ yêu cầu đề: **≥3 mô hình + tuning + K-Fold**."

**S18 — Phần 4.2 Bảng so sánh.** "*(cue: chỉ bảng)* Đọc theo cột **F1** — con số so sánh chính theo đề. Từ mô hình thô **0,231**, thêm 3 đặc trưng lên 0,352, chuyển sang cây nhảy vọt lên ~0,77; reweighting và chỉnh ngưỡng giữ ổn định; **bản gộp cuối cùng đạt 0,781**. Cột *báo đúng* là Precision, *bắt được* là Recall. ⇒ Hành trình **0,231 → 0,781 = gấp 3,4 lần**, mỗi bước cải tiến đều đo được."

**S19 — Phần 4.3 Ensemble.** "Ý tưởng gộp: mỗi mô hình sai ở chỗ khác nhau, gộp lại thì bù trừ, ổn định hơn. Hai cách: **Bỏ phiếu** (trung bình Random Forest + XGBoost, mỗi cái 50%) và **Trộn** (một mô hình nhỏ học cách trộn 4 mô hình con). Chọn cách tốt hơn **bằng IWV** → chốt **Bỏ phiếu** vì đơn giản, khó sai, khó overfit shift. Vẫn giữ cả hai để không đặt hết cược một cửa. ⇒ Bản chốt v6 là **Voting RF + XGB**. **[chuyển]** Mời Người 4 trình bày kết quả cuối và kết luận."

---

## NGƯỜI 4 — Kết quả, Độ tin cậy & Kết luận (S20–S28, ~3,5')

**S20 — Divider Phần 4.** **[mở]** "Cảm ơn bạn. Em là Người 4, trình bày kết quả cuối, độ tin cậy và phần báo cáo."

**S21 — Kết quả cuối trên B (3đ).** "Trên nhà máy B — tập mô hình **chưa từng thấy**: **F1 = 0,781**, bắt được **~75%** máy hỏng (Recall), và **4 trên 5** cảnh báo là đúng (Precision ~81%). *(cue: chỉ PR-curve)* Đường PR của bản chốt cao hơn hẳn đường *đoán bừa*. ⇒ Đây là ô 3 điểm — kết quả thật trên phân phối đích."

**S22 — Confusion matrix.** "Nhìn cụ thể ở ngưỡng 0,705: **TP** là bắt đúng máy hỏng — mục tiêu; **FN** là **bỏ sót** máy hỏng — **tốn kém nhất** vì máy dừng đột ngột; **FP** là báo động giả — chỉ tốn công kiểm tra, rẻ hơn. Recall ~75%, Precision ~81%. ⇒ Vì bỏ sót đắt hơn báo nhầm, ta **có thể hạ ngưỡng để tăng Recall** tuỳ chi phí nhà máy."

**S23 — Bootstrap.** "Con số 0,781 có chắc không? Chỉ **477 máy hỏng** ở B nên F1 có sai số — phải báo khoảng tin cậy. Bốc lại mẫu 2000 lần: **F1 = 0,781, khoảng tin cậy 95% là [0,751; 0,809]**. Các bản đầu bảng chênh rất nhỏ nên coi như ngang nhau — nhóm **không khoe hơn–kém**. Nhưng so trực tiếp từng lần, bản gộp thắng bản đơn **99,8%** số lần → nhỉnh đều nhưng biên độ nhỏ. ⇒ Đúng tinh thần khoa học: **không thổi phồng chênh lệch nhỏ**."

**S24 — Phần 5.1 Insight vận hành.** "Rút ra gì cho nhà máy? Một: **theo dõi độ mòn dao là quan trọng nhất** — vừa báo hỏng tốt vừa can thiệp được bằng thay dao, ưu tiên số một cho đội bảo trì. Hai: **đặt cảnh báo theo ngưỡng vật lý** dùng lại được cả khi đổi máy hay đổi nhà máy, không cần học lại. Ba: cân nhắc bỏ sót và báo động giả để chọn điểm vận hành. ⇒ Đề xuất **2 mức cảnh báo**: mức cao thì dừng máy kiểm tra ngay, mức thấp thì theo dõi thêm và lên lịch bảo trì gần."

**S25 — Phần 5.2 Hạn chế & cải tiến.** "**Hạn chế**: mô hình cây đoán kém ở vùng chưa thấy (2,8% máy B ngoài dải A); giả định *cơ chế hỏng không đổi* chưa kiểm chứng 100% vì không có nhãn B; độ tin IWV giới hạn (ESS 25,5%); và dữ liệu có trần hiệu năng. **Hướng cải tiến**: hiệu chỉnh lại ngưỡng công suất; thêm dữ liệu theo thời gian để bắt xu hướng mòn dao; domain adaptation nâng cao; và thu thập một ít nhãn B để kiểm chứng. ⇒ Nhóm **chủ động nêu hạn chế** thay vì giấu."

**S26 — Quyết định kỹ thuật & lý do.** "*(cue: chỉ bảng)* Slide này để chứng minh **mọi lựa chọn đều có lý do**, sẵn sàng giải thích khi thầy/cô hỏi: dùng F1 vì lớp hiếm; 3 đặc trưng neo ngưỡng vật lý vì hằng số bất biến; mô hình cây vì tín hiệu phi tuyến; không SMOTE để tránh mẫu giả; chọn model bằng IWV để chống rò rỉ; clip trọng số để chặn mẫu cá biệt; chốt Voting vì đơn giản và robust; bootstrap để không thổi phồng. ⇒ Không quyết định nào tuỳ tiện."

**S27 — Kết luận.** "Bốn ý đọng lại: **chìa khoá** là bám quy luật vật lý không đổi thay vì các con số thô đã lệch; **nhờ đó** mô hình học ở A vẫn chạy tốt trên B; **trung thực** vì mọi lựa chọn dùng IWV, không nhìn đáp án; và **kết quả** F1 = 0,781, gấp 3,4 lần baseline. Nhóm em cảm ơn thầy/cô đã lắng nghe và sẵn sàng hỏi–đáp."

**S28 — Q&A.** "Nhóm em xin nhận câu hỏi ạ."

---

## Ma trận phân công Hỏi & Đáp

> Nguyên tắc: ai trình bày phần nào thì chủ trả lời câu hỏi phần đó; các thành viên khác bổ sung. Tham chiếu `NGAN_HANG_QA.md`.

| Chủ đề câu hỏi | Người chủ trả lời | Ý chốt nhanh |
|---|---|---|
| Vì sao không dùng accuracy? | 1 | Lớp hỏng ~8% → accuracy 92% vẫn vô dụng, Recall 0. |
| Covariate shift là gì, sao biết? | 1 | P(x) lệch nhưng tỉ lệ nhãn ổn định (7,4→8,0%). |
| Chống rò rỉ như thế nào? | 2 | Fit scaler/encoder chỉ trên A, gói Pipeline, fit lại mỗi fold. |
| 3 đặc trưng lấy ngưỡng ở đâu? | 2 | Hằng số vật lý cơ chế sinh lỗi AI4I (8,6°/1380/3500–9000W), bất biến A↔B. |
| PSI biên ≈ 0 có đáng tin? | 2 | Bổ sung bằng KS ≈ 0,01, drift-AUC 0,51 và P(hỏng|cờ) 0,84↔0,83. |
| Reweighting sao gain nhỏ? | 3 | Đặc trưng biên đã hấp thụ shift (drift-AUC biên 0,51) → chỉ còn vá nhỏ. |
| IWV hoạt động ra sao? | 3 | Đánh trọng số density-ratio trên A → giả lập B; chọn model/ngưỡng không nhìn nhãn B. |
| Vì sao chọn Voting thay Stacking? | 3 | F1-IWV ngang nhau; Voting đơn giản, khó overfit shift. |
| Vì sao FN đắt hơn FP? | 4 | Bỏ sót → máy dừng đột ngột; báo nhầm chỉ tốn công kiểm tra. |
| 0,781 có chắc không? | 4 | 95% CI [0,751; 0,809]; so cặp bản gộp thắng 99,8% nhưng biên độ nhỏ. |
| Hạn chế lớn nhất? | 4 | Cây không ngoại suy (2,8% B ngoài dải A); thiếu nhãn B để kiểm giả định. |

---

## Ghi chú luyện tập

- **Tổng ~13–14'**: mỗi người bấm giờ phần mình ~3–3,5'. Nếu quá giờ, cắt câu ví von ở S5 và bảng chi tiết ở S18 (chỉ đọc dòng F1).
- **Chuyển người mượt**: người trước kết bằng câu **[chuyển]**, người sau mở bằng "Cảm ơn bạn. Em là Người X…".
- **Nhấn 2 lần** cụm *"chọn bằng IWV — không nhìn nhãn B"* (S16 và S27) vì đây là điểm khác biệt của bài.
- Slide có ảnh (S7, S8, S12, S13, S15, S16, S21, S23) → **chỉ tay vào biểu đồ** khi nói *(cue)*.
