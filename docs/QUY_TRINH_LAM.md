# Quy trình làm bài

Tài liệu này kể lại quá trình nhóm giải bài toán dự đoán hỏng hóc thiết bị, từ lúc mới nhận đề cho đến khi đi sâu tìm cách nâng F1. Mục đích là để người đọc hiểu vì sao lời giải lại đi theo hướng này, chứ không chỉ nhìn thấy kết quả cuối.

## Bắt đầu: hiểu đề và làm quen dữ liệu

Đề yêu cầu xây một mô hình dự đoán máy phay CNC có hỏng trong ca kế tiếp hay không, với điểm nhấn là dữ liệu huấn luyện và dữ liệu kiểm thử đến từ hai dây chuyền khác nhau nên có hiện tượng dịch chuyển phân phối (distribution shift). Tập train có 14000 dòng lấy từ nhà máy A, tập test có 6000 dòng từ nhà máy B mới hơn và nóng hơn.

Khi xem qua các cột, nhóm nhận ra đây thực chất là bộ dữ liệu AI4I 2020 quen thuộc được đổi tên tiếng Việt. Điều này có ích vì nhãn hỏng của nó không phải ngẫu nhiên mà sinh ra từ bốn cơ chế vật lý: mòn dao, tản nhiệt kém, quá tải công suất và quá tải căng thẳng. Biết được điều đó, nhóm định hướng ngay từ đầu là sẽ tạo các đặc trưng bám theo bốn cơ chế này.

## Kiểm tra dữ liệu trước khi làm gì khác

Trước khi vội vàng huấn luyện, nhóm dành thời gian soi kỹ chất lượng dữ liệu, và phát hiện vài chỗ được cài cắm có chủ đích. Rõ nhất là cột tốc độ quay có tới 309 dòng mang đúng giá trị 1180.00 — một phân phối liên tục bình thường không thể trùng khít như vậy, nên đây chắc chắn là dấu vết cắt biên nhân tạo. Vài cột khác như độ mòn dao và mômen xoắn cũng bị cắt ở hai đầu.

Một điểm đáng lưu ý nữa là đề ghi tỷ lệ hỏng khoảng 3–5%, nhưng đo thực tế lại là 7,4% ở train và 7,9% ở test. Nhóm quyết định tin vào số đo được thay vì con số trong đề. Hai biến phân loại cũng cần cẩn thận: ca làm việc có tỷ lệ hỏng phẳng đều nên gần như là nhiễu, còn loại sản phẩm nhìn bề ngoài cũng phẳng nhưng thật ra nó quyết định ngưỡng của cơ chế quá tải căng thẳng, nên không được vội loại. Cuối cùng, một số dòng trong test có nhiệt độ vượt ra ngoài khoảng của train, tức mô hình sẽ phải ngoại suy ở vùng chưa từng thấy.

Từ những quan sát này, nhóm kết luận đây là kiểu covariate shift: quy luật vật lý gây hỏng không đổi giữa hai nhà máy, chỉ có điều kiện vận hành (nhiệt độ, tải) là dịch đi. Kết luận đó ảnh hưởng lớn đến cách xử lý shift về sau.

## Khám phá dữ liệu

Ở bước EDA, nhóm thống kê mô tả, vẽ phân phối của từng biến cho cả hai nhà máy để thấy độ lệch, và vẽ ma trận tương quan. Nhiệt độ ở nhà máy B cao hơn khoảng 2,5 độ và tốc độ quay cũng cao hơn, đúng với bối cảnh khí hậu nóng hơn. Điều hơi bất ngờ là tương quan tuyến tính giữa các biến với nhãn lại rất yếu, nhưng nghĩ kỹ thì hợp lý, vì cơ chế hỏng hoạt động theo ngưỡng chứ không tuyến tính.

Về sau khi rà soát lại, nhóm bổ sung thêm hai thứ cho EDA: dùng mutual information bên cạnh Pearson để bắt được quan hệ phi tuyến (ví dụ mômen xoắn có Pearson gần như bằng 0 nhưng mutual information vẫn dương), và vẽ phân phối của từng biến tách theo lớp hỏng và không hỏng, nhờ đó thấy rõ độ mòn dao là biến tách hai lớp tốt nhất.

## Tiền xử lý và tạo đặc trưng

Nguyên tắc quan trọng nhất ở bước này là chống rò rỉ dữ liệu: nhóm chỉ học các tham số chuẩn hoá từ tập train rồi mới áp cho cả hai tập, tuyệt đối không nhìn vào test. Có một điểm tinh tế là sau khi chuẩn hoá, dữ liệu test không có trung bình bằng 0 — điều này đúng và cố ý, vì phần lệch đó chính là shift mà nhóm muốn giữ lại để phân tích ở bước sau.

