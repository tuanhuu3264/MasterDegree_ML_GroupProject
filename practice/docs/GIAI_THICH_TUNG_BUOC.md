# 🧑‍🏫 Giảng lại từng bước — dùng 1 ví dụ đồ chơi xuyên suốt

> Cách đọc: mỗi phần gồm **① Câu chuyện** (hiểu ý) → **② Ví dụ số cực nhỏ tính tay** (thấy con số) → **③ Công thức** (để viết báo cáo).
> Mọi con số dưới đây đã được kiểm tra bằng máy, bạn tự bấm tay lại được.

## 🏭 Bối cảnh đồ chơi (nhớ kỹ, dùng cho mọi phần)
Ta có **máy phay**. Muốn đoán máy sẽ **HỎNG (1)** hay **OK (0)** trong ca tới.
- **Nhà máy A** = nơi ta có nhiều dữ liệu để **học** (train).
- **Nhà máy B** = nơi ta sẽ **đem máy đi chạy thật** (test). B **mới, nóng hơn** A.

---

# PHẦN A — TIỀN XỬ LÝ & FEATURE ENGINEERING

## A1. Scaling (chuẩn hoá) — "đổi mọi thứ về cùng một thước đo"

**① Câu chuyện.** Máy có nhiều số đo khác đơn vị: nhiệt độ ~300 (K), tốc độ ~1500 (rpm), mômen ~40 (Nm). Nếu để nguyên, mô hình sẽ tưởng "tốc độ quan trọng gấp 40 lần mômen" chỉ vì **con số to hơn**, chứ không phải vì nó quan trọng thật. Scaling đưa tất cả về cùng thang để so công bằng.

**② Ví dụ số.** Nhiệt độ ở A có trung bình $\mu=40$, độ lệch chuẩn $\sigma=7$. Một máy đo 50 độ:
$$z=\frac{50-40}{7}=1.43$$
Nghĩa là "nóng hơn trung bình 1.43 lần độ lệch chuẩn". Giờ mọi feature đều nói cùng ngôn ngữ "cao/thấp hơn trung bình bao nhiêu".

**③ Công thức.** $z=\dfrac{x-\mu}{\sigma}$ → sau khi đổi, mỗi cột có trung bình ≈ 0, độ lệch ≈ 1.

## A2. "Fit trên Train" — luật chống ăn gian (data leakage)

**① Câu chuyện.** Cái "thước" ($\mu=40,\sigma=7$) phải đo **chỉ từ nhà máy A**. Khi đo máy ở nhà máy B, ta **dùng lại thước của A**, tuyệt đối **không** được nhìn dữ liệu B để chế thước mới. Nhìn trộm B = **ăn gian (leakage)** → lúc báo cáo thì đẹp, lúc chạy thật thì hỏng.

**② Điều bất ngờ (rất quan trọng).** Vì B nóng hơn, khi đo B bằng thước của A, trung bình của B **không** ra 0 mà ra dương (ví dụ +1.26). **Đúng như vậy!** Cái "lệch khỏi 0" đó **chính là distribution shift** — ta cố tình giữ nó để phần sau phát hiện. Nếu bạn chế thước riêng cho B, bạn đã **vô tình xoá mất shift**.

## A3. Feature Engineering — "tự tính ra con số biết nói"

**① Câu chuyện.** Đừng bắt mô hình tự mò. Giống bác sĩ không nhìn cân nặng & chiều cao riêng lẻ mà tính **BMI = cân/cao²**. Ta tính sẵn các con số phản ánh **nguyên nhân hỏng**, ví dụ **công suất = mômen × tốc độ** (máy quá tải công suất thì hỏng).

**② Ví dụ số — vì sao nhìn 1 biến lẻ dễ bị lừa.** Quy tắc hỏng: **công suất (mômen×tốc độ) > 20 thì HỎNG**.

| Máy | mômen | tốc độ | mômen×tốc độ | Kết quả |
|---|---|---|---|---|
| 1 | 2 | 8 | 16 | OK |
| 2 | **8** | 2 | 16 | OK |
| 3 | 5 | 5 | **25** | **HỎNG** |

