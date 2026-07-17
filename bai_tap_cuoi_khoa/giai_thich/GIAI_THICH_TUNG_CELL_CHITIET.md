# Giải thích từng cell — kiểu dễ hiểu cho người mới

> Đọc file này bạn **không cần biết nhiều về máy học** vẫn hiểu notebook đang làm gì.
> Mỗi cell có: 🎯 **làm gì** · 💬 **vì sao (nói nôm na)** · 📌 **ví dụ** · 🔧 **con số/ngưỡng & vì sao chọn** (khi có).
> Notebook có 114 ô, trong đó 33 ô là code (chạy được), còn lại là chữ giải thích.

## Bài này làm gì? (đọc 30 giây là nắm)

Nhà máy có nhiều **máy phay CNC**. Ta muốn máy tính **đoán trước máy nào sắp hỏng** để sửa trước, đỡ phải dừng dây chuyền đột ngột.

Cái khó: ta **học trên máy ở nhà máy cũ (gọi là A)** nhưng phải **đoán đúng ở nhà máy mới (gọi là B)** — nhà máy B nóng hơn, chạy nhanh hơn. Giống như **học lái xe ở đường quê rồi phải chạy trong thành phố**: vẫn là lái xe, nhưng điều kiện khác nên dễ sai. Trong máy học, chuyện "dữ liệu lúc học khác lúc dùng" gọi là **distribution shift** (dữ liệu bị lệch).

Thêm một cái khó nữa: **chỉ ~8% máy thật sự hỏng** (rất hiếm). Nếu cứ đoán "máy nào cũng không hỏng" thì đúng 92% — nghe cao nhưng **vô dụng** vì bỏ sót hết máy hỏng.

**Ý tưởng chính của cả bài:** thay vì cho máy tính học các con số thô (nhiệt độ, tốc độ… vốn đã bị lệch giữa A và B), ta tạo ra vài **"đèn cảnh báo"** đo "máy còn cách ngưỡng hỏng bao xa". Vì ngưỡng hỏng là **quy luật vật lý không đổi** giữa hai nhà máy, nên đèn cảnh báo học ở A vẫn đúng ở B. Nhờ đó điểm số cuối cùng đạt **F1 = 0,783** (gấp 3,4 lần cách làm ngây thơ ban đầu).

*(F1 là một kiểu điểm chấm, càng gần 1 càng tốt — sẽ giải thích kỹ ở dưới.)*

---

## PHẦN 0 — Chuẩn bị (ô 2, 4)

### Ô 2 — Nạp dữ liệu
🎯 **Làm gì.** Mở 2 file dữ liệu (nhà máy A để học, nhà máy B để kiểm tra), khai báo tên các cột, in ra vài thông tin.

💬 **Vì sao.** Trước khi làm gì cũng phải "mở tủ lấy đồ ra". Có một dòng `RANDOM_STATE = 42` — đây là cách **khoá tính ngẫu nhiên** để lần nào chạy lại cũng ra **đúng kết quả cũ** (nếu không, mỗi lần chạy máy tính lại xáo trộn khác đi một chút).

📌 **Ví dụ.** In ra: nhà máy A có 14.000 máy, 7,36% hỏng; nhà máy B có 6.000 máy, 7,95% hỏng. Hai tỉ lệ này **gần bằng nhau** — một chi tiết nhỏ nhưng quan trọng (xem ô 7).

### Ô 4 — Kiểm tra dữ liệu trùng
🎯 **Làm gì.** Đếm xem có dòng nào bị **lặp lại y hệt** không.

💬 **Vì sao.** Dữ liệu lặp làm máy tính "học vẹt" và chấm điểm sai (như một câu hỏi bị in 2 lần trong đề thi). Ở đây đếm được **0 dòng trùng** → dữ liệu sạch, đi tiếp.

---

## PHẦN 1 — Khám phá dữ liệu (ô 5–45): nhìn tận mắt sự khác nhau A/B

