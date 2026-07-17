# Giải thích từng slide — hiểu sâu để trình bày & trả lời tự tin

> **Tài liệu học, KHÔNG phải để chiếu.** Mỗi slide giải thích 3 phần:
> **📌 Trên slide có gì** · **💡 Hiểu sâu (vì sao)** · **🔑 Con số / ý phải nhớ**.
> Deck: `SLIDE_THUYET_TRINH_v6.pptx` (28 slide) · Lời thoại: `SCRIPT_THUYET_TRINH_4NGUOI_v6.md`.

## Bức tranh lớn (đọc trước khi vào từng slide)

Bài toán: **đoán máy CNC nào sắp hỏng ở ca kế tiếp** — phân loại nhị phân, lớp hỏng **~8%** (rất hiếm).
Điểm xoắn não: **học ở nhà máy A (cũ) nhưng bị chấm ở nhà máy B (mới, nóng hơn, nhanh hơn)** — dữ liệu
lúc học ≠ lúc dùng (**distribution shift**), và **không được xem nhãn của B**.

Toàn bài xoay quanh **một ý tưởng cốt lõi**: thay vì để mô hình học các *con số thô* (đã bị lệch A→B),
ta tạo **4 đặc trưng neo vào ngưỡng vật lý của luật gây hỏng** — những ngưỡng này **không đổi giữa A và
B**, nên mô hình học ở A vẫn chạy tốt trên B. Kết quả: **F1 = 0,783** trên B (gấp 3,4 lần mô hình thô),
và bài chứng minh được đây là **trần** mà dữ liệu cho phép (~25% ca hỏng là nhiễu ngẫu nhiên).

Mạch 4 phần = 4 người: **① Bài toán & EDA · ② Đặc trưng & đo shift · ③ Xử lý shift & mô hình · ④ Kết quả & kết luận.**

---

# PHẦN 1 — Mở đầu & Khám phá dữ liệu (Người 1, S1–S8)

## Slide 1 — Trang tiêu đề
**📌 Trên slide:** Tên đề tài + 4 con số lớn: F1 = **0,783** · **3,4×** so với baseline · **~8%** máy hỏng · **0** lỗi khi chạy notebook.
**💡 Hiểu sâu:** 4 con số này là "trailer" của cả bài — nói ngay kết quả (0,783), mức cải thiện (3,4×), độ khó (lớp hiếm 8%), và tính nghiêm túc kỹ thuật (chạy full không lỗi). Người nghe nắm được "bài này làm gì, tốt cỡ nào" chỉ trong 10 giây.
**🔑 Nhớ:** F1 là **thước đo chính** (không phải accuracy). 0,783 là điểm trên **nhà máy B** — tập chưa từng thấy.

## Slide 2 — Nội dung (Agenda)
**📌 Trên slide:** 4 khối tương ứng 4 người.
**💡 Hiểu sâu:** Hai khối **nặng điểm nhất** theo rubric là **Xử lý shift (2đ)** và **Kết quả trên B (3đ)** — nhắc để giám khảo biết bài bám sát thang điểm.
**🔑 Nhớ:** Chuyển người ở 4 slide "Divider": S3, S9, S14, S20.

## Slide 3 — Divider Phần 1
**📌 Trên slide:** Tiêu đề "Mở đầu & Khám phá dữ liệu".
**💡 Hiểu sâu:** Slide ngăn cách, chỉ để chuyển mạch. Không có nội dung kỹ thuật.

## Slide 4 — Bài toán
**📌 Trên slide:** Mô tả bài toán + dữ liệu (5 số đo + 2 nhãn phân loại) + **2 thách thức cốt lõi**: ① lớp hiếm ~8% → cấm accuracy; ② 2 nhà máy khác nhau → distribution shift.
**💡 Hiểu sâu:** Đây là slide "khung xương". Hai thách thức này **quyết định mọi lựa chọn kỹ thuật về sau**:
- Vì lớp hiếm → dùng **F1/AUC-PR**, phạt nặng bỏ sót (class_weight), không dùng accuracy.
- Vì shift → tạo **đặc trưng bất biến** + reweighting + chọn model bằng IWV.
5 số đo: nhiệt độ môi trường, nhiệt độ máy, tốc độ quay, mômen (lực xoắn), độ mòn dao. 2 nhãn: loại sản phẩm (L/M/H), ca làm việc.
**🔑 Nhớ:** "Đoán bừa *không hỏng* vẫn đúng 92% nhưng vô dụng" — đây là lý do **1 câu** giết chết accuracy.

