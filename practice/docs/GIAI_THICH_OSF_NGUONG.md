# 🧷 Ngưỡng OSF 11000/12000/13000 — nguồn gốc & kiểm chứng (kèm đính chính)

Note ghi lại một chuỗi kiểm chứng về ngưỡng OSF dùng trong `osf_margin`, **có cả những nhận định ban đầu SAI đã sửa**.
Mục đích: không lặp lại kết luận vội, và trung thực về giới hạn.

---

## 1. Công thức OSF & osf_margin

OSF = Overstrain Failure (hỏng do quá tải cơ học). Đại lượng căng thẳng:

```
tich_mon_momen = do_mon_dao (phút) × momen_xoan (Nm)    [phút·Nm]
osf_margin     = tich_mon_momen − ngưỡng(hạng)
ngưỡng:  L = 11000,  M = 12000,  H = 13000   (phút·Nm)
```

`osf_margin > 0` ⇒ đã vượt ngưỡng ⇒ (lẽ ra) nguy cơ OSF.

## 2. Nguồn gốc các con số — KHÔNG suy ra từ dữ liệu

11000/12000/13000 lấy từ **tài liệu bộ AI4I 2020** (UCI) — bộ dữ liệu gốc mà đề bài dựa vào (chỉ đổi tên sang
tiếng Việt). Đây là **kiến thức domain / spec thiết kế**, không phải tôi tính ra từ dữ liệu.

## 3. Thử tự tìm lại từ dữ liệu → KHÔNG khớp

Quét ngưỡng tối ưu cho luật "tich > t ⇒ hỏng" theo từng hạng:

| Hạng | F1-scan | Youden J | AI4I |
|---|---|---|---|
| L | 10800 | ~8226 | 11000 |
| M | 9300 | ~7890 | 12000 |
| H | 9600 | ~7951 | 13000 |

→ Ngưỡng tối ưu theo dữ liệu **dồn về ~8000**, **không** cách nhau 1000, **không** theo thứ tự hạng. Dữ liệu **không**
chỉ về 11000/12000/13000.

## 4. Tỷ lệ hỏng tăng DẦN, không có bậc thang tại ngưỡng

Bin theo `tich` (mỗi 1000):

| tich | L (ngưỡng 11000) | M (12000) | H (13000) |
|---|---|---|---|
| 8000–9000 | 9.1% | 9.7% | 7.6% |
| 9000–10000 | 12.1% | 13.9% | 12.1% |
| 10000–11000 | 15.9% | 19.5% | 23.4% |
| 11000–12000 | 19.3% | 20.4% | 11.8% |
| 12000–13000 | 35.9% | 14.0% | 20.0% |
| 13000–14000 | 89.5% | 39.1% | 27.8% |
| 14000+ | ~75–100% | ~100% | ~55–100% |

→ Tỷ lệ **bò lên từ từ**, chỉ gần chắc chắn ở **tích rất cao (13000–16000+)**, không nhảy tại ngưỡng AI4I.

## 5. ⚠️ Hai nhận định ban đầu SAI (đã sửa)

1. **"Ngưỡng tạo bước nhảy hỏng sạch"** — SAI. Soi mịn thì tỷ lệ dốc lên có nhiễu, không phải bậc thang.
   (Con số "6% → 40% quanh ngưỡng" chỉ là ảo giác do gộp trung bình một đường dốc thành hai xô.)
2. **"Dữ liệu xác nhận ngưỡng AI4I hợp lý"** — SAI. Dữ liệu không cho bậc nhảy tại các ngưỡng đó; ngưỡng tách
   tốt nhất ~8000 và không theo hạng.

## 6. Vì sao lệch — dấu vết LABEL NOISE cố ý

Trong AI4I **gốc**, vượt ngưỡng OSF thì hỏng gần **100%** (xác định). Ở đây vượt ngưỡng chỉ hỏng **19–40%** →
**nhãn đã bị làm nhiễu có chủ đích** (đúng tinh thần "cài trick"). Chính label noise này vừa **xoá bậc thang OSF**,
vừa là **nguyên nhân trần F1 ~0.78** (xem Phần 5 notebook).

## 7. Vậy `osf_margin` còn dùng được không? — CÓ

`osf_margin` vẫn là feature tốt, **không phải vì ngưỡng chính xác**, mà vì:
- Nó mã hoá xu hướng **đơn điệu**: tích càng cao càng dễ hỏng (rõ trong bảng §4).
- Trừ theo hạng chỉ **hiệu chỉnh nhẹ** cho đúng thứ tự L < M < H (hạng L nhạy hơn H ở cùng tích — §8).
- **Cây/rừng tự tìm ranh giới thật** bất kể ngưỡng ta cắm, nên feature vẫn có ích.

## 8. Điều gì VẪN đúng: hạng có điều biến (interaction thật)

Ở cùng một tích > 12000: hạng **L hỏng ~56%** vs **H ~35%** → hạng thật sự điều biến quan hệ tich→hỏng
(L nhạy hơn). Nên đưa `loai_san_pham` vào **qua tương tác** là đúng — chỉ là **giá trị ngưỡng chính xác thì không**
kiểm chứng được từ dữ liệu này.

## Kết luận

> 11000/12000/13000 là **từ spec AI4I**, **không** được dữ liệu (đã bị sửa) xác nhận như ranh giới sắc.
> `osf_margin` dùng được như **tín hiệu đơn điệu + hiệu chỉnh hạng**, cây/rừng tự tinh chỉnh. **Không** khẳng định
> "ngưỡng khớp dữ liệu". Sự lệch này chính là dấu vết label noise — cùng gốc rễ với trần F1.
