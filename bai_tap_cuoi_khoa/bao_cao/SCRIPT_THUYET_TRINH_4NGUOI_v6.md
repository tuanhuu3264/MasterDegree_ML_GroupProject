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
| **Người 2** | 9–13 | Tiền xử lý · 4 đặc trưng · PSI+KS · drift classifier (Phần 2 + 3.1–3.2) | ~3,5' |
| **Người 3** | 14–19 | Reweighting · IWV · 4 mô hình · so sánh · ensemble (Phần 3.3–3.4 + Phần 4) | ~3,5' |
| **Người 4** | 20–28 | Kết quả · confusion · bootstrap · insight · hạn chế · quyết định · kết luận · Q&A | ~3,5' |

---

## NGƯỜI 1 — Mở đầu & Khám phá dữ liệu (S1–S8, ~3')

**S1 — Title.** **[mở]** "Kính chào thầy/cô và các bạn. Nhóm em trình bày bài toán **dự đoán máy CNC sắp hỏng khi dữ liệu lúc học khác lúc dùng thật**. Kết quả chốt: **F1 = 0,783** trên nhà máy B, gấp **3,4 lần** mô hình ban đầu, và notebook chạy full **không lỗi**. Bài gồm 4 phần do 4 thành viên trình bày."

**S2 — Nội dung.** "Mạch trình bày 4 khối: em — bài toán & khám phá dữ liệu; Người 2 — tiền xử lý, tạo đặc trưng & phát hiện shift; Người 3 — xử lý shift & xây mô hình; Người 4 — kết quả, độ tin cậy & kết luận. *(cue: chỉ bảng)* Hai khối nặng điểm nhất là **xử lý shift (2đ)** và **kết quả thật (3đ)**."

**S3 — Divider Phần 1.** "Em bắt đầu Phần 1 — Mở đầu và khám phá dữ liệu."

**S4 — Bài toán.** "Nhà máy có đội máy phay CNC; ta muốn đoán **máy nào sẽ hỏng ở ca kế tiếp** để sửa trước, tức chuyển từ bảo trì bị động sang chủ động. Dữ liệu gồm 5 số đo cảm biến và 2 nhãn phân loại. Có **hai thách thức cốt lõi**: một là máy hỏng chỉ **~8%** — rất hiếm, nên **accuracy vô nghĩa**, phải dùng F1/AUC-PR; hai là học ở nhà máy A nhưng chạy ở nhà máy B nóng hơn, nhanh hơn — đó là **distribution shift**. ⇒ Hai thách thức này định hình mọi quyết định phía sau."

**S5 — Vì sao khó.** "Distribution shift nghĩa là phân phối đầu vào ở B lệch khỏi A — ví như học lái ở đường quê rồi phải chạy trong phố. **May mắn** là *nguyên nhân* gây hỏng vẫn theo cùng quy luật vật lý ở cả A và B; chỉ có *các con số* bị lệch. Cái khó nhất: **bị chấm trên B nhưng không được xem đáp án của B** — xem là rò rỉ. ⇒ Chiến lược 3 bước: **đo** mức lệch, **tạo đặc trưng miễn nhiễm** lệch, rồi **tinh chỉnh** thêm."

**S6 — Phần 1.1 Máy hỏng hiếm cỡ nào.** "Nhà máy A có 7,36% hỏng, B có 7,95% — **tỉ lệ hỏng gần như không đổi**. Đây là chi tiết quan trọng: cái lệch nằm ở **số đo đầu vào**, không phải ở nhãn — nên đây là *covariate shift*, hợp với importance reweighting. Dữ liệu sạch: 0 thiếu, 0 trùng. ⇒ Vì hỏng quá hiếm nên nhóm chốt dùng **F1** ngay từ đầu."

**S7 — Phần 1.2 Hai nhà máy lệch thế nào.** "Đo bằng số: từ A sang B, **nhiệt độ môi trường +2,5°, nhiệt độ máy +1,9°, tốc độ +70 vòng/phút**, lực xoắn thấp hơn ~8,5%, riêng **độ mòn dao gần như không đổi**. *(cue: chỉ histogram)* Nhìn biểu đồ, hai màu A–B **không trùng nhau** — đó là shift thấy tận mắt. ⇒ Độ mòn dao là chỗ **neo tin cậy** vì nó ổn định qua hai nhà máy."