## Slide 5 — Vì sao khó?
**📌 Trên slide:** Định nghĩa distribution shift + ví von "học lái đường quê, chạy trong phố" + **may mắn** (quy luật hỏng giống nhau, chỉ con số lệch) + cái khó nhất (bị chấm trên B nhưng cấm xem đáp án B) + **chiến lược 3 bước**.
**💡 Hiểu sâu:** Slide này gieo **toàn bộ chiến lược** của bài:
1. **Đo** mức lệch (PSI, KS, drift classifier) — Phần 2.
2. **Tạo đặc trưng miễn nhiễm lệch** (neo ngưỡng vật lý) — Phần 2, đây là át chủ bài.
3. **Tinh chỉnh** (reweighting, threshold, ensemble) — Phần 3.
Chi tiết vàng: "quy luật *nguyên nhân* gây hỏng giống nhau A/B, chỉ *các con số* lệch" — đây chính là định nghĩa **covariate shift**, và là lý do vì sao đặc trưng-theo-ngưỡng lại hiệu quả.
**🔑 Nhớ:** "Xem nhãn B = gian lận (rò rỉ)" → mọi lựa chọn phải chọn bằng **IWV**, không nhìn B.

## Slide 6 — Máy hỏng hiếm cỡ nào (Phần 1.1)
**📌 Trên slide:** A: 7,36% hỏng (1031/14000), B: 7,95% (477/6000). Bảng trung bình/độ lệch 5 số đo A vs B. Dữ liệu sạch (0 thiếu, 0 trùng).
**💡 Hiểu sâu:** Điểm mấu chốt: **tỉ lệ hỏng gần như không đổi** (7,4%→8,0%). Điều này chứng minh cái lệch nằm ở **đầu vào** (số đo) chứ **không** ở nhãn — tức đúng là **covariate shift** (P(x) đổi, tỉ lệ nhãn ổn định). Nếu tỉ lệ hỏng cũng đổi mạnh thì reweighting sẽ vô hiệu; ở đây nó ổn định nên reweighting là công cụ hợp lệ.
Nhìn bảng: nhiệt độ B **cao hơn và tản rộng hơn**, tốc độ B **nhanh hơn**, mômen B **thấp hơn**, riêng **độ mòn dao gần y hệt** (127 vs 127).
**🔑 Nhớ:** Tỉ lệ hỏng ổn định → **covariate shift** → hợp với importance reweighting. Độ mòn dao = biến ổn định nhất (chỗ neo tin cậy).

## Slide 7 — Hai nhà máy lệch thế nào (Phần 1.2)
**📌 Trên slide:** Bảng "B so với A" + **histogram 5 số đo A (xanh) vs B (đỏ)**.
**💡 Hiểu sâu:** Đây là shift **nhìn tận mắt**: trên histogram, hai màu A/B **không trùng nhau** ở nhiệt độ (lệch mạnh) nhưng **trùng khít** ở độ mòn dao (ổn định). Trực quan hoá này chuẩn bị cho lập luận Phần 2: "biến thô lệch, nhưng đặc trưng dựng từ ngưỡng thì không lệch".
**🔑 Nhớ:** Nhiệt độ môi trường +2,5° (rộng hơn ~29%), nhiệt độ máy +1,9°, tốc độ +70 v/ph, mômen thấp hơn 8,5%, **mòn dao ≈ bằng nhau**.

