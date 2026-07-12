# Pain Points — Bài cuối khoá Predictive Maintenance dưới Distribution Shift

> Catalogue rủi ro/cạm bẫy của bài, tổng hợp từ (1) phân tích dữ liệu thật, (2) rubric,
> (3) scan toàn bộ note khoá học + slide bằng 4 agent. Mức độ: 🔴 cao (dễ mất điểm / hỏng
> kết quả) · 🟠 trung bình · 🟡 cần lưu ý. Đi kèm cách giảm thiểu. Bổ trợ cho [CHIEN_LUOC.md].

---

## 0. Cạm bẫy TRUNG TÂM — nghịch lý chấm điểm

**🔴 P0. Bị chấm bằng hiệu năng trên Dây chuyền B (3.0đ) nhưng KHÔNG được dùng nhãn B để tối ưu.**
Đây là mâu thuẫn gốc chi phối toàn bộ bài: mọi lựa chọn (model, siêu tham số, ngưỡng, ensemble)
phải "nhắm" vào B mà chỉ được nhìn A. Chọn theo nhãn Test = rò rỉ = điểm ảo + phản mục tiêu (mất
khả năng transfer thật). → *Giảm thiểu:* **Importance-Weighted Validation** (mô phỏng B từ A bằng
density-ratio); Test chỉ chấm 1 lần cuối để báo cáo.

---

## 1. Distribution Shift (nhóm nguy hiểm nhất — Phần 3 + Kết quả)

**🔴 P1. Model bám phân phối A → "gãy" trên B.** XGB variance cao học biên phi tuyến tinh vi khớp A;
B dịch (nóng hơn +2.5°/+1.9°, quay +70rpm, std nhiệt loe ~30%) → biên rơi sai chỗ. *Giảm thiểu:*
regularize mạnh tay hơn mức tối ưu-trên-A; giữ LogReg làm mỏ neo; reweighting + calibration; ensemble.

**🔴 P2. Cây/boosting KHÔNG ngoại suy được — 2.8% dòng Test nằm NGOÀI khoảng Train.**
Đã đo: `toc_do_quay` B max 2414.9 > A max 2153.5; nhiệt độ B cũng vượt trần A. Cây dự đoán **phẳng**
(hằng số) ngoài vùng đã thấy → sai hệ thống ở đúng vùng B mở rộng. *Giảm thiểu:* nêu rõ hạn chế này
trong báo cáo; LogReg/mô hình tuyến tính ngoại suy "có hướng" nên bổ khuyết; cân nhắc clip/winsorize
hoặc feature cơ học (tỉ lệ) ít nhạy biên.

**🔴 P3. Reweighting chỉ đúng nếu là covariate shift thuần (P(y|x) không đổi).** Nếu Dây chuyền B còn
đổi *quan hệ* hỏng↔đặc trưng (concept drift) thì density-ratio vô hiệu — mà ta **không kiểm chứng
được** vì không có nhãn B. *Giảm thiểu:* nêu giả định rõ ràng; lập luận vật lý (cơ chế hỏng bất biến)
+ bằng chứng prior nhãn ổn định (7.4%→8.0%) để biện minh giả định covariate shift; coi đó là *hạn chế*.

**🟠 P4. Trọng số density-ratio cực đoan → IWV variance bùng nổ, ước lượng nhiễu.** Vài mẫu A hiếm ở
vùng B được gán trọng số khổng lồ → validation bị vài điểm chi phối. *Giảm thiểu:* **clip trọng số**
(vd percentile 1–99 hoặc trần w≤10), chuẩn hoá tổng trọng số; báo cáo effective sample size.

**🟠 P5. Chính bộ ước lượng density-ratio có thể sai → chọn nhầm model.** Drift classifier ước lượng
kém thì IWV lệch. *Giảm thiểu:* chạy **song song CV thường (Stratified) không reweight** làm đối chứng;
hai bảng xếp hạng lệch nhau = bằng chứng shift (đưa vào báo cáo), đồng thời cảnh báo độ tin IWV.

**🟠 P6. Ngưỡng calibrate trên A có thể không giữ trên B.** Phân phối điểm số (score) dịch theo shift
dù prior nhãn ổn định. *Giảm thiểu:* chọn ngưỡng trên **IWV** (đã mô phỏng B) chứ không trên A thô;
báo cáo độ nhạy F1 quanh ngưỡng.

