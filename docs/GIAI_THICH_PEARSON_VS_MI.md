# 📈 Pearson vs Mutual Information — vì sao quan hệ hỏng hóc "phi tuyến theo ngưỡng"

Note ghi lại giải thích **mục 1.5** của [`../bai_tap_FINAL.ipynb`](../bai_tap_FINAL.ipynb), kèm **số thật** và
một chỗ **đã sửa** cho đúng.

---

## 1. Hai thước đo khác nhau

| | **Pearson correlation** | **Mutual Information (MI)** |
|---|---|---|
| Đo cái gì | quan hệ **tuyến tính** (đường thẳng): "x tăng thì y tăng/giảm đều" | **mọi** dạng phụ thuộc, kể cả cong/ngưỡng/chữ U |
| Mù với | quan hệ phi tuyến (ngưỡng, chữ U) | (không mù) |
| Khoảng giá trị | −1…1 (0 = không có quan hệ tuyến tính) | ≥ 0 (0 = độc lập hoàn toàn) |

**Ý chính:** Pearson chỉ thấy đường thẳng. Nếu hỏng hóc xảy ra kiểu "vượt ngưỡng 240 thì đột ngột nguy hiểm"
(một bậc thang, không phải dốc đều), Pearson sẽ **đánh giá thấp / bỏ sót**, còn MI thì bắt được.

## 2. Số thật (train)

| Feature | \|Pearson\| | MI |
|---|---|---|
| nhiet_do_moi_truong | 0.001 | 0.000 |
| nhiet_do_quy_trinh | 0.033 | 0.001 |
| toc_do_quay | 0.066 | 0.008 |
| **momen_xoan** | **0.006** | **0.021** |
| **do_mon_dao** | **0.195** | **0.061** |

## 3. ⚠️ Chỗ đã sửa trong ô insight

Bản cũ dòng Quan sát viết *"Pearson của từng biến gốc đều rất nhỏ (|corr| < 0.1)"* — **sai với `do_mon_dao`**
(thực tế **0.195 > 0.1**), lại **mâu thuẫn** với dòng Chứng cứ ghi "|corr| ~ 0.19".

**Đã sửa thành:** *"hầu hết biến gốc có Pearson rất nhỏ; riêng `do_mon_dao` nhỉnh nhất (0.195) nhưng vẫn yếu,
và quan hệ thật là **ngưỡng** chứ không tuyến tính."*

## 4. Hai bằng chứng cho "phi tuyến theo ngưỡng"

**Bằng chứng A — `momen_xoan` (ca sạch nhất):** Pearson = **0.006** (≈ 0 tuyệt đối) nhưng MI = **0.021**
(~3.5× tương đối). Vì mômen gây hỏng ở **cả hai cực** — quá thấp (PWF thiếu công suất) *và* quá cao (quá tải).
Quan hệ hình **chữ U** → triệt tiêu về đường thẳng → Pearson ≈ 0; nhưng phụ thuộc vẫn có thật → MI thấy được.
Đây đúng là "Pearson mù, MI bắt".

**Bằng chứng B — `do_mon_dao` (bậc thang):** tỷ lệ hỏng theo mức mòn:

| Mức mòn dao | Tỷ lệ hỏng |
|---|---|
| 0–100 | 4.3% |
| 100–180 | 4.1% |
| 180–220 | 5.7% |
| 220–240 | 7.3% |
| **240–260** | **57.5%** |

Phẳng lì ~4–7% cho tới 240, rồi **nhảy vọt lên 57.5%** → **hàm bậc thang**, không dốc đều. Pearson chỉ bắt phần
"xu hướng tăng dần" (0.195) nên **không diễn tả được cú nhảy** — mà cú nhảy mới là bản chất.

## 5. Vì sao dẫn tới Feature Engineering

Cả hai bằng chứng nói cùng một điều: **không biến gốc nào dự báo hỏng một cách tuyến tính** — quan hệ là **ngưỡng**
và **tương tác**. Mô hình tuyến tính (LogReg) chỉ vẽ được đường thẳng, nên phải **tự tay tạo feature mã hoá
ngưỡng/tương tác**: `chenh_lech_nhiet` (HDF), `cong_suat_co` (PWF), `osf_margin` (OSF theo hạng SP). Đó là lý do
MI ở đây không chỉ là "biểu đồ đẹp" mà là **bằng chứng thúc đẩy toàn bộ Phần 2**.

> 🔧 Tái tạo: `mutual_info_classif(train[NUM], y)` so với `np.corrcoef`; và `pd.cut(do_mon_dao,...)` rồi lấy
> `groupby(...).hong_hoc.mean()` để ra bảng bậc thang.