## Slide 8 — Dấu hiệu hỏng & vùng lạ (Phần 1.3–1.4)
**📌 Trên slide:** (trái) phân bố theo nhãn — mòn dao hỏng ~177 vs lành ~123; (phải) ma trận tương quan. + ghi chú: ca làm việc không lệch (p=0,54), loại SP có lệch (p<0,001), **2,8% máy B ngoài dải A**.
**💡 Hiểu sâu:** Ba ý:
1. **Độ mòn dao** là tín hiệu tuyến tính rõ nhất (hỏng dồn mức mòn cao).
2. Các biến khác **tương quan tuyến tính ≈ 0 nhưng KHÔNG vô dụng**: tốc độ hỏng dồn đuôi **thấp**, mômen dồn **cả hai đầu** (quá/thiếu tải) → quan hệ **phi tuyến** → cần mô hình cây + đặc trưng khéo (báo trước Phần 2).
3. **2,8% máy B nằm ngoài dải giá trị của A** → mô hình cây (không ngoại suy được) dễ sai ở vùng lạ → ghi vào **Hạn chế** (trung thực).
**🔑 Nhớ:** "Tương quan tuyến tính ≈ 0 nhưng phi tuyến có tín hiệu" là lý do vì sao LogReg thô thất bại còn cây thắng. 2,8% ngoài dải A = hạn chế đã nêu.

---

# PHẦN 2 — Tiền xử lý, Đặc trưng & Phát hiện shift (Người 2, S9–S13)

## Slide 9 — Divider Phần 2
Slide ngăn cách. Giới thiệu: chuẩn hoá chống rò rỉ, **4 đặc trưng vật lý**, đo shift bằng PSI/KS + drift classifier.

## Slide 10 — Chuẩn bị dữ liệu, chống rò rỉ (Phần 2.1)
**📌 Trên slide:** Chuẩn hoá (cho model tuyến tính) · **quy tắc vàng: fit chỉ trên A** · mã hoá Ordinal (L<M<H) / One-Hot (ca) · phạt lớp hiếm (class_weight ≈ 12,6, không SMOTE) · gói Pipeline fit-lại-mỗi-fold.
**💡 Hiểu sâu:** Slide về **kỷ luật chống rò rỉ (leakage)** — điều đề nhấn mạnh. Nếu học cách chuẩn hoá/mã hoá bằng cả dữ liệu B (kể cả chỉ mean/std của B), điểm sẽ **đẹp giả** rồi sụp khi dùng thật. **Pipeline** đảm bảo mọi phép biến đổi được **fit lại chỉ trên phần train của mỗi fold**.
Vì sao Ordinal cho loại SP mà không One-Hot? Vì L<M<H **có thứ tự** (độ cứng tăng dần) — giữ thứ tự giúp model hiểu quan hệ. Ca làm việc không thứ tự → One-Hot (tách cột).
Vì sao **không SMOTE**? SMOTE chế "máy hỏng giả" bằng nội suy — dưới shift dễ tạo điểm **phi vật lý**. Thay vào đó dùng class_weight (phạt nặng bỏ sót, ~12,6 = tỉ lệ lành/hỏng).
**🔑 Nhớ:** Rò rỉ = dùng thông tin B khi học. Pipeline + fit-chỉ-trên-A = tấm khiên chống rò rỉ.

## Slide 11 — Bốn đặc trưng vật lý (Phần 2.2) ⭐ SLIDE QUAN TRỌNG NHẤT
**📌 Trên slide:** Bảng 4 đặc trưng (công thức + ý nghĩa + kiểu hỏng) + "vì sao hay" (ngưỡng là hằng số cơ chế) + kiểm chứng (AUC-PR 0,22→0,65).
**💡 Hiểu sâu:** Đây là **ý tưởng cốt lõi cả bài**. Mỗi đặc trưng đo "**máy còn cách ngưỡng hỏng bao xa**" bằng hàm **hinge** (`max(·,0)` — chỉ "bật" khi vào vùng nguy):
- `nguy_tan_nhiet` = max(8,6−ΔT,0) × max(1380−tốc,0) → cơ chế **HDF** (tản nhiệt kém): cần **đồng thời** chênh nhiệt nhỏ VÀ quay chậm → **nhân 2 hinge** = phép AND.
- `lech_cong_suat` = max(2600−P,0) + max(P−11500,0) → cơ chế **PWF**: hỏng ở **cả hai đuôi** công suất (quá cao *hoặc* quá thấp).
- `bien_overstrain` = mòn×mômen − ngưỡng(loại SP) → cơ chế **OSF** (quá tải): biên **có dấu** theo từng loại → đây là lý do biến `loại SP` (tưởng vô dụng) **thực ra là ngưỡng của luật**.
- `mon_twf` = max(mòn−244,0) → cơ chế **TWF** (mòn dao): corr với hỏng **0,43** — mạnh nhất bảng.
**Vì sao đây là đòn chống shift mạnh nhất:** các ngưỡng (8,6°/1380/2600–11500/244) là **thuộc tính cơ chế của máy**, không phải thống kê của A → `P(hỏng | vượt ngưỡng)` **bất biến** A→B. Ta biến các trục **dịch mạnh nhất** (nhiệt độ, tốc độ) thành **tín hiệu ổn định**.
**🔑 Nhớ:** 4 đặc trưng = 4 cơ chế hỏng HDF/PWF/OSF/TWF. Thêm 4 cột này, AUC-PR nhảy 0,22→0,65 (gấp ~3). Chi tiết "vì sao chọn ngưỡng" → xem mục riêng cuối script.

