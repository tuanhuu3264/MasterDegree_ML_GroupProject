# 🎓🍜 Giải thích 2 phiên bản — Học thuật & Dễ hiểu cho người mới

> Mỗi khái niệm quan trọng trong đề được trình bày **song song 2 phiên bản**:
> - 🎓 **Học thuật:** định nghĩa chuẩn + công thức (để viết báo cáo, bảo vệ).
> - 🍜 **Dễ hiểu:** ví von đời thường + ví dụ số thật (để nắm ý tưởng nhanh).
>
> Bối cảnh xuyên suốt: máy học ở **nhà máy cũ (A, mát)**, đem chạy ở **nhà máy mới (B, nóng)**.

---

## 1. Distribution Shift (dịch chuyển phân phối)

🎓 **Học thuật**
> Phân phối dữ liệu lúc triển khai khác lúc huấn luyện: $P_{train}(x,y)\neq P_{test}(x,y)$. Hệ quả: bộ ước lượng tối ưu trên $P_{train}$ **không** còn tối ưu trên $P_{test}$, gây suy giảm hiệu năng khi triển khai.

🍜 **Dễ hiểu**
> Bạn **luyện thi bằng đề trường A** suốt 2 năm, nhưng hôm thi lại là **đề trường B** ra theo kiểu khác. Kiến thức gốc giống nhau, nhưng "phong cách đề" đổi → điểm tụt nếu không thích nghi.
>
> **Ví dụ số thật:** nhiệt độ môi trường trung bình A = **300.0 K** → B = **302.5 K** (nóng hơn 2.5 độ). Máy được học ở điều kiện mát, giờ chạy ở nơi nóng → dễ dự đoán sai.

---

## 2. Covariate Shift vs Concept Drift

🎓 **Học thuật**
> - **Covariate shift:** $P(x)$ đổi nhưng quy luật $P(y\mid x)$ **giữ nguyên**.
> - **Concept drift:** chính quy luật $P(y\mid x)$ đổi.
> Bài này là **covariate shift** (đã kiểm chứng: xác suất hỏng theo cùng một cơ chế vật lý HDF 0.84→0.83 gần như bất biến giữa A và B).

🍜 **Dễ hiểu**
> - **Covariate shift = "đề hỏi vùng khác nhưng luật chấm không đổi".** Thầy vẫn chấm y hệt, chỉ là đề B hỏi nhiều vào phần bạn ít ôn.
> - **Concept drift = "luật chấm đổi".** Cùng một bài làm, hôm nay thầy cho 8 điểm, mai thầy cho 5.
>
> Ở máy phay: **luật vật lý gây hỏng không đổi** (nóng quá + quay chậm → hỏng), chỉ **điều kiện vận hành đổi** → đây là covariate shift. Vì vậy ta chỉ cần "cân lại dữ liệu", không phải học lại luật.

---

## 3. Target Imbalance (mất cân bằng lớp)

🎓 **Học thuật**
> Tỷ lệ lớp dương $\pi_+ = P(y=1)\ll 0.5$. Khi đó *accuracy* mất ý nghĩa vì bộ phân loại hằng số ($\hat y=0$) đạt accuracy $=1-\pi_+$ nhưng recall $=0$. Cần metric nhạy lớp thiểu số (F1, AUC-PR).

🍜 **Dễ hiểu**
> Trong **100 sản phẩm chỉ ~7 cái hỏng**. Nếu bạn "nhắm mắt đoán tất cả đều tốt" → đúng **93%** nghe rất oách, nhưng **không bắt được cái hỏng nào** → vô dụng cho bảo trì!
>
> **Ví dụ số thật:** Train có 1031 hỏng / 14000 = **7.36%** → tỷ lệ **12.6 tốt : 1 hỏng**. *(Đề ghi 3–5% nhưng thực tế 7–8% → phải dùng số thật.)*

---

## 4. Scaling & Data Leakage ("fit trên Train, transform cả hai")

🎓 **Học thuật**
> Chuẩn hoá $z=\frac{x-\mu}{\sigma}$ với $(\mu,\sigma)$ **ước lượng chỉ trên Train**, rồi áp cho cả Train/Test. Nếu ước lượng trên Test (hoặc Train∪Test) sẽ gây **data leakage** → đánh giá lạc quan chệch và làm méo thông tin shift.

🍜 **Dễ hiểu**
> Giống **chấm điểm theo đường cong (curve)** dựa trên lớp A. Khi chấm lớp B, bạn phải dùng **"thước đo của lớp A"** — **không được lén nhìn điểm lớp B trước** rồi mới lập thước (đó là ăn gian = leakage).
>
> **Điểm hay:** sau khi đo bằng thước của A, điểm lớp B **không** trung bình 0 (vì B giỏi/nóng hơn) — **đúng như vậy!** Cái "lệch" đó chính là shift ta cần giữ để phát hiện.