Về đặc trưng, thay vì để mô hình tự mò, nhóm tính sẵn vài con số phản ánh trực tiếp cơ chế hỏng: chênh lệch nhiệt độ cho tản nhiệt, công suất cơ (mômen nhân tốc độ góc) cho quá tải công suất, và tích mòn nhân mômen cho quá tải căng thẳng. Kiểm chứng lại thì AUC 5-fold tăng từ 0,867 lên 0,878, đủ để khẳng định các đặc trưng này có ích thật chứ không phải làm cho có.

## Phần trọng tâm: xử lý distribution shift

Đầu tiên nhóm đo mức độ shift bằng hai chỉ số PSI và KS cho từng biến, rồi huấn luyện một bộ phân loại để đoán mỗi dòng thuộc nhà máy A hay B. Kết quả cho thấy nhiệt độ dịch mạnh nhất (PSI của nhiệt độ môi trường lên tới 1,08) trong khi độ mòn dao gần như không đổi (PSI chỉ 0,001). Bộ phân loại phân biệt hai nhà máy đạt AUC 0,81, xác nhận shift là có thật và mạnh, với thủ phạm chính là nhiệt độ.

Để xử lý, nhóm thử hai kỹ thuật là cân lại trọng số mẫu theo tỷ số mật độ (importance reweighting) và hiệu chỉnh ngưỡng. Điều thú vị là reweighting cải thiện rất ít. Nghĩ lại thì điều này hợp lý: vì đây là covariate shift, và các đặc trưng theo cơ chế mà nhóm tạo ra vốn đã ít bị shift hơn hẳn (PSI của chênh lệch nhiệt chỉ 0,32, nhỏ hơn ba lần so với nhiệt độ thô). Nói cách khác, chính việc tạo đặc trưng tốt đã hấp thụ phần lớn shift, nên không còn nhiều cho reweighting làm.

## Xây mô hình và đánh giá

Nhóm huấn luyện ba mô hình đại diện cho ba mức: hồi quy logistic, random forest và XGBoost, đều tinh chỉnh siêu tham số bằng RandomizedSearchCV kết hợp Stratified K-Fold, và đánh giá bằng nhiều chỉ số thay vì chỉ accuracy (vì accuracy vô nghĩa khi dữ liệu mất cân bằng). Random forest cho kết quả tốt nhất với F1 khoảng 0,78. Hồi quy logistic kém hơn hẳn, và điều đó lại là bằng chứng củng cố nhận định rằng cơ chế hỏng là phi tuyến.

## Tinh gọn lại bộ đặc trưng

Sau khi có mô hình chạy được, nhóm quay lại xem đặc trưng nào thực sự đóng góp. Thay vì loại theo cảm tính, nhóm đo bằng permutation importance và thử bỏ đi từng nhóm (ablation). Kết quả cho thấy đặc trưng tỷ lệ mômen trên tốc độ hoàn toàn vô dụng (mức đóng góp bằng 0) và ca làm việc chỉ là nhiễu, nên loại cả hai. Ngược lại, nhóm thêm một đặc trưng mới là osf_margin — hiệu giữa tích mòn nhân mômen và ngưỡng tương ứng với hạng sản phẩm — và nó nâng AUC-PR từ 0,681 lên 0,693. Bài học rút ra là trên mô hình cây, chỉ nên thêm đặc trưng khi nó gói được một tương tác nhiều biến hoặc một ngưỡng thay đổi theo điều kiện, còn những biến đổi đơn giản của một biến thì cây tự làm được rồi.

## Thử các phương án khác cho shift

Để chắc chắn hướng đi là hợp lý, nhóm thử thêm một phương pháp xử lý shift khác là CORAL, vốn căn chỉnh cấu trúc hiệp phương sai giữa hai tập. Hoá ra CORAL lại làm kết quả tệ đi (F1 tụt từ 0,778 xuống 0,743). Lý do là shift ở đây chủ yếu là dịch trung bình chứ không phải đổi cấu trúc tương quan, nên CORAL căn chỉnh nhầm thứ và làm méo các đặc trưng cơ chế. Đây là một bài học đáng giá: phải chọn phương pháp xử lý shift cho đúng loại shift, chứ không áp dụng bừa.

## Đi sâu tìm cách nâng F1