Các ô ở phần này chủ yếu **vẽ biểu đồ** để hiểu dữ liệu. Quan trọng là *thấy được gì*, không phải code.

### Ô 7 — Bao nhiêu % máy hỏng?
🎯 Vẽ cột tỉ lệ máy hỏng ở A và B.
💬 Khẳng định 2 điều: (1) máy hỏng **rất hiếm (~8%)** → không được dùng "tỉ lệ đoán đúng" (accuracy) để chấm, vì đoán bừa "không hỏng" cũng đã 92%; (2) tỉ lệ hỏng ở A và B **gần bằng nhau** → cái khác nhau nằm ở **số liệu đầu vào**, không phải ở chuyện "máy B hay hỏng hơn".

### Ô 11 — Bảng tóm tắt từng cột
🎯 In bảng trung bình / nhỏ nhất / lớn nhất… của từng biến, cho cả A và B.
💬 Nhìn nhanh đã thấy các cột của B "trượt" đi so với A (ví dụ nhiệt độ B cao hơn) — dấu hiệu đầu tiên của việc dữ liệu bị lệch.

### Ô 14 & 16 — Vẽ chồng phân bố A/B + đo mức lệch
🎯 (14) Vẽ biểu đồ phân bố của A (xanh) chồng lên B (đỏ) cho 5 biến; (16) tính mỗi cột "trượt" bao nhiêu %.
💬 Đây là **bằng chứng nhìn tận mắt**: hai màu xanh–đỏ **không trùng nhau** ở nhiệt độ và tốc độ (B lệch nhiều), nhưng **trùng khít** ở độ mòn dao (không lệch).
📌 **Kết quả:** B nóng hơn +2,5°, quay nhanh hơn +70 vòng/phút, lực xoắn thấp hơn ~8%, **riêng độ mòn dao gần như y nguyên** → độ mòn dao là "chỗ đáng tin" để bám vào.

### Ô 20 & 23 — Máy hỏng khác máy lành ở biến nào?
🎯 (20) Vẽ hộp so máy hỏng vs máy lành theo từng biến; (23) bảng màu xem các biến có "đi cùng nhau" không.
💬 Chỉ **độ mòn dao** phân biệt rõ máy hỏng (mòn nhiều hơn hẳn). Các biến khác nhìn riêng thì gần như trùng nhau → tín hiệu hỏng **không nằm ở một biến đơn** mà ẩn trong sự kết hợp nhiều biến → cần mô hình mạnh hơn (mô hình "cây" ở phần sau).

### Ô 27 & 30 — Máy hỏng "tụ" ở tổ hợp nào?
🎯 Vẽ phân bố theo nhãn và chấm từng máy lên đồ thị 2 biến, tô đỏ máy hỏng.
💬 Lộ ra điều thú vị: máy hỏng có **lực xoắn dồn về hai đầu** (quá cao *hoặc* quá thấp = quá tải hoặc thiếu tải), và **quay chậm**. Tức máy hỏng theo **tổ hợp** (mòn cao + lực xoắn bất thường), không theo một ngưỡng đơn giản. Đây là gợi ý để tạo "đèn cảnh báo" ở Phần 2.

### Ô 34 & 38 — Loại sản phẩm & ca làm việc
🎯 So tỉ lệ hỏng theo loại sản phẩm / ca; kiểm tra 2 nhà máy có khác tỉ lệ loại/ca không.
💬 Tỉ lệ hỏng giữa các loại/ca gần bằng nhau → hai biến này **ít giá trị**. Có một lưu ý: tỉ lệ loại sản phẩm L/M/H **khác nhau giữa A và B** — nhưng "đèn cảnh báo" sau này đã tính ngưỡng riêng cho từng loại nên không sao.

### Ô 42 — Bao nhiêu máy B "lạ hoàn toàn"?
🎯 Đếm xem có bao nhiêu máy B có số liệu **vượt ra ngoài khoảng đã từng thấy ở A**.
💬 Mô hình "cây" đoán **rất kém ở vùng chưa từng thấy** (giống học sinh gặp dạng bài lạ). Kết quả: **2,8% máy B "lạ"** → đây là điểm yếu sẽ thành thật nêu trong báo cáo.

