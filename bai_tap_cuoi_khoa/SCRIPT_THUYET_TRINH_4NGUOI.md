# Script thuyết trình — 4 người (deck `SLIDE_THUYET_TRINH_v5.pptx`, 29 slide)

> Tổng ~13–14 phút + Q&A. Chuyển người ở các slide **Divider** (3, 10, 15, 21).
> Script này cũng nằm trong **speaker notes** của từng slide. Ký hiệu: **[mở]** câu mở, **[chuyển]** câu bàn giao, *(cue: …)* = động tác/nhấn mạnh.

## Phân công nhanh

| Người | Slide | Nội dung | Thời lượng |
|---|---|---|---|
| — (chung) | 1–2 | Mở đầu + Agenda | ~0,5' |
| **1** | 3–9 | Bài toán · distribution shift · bản đồ đề · EDA (Phần 1) | ~3' |
| **2** | 10–14 | Tiền xử lý · 3 đặc trưng · đo shift PSI/KS · drift classifier (Phần 2 + 3.1–3.2) | ~3' |
| **3** | 15–20 | Reweighting · IWV · 4 mô hình · so sánh · ensemble (Phần 3.3–3.4 + Phần 4) | ~3,5' |
| **4** | 21–29 | Kết quả · confusion matrix · bootstrap · báo cáo · quyết định kỹ thuật · kết luận · Q&A (Kết quả + Phần 5) | ~4' |

---

## ⭐ Cách script đáp ứng 2 tiêu chí Phần 5 (0,5đ)

**Tiêu chí 1 — "Trình bày rõ ràng, logic; giải thích được quyết định kỹ thuật khi được hỏi":**
- *Rõ ràng, logic:* mạch 5 phần + slide Divider báo chuyển phần; mỗi người **kết mỗi slide bằng một câu "⇒ vì sao"**; câu **[chuyển]** nối liền các phần.
- *Giải thích quyết định khi hỏi:* **Người 4 trình bày slide 27 "Quyết định kỹ thuật & lý do"** (bảng 8 quyết định → lý do) — chứng minh không quyết định nào tuỳ tiện; đồng thời **ma trận phân công Q&A** (cuối file) để đúng người trả lời đúng mảng, dựa trên `NGAN_HANG_QA.md`.

**Tiêu chí 2 — "Kết luận có insight vận hành/bảo trì; nhận ra hạn chế và đề xuất hướng cải tiến":**
- **Người 4** đảm nhiệm trọn: **S25** insight vận hành (ưu tiên độ mòn dao, cảnh báo theo ngưỡng vật lý, 2 mức cảnh báo) · **S26** hạn chế + hướng cải tiến · **S28** kết luận đọng lại.

> Chốt kỷ luật xuyên suốt (nhắc đi nhắc lại cho ăn điểm tiêu chí 1): *"mọi lựa chọn chọn bằng IWV — không nhìn nhãn Test B"*.

---

## NGƯỜI 1 — Mở đầu & Khám phá dữ liệu (S1–S9, ~3')

**S1 — Title** — **[mở]** "Kính chào thầy/cô và các bạn. Nhóm em trình bày bài toán **dự đoán máy CNC sắp hỏng khi dữ liệu lúc học khác lúc dùng thật**. Kết quả chốt: **F1 = 0,781** trên nhà máy B, gấp **3,4 lần** baseline, notebook chạy full không lỗi. Bài gồm 4 phần do 4 thành viên trình bày."

**S2 — Agenda** — "Người 1 (em) trình bày bài toán & khám phá dữ liệu; Người 2 tiền xử lý, tạo đặc trưng & phát hiện shift; Người 3 xử lý shift & mô hình; Người 4 kết quả, độ tin cậy & kết luận. *(cue: chỉ vào bảng)* Hai khối nhiều điểm nhất là **xử lý shift (2đ)** và **kết quả thật (3đ)**."

**S3 — Divider Phần 1** — "Em bắt đầu Phần 1."

**S4 — Bài toán** — "Mục tiêu: dự đoán nhị phân — máy có hỏng ở ca kế tiếp không — để bảo trì chủ động. Có 5 số đo cảm biến + 2 nhãn phân loại. Hai thách thức: *(1)* máy hỏng chỉ **~8%** nên rất hiếm — **accuracy vô nghĩa, phải dùng F1/AUC-PR**; *(2)* học ở nhà máy A nhưng chấm ở nhà máy B khác điều kiện — **distribution shift**."