**S8 — Phần 1.3–1.4 Dấu hiệu hỏng & vùng lạ.** *(cue: biểu đồ phân bố bên TRÁI, ma trận tương quan bên PHẢI)* "Nhìn biểu đồ phân bố theo nhãn bên trái: **độ mòn dao tách rõ nhất** — máy hỏng mòn ~177 phút so với máy lành ~123. Các biến khác có tương quan tuyến tính gần như bằng 0 (xem hàng `hong_hoc` trên ma trận tương quan bên phải), nhưng **không phải vô dụng**: **tốc độ** máy hỏng dồn về đuôi **THẤP** (quay chậm → tản nhiệt kém), còn **mômen** dồn về **CẢ HAI ĐẦU** (quá tải hoặc thiếu tải) — nên quan hệ là phi tuyến. Về phân loại: ca làm việc không lệch, nhưng loại sản phẩm **có lệch**; và **2,8% máy B nằm ngoài dải A** — nhóm ghi vào Hạn chế vì mô hình cây dễ sai ở vùng lạ. ⇒ Tín hiệu hỏng **phức tạp theo tổ hợp** → cần mô hình mạnh và đặc trưng khéo. **[chuyển]** Mời Người 2 trình bày cách xử lý dữ liệu và tạo đặc trưng."

---

## NGƯỜI 2 — Tiền xử lý, Đặc trưng & Phát hiện shift (S9–S13, ~3,5')

**S9 — Divider Phần 2.** **[mở]** "Cảm ơn bạn. Em là Người 2, trình bày tiền xử lý, bốn đặc trưng vật lý, và phần đo shift."

**S10 — Phần 2.1 Chuẩn bị dữ liệu.** "Số đo được đưa về cùng thang cho mô hình tuyến tính; mô hình cây thì không cần. **Quy tắc vàng chống rò rỉ**: chỉ học cách chuẩn hoá **trên A**, rồi áp cho cả A và B — không bao giờ nhìn lén B. Nhãn chữ đổi thành số: loại sản phẩm L<M<H giữ thứ tự nên dùng Ordinal; ca làm việc không thứ tự nên One-Hot. Lớp hiếm xử bằng **phạt nặng khi bỏ sót** (class_weight ≈ 12,6), **không dùng SMOTE**. Tất cả gói trong Pipeline, fit lại đúng trong từng fold. ⇒ Nếu nhìn lén B, điểm cao trên giấy nhưng triển khai thật sẽ sụp — đây là điều đề nhấn mạnh nhất ở Phần 2."

**S11 — Phần 2.2 Bốn đặc trưng vật lý.** "Đây là **ý tưởng cốt lõi cả bài**. Nhóm tạo 4 đặc trưng đo *'máy còn cách ngưỡng hỏng bao xa'*: **nguy_tan_nhiet** (tản nhiệt kém), **lech_cong_suat** (quá/thiếu công suất), **bien_overstrain** (quá tải theo loại sản phẩm), và **mon_twf** (mòn dao vượt ngưỡng thay dao). Điểm hay: các ngưỡng — 8,6 độ, 1380 vòng/phút, dải 2600–11500W, mòn 244 phút — là **hằng số cơ chế của máy**, nhóm **khôi phục từ luật sinh nhãn trên A** — tức quét thử ngưỡng đến đúng chỗ *tỉ lệ hỏng vọt lên*, tuyệt đối không nhìn B — rồi kiểm chứng chúng **không đổi giữa A và B**, nên 4 đặc trưng **miễn nhiễm với shift**. *(nếu bị hỏi chi tiết từng con số → xem mục "Vì sao chọn các ngưỡng đó" ở cuối script)* Kiểm chứng bằng số theo yêu cầu đề: chỉ thêm 4 đặc trưng, mô hình đơn giản mạnh gần **gấp ba** — AUC-PR từ 0,22 lên 0,65. ⇒ Cả bốn tương quan với hỏng mạnh, riêng mon_twf (0,43) hơn cả độ mòn thô, chứng tỏ không phải thêm cho có."

**S12 — Phần 3.1 PSI + KS.** "Bước đầu của xử lý shift là **đo** mức lệch từng biến bằng hai thước đo: **PSI** và **KS**. *(cue: chỉ bảng)* Hai biến nhiệt độ lệch mạnh — PSI 1,08 và 0,55, KS 0,43 và 0,31; tốc độ và lực xoắn lệch nhẹ; còn **4 đặc trưng vật lý PSI ≈ 0 và KS ≤ 0,06** — gần như không lệch, dù chúng được dựng từ chính các biến nhiệt độ đang lệch mạnh. **Lưu ý trung thực** (điểm cộng): ba đặc trưng hinge phần lớn bằng 0 nên PSI bị bão hoà về 0; nên bằng chứng bất biến **chính** là drift-AUC 0,53 ở slide sau, chứ không chỉ dựa PSI. ⇒ Shift dồn ở biến thô, đặc trưng biên đã hấp thụ nó."