---

## PHẦN 2 — Dựng "thước đo" và làm bản nháp đầu tiên (ô 47, 49)

### Ô 47 — Thước đo chung
🎯 **Làm gì.** Viết một hàm `evaluate()` để **chấm điểm** mọi phiên bản mô hình theo cùng một cách, và ghi vào một **bảng xếp hạng**.
💬 **Vì sao.** Để so sánh công bằng: mọi phiên bản (v0, v1, v2…) đều chấm bằng **cùng một thước**. Thước này in các điểm F1 / AUC-PR / Precision / Recall — **cố tình không có accuracy** (vì lớp hiếm).

> **Giải thích nhanh mấy điểm này:**
> - **Precision ("báo đúng"):** trong các máy bị báo "sắp hỏng", bao nhiêu % **đúng là hỏng thật**.
> - **Recall ("bắt được"):** trong các máy **thật sự hỏng**, bắt được bao nhiêu %.
> - **F1:** gộp hai cái trên thành một điểm, chỉ cao khi **cả hai cùng cao**. Đây là điểm chính để so sánh.
> - **AUC-PR / AUC-ROC:** hai điểm phụ (0→1) đo chất lượng chung, càng cao càng tốt.

### Ô 49 — Bản nháp đầu tiên (v0)
🎯 **Làm gì.** Mô hình đơn giản nhất (Logistic Regression — một kiểu vẽ đường thẳng phân loại), chưa thêm gì đặc biệt.
💬 **Vì sao làm bản nháp yếu này.** Để làm **mốc**: mọi cải tiến sau đều so với nó xem có thật sự tốt lên không.
🔧 **Vài lựa chọn nhỏ:**
- Chữ → số: loại sản phẩm L<M<H đổi thành 1,2,3 (**vì có thứ tự**); ca làm việc thì tách mỗi ca một cột (**vì không có thứ tự**).
- `class_weight='balanced'` = **"phạt nặng khi bỏ sót máy hỏng"** để mô hình chịu khó bắt lớp hiếm.
- Học cách chuẩn hoá **chỉ trên A** rồi áp cho B → **không nhìn lén B** (chống gian lận).
📌 **Kết quả:** F1 chỉ **0,23** — rất yếu, đúng như dự đoán. Đây là điểm xuất phát.

---

## PHẦN 3 — Tạo "đèn cảnh báo" (ô 52) ⭐ QUAN TRỌNG NHẤT

### Ô 52 — Bốn đèn cảnh báo vật lý ⭐⭐⭐
🎯 **Làm gì.** Tạo **4 cột mới**, mỗi cột như một **đèn cảnh báo** đo "máy còn cách vạch hỏng bao xa".

💬 **Vì sao đây là chìa khoá.** Giống **đèn báo sắp hết xăng** trên ô tô: nó chỉ sáng khi bình xăng xuống dưới một vạch. Vạch đó là **cố định theo cấu tạo xe**, không đổi dù bạn lái ở quê hay ở phố. Ở đây cũng vậy: máy CNC hỏng theo **4 cơ chế vật lý có ngưỡng cố định**. Ta đo "khoảng cách tới ngưỡng" cho từng cơ chế. Vì ngưỡng cố định, đèn cảnh báo **học ở nhà máy A vẫn đúng ở nhà máy B** — trong khi nhiệt độ, tốc độ thô thì đã lệch.

**4 đèn cảnh báo (kèm ngưỡng và vì sao chọn ngưỡng đó):**