**S5 — Shift là gì** — "Distribution shift = dữ liệu lúc học khác lúc dùng, như học lái ở quê rồi ra thành phố. Mấu chốt: **cơ chế hỏng thì giống nhau A và B, chỉ các con số bị lệch** (covariate shift). Luật khó nhất: bị chấm trên B nhưng **cấm nhìn nhãn B**. ⇒ Chiến lược 3 bước: đo lệch → tạo đặc trưng miễn nhiễm → tinh chỉnh."

**S6 — Bản đồ đề** — "Bài bám đúng 5 phần chấm điểm. ⇒ Nhóm đầu tư nặng nhất vào xử lý shift và kết quả — nơi quyết định điểm."

**S7 — EDA 1.1** — "Máy hỏng ~7–8% ở cả hai. **Tỉ lệ hỏng gần như không đổi A→B** ⇒ cái lệch nằm ở **số đo đầu vào**, không phải ở nhãn — đúng covariate shift. Dữ liệu sạch: **0 thiếu, 0 trùng**. *(cue: chỉ bảng)* B nóng hơn, quay nhanh hơn; độ mòn dao gần như bằng."

**S8 — EDA 1.2** — "Định lượng: B nóng hơn +2–2,5°, dao động rộng hơn ~30%, quay nhanh +70 v/ph, lực xoắn thấp hơn 8,5%. *(cue: chỉ histogram)* Hai màu A/B **không trùng nhau = shift nhìn tận mắt**. Độ mòn dao là chỗ neo tin cậy."

**S9 — EDA 1.3–1.4** — "Dấu hiệu hỏng: độ mòn dao tách rõ nhất; các biến khác dồn về **hai đầu** (quá tải/thiếu tải) ⇒ tín hiệu **phi tuyến theo tổ hợp** → cần mô hình cây + feature engineering. Kiểm thêm: ca không lệch, loại SP có lệch; 2,8% máy B ngoài dải A (ghi Hạn chế). **[chuyển]** Em mời bạn Người 2."

---

## NGƯỜI 2 — Tiền xử lý, Đặc trưng & Đo shift (S10–S14, ~3')

**S10 — Divider Phần 2** — "Cảm ơn bạn. Em trình bày tiền xử lý, tạo đặc trưng và phát hiện shift."

**S11 — Phần 2.1** — "Chuẩn hoá số đo + mã hoá nhãn chữ. **Quy tắc vàng chống rò rỉ: chỉ học tham số chuẩn hoá trên A rồi áp cho cả hai — tuyệt đối không fit trên B** (⇒ vì sao: fit trên B = điểm ảo, triển khai thật sụp). Loại SP mã hoá thứ tự L<M<H, ca one-hot. Lớp hiếm: class_weight / scale_pos_weight ≈ 12,6. Tất cả gói trong Pipeline để fit lại đúng trong mỗi fold."

**S12 — Phần 2.2 (ý tưởng cốt lõi)** — "Đây là **ý tưởng cốt lõi**. Thay vì tích thô, nhóm mã hoá **'khoảng cách tới ngưỡng hỏng'** cho 3 cơ chế (tản nhiệt kém, quá/thiếu công suất, quá tải). ⇒ Vì sao hay: các ngưỡng là **hằng số vật lý bất biến A↔B** → 3 đặc trưng **miễn nhiễm shift**. Kiểm chứng bằng số: chỉ thêm 3 cột, LogReg mạnh gần **gấp đôi (AUC-PR 0,22→0,50)**."

**S13 — Phần 3.1 PSI/KS** — "Đo mức lệch bằng PSI/KS. Nhiệt độ lệch rất mạnh (PSI 1,08 / 0,55); **3 đặc trưng vật lý PSI ≈ 0** dù tạo từ chính biến đang lệch. *(cue: đọc ô cảnh báo)* **Lưu ý trung thực:** 2 đặc trưng hinge phần lớn = 0 nên PSI bị bão hoà về 0 → bằng chứng bất biến **chính** là drift-AUC 0,51 và bảng P(hỏng|cờ), không chỉ PSI. *(nêu điều này = ăn điểm hiểu sâu công cụ)*."

**S14 — Phần 3.2 Drift classifier** — "Huấn luyện mô hình đoán A/B chỉ từ số đo: dùng số đo thô AUC **0,82** (lệch mạnh, thủ phạm 2 biến nhiệt độ); chỉ 3 đặc trưng vật lý AUC **0,51** ≈ tung đồng xu → **tàng hình với shift**. Củng cố: tỉ lệ hỏng khi vượt ngưỡng giống nhau A/B (0,84 vs 0,83) ⇒ cơ chế bất biến. **[chuyển]** Em mời bạn Người 3."