**S13 — Phần 3.2 Drift Classifier.** "Cách xác định **shift nằm ở đâu**: huấn luyện một mô hình đoán *'máy này thuộc A hay B'* chỉ từ số đo — đoán càng dễ thì hai nhà máy càng khác. Dùng **tất cả số đo → AUC 0,82** (lệch mạnh); nhưng chỉ dùng **4 đặc trưng vật lý → AUC 0,53**, tức gần như tung đồng xu. *(cue: chỉ biểu đồ cột importance bên dưới)* **Feature importance** của mô hình đoán A/B — vẽ thành biểu đồ cột — cho thấy hai cột đỏ *nhiệt độ môi trường (38%)* và *nhiệt độ máy (20%)* vượt hẳn các biến còn lại, cộng lại **~58%** — đây chính là **bằng chứng trực quan** rằng hai biến nhiệt độ là **thủ phạm chính** gây shift. Thêm bằng chứng: khi máy vượt ngưỡng nguy hiểm thì tỉ lệ hỏng **giống nhau** ở A và B (0,84 so với 0,82). ⇒ Ba lát cắt — PSI, drift-AUC, importance — cùng một kết luận. **[chuyển]** Mời Người 3 trình bày cách xử lý shift và xây mô hình."

---

## NGƯỜI 3 — Xử lý shift & Xây mô hình (S14–S19, ~3,5')

**S14 — Divider Phần 3.** **[mở]** "Cảm ơn bạn. Em là Người 3, trình bày xử lý shift và bốn mô hình."

**S15 — Phần 3.3 Reweighting.** "Kỹ thuật xử lý lệch thứ nhất — **Importance Reweighting**: máy A nào **trông giống B** thì cho *'điểm chú ý'* cao hơn khi học, để mô hình học nghiêng về B. Điểm chú ý = mức giống B chia mức giống A, lấy từ drift classifier. Phải **chặn điểm quá lớn** (giới hạn 10) để vài máy lạ không chi phối toàn bộ. Kết quả trước–sau: gần như đứng yên — F1 giữ 0,783, AUC-PR 0,675 về 0,671. ⇒ **Đứng yên là tin tốt**: bốn đặc trưng vật lý đã lo gần hết việc chống lệch, kỹ thuật này chỉ vá phần nhỏ — làm đúng đặc trưng thì đỡ phải bù bằng thống kê."

**S16 — Phần 3.4 IWV & ngưỡng.** "Kỹ thuật thứ hai giải **nghịch lý chấm điểm**: bị chấm trên B nhưng cấm xem đáp án B — vậy chọn mô hình bằng gì? Câu trả lời là **IWV — Importance-Weighted Validation**: dùng dữ liệu A nhưng đánh trọng số cho phần *'giống B'*, tạo một bộ chấm thử **giả lập B** mà không cần nhãn B. Nhờ đó thử–sai bao nhiêu cũng không gian lận; nhãn B chỉ dùng **một lần cuối** để báo cáo. Ta cũng chỉnh **ngưỡng báo hỏng** cho F1 cao nhất thay vì để mặc định 0,5. *(cue: chỉ đồ thị)* Đường chấm-thử-giả-lập bám sát đường kết-quả-thật-trên-B → harness đáng tin. ⇒ Đây là chốt kỷ luật của cả bài: **chọn mọi thứ bằng IWV, không nhìn nhãn B**."

**S17 — Phần 4.1 Thử 4 mô hình.** "Nhóm thử **4 mô hình thuộc 3 trường phái** để lát gộp cho đa dạng: Logistic Regression làm mốc; Random Forest và ExtraTrees kiểu *nhiều cây bỏ phiếu*, ổn định; XGBoost kiểu *nhiều cây sửa lỗi nối tiếp*, mạnh nhưng dễ học thuộc A. Dò siêu tham số **tự động bằng RandomizedSearchCV** với **StratifiedKFold 5** giữ đúng tỉ lệ hỏng. Chấm bằng F1/AUC-PR, chọn model bằng IWV. ⇒ Đủ yêu cầu đề: **≥3 mô hình + tuning + K-Fold**."

**S18 — Phần 4.2 Bảng so sánh.** "*(cue: chỉ bảng)* Đọc theo cột **F1** — con số so sánh chính theo đề. Từ mô hình thô **0,231**, thêm 4 đặc trưng vọt lên 0,716, chuyển sang cây đạt 0,783; reweighting và chỉnh ngưỡng giữ ổn định; **bản gộp cuối chốt 0,783**. Cột *báo đúng* là Precision, *bắt được* là Recall; **AUC-PR** là diện tích dưới đường Precision–Recall — thước đo xếp hạng dành cho lớp hiếm (đường 'đoán bừa' chỉ ~0,08 nên 0,67 là rất tốt), còn **AUC-ROC** là xác suất model chấm một máy hỏng cao hơn một máy lành (0,5 = ngẫu nhiên, 1 = hoàn hảo). ⇒ Hành trình **0,231 → 0,783 = gấp 3,4 lần**; từ v2 các bản hội tụ 0,783 — dấu hiệu đã **chạm trần dữ liệu** (nói rõ ở phần hạn chế)."