## Slide 12 — Đo shift bằng PSI/KS (Phần 3.1)
**📌 Trên slide:** Bảng PSI + KS-D cho từng số đo + lưu ý trung thực (hinge bão hoà về 0).
**💡 Hiểu sâu:** **PSI** và **KS** là 2 thước đo độ lệch một biến giữa A và B. Kết quả:
- Nhiệt độ môi trường PSI **1,08** (rất mạnh), nhiệt độ máy 0,55 (mạnh) → **thủ phạm shift**.
- Tốc độ/mômen: lệch nhẹ. Độ mòn dao: ~0 (ổn định).
- **4 đặc trưng vật lý: PSI ≈ 0** — dù chúng được dựng **từ chính** nhiệt độ & tốc độ đang lệch mạnh! Đây là **bằng chứng số** cho ý tưởng chính.
**Lưu ý trung thực (điểm cộng):** 3/4 đặc trưng là hinge nên phần lớn giá trị = 0 → PSI dễ "bão hoà" về 0. Vì thế nhóm **không chỉ dựa PSI** mà còn chứng minh bất biến bằng **drift-AUC** (S13) và **bảng P(hỏng|cờ)** — đa bằng chứng.
**🔑 Nhớ:** PSI < 0,1 không lệch · 0,1–0,25 nhẹ · > 0,25 mạnh. Nhiệt độ MT 1,08 = thủ phạm số 1. Đặc trưng vật lý ≈ 0.

## Slide 13 — Shift nằm ở đâu? Drift Classifier (Phần 3.2)
**📌 Trên slide:** Mẹo huấn luyện model đoán "A hay B" + **AUC 0,82** (dùng số thô) vs **AUC 0,53** (chỉ 4 đặc trưng) + biểu đồ cột importance (2 nhiệt độ đỏ ~58%).
**💡 Hiểu sâu:** **Drift classifier** = huấn luyện một model chỉ để đoán mẫu thuộc A hay B. Nếu nó đoán **dễ** → hai nhà máy khác nhau nhiều.
- Dùng **tất cả số đo** → AUC **0,82** (phân biệt A/B rất tốt = shift mạnh).
- Chỉ dùng **4 đặc trưng vật lý** → AUC **0,53** ≈ tung đồng xu → gần như **không phân biệt được A/B**.
→ Kết luận đắt giá: **toàn bộ shift nằm ở biến thô; đặc trưng vật lý "trong suốt" với shift**. Biểu đồ importance cho thấy 2 biến nhiệt độ chiếm ~58% = thủ phạm chính.
**Ba lát cắt** (PSI, drift-AUC, importance) cùng một kết luận → rất thuyết phục.
**🔑 Nhớ:** AUC 0,5 = không lệch, 1 = khác hẳn. Thô = 0,82, đặc trưng vật lý = 0,53. Đây là bằng chứng **định lượng** cho "đặc trưng miễn nhiễm shift".

---

# PHẦN 3 — Xử lý shift & Xây mô hình (Người 3, S14–S19)