---

## NGƯỜI 3 — Xử lý shift & Mô hình (S15–S20, ~3,5')

**S15 — Divider Phần 3** — "Cảm ơn bạn. Em trình bày xử lý shift và xây mô hình."

**S16 — Phần 3.3 Reweighting** — "Kỹ thuật #1 — **Importance Reweighting**: máy A nào giống B thì cho trọng số cao hơn khi học. ⇒ Vì sao **clip ≤ 10**: trọng số thô nổ tới ~57, phải chặn kẻo vài mẫu chi phối. Kết quả nhích nhẹ 0,669→0,672 — **và đó là tin tốt**: đặc trưng vật lý đã gánh gần hết việc chống lệch, reweighting chỉ vá phần nhỏ."

**S17 — Phần 3.4 IWV** — "Vấn đề đạo đức: chấm trên B nhưng cấm nhìn nhãn B. Giải pháp **IWV** — dùng dữ liệu A đánh trọng số cho 'giống B' → **bộ chấm thử giả lập B mà không cần nhãn B**. *(cue: chỉ đồ thị)* đường IWV bám sát đường B thật ⇒ harness đáng tin. Ngưỡng 0,5 không tối ưu lớp hiếm → chỉnh để F1 cao nhất. Lưu ý ESS 25,5% → có nhiễu, coi các bản đầu bảng là ngang nhau."

**S18 — Phần 4.1 Models** — "4 mô hình 3 trường phái: LogReg (mốc); RF & ExtraTrees (bagging, ổn định); XGBoost (boosting, mạnh nhưng dễ overfit A). Dò siêu tham số **RandomizedSearchCV + StratifiedKFold(5)**, chấm AUC-PR. ⇒ **Chọn model bằng IWV, không nhìn nhãn B.**"

**S19 — Phần 4.2 Bảng so sánh** — "*(cue: chỉ bảng)* Baseline 0,231 → +3 đặc trưng 0,352 → mô hình cây **nhảy vọt ~0,77** → bản gộp **0,781** (cao nhất). **F1 là số so sánh chính** theo đề. 'Báo đúng' = Precision, 'Bắt được' = Recall."

**S20 — Phần 4.3 Ensemble** — "Gộp mô hình vì mỗi cái sai chỗ khác nhau → bù trừ. Voting (RF+XGB 50/50) vs Stacking. ⇒ **Chốt Voting** (chọn bằng IWV): đơn giản, khó overfit shift; Stacking nghiêng nặng XGB — cái dễ gãy trên B. **[chuyển]** Em mời bạn Người 4."

---

## NGƯỜI 4 — Kết quả, Báo cáo & Kết luận (S21–S29, ~4')  *(chủ lực 2 tiêu chí Phần 5)*

**S21 — Divider Phần 4** — "Cảm ơn bạn. Em trình bày kết quả cuối, độ tin cậy và bài học."

**S22 — Kết quả** — "*(cue: chỉ 3 thẻ số)* Bản chốt gộp RF+XGB, ngưỡng 0,705 chọn bằng IWV: **F1 = 0,781, Recall ~75%, Precision ~81%**. *(cue: chỉ biểu đồ hành trình)* từ 0,231 lên 0,781 = **gấp 3,4 lần**. PR-curve nằm cao hơn hẳn 'đoán bừa' ⇒ mô hình thật sự có giá trị."

**S23 — Confusion matrix** — "*(cue: chỉ 4 ô)* Nhìn tường minh: TP bắt đúng máy hỏng; **FN — bỏ sót — tốn kém nhất** (máy dừng đột ngột); FP — báo động giả — rẻ hơn. Ở ngưỡng 0,705: Recall ~75%, Precision ~81%. ⇒ Vì FN đắt hơn nên **thực tế có thể hạ ngưỡng để tăng Recall**."

**S24 — Bootstrap** — "F1 lớp hiếm nhiễu (chỉ 477 máy hỏng) nên nhóm bootstrap 2000 lần: **F1 = 0,781, CI 95% [0,751; 0,809]**. Các bản đầu bảng chênh rất nhỏ → coi ngang nhau, **không thổi phồng hơn-kém**. So cặp: bản gộp thắng bản đơn 99,8% số lần nhưng biên độ nhỏ. *(nhấn: trung thực về thống kê)*."

