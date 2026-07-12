# 📊 Đọc biểu đồ EDA trong `bai_tap_FINAL.ipynb` — giải thích các ô insight

Note ghi lại cách **đọc từng biểu đồ EDA** và vì sao rút ra insight đó. Mỗi ô insight trong notebook viết theo
khung **🔎 Quan sát → 💡 Insight → 🛠️ Hướng xử lý → 📐 Chứng cứ** (thấy gì → nghĩa là gì → làm gì → dựa số nào).

---

## Mục 1.1 — Kiểm tra kiểu dữ liệu & thiếu dữ liệu

Cell in ra bảng 3 cột cho mỗi biến: `dtype` (kiểu), `n_missing` (số ô trống), `n_unique` (số giá trị khác nhau).
Đây là việc **luôn làm đầu tiên** vì mọi bước sau (scale, encode, train) đều giả định dữ liệu sạch.

- **🔎 Quan sát:** mọi cột `n_missing = 0`; đếm được **5 biến số** (nhiệt độ, tốc độ, mômen, mòn dao),
  **2 biến phân loại** (`loai_san_pham` L/M/H, `ca_lam_viec` Sáng/Chiều/Đêm), **1 nhãn** `hong_hoc` (0/1).
- **💡 Insight:** **Imputation** = "điền khuyết" (đoán giá trị cho ô trống) — tốn công và có rủi ro làm lệch dữ liệu.
  Vì không có ô trống → **bỏ qua được cả khâu imputation**.
- **🛠️ Hướng xử lý:** dồn công vào phần khó thật sự: scaling/encoding/FE (Phần 2) và **phân phối & distribution shift**
  (1.3 + Phần 3). Phân biệt số vs phân loại vì hai loại xử lý khác nhau: số thì **scale**, chữ thì **encode**.
- **📐 Chứng cứ:** cột `n_missing` = 0 toàn bộ (nhìn thấy trong bảng, không giả định).

> Ý nghĩa: một quyết định nhỏ nhưng **đúng quy trình** — bỏ qua imputation *vì đã kiểm tra và xác nhận sạch*,
> chứ không phải vì quên kiểm tra.

---

## Mục 1.3 — So sánh phân phối A (Train) vs B (Test): dấu hiệu shift

Biểu đồ: 6 ô, mỗi ô **chồng 2 histogram** — xanh = A, đỏ = B — cho từng biến số. Trục ngang = giá trị,
trục dọc = mật độ.

- **🔎 Quan sát:** hai nhiệt độ của B **dịch hẳn sang phải** (cả "quả đồi" trượt về giá trị lớn = nóng hơn);
  `do_mon_dao` hai màu **trùng khít** (không dịch); `toc_do_quay`/`momen_xoan` lệch nhẹ.
  → Hai quả đồi **cùng hình dạng, chỉ trượt ngang** = dấu hiệu một **độ dời (offset) đều**.
- **💡 Insight:** shift **khu trú ở nhóm nhiệt độ**, khớp mô tả "nhà máy B ở khu khí hậu nóng hơn". Và đây là:

  | Loại shift | Định nghĩa | Ở bài này |
  |---|---|---|
  | **Covariate shift** | *Đầu vào* dịch: P(x) đổi nhưng **quan hệ x→y giữ nguyên** | ✅ đúng |
  | **Concept drift** | *Quan hệ* đổi: cùng x nhưng y khác đi | ❌ không |

  Là covariate shift vì **cơ chế vật lý gây hỏng không đổi** (dao mòn quá thì vẫn hỏng), chỉ có **điều kiện đầu vào
  (nhiệt độ) bị dịch**. Phân biệt này quan trọng: covariate shift **chữa được** bằng chỉnh đầu vào; concept drift
  buộc phải thu thập nhãn mới + train lại (khó hơn nhiều).
- **🛠️ Hướng xử lý:**
  1. **Tạo feature triệt tiêu offset nhiệt** = `chenh_lech_nhiet = nhiệt_quy_trình − nhiệt_môi_trường`.
     Nếu B nóng hơn A một lượng đều, **lấy hiệu sẽ khử lượng dịch đó**:

     | | Nhiệt môi trường | Nhiệt quy trình | Hiệu |
     |---|---|---|---|
     | Máy ở A | 300.0 | 310.0 | **10.0** |
     | Cùng máy ở B (nóng hơn 2.5) | 302.5 | 312.5 | **10.0** |

     Hai nhiệt độ thô đều +2.5 nhưng **hiệu vẫn 10.0** → feature hiệu nhiệt "miễn nhiễm" shift.
  2. **Định lượng bằng PSI/KS ở Phần 3** — quan sát bằng mắt chỉ là định tính; cần số để xếp hạng mức shift.
- **📐 Chứng cứ:** Phần 3.1 cho **PSI nhiệt độ ~1.08** (dịch mạnh, ngưỡng >0.25) vs **`do_mon_dao` ~0.001**
  (không dịch). Con số ăn khớp với mắt thấy → kết luận đáng tin.

> **Quy ước PSI:** > 0.25 = dịch mạnh · 0.1–0.25 = nhẹ · < 0.1 = không dịch.

---

## Mạch logic xuyên suốt EDA (vì sao viết theo 4 dòng)

Khung **Quan sát → Insight → Hướng xử lý → Chứng cứ** giúp mỗi quyết định **truy được nguồn**: nhìn thấy gì →
suy ra điều gì → làm gì tiếp → dựa vào số nào. Nhờ vậy khi bảo vệ, mọi bước xử lý đều có lý do và bằng chứng,
không phải "làm theo quán tính".

> Xem thêm: [`GIAI_THICH_EDA_LOGIC.md`](GIAI_THICH_EDA_LOGIC.md) (mạch EDA → Insight → Hướng xử lý tổng quát).
