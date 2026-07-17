# 🔴🔵 Phân phối feature theo LỚP (hỏng vs không) — mục 1.6

Note ghi lại giải thích **mục 1.6** của [`../bai_tap_FINAL.ipynb`](../bai_tap_FINAL.ipynb): xem mỗi feature phân bố
thế nào ở **máy hỏng (đỏ) vs không hỏng (xanh)**, để tìm ngưỡng cơ chế. Kèm **số thật** và một chỗ **đã sửa**.

---

## Soát từng khẳng định (đối chiếu dữ liệu)

### ① "Máy hỏng dồn về vùng mòn dao cao" — ĐÚNG, nhưng cần lưu ý *tỷ lệ vs số lượng*
- Mòn dao trung bình: **hỏng = 177** vs **không hỏng = 123** → máy hỏng nghiêng về mòn cao. ✅
- **Lưu ý:** dù *tỷ lệ* hỏng cao ở mòn lớn, **60.8% số CA hỏng thật lại nằm ở vùng mòn ≤ 240** — vì máy mòn thấp
  đông hơn nhiều và vẫn hỏng qua cơ chế khác (nhiệt/công suất/quá tải). Nói chuẩn: *"tỷ lệ hỏng tăng vọt ở mòn cao"*,
  không phải "mọi máy hỏng đều mòn cao".

### ② "Mômen cao" — ❌ SAI → phải là "cả hai cực mômen (chữ U)"
Mômen trung bình hai lớp **gần bằng nhau**: hỏng 39.7 vs không 40.0. Tỷ lệ hỏng theo mức mômen:

| Mômen (Nm) | Tỷ lệ hỏng |
|---|---|
| 0–20 (rất thấp) | **36.9%** |
| 20–30 | 5.7% |
| 30–40 | 6.3% |
| 40–50 | 5.4% |
| 50–60 | 8.1% |
| 60–80 (rất cao) | **29.1%** |

→ Hỏng dồn ở **cả hai đầu** (thấp = thiếu công suất PWF; cao = quá tải), **hình chữ U**, không phải "cao".
Chính vì chữ U mà trung bình hai lớp bằng nhau và **Pearson ≈ 0.006** (khớp [`GIAI_THICH_PEARSON_VS_MI.md`](GIAI_THICH_PEARSON_VS_MI.md)).
**Đã sửa** ô insight: "mômen cao" → **"cả hai cực mômen"**.

### ③ "Hai đuôi tốc độ" — ĐÚNG
Tỷ lệ hỏng theo tốc độ: thấp (1180–1300) = **13.1%**, giữa ~6%, cao (1900–2200) = **9.4%** → hai đuôi cao hơn giữa
(cũng chữ U, nhẹ hơn). ✅

### ④ "Hai lớp chồng lấn nhiều" — ĐÚNG
Vùng mòn > 240 chỉ **57.5%** thật sự hỏng → **42.5% vượt ngưỡng mà không hỏng**; và 60.8% ca hỏng lại ở mòn thấp.
Hai đám mây đỏ/xanh trùm lên nhau, không có ranh giới sạch. ✅

## Insight & hướng xử lý (đều đúng)

- **Insight:** có **ngưỡng cơ chế** (mòn ~240) nhưng **vượt ngưỡng không chắc chắn hỏng** → nhãn mang **yếu tố ngẫu nhiên**
  (42.5% máy vượt ngưỡng vẫn không hỏng = phần "may rủi" feature không giải thích được).
- **Hướng xử lý:** (a) tạo feature **"khoảng cách tới ngưỡng"** (`osf_margin`, `twf_margin`…) để mã hoá ngưỡng cho mô hình;
  (b) **dự báo trước F1 có trần** — phần chồng lấn 42.5% là nhiễu không khử được, chính là mầm mống trần ~0.78 (Phần 5).

## Tóm lại

Ô 1.6 về cơ bản đúng và dẫn đúng tới FE + dự báo trần F1, **trừ lỗi "mômen cao"** → đã sửa thành **"cả hai cực mômen (chữ U)"**.
Lỗi này lại **củng cố** mục 1.5 (vì sao Pearson mù với mômen). Đã thêm bảng bin mômen + số trung bình hai lớp làm chứng cứ.
