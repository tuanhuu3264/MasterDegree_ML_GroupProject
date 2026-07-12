# ⚖️ Vì sao chọn `class_weight='balanced'` chứ không dùng SMOTE

Note ghi lại phân tích **xử lý mất cân bằng** cho bài Predictive Maintenance — kèm **bằng chứng đo được**,
không phải lập luận cảm tính. Liên quan mục **2.6** của [`../bai_tap_FINAL.ipynb`](../bai_tap_FINAL.ipynb).

---

## 1. Vấn đề gốc

Lớp hỏng chỉ ~7.4% (train) / 7.9% (test). Khi mô hình tối ưu tổng lỗi, lực kéo tự nhiên là **phớt lờ lớp hỏng**
(đoán "không hỏng" hết đã đúng ~92%). Cần một kỹ thuật bắt mô hình chú ý lớp thiểu số. Có 2 họ:
- **`class_weight='balanced'`** — đổi *trọng số phạt*, không đụng dữ liệu.
- **SMOTE** — *sinh thêm* mẫu hỏng nhân tạo cho tới khi cân bằng.

## 2. Bằng chứng #1 — so sánh trực tiếp trên Test B

Cùng RandomForest, cùng cách chọn ngưỡng (F1 tối ưu trên CV-train):

| Xử lý imbalance | AUC-PR | F1 | Precision | Recall |
|---|---|---|---|---|
| **`class_weight='balanced'`** | 0.693 | **0.781** | **0.812** | **0.753** |
| SMOTE | 0.694 | 0.759 | 0.791 | 0.730 |

→ SMOTE làm **F1 tụt 0.781 → 0.759**, tụt **cả precision lẫn recall**. Không phải "an toàn hơn về lý thuyết"
chung chung — trên dữ liệu này nó **thực sự tệ hơn**.

## 3. Bằng chứng #2 — SMOTE làm gì với dữ liệu (cách "biết được")

**Cách đo:** `SMOTE.fit_resample(X, y)` của imblearn trả về **dữ liệu gốc trước, mẫu sinh thêm nối vào sau**.
Train có 14.000 dòng → mọi dòng từ index 14000 trở đi (**11.938 dòng**) chính là máy hỏng-giả mới. Ta tách riêng
chúng ra và **đọc thẳng cột `do_mon_dao`** để xem chúng rơi vào đâu.

| Đo trên | Tỉ lệ ở vùng mòn dao ≤ 240 (vùng an toàn) |
|---|---|
| Máy hỏng **thật** | 60.8% |
| Máy hỏng-**giả** (SMOTE sinh) | 63.8% |

→ SMOTE **không** đặt sai chỗ: nó sao chép trung thực phân phối máy hỏng thật (60.8% ≈ 63.8%). Máy hỏng vốn
hay nằm ở vùng mòn thấp vì hỏng còn do **HDF/PWF/OSF** (tản nhiệt, công suất, quá tải), không chỉ do mòn dao.

## 4. Tác hại thật — **thổi phồng mật độ**, không phải đặt sai chỗ

Vấn đề nằm ở **mật độ hỏng ở vùng an toàn** (vùng mòn ≤ 240, chiếm 95% số máy):

| Vùng mòn ≤ 240 | Tỉ lệ hỏng |
|---|---|
| Thực tế | **4.7%** |
| Sau khi SMOTE cân bằng lớp | **39.4%** |

→ **Bị thổi phồng ~8 lần.** SMOTE phải sinh ~12.000 máy hỏng để cân lớp; vì rải theo phân phối hỏng thật,
phần lớn rơi vào vùng an toàn (nơi tập trung 95% số máy). Mô hình từ đó **nhìn vùng an toàn như thể ~40% nguy hiểm
thay vì ~5%** → lệch ranh giới quyết định → báo oan nhiều hơn → **precision giảm → F1 giảm** (khớp bảng ở mục 2).

## 5. Vì sao `class_weight` tránh được

`class_weight='balanced'` cũng "tăng trọng lượng" lớp hỏng (~6.8× — công thức
$w = \frac{n}{2 \times n_{lớp}}$), **nhưng chỉ tăng trên các máy hỏng THẬT đang có**, không rải điểm mới ra
không gian. **Mật độ tương đối giữa các vùng giữ nguyên** — vùng an toàn vẫn "thưa hỏng", vùng nguy hiểm vẫn
"dày hỏng". Nó đạt cùng mục tiêu (bắt mô hình chú ý lớp hỏng) mà **không bóp méo hình dạng phân phối**.

Ba đặc điểm của bài này khiến SMOTE dễ dính lỗi mà class_weight thì không:
1. **Chồng lấn nặng** — mòn > 240 chỉ 57.5% hỏng; nội suy trong vùng lẫn dễ tạo nhiễu.
2. **Nhãn có yếu tố ngẫu nhiên** (chính thứ tạo trần F1 ~0.78) — SMOTE **khuếch đại nhiễu**.
3. **Có distribution shift A→B** — SMOTE làm dày cấu trúc Train A → càng khớp A càng dễ lệch khi sang B.

## 6. Chốt lại (một câu)

> Mất cân bằng khiến mô hình "lười" bỏ qua máy hỏng. `class_weight` sửa bằng cách **phạt nặng hơn khi bỏ sót**
> (không bịa dữ liệu); SMOTE sửa bằng cách **thêm máy hỏng giả**, nhưng ở bài nhiều nhiễu + chồng lấn + shift này
> nó **thổi phồng mật độ hỏng ở vùng an toàn từ 4.7% lên 39.4% (~8×)**, kéo F1 xuống 0.759. Vì thế notebook
> chọn **`class_weight='balanced'`** và chỉ để SMOTE làm minh hoạ.

> 🔧 Tái tạo bằng chứng: chạy lại RandomForest với `class_weight='balanced'` vs `imblearn.pipeline` có bước
> `SMOTE`, so F1/precision/recall trên Test; và tách 11.938 dòng SMOTE sinh ra để đếm `do_mon_dao`.