## Slide 14 — Divider Phần 3
Ngăn cách. Giới thiệu: reweighting, chọn ngưỡng bằng IWV, so 4 mô hình + ensemble.

## Slide 15 — Xử lý lệch bằng trọng số (Phần 3.3)
**📌 Trên slide:** Ý tưởng Importance Reweighting + clip trọng số ≤ 10 + kết quả gần như đứng yên (F1 giữ 0,783; AUC-PR 0,675→0,671).
**💡 Hiểu sâu:** **Reweighting**: máy A nào **trông giống B** thì cho "điểm chú ý" cao hơn khi học → model học nghiêng về B. Điểm chú ý = **mức giống B / mức giống A** (density-ratio, lấy từ drift classifier). Phải **clip ≤ 10** vì vài máy A rất hiếm ở vùng B sẽ có trọng số **nổ tới ~77** → chi phối toàn bộ.
**Điểm tinh tế:** kết quả **gần như không đổi** — và đó là **tin tốt**! Vì **4 đặc trưng vật lý đã hấp thụ gần hết shift** (drift-AUC đặc trưng chỉ 0,53), nên reweighting chỉ còn "vá phần nhỏ" còn sót. Đây **định lượng khẳng định**: làm đúng đặc trưng thì đỡ phải bù shift bằng thống kê.
**🔑 Nhớ:** Gain nhỏ = tin tốt (đặc trưng đã gánh phần nặng). Trọng số nổ ~77 → clip [0,2 ; 10]. Vẫn giữ reweighting làm minh chứng "kỹ thuật xử lý shift" (rubric).

## Slide 16 — Chọn ngưỡng trung thực bằng IWV (Phần 3.4)
**📌 Trên slide:** Nghịch lý chấm điểm + **IWV** + chỉnh ngưỡng báo hỏng (mặc định 0,5 không tối ưu) + ESS ≈ 24,2%.
**💡 Hiểu sâu:** **Nghịch lý**: bị chấm trên B nhưng cấm xem nhãn B → chọn model/ngưỡng bằng gì? **IWV (Importance-Weighted Validation)**: chấm thử trên dữ liệu A **đã đánh trọng số density-ratio** → tạo một bộ validation "**giả lập B**" mà **không cần nhãn B**. Nhờ đó thử-sai bao nhiêu cũng không gian lận; nhãn B chỉ dùng **1 lần cuối**.
**Chỉnh ngưỡng:** ngưỡng mặc định 0,5 không hợp lớp hiếm → dò trên IWV, chốt **0,585** cho F1 cao nhất.
**ESS (số mẫu hiệu dụng) = 24,2%:** sau khi đánh trọng số, do vài mẫu nặng ký lấn át, dữ liệu thật sự có ích chỉ còn ~24% của 14.000 → ước lượng IWV **nhiễu** → các bản điểm sát nhau coi như **ngang nhau** (không khoe hơn-kém vặt).
**🔑 Nhớ:** IWV = "tự chấm điểm như thể đứng ở B mà không nhìn đáp án B". Đây là **chốt kỷ luật** của cả bài — nhắc lại ở S27.

## Slide 17 — Thử 4 mô hình, chấm công bằng (Phần 4.1)
**📌 Trên slide:** 4 mô hình / 3 trường phái + RandomizedSearchCV + StratifiedKFold 5 + chấm bằng F1/AUC-PR.
**💡 Hiểu sâu:** 4 base thuộc **3 trường phái khác nhau** (để lát gộp ensemble cho đa dạng):
- **Logistic Regression** — tuyến tính, làm mốc.
- **Random Forest & ExtraTrees** — "nhiều cây bỏ phiếu", **variance thấp** (ổn định).
- **XGBoost** — "nhiều cây sửa lỗi nối tiếp", mạnh nhưng dễ **học thuộc lòng A**.
Dò siêu tham số **tự động** (RandomizedSearchCV) + **StratifiedKFold 5** (chia 5 phần, giữ đúng tỉ lệ ~8% hỏng mỗi phần). Đủ yêu cầu đề: **≥3 mô hình + tuning + K-Fold**.
**🔑 Nhớ:** 3 trường phái = đa dạng để ensemble. Chọn model **bằng IWV**, B chỉ chấm 1 lần cuối.