→ Nếu chỉ nhìn **mômen**: máy 2 có mômen cao nhất (8) mà lại **OK**; máy 3 mômen vừa (5) lại **HỎNG** → nhìn lẻ **gây hiểu nhầm**. Chỉ khi tính **tích mômen×tốc độ** thì quy luật mới lộ ra rõ ràng. Đó là sức mạnh của feature engineering.

**③ Trong bài thật:** công suất cơ $P=\text{mômen}\times\dfrac{2\pi\cdot\text{rpm}}{60}$ (đơn vị Watt). Dòng đầu dữ liệu thật: $P=9277$ W > ngưỡng 9000 → máy đó nguy cơ hỏng do quá tải.

**④ Feature "ăn tiền" nhất — `osf_margin`:** giống hệt ví dụ đồ chơi trên, nhưng **ngưỡng thay đổi theo hạng sản phẩm** (L/M/H = 11000/12000/13000). Ta tính `osf_margin = mòn×momen − ngưỡng(hạng)` → dương nghĩa là "đã vượt ngưỡng quá tải căng thẳng". Thêm feature này nâng AUC-PR **0.681 → 0.693**.
> 💡 **Bài học:** trên mô hình cây, chỉ nên thêm feature khi nó gộp **nhiều biến / ngưỡng đổi theo điều kiện** (như `osf_margin`). Còn biến đổi của **một** biến (ví dụ mômen/tốc độ) thì cây tự làm được → thêm vào **vô ích** (ta đã bỏ `momen_tren_tocdo` vì importance = 0).

---

# PHẦN B — DISTRIBUTION SHIFT LÀ GÌ & VÌ SAO NGUY HIỂM

**① Câu chuyện.** Bạn ôn thi bằng **đề trường A** suốt 2 năm, hôm thi lại là **đề trường B** (cùng môn nhưng ra kiểu khác). Kiến thức gốc giống, nhưng đề khác → điểm tụt. Máy học ở **nhà máy A (mát)**, đem chạy **nhà máy B (nóng)** cũng vậy: mô hình quen với "mát" nên dự đoán sai ở "nóng".

**② Ví dụ số.** Nhiệt độ trung bình: A = **300 K**, B = **302.5 K**. Dữ liệu "trôi" sang vùng nóng mà mô hình **chưa từng thấy nhiều** → dễ sai.

**③ Hai kiểu shift — phải phân biệt:**

| Kiểu | Cái gì đổi | Ví von | Bài này? |
|---|---|---|---|
| **Covariate shift** | Dữ liệu đầu vào $P(x)$ | "Đề hỏi vùng khác, **luật chấm không đổi**" | ✅ Đúng |
| **Concept drift** | Quy luật $P(y\mid x)$ | "**Luật chấm** thay đổi" | ❌ Không |

Ở máy phay: **luật vật lý gây hỏng không đổi** (nóng + quay chậm → hỏng), chỉ **điều kiện vận hành đổi** → **covariate shift**. Tin tốt: chỉ cần "cân lại dữ liệu", **không phải học lại luật**.

---

# PHẦN C — 3 CÁCH ĐO SHIFT (PSI · KS · Drift Classifier)

Ta dùng một **ví dụ đồ chơi** cho cả 3: feature "**mức tải**" có 3 loại Low/Med/High.

| | Low | Med | High |
|---|---|---|---|
| **Nhà máy A** (train) | 50% | 30% | 20% |
| **Nhà máy B** (test)  | 20% | 30% | 50% |

Thấy ngay: A nhiều máy tải Thấp, B nhiều máy tải Cao → đã "trôi".

## C1. PSI — "đếm % đồ mỗi ngăn tủ rồi so"

**① Câu chuyện.** Chia dữ liệu thành các **ngăn tủ**. Đếm **% đồ mỗi ngăn** ở tủ A và tủ B. Ngăn nào tỷ lệ lệch nhiều → shift mạnh.

**② Tính tay:** với mỗi ngăn lấy $(a-e)\times\ln\frac{a}{e}$ rồi cộng ($e$=A, $a$=B):
- Low: $(0.2-0.5)\times\ln\frac{0.2}{0.5} = (-0.3)\times(-0.916)= +0.275$
- Med: $(0.3-0.3)\times\ln 1 = 0$
- High: $(0.5-0.2)\times\ln\frac{0.5}{0.2} = (0.3)\times(0.916)= +0.275$
- **PSI = 0.275 + 0 + 0.275 = 0.55**