**🟠 P7. Feature engineering có thể "nhập khẩu" shift.** `cong_suat_co = momen×rpm` phụ thuộc `toc_do_quay`
(dịch mạnh) → feature mới có thể drift mạnh hơn cả biến gốc. *Giảm thiểu:* **tính PSI/KS cho cả feature
mới**; giữ feature vừa tăng điểm vừa ổn định qua shift; loại/biến đổi feature drift nặng mà ít lợi.

**🟡 P8. Nhầm hai nghĩa "covariate shift".** Trong `neural-network.md` từ này chỉ *internal covariate
shift* (lý do Batch Norm) — KHÁC hẳn train-vs-test shift của bài. *Giảm thiểu:* định nghĩa lại tự chứa
trong notebook, không trích nhầm.

---

## 2. Phát hiện shift bằng thống kê (Phần 3 — toàn bộ NGOÀI khoá)

**🔴 P9. PSI không có trong bất kỳ tài liệu khoá nào.** Không slide, không note, không đề cương.
*Giảm thiểu:* notebook **tự định nghĩa** công thức `PSI = Σ(%A−%E)·ln(%A/%E)`, chia **10 bin theo phân
vị Train**, xử lý bin rỗng bằng epsilon; ghi rõ **bảng ngưỡng quy ước ngành** (<0.1 không / 0.1–0.25
nhẹ / >0.25 mạnh) và nói đây là quy ước thực hành, không phải test có p-value.

**🟠 P10. KS-Test: p-value ≈ 0 với n=14000 dù shift nhỏ.** Mẫu lớn làm mọi khác biệt "có ý nghĩa
thống kê". *Giảm thiểu:* báo cáo **statistic D (effect size)**, không chỉ p; neo vào khung H₀/H₁ đã
học (`kiem-dinh-gia-thuyet.md`) — H₀: A,B cùng phân phối; đúng tinh thần "significant ≠ quan trọng".

**🟠 P11. KS chỉ dùng cho biến số — biến phân loại (loại SP, ca) cần cách khác.** *Giảm thiểu:*
Chi-square test hoặc PSI cho biến phân loại; nêu rõ tách hai loại.

**🟠 P12. Drift Classifier dễ bị hiểu/áp dụng sai.** (a) Nếu lỡ đưa nhãn `hong_hoc` vào → AUC ảo;
(b) diễn giải AUC sai. *Giảm thiểu:* **chỉ dùng feature, tuyệt đối không target**; quy ước AUC≈0.5 →
không shift, AUC→1 → shift mạnh; feature importance = "thủ phạm"; chạy trên gộp A/B với nhãn giả 0/1.

**🟡 P13. PSI phụ thuộc cách chia bin.** Số bin / cách chia đổi thì giá trị đổi. *Giảm thiểu:* cố định
10 bin phân vị Train, nêu rõ; đối chiếu KS để không phụ thuộc một thước.

**🟡 P14. Reweighting/density-ratio là kiến thức ngoài khoá — giảng viên không có "đáp án chuẩn".**
*Giảm thiểu:* giải thích trực giác thật kỹ: w(x)=P_B(x)/P_A(x) ≈ p/(1−p) từ drift classifier; nối vào
cái đã học — nó là dạng tổng quát của `class_weight`/`sample_weight` nhưng đánh theo *đặc trưng*.

---

## 3. Mất cân bằng lớp (~7–8%)

**🔴 P15. Accuracy vô nghĩa, nhưng dễ vô tình dùng.** Đoán "không hỏng" hết vẫn ~92% accuracy.
*Giảm thiểu:* cấm accuracy; F1 (số so sánh chính) + AUC-PR + PR-curve.

**🔴 P16. `scoring='accuracy'` trong RandomizedSearchCV (mặc định nhiều ví dụ) → chọn sai model/ngưỡng.**
*Giảm thiểu:* đặt `scoring='average_precision'` (refit theo AP), theo dõi thêm `f1`; **tách chọn ngưỡng**
sang bước Threshold Calibration thay vì để search tối ưu F1 tại ngưỡng 0.5 cứng.

