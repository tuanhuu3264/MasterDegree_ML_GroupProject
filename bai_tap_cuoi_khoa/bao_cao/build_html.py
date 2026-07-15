# -*- coding: utf-8 -*-
"""Dung file HTML bao cao (nhung anh base64) -> bao_cao/bao_cao.html"""
import base64, os, sys
sys.stdout.reconfigure(encoding='utf-8')

OUT = 'bao_cao/assets/'
def img(name):
    with open(OUT+name,'rb') as f:
        b = base64.b64encode(f.read()).decode()
    return f'data:image/png;base64,{b}'

I = {k: img(v) for k,v in {
    'journey':'01_journey.png','shift':'02_shift.png','psi':'03_psi.png',
    'inv':'04_invariance.png','cm':'05_confusion.png','drift':'06_drift.png'}.items()}

HTML = f"""<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8">
<style>
  @page {{ size: A4; margin: 18mm 16mm 20mm 16mm; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI','Arial',sans-serif; color:#1e293b; font-size:10.5pt;
         line-height:1.55; margin:0; }}
  h1,h2,h3,h4 {{ color:#0f172a; line-height:1.25; }}
  h2 {{ font-size:15pt; border-bottom:2.5px solid #2563eb; padding-bottom:4px;
        margin-top:22px; margin-bottom:10px; }}
  h3 {{ font-size:12pt; color:#1d4ed8; margin-top:16px; margin-bottom:6px; }}
  h4 {{ font-size:10.8pt; margin:10px 0 4px; }}
  p {{ margin:6px 0; text-align:justify; }}
  ul,ol {{ margin:6px 0 6px 0; padding-left:20px; }}
  li {{ margin:3px 0; }}
  code {{ background:#f1f5f9; padding:1px 5px; border-radius:3px; font-size:9.5pt;
          font-family:'Consolas',monospace; color:#be123c; }}
  table {{ border-collapse:collapse; width:100%; margin:10px 0; font-size:9.5pt; }}
  th,td {{ border:1px solid #cbd5e1; padding:5px 8px; text-align:left; vertical-align:top; }}
  th {{ background:#eff6ff; color:#0f172a; font-weight:600; }}
  tr:nth-child(even) td {{ background:#f8fafc; }}
  .center {{ text-align:center; }}
  img.chart {{ max-width:100%; display:block; margin:8px auto; }}
  .fig {{ text-align:center; margin:12px 0; }}
  .cap {{ font-size:9pt; color:#64748b; font-style:italic; margin-top:2px; }}
  .box {{ background:#f8fafc; border:1px solid #e2e8f0; border-left:4px solid #2563eb;
          padding:10px 14px; margin:12px 0; border-radius:4px; }}
  .box.ok {{ border-left-color:#059669; background:#f0fdf4; }}
  .box.warn {{ border-left-color:#f59e0b; background:#fffbeb; }}
  .kpi-row {{ display:flex; gap:10px; margin:14px 0; }}
  .kpi {{ flex:1; text-align:center; background:#0f172a; color:#fff; border-radius:8px;
          padding:12px 6px; }}
  .kpi .v {{ font-size:19pt; font-weight:700; color:#38bdf8; }}
  .kpi .l {{ font-size:8.5pt; color:#cbd5e1; margin-top:2px; }}
  .formula {{ background:#0f172a; color:#e2e8f0; padding:8px 12px; border-radius:5px;
              font-family:'Consolas',monospace; font-size:9.5pt; margin:6px 0; }}
  .pagebreak {{ page-break-before:always; }}
  .cover {{ text-align:center; padding-top:60px; }}
  .cover .badge {{ display:inline-block; background:#2563eb; color:#fff; padding:5px 16px;
                   border-radius:20px; font-size:9.5pt; letter-spacing:1px; margin-bottom:24px; }}
  .cover h1 {{ font-size:26pt; margin:8px 0; color:#0f172a; }}
  .cover .sub {{ font-size:13pt; color:#475569; margin:6px 0; }}
  .cover .meta {{ margin-top:40px; font-size:11pt; color:#334155; }}
  .cover .meta div {{ margin:5px 0; }}
  .tag {{ display:inline-block; background:#dbeafe; color:#1e40af; padding:1px 7px;
          border-radius:4px; font-size:8.5pt; margin:1px; }}
  .footer-note {{ font-size:8.5pt; color:#94a3b8; text-align:center; margin-top:30px;
                  border-top:1px solid #e2e8f0; padding-top:8px; }}
  .two {{ display:flex; gap:16px; }}
  .two > div {{ flex:1; }}
  strong {{ color:#0f172a; }}
</style></head>
<body>

<!-- ================= COVER ================= -->
<div class="cover">
  <div class="badge">BÀI TẬP CUỐI KHÓA · MACHINE LEARNING</div>
  <h1>Dự đoán Hỏng hóc Thiết bị CNC<br>dưới Distribution Shift</h1>
  <div class="sub">Bảo trì dự đoán (Predictive Maintenance) · Phân loại nhị phân lệch lớp</div>
  <div class="sub" style="font-size:11pt;color:#64748b;">Chuyển giao mô hình Dây chuyền A → Dây chuyền B</div>
  <div class="kpi-row" style="max-width:520px;margin:40px auto;">
    <div class="kpi"><div class="v">0.781</div><div class="l">F1 (Dây chuyền B)</div></div>
    <div class="kpi"><div class="v">0.872</div><div class="l">AUC-ROC</div></div>
    <div class="kpi"><div class="v">0.670</div><div class="l">AUC-PR</div></div>
    <div class="kpi"><div class="v">3.4×</div><div class="l">so với baseline</div></div>
  </div>
  <div class="meta">
    <div><strong>Nhóm thực hiện:</strong> ____________________________</div>
    <div><strong>Thành viên / MSSV:</strong> ____________________________</div>
    <div><strong>Môn học:</strong> Machine Learning — Thạc sĩ Kỹ thuật Phần mềm (MSE)</div>
    <div><strong>Bộ dữ liệu:</strong> AI4I 2020 (biến thể) · Train A (14.000) · Test B (6.000)</div>
  </div>
  <div class="footer-note">Toàn bộ lựa chọn mô hình/ngưỡng thực hiện bằng Importance-Weighted Validation —
  không nhìn nhãn Test. Số liệu trong báo cáo tái lập tất định từ dữ liệu gốc.</div>
</div>

<!-- ================= 1. TOM TAT DIEU HANH ================= -->
<div class="pagebreak"></div>
<h2>1. Tóm tắt điều hành</h2>
<p>Bài toán yêu cầu dự đoán máy CNC <strong>hỏng ở ca kế tiếp</strong> (nhãn <code>hong_hoc</code> ∈ {{0,1}},
tỉ lệ hỏng ~8%). Thách thức cốt lõi <strong>không nằm ở thuật toán</strong> mà ở <strong>distribution
shift</strong>: mô hình huấn luyện trên <strong>Dây chuyền A</strong> (nhà máy cũ) nhưng phải chạy tốt trên
<strong>Dây chuyền B</strong> (nhà máy mới — nóng hơn +2.5°, quay nhanh hơn +70 rpm). Nếu huấn luyện ngây thơ,
mô hình học "biên quyết định" theo phân phối của A và <strong>sụp đổ trên B</strong>.</p>

<div class="box ok">
<strong>Luận điểm xuyên suốt.</strong> Thay vì vá mô hình đã học biên bị dịch, chúng tôi <strong>dựng đặc trưng
trên hằng số vật lý bất biến</strong> (ngưỡng sinh lỗi HDF/PWF/OSF của máy). Nhờ đó biên học trên A
<strong>chuyển thẳng</strong> sang B (PSI ≈ 0, Drift-AUC 0.51). Các lớp reweighting · hiệu chỉnh ngưỡng ·
ensemble chỉ là tinh chỉnh cuối — tất cả chọn bằng <strong>IWV, không rò rỉ nhãn Test</strong>.</div>

<p><strong>Kết quả chốt (bản v6 — Voting RF+XGB, ngưỡng 0.705):</strong> F1 = <strong>0.781</strong>,
AUC-ROC = 0.872, AUC-PR = 0.670, Precision = 0.812, Recall = 0.753 trên Dây chuyền B — tăng
<strong>3.4 lần</strong> so với baseline Logistic Regression (F1 = 0.231).</p>

<div class="fig"><img class="chart" src="{I['journey']}" style="max-width:88%;">
<div class="cap">Hình 1. Hành trình cải tiến qua 6 phiên bản. Bước nhảy lớn nhất đến từ feature engineering
vật lý (v0→v1), không phải từ thuật toán phức tạp hơn.</div></div>

<!-- ================= 2. BOI CANH & BAI TOAN ================= -->
<h2>2. Bối cảnh &amp; Phát biểu bài toán</h2>

<h3>2.1 Bài toán nghiệp vụ</h3>
<p>Bảo trì dự đoán cho phép thay dao/kiểm tra máy <em>trước khi</em> hỏng, tránh dừng dây chuyền đột ngột.
Đây là bài <strong>phân loại nhị phân</strong>: nhãn <code>hong_hoc</code> = 1 nếu máy sẽ hỏng ở ca kế tiếp.
Sai lầm <strong>bỏ sót (FN — máy hỏng bất ngờ)</strong> thường đắt hơn <strong>báo động giả (FP)</strong>,
nên ưu tiên Recall nhưng chốt bằng F1 / AUC-PR (do lệch lớp).</p>

<h3>2.2 Dữ liệu</h3>
<table>
<tr><th>Thuộc tính</th><th>Chi tiết</th></tr>
<tr><td>Kích thước</td><td>Train A: 14.000 × 8 · Test B: 6.000 × 8 · <strong>0 giá trị thiếu, 0 hàng trùng</strong></td></tr>
<tr><td>5 biến số</td><td>nhiệt độ môi trường, nhiệt độ quy trình, tốc độ quay, mômen xoắn, độ mòn dao</td></tr>
<tr><td>2 biến phân loại</td><td><code>loai_san_pham</code> (L&lt;M&lt;H — có thứ tự) · <code>ca_lam_viec</code> (danh nghĩa)</td></tr>
<tr><td>Nhãn</td><td><code>hong_hoc</code> ∈ {{0,1}} — tỉ lệ hỏng A: 7.36% · B: 7.95%</td></tr>
</table>

<h3>2.3 Thách thức cốt lõi — Distribution Shift A→B</h3>
<p>Đây là <strong>covariate shift</strong>: phân phối đầu vào P(x) dịch chuyển, nhưng cơ chế P(y|x) ổn định.
Bằng chứng: tỉ lệ nhãn gần như không đổi (7.36% → 7.95%), trong khi các biến vật lý dịch mạnh và
<strong>có hướng</strong> — B là nhà máy nóng hơn, quay nhanh hơn.</p>

<div class="fig"><img class="chart" src="{I['shift']}">
<div class="cap">Hình 2. Chồng phân phối A (xanh) vs B (đỏ). Nhiệt độ &amp; tốc độ dịch rõ; độ mòn dao ổn định.</div></div>

<h3>2.4 Tại sao cấm accuracy</h3>
<p>Với chỉ ~8% máy hỏng, một mô hình "đoán không hỏng" cho mọi máy đã đạt <strong>92% accuracy</strong>
nhưng Recall = 0% — vô dụng. Do đó độ đo được chốt <strong>từ đầu</strong>: <strong>AUC-PR / F1 / AUC-ROC /
Precision / Recall</strong> (không accuracy), kèm bootstrap 95% CI cho F1.</p>

<!-- ================= 3. EDA ================= -->
<div class="pagebreak"></div>
<h2>3. Phân tích khám phá — những phát hiện định hướng</h2>
<p>EDA ở bài này khác thường lệ: ngoài hiểu dữ liệu, mục tiêu chính là <strong>đo và định vị shift</strong>
để chọn chiến lược. Bốn phát hiện dẫn dắt toàn bộ quyết định kỹ thuật:</p>

<table>
<tr><th>#</th><th>Phát hiện</th><th>Hệ quả cho mô hình</th></tr>
<tr><td>1</td><td>Lệch lớp ~8%, ổn định A→B</td><td>Cấm accuracy → F1/AUC-PR; là covariate shift → hợp reweighting</td></tr>
<tr><td>2</td><td>Nhiệt độ/tốc độ B dịch mạnh (còn phân tán rộng hơn ~30%)</td><td>Không dùng thẳng biến thô làm biên; cần feature bất biến</td></tr>
<tr><td>3</td><td><code>do_mon_dao</code> là tín hiệu #1 (corr +0.20) &amp; ổn định</td><td>Mỏ neo dự báo — vừa dự đoán tốt vừa can thiệp được (thay dao)</td></tr>
<tr><td>4</td><td>Tín hiệu hỏng chủ yếu <strong>phi tuyến / theo tương tác</strong> (2 đuôi)</td><td>Cần mô hình cây + feature cơ học, không tuyến tính thuần</td></tr>
</table>

<div class="box warn"><strong>Rủi ro ngoại suy (P2).</strong> ~2.8% dòng B nằm <strong>ngoài dải giá trị của A</strong>
(rõ nhất: tốc độ max B 2414 &gt; max A 2153). Mô hình cây <strong>không ngoại suy</strong> — dự đoán phẳng
ngoài vùng đã thấy. Đây là lý do giữ Logistic Regression trong ensemble như lớp phòng thủ.</div>

<!-- ================= 4. QUYET DINH KY THUAT ================= -->
<h2>4. Quyết định kỹ thuật cốt lõi</h2>

<h3>4.1 Feature engineering — 3 đặc trưng "khoảng-cách-tới-biên" vật lý</h3>
<p>Bộ dữ liệu AI4I có <strong>ngưỡng sinh lỗi vật lý cố định</strong>. Chúng tôi chế 3 đặc trưng, mỗi cái là
một <em>hinge</em> (bản lề) chỉ "bật" khi máy tiến vào vùng nguy hiểm — đo <strong>khoảng cách tới biên</strong>
chứ không phải giá trị thô:</p>

<table>
<tr><th>Feature</th><th>Công thức</th><th>Cơ chế &amp; logic</th></tr>
<tr><td><code>nguy_tan_nhiet</code></td>
    <td>max(8.6−ΔT, 0) × max(1380−tốc_độ, 0)</td>
    <td><strong>HDF</strong> (tản nhiệt kém) — tích 2 hinge = phép <strong>AND</strong>: chỉ &gt;0 khi CẢ
        chênh nhiệt &lt; 8.6 K VÀ tốc độ &lt; 1380 rpm</td></tr>
<tr><td><code>lech_cong_suat</code></td>
    <td>max(3500−P, 0) + max(P−9000, 0)<br>với P = mômen×tốc_độ×2π/60</td>
    <td><strong>PWF</strong> (công suất) — tổng 2 hinge = phép <strong>OR</strong>: khoảng cách ra ngoài dải
        an toàn [3500, 9000] W (thiếu HOẶC thừa)</td></tr>
<tr><td><code>bien_overstrain</code></td>
    <td>độ_mòn × mômen − ngưỡng(loại)<br>{{L:11000, M:12000, H:13000}}</td>
    <td><strong>OSF</strong> (overstrain) — biên có dấu theo loại sản phẩm (chỗ <code>loai_san_pham</code>
        thật sự có ích)</td></tr>
</table>

<div class="box"><strong>Vì sao hinge <code>max(0,·)</code>, không chỉ phép trừ?</strong> Máy ở vùng an toàn
<em>không cần</em> phân biệt xa hay gần biên — chỉ cần về 0. Chỉ máy vào vùng nguy mới cần biết "nguy đến đâu".
Hinge nén phẳng vùng an toàn về 0, giữ tín hiệu ở đúng vùng quan trọng. <strong>Đây cũng là lý do ngưỡng
HDF/PWF thật sự ảnh hưởng kết quả</strong> (đổi ngưỡng → đổi nhóm máy bị nén về 0 → đổi thứ hạng), trong khi
<code>bien_overstrain</code> (không hinge) bất biến với dịch hằng số của ngưỡng.</div>

<div class="box ok"><strong>Kết quả đột phá.</strong> Chỉ thêm 3 feature này vào <em>chính LogReg cũ</em>:
F1 <strong>0.231 → 0.352</strong>, AUC-PR <strong>0.220 → 0.501</strong> (gấp ~2.3×). Feature vật lý — không
phải thuật toán mạnh hơn — mới là đòn bẩy lớn nhất.</div>

<h3>4.2 Tại sao ngưỡng vật lý bất biến qua shift</h3>
<p>Hằng số 8.6 / 1380 / 3500 / 9000 là <strong>thuộc tính vật lý của máy</strong>, không ước lượng từ phân
phối A. Vì vậy dù biến thô dịch mạnh, feature biên "hấp thụ" shift — PSI ≈ 0. Đây là "reweighting của người
nghèo": xử lý shift ngay tại tầng đặc trưng thay vì tầng mô hình.</p>

<div class="fig"><img class="chart" src="{I['psi']}">
<div class="cap">Hình 3. PSI theo từng feature. Biến thô (đỏ) shift mạnh — nhiệt độ MT tới 1.08; ba feature biên (★, xanh)
gần như bằng 0 dù dựng từ chính các biến nhiệt độ/tốc độ dịch mạnh.</div></div>

<h3>4.3 Bằng chứng bất biến — P(hỏng | vượt-biên) đứng yên</h3>
<p>PSI chứng minh <em>input</em> dịch. Câu hỏi sống-còn: cơ chế hỏng có dịch không? Ta so Precision của mỗi
luật vật lý trên A vs B — nếu bằng nhau nghĩa là P(y | cơ_chế) bất biến (đúng giả định covariate shift):</p>

<div class="two">
<div class="fig"><img class="chart" src="{I['inv']}">
<div class="cap">Hình 4. P(hỏng | cờ luật) gần như đứng yên A→B.</div></div>
<div class="fig"><img class="chart" src="{I['drift']}">
<div class="cap">Hình 5. Drift Classifier: feature biên không phân biệt được A/B (AUC 0.51).</div></div>
</div>
<p>Ba lát cắt độc lập (PSI · bảng bất biến Precision · Drift-AUC) <strong>cùng một kết luận</strong>: shift nằm
trọn trong biến thô, feature biên "trong suốt" với shift → covariate shift <em>sạch</em>, xử lý được bằng
feature bất biến.</p>

<!-- ================= tiep tuc ================= -->
<div class="pagebreak"></div>
<h3>4.4 Chiến lược mô hình — từ baseline đến ensemble</h3>
<p>Nguyên tắc: bắt đầu <strong>baseline đơn giản</strong> rồi nâng dần, mỗi bước cô lập đúng một đóng góp:</p>
<ul>
<li><strong>v0</strong> — Logistic Regression thô, <code>class_weight='balanced'</code>, scaler fit chỉ trên train (mốc tham chiếu).</li>
<li><strong>v1</strong> — thêm 3 feature biên (giữ nguyên LogReg → đo đúng đóng góp của FE).</li>
<li><strong>v2</strong> — 3 mô hình cây (Random Forest · XGBoost · ExtraTrees), tune bằng
    <code>RandomizedSearchCV</code> + <code>StratifiedKFold(5)</code>, scoring = <strong>AUC-PR</strong>.
    Cây <code>passthrough</code> (không cần scale).</li>
<li><strong>v3</strong> — Importance Reweighting (density-ratio từ Drift Classifier, clip [0.2, 10]).</li>
<li><strong>v4</strong> — Threshold Calibration bằng IWV.</li>
<li><strong>v5/v6</strong> — Ensemble Voting &amp; Stacking; chốt bằng IWV.</li>
</ul>

<h3>4.5 IWV — chọn mô hình/ngưỡng mà KHÔNG nhìn nhãn Test</h3>
<div class="box"><strong>Nghịch lý chấm điểm.</strong> Bài chấm trên B nhưng không được nhìn nhãn B để chọn cấu
hình. <strong>Lời giải — Importance-Weighted Validation (IWV):</strong> dùng xác suất out-of-fold trên Train A,
đánh trọng số density-ratio (mẫu A "giống B" nặng hơn) để mô phỏng phân phối B, rồi chọn mô hình/ngưỡng tối đa
F1-có-trọng-số. Toàn bộ chọn lựa "như thể đứng ở B" mà chỉ dùng dữ liệu A. Test chỉ chấm <strong>một lần cuối</strong>.</div>
<p>Kiểm chứng: ngưỡng IWV (0.625) rất sát ngưỡng oracle-trên-B (0.551) → IWV đáng tin. Hạn chế: effective
sample size chỉ 25.5% → ước lượng IWV nhiễu (bàn ở mục 7).</p>

<h3>4.6 Xử lý shift — vì sao các lớp bù chỉ cho gain nhỏ</h3>
<p>Reweighting (v3) và threshold-calibration (v4) gần như đi ngang (AUC-PR 0.665 → 0.676 → 0.676). Đây
<strong>là tin tốt, không phải thất bại</strong>: feature biên vật lý đã hấp thụ phần lớn shift (Drift-AUC riêng
feature biên chỉ 0.51), nên các lớp bù thống kê chỉ vá phần sót. Kết luận: <em>FE vật lý đúng làm giảm nhu cầu
bù shift bằng thống kê</em>.</p>

<!-- ================= 5. KET QUA ================= -->
<h2>5. Kết quả</h2>

<h3>5.1 Bảng tổng hợp hành trình cải tiến</h3>
<table>
<tr><th>Mốc</th><th>Ý tưởng chính</th><th>F1 (B)</th><th>AUC-PR (B)</th></tr>
<tr><td>v0</td><td>LogReg thô, class_weight</td><td>0.231</td><td>0.220</td></tr>
<tr><td>v1</td><td>+3 feature khoảng-cách-tới-biên vật lý (cứu LogReg)</td><td>0.352</td><td>0.501</td></tr>
<tr><td>v2</td><td>Mô hình cây (RF/XGB/ExtraTrees) tuned</td><td>~0.77</td><td>0.66–0.67</td></tr>
<tr><td>v3</td><td>Importance Reweighting (density-ratio, clip)</td><td>0.772</td><td><strong>0.676</strong></td></tr>
<tr><td>v4</td><td>Threshold Calibration bằng IWV</td><td>0.771</td><td>0.676</td></tr>
<tr style="background:#f0fdf4;"><td><strong>v6</strong></td><td><strong>Voting (RF+XGB) — chốt bằng IWV</strong></td><td><strong>0.781</strong></td><td>0.670</td></tr>
</table>

<h3>5.2 Kết quả chốt trên Dây chuyền B</h3>
<div class="two">
<div>
<p>Bản chốt <strong>v6 = Voting</strong> trọng số RF 0.5 / XGB 0.5, ngưỡng 0.705 (chọn bằng IWV):</p>
<table>
<tr><th>Độ đo</th><th>Giá trị</th></tr>
<tr><td>F1</td><td><strong>0.781</strong></td></tr>
<tr><td>AUC-ROC</td><td>0.872</td></tr>
<tr><td>AUC-PR</td><td>0.670</td></tr>
<tr><td>Precision</td><td>0.812</td></tr>
<tr><td>Recall</td><td>0.753</td></tr>
</table>
<p style="font-size:9.5pt;">Đọc ma trận: trong 477 máy thực sự hỏng ở B, bắt được <strong>359</strong> (TP), bỏ sót
<strong>118</strong> (FN); phát 442 cảnh báo thì <strong>83</strong> là báo động giả (FP). Cứ ~5 cảnh báo có ~4 đúng.</p>
</div>
<div class="fig"><img class="chart" src="{I['cm']}" style="max-width:96%;">
<div class="cap">Hình 6. Ma trận nhầm lẫn v6 tại ngưỡng chốt.</div></div>
</div>

<h3>5.3 Độ tin cậy — bootstrap 95% CI</h3>
<ul>
<li><strong>F1 = 0.781, 95% CI = [0.751, 0.809]</strong> (±0.03): CI rộng vì chỉ 477 mẫu hỏng ở B → giá trị
tuyệt đối của F1 kém chắc chắn.</li>
<li><strong>So sánh cặp mới đúng:</strong> trên cùng resample, P(F1<sub>v6</sub> &gt; F1<sub>xgb</sub>) = 99.8%,
delta = +0.009 với 95% CI [+0.003, +0.015] nằm trọn phía dương → ensemble nhỉnh <strong>nhất quán về hướng</strong>
dù biên độ nhỏ (~0.9%).</li>
<li><strong>Ngưỡng robust:</strong> đỉnh F1-theo-ngưỡng <em>phẳng</em> quanh 0.705 → F1 ít đổi khi ngưỡng dao động ±0.05.</li>
</ul>

<!-- ================= 6. INSIGHT VAN HANH ================= -->
<div class="pagebreak"></div>
<h2>6. Insight vận hành &amp; bảo trì</h2>

<h4>① Độ mòn dao là "kim chỉ nam" bảo trì</h4>
<p><code>do_mon_dao</code> là tín hiệu số 1 <strong>và</strong> ổn định qua shift (PSI ≈ 0, importance dẫn đầu
ở mọi mô hình). Ưu tiên số một cho đội bảo trì: <strong>giám sát và thay dao đúng chu kỳ</strong> — biến vừa
dự báo tốt vừa <em>can thiệp được</em> (khác nhiệt độ/tốc độ do quy trình quyết định).</p>

<h4>② Cảnh báo theo ngưỡng vật lý dùng được xuyên nhà máy</h4>
<p>P(hỏng | vượt-biên) gần như đứng yên A→B (HDF .84→.83, OSF .40→.37). Hệ quả vận hành: <strong>có thể đặt
cảnh báo theo ngưỡng ngay cả khi đổi máy/dây chuyền</strong>, không cần train lại từ đầu — tiết kiệm chi phí
triển khai khi mở rộng nhà máy.</p>

<h4>③ Cân bằng báo động giả ↔ bỏ sót</h4>
<p>Vì bỏ sót (FN — máy hỏng bất ngờ, dừng dây chuyền) thường <strong>đắt hơn</strong> báo động giả (kiểm tra
thừa), có thể <strong>hạ ngưỡng để tăng Recall</strong> khi chi phí dừng máy thấp. Mô hình độc-lập-ngưỡng
(AUC-PR/PR-curve) cho phép chọn điểm vận hành theo chi phí thực tế.</p>

<div class="box ok"><strong>Khuyến nghị 2 mức cảnh báo.</strong>
<table style="margin:6px 0;">
<tr><th>Mức</th><th>Ngưỡng</th><th>Ưu tiên</th><th>Hành động vận hành</th></tr>
<tr><td>🔴 Đỏ</td><td>Cao</td><td>Precision</td><td>Lệnh <strong>dừng máy kiểm tra ngay</strong> — độ tin cậy cao, ít báo nhầm</td></tr>
<tr><td>🟡 Vàng</td><td>Thấp</td><td>Recall</td><td><strong>Theo dõi tăng cường</strong> / lên lịch bảo trì gần — bắt thêm máy nghi ngờ</td></tr>
</table></div>

<!-- ================= 7. HAN CHE ================= -->
<h2>7. Hạn chế (trung thực về phương pháp)</h2>
<table>
<tr><th>Hạn chế</th><th>Bản chất &amp; ảnh hưởng</th></tr>
<tr><td><strong>Cây không ngoại suy (P2)</strong></td>
    <td>~2.8% dòng B ngoài dải A → RF/XGB dự đoán phẳng, có thể sai hệ thống ở vùng B mở rộng. LogReg trong
        ensemble bù một phần nhưng vẫn là rủi ro.</td></tr>
<tr><td><strong>Giả định covariate shift chưa chứng minh trực tiếp (P3)</strong></td>
    <td>Reweighting/IWV chỉ đúng nếu P(hỏng|đặc-trưng) bất biến. Ta biện minh bằng vật lý + prior nhãn ổn định
        (7.4%→8.0%), nhưng <strong>không có nhãn B để chứng minh</strong>. Nếu B có concept drift thật thì
        density-ratio vô hiệu.</td></tr>
<tr><td><strong>Độ tin IWV giới hạn</strong></td>
    <td>Effective sample size chỉ 25.5% (vài mẫu A hiếm ở vùng B mang trọng số lớn) → IWV nhiễu. Khoảng cách
        Voting↔Stacking (0.794 vs 0.791) nằm trong sai số → coi hai bản gần tương đương; chọn Voting vì đơn
        giản, khó overfit shift hơn.</td></tr>
<tr><td><strong>Dư địa còn lại hẹp</strong></td>
    <td>Gain reweighting &amp; threshold-cal nhỏ vì FE đã hấp thụ phần lớn shift — câu chuyện đẹp nhưng cũng
        nghĩa là ít không gian cải thiện thêm bằng kỹ thuật shift.</td></tr>
<tr><td><strong>Trần dữ liệu</strong></td>
    <td>Chỉ 5 biến số + 2 phân loại (2 phân loại gần vô ích), nhãn theo luật gần tất định (kiểu AI4I) → trần
        hiệu năng bị giới hạn; feature của ta là <em>proxy</em> của luật thật.</td></tr>
</table>

<!-- ================= 8. HUONG CAI TIEN ================= -->
<h2>8. Hướng cải tiến</h2>
<ol>
<li><strong>Hiệu chỉnh lại hằng số ngưỡng PWF.</strong> Precision luật PWF chỉ ~0.17 → dải [3500, 9000] W có
thể lệch. Ước lượng lại hai mép bằng phân vị công suất của nhóm hỏng/không-hỏng <strong>trên A</strong> (không
nhìn B). <em>(Thí nghiệm phụ lục A cho thấy thu hẹp dải PWF nâng precision cờ từ 0.17 → 0.49.)</em></li>
<li><strong>Đặc trưng theo thời gian.</strong> Nếu có dữ liệu chuỗi, bắt <strong>xu hướng mòn dao</strong> thay
vì ảnh chụp tức thời → cảnh báo sớm hơn.</li>
<li><strong>Domain adaptation nâng cao</strong> (CORAL, adversarial feature alignment) thay reweighting đơn
giản để xử lý phần shift còn sót ở đuôi phân phối.</li>
<li><strong>Thu thập một ít nhãn B</strong> (active learning trên máy được cảnh báo) → kiểm chứng trực tiếp
giả định covariate shift và tinh chỉnh ngưỡng trên phân phối thật.</li>
<li><strong>Conformal prediction</strong> để kèm khoảng tin cậy cho mỗi cảnh báo — hữu ích cho quyết định vận hành.</li>
</ol>

<!-- ================= 9. KET LUAN ================= -->
<h2>9. Kết luận</h2>
<p>Hai ô trọng số của rubric — <strong>Xử lý Shift (2.0đ)</strong> và <strong>Kết quả trên B (3.0đ)</strong> —
được giải bằng một luận điểm xuyên suốt: <strong>dựng đặc trưng trên hằng số vật lý bất biến</strong> thay vì
vá mô hình đã học biên dịch chuyển. Nhờ đó biên học trên Dây chuyền A <strong>transfer thẳng</strong> sang Dây
chuyền B; reweighting, threshold-calibration và ensemble chỉ là các lớp tinh chỉnh cuối — tất cả <strong>chọn
bằng IWV, không rò rỉ nhãn Test</strong>.</p>
<p class="center" style="font-size:12pt;margin-top:16px;">
<strong>Kết quả: F1 = 0.781 trên Dây chuyền B — tăng 3.4 lần so với baseline (0.231).</strong></p>

<div class="footer-note">Báo cáo sinh tự động từ notebook <code>bai_tap_cuoi_khoa.ipynb</code>. Biểu đồ &amp; số liệu
(PSI, ma trận nhầm lẫn, bằng chứng bất biến) tái lập tất định từ <code>Data_Final/</code>. Các độ đo mô hình
(F1/AUC/CI) lấy từ kết quả chạy notebook.</div>

</body></html>"""

with open('bao_cao/bao_cao.html','w',encoding='utf-8') as f:
    f.write(HTML)
print('HTML written: bao_cao/bao_cao.html', f'({len(HTML)} chars)')