## Slide 18 — Bảng so sánh (Phần 4.2)
**📌 Trên slide:** Bảng 8 dòng từ LogReg thô → bản chốt v6, cột AUC-ROC/AUC-PR/F1/P/R.
**💡 Hiểu sâu:** Đọc theo cột **F1** (số so sánh chính):
| Bản | F1 | Ý nghĩa |
|---|---|---|
| LogReg thô | 0,231 | Baseline, gần như vô dụng |
| +4 đặc trưng | 0,716 | **Nhảy vọt** — đặc trưng gánh phần nặng |
| Random Forest | **0,783** | Cây khai thác nốt phi tuyến |
| +reweighting / +ngưỡng | 0,783 | Giữ ổn định |
| GỘP (v6) | **0,783** | Bản chốt |
**Câu chuyện quan trọng:** từ v2 (RF) trở đi **mọi bản đều hội tụ 0,783** — dấu hiệu đã **chạm trần dữ liệu** (giải thích ở S25). Đây không phải model yếu mà là giới hạn thông tin của dữ liệu.
**Giải thích thuật ngữ cột:** **AUC-PR** = diện tích dưới đường Precision-Recall (đoán bừa chỉ ~0,08 nên 0,67 rất tốt); **AUC-ROC** = xác suất chấm máy hỏng cao hơn máy lành (0,5 ngẫu nhiên, 1 hoàn hảo).
**🔑 Nhớ:** Hành trình 0,231 → 0,783 = **gấp 3,4 lần**. Từ v2 hội tụ 0,783 = chạm trần.

## Slide 19 — Ensemble (Phần 4.3)
**📌 Trên slide:** Voting (RF 25% + ExtraTrees 25% + XGBoost 50%) vs Stacking + chọn Voting bằng IWV.
**💡 Hiểu sâu:** **Ensemble** = gộp nhiều model vì chúng **sai ở chỗ khác nhau** → gộp lại thì bù trừ, ổn định hơn.
- **Voting** = trung bình **có trọng số** dự đoán (trọng số RF 0,25 / ET 0,25 / XGB 0,5 dò bằng IWV).
- **Stacking** = một model nhỏ (meta) học cách **trộn** kết quả 4 model con.
IWV chấm hai bản **ngang điểm** → chốt **Voting** vì đơn giản, khó sai, **khó overfit shift** hơn Stacking (Stacking dễ nghiêng nặng về XGB — cái dễ gãy trên B).
**🔑 Nhớ:** Voting = trung bình có trọng số; Stacking = model trộn. Chốt Voting vì đơn giản & robust. Bản chốt v6 = Voting RF+ET+XGB.

---

# PHẦN 4 — Kết quả, Độ tin cậy & Kết luận (Người 4, S20–S28)

## Slide 20 — Divider Phần 4
Ngăn cách. Giới thiệu: kết quả cuối trên B, confusion matrix, bootstrap, insight & hạn chế.

## Slide 21 — Kết quả cuối trên B (3 điểm)
**📌 Trên slide:** F1 = **0,783** · Recall ~75% · Precision 4/5 (~82%) + PR-curve.
**💡 Hiểu sâu:** Đây là **ô 3 điểm** của rubric — kết quả thật trên **phân phối đích** (nhà máy B, chưa từng thấy). Đọc số: bắt được **~75%** máy sắp hỏng, và **4/5 cảnh báo là đúng**. Đường PR của v6 cao hơn hẳn đường "đoán bừa" (baseline ~0,08).
**🔑 Nhớ:** 0,783 / R 75% / P 82% trên B. Đây là con số "ăn điểm" chính.