**🟠 P17. F1 trên lớp hiếm rất "nhiễu" giữa các fold → xếp hạng leaderboard bấp bênh.** Chỉ 1031 mẫu
hỏng ở Train, 477 ở Test → sai số ước lượng lớn. *Giảm thiểu:* `RepeatedStratifiedKFold` (vd 5×3) cho
con số ổn định; báo cáo khoảng dao động, không chốt hơn-thua vì chênh 0.001.

**🟠 P18. Precision sụp khi đẩy Recall.** v0 đã thấy P=0.137 ở R=0.736. Bảo trì muốn bắt hết máy hỏng
nhưng báo động giả nhiều thì mất niềm tin. *Giảm thiểu:* chọn ngưỡng theo chi phí FP vs FN; trình bày
đánh đổi bằng PR-curve; nêu khuyến nghị vận hành (ngưỡng cảnh báo 2 mức chẳng hạn).

**🟠 P19. AUC-ROC lạc quan giả khi lệch nặng** (TN khổng lồ ép FPR nhỏ). *Giảm thiểu:* dùng ROC chỉ để
so model; nhấn AUC-PR/F1 mới phản ánh thật; nêu rõ trong báo cáo.

**🟠 P20. XGBoost KHÔNG được khoá dạy `scale_pos_weight`.** Nếu quên, XGB thiên lớp đa số. *Giảm thiểu:*
đặt `scale_pos_weight ≈ n_neg/n_pos ≈ 11–12`; đây là "class_weight của XGB".

---

## 4. Tiền xử lý & Rò rỉ dữ liệu (Phần 2)

**🔴 P21. Fit scaler/encoder trên toàn bộ (gồm Test) = leakage → điểm ảo.** *Giảm thiểu:* `fit` CHỈ trên
Train A, `transform` cả hai; gói `Pipeline` để không quên.

**🔴 P22. Trong CV, scaler phải fit LẠI trong từng fold — nếu fit trước khi chia fold → rò rỉ chéo.**
*Giảm thiểu:* bọc `Pipeline([scaler, model])` rồi đưa vào RandomizedSearchCV; scaler chỉ gắn model tuyến tính.

**🔴 P23. SMOTE trước khi tách/ngoài CV = leakage nặng.** *Giảm thiểu:* nếu dùng SMOTE, để trong
`imblearn.Pipeline`, chỉ tác động lúc fit, nằm trong CV; tốt hơn: **ưu tiên class_weight**, SMOTE chỉ nhánh so sánh.

**🟠 P24. SMOTE sinh mẫu tổng hợp trên phân phối A → làm model bám gu A chặt hơn, PHẢN tác dụng dưới
covariate shift; còn có thể "đá nhau" với reweighting.** Lớp hỏng lại đa cụm (đuôi kép mômen) → nội suy
giữa 2 cụm tạo mẫu vô nghĩa. *Giảm thiểu:* class_weight làm chính; không kết hợp mù SMOTE + reweighting.

**🟠 P25. OneHotEncoder gặp mức lạ trên B → lỗi/cột lệch.** *Giảm thiểu:* `handle_unknown='ignore'`;
kiểm tra tập giá trị categorical A vs B.

**🟠 P26. Encode sai loại biến.** `loai_san_pham` L/M/H **có thứ tự** → Ordinal giữ thứ tự; `ca_lam_viec`
**không thứ tự** → One-hot. Label-encode nominal tạo thứ tự giả, LogReg học sai. *Giảm thiểu:* encode đúng
bản chất; `drop_first` cho LogReg tránh dummy trap.

**🟡 P27. Feature selection / importance chạy trên toàn bộ dữ liệu = rò rỉ.** *Giảm thiểu:* chọn feature
TRONG CV / chỉ trên Train.

**🟡 P28. Density-ratio classifier lỡ nhìn nhãn hỏng của B → rò rỉ tinh vi.** *Giảm thiểu:* chỉ dùng
đặc trưng (nhãn giả miền A/B), không đụng `hong_hoc` của B.

---

## 5. Feature Engineering (Phần 2 — 1.5đ)