---

## 5. Feature Engineering (tạo đặc trưng có ý nghĩa cơ học)

🎓 **Học thuật**
> Biến đổi feature thô thành đặc trưng phản ánh **cơ chế sinh nhãn phi tuyến**, giúp mô hình (đặc biệt tuyến tính) biểu diễn được biên quyết định. VD công suất cơ $P=\tau\cdot\omega$ với $\omega=\frac{2\pi\cdot\text{rpm}}{60}$.

🍜 **Dễ hiểu**
> Bác sĩ không chỉ nhìn **cân nặng** và **chiều cao** riêng lẻ, mà tính **BMI = cân/cao²** — một con số "biết nói" hơn. Tương tự, ta tính:
> - **Chênh lệch nhiệt** = nhiệt quy trình − nhiệt môi trường → đo "tản nhiệt tốt hay kém".
> - **Công suất** = mômen × tốc độ → đo "máy có bị quá tải không".
>
> - **`osf_margin`** = mòn×momen − ngưỡng theo hạng SP → đo "đã vượt quá tải căng thẳng chưa" (**feature mạnh nhất tự tạo**).
>
> **Ví dụ số thật (dòng đầu Train):** công suất $= 47.52 \times 1864.3 \times \frac{2\pi}{60} = \mathbf{9277\ W} > 9000$ → **vượt ngưỡng an toàn** → máy này có nguy cơ hỏng vì quá tải công suất. Mô hình "nhìn thấy" ngay nhờ feature này.

📌 **Chọn feature bằng số, không cảm tính:** đo permutation importance → **bỏ** `momen_tren_tocdo` (=0) và `ca_lam_viec` (nhiễu), **thêm** `osf_margin` (nâng AUC-PR 0.681→0.693). Quy tắc: trên cây, chỉ thêm feature gộp **nhiều biến / ngưỡng theo điều kiện** (như `osf_margin`); biến đổi của **một** biến thì cây tự làm.

---

## 6. PSI (Population Stability Index)

🎓 **Học thuật**
> Đo độ dịch phân phối một biến giữa Train ($e_i$) và Test ($a_i$) theo B bins:
> $$\text{PSI}=\sum_{i=1}^{B}(a_i-e_i)\ln\frac{a_i}{e_i}$$
> Ngưỡng: $<0.1$ ổn định · $0.1$–$0.25$ nhẹ · $>0.25$ mạnh.

🍜 **Dễ hiểu**
> Chia dữ liệu thành **10 ngăn tủ** theo giá trị. Đếm **% đồ mỗi ngăn** ở tủ A và tủ B. Nếu tỷ lệ giống nhau → PSI ≈ 0 (tủ chưa bị dọn). Nếu đồ **dồn sang ngăn khác** → PSI lớn (tủ đã sắp xếp lại).
>
> **Ví dụ số thật (`momen_xoan`):** ngăn "mômen thấp" ở A có 10% đồ, ở B có **16.6%** đồ (dồn về đây); ngăn "mômen cao" A 10% → B chỉ **4.65%**. Cộng chênh lệch → **PSI = 0.12 = shift nhẹ**.

---

## 7. KS-Test (Kolmogorov–Smirnov)

🎓 **Học thuật**
> Kiểm định phi tham số so 2 phân phối liên tục qua khoảng cách CDF lớn nhất:
> $$D=\sup_x\lvert F_{train}(x)-F_{test}(x)\rvert,\quad \text{p-value nhỏ}\Rightarrow\text{khác biệt có ý nghĩa}.$$

🍜 **Dễ hiểu**
> Vẽ 2 đường "**tích luỹ**" (đến giá trị x thì đã gom được bao nhiêu % dữ liệu) cho A và B. **KS = chỗ 2 đường cách xa nhau nhất.** Cách xa nhiều → 2 phân phối khác nhau nhiều.
>
> **Ví dụ số thật:** nhiệt độ môi trường $D=0.43$ (cách nhau tới 43% — rất khác) còn độ mòn dao $D=0.009$ (gần như trùng — **không** shift). 👉 Kết luận: nhiệt độ trôi mạnh, độ mòn dao đứng yên.

---

## 8. Drift Classifier (bộ phân loại phát hiện shift)

🎓 **Học thuật**
> Gán nhãn miền (Train=0, Test=1) và huấn luyện phân loại. AUC $\approx0.5$ ⇒ hai phân phối trùng (không shift); AUC $\to1$ ⇒ shift mạnh. Feature importance chỉ ra biến "thủ phạm".

