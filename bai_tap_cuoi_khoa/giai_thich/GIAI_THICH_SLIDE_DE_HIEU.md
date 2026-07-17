# Giải thích từng slide — kiểu dễ hiểu cho người mới

> Đọc file này để **hiểu mỗi slide đang nói gì** và **nên nói gì khi thuyết trình**, kể cả khi bạn ít kiến thức máy học.
> Deck: `SLIDE_THUYET_TRINH_v6.pptx` (28 slide) · Lời thoại chi tiết: `SCRIPT_THUYET_TRINH_4NGUOI_v6.md`.
> Mỗi slide: 🖼️ **trên slide có gì** · 🗣️ **nói nôm na** · ⭐ **con số/ý phải nhớ**.

## Cả bài nói gì? (đọc 30 giây)

Ta dạy máy tính **đoán trước máy CNC nào sắp hỏng** để sửa trước. Cái khó: **học ở nhà máy cũ (A) nhưng phải đoán đúng ở nhà máy mới (B)** — B nóng hơn, chạy nhanh hơn (giống *học lái xe ở quê rồi phải chạy trong phố*). Và máy hỏng **rất hiếm (~8%)**.

Chìa khoá: thay vì học các con số thô (đã lệch giữa A và B), ta tạo **4 "đèn cảnh báo"** đo "máy còn cách vạch hỏng bao xa". Vì vạch hỏng là **quy luật vật lý cố định**, đèn học ở A vẫn đúng ở B. Kết quả: **F1 = 0,783** (gấp 3,4 lần cách làm ngây thơ).

*(F1 = một kiểu điểm chấm, càng gần 1 càng tốt. Bài dùng 4 người trình bày, mỗi người một phần.)*

---

## PHẦN 1 — Bài toán & khám phá dữ liệu (Người 1, slide 1–8)

### Slide 1 — Trang bìa
🖼️ Tên đề tài + tên 4 thành viên + giảng viên hướng dẫn.
🗣️ Chào, giới thiệu tên đề tài và nhóm. Nói ngay kết quả: "F1 = 0,783, gấp 3,4 lần mô hình ban đầu, notebook chạy không lỗi."

### Slide 2 — Mục lục
🖼️ 4 khối = 4 người.
🗣️ Giới thiệu mạch trình bày. Nhấn: **2 phần nặng điểm nhất** là "xử lý dữ liệu lệch" (2đ) và "kết quả thật trên nhà máy B" (3đ).

### Slide 3 — Chuyển phần 1
🖼️ Slide ngăn cách, không có nội dung kỹ thuật.

### Slide 4 — Bài toán
🖼️ Mô tả bài toán + **2 thách thức**: ① máy hỏng quá hiếm; ② hai nhà máy khác nhau.
🗣️ "Ta muốn đoán máy nào sắp hỏng để sửa trước. Có 2 cái khó: máy hỏng chỉ 8% nên **không dùng 'tỉ lệ đoán đúng'** (đoán bừa 'không hỏng' cũng đã 92% mà vô dụng); và học ở nhà máy A nhưng chấm ở nhà máy B khác điều kiện."
⭐ 2 thách thức này quyết định mọi lựa chọn sau.

### Slide 5 — Vì sao khó?
🖼️ Ví von "học lái xe đường quê → thành phố" + chiến lược 3 bước.
🗣️ "Dữ liệu lúc học khác lúc dùng, gọi là **distribution shift**. May mắn: **nguyên nhân gây hỏng vẫn như nhau**, chỉ các con số bị lệch. Khó nhất: bị chấm trên B nhưng **cấm xem đáp án của B** (xem = gian lận)."
⭐ Chiến lược: **đo** mức lệch → tạo **đèn cảnh báo miễn nhiễm lệch** → **tinh chỉnh** thêm.

### Slide 6 — Máy hỏng hiếm cỡ nào
🖼️ A: 7,36% hỏng · B: 7,95% · bảng số liệu A vs B.
🗣️ "Máy hỏng chỉ ~8%. Quan trọng: tỉ lệ hỏng A và B **gần bằng nhau** → cái lệch nằm ở **số liệu đầu vào**, không phải ở nhãn."
⭐ Tỉ lệ hỏng ổn định → hợp với kỹ thuật "chú ý máy giống B" (phần sau).