**S19 — Phần 4.3 Ensemble.** "Ý tưởng gộp: mỗi mô hình sai ở chỗ khác nhau, gộp lại thì bù trừ, ổn định hơn. Hai cách: **Bỏ phiếu** (trung bình có trọng số RF 25% + ExtraTrees 25% + XGBoost 50%, trọng số dò bằng IWV) và **Trộn** (một mô hình nhỏ học cách trộn 4 mô hình con). Chọn cách tốt hơn **bằng IWV** → hai bản ngang điểm, chốt **Bỏ phiếu** vì đơn giản, khó sai, khó overfit shift. ⇒ Bản chốt v6 là **Voting RF + ExtraTrees + XGB**. **[chuyển]** Mời Người 4 trình bày kết quả cuối và kết luận."

---

## NGƯỜI 4 — Kết quả, Độ tin cậy & Kết luận (S20–S28, ~3,5')

**S20 — Divider Phần 4.** **[mở]** "Cảm ơn bạn. Em là Người 4, trình bày kết quả cuối, độ tin cậy và phần báo cáo."

**S21 — Kết quả cuối trên B (3đ).** "Trên nhà máy B — tập mô hình **chưa từng thấy**: **F1 = 0,783**, bắt được **~75%** máy hỏng (Recall), và **4 trên 5** cảnh báo là đúng (Precision ~82%). *(cue: chỉ PR-curve)* Đường PR của bản chốt cao hơn hẳn đường *đoán bừa*. ⇒ Đây là ô 3 điểm — kết quả thật trên phân phối đích."

**S22 — Confusion matrix.** "Nhìn cụ thể ở ngưỡng 0,585: **TP** là bắt đúng máy hỏng — mục tiêu (358 máy); **FN** là **bỏ sót** máy hỏng — **tốn kém nhất** vì máy dừng đột ngột (119); **FP** là báo động giả — chỉ tốn công kiểm tra, rẻ hơn (80). Recall ~75%, Precision ~82%. ⇒ Vì bỏ sót đắt hơn báo nhầm, ta **có thể hạ ngưỡng để tăng Recall** tuỳ chi phí nhà máy."

**S23 — Bootstrap.** "Con số 0,783 có chắc không? Chỉ **477 máy hỏng** ở B nên F1 có sai số — phải báo khoảng tin cậy. Bốc lại mẫu 2000 lần: **F1 = 0,783, khoảng tin cậy 95% là [0,753; 0,811]**. Các bản đầu bảng chênh rất nhỏ nên coi như ngang nhau — nhóm **không khoe hơn–kém**. Nhưng so trực tiếp từng lần, bản gộp thắng bản đơn **100%** số lần (chênh +0,015) → nhỉnh đều nhưng biên độ nhỏ. ⇒ Đúng tinh thần khoa học: **không thổi phồng chênh lệch nhỏ**."

**S24 — Phần 5.1 Insight vận hành.** "Rút ra gì cho nhà máy? Một: **theo dõi độ mòn dao là quan trọng nhất** — vừa báo hỏng tốt vừa can thiệp được bằng thay dao, ưu tiên số một cho đội bảo trì. Hai: **đặt cảnh báo theo ngưỡng vật lý** dùng lại được cả khi đổi máy hay đổi nhà máy, không cần học lại. Ba: cân nhắc bỏ sót và báo động giả để chọn điểm vận hành. ⇒ Đề xuất **2 mức cảnh báo**: mức cao thì dừng máy kiểm tra ngay, mức thấp thì theo dõi thêm và lên lịch bảo trì gần."

**S25 — Phần 5.2 Hạn chế & cải tiến.** "**Hạn chế**: mô hình cây đoán kém ở vùng chưa thấy (2,8% máy B ngoài dải A); giả định *cơ chế hỏng không đổi* chưa kiểm chứng 100% vì không có nhãn B; độ tin IWV giới hạn (**ESS 24,2%** — *Effective Sample Size*, tức "số mẫu hiệu dụng" sau khi đánh trọng số chỉ còn ~24% của 14.000, nên các bản đầu bảng coi như ngang nhau); và **~25% ca hỏng là nhiễu ngẫu nhiên** — không khớp luật nào — nên **trần F1 ≈ 0,78 đã được định lượng** (Phụ lục A của notebook). **Hướng cải tiến**: mục số một — khôi phục luật sinh nhãn từ A — nhóm **đã thực hiện**: precision luật từ 0,26 lên 0,81, F1 từ 0,781 lên 0,783; còn lại: thêm dữ liệu theo thời gian để bắt xu hướng mòn dao; domain adaptation nâng cao; và thu thập một ít nhãn B để kiểm chứng. ⇒ Nhóm **chủ động nêu hạn chế** thay vì giấu — và chứng minh 'sao không cao hơn nữa': không phải model yếu, mà dữ liệu chỉ cho phép đến đó."