| Đèn | Ý nghĩa đời thường | Ngưỡng & vì sao chọn |
|---|---|---|
| **nguy_tan_nhiet** | Máy **nóng dồn**: vừa ít thoát nhiệt **VÀ** quay chậm | Bật khi chênh nhiệt < 8,6° **và** tốc độ < 1380 v/ph. Tại mốc này, trong các máy vượt ngưỡng có **84% hỏng thật** — nếu nới lỏng ngưỡng thì tỉ lệ này rớt còn ~45%, nên 8,6/1380 là mốc "đúng" nhất. |
| **lech_cong_suat** | Công suất **ra ngoài vùng an toàn** (quá cao hoặc quá thấp) | Vùng an toàn là [2600 ; 11500]. Vì máy **lành** hầu hết chạy trong khoảng ~2960–10560, nên đặt vạch hơi rộng hơn để chỉ bắt máy thật sự bất thường. (Vạch cũ [3500;9000] quá hẹp → 83% báo nhầm.) |
| **bien_overstrain** | **Quá tải** (mòn × lực xoắn vượt ngưỡng theo từng loại sản phẩm) | Ngưỡng khác nhau: L=12800, M=13900, H=14500 (sản phẩm cứng chịu tải cao hơn mới hỏng — đúng vật lý). Tỉ lệ hỏng vọt lên đúng tại các mốc này. |
| **mon_twf** | **Dao mòn** quá mức, sắp phải thay | Bật khi độ mòn > 244 phút. Vì các máy hỏng "do mòn" dồn ở vùng 244–253 phút, và dao lành mòn tối đa cũng chỉ tới 253. Đây là đèn **mạnh nhất** (liên quan tới hỏng nhiều nhất). |

💬 **Vì sao dùng phép "max(...,0)".** Đó là cách nói "**chỉ tính khi vượt vạch, chưa vượt thì = 0**" — giống đèn xăng: còn nhiều xăng thì đèn tắt (giá trị 0), gần cạn mới sáng dần.

📌 **Ví dụ tính tay một máy.** Máy: chênh nhiệt 6°, tốc 1200 v/ph, mòn 250, lực xoắn 50, loại L, công suất 8000W:
- Đèn *nóng dồn*: chênh nhiệt 6 < 8,6 **và** tốc 1200 < 1380 → **đèn sáng** (giá trị 468).
- Đèn *công suất*: 8000 nằm trong [2600;11500] → **tắt** (0), an toàn.
- Đèn *quá tải*: 250×50 = 12500, còn dưới ngưỡng L=12800 một chút → gần vạch (−300).
- Đèn *dao mòn*: 250 > 244 → **sáng** (6), sắp phải thay dao.
→ Máy này bật 2 đèn: nóng dồn + dao mòn. Mô hình đọc đúng tình trạng.

📌 **Kết quả:** chỉ thêm 4 cột này, mô hình đơn giản nhảy từ F1 **0,23 lên 0,72** (mạnh gần gấp 3). Vì ngưỡng vật lý không đổi A↔B nên 4 đèn này "miễn nhiễm" với sự lệch dữ liệu.

### Ô 55 & 58 — Kiểm tra đèn có thật sự hữu ích không
🎯 Vẽ biểu đồ và xem mô hình có "dựa vào" 4 đèn không.
💬 Đề bài yêu cầu "chứng minh bằng số". Kết quả: cả 4 đèn đều liên quan mạnh tới hỏng (đèn *dao mòn* thậm chí mạnh hơn cả biến gốc tốt nhất), và mô hình **thật sự sử dụng** chúng chứ không phải "thêm cho có".

---

## PHẦN 4 — Mô hình mạnh hơn: "cây" (ô 62)

### Ô 62 — Huấn luyện 3 mô hình cây ⭐
🎯 **Làm gì.** Huấn luyện 3 mô hình mạnh và **tự động dò tham số tốt nhất** cho mỗi cái.

💬 **Ba mô hình là gì (nói nôm na):**
- **Random Forest & ExtraTrees** = "**nhiều cây quyết định cùng bỏ phiếu**" → kết quả ổn định, ít may rủi.
- **XGBoost** = "nhiều cây **học nối tiếp, cây sau sửa lỗi cây trước**" → rất mạnh, nhưng **dễ học thuộc lòng** nhà máy A.

Dùng 3 cái vì chúng **sai ở chỗ khác nhau**, lát nữa gộp lại cho chắc.