## Slide 22 — Ma trận nhầm lẫn (Confusion matrix)
**📌 Trên slide:** Bảng 2×2 tại ngưỡng 0,585 + cách đọc TP/TN/FP/FN + đánh đổi FN↔FP.
**💡 Hiểu sâu:** Tại ngưỡng **0,585** trên B:
- **TP = 358** (bắt đúng máy hỏng — mục tiêu)
- **FN = 119** (bỏ sót máy hỏng — **tốn kém nhất**, máy dừng đột ngột)
- **FP = 80** (báo động giả — chỉ tốn công kiểm tra, rẻ hơn FN)
- **TN = 5443** (đúng máy lành)
Vì **FN đắt hơn FP**, ta có thể **hạ ngưỡng để tăng Recall** (bắt nhiều máy hỏng hơn, chấp nhận thêm báo động giả) tuỳ chi phí thực tế nhà máy.
**🔑 Nhớ:** TP 358 / FN 119 / FP 80 / TN 5443. FN (bỏ sót) đắt hơn FP (báo nhầm) → có thể hạ ngưỡng.

## Slide 23 — Bootstrap (độ tin cậy)
**📌 Trên slide:** Chỉ 477 máy hỏng → F1 có sai số → **bootstrap 2000 lần** → F1 = 0,783, 95% CI [0,753 ; 0,811].
**💡 Hiểu sâu:** Vì tập B chỉ có **477 máy hỏng**, con số F1 có **sai số** — phải báo khoảng tin cậy. **Bootstrap** = bốc lại mẫu (có hoàn lại) 2000 lần, mỗi lần tính F1, xem nó dao động cỡ nào.
- F1 = 0,783, **95% CI [0,753 ; 0,811]** (rộng ±0,03).
- Các bản đầu bảng (0,767–0,783) chênh rất nhỏ, CI **chồng lấn** → coi như **ngang nhau**, **không khoe hơn-kém** vặt.
- Nhưng so **cặp** (cùng resample): bản gộp thắng bản đơn **100% số lần**, chênh trung bình **+0,015** → nhỉnh **nhất quán về hướng** nhưng **biên độ nhỏ**. Đây là kết luận **trung thực**.
**🔑 Nhớ:** 477 mẫu hỏng → CI rộng → không thổi phồng chênh lệch nhỏ. So cặp: v6 > XGB đơn 100% số lần nhưng chỉ +0,015.

## Slide 24 — Insight vận hành (Phần 5.1)
**📌 Trên slide:** 3 rút ra + đề xuất 2 mức cảnh báo.
**💡 Hiểu sâu:** Chuyển từ "điểm số" sang "giá trị thực tế cho nhà máy":
1. **Theo dõi độ mòn dao là số 1** — vừa báo hỏng tốt, vừa **can thiệp được** (thay dao). Luật TWF khôi phục được (mòn > 244) cho thẳng **ngưỡng thay dao**.
2. **Đặt cảnh báo theo ngưỡng vật lý** — dùng lại được cả khi **đổi máy/đổi nhà máy** (vì ngưỡng bất biến), không cần học lại.
3. Cân nhắc bỏ sót ↔ báo động giả → đề xuất **2 mức cảnh báo**: mức cao (chắc chắn) → dừng máy kiểm tra ngay; mức thấp (nghi ngờ) → theo dõi/lên lịch bảo trì.
**🔑 Nhớ:** Mòn dao = vừa dự báo vừa can thiệp được → ưu tiên #1. Ngưỡng vật lý = tái sử dụng khi đổi máy.

## Slide 25 — Hạn chế & Hướng cải tiến (Phần 5.2)
**📌 Trên slide:** 4 hạn chế + 4 hướng cải tiến (mục 1 đã làm).
**💡 Hiểu sâu:** **Hạn chế** (nêu trung thực):
- Cây **không ngoại suy** được → 2,8% máy B ngoài dải A dễ sai.
- Giả định "cơ chế hỏng không đổi" **chưa kiểm chứng 100%** (không có nhãn B).
- **ESS 24,2%** → độ tin IWV giới hạn.
- **~25% ca hỏng là nhiễu ngẫu nhiên** (không khớp luật nào) → **trần F1 ≈ 0,78 đã được định lượng** (Phụ lục A). Đây là câu trả lời cho "sao không cao hơn nữa?": **không phải model yếu, mà dữ liệu chỉ cho phép đến đó**.
**Hướng cải tiến:** mục 1 (khôi phục luật sinh nhãn từ A) **đã làm** → precision luật 0,26→0,81, F1 0,781→0,783; còn lại: đặc trưng theo thời gian, domain adaptation (CORAL/adversarial), thu thập ít nhãn B.
**🔑 Nhớ:** Trần ≈ 0,78 vì ~25% ca hỏng là nhiễu → chạm trần, không phải model yếu. Đây là **vũ khí** trả lời "sao không ≥0,80".