**③ Đọc kết quả:** quy ước `<0.1` không shift · `0.1–0.25` nhẹ · **`>0.25` mạnh**. Ở đây 0.55 → **shift mạnh**.
Công thức: $\text{PSI}=\sum_i (a_i-e_i)\ln\frac{a_i}{e_i}$.

## C2. KS-Test — "chỗ 2 đường tích luỹ cách xa nhất"

**① Câu chuyện.** Với mỗi mốc giá trị $x$, hỏi "đến đây đã gom được bao nhiêu % máy?" cho cả A và B → 2 đường **tích luỹ**. **KS = khoảng cách lớn nhất** giữa 2 đường.

**② Tính tay.** A = {30,35,40,45,50}, B = {40,45,50,55,60} (mỗi máy 20%):

| Mốc x | % của A ≤ x | % của B ≤ x | Chênh lệch |
|---|---|---|---|
| 35 | 0.4 | 0.0 | **0.4** |
| 40 | 0.6 | 0.2 | **0.4** |
| 45 | 0.8 | 0.4 | **0.4** |
| 50 | 1.0 | 0.6 | **0.4** |
| 55 | 1.0 | 0.8 | 0.2 |

→ Khoảng cách lớn nhất = **D = 0.4**. Kèm **p-value**: nếu p < 0.05 → khác biệt "thật", không phải ngẫu nhiên.
Công thức: $D=\max_x |F_A(x)-F_B(x)|$.

**PSI vs KS:** PSI cho biết **mạnh hay nhẹ**; KS cho biết **có ý nghĩa thống kê hay không**. Dùng cả hai cho chắc.

## C3. Drift Classifier — "thuê thám tử đoán A hay B"

**① Câu chuyện.** Trộn dữ liệu A và B, dán nhãn `A=0, B=1`, rồi huấn luyện một mô hình **đoán mẫu này thuộc A hay B**.
- Đoán **trúng dễ** (điểm AUC gần 1) → A và B khác nhau rõ → **shift mạnh**.
- Đoán **như tung đồng xu** (AUC ≈ 0.5) → A và B giống hệt → **không shift**.

**② Số thật của bài:** thám tử đạt **AUC = 0.81** → shift có thật & mạnh. Feature giúp thám tử đoán trúng nhất = **nhiệt độ** → nhiệt độ là "thủ phạm" gây shift.

**③ Hơn PSI/KS ở chỗ:** PSI/KS xét **từng biến riêng lẻ**; thám tử nhìn **nhiều biến cùng lúc** nên bắt được cả shift kiểu kết hợp.

---

# PHẦN D — IMPORTANCE REWEIGHTING (cân lại mẫu để "giống B")

**① Câu chuyện.** Ta chỉ có nhiều dữ liệu ở A, nhưng muốn mô hình giỏi ở B. Mẹo: khi huấn luyện, **coi trọng hơn** những máy ở A **trông giống máy ở B**, và **coi nhẹ** những máy A kiểu hiếm gặp ở B. "Mức coi trọng" đó gọi là **trọng số $w$**.

**② Tính tay (dùng lại bảng mức tải).** $w = \dfrac{\text{tỷ lệ ở B}}{\text{tỷ lệ ở A}}$:

| Mức tải | A | B | $w=B/A$ | Ý nghĩa |
|---|---|---|---|---|
| Low | 0.5 | 0.2 | **0.4** | A thừa máy tải thấp → coi nhẹ |
| Med | 0.3 | 0.3 | **1.0** | bằng nhau → giữ nguyên |
| High | 0.2 | 0.5 | **2.5** | B nhiều máy tải cao → coi trọng gấp 2.5 |

→ Một máy tải **High** ở A được tính như thể **2.5 máy** khi huấn luyện → tập A "trông giống" B hơn.

**③ Công thức.**
- Lý thuyết: trọng số lý tưởng $w(x)=\dfrac{P_B(x)}{P_A(x)}$ (tỷ số mật độ — chính là cột $B/A$ ở trên).
- Thực tế khó tính trực tiếp → dùng **thám tử** (drift classifier): nếu $p(x)$ = xác suất thám tử nói "thuộc B", thì
$$w(x)=\frac{p(x)}{1-p(x)}\quad(\text{tỷ số "khả năng B" trên "khả năng A"}).$$
- **Điều kiện dùng được:** phải là **covariate shift** (luật chấm không đổi) — đúng với bài này.