🔧 **Vài lựa chọn tham số (và lý do đời thường):**
- **"Tự động dò tham số ngẫu nhiên":** thay vì thử hết mọi tổ hợp (quá nhiều, tốn thời gian), máy thử ngẫu nhiên ~25–30 tổ hợp và giữ cái tốt nhất — nhanh mà vẫn tốt.
- **Chấm bằng AUC-PR (không accuracy):** vì lớp hiếm.
- **Chia dữ liệu 5 phần giữ đúng tỉ lệ hỏng:** để mỗi lần kiểm tra đều có đủ máy hỏng (nếu không, có phần không có máy hỏng nào → chấm sai).
- `scale_pos_weight ≈ 12,6` cho XGBoost = cũng là cách "**phạt nặng khi bỏ sót**".

📌 **Kết quả thú vị:** Random Forest **thắng trên nhà máy B** (F1 0,783) dù XGBoost trông "học giỏi hơn" trên nhà máy A. Bài học: mô hình học thuộc lòng A chưa chắc chạy tốt ở B → phải có cách chọn mô hình "hướng về B" (Phần 6).

---

## PHẦN 5 — Đo và xử lý sự lệch dữ liệu (ô 70, 74, 78, 82)

### Ô 70 — Đo mỗi biến lệch mạnh cỡ nào
🎯 Tính hai "thước đo độ lệch" (**PSI** và **KS**) cho từng biến giữa A và B.
💬 **PSI** là một con số: dưới 0,1 = không lệch, trên 0,25 = lệch mạnh.
📌 **Kết quả:** nhiệt độ lệch rất mạnh (PSI 1,08); nhưng **4 đèn cảnh báo gần như không lệch (≈0)** — dù chúng được tạo ra từ chính nhiệt độ đang lệch. Đây là **bằng chứng bằng số** cho ý tưởng chính của bài.

### Ô 74 — "Vượt ngưỡng thì tỉ lệ hỏng" có giống nhau ở A và B không?
🎯 Kiểm tra: khi máy bật một đèn cảnh báo, tỉ lệ nó hỏng thật ở A và B có bằng nhau không.
💬 Nếu bằng nhau → **quy luật gây hỏng không đổi**, chỉ có số liệu đầu vào đổi. Đây là lý do bám vào đèn cảnh báo là cách xử lý đúng.
📌 **Kết quả:** đèn *nóng dồn* 84% (A) vs 82% (B), các đèn khác cũng lệch dưới 6% → quy luật ổn định.

### Ô 78 — Máy tính có tự phân biệt được "đây là A hay B" không?
🎯 Huấn luyện một mô hình đoán "máy này thuộc nhà máy A hay B", chỉ từ số liệu.
💬 Nếu nó đoán **dễ** → hai nhà máy khác nhau nhiều. Điểm của nó: 0,5 = đoán mò (không khác), 1,0 = khác hẳn.
📌 **Kết quả:** dùng **số thô** thì đoán rất chuẩn (0,82 = khác nhiều); dùng **4 đèn cảnh báo** thì như tung đồng xu (0,53 = gần như không khác). → toàn bộ sự lệch nằm ở số thô, đèn cảnh báo "tàng hình" với sự lệch.

### Ô 82 — Chú ý hơn tới những máy A "giống B"
🎯 **Làm gì.** Cho những máy ở A mà **trông giống máy B** một **trọng số cao hơn** khi học.
💬 **Vì sao.** Giống như ôn thi: nếu biết đề thật sẽ giống dạng nào, ta **luyện kỹ dạng đó hơn**. Ở đây, máy A nào giống B thì cho "học kỹ hơn" để mô hình quen với kiểu B.
🔧 **Con số quan trọng:** phải **đặt trần cho trọng số (tối đa 10)**. Vì vài máy A rất giống B sẽ có trọng số vọt lên ~77 — như **một người la thật to át cả lớp**. Đặt trần để không ai chi phối quá mức.
📌 **Kết quả:** điểm gần như **không đổi (vẫn 0,783)** — và **đó là tin tốt**: nghĩa là 4 đèn cảnh báo đã lo gần hết việc chống lệch rồi, kỹ thuật này chỉ vá phần nhỏ còn lại.