### Slide 7 — Hai nhà máy lệch thế nào
🖼️ Bảng "B so với A" + biểu đồ phân bố A (xanh) vs B (đỏ).
🗣️ "Nhìn biểu đồ: hai màu **không trùng nhau** ở nhiệt độ, tốc độ → B nóng hơn, quay nhanh hơn. Riêng **độ mòn dao trùng khít** → đó là chỗ đáng tin."
⭐ B nóng hơn +2,5°, nhanh hơn +70 v/ph; mòn dao ≈ không đổi.

### Slide 8 — Dấu hiệu hỏng & máy "lạ"
🖼️ Biểu đồ phân bố theo nhãn + ma trận tương quan + ghi chú "2,8% máy B lạ".
🗣️ "Chỉ **độ mòn dao** phân biệt rõ máy hỏng. Các biến khác phải nhìn **theo tổ hợp** mới thấy → cần mô hình mạnh. Và có 2,8% máy B 'lạ hoàn toàn' → điểm yếu sẽ nêu thật."

---

## PHẦN 2 — Xử lý dữ liệu & tạo đèn cảnh báo (Người 2, slide 9–13)

### Slide 9 — Chuyển phần 2
🖼️ Ngăn cách.

### Slide 10 — Chuẩn bị dữ liệu (chống "gian lận vô tình")
🖼️ Quy tắc vàng: học cách xử lý **chỉ trên A** · đổi chữ thành số · phạt nặng bỏ sót.
🗣️ "**Không được nhìn lén dữ liệu B** khi chuẩn bị — nếu nhìn, điểm đẹp trên giấy nhưng dùng thật sẽ sụp. Chữ đổi thành số: loại sản phẩm L<M<H giữ thứ tự, ca làm việc thì tách riêng. Máy hỏng hiếm nên **phạt nặng khi bỏ sót**."
⭐ "Nhìn lén B = rò rỉ" — đây là điều đề nhấn mạnh nhất ở phần này.

### Slide 11 — Bốn đèn cảnh báo ⭐ SLIDE QUAN TRỌNG NHẤT
🖼️ Bảng 4 đặc trưng + công thức + kiểu hỏng.
🗣️ "Đây là **ý tưởng cốt lõi**. Ta tạo 4 'đèn cảnh báo' đo 'máy còn cách vạch hỏng bao xa' — giống **đèn báo sắp hết xăng**: vạch cố định theo cấu tạo máy, không đổi dù ở nhà máy nào. Bốn đèn tương ứng 4 kiểu hỏng: nóng dồn, quá/thiếu công suất, quá tải, mòn dao."
⭐ Chỉ thêm 4 đèn này, mô hình đơn giản mạnh gần **gấp ba** (điểm AUC-PR 0,22→0,65). Vì vạch không đổi A↔B nên 4 đèn "miễn nhiễm" với sự lệch.
*(Nếu bị hỏi "vạch 2600, 244… ở đâu ra?" → xem mục "Vì sao chọn ngưỡng" ở cuối lời thoại.)*

### Slide 12 — Đo mỗi biến lệch mạnh cỡ nào
🖼️ Bảng PSI/KS.
🗣️ "Hai thước đo độ lệch. Nhiệt độ lệch rất mạnh; nhưng **4 đèn cảnh báo gần như không lệch (≈0)** — dù chúng làm từ chính nhiệt độ đang lệch. Đây là bằng chứng bằng số cho ý tưởng chính."
⭐ Số càng cao càng lệch: nhiệt độ 1,08 (rất mạnh), đèn cảnh báo ≈ 0.

