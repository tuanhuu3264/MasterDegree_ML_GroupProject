# -*- coding: utf-8 -*-
"""Dung file HTML bao cao (nhung anh base64) -> bao_cao/bao_cao.html
Phong cach HOC THUAT: giong khach quan, font serif, danh so Bang/Hinh, khong emoji."""
import base64, sys
sys.stdout.reconfigure(encoding='utf-8')

OUT = 'bao_cao/assets/'
def img(name):
    with open(OUT+name,'rb') as f:
        b = base64.b64encode(f.read()).decode()
    return f'data:image/png;base64,{b}'

I = {k: img(v) for k,v in {
    'journey':'01_journey.png','shift':'02_shift.png','psi':'03_psi.png',
    'inv':'04_invariance.png','cm':'05_confusion.png','drift':'06_drift.png',
    'hinge':'07_hinge.png','reweight':'08_reweight.png'}.items()}

HTML = f"""<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8">
<style>
  @page {{ size: A4; margin: 22mm 20mm 20mm 22mm; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: 'Cambria','Georgia','Times New Roman',serif; color:#1a1a1a;
         font-size:11pt; line-height:1.5; margin:0; text-align:justify; }}
  h1,h2,h3,h4 {{ font-family:'Cambria','Georgia',serif; color:#14243d; line-height:1.3; }}
  h2 {{ font-size:14pt; margin-top:20px; margin-bottom:8px; padding-bottom:3px;
        border-bottom:1px solid #14243d; }}
  h3 {{ font-size:12pt; color:#1f3a5f; margin-top:14px; margin-bottom:5px; }}
  h4 {{ font-size:11pt; margin:9px 0 3px; color:#14243d; font-style:italic; }}
  p {{ margin:6px 0; }}
  ul,ol {{ margin:6px 0; padding-left:22px; }}
  li {{ margin:3px 0; }}
  code {{ font-family:'Consolas','Courier New',monospace; font-size:9.6pt;
          background:#f4f4f4; padding:0 3px; color:#333; }}
  table {{ border-collapse:collapse; width:100%; margin:8px 0 4px; font-size:9.6pt;
           font-family:'Calibri','Segoe UI',sans-serif; }}
  th,td {{ border:1px solid #b8bfc9; padding:5px 8px; text-align:left; vertical-align:top; }}
  th {{ background:#e8ecf2; color:#14243d; font-weight:700; }}
  caption {{ caption-side:top; text-align:left; font-size:9.5pt; font-style:italic;
             color:#333; margin-bottom:3px; padding-left:2px; }}
  .center {{ text-align:center; }}
  img.chart {{ max-width:100%; display:block; margin:6px auto; }}
  .fig {{ text-align:center; margin:12px 0; }}
  .cap {{ font-size:9.3pt; color:#333; margin-top:3px; text-align:center;
          font-family:'Calibri',sans-serif; }}
  .cap b {{ color:#14243d; }}
  .abstract {{ background:#f7f8fa; border:1px solid #d5dbe4; padding:12px 18px;
               margin:14px 0; font-size:10.5pt; }}
  .abstract .h {{ font-weight:700; font-style:italic; color:#14243d; }}
  .note {{ border-left:3px solid #1f3a5f; padding:4px 0 4px 12px; margin:10px 0;
           background:#fafbfc; }}
  .note .t {{ font-weight:700; color:#14243d; }}
  .formula {{ text-align:center; font-family:'Cambria Math','Cambria',serif;
              font-size:11.5pt; margin:9px 0; font-style:italic; }}
  .formula .cmt {{ font-family:'Calibri',sans-serif; font-style:normal;
                   font-size:9pt; color:#555; }}
  .pagebreak {{ page-break-before:always; }}
  .avoid-break {{ page-break-inside:avoid; }}
  .cover {{ text-align:center; padding-top:40px; }}
  .cover .inst {{ font-size:11pt; letter-spacing:0.5px; color:#333; text-transform:uppercase; }}
  .cover .rule {{ width:70px; border-top:2px solid #14243d; margin:18px auto; }}
  .cover h1 {{ font-size:23pt; margin:14px 30px; color:#14243d; line-height:1.35; }}
  .cover .sub {{ font-size:12.5pt; color:#333; font-style:italic; margin:8px 30px; }}
  .cover .type {{ font-size:11pt; color:#555; margin-top:26px; }}
  .cover .meta {{ margin:34px auto 0; font-size:11pt; color:#222; max-width:470px; text-align:left; }}
  .cover .meta table {{ font-family:'Cambria',serif; font-size:11pt; border:none; }}
  .cover .meta td {{ border:none; padding:4px 6px; }}
  .cover .meta td.k {{ font-weight:700; color:#14243d; width:38%; }}
  .footer-note {{ font-size:8.8pt; color:#666; text-align:justify; margin-top:24px;
                  border-top:1px solid #d5dbe4; padding-top:7px; font-family:'Calibri',sans-serif; }}
  .two {{ display:flex; gap:16px; align-items:flex-start; }}
  .two > div {{ flex:1; }}
  strong {{ color:#14243d; }}
  .toc li {{ margin:4px 0; }}
  .kw {{ font-size:10pt; margin-top:8px; }}
</style></head>
<body>

<!-- ================= TRANG BIA ================= -->
<div class="cover">
  <div class="inst">Chương trình Thạc sĩ Kỹ thuật Phần mềm (MSE)</div>
  <div class="inst" style="font-size:10pt;">Học phần: Máy học (Machine Learning)</div>
  <div class="rule"></div>
  <div class="type">BÁO CÁO BÀI TẬP CUỐI KHÓA</div>
  <h1>Dự đoán hỏng hóc thiết bị CNC trong điều kiện<br>dịch chuyển phân phối dữ liệu</h1>
  <div class="sub">Bảo trì dự đoán bằng đặc trưng bất biến vật lý và kiểm định có trọng số quan trọng<br>
  cho bài toán phân loại nhị phân mất cân bằng, chuyển giao giữa hai dây chuyền sản xuất</div>
  <div class="meta">
    <table>
      <tr><td class="k">Nhóm thực hiện</td><td>________________________________</td></tr>
      <tr><td class="k">Thành viên / MSSV</td><td>________________________________</td></tr>
      <tr><td class="k">Giảng viên hướng dẫn</td><td>________________________________</td></tr>
      <tr><td class="k">Bộ dữ liệu</td><td>AI4I 2020 (biến thể); Train A: 14.000 mẫu — Test B: 6.000 mẫu</td></tr>
      <tr><td class="k">Kết quả chính</td><td>F1 = 0,781 · AUC-ROC = 0,872 · AUC-PR = 0,670 (trên Dây chuyền B)</td></tr>
    </table>
  </div>
</div>

<!-- ================= TOM TAT ================= -->
<div class="pagebreak"></div>
<h2>Tóm tắt</h2>
<div class="abstract">
<p><span class="h">Tóm tắt.</span> Báo cáo trình bày một phương pháp dự đoán hỏng hóc thiết bị CNC ở ca vận hành
kế tiếp, phát biểu dưới dạng bài toán phân loại nhị phân mất cân bằng (tỉ lệ hỏng khoảng 8%). Thách thức trọng tâm
không nằm ở việc lựa chọn thuật toán mà ở hiện tượng <em>dịch chuyển phân phối</em> (distribution shift): mô hình được
huấn luyện trên Dây chuyền A song phải vận hành trên Dây chuyền B có điều kiện nhiệt và tốc độ khác biệt, trong khi
nhãn của tập kiểm thử không được sử dụng cho quá trình lựa chọn mô hình. Nghiên cứu chẩn đoán hiện tượng này là
<em>dịch chuyển hiệp biến</em> (covariate shift) và đề xuất ba đặc trưng "khoảng cách tới biên" neo trên các ngưỡng
vật lý bất biến của cơ chế sinh lỗi (HDF, PWF, OSF). Nhờ đặc trưng bất biến, ranh giới quyết định học trên Dây chuyền A
chuyển giao trực tiếp sang Dây chuyền B (PSI ≈ 0; Drift-AUC = 0,51). Các kỹ thuật hiệu chỉnh trọng số theo tỉ lệ mật độ,
hiệu chỉnh ngưỡng và học kết hợp được áp dụng như các lớp tinh chỉnh, toàn bộ được lựa chọn thông qua kiểm định có
trọng số quan trọng (Importance-Weighted Validation) nhằm bảo đảm không rò rỉ nhãn tập kiểm thử. Mô hình cuối cùng
(học kết hợp bỏ phiếu giữa Random Forest và XGBoost) đạt F1 = 0,781 trên Dây chuyền B, cải thiện 3,4 lần so với mô
hình cơ sở.</p>
<p class="kw"><span class="h">Từ khóa:</span> bảo trì dự đoán; dịch chuyển hiệp biến; đặc trưng bất biến; hiệu chỉnh
trọng số theo tỉ lệ mật độ; học kết hợp; dữ liệu mất cân bằng.</p>
</div>

<h2>Mục lục</h2>
<div class="toc"><ol>
<li>Giới thiệu</li>
<li>Dữ liệu và phát biểu bài toán</li>
<li>Phân tích khám phá dữ liệu</li>
<li>Tổng hợp các quyết định thiết kế</li>
<li>Phương pháp đề xuất và luận cứ
   <ul><li>5.1 Độ đo; 5.2 Chiến lược chia dữ liệu; 5.3 Thiết kế đặc trưng; 5.4 Cơ chế ngưỡng và tính bất biến hạng;
   5.5 Lựa chọn họ mô hình; 5.6 Hiệu chỉnh dịch chuyển; 5.7 Kiểm định có trọng số quan trọng; 5.8 Học kết hợp;
   5.9 Ngưỡng quyết định</li></ul></li>
<li>Thực nghiệm và kết quả</li>
<li>Thảo luận: hàm ý vận hành và bảo trì</li>
<li>Hạn chế của phương pháp</li>
<li>Hướng phát triển</li>
<li>Kết luận · Phụ lục: kiểm soát rò rỉ dữ liệu</li>
</ol></div>

<!-- ================= 1. GIOI THIEU ================= -->
<h2>1. Giới thiệu</h2>
<p>Bảo trì dự đoán cho phép can thiệp vào thiết bị trước khi sự cố xảy ra, qua đó giảm thiểu thời gian dừng dây
chuyền ngoài kế hoạch. Bài toán được phát biểu dưới dạng phân loại nhị phân với nhãn <code>hong_hoc</code> ∈ {{0,1}},
trong đó nhãn dương biểu thị thiết bị sẽ hỏng ở ca kế tiếp. Trong bối cảnh vận hành, sai lầm bỏ sót (dự báo âm cho
một thiết bị thực tế hỏng) gây tổn thất lớn hơn báo động giả, do đó phương pháp ưu tiên độ nhạy (Recall) nhưng vẫn
cân bằng với độ chính xác (Precision) thông qua độ đo F1.</p>
<p>Điểm khác biệt của bài toán so với một bài phân loại thông thường là yêu cầu chuyển giao mô hình giữa hai phân
phối dữ liệu: tập huấn luyện thu thập từ Dây chuyền A (nhà máy cũ) trong khi tập kiểm thử đến từ Dây chuyền B (nhà
máy mới, điều kiện nhiệt và tốc độ cao hơn). Ràng buộc quan trọng là nhãn của Dây chuyền B không được sử dụng trong
quá trình lựa chọn mô hình hay hiệu chỉnh siêu tham số. Toàn bộ báo cáo được tổ chức theo hướng luận giải: mỗi quyết
định kỹ thuật đều nêu rõ căn cứ lựa chọn, các phương án thay thế đã cân nhắc và bị loại bỏ, cùng rủi ro trong trường
hợp giả định nền tảng không được thỏa mãn.</p>

<!-- ================= 2. DU LIEU ================= -->
<h2>2. Dữ liệu và phát biểu bài toán</h2>
<h3>2.1 Mô tả dữ liệu</h3>
<table>
<caption>Bảng 1. Đặc điểm bộ dữ liệu.</caption>
<tr><th style="width:26%">Thuộc tính</th><th>Chi tiết</th></tr>
<tr><td>Kích thước</td><td>Train A: 14.000 × 8; Test B: 6.000 × 8; không có giá trị thiếu, không có bản ghi trùng lặp.</td></tr>
<tr><td>Biến số (5)</td><td>nhiệt độ môi trường, nhiệt độ quy trình, tốc độ quay, mômen xoắn, độ mòn dao.</td></tr>
<tr><td>Biến phân loại (2)</td><td><code>loai_san_pham</code> (L &lt; M &lt; H, có thứ tự); <code>ca_lam_viec</code> (danh nghĩa).</td></tr>
<tr><td>Nhãn</td><td><code>hong_hoc</code>; tỉ lệ hỏng: 7,36% (A) và 7,95% (B).</td></tr>
</table>

<h3>2.2 Chẩn đoán loại dịch chuyển phân phối</h3>
<p>Việc xác định đúng loại dịch chuyển là điều kiện tiên quyết, bởi mỗi loại đòi hỏi một chiến lược xử lý khác nhau.
Bảng 2 trình bày ba loại dịch chuyển và bằng chứng tương ứng trong dữ liệu.</p>
<table>
<caption>Bảng 2. Chẩn đoán loại dịch chuyển phân phối.</caption>
<tr><th>Loại dịch chuyển</th><th>Đặc điểm</th><th>Bằng chứng trong dữ liệu</th></tr>
<tr><td>Dịch chuyển hiệp biến — P(x) thay đổi, P(y|x) ổn định</td><td>Phân phối đầu vào thay đổi, cơ chế sinh nhãn giữ nguyên</td>
    <td>Có: biến thô dịch mạnh nhưng tỉ lệ nhãn ổn định (7,36% → 7,95%); P(hỏng | vượt ngưỡng) gần như không đổi (mục 5.4)</td></tr>
<tr><td>Dịch chuyển nhãn — P(y) thay đổi</td><td>Tỉ lệ lớp thay đổi đáng kể</td><td>Không: tiên nghiệm nhãn gần như không đổi</td></tr>
<tr><td>Dịch chuyển khái niệm — P(y|x) thay đổi</td><td>Cùng đầu vào nhưng quan hệ với nhãn thay đổi</td><td>Không quan sát thấy; tuy nhiên chưa thể loại trừ tuyệt đối do thiếu nhãn B (xem mục 8)</td></tr>
</table>
<p>Kết luận về <strong>dịch chuyển hiệp biến</strong> cho phép áp dụng bộ công cụ phù hợp: đặc trưng bất biến, hiệu
chỉnh trọng số theo tỉ lệ mật độ, và kiểm định có trọng số quan trọng. Nếu chẩn đoán sai thành dịch chuyển khái niệm,
các kỹ thuật này sẽ không còn hiệu lực.</p>

<h3>2.3 Lựa chọn độ đo đánh giá</h3>
<div class="note"><span class="t">Về việc loại bỏ độ chính xác (accuracy).</span> Với tỉ lệ hỏng khoảng 8%, một mô
hình dự báo toàn bộ là "không hỏng" đạt độ chính xác 92% nhưng độ nhạy bằng 0. Độ chính xác thưởng cho việc dự đoán
đúng lớp đa số — đối tượng không phải là mối quan tâm của bài toán — nên bị loại khỏi hệ độ đo.</div>
<p>Về ưu tiên AUC-PR so với AUC-ROC: AUC-ROC được tính trên nền toàn bộ lớp âm (5.523 mẫu), do đó dễ cho giá trị cao
một cách thiếu ý nghĩa khi lớp âm áp đảo. Ngược lại, AUC-PR chỉ đánh giá chất lượng của các cảnh báo dương, phù hợp
với mục tiêu vận hành. Báo cáo trình bày đồng thời ba độ đo: F1 là độ đo so sánh chính, AUC-PR là tham chiếu về độ
nhạy với lớp hiếm, và AUC-ROC dùng để so sánh khả năng xếp hạng.</p>

<!-- ================= 3. EDA ================= -->
<h2>3. Phân tích khám phá dữ liệu</h2>
<p>Phân tích khám phá được thực hiện nhằm định hướng quyết định thiết kế. Bốn phát hiện chính và hệ quả kỹ thuật
tương ứng được tổng hợp trong Bảng 3.</p>
<table>
<caption>Bảng 3. Các phát hiện khám phá và quyết định kéo theo.</caption>
<tr><th style="width:5%">#</th><th style="width:48%">Phát hiện (bằng chứng)</th><th>Quyết định kéo theo</th></tr>
<tr><td>1</td><td>Mất cân bằng lớp khoảng 8%, ổn định giữa A và B</td><td>Loại độ chính xác, dùng F1/AUC-PR (§5.1); là dịch chuyển hiệp biến nên phù hợp hiệu chỉnh trọng số (§5.6)</td></tr>
<tr><td>2</td><td>Nhiệt độ và tốc độ trên B dịch mạnh, độ phân tán rộng hơn khoảng 30% (Hình 1)</td><td>Không sử dụng biến thô làm ranh giới quyết định; cần đặc trưng bất biến (§5.3)</td></tr>
<tr><td>3</td><td>Độ mòn dao là tín hiệu mạnh nhất (hệ số tương quan +0,20) và ổn định (PSI = 0,001)</td><td>Chỉ báo dự báo then chốt, đồng thời can thiệp được; cơ sở cho khuyến nghị bảo trì (§7)</td></tr>
<tr><td>4</td><td>Tín hiệu hỏng mang tính phi tuyến, tập trung ở các đuôi phân phối (mòn dao cao, tốc độ thấp, mômen ở cả hai biên)</td><td>Cần mô hình cây; mô hình tuyến tính thuần không đủ (§5.5)</td></tr>
</table>
<div class="fig avoid-break"><img class="chart" src="{I['shift']}">
<div class="cap"><b>Hình 1.</b> Phân phối chồng lấn giữa Dây chuyền A và B: nhiệt độ và tốc độ dịch chuyển rõ rệt,
trong khi độ mòn dao ổn định.</div></div>
<div class="note"><span class="t">Phát hiện bổ sung — rủi ro ngoại suy.</span> Khoảng 2,8% số mẫu trên B nằm ngoài
miền giá trị quan sát được của A (chẳng hạn tốc độ cực đại của B là 2.414 so với 2.153 của A). Do mô hình cây không
có khả năng ngoại suy, phát hiện này trực tiếp dẫn tới quyết định giữ mô hình hồi quy logistic trong tổ hợp học kết
hợp như một cơ chế phòng vệ (§5.5, §5.8).</div>

<!-- ================= 4. TONG HOP QUYET DINH ================= -->
<div class="pagebreak"></div>
<h2>4. Tổng hợp các quyết định thiết kế</h2>
<p>Bảng 4 tổng hợp toàn bộ quyết định kỹ thuật của nghiên cứu; mỗi hàng nêu căn cứ lựa chọn, phương án thay thế đã
bị loại bỏ và rủi ro nếu giả định nền tảng không được thỏa mãn. Luận cứ chi tiết được trình bày trong Mục 5.</p>
<table>
<caption>Bảng 4. Tổng hợp quyết định thiết kế và luận cứ.</caption>
<tr><th style="width:15%">Quyết định</th><th style="width:29%">Căn cứ lựa chọn</th><th style="width:30%">Phương án thay thế bị loại bỏ</th><th style="width:26%">Rủi ro nếu giả định sai</th></tr>
<tr><td>Độ đo: F1 và AUC-PR</td><td>Lớp mất cân bằng khiến độ chính xác vô nghĩa; bỏ sót đắt hơn báo động giả</td><td>Độ chính xác (thưởng lớp đa số); chỉ tối đa Recall (dự báo hỏng toàn bộ)</td><td>Thấp — độ đo là ràng buộc của đề bài</td></tr>
<tr><td>Chia dữ liệu theo dây chuyền A→B</td><td>Phản ánh đúng bản chất dịch chuyển và điều kiện triển khai thực tế</td><td>Chia ngẫu nhiên/phân tầng — trộn lẫn A và B, làm rò rỉ thông tin B và che khuất dịch chuyển</td><td>Thấp — do đề bài quy định</td></tr>
<tr><td>Cân bằng lớp bằng trọng số, không sinh mẫu giả</td><td>Chia theo dây chuyền làm mất phân tầng; trọng số bù không tạo dữ liệu giả</td><td>SMOTE/lấy mẫu tăng — nội suy mẫu giả ở vùng lớp hiếm, rủi ro dưới dịch chuyển</td><td>Trung bình — nếu 8% là quá ít, trọng số có thể chưa đủ</td></tr>
<tr><td>Đặc trưng khoảng cách tới biên vật lý</td><td>Ngưỡng vật lý bất biến giúp ranh giới chuyển giao A→B</td><td>Tương tác thô/đa thức (dịch theo phân phối A); để cây tự học ngưỡng (học ngưỡng tối ưu của A)</td><td>Cao — nếu ngưỡng vật lý sai lệch, đặc trưng mất giá trị</td></tr>
<tr><td>Mã hóa: thứ tự cho loại SP, one-hot cho ca</td><td>Loại sản phẩm có thứ tự thực; ca làm việc là danh nghĩa</td><td>One-hot cho loại SP (bỏ thông tin thứ tự); mã thứ tự cho ca (áp đặt thứ tự giả)</td><td>Thấp</td></tr>
<tr><td>Họ mô hình: cây và hồi quy logistic</td><td>Tín hiệu phi tuyến; cây vượt trội trên dữ liệu bảng; logistic ngoại suy được</td><td>Chỉ tuyến tính (kém rõ rệt); học sâu (dư thừa cho 7 biến, dễ quá khớp)</td><td>Thấp</td></tr>
<tr><td>Tối ưu siêu tham số: RandomizedSearchCV theo AUC-PR</td><td>Không gian lớn nên tìm ngẫu nhiên hiệu quả hơn tìm lưới</td><td>GridSearch (vét cạn, kém hiệu quả); tối ưu theo độ chính xác (sai độ đo)</td><td>Thấp</td></tr>
<tr><td>Hiệu chỉnh dịch chuyển bằng trọng số tỉ lệ mật độ</td><td>Điều chỉnh phân phối huấn luyện về phía B mà không cần nhãn B</td><td>Bỏ qua dịch chuyển (ranh giới lệch); huấn luyện lại trên B (không có nhãn B)</td><td>Trung bình — sai nếu không phải dịch chuyển hiệp biến thuần</td></tr>
<tr><td>Lựa chọn mô hình/ngưỡng bằng IWV</td><td>Bài toán chấm trên B nhưng cấm sử dụng nhãn B</td><td>Lựa chọn theo điểm số trên B (rò rỉ nhãn kiểm thử, đánh giá thiên lệch)</td><td>Cao — cỡ mẫu hiệu dụng thấp (25,5%) khiến IWV nhiễu</td></tr>
<tr><td>Học kết hợp: chọn bỏ phiếu thay vì xếp chồng</td><td>Bốn mô hình cơ sở ít tương quan; bỏ phiếu đơn giản, ít quá khớp dịch chuyển</td><td>Xếp chồng — mô hình tổng hợp thiên lệch về XGBoost, F1-IWV thấp hơn sát ngưỡng</td><td>Thấp — hai phương án gần tương đương</td></tr>
</table>

<!-- ================= 5. PHUONG PHAP ================= -->
<h2>5. Phương pháp đề xuất và luận cứ</h2>

<h3>5.1 Độ đo đánh giá</h3>
<p>Như đã lập luận ở Mục 2.3, độ chính xác bị loại và AUC-PR được ưu tiên so với AUC-ROC. Độ đo F1 được chọn làm
tiêu chí so sánh đơn trị vì là trung bình điều hòa của Precision và Recall, phạt nặng khi một trong hai thành phần
thấp — phù hợp yêu cầu vừa hạn chế bỏ sót vừa hạn chế báo động giả. Do lớp hiếm chỉ gồm 477 mẫu trên B khiến ước
lượng F1 có phương sai lớn, khoảng tin cậy 95% được ước lượng bằng phương pháp bootstrap (Mục 6.1).</p>

<h3>5.2 Chiến lược chia dữ liệu</h3>
<div class="note"><span class="t">Chia theo dây chuyền thay vì ngẫu nhiên.</span> Mục tiêu thực tế là mô hình huấn
luyện trên nhà máy cũ vận hành được trên nhà máy mới. Nếu trộn A và B rồi chia ngẫu nhiên, tập kiểm định sẽ chứa mẫu
của B, khiến mô hình tiếp xúc trước với phân phối B, làm điểm kiểm định cao giả tạo và triệt tiêu khả năng đo lường
dịch chuyển. Chia theo dây chuyền bảo toàn đúng ranh giới triển khai thực tế.</div>
<p>Về xử lý mất cân bằng, phương pháp không sử dụng SMOTE hay lấy mẫu tăng. Các kỹ thuật này nội suy mẫu hỏng giả từ
các mẫu hỏng lân cận; dưới điều kiện dịch chuyển, vùng lớp hiếm của A không đại diện cho B, khiến mẫu giả làm mô hình
tự tin sai lệch. Thay vào đó, phương pháp sử dụng <code>class_weight='balanced'</code> cho hồi quy logistic và Random
Forest, cùng <code>scale_pos_weight ≈ 12,6</code> cho XGBoost — bù mất cân bằng bằng trọng số hàm mất mát thay vì tạo
dữ liệu giả. Toàn bộ bước chuẩn hóa và mã hóa được đóng gói trong <code>Pipeline</code> và huấn luyện lại trên tập
huấn luyện ở mỗi vòng kiểm định chéo nhằm ngăn rò rỉ dữ liệu.</p>

<h3>5.3 Thiết kế đặc trưng</h3>
<p>Phân tích khám phá cho thấy tín hiệu hỏng mang tính phi tuyến. Nhiều phương án tạo phi tuyến đã được cân nhắc và
đánh giá như trong Bảng 5.</p>
<table>
<caption>Bảng 5. So sánh các phương án tạo đặc trưng phi tuyến.</caption>
<tr><th>Phương án</th><th>Đánh giá</th></tr>
<tr><td>Tương tác thô (mòn × mômen), đa thức bậc hai</td><td>Bị loại — được dựng từ biến thô nên dịch chuyển theo phân phối A, không hỗ trợ chuyển giao</td></tr>
<tr><td>Để mô hình cây tự học ngưỡng phân tách</td><td>Đúng một phần, nhưng cây học ngưỡng tối ưu trên A; khi B dịch chuyển, ngưỡng lệch vị trí</td></tr>
<tr><td>Khoảng cách tới biên vật lý (lựa chọn)</td><td>Được chọn — neo trên hằng số vật lý không đổi giữa A và B, do đó ranh giới bất biến</td></tr>
</table>
<p>Ba đặc trưng đề xuất, mỗi đặc trưng là một hàm bản lề (hinge) chỉ nhận giá trị dương khi thiết bị đi vào vùng
nguy hiểm, được mô tả trong Bảng 6.</p>
<table>
<caption>Bảng 6. Ba đặc trưng khoảng cách tới biên và luận cứ dạng hàm.</caption>
<tr><th style="width:20%">Đặc trưng</th><th style="width:32%">Công thức</th><th>Cơ chế và luận cứ dạng hàm</th></tr>
<tr><td><code>nguy_tan_nhiet</code></td><td>max(8,6 − ΔT, 0) × max(1380 − tốc độ, 0)</td>
    <td>Cơ chế HDF (tản nhiệt). Tích hai hàm bản lề tương đương phép hội (AND): chỉ nguy hiểm khi đồng thời chênh
    lệch nhiệt nhỏ và tốc độ thấp — nếu một điều kiện được thỏa, một thừa số bằng 0 nên tích bằng 0.</td></tr>
<tr><td><code>lech_cong_suat</code></td><td>max(3500 − P, 0) + max(P − 9000, 0)</td>
    <td>Cơ chế PWF (công suất). Tổng hai hàm bản lề tương đương phép tuyển (OR): nguy hiểm khi công suất ra ngoài
    dải an toàn [3500, 9000] W (thiếu hoặc thừa); hai số hạng không thể đồng thời dương.</td></tr>
<tr><td><code>bien_overstrain</code></td><td>mòn × mômen − ngưỡng(loại)</td>
    <td>Cơ chế OSF (quá tải). Biên có dấu theo loại sản phẩm; không dùng hàm bản lề vì thông tin "còn xa ngưỡng"
    (giá trị âm) cũng hữu ích cho mô hình.</td></tr>
</table>
<div class="note"><span class="t">Bằng chứng đóng góp (cô lập).</span> Khi bổ sung ba đặc trưng này vào mô hình hồi
quy logistic cơ sở mà giữ nguyên mọi thành phần khác, F1 tăng từ 0,231 lên 0,352 và AUC-PR tăng từ 0,220 lên 0,501
(khoảng 2,3 lần). Hệ số tương quan điểm-nhị (point-biserial) của cả ba đặc trưng đều đạt tối thiểu 0,18, ngang bằng
hoặc vượt độ mòn dao (0,195).</div>

<h3>5.4 Cơ chế ngưỡng và tính bất biến hạng</h3>
<p>Đây là một điểm tinh tế thường bị hiểu sai. Hàm bản lề <code>max(0, ·)</code> không đơn thuần mang tính hình thức
mà là vị trí duy nhất tại đó giá trị ngưỡng thực sự tác động đến mô hình cây. Hình 2 minh họa hai cơ chế liên quan.</p>
<div class="fig avoid-break"><img class="chart" src="{I['hinge']}">
<div class="cap"><b>Hình 2.</b> (a) Hàm bản lề nén phẳng vùng an toàn về 0; thay đổi ngưỡng làm thay đổi tập mẫu bị nén,
do đó thay đổi thứ hạng. (b) Không dùng hàm bản lề: phép trừ hằng số dịch chuyển mọi mẫu như nhau nên thứ tự được
bảo toàn, mô hình cây cho kết quả không đổi.</div></div>
<table>
<caption>Bảng 7. Tác động của thay đổi ngưỡng theo loại đặc trưng.</caption>
<tr><th>Loại đặc trưng</th><th>Ngưỡng có tác động?</th><th>Cơ chế</th></tr>
<tr><td>Có hàm bản lề (<code>nguy_tan_nhiet</code>, <code>lech_cong_suat</code>)</td><td>Có</td>
    <td>Thay đổi ngưỡng làm thay đổi tập mẫu bị nén về 0, dẫn tới thay đổi thứ hạng và mô hình quan sát dữ liệu khác đi</td></tr>
<tr><td>Không hàm bản lề (<code>bien_overstrain</code>)</td><td>Không</td>
    <td>Phép trừ hằng số tương đương cộng đều mọi mẫu nên thứ tự bất biến; mô hình cây chỉ phụ thuộc thứ hạng nên kết
    quả không đổi (kiểm chứng thực nghiệm: giảm ngưỡng 100 hoặc 200 đơn vị, F1 giữ nguyên 0,7818)</td></tr>
</table>
<p>Tính bất biến hạng có hai hệ quả. Thứ nhất, không cần ước lượng chính xác ngưỡng OSF vì sai lệch hằng số không
gây hại. Thứ hai, cùng lập luận cho thấy phép chuẩn hóa <code>StandardScaler</code> cũng bất biến với dịch chuyển đều
(giá trị trung bình dịch theo nên điểm z triệt tiêu), do đó đặc trưng vật lý bền vững với cả mô hình tuyến tính lẫn
mô hình cây khi B dịch chuyển đồng đều.</p>

<h3>5.5 Lựa chọn họ mô hình</h3>
<p>Do tín hiệu phi tuyến và tập trung ở các đuôi phân phối, mô hình tuyến tính thuần tỏ ra hạn chế; thực nghiệm xác nhận mô hình
cây vượt trội (F1 tăng từ 0,35 lên 0,77). Nghiên cứu sử dụng ba mô hình cây theo ba cơ chế khác nhau nhằm tăng tính
đa dạng cho học kết hợp: Random Forest (đóng bao, giảm phương sai), XGBoost (tăng cường, giảm độ chệch) và ExtraTrees
(ngẫu nhiên hóa ngưỡng, phương sai thấp hơn nữa). Tham số <code>max_features='sqrt'</code> được chọn thay vì giá trị
mặc định do tồn tại biến trội là độ mòn dao; nếu để toàn bộ đặc trưng, các cây trở nên tương đồng và mất tính đa dạng.</p>
<p>Học sâu không được sử dụng: với chỉ 7 biến và 14.000 mẫu cùng tín hiệu gần với luật xác định, mạng nơ-ron có dung
lượng dư thừa, dễ quá khớp phân phối A (rủi ro cao dưới dịch chuyển) và khó diễn giải, đồng thời không mang lại lợi thế
trên dữ liệu bảng quy mô này. Mô hình hồi quy logistic được giữ lại trong tổ hợp mặc dù hiệu năng đơn lẻ thấp hơn, do
mô hình cây không ngoại suy được ngoài miền giá trị của A; hồi quy logistic ngoại suy có hướng nên bù đắp cho khoảng
2,8% số mẫu B vượt ngoài miền quan sát của A.</p>

<div class="pagebreak"></div>
<h3>5.6 Hiệu chỉnh dịch chuyển bằng trọng số tỉ lệ mật độ</h3>
<p>Sau khi thiết kế đặc trưng đã hấp thụ phần lớn dịch chuyển, một lớp hiệu chỉnh thống kê được bổ sung nhằm xử lý
phần còn lại: mỗi mẫu huấn luyện được gán trọng số theo mức độ tương đồng với phân phối B. Tỉ lệ mật độ được ước lượng
thông qua một bộ phân loại dịch chuyển (gán nhãn giả A = 0, B = 1):</p>
<div class="formula">w(x) = P(B | x) / P(A | x) = p / (1 − p)
<div class="cmt">mẫu của A càng giống B thì trọng số càng lớn</div></div>
<div class="fig avoid-break"><img class="chart" src="{I['reweight']}">
<div class="cap"><b>Hình 3.</b> Hiệu chỉnh trọng số điều chỉnh phân phối huấn luyện của A về phía B mà không sử dụng nhãn B.</div></div>
<p>Trọng số được cắt ngưỡng trong khoảng [0,2; 10] và chuẩn hóa về trung bình bằng 1. Lý do là một số ít mẫu hiếm của
A nằm trong vùng B có xác suất xấp xỉ 1, khiến trọng số thô tăng đến khoảng 57 và một mẫu đơn lẻ chi phối toàn bộ
gradient; việc cắt ngưỡng giữ ổn định phương sai (chỉ 0,5% số mẫu chạm giới hạn).</p>
<div class="note"><span class="t">Về mức cải thiện nhỏ của hiệu chỉnh.</span> Mức tăng của AUC-PR từ 0,665 lên 0,676
là kết quả nhất quán với lý thuyết chứ không phải dấu hiệu thất bại. Drift-AUC tính riêng trên các đặc trưng biên chỉ
đạt 0,51 (Hình 5), nghĩa là trên không gian đặc trưng này, A và B gần như không phân biệt được, do đó không còn nhiều
dịch chuyển để hiệu chỉnh. Điều này khẳng định rằng thiết kế đặc trưng vật lý đúng đắn làm giảm nhu cầu hiệu chỉnh
dịch chuyển bằng phương pháp thống kê.</div>

<h3>5.7 Kiểm định có trọng số quan trọng (IWV)</h3>
<p>Ràng buộc trọng tâm là mô hình được chấm trên B nhưng không được sử dụng nhãn B để lựa chọn. Cơ sở lý thuyết của
IWV nằm ở việc kỳ vọng hàm mất mát trên B có thể biểu diễn thành kỳ vọng có trọng số trên A:</p>
<div class="formula">𝔼<sub>B</sub>[L] = 𝔼<sub>A</sub>[ w(x) · L ], &nbsp; với &nbsp; w(x) = p<sub>B</sub>(x) / p<sub>A</sub>(x)</div>
<p>Nói cách khác, việc đánh giá mô hình trên tập huấn luyện A với trọng số tỉ lệ mật độ xấp xỉ việc đánh giá trên B.
Quy trình gồm ba thành phần: (i) xác suất ngoài nếp gấp (out-of-fold) trên A, bảo đảm mỗi mẫu được dự đoán bởi mô hình
không huấn luyện trên chính nó, tránh rò rỉ từ mô hình cơ sở sang mô hình tổng hợp; (ii) các độ đo Precision, Recall,
F1 có trọng số; (iii) quét ngưỡng để cực đại hóa F1 có trọng số. Toàn bộ quá trình lựa chọn mô hình, ngưỡng và trọng
số bỏ phiếu đều dựa trên IWV; nhãn B chỉ dùng để theo dõi và được chấm một lần duy nhất ở bước cuối.</p>
<p>Về giới hạn: đẳng thức trên chỉ đúng khi hiện tượng là dịch chuyển hiệp biến thuần và tỉ lệ mật độ được ước lượng
tốt. Cỡ mẫu hiệu dụng chỉ đạt 25,5% (do một số mẫu có trọng số lớn) khiến ước lượng IWV có nhiễu; vì vậy không nên
tin cậy các chênh lệch IWV nhỏ hơn khoảng 0,005 — nhận định này dẫn tới quyết định ở Mục 5.8.</p>

<h3>5.8 Học kết hợp</h3>
<p>Bốn mô hình cơ sở ít tương quan (tương quan out-of-fold giữa RF và XGB là 0,95, giữa logistic và các mô hình khác
khoảng 0,62) nên việc kết hợp mang lại lợi ích. Hai phương án kết hợp được so sánh trong Bảng 8.</p>
<table>
<caption>Bảng 8. So sánh hai phương án học kết hợp.</caption>
<tr><th>Phương án</th><th>Kết quả</th><th>Đánh giá</th></tr>
<tr><td>Bỏ phiếu — trung bình có trọng số (IWV chọn RF 0,5 / XGB 0,5)</td><td>F1-IWV = 0,794; F1-B = 0,781</td>
    <td>Được chọn — đơn giản, ít tham số, ít quá khớp dịch chuyển</td></tr>
<tr><td>Xếp chồng — mô hình tổng hợp logistic (thiên về XGB, hệ số 4,6)</td><td>F1-IWV = 0,791; F1-B = 0,781</td>
    <td>Bị loại — dồn trọng số vào một mô hình cơ sở, F1-IWV thấp hơn</td></tr>
</table>
<p>Dù F1 trên B của hai phương án bằng nhau, chênh lệch F1-IWV (0,794 so với 0,791) nhỏ hơn ngưỡng tin cậy do cỡ mẫu
hiệu dụng thấp, nên hai phương án được xem là gần tương đương. Trong trường hợp đó, phương án đơn giản và ổn định hơn
được ưu tiên theo nguyên lý tiết kiệm, đồng thời an toàn hơn dưới dịch chuyển vì không dồn rủi ro vào một mô hình cơ sở
đơn lẻ.</p>

<h3>5.9 Ngưỡng quyết định</h3>
<p>Ngưỡng mặc định 0,5 chỉ tối ưu cho lớp cân bằng và phân phối cố định — cả hai điều kiện đều không thỏa mãn ở đây.
Phương pháp quét ngưỡng để cực đại hóa F1 trên thang IWV (mô phỏng B), thu được giá trị 0,705. Ngưỡng này gần với
ngưỡng tối ưu lý tưởng ước lượng trực tiếp trên B (0,55–0,63), cho thấy IWV đáng tin cậy; đồng thời đỉnh của đường
F1 theo ngưỡng khá phẳng quanh 0,705, cho thấy lựa chọn ngưỡng có tính ổn định.</p>

<!-- ================= 6. KET QUA ================= -->
<h2>6. Thực nghiệm và kết quả</h2>
<div class="fig avoid-break"><img class="chart" src="{I['journey']}" style="max-width:82%;">
<div class="cap"><b>Hình 4.</b> Diễn tiến cải thiện qua sáu phiên bản. Mức cải thiện lớn nhất (v0 → v1) đến từ thiết kế
đặc trưng vật lý, không phải từ thuật toán phức tạp hơn.</div></div>
<div class="two avoid-break">
<div>
<table>
<caption>Bảng 9. Kết quả mô hình cuối cùng v6 (bỏ phiếu, ngưỡng 0,705) trên Dây chuyền B.</caption>
<tr><th>Độ đo</th><th>Giá trị</th></tr>
<tr><td>F1</td><td>0,781</td></tr>
<tr><td>AUC-ROC</td><td>0,872</td></tr>
<tr><td>AUC-PR</td><td>0,670</td></tr>
<tr><td>Precision</td><td>0,812</td></tr>
<tr><td>Recall</td><td>0,753</td></tr>
</table>
<p style="font-size:10pt;">Trong 477 thiết bị thực tế hỏng trên B, mô hình phát hiện 359 (dương thật) và bỏ sót 118
(âm giả); trong 442 cảnh báo phát ra, 83 là báo động giả (dương giả). Tỉ lệ cảnh báo đúng xấp xỉ bốn trên năm.</p>
</div>
<div class="fig"><img class="chart" src="{I['cm']}" style="max-width:95%;">
<div class="cap"><b>Hình 5.</b> Ma trận nhầm lẫn của mô hình v6 trên Dây chuyền B.</div></div>
</div>
<div class="two avoid-break" style="margin-top:6px;">
<div class="fig"><img class="chart" src="{I['psi']}">
<div class="cap"><b>Hình 6.</b> Chỉ số PSI: dịch chuyển tập trung ở biến thô; ba đặc trưng biên có PSI xấp xỉ 0.</div></div>
<div class="fig"><img class="chart" src="{I['drift']}">
<div class="cap"><b>Hình 7.</b> Drift-AUC: đặc trưng biên không phân biệt được A và B (0,51 ≈ dự đoán ngẫu nhiên).</div></div>
</div>
<div class="fig avoid-break"><img class="chart" src="{I['inv']}" style="max-width:62%;">
<div class="cap"><b>Hình 8.</b> Xác suất hỏng có điều kiện P(hỏng | vượt ngưỡng) gần như không đổi khi chuyển từ A sang B,
xác nhận cơ chế sinh lỗi bất biến.</div></div>

<h3>6.1 Đánh giá độ tin cậy bằng bootstrap</h3>
<ul>
<li>Ước lượng điểm F1 = 0,781 với khoảng tin cậy 95% là [0,751; 0,809]. Khoảng rộng (± 0,03) phản ánh việc chỉ có
477 mẫu hỏng trên B, khiến giá trị tuyệt đối của F1 kém chắc chắn; các khoảng tin cậy của những phiên bản đầu bảng
chồng lấn nhau, do đó không thể kết luận hơn kém dựa trên ước lượng điểm đơn lẻ.</li>
<li>So sánh theo cặp trên cùng mẫu bootstrap cho kết quả tin cậy hơn: xác suất F1 của v6 lớn hơn F1 của XGBoost đạt
99,8%, với chênh lệch trung bình +0,009 và khoảng tin cậy 95% [+0,003; +0,015] nằm hoàn toàn ở phía dương. Điều này
cho thấy học kết hợp vượt trội nhất quán về hướng, tuy biên độ nhỏ (khoảng 0,9%).</li>
</ul>

<!-- ================= 7. THAO LUAN ================= -->
<h2>7. Thảo luận: hàm ý vận hành và bảo trì</h2>
<p><strong>Độ mòn dao là chỉ báo then chốt cho bảo trì.</strong> Đây vừa là tín hiệu dự báo mạnh nhất, vừa ổn định
qua dịch chuyển (PSI xấp xỉ 0, độ quan trọng dẫn đầu ở mọi mô hình), lại là biến can thiệp được. Do đó, ưu tiên hàng
đầu cho đội bảo trì là giám sát và thay dao theo đúng chu kỳ.</p>
<p><strong>Cảnh báo theo ngưỡng vật lý có khả năng áp dụng xuyên nhà máy.</strong> Vì xác suất hỏng có điều kiện gần
như không đổi khi chuyển từ A sang B, có thể thiết lập cảnh báo dựa trên ngưỡng ngay cả khi thay đổi thiết bị hoặc dây
chuyền mà không cần huấn luyện lại, qua đó tiết kiệm chi phí triển khai khi mở rộng quy mô.</p>
<p><strong>Điều chỉnh ngưỡng theo chi phí thực tế.</strong> Do bỏ sót đắt hơn báo động giả, có thể hạ ngưỡng để tăng
độ nhạy khi chi phí dừng máy thấp. Đặc tính độc lập ngưỡng của mô hình (thông qua AUC-PR) cho phép lựa chọn điểm vận
hành phù hợp với bài toán chi phí cụ thể.</p>
<div class="note"><span class="t">Khuyến nghị hai cấp cảnh báo.</span>
<table style="margin:6px 0;">
<tr><th>Cấp</th><th>Ngưỡng</th><th>Ưu tiên</th><th>Hành động vận hành</th></tr>
<tr><td>Cấp 1 (cao)</td><td>Ngưỡng cao</td><td>Precision</td><td>Dừng máy kiểm tra ngay; độ tin cậy cao, ít báo nhầm</td></tr>
<tr><td>Cấp 2 (thấp)</td><td>Ngưỡng thấp</td><td>Recall</td><td>Tăng cường theo dõi, lập lịch bảo trì gần; phát hiện thêm thiết bị nghi ngờ</td></tr>
</table></div>

<!-- ================= 8. HAN CHE ================= -->
<h2>8. Hạn chế của phương pháp</h2>
<table>
<caption>Bảng 10. Các hạn chế và ảnh hưởng.</caption>
<tr><th style="width:34%">Hạn chế</th><th>Bản chất và ảnh hưởng</th></tr>
<tr><td>Mô hình cây không ngoại suy</td><td>Khoảng 2,8% số mẫu B nằm ngoài miền giá trị của A, dẫn tới dự đoán phẳng; hồi quy logistic chỉ bù đắp một phần.</td></tr>
<tr><td>Giả định dịch chuyển hiệp biến chưa được chứng minh trực tiếp</td><td>Hiệu chỉnh trọng số và IWV chỉ đúng nếu P(hỏng | đặc trưng) bất biến; nghiên cứu biện luận bằng cơ chế vật lý và tính ổn định của tiên nghiệm nhãn, nhưng không có nhãn B để kiểm chứng. Nếu tồn tại dịch chuyển khái niệm thực sự, tỉ lệ mật độ mất hiệu lực.</td></tr>
<tr><td>Độ tin cậy của IWV bị giới hạn</td><td>Cỡ mẫu hiệu dụng 25,5% khiến ước lượng nhiễu; chênh lệch giữa bỏ phiếu và xếp chồng nằm trong sai số.</td></tr>
<tr><td>Không gian cải thiện còn hẹp</td><td>Thiết kế đặc trưng đã hấp thụ phần lớn dịch chuyển, nên dư địa cải thiện thêm bằng kỹ thuật xử lý dịch chuyển là hạn chế.</td></tr>
<tr><td>Trần hiệu năng của dữ liệu</td><td>Chỉ có 5 biến số và 2 biến phân loại (gần như không mang thông tin), nhãn gần với luật xác định; các đặc trưng là xấp xỉ của luật sinh lỗi thực.</td></tr>
</table>

<!-- ================= 9. HUONG PHAT TRIEN ================= -->
<h2>9. Hướng phát triển</h2>
<ol>
<li>Hiệu chỉnh lại hằng số ngưỡng PWF: độ chính xác của luật PWF chỉ khoảng 0,17, cho thấy dải [3500; 9000] W có thể
lệch. Có thể ước lượng lại hai biên bằng phân vị công suất của nhóm hỏng và không hỏng trên A. Thí nghiệm ở Phụ lục
cho thấy việc thu hẹp dải nâng độ chính xác của cờ báo từ 0,17 lên 0,49.</li>
<li>Xây dựng đặc trưng theo thời gian nhằm nắm bắt xu hướng mòn dao thay vì trạng thái tức thời, cho phép cảnh báo sớm hơn.</li>
<li>Áp dụng các kỹ thuật thích ứng miền nâng cao (CORAL, căn chỉnh đặc trưng đối kháng) để xử lý phần dịch chuyển còn
sót ở đuôi phân phối.</li>
<li>Thu thập một lượng nhỏ nhãn trên B thông qua học chủ động nhằm kiểm chứng trực tiếp giả định dịch chuyển hiệp biến.</li>
<li>Áp dụng dự đoán bảo giác (conformal prediction) để cung cấp khoảng tin cậy cho mỗi cảnh báo, hỗ trợ ra quyết định
vận hành.</li>
</ol>

<!-- ================= 10. KET LUAN ================= -->
<h2>10. Kết luận</h2>
<p>Nghiên cứu giải quyết hai thành phần trọng số cao của tiêu chí đánh giá — xử lý dịch chuyển và kết quả trên tập
kiểm thử — thông qua một luận điểm xuyên suốt: xây dựng đặc trưng trên các hằng số vật lý bất biến thay vì hiệu chỉnh
một mô hình đã học ranh giới bị dịch chuyển. Nhờ đó, ranh giới quyết định học trên Dây chuyền A chuyển giao trực tiếp
sang Dây chuyền B; các bước hiệu chỉnh trọng số, hiệu chỉnh ngưỡng và học kết hợp chỉ đóng vai trò tinh chỉnh cuối
cùng, toàn bộ được lựa chọn bằng kiểm định có trọng số quan trọng mà không rò rỉ nhãn tập kiểm thử. Mỗi quyết định
trong báo cáo đều được luận giải kèm phương án thay thế và rủi ro tương ứng. Kết quả cuối cùng đạt F1 = 0,781 trên
Dây chuyền B, cải thiện 3,4 lần so với mô hình cơ sở.</p>

<!-- ================= PHU LUC ================= -->
<h2>Phụ lục. Kiểm soát rò rỉ dữ liệu</h2>
<p>Bảng 11 tổng hợp các nguy cơ rò rỉ tiềm tàng và biện pháp phòng ngừa đã áp dụng.</p>
<table>
<caption>Bảng 11. Nguy cơ rò rỉ và biện pháp phòng ngừa.</caption>
<tr><th>Nguy cơ</th><th>Biểu hiện</th><th>Biện pháp phòng ngừa</th></tr>
<tr><td>Rò rỉ dữ liệu</td><td>Điểm số trên tập kiểm thử cao bất thường</td><td>Chuẩn hóa, mã hóa, chọn đặc trưng chỉ huấn luyện trên tập huấn luyện, đóng gói trong Pipeline; quan hệ cơ sở–tổng hợp dùng dự đoán ngoài nếp gấp</td></tr>
<tr><td>Rò rỉ nhãn kiểm thử</td><td>Lựa chọn cấu hình theo điểm số trên B</td><td>Lựa chọn mô hình, ngưỡng và trọng số chỉ bằng IWV; nhãn B chấm một lần cuối</td></tr>
<tr><td>Mất cân bằng lớp</td><td>Độ chính xác 92%, độ nhạy bằng 0</td><td>Loại độ chính xác; dùng F1/AUC-PR, trọng số lớp và hiệu chỉnh ngưỡng</td></tr>
<tr><td>Quá khớp</td><td>Sai số huấn luyện gần 0 nhưng kém trên kiểm thử</td><td>Kiểm định chéo chọn tham số; chính quy hóa; học kết hợp; đặc trưng bất biến</td></tr>
</table>

<div class="footer-note">Báo cáo được biên soạn dựa trên notebook <code>bai_tap_cuoi_khoa.ipynb</code>. Các số liệu định
lượng và biểu đồ về PSI, ma trận nhầm lẫn, bằng chứng bất biến và Drift-AUC được tái lập tất định từ dữ liệu gốc trong
thư mục <code>Data_Final/</code>; các độ đo mô hình (F1, AUC, khoảng tin cậy) lấy từ kết quả chạy notebook. Hình 2 và
Hình 3 là minh họa cơ chế mang tính khái niệm.</div>

</body></html>"""

with open('bao_cao/bao_cao.html','w',encoding='utf-8') as f:
    f.write(HTML)
print('HTML written (academic):', len(HTML), 'chars')