---

## PHẦN 6 — Chọn mô hình mà KHÔNG nhìn đáp án của B (ô 87, 90, 96, 98, 102, 105)

### Ô 87 — Cách "thi thử" mô phỏng nhà máy B ⭐⭐
🎯 **Làm gì.** Dựng cách tự chấm điểm (gọi là **IWV**) để chọn mô hình/ngưỡng **như thể đang ở nhà máy B**, nhưng **chỉ dùng dữ liệu A**.
💬 **Vì sao (quan trọng nhất của cả bài).** Đề bài chấm trên B nhưng **cấm xem đáp án B** (xem = gian lận). Giải pháp: **tự ra đề thi thử giống đề thật** — lấy dữ liệu A, đánh trọng số cho phần "giống B", rồi chấm trên đó. Nhờ vậy thử sai bao nhiêu cũng không gian lận; đáp án B chỉ mở ra **một lần cuối** để báo cáo.
🔧 **Con số:** "số mẫu thật sự có ích" chỉ còn **~24%** của 14.000 (vì vài mẫu nặng trọng số lấn át) → cách thi thử này **hơi nhiễu**, nên các phiên bản điểm sát nhau coi như ngang nhau.

### Ô 90 — Chọn "vạch báo hỏng" (ngưỡng)
🎯 **Làm gì.** Chọn "đạt bao nhiêu điểm nghi ngờ thì kêu là hỏng" sao cho điểm F1 cao nhất — chọn bằng cách thi thử ở ô 87.
💬 **Vì sao.** Vạch mặc định 0,5 **không hợp** với lớp hiếm. Chấm thử cho ra vạch tốt nhất là **0,585**.

### Ô 96 & 98 — Gộp 4 mô hình lại cho chắc
🎯 **Làm gì.** (96) **Bỏ phiếu (Voting)** — lấy trung bình có trọng số ý kiến 4 mô hình; (98) **Trộn (Stacking)** — một mô hình nhỏ học cách trộn.
💬 **Vì sao.** 4 mô hình sai ở chỗ khác nhau → gộp lại thì bù trừ, ổn định hơn. Trọng số gộp cũng chọn bằng cách thi thử (không nhìn B).
📌 **Kết quả:** máy tự chọn **Random Forest 25% + ExtraTrees 25% + XGBoost 50%** (bỏ mô hình yếu). Cả Bỏ phiếu và Trộn cho điểm ngang nhau → chọn **Bỏ phiếu** vì đơn giản, ít rủi ro hơn.

### Ô 102 — Chốt mô hình + kết quả cuối
🎯 So Bỏ phiếu vs Trộn (bằng thi thử), chọn bản thắng, rồi mới **mở đáp án B đúng một lần** để báo cáo.
📌 **Kết quả cuối:** F1 = **0,783**, báo đúng 82%, bắt được 75% máy hỏng.

### Ô 105 — Bảng "đúng/sai" (ma trận nhầm lẫn)
🎯 Đếm 4 tình huống của bản chốt trên nhà máy B.
📌 **Kết quả:** bắt đúng **358** máy hỏng, **bỏ sót 119**, **báo nhầm 80**, đúng **5443** máy lành. Vì bỏ sót (máy dừng đột ngột) tốn kém hơn báo nhầm, sau này có thể hạ vạch báo để bắt được nhiều máy hỏng hơn.

---

## PHẦN 7 — Con số có đáng tin không? + Giải thích "sao không cao hơn" (ô 108, 112)