**S26 — Quyết định kỹ thuật & lý do.** "*(cue: chỉ bảng)* Slide này để chứng minh **mọi lựa chọn đều có lý do**, sẵn sàng giải thích khi thầy/cô hỏi: dùng F1 vì lớp hiếm; 4 đặc trưng neo ngưỡng cơ chế khôi phục từ A vì hằng số bất biến; mô hình cây vì tín hiệu phi tuyến; không SMOTE để tránh mẫu giả; chọn model bằng IWV để chống rò rỉ; clip trọng số để chặn mẫu cá biệt; chốt Voting vì đơn giản và robust; bootstrap để không thổi phồng. ⇒ Không quyết định nào tuỳ tiện."

**S27 — Kết luận.** "Bốn ý đọng lại: **chìa khoá** là bám quy luật vật lý không đổi thay vì các con số thô đã lệch; **nhờ đó** mô hình học ở A vẫn chạy tốt trên B; **trung thực** vì mọi lựa chọn dùng IWV, không nhìn đáp án; và **kết quả** F1 = 0,783, gấp 3,4 lần baseline — chạm trần mà dữ liệu cho phép. Nhóm em cảm ơn thầy/cô đã lắng nghe và sẵn sàng hỏi–đáp."

**S28 — Q&A.** "Nhóm em xin nhận câu hỏi ạ."

---

## Ma trận phân công Hỏi & Đáp

> Nguyên tắc: ai trình bày phần nào thì chủ trả lời câu hỏi phần đó; các thành viên khác bổ sung. Tham chiếu `NGAN_HANG_QA.md`.

| Chủ đề câu hỏi | Người chủ trả lời | Ý chốt nhanh |
|---|---|---|
| Vì sao không dùng accuracy? | 1 | Lớp hỏng ~8% → accuracy 92% vẫn vô dụng, Recall 0. |
| Covariate shift là gì, sao biết? | 1 | P(x) lệch nhưng tỉ lệ nhãn ổn định (7,4→8,0%). |
| Chống rò rỉ như thế nào? | 2 | Fit scaler/encoder chỉ trên A, gói Pipeline, fit lại mỗi fold. |
| 4 đặc trưng lấy ngưỡng ở đâu? *(→ mục chi tiết cuối script)* | 2 | Quét ngưỡng trên A tìm chỗ tỉ lệ hỏng vọt lên (8,6°/1380 · 2600–11500W · OSF theo loại 12800/13900/14500 · mòn 244); precision luật 0,81 ở A ↔ 0,82 ở B → biên vật lý bất biến, không tinh chỉnh trên test. |
| PSI biên ≈ 0 có đáng tin? | 2 | Bổ sung bằng KS ≤ 0,06, drift-AUC 0,53 và P(hỏng|cờ) ANY 0,81↔0,82. |
| Reweighting sao gain nhỏ? | 3 | Đặc trưng biên đã hấp thụ shift (drift-AUC biên 0,53) → chỉ còn vá nhỏ. |
| IWV hoạt động ra sao? | 3 | Đánh trọng số density-ratio trên A → giả lập B; chọn model/ngưỡng không nhìn nhãn B. |
| Vì sao chọn Voting thay Stacking? | 3 | F1-IWV ngang nhau; Voting đơn giản, khó overfit shift. |
| Vì sao FN đắt hơn FP? | 4 | Bỏ sót → máy dừng đột ngột; báo nhầm chỉ tốn công kiểm tra. |
| 0,783 có chắc không? | 4 | 95% CI [0,753; 0,811]; so cặp bản gộp thắng 100% (chênh +0,015) nhưng biên độ nhỏ. |
| Sao không cao hơn nữa (≥0,80)? | 4 | ~25% ca hỏng KHÔNG khớp luật nào = nhiễu ngẫu nhiên (kiểu RNF của AI4I) → trần F1 ≈ 0,78; mọi bản v2–v6 hội tụ 0,783; oracle biết trước B cũng chỉ ~0,78; ≥0,80 chỉ có thể bằng leakage. |
| Hạn chế lớn nhất? | 4 | Cây không ngoại suy (2,8% B ngoài dải A); thiếu nhãn B để kiểm giả định. |

---

## Vì sao chọn các ngưỡng đó cho 4 đặc trưng? *(câu hỏi "tủ" — trả lời chi tiết)*

> Đây là câu giám khảo hay hỏi nhất: *"Những con số 2600, 11500, 12800, 244… ở đâu ra? Có phải tự bịa / tinh chỉnh trên tập test không?"*