## Slide 26 — Quyết định kỹ thuật & lý do
**📌 Trên slide:** Bảng 8 quyết định + lý do.
**💡 Hiểu sâu:** Slide "phòng thủ" — chứng minh **mọi lựa chọn đều có lý do**, không tuỳ tiện. Mỗi dòng là một cặp *quyết định → vì sao*: dùng F1 (lớp hiếm), 4 đặc trưng neo ngưỡng cơ chế (bất biến), cây (phi tuyến), không SMOTE (tránh mẫu giả), chọn model bằng IWV (chống rò rỉ), clip trọng số (chặn mẫu cá biệt), Voting (đơn giản & robust), bootstrap (không thổi phồng).
**🔑 Nhớ:** Đây là slide để trả lời "vì sao chọn X?" — mỗi lựa chọn có 1 câu lý do sẵn.

## Slide 27 — Kết luận
**📌 Trên slide:** 4 ý: Chìa khoá · Nhờ đó · Trung thực · Kết quả.
**💡 Hiểu sâu:** Đóng bài bằng 4 câu đọng lại:
1. **Chìa khoá**: bám quy luật vật lý không đổi thay vì con số thô đã lệch.
2. **Nhờ đó**: model học ở A vẫn chạy tốt trên B.
3. **Trung thực**: mọi lựa chọn chọn bằng IWV, không nhìn đáp án B.
4. **Kết quả**: F1 = 0,783, gấp 3,4 lần baseline — chạm trần dữ liệu cho phép.
**🔑 Nhớ:** Nhấn lại cụm "chọn bằng IWV — không nhìn nhãn B" (đây là điểm khác biệt của bài).

## Slide 28 — Q&A
Slide hỏi đáp. Xem **ma trận phân công Q&A** và **bảng thuật ngữ** ở cuối script.

---

## Sơ đồ nhân-quả toàn bài (một hình để nhớ)

```
Lớp hiếm 8%  ──►  cấm accuracy, dùng F1/AUC-PR + class_weight
Shift A→B    ──►  đo (PSI/KS/drift) ──► shift nằm ở BIẾN THÔ (drift-AUC 0,82)
                          │
                          ▼
          4 đặc trưng neo NGƯỠNG VẬT LÝ (khôi phục từ A)
          → drift-AUC còn 0,53 (miễn nhiễm shift)  ◄── át chủ bài
                          │
                          ▼
   reweighting + threshold + ensemble (đều chọn bằng IWV, không nhìn B)
                          │
                          ▼
              F1 = 0,783 trên B  (chạm trần ~0,78 vì 25% ca hỏng là nhiễu)
```

## 5 câu "phòng thủ" hay bị hỏi nhất
1. **Sao không dùng accuracy?** → Lớp hỏng 8%, đoán bừa "không hỏng" đã 92% mà Recall = 0 → vô dụng.
2. **Ngưỡng 2600/244… ở đâu ra?** → Quét trên A tìm chỗ tỉ lệ hỏng vọt lên; kiểm chứng bất biến sang B (xem mục riêng trong script).
3. **Reweighting sao gain ~0?** → Đặc trưng vật lý đã hấp thụ gần hết shift (drift-AUC đặc trưng 0,53) → dư địa nhỏ. Đó là tin tốt.
4. **Sao không ≥0,80?** → ~25% ca hỏng là nhiễu ngẫu nhiên → trần ≈0,78; oracle biết trước B cũng chỉ ~0,78; ≥0,80 chỉ có thể bằng leakage.
5. **Chống rò rỉ thế nào?** → Fit scaler/encoder chỉ trên A, gói Pipeline fit-lại-mỗi-fold; chọn model/ngưỡng bằng IWV, nhãn B chỉ chấm 1 lần cuối.