🍜 **Dễ hiểu**
> Thuê một **thám tử** thử đoán: *"Mẫu này thuộc nhà máy A hay B?"*.
> - Nếu thám tử **đoán trúng dễ dàng** → hai nhà máy khác nhau rõ (shift mạnh).
> - Nếu chỉ đoán **như tung đồng xu (50/50)** → hai nơi giống hệt (không shift).
>
> **Ví dụ số thật:** thám tử đạt **AUC = 0.81** (đoán khá chuẩn) → shift có thật & mạnh. Manh mối lớn nhất giúp thám tử: **nhiệt độ** (thủ phạm chính).

---

## 9. Importance Reweighting & Density-Ratio (cân lại mẫu)

🎓 **Học thuật**
> Dùng đẳng thức importance sampling để ước lượng rủi ro Test bằng dữ liệu Train có trọng số:
> $$\mathbb E_{P_{test}}[\ell]=\mathbb E_{P_{train}}[\,w(x)\,\ell\,],\quad w(x)=\frac{P_{test}(x)}{P_{train}(x)}=\frac{p(x)}{1-p(x)}\cdot\text{const}$$
> với $p(x)$ từ drift classifier. Chỉ hợp lệ dưới covariate shift.

🍜 **Dễ hiểu**
> Lớp A có nhiều bạn kiểu-X, lớp B có nhiều bạn kiểu-Y. Muốn ôn luyện cho **giống lớp B**, ta **coi trọng hơn** (nhân điểm) những bạn ở A **trông giống học sinh B**.
> - $w$ = "mức coi trọng". Bạn A nào càng giống B → $w$ càng lớn.
>
> **Ví dụ số thật:** trọng số chạy từ 0.002 (mẫu rất "kiểu A", coi nhẹ) đến 8.5 (mẫu "giống B", coi nặng). Sau khi cân, tập Train "trông giống" nhà máy B hơn khi huấn luyện.

---

## 10. Threshold Calibration (hiệu chỉnh ngưỡng)

🎓 **Học thuật**
> Thay ngưỡng mặc định 0.5 bằng $t^\ast=\arg\max_t F1\big(y,\ \mathbb 1[\hat p\ge t]\big)$ ước lượng trên **OOF của Train** (không dùng nhãn Test → tránh leakage), rồi áp cho Test.

🍜 **Dễ hiểu**
> Chuông báo cháy mặc định kêu khi khói ≥ 50%. Nhưng **nhà bếp nhiều khói** → phải chỉnh lại độ nhạy cho hợp, kẻo lúc nào cũng kêu (hoặc chẳng bao giờ kêu). Ta chỉnh "mức nhạy" báo hỏng thay vì cứ để 0.5.
>
> **Ví dụ số thật:** đổi ngưỡng từ 0.5 → **0.324** giúp F1 trên nhà máy B tăng **0.721 → 0.729**.

---

## 11. Precision · Recall · F1

🎓 **Học thuật**
> $\text{Precision}=\frac{TP}{TP+FP}$, $\text{Recall}=\frac{TP}{TP+FN}$, $F1=\frac{2PR}{P+R}$ (trung bình điều hoà — phạt mạnh khi một trong hai thấp).

🍜 **Dễ hiểu** (dùng ví dụ "bác sĩ chẩn đoán máy hỏng")
> - **Precision = "hô có bệnh thì đúng bao nhiêu"** → tránh **báo oan** (bắt máy tốt đi sửa vô ích).
> - **Recall = "máy thực sự bệnh thì bắt được bao nhiêu"** → tránh **bỏ sót** (để máy hỏng gây dừng chuyền).
> - **F1 = điểm cân bằng** cả hai. Không thể "ăn gian" bằng cách hô ầm ĩ hay im thin thít.
>
> **Ví dụ số thật (RandomForest):** trong 477 máy thực hỏng, bắt được **358** (Recall 75%); trong các lần hô hỏng, đúng **80.8%** (Precision); F1 = **0.778**.

| | Dự đoán tốt | Dự đoán hỏng |
|---|---|---|
| **Máy tốt (5523)** | 5438 ✅ | 85 (báo oan) |
| **Máy hỏng (477)** | 119 (bỏ sót) | 358 ✅ |

---

## 12. AUC-ROC vs AUC-PR

🎓 **Học thuật**
> - **AUC-ROC:** diện tích dưới đường TPR–FPR; = xác suất xếp hạng đúng cặp dương/âm. Với imbalance nặng dễ **lạc quan** (FPR loãng bởi nhiều mẫu âm).
> - **AUC-PR:** diện tích dưới Precision–Recall, baseline $=\pi_+$; nhạy lớp thiểu số hơn → **ưu tiên khi imbalance**.