**🔴 P29. Rubric đòi "KIỂM CHỨNG tác dụng" feature mới — nói "vì vật lý nên tốt" là chưa đủ.**
*Giảm thiểu:* (a) bivariate với nhãn (boxplot, point-biserial); (b) A/B trên leaderboard v0 vs v1
(F1/AUC-PR trên validation, không phải train); (c) |hệ số chuẩn hoá|/importance; (d) PSI/KS của feature mới.

**🟠 P30. FE tạo đa cộng tuyến** (`cong_suat_co` tương quan với cả momen & rpm) → hệ số LogReg mất ổn
định/khó diễn giải. *Giảm thiểu:* kiểm VIF/tương quan; cân nhắc L1/ElasticNet để tự loại; với cây thì ít ảnh hưởng.

**🟠 P31. Sai đơn vị công suất.** `cong_suat_co = momen × rpm × 2π/60` (W). Quên `2π/60` (đổi rpm→rad/s)
là sai vật lý — dễ bị hỏi. *Giảm thiểu:* ghi công thức + đơn vị rõ trong cell.

**🟡 P32. Over-engineer biến phân loại** dù EDA cho thấy gần như vô ích → tốn công, thêm nhiễu.
*Giảm thiểu:* encode đủ cho rubric, không đẻ thêm feature từ categorical.

---

## 6. Mô hình & Tuning (Phần 4 — 2.0đ)

**🔴 P33. Rubric yêu cầu ≥ 3 mô hình (KHÔNG phải 2).** Thiếu là mất điểm cứng. *Giảm thiểu:* LogReg + RF
+ XGB (đủ 3 trường phái) — đã chốt.

**🟠 P34. Dominant feature `do_mon_dao` làm cây RF tương quan cao (ρ lớn) → bagging mất tác dụng giảm
variance.** *Giảm thiểu:* đặt `max_features='sqrt'/'log2'`, ĐỪNG để `max_features=None` (thành bagging thuần).

**🟠 P35. XGB early stopping cần `eval_set` — nếu lỡ dùng Test B thì rò rỉ + chọn số cây "theo gu B thật".**
*Giảm thiểu:* eval_set = validation tách từ Train, lý tưởng có đánh trọng số IWV; combo η nhỏ + n_estimators
lớn + early stopping.

**🟠 P36. Không gian tuning rộng + `n_iter` nhỏ → RandomizedSearch bỏ lỡ vùng tối ưu.** *Giảm thiểu:*
coarse-to-fine; khoanh vùng prior theo slide; đủ `n_iter` (vd 30–60).

**🟠 P37. Hướng regularization dễ đặt SAI CHIỀU cho LogReg.** `C = 1/λ` → **C nhỏ = phạt mạnh** (ngược
`alpha`). Quét sai chiều là vô tình cho model tự do hơn dưới shift. *Giảm thiểu:* quét `C` về phía nhỏ
(`np.logspace(-3,1)`), thử `penalty='l1'/elasticnet` (solver saga), nhớ scale trước khi phạt.

**🟠 P38. AdaBoost (nếu thêm) nhạy noise cảm biến CNC → dễ gãy.** *Giảm thiểu:* không dùng làm ngựa chiến;
nếu nhắc thì chỉ để so sánh.

**🟡 P39. Chi phí tính toán.** RandomizedSearch × K-fold × 3 model × (repeated) × ensemble có thể nặng.
*Giảm thiểu:* `n_jobs=-1`, giới hạn `n_iter`, cache; XGB `hist`.

**🟡 P40. Reproducibility.** Thiếu `random_state` → kết quả nhảy giữa các lần build. *Giảm thiểu:* seed
mọi chỗ (split, model, search, SMOTE).

---

## 7. Ensemble (v5 — Kết quả 3.0đ)

**🔴 P41. Stacking rò rỉ nếu meta học trên dự đoán in-sample của base.** *Giảm thiểu:* **bắt buộc OOF**
(`StackingClassifier(cv=StratifiedKFold)`).

**🔴 P42. Meta học "gu A" → đặt cược nặng vào base mạnh-trên-A (XGB) mà XGB lại dễ gãy nhất trên B →
ensemble tệ hơn cả voting.** *Giảm thiểu:* meta **đơn giản (LogReg)**; huấn luyện meta trên OOF **có đánh
trọng số density-ratio**; giữ Voting làm đối trọng; chọn v5a/v5b bằng IWV.