**Cách làm chung — "khôi phục ngưỡng của luật sinh nhãn", CHỈ dùng Dây chuyền A:** dữ liệu kiểu AI4I được sinh ra từ **các luật có ngưỡng cố định**. Với mỗi cơ chế hỏng, nhóm **quét thử nhiều ngưỡng trên A** và tìm đúng chỗ **tỉ lệ hỏng vọt lên** — đó chính là **biên mà luật dùng để sinh nhãn**. Tuyệt đối **không nhìn nhãn B**; sau đó kiểm chứng biên này **giữ nguyên độ chính xác trên B** (precision luật gộp **0,81 ở A ↔ 0,82 ở B**) → chứng tỏ là **biên vật lý bất biến**, không phải tinh chỉnh trên tập test.

| Đặc trưng | Ngưỡng chốt | Bằng chứng trên A → vì sao chọn |
|---|---|---|
| **HDF** `nguy_tan_nhiet` | ΔT < **8,6 K** *và* tốc độ < **1380 v/ph** | **Giữ nguyên hằng số AI4I** vì đã khớp sẵn: tại đây P(hỏng) = **0,84**. Nới lỏng (ΔT<9,0 hoặc rpm<1450) tụt còn ~0,45–0,55 → 8,6/1380 đúng là điểm tốt nhất, không cần đổi. |
| **PWF** `lech_cong_suat` | công suất ngoài dải **[2600 ; 11500] W** | Máy **lành** chạy công suất trong khoảng **~2960–10560 W** (phân vị 1–99). Dải cũ **[3500 ; 9000]** cắt vào **giữa vùng lành** → 83% cờ là báo động giả (P chỉ **0,17**). Nới dải ra **ôm vừa khít vùng lành** → chỉ bắt máy thật sự lệch công suất, P(hỏng) = **0,79**. |
| **OSF** `bien_overstrain` | mòn×mômen > **{L: 12800 · M: 13900 · H: 14500}** | Quét theo **từng loại sản phẩm**, tỉ lệ hỏng vọt cao đúng tại các mốc này: L→**0,88**, M→**0,94**, H→**0,93**. Ngưỡng **tăng dần theo độ cứng L < M < H** — sản phẩm cứng chịu tải lớn hơn mới hỏng (đúng vật lý). Dải cũ {11000/12000/13000} đặt quá thấp → P chỉ ~0,3–0,4. |
| **TWF** `mon_twf` | mòn dao > **244 phút** | Tỉ lệ hỏng **nhảy bậc** từ 0,57 (mốc 240) lên **0,80** (mốc 244); dao **lành** mòn tối đa chỉ tới **253** → vùng 244–253 là "dao sắp phải thay". Đây là luật TWF mà bản gốc AI4I **bỏ sót**, nhóm bổ sung. |

**Câu chốt khi bị hỏi:** *"Ngưỡng không phải con số bịa hay tinh chỉnh trên tập test — chúng là **biên vật lý của luật sinh nhãn**, khôi phục bằng cách tìm chỗ tỉ lệ hỏng vọt lên **chỉ trên Dây chuyền A**, và đã kiểm chứng **giữ nguyên độ chính xác khi sang B**. Chính vì thế 4 đặc trưng mới miễn nhiễm với shift."*

---

## Bảng thuật ngữ — giải thích dễ hiểu mọi từ chuyên môn trên slide

> Dùng để **trả lời khi giám khảo hỏi "… là gì?"**. Mỗi từ được giải thích bằng **một câu đời thường**, kèm ví dụ. Cột cuối ghi từ đó nằm ở slide nào.

### A. Các cách chấm điểm mô hình
| Từ trên slide | Nói cho dễ hiểu |
|---|---|
| **Accuracy** (tỉ lệ đoán đúng) | Đoán đúng bao nhiêu phần trăm tổng số máy. **Không dùng** vì máy hỏng quá hiếm: cứ nói "máy nào cũng không hỏng" là đã đúng 92% rồi, nhưng bỏ sót sạch máy hỏng → vô dụng. *(S4, S6)* |
| **Precision — "Báo đúng"** | Cứ 10 lần máy **kêu "sắp hỏng"** thì bao nhiêu lần **đúng là hỏng thật**. Cao = ít báo động giả. *(S18, S21, S22)* |
| **Recall — "Bắt được"** | Trong tất cả máy **thật sự hỏng**, model **tìm ra được** bao nhiêu phần trăm. Cao = ít bỏ sót. *(S18, S21, S22)* |
| **F1** | Gộp "báo đúng" và "bắt được" thành **một điểm duy nhất**, chỉ cao khi **cả hai cùng cao**. Đây là điểm chính để chấm bài. *(S1, S4, S6, S18)* |
| **AUC-PR** | Một điểm từ 0 đến 1 cho biết model **đẩy máy hỏng lên đầu danh sách nghi ngờ** tốt tới đâu. Đoán bừa chỉ được ~0,08 (bằng tỉ lệ máy hỏng), nên 0,67 là khá cao. Hợp với bài "máy hỏng hiếm". *(S4, S11, S17, S18)* |
| **AUC-ROC** | Bốc ngẫu nhiên 1 máy hỏng và 1 máy lành, đây là **xác suất model chấm máy hỏng điểm cao hơn**. 0,5 = đoán mò, 1 = phân biệt hoàn hảo. *(S18)* |
| **PR-curve** (đường Precision–Recall) | Khi vặn cảnh báo từ "chặt" sang "lỏng", ta được một đường cho thấy đánh đổi giữa báo-đúng và bắt-được. Đường càng cong lên phía trên càng tốt. *(S17, S21)* |