Đến đây câu hỏi đặt ra là liệu có cách nào đẩy F1 vượt 0,8 mà vẫn đúng ràng buộc của đề hay không. Nhóm làm theo một vòng lặp rõ ràng: khai phá dữ liệu để tìm đặc trưng tốt hơn, huấn luyện lại, rồi kiểm tra F1; nếu chưa đạt thì quay lại tìm tiếp.

Bước khai phá cho kết quả khá bất ngờ. Khi đo tỷ lệ hỏng theo từng khoảng giá trị, nhóm tìm được ngưỡng thật của các cơ chế trong chính bộ dữ liệu này, và chúng khác với ngưỡng mặc định của AI4I. Chẳng hạn với độ mòn dao, tỷ lệ hỏng vẫn quanh 7% cho tới khoảng 240, rồi nhảy vọt lên 57% ở khoảng 240–255. Tương tự, công suất quá thấp (dưới 2800) hay quá cao (trên 10000) đều làm tỷ lệ hỏng tăng mạnh.

Nhưng chính bước này cũng hé lộ một sự thật quan trọng: ngay ở vùng nguy hiểm nhất, tỷ lệ hỏng cũng chỉ khoảng 57–78% chứ không phải 100%. Nghĩa là kể cả những máy ở trạng thái xấu nhất thì vẫn có gần một nửa không hỏng. Để kiểm chứng, nhóm cho một random forest học thuộc lòng tập train (nó đạt F1 bằng 1,0) rồi so với F1 khi đánh giá chéo (chỉ 0,755). Khoảng cách 0,25 giữa hai con số đó chính là phần nhiễu không thể khử — hay nói cách khác, đây là trần Bayes của bài toán.

Dù vậy, việc khai phá ngưỡng không hề vô ích. Nhóm dùng các ngưỡng vừa tìm được để tạo ra những đặc trưng "sắc" hơn, chẳng hạn khoảng cách tới ngưỡng mòn dao 240, hay mức vượt biên công suất. Những đặc trưng này có tương quan với nhãn khá cao (0,18 đến 0,25) và gần như không bị shift (PSI xấp xỉ 0), đúng tiêu chí một đặc trưng tốt. Khi huấn luyện lại ba mô hình, các đặc trưng sắc nâng hồi quy logistic từ 0,31 lên 0,58 và XGBoost từ 0,75 lên 0,77, dù random forest vẫn giữ nguyên khoảng 0,78 vì cây vốn đã tự tìm được các ngưỡng đó.

Cuối cùng, để trả lời dứt điểm câu hỏi về mốc 0,8, nhóm đo trần tuyệt đối bằng cách cho phép chọn ngưỡng tối ưu ngay trên nhãn test — một dạng gian lận có kiểm soát chỉ để biết giới hạn trên. Kết quả cao nhất cũng chỉ 0,783. Điều đó có nghĩa là không có cách hợp lệ nào đạt tới 0,8 trên bộ dữ liệu này. Muốn F1 cao hơn thật sự thì phải có thêm dữ liệu mới như cảm biến rung, âm thanh hay tốc độ mòn dao theo thời gian, chứ không phải xử lý thêm.

## Nhìn lại toàn bộ

Nhìn lại, mỗi quyết định trong bài đều xuất phát từ một quan sát cụ thể chứ không phải làm theo thói quen. Nhóm dùng F1 và AUC-PR thay vì accuracy vì dữ liệu mất cân bằng; chỉ học chuẩn hoá trên train để vừa chống rò rỉ vừa giữ shift; ưu tiên mô hình cây vì cơ chế phi tuyến; chọn và loại đặc trưng dựa trên số đo chứ không cảm tính; và cuối cùng chấp nhận F1 khoảng 0,78 vì đã chứng minh được đó là trần tự nhiên của bài toán. Con số 0,78 không phải là dấu hiệu làm chưa tốt, mà là kết quả tối ưu hợp lệ khi bản thân nhãn đã chứa sẵn phần ngẫu nhiên không thể đoán trước.

---

*Chi tiết kỹ thuật xem [`TONG_QUAN_KY_THUAT.md`](TONG_QUAN_KY_THUAT.md); giải thích khái niệm xem [`GIAI_THICH_TU_KHOA_DE_BAI.md`](GIAI_THICH_TU_KHOA_DE_BAI.md); mã nguồn ở [`../bai_tap_cuoi_khoa.ipynb`](../bai_tap_cuoi_khoa.ipynb) và [`../bai_tap_nang_cao_F1.ipynb`](../bai_tap_nang_cao_F1.ipynb).*