**🟡 P43. Base model tương quan cao → ensemble lợi ít.** *Giảm thiểu:* đã chọn 3 trường phái decorrelated;
đừng kỳ vọng stacking thắng lớn (khoá học/thực tế: thêm <1%).

---

## 8. Đánh giá & Phương pháp luận

**🔴 P44. So model ở các ngưỡng khác nhau = so sai.** *Giảm thiểu:* cùng metric độc-lập-ngưỡng (AUC-PR)
để so; khi báo F1 thì nêu rõ ngưỡng.

**🟠 P45. Báo hiệu năng Test nhưng lỡ dùng nó để chỉnh = rò rỉ ngầm, điểm lạc quan giả.** *Giảm thiểu:*
Test chấm đúng 1 lần cuối; mọi lựa chọn qua IWV.

**🟡 P46. Quên đường cơ sở PR = tỉ lệ dương (~0.08).** *Giảm thiểu:* vẽ baseline trên PR-curve để thấy
model hơn "đoán mù" bao nhiêu.

---

## 9. Sản phẩm nộp & Quy trình

**🔴 P47. Notebook phải TỰ CHỨA, tiếng Việt, KHÔNG trích note cá nhân/wikilink** (theo quy ước nộp).
Mọi định nghĩa PSI/KS/drift/reweighting viết lại tự chứa. *Giảm thiểu:* rà soát trước khi nộp.

**🔴 P48. Notebook phải chạy từ đầu tới cuối KHÔNG lỗi, output đầy đủ, đúng thứ tự cell.** *Giảm thiểu:*
build bằng `build_notebook.py` (execute qua nbconvert) — đã có; kiểm imgs/errors mỗi lần.

**🟠 P49. `build_notebook.py` execute LẠI toàn bộ mỗi lần → khi thêm cell tuning nặng, rebuild có thể
chậm/timeout (nbconvert timeout=600s).** *Giảm thiểu:* giới hạn `n_iter`/`n_jobs`; nếu cần, tăng timeout
hoặc tách cell nặng; cân nhắc cache kết quả search.

**🟠 P50. Đổi tên file `bai_tap_cuoi_khoa_<MSSV>.ipynb`; xoá placeholder `<điền tên/MSSV>`.** *Giảm thiểu:*
checklist cuối.

**🟡 P51. Bài NHÓM — đồng bộ MSSV, phân công, tránh sửa đè.** *Giảm thiểu:* thống nhất 1 nguồn chân lý
(build script) + review.

---

## 10. Rủi ro "bản chất dữ liệu"

**🟠 P52. Nhãn hỏng có thể theo luật vật lý gần tất định (kiểu AI4I).** Feature của ta có thể chỉ là
*proxy* → trần hiệu năng bị giới hạn nếu thiếu đúng biến tương tác. *Giảm thiểu:* FE cơ học đúng 4 cơ
chế hỏng để tiệm cận luật thật.

**🟡 P53. `do_mon_dao` bị chặn [0, 253] giống hệt A và B** → có thể đã cắt/bão hoà; ổn định qua shift là
lợi thế nhưng cũng có thể che mất tín hiệu ở đuôi. *Giảm thiểu:* kiểm mật độ ở biên 253.

**🟡 P54. Chỉ 5 biến số + 2 phân loại, 2 phân loại gần vô ích → dư địa feature hẹp.** *Giảm thiểu:* dồn
sức vào FE cơ học chất lượng thay vì số lượng.

---

### Xếp ưu tiên xử lý (top nên canh)
1. **P0/P1/P2/P3** — trục shift + ngoại suy + giả định covariate (định hình cả bài).
2. **P9/P10/P12** — Phần 3 ngoài khoá, phải tự định nghĩa chuẩn để ăn 2.0đ.
3. **P15/P16/P21/P22/P23** — rò rỉ + metric sai là mất điểm/điểm ảo tức thì.
4. **P29/P33/P41/P42** — kiểm chứng FE, đủ 3 model, ensemble không rò rỉ/không lệch cược.
5. **P47/P48** — điều kiện nộp bài, hỏng là mất điểm oan.