---

# PHẦN E — ĐỌC ĐIỂM SỐ (Precision · Recall · F1 · AUC)

**① Câu chuyện.** Coi mô hình như **bác sĩ chẩn đoán máy bệnh**. Có 2 kiểu sai:
- **Báo oan** (máy tốt bị bắt đi sửa) → tốn công.
- **Bỏ sót** (máy hỏng mà không báo) → máy chết giữa ca, tốn to.

**② Ví dụ số.** 10 máy, trong đó **4 máy thực sự hỏng**. Mô hình dự đoán:
- Bắt đúng **3** máy hỏng (TP=3), **bỏ sót 1** (FN=1).
- **Báo oan 1** máy tốt (FP=1), còn lại 5 máy tốt báo đúng (TN=5).

| | Đoán OK | Đoán HỎNG |
|---|---|---|
| **Thực OK (6)** | 5 ✅ | 1 (báo oan) |
| **Thực HỎNG (4)** | 1 (bỏ sót) | 3 ✅ |

- **Precision** = trong các lần *hô hỏng*, đúng bao nhiêu = $\frac{3}{3+1}=0.75$ (75% lần hô là thật).
- **Recall** = trong các máy *thực hỏng*, bắt được bao nhiêu = $\frac{3}{3+1}=0.75$ (bắt 3/4).
- **F1** = điểm cân bằng cả hai = $\frac{2\times0.75\times0.75}{0.75+0.75}=0.75$.

**③ Vì sao cần F1 & AUC-PR (không dùng accuracy):**
- **Accuracy đánh lừa:** máy hỏng hiếm (7%), cứ "đoán tất cả OK" là đúng 93% — nhưng **bắt được 0 máy hỏng** → vô dụng. F1 không cho ăn gian kiểu đó.
- **AUC-ROC** cũng dễ "ảo tưởng" khi hàng hỏng hiếm; **AUC-PR** nhìn thẳng vào lớp hỏng nên **thật lòng hơn**. (Bài thật: mô hình tốt nhất Precision 0.81, Recall 0.75, **F1 0.78**.)

Công thức: $\text{Precision}=\frac{TP}{TP+FP}$, $\text{Recall}=\frac{TP}{TP+FN}$, $F1=\frac{2PR}{P+R}$.

---

# 🎯 TÓM TẮT 1 DÒNG MỖI Ý

| Ý | Nhớ bằng một câu | Số ví dụ |
|---|---|---|
| Scaling | "Đổi mọi thứ về cùng thước" | z=(50−40)/7=1.43 |
| Fit-on-train | "Đo bằng thước của A, cấm nhìn trộm B" | B sau scale mean ≠ 0 (giữ shift) |
| Feature engineering | "Tính BMI thay vì nhìn cân & cao riêng" | mômen×tốc độ=25 → HỎNG |
| Distribution shift | "Luyện đề A, thi đề B" | nhiệt 300→302.5 |
| Covariate shift | "Đề khác nhưng luật chấm không đổi" | luật vật lý bất biến |
| PSI | "Đếm % đồ mỗi ngăn tủ" | 0.55 → shift mạnh |
| KS | "Chỗ 2 đường tích luỹ xa nhất" | D=0.4 |
| Drift classifier | "Thám tử đoán A hay B" | AUC=0.81 |
| Reweighting | "Coi trọng máy A giống B" | w(High)=2.5 |
| Precision | "Hô hỏng đúng bao nhiêu" | 3/4=0.75 |
| Recall | "Máy hỏng bắt được bao nhiêu" | 3/4=0.75 |
| F1 | "Điểm cân bằng, cấm ăn gian" | 0.75 |

---
*Đọc kèm: `GIAI_THICH_2_VERSION.md` (2 phiên bản mỗi ý) · `GIAI_THICH_TU_KHOA_DE_BAI.md` (chi tiết + lỗi thường gặp) · `bai_tap_cuoi_khoa.ipynb` (code thật).*