### Slide 13 — Máy tính có phân biệt được A/B không?
🖼️ AUC 0,82 (dùng số thô) vs 0,53 (dùng đèn cảnh báo) + biểu đồ cột.
🗣️ "Huấn luyện một mô hình đoán 'máy này của A hay B'. Đoán càng dễ = hai nhà máy càng khác. Dùng **số thô** thì đoán rất chuẩn (0,82); dùng **đèn cảnh báo** thì như tung đồng xu (0,53). → sự lệch nằm hết ở số thô, đèn cảnh báo 'tàng hình' với nó."

---

## PHẦN 3 — Xử lý lệch & xây mô hình (Người 3, slide 14–19)

### Slide 14 — Chuyển phần 3
🖼️ Ngăn cách.

### Slide 15 — Chú ý hơn tới máy A "giống B" (reweighting)
🖼️ Ý tưởng + kết quả gần như đứng yên.
🗣️ "Máy nào ở A **trông giống B** thì cho 'học kỹ hơn' — giống ôn thi, biết đề giống dạng nào thì luyện dạng đó. Kết quả gần như không đổi — **và đó là tin tốt**: 4 đèn cảnh báo đã lo gần hết rồi, kỹ thuật này chỉ vá phần nhỏ."
⭐ Phải **đặt trần cho trọng số** để một máy không 'la to át cả lớp'.

### Slide 16 — Chọn mô hình mà không nhìn đáp án (IWV)
🖼️ Nghịch lý chấm điểm + cách giải.
🗣️ "Bị chấm trên B nhưng cấm xem đáp án B — chọn mô hình bằng gì? Ta **tự ra đề thi thử giống đề thật** (gọi là IWV): dùng dữ liệu A nhưng đánh trọng số cho phần giống B. Nhờ đó thử sai bao nhiêu cũng không gian lận; đáp án B chỉ mở **một lần cuối**."
⭐ Đây là **chốt trung thực** của cả bài — nhắc lại ở slide kết luận.

### Slide 17 — Thử 4 mô hình
🖼️ 4 mô hình / 3 trường phái + cách dò tham số.
🗣️ "Thử 4 mô hình khác nhau để lát gộp cho đa dạng: một mô hình đơn giản làm mốc; hai mô hình 'nhiều cây bỏ phiếu' (ổn định); một mô hình 'học nối tiếp' (mạnh nhưng dễ học thuộc lòng A). Máy **tự dò tham số tốt nhất**."

### Slide 18 — Bảng so sánh các phiên bản
🖼️ Bảng từ mô hình thô đến bản chốt.
🗣️ "Đọc theo cột **F1**. Từ mô hình thô 0,231, thêm 4 đèn cảnh báo vọt lên 0,716, chuyển sang mô hình cây đạt 0,783. Từ đó về sau các bản **hội tụ 0,783** — dấu hiệu đã chạm trần dữ liệu."
⭐ Hành trình 0,231 → 0,783 = **gấp 3,4 lần**.

### Slide 19 — Gộp mô hình cho chắc (ensemble)
🖼️ Voting vs Stacking.
🗣️ "Mỗi mô hình sai ở chỗ khác nhau → gộp lại thì bù trừ, ổn định hơn. Máy tự chọn Random Forest 25% + ExtraTrees 25% + XGBoost 50%. Chốt cách 'bỏ phiếu' vì đơn giản, ít rủi ro."

---

## PHẦN 4 — Kết quả & kết luận (Người 4, slide 20–28)

### Slide 20 — Chuyển phần 4
🖼️ Ngăn cách.

### Slide 21 — Kết quả cuối trên nhà máy B (3 điểm)
🖼️ F1 = 0,783 · bắt được ~75% · báo đúng 4/5 + đường PR.
🗣️ "Trên nhà máy B (mô hình **chưa từng thấy**): F1 = 0,783, bắt được 75% máy sắp hỏng, cứ 5 cảnh báo thì ~4 đúng. Đây là ô 3 điểm — kết quả thật."
⭐ 0,783 / bắt 75% / báo đúng 82%.