🍜 **Dễ hiểu**
> - **AUC-ROC** dễ "ảo tưởng sức mạnh" khi hàng hỏng quá hiếm (mẫu số quá nhiều máy tốt che lấp lỗi).
> - **AUC-PR** nhìn thẳng vào câu hỏi thực tế: *"trong đống tôi hô hỏng, bao nhiêu là hỏng thật, và tôi có bỏ sót nhiều không?"*.
>
> **Ví dụ số thật:** RandomForest AUC-ROC 0.885 (đẹp), nhưng con số "thật lòng" hơn là AUC-PR **0.686** (so với đoán bừa chỉ 0.08 → vẫn rất tốt).

---

## 13. Stratified K-Fold (chia gập phân tầng)

🎓 **Học thuật**
> Chia dữ liệu thành K fold **bảo toàn tỷ lệ lớp** trong mỗi fold; giảm phương sai ước lượng CV khi imbalance so với K-Fold thường.

🍜 **Dễ hiểu**
> Chia 5 rổ để kiểm tra chéo. **Mỗi rổ phải có đúng ~7% quả hỏng** — nếu để ngẫu nhiên, có rổ **không có quả hỏng nào** → test không công bằng. "Phân tầng" = ép mỗi rổ đều đủ đại diện.

---

## 14. RandomizedSearchCV (dò siêu tham số ngẫu nhiên)

🎓 **Học thuật**
> Lấy mẫu ngẫu nhiên $n$ cấu hình từ không gian phân phối siêu tham số, mỗi cấu hình đánh giá bằng CV; hiệu quả hơn GridSearch khi không gian lớn (Bergstra & Bengio, 2012).

🍜 **Dễ hiểu**
> Mô hình có nhiều **"nút vặn"** (độ sâu cây, tốc độ học, số cây…). Thử **mọi tổ hợp** thì tốn cả ngày. Thay vào đó **thử ngẫu nhiên vài chục tổ hợp** — thường trúng cấu hình gần tối ưu mà nhanh hơn nhiều.

---

## 15. Xử lý Imbalance: class_weight vs SMOTE

🎓 **Học thuật**
> - **class_weight `balanced`:** $w_c=\frac{n}{K n_c}$ — đưa trọng số nghịch tần suất vào hàm mất mát; không thay đổi dữ liệu.
> - **SMOTE:** sinh mẫu thiểu số bằng nội suy k-NN $x_{new}=x_i+\lambda(x_{nn}-x_i)$; chỉ áp trên Train, trong CV.

🍜 **Dễ hiểu**
> - **class_weight = "phạt nặng hơn khi bỏ sót hàng hỏng"** (như giáo viên cho câu khó nhiều điểm hơn để học sinh chú ý).
> - **SMOTE = "nhân bản có biến tấu"** vài mẫu hỏng hiếm để lớp học có nhiều ví dụ hỏng hơn mà học.
>
> Ở bài có shift, **class_weight thường ổn định hơn** SMOTE (SMOTE dễ tạo mẫu giả không thực tế ở vùng biên).

---

## 🧭 Bản đồ ghi nhớ nhanh (một câu mỗi khái niệm)

| Khái niệm | Nhớ bằng một câu |
|---|---|
| Distribution shift | "Luyện đề A, thi đề B" |
| Covariate shift | "Đề hỏi vùng khác, luật chấm không đổi" |
| Imbalance | "100 hàng, 7 hỏng — đoán bừa 'tốt' vẫn đúng 93%" |
| Fit scaler on train | "Chấm curve bằng thước lớp A, cấm nhìn trộm lớp B" |
| Feature engineering | "Tính BMI thay vì nhìn cân & cao riêng" |
| PSI | "Đếm % đồ mỗi ngăn tủ A vs B" |
| KS-Test | "Chỗ 2 đường tích luỹ cách xa nhất" |
| Drift classifier | "Thám tử đoán mẫu thuộc A hay B" |
| Importance reweighting | "Coi trọng bạn ở A giống học sinh B" |
| Threshold calibration | "Chỉnh độ nhạy chuông báo cháy" |
| Precision | "Hô hỏng thì đúng bao nhiêu" |
| Recall | "Máy hỏng thật bắt được bao nhiêu" |
| F1 | "Điểm cân bằng, không cho ăn gian" |
| AUC-PR | "Con số thật lòng khi hàng hỏng hiếm" |
| Stratified K-Fold | "Mỗi rổ đều có quả hỏng" |
| RandomizedSearchCV | "Thử ngẫu nhiên các nút vặn" |

---
*Đọc kèm: `GIAI_THICH_TU_KHOA_DE_BAI.md` (chi tiết công thức + ví dụ số) và `bai_tap_cuoi_khoa.ipynb` (code chạy thật).*