### Ô 108 — Kiểm tra độ chắc chắn (bootstrap)
🎯 **Làm gì.** **Bốc lại mẫu 2000 lần** để xem điểm F1 dao động cỡ nào.
💬 **Vì sao.** Nhà máy B chỉ có **477 máy hỏng** — quá ít nên con số F1 có sai số. Ta phải báo một **khoảng** thay vì một con số. (Giống thăm dò ý kiến: hỏi lại nhiều nhóm khác nhau để biết kết quả có ổn định không.)
📌 **Kết quả:** F1 = 0,783, dao động trong khoảng **[0,753 ; 0,811]**. Bản gộp hơn mô hình đơn **100% số lần** nhưng chỉ hơn +0,015 → hơn nhất quán nhưng **biên độ nhỏ**, nên trình bày khiêm tốn.

### Ô 112 — Vì sao điểm không cao hơn nữa? ⭐⭐
🎯 **Làm gì.** So bộ ngưỡng cũ (chuẩn AI4I gốc) với bộ ngưỡng đã khôi phục từ A; đo xem còn bao nhiêu máy hỏng "không theo quy luật nào".
💬 **Vì sao ô này quan trọng.** Nó trả lời **2 câu giám khảo hay hỏi:**
1. *"Mấy con số ngưỡng (2600, 244…) ở đâu ra?"* → Không phải bịa. Ta **quét thử trên nhà máy A** và tìm đúng chỗ tỉ lệ hỏng vọt lên — đó là ngưỡng thật của quy luật. Nhờ khôi phục lại, độ chính xác của quy luật tăng từ **0,26 lên 0,81**.
2. *"Sao F1 không lên 0,90 được?"* → Vì sau khi quy luật đã "sạch", **vẫn còn ~25% máy hỏng không theo quy luật nào** — chúng hỏng **ngẫu nhiên**, số liệu không hề báo trước. Không mô hình nào đoán được chuyện ngẫu nhiên → **trần điểm tối đa chỉ khoảng 0,78**. Mọi phiên bản của bài đều dừng đúng ở đó. Muốn cao hơn chỉ có cách gian lận (nhìn đáp án B).

---

## Tóm cả bài trong một hình

```
Nạp dữ liệu   →  8% máy hỏng (hiếm), A và B lệch nhau
Khám phá      →  lệch nằm ở số thô; hỏng theo tổ hợp; mòn dao quan trọng nhất
Bản nháp v0   →  mô hình thô: F1 = 0,23 (yếu)
+ 4 đèn cảnh báo →  F1 = 0,72  ← chìa khoá: ngưỡng vật lý không đổi A↔B
+ mô hình cây →  F1 = 0,78
Đo & bù lệch  →  đèn cảnh báo đã lo gần hết, vá thêm chỉ nhích nhẹ
Thi thử (IWV) →  chọn mô hình/vạch mà KHÔNG nhìn đáp án B
Kết quả       →  F1 = 0,783 (chắc chắn trong [0,753; 0,811])
Vì sao dừng ở đây? →  25% máy hỏng là ngẫu nhiên → trần ≈ 0,78
```

## 6 câu hỏi hay gặp — trả lời gọn
1. **Sao không dùng "tỉ lệ đoán đúng" (accuracy)?** → Máy hỏng chỉ 8%, đoán "ai cũng khoẻ" đã đúng 92% mà bỏ sót hết → vô dụng.
2. **Mấy ngưỡng 2600/244… ở đâu ra?** → Quét trên nhà máy A tìm chỗ tỉ lệ hỏng vọt lên; kiểm tra thấy vẫn đúng trên B.
3. **Sao "chú ý máy giống B" gần như không giúp?** → Vì 4 đèn cảnh báo đã lo gần hết việc chống lệch rồi — đó là tin tốt.
4. **Sao F1 không lên 0,90?** → 25% máy hỏng là ngẫu nhiên, không đoán được → trần ~0,78.
5. **Sao không nhìn đáp án B cho dễ?** → Nhìn = gian lận; điểm đẹp trên giấy nhưng dùng thật sẽ hỏng.
6. **F1 = 0,783 là tốt hay xấu?** → Tốt: gấp 3,4 lần cách làm ngây thơ, và đã chạm mức tối đa mà dữ liệu cho phép.