### Slide 22 — Bảng đúng/sai (confusion matrix)
🖼️ 4 ô TP/TN/FP/FN + cách đọc.
🗣️ "Bắt đúng **358** máy hỏng, **bỏ sót 119**, **báo nhầm 80**. Bỏ sót (máy dừng đột ngột) tốn kém hơn báo nhầm → có thể hạ vạch báo để bắt nhiều hơn."

### Slide 23 — Con số có chắc không? (bootstrap)
🖼️ F1 = 0,783, khoảng [0,753; 0,811].
🗣️ "Nhà máy B chỉ có 477 máy hỏng nên con số có sai số — ta **bốc lại mẫu 2000 lần** để xem F1 dao động cỡ nào. Kết quả nằm trong [0,753; 0,811]. Bản gộp hơn mô hình đơn 100% số lần nhưng chênh nhỏ → nói khiêm tốn, không thổi phồng."

### Slide 24 — Rút ra gì cho nhà máy?
🖼️ 3 ý + đề xuất 2 mức cảnh báo.
🗣️ "Một: **theo dõi độ mòn dao** là quan trọng nhất — vừa báo hỏng tốt vừa thay dao được. Hai: **đặt cảnh báo theo ngưỡng vật lý** dùng lại được cả khi đổi máy. Ba: cân nhắc bỏ sót ↔ báo nhầm → đề xuất 2 mức: mức cao thì dừng máy ngay, mức thấp thì theo dõi thêm."

### Slide 25 — Hạn chế & hướng cải tiến
🖼️ 4 hạn chế + 4 hướng.
🗣️ "Nêu thật hạn chế: mô hình cây đoán kém ở máy 'lạ' (2,8%); chưa có đáp án B để kiểm chứng 100%; và **~25% máy hỏng là ngẫu nhiên** nên trần điểm ~0,78. Hướng cải tiến: đã khôi phục lại các ngưỡng từ A; còn lại thêm dữ liệu theo thời gian, thu thập ít nhãn B…"
⭐ "Trần ~0,78 vì 25% máy hỏng ngẫu nhiên" — vũ khí trả lời "sao không cao hơn?".

### Slide 26 — Mọi quyết định đều có lý do
🖼️ Bảng quyết định + lý do.
🗣️ "Slide này để chứng minh không có lựa chọn nào tuỳ tiện: dùng F1 vì lớp hiếm; đèn cảnh báo neo ngưỡng vật lý; không tạo dữ liệu giả; chọn mô hình bằng thi thử (không nhìn B)…"

### Slide 27 — Kết luận
🖼️ 4 ý đọng lại.
🗣️ "Chìa khoá: bám quy luật vật lý không đổi thay vì số thô đã lệch. Nhờ đó mô hình học ở A chạy tốt trên B. Trung thực: mọi lựa chọn dùng 'thi thử', không nhìn đáp án. Kết quả: F1 = 0,783, gấp 3,4 lần."
⭐ Nhấn lại: **"chọn bằng thi thử — không nhìn đáp án B"**.

### Slide 28 — Hỏi & Đáp
🖼️ Q&A. Xem bảng câu hỏi thường gặp trong lời thoại.

---

## 6 câu hỏi hay bị hỏi — trả lời gọn
1. **Sao không dùng 'tỉ lệ đoán đúng'?** → Máy hỏng chỉ 8%, đoán "ai cũng khoẻ" đã đúng 92% mà bỏ sót hết.
2. **4 đèn cảnh báo lấy ngưỡng ở đâu?** → Quét trên nhà máy A tìm chỗ tỉ lệ hỏng vọt lên; kiểm tra thấy vẫn đúng trên B.
3. **Sao "chú ý máy giống B" gần như không giúp?** → Vì đèn cảnh báo đã lo gần hết — đó là tin tốt.
4. **Sao F1 không lên 0,90?** → 25% máy hỏng là ngẫu nhiên, không đoán được → trần ~0,78.
5. **Sao không nhìn đáp án B cho dễ?** → Nhìn = gian lận; điểm ảo, dùng thật sẽ sai.
6. **0,783 tốt hay xấu?** → Tốt: gấp 3,4 lần cách ngây thơ và đã chạm mức tối đa dữ liệu cho phép.