### B. Phát hiện dữ liệu bị lệch
| Từ trên slide | Nói cho dễ hiểu |
|---|---|
| **Distribution shift** (dữ liệu bị lệch) | Dữ liệu lúc **học** (nhà máy A) khác dữ liệu lúc **dùng thật** (nhà máy B). Giống học lái ở đường quê rồi phải chạy trong phố. *(S1, S4, S5)* |
| **Covariate shift** (lệch "sạch") | Chỉ **các con số đầu vào** (nhiệt độ, tốc độ) bị lệch, còn **quy luật gây hỏng vẫn y nguyên**. Nhờ vậy mới chữa được bằng cách đánh trọng số. *(S6)* |
| **PSI** | Một con số đo **một biến lệch mạnh cỡ nào** giữa A và B. Dưới 0,1 = không lệch; 0,1–0,25 = lệch nhẹ; trên 0,25 = lệch mạnh. *(S9, S12)* |
| **KS** | Cũng đo độ lệch của một biến, bằng **khoảng cách lớn nhất giữa hai đường phân bố** A và B. Số càng lớn càng lệch. *(S9, S12)* |
| **Drift classifier** (mô hình đoán A/B) | Huấn luyện một model chỉ để đoán "mẫu này của nhà máy A hay B". Nếu nó đoán **quá dễ** → hai nhà máy khác nhau nhiều. Điểm của nó (drift-AUC): 0,5 = không phân biệt nổi (tốt, ít lệch), 1 = khác hẳn. *(S5, S9, S12, S13)* |
| **Feature importance** (mức quan trọng của biến) | Cho biết model **dựa vào biến nào nhiều nhất**. Ở đây 2 biến nhiệt độ chiếm ~58% → chúng là thủ phạm chính gây lệch. *(S13)* |

### C. Xử lý lệch & chọn mô hình không "gian lận"
| Từ trên slide | Nói cho dễ hiểu |
|---|---|
| **Leakage — "rò rỉ"** | Lỡ **nhìn trộm dữ liệu nhà máy B** khi đang học → điểm đẹp trên giấy nhưng dùng thật thì hỏng. Phải tránh tuyệt đối. *(S5, S10, S26)* |
| **Importance Reweighting** (đánh trọng số) | Máy nào ở A mà **trông giống máy B** thì cho **"điểm chú ý" cao hơn** khi học, để model học nghiêng về kiểu B. *(S5, S6, S15)* |
| **Density-ratio** | Chính "điểm chú ý" đó, tính bằng **mức-giống-B chia mức-giống-A**. *(S15)* |
| **Threshold — "ngưỡng báo hỏng"** | Máy phải "đạt bao nhiêu điểm nghi ngờ" thì mới **bị kêu là hỏng**. Mặc định 0,5 không hợp với lớp hiếm; nhóm chỉnh xuống **0,585** cho F1 cao nhất. *(S5, S16, S22)* |
| **IWV** | Cách **tự chấm điểm cho mình như thể đang đứng ở nhà máy B**, nhưng chỉ dùng dữ liệu A (đã đánh trọng số). Nhờ đó chọn model và ngưỡng mà **không cần xem đáp án của B**. *(S14, S16, S17, S19, S26)* |
| **ESS** ("số mẫu hiệu dụng") | Sau khi đánh trọng số, vài mẫu "nặng ký" lấn át, nên **lượng dữ liệu thật sự có ích chỉ còn ~24%** của 14.000. Vì ít nên các bản điểm sát nhau coi như ngang nhau. *(S16, S25)* |
| **Harness** | "Bộ khung tự chấm điểm" (chính là IWV) nhóm tự dựng để thử nghiệm như đang ở B. *(S16)* |