**S25 — Phần 5.1 Insight**  *(← Tiêu chí 2)* — "Bài học vận hành: *(1)* **theo dõi độ mòn dao là ưu tiên #1** — vừa báo hỏng tốt vừa can thiệp được (thay dao); *(2)* **đặt cảnh báo theo ngưỡng vật lý** → dùng lại được khi đổi máy/nhà máy, không cần train lại; *(3)* bỏ sót đắt hơn báo động giả → **đề xuất 2 mức cảnh báo**: mức cao dừng máy kiểm tra ngay, mức thấp theo dõi/lên lịch bảo trì."

**S26 — Phần 5.2 Hạn chế & Cải tiến**  *(← Tiêu chí 2)* — "**Hạn chế** (trung thực): cây không ngoại suy (2,8% máy B ngoài dải A); giả định covariate-shift-thuần **chưa kiểm chứng được** vì thiếu nhãn B; ESS 25,5%; chỉ 5 số đo → có trần hiệu năng. **Cải tiến:** hiệu chỉnh ngưỡng công suất; thêm dữ liệu chuỗi thời gian; domain adaptation (CORAL); thu một ít nhãn B để kiểm chứng."

**S27 — Quyết định kỹ thuật & lý do**  *(← Tiêu chí 1)* — "*(cue: chỉ bảng)* Slide này tổng hợp **mọi quyết định kỹ thuật và lý do** — cho thấy bài có mạch logic chặt, không quyết định nào tuỳ tiện, và là bảng để nhóm **trả lời nhanh khi thầy/cô hỏi 'vì sao'**: dùng F1 vì lớp hiếm; 3 đặc trưng vật lý vì ngưỡng bất biến; chọn model bằng IWV để không rò rỉ; clip trọng số vì w thô nổ tới 57; chốt Voting vì đơn giản, khó overfit."

**S28 — Kết luận**  *(← Tiêu chí 2)* — "Tóm lại: chìa khoá là **bám quy luật vật lý bất biến** thay vì các con số thô đã lệch → mô hình học ở A vẫn chạy tốt trên B; mọi lựa chọn **trung thực qua IWV, không nhìn nhãn B**. Kết quả **F1 = 0,781, gấp 3,4 lần** baseline."

**S29 — Q&A** — "Nhóm em xin cảm ơn thầy/cô và sẵn sàng trả lời câu hỏi." *(cả nhóm đứng lên; trả lời theo ma trận dưới)*

---

## Ma trận phân công Q&A  (tra `NGAN_HANG_QA.md`)

| Người | Chịu trách nhiệm nhóm câu hỏi |
|---|---|
| **1** | **A** — Bài toán, dữ liệu, thước đo (vì sao F1 không accuracy, sạch dữ liệu…) |
| **2** | **B** — Phát hiện shift (PSI, sao PSI=0,0000, KS, drift classifier) · **C** — Feature engineering (vì sao đặc trưng biên, ngưỡng lấy đâu) |
| **3** | **D** — Xử lý shift & rò rỉ (reweighting, clip, IWV, "có nhìn nhãn B không") · **E** — Mô hình & ensemble (sao RF>XGB, sao Voting) |
| **4** | **F** — Đánh giá & độ tin cậy (bootstrap, CI, so cặp) · **G** — Vận hành & mở rộng (2 mức cảnh báo, đổi dây chuyền) · **H** — Câu chốt hạ |

> Nguyên tắc trả lời: **nói thẳng + có số + thừa nhận hạn chế khi cần**. Câu khó nhất đã có sẵn đáp án mẫu trong `NGAN_HANG_QA.md` (đặc biệt B3 "sao PSI=0,0000", D3 "có rò rỉ nhãn B không", F3 "bootstrap có công bằng không").

---

## Mẹo tổng khi trình bày (ăn điểm tiêu chí 1)
- Mỗi người **kết slide bằng một câu "⇒ vì sao"** — đó chính là "giải thích quyết định kỹ thuật".
- Nhắc lại đúng **3 lần** câu neo: *"chọn bằng IWV, không nhìn nhãn Test B"* (mở đầu, phần shift, kết luận).
- Bấm giờ: nếu quá giờ, **cắt ở slide phụ** (S6 bản đồ đề, S9 phần 1.4, S23 confusion matrix) — giữ nguyên S12 (đặc trưng), S14 (drift 0,51), S22 (kết quả), S25–28 (báo cáo).