### D. Các mô hình & cách huấn luyện
| Từ trên slide | Nói cho dễ hiểu |
|---|---|
| **Logistic Regression** | Mô hình đơn giản nhất, dùng làm **mốc** để so sánh. *(S17)* |
| **Random Forest / ExtraTrees** | "**Rừng nhiều cây quyết định cùng bỏ phiếu**" → kết quả ổn định, ít dao động. *(S17)* |
| **XGBoost** | "Nhiều cây **học nối tiếp, cây sau sửa lỗi cây trước**" → mạnh nhưng dễ **học thuộc lòng** nhà máy A. *(S17)* |
| **Variance** (độ dao động) | "Variance thấp" nghĩa là **kết quả ít đổi** giữa các lần huấn luyện → mang sang nhà máy B an toàn hơn. *(S17)* |
| **Overfit** (học thuộc lòng) | Model học quá khít dữ liệu A đến mức **gặp B lạ là sai**. *(S19, S26)* |
| **class_weight / scale_pos_weight** | **Phạt nặng khi bỏ sót máy hỏng** (nặng gấp ~12,6 lần máy lành) để model chịu khó bắt lớp hiếm — thay cho việc chế dữ liệu giả. *(S10, S26)* |
| **SMOTE** | Kỹ thuật **tự chế thêm máy-hỏng giả** cho bớt hiếm. Nhóm **không dùng** vì dễ tạo ra máy "không có thật" khi dữ liệu đang lệch. *(S10, S26)* |
| **Ordinal / One-Hot** | Hai cách **đổi chữ thành số** cho máy hiểu: **Ordinal** khi có thứ tự (L < M < H); **One-Hot** khi không thứ tự (ca Sáng/Chiều/Đêm — tách mỗi ca một cột riêng). *(S10)* |
| **Pipeline** | **Gói tất cả các bước** (chuẩn hoá, mã hoá, model) thành một khối, huấn luyện lại trong từng lần kiểm tra → **không bị rò rỉ**. *(S10)* |
| **StratifiedKFold / K-Fold** (kiểm tra chéo) | **Chia dữ liệu thành 5 phần**, lần lượt lấy 4 phần học – 1 phần kiểm tra, để đánh giá cho chắc. "Stratified" = mỗi phần giữ đúng tỉ lệ ~8% máy hỏng. *(S10, S17)* |
| **RandomizedSearchCV / siêu tham số** | **Dò tự động** các "nút vặn" của model (số cây, độ sâu cây…) để tìm bộ cài đặt tốt nhất. *(S17)* |
| **Ensemble / Voting / Stacking** | **Gộp nhiều model cho chắc ăn**. **Voting** = lấy **trung bình có trọng số** ý kiến các model. **Stacking** = **một model nhỏ học cách trộn** các ý kiến đó. *(S5, S19)* |

### E. Đánh giá độ tin cậy
| Từ trên slide | Nói cho dễ hiểu |
|---|---|
| **Bootstrap** | **Bốc lại mẫu (có hoàn lại) 2000 lần**, mỗi lần tính F1, để xem con số F1 **dao động cỡ nào** → biết nó chắc hay không. *(S20, S23)* |
| **95% CI** (khoảng tin cậy 95%) | Khoảng **[0,753 ; 0,811]** mà F1 "thật" nhiều khả năng (95%) nằm trong đó. *(S23)* |
| **Confusion matrix** (ma trận nhầm lẫn) | Bảng 2×2 đếm 4 tình huống: **TP** bắt đúng máy hỏng · **TN** đúng máy lành · **FP** báo động giả · **FN** bỏ sót máy hỏng. *(S20, S22)* |
| **Baseline** (mốc ban đầu) | Model thô nhất (F1 chỉ 0,231) để thấy đã cải thiện **gấp 3,4 lần**. *(S1, S27)* |

### F. Đặc trưng vật lý
| Từ trên slide | Nói cho dễ hiểu |
|---|---|
| **HDF / PWF / OSF / TWF** | 4 kiểu hỏng máy (theo chuẩn dữ liệu AI4I): **tản nhiệt kém · quá/thiếu công suất · quá tải · mòn dao**. *(S11)* |
| **hinge — "bản lề"** | Hàm `max(giá trị, 0)` chỉ **"bật" lên khi máy vượt ngưỡng nguy hiểm**, còn bình thường thì bằng 0 → đo "còn cách vùng hỏng bao xa". *(S11)* |
| **ΔT và P** | ΔT = nhiệt độ máy trừ nhiệt độ môi trường. P (công suất cơ) = mômen × tốc độ × 2π/60. *(S11)* |
| **Domain adaptation / CORAL / adversarial** | Các **kỹ thuật nâng cao** để kéo dữ liệu A và B "khớp" nhau hơn — mới chỉ nêu ở phần **hướng cải tiến**, chưa làm. *(S25)* |

---

## Ghi chú luyện tập

- **Tổng ~13–14'**: mỗi người bấm giờ phần mình ~3–3,5'. Nếu quá giờ, cắt câu ví von ở S5 và bảng chi tiết ở S18 (chỉ đọc dòng F1).
- **Chuyển người mượt**: người trước kết bằng câu **[chuyển]**, người sau mở bằng "Cảm ơn bạn. Em là Người X…".
- **Nhấn 2 lần** cụm *"chọn bằng IWV — không nhìn nhãn B"* (S16 và S27) vì đây là điểm khác biệt của bài.
- Slide có ảnh (S7, S8, S12, S13, S15, S16, S21, S23) → **chỉ tay vào biểu đồ** khi nói *(cue)*.
