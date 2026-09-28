# Kịch bản thuyết trình project phân tích lương nhân viên

**Thời lượng gợi ý:** 12–15 phút.

> **Lưu ý khi trình bày:** Các số liệu dưới đây được tính từ `data/Employers_data.csv` khi chưa chọn bộ lọc. Project chưa ghi rõ đơn vị tiền tệ và kỳ trả lương, vì vậy hãy gọi là “đơn vị lương trong dữ liệu”.

## 1. Mở đầu — 1 phút

**Thao tác:** Mở ứng dụng ở trang **Tổng quan**.

> Em xin trình bày project **Web phân tích và trực quan hóa dữ liệu lương nhân viên**. Mục tiêu của project là biến một bảng dữ liệu nhân viên thành những thông tin dễ quan sát: mức lương phân bố ra sao, khác nhau thế nào giữa các nhóm nhân viên, và số năm kinh nghiệm có liên hệ với lương như thế nào.
>
> Ứng dụng được viết bằng Python, sử dụng Streamlit cho giao diện, pandas để xử lý dữ liệu, Plotly để vẽ biểu đồ, SciPy cho kiểm định thống kê và scikit-learn cho mô hình hồi quy.

## 2. Dữ liệu và quy trình xử lý — 2 phút

> Đầu vào là file `Employers_data.csv`, gồm **10.000 nhân viên**. Các trường chính gồm tuổi, giới tính, phòng ban, chức danh, số năm kinh nghiệm, học vấn, địa điểm và lương.
>
> Trước khi phân tích, chương trình kiểm tra các cột bắt buộc, chuẩn hóa ký hiệu giá trị khuyết, chuyển tuổi, kinh nghiệm và lương sang kiểu số. Nếu dữ liệu mới có lương bị khuyết thì dòng đó được loại bỏ; tuổi và kinh nghiệm bị khuyết được điền bằng trung bình, còn biến phân loại được điền bằng giá trị phổ biến nhất. Chương trình cũng loại bản ghi trùng và chia tuổi, kinh nghiệm thành các nhóm để so sánh.
>
> Riêng với **file đang trình bày**, dữ liệu đầu vào không có giá trị khuyết ở các cột phân tích và không có bản ghi trùng cần loại, nên sau xử lý vẫn còn 10.000 nhân viên.
>
> Về cấu trúc mã nguồn, `analysis.py` phụ trách xử lý và tính toán, `charts.py` tạo biểu đồ, `insights.py` sinh nhận xét theo dữ liệu đang xem, còn `app.py` ghép tất cả thành ba trang tương tác.

## 3. Trang Tổng quan — 2 phút

**Thao tác:** Chỉ vào dãy chỉ số và ba biểu đồ đầu trang.

> Trang đầu tiên trả lời câu hỏi: **bức tranh chung về lương là gì?** Dữ liệu có 10.000 nhân viên; lương trung bình là **115.381,5**, trung vị là **120.000**, thấp nhất **25.000** và cao nhất **215.000**.
>
> Biểu đồ phân bố cho thấy các mức lương tập trung ở đâu; đường đứt nét đánh dấu giá trị trung bình. Phần thống kê bên dưới cho biết 50% nhân viên có lương nằm trong khoảng **70.000 đến 150.000**, tức IQR bằng **80.000**. Theo quy tắc 1,5 lần IQR, dữ liệu này không có giá trị ngoại lệ.
>
> Hai biểu đồ bên cạnh cho phép so sánh **quy mô phòng ban** với **lương trung bình phòng ban**. Ví dụ, Finance có lương trung bình cao nhất, khoảng **130.376**, trong khi Engineering khoảng **90.680**. Quy mô nhân sự và mức lương là hai góc nhìn khác nhau, nên cần đọc cả hai biểu đồ.

**Thao tác:** Rê chuột vào biểu tượng 💡 của một biểu đồ.

> Biểu tượng bóng đèn hiển thị nhận xét được tính từ dữ liệu hiện tại. Khi đổi bộ lọc, nhận xét này cũng thay đổi.

## 4. Trang Phân tích lương — 2–3 phút

**Thao tác:** Chuyển sang **Phân tích lương**.

> Trang thứ hai đi sâu vào chênh lệch lương theo **phòng ban, chức danh, học vấn và địa điểm**. Mỗi biểu đồ đặt trung bình cạnh trung vị để thấy liệu một vài mức lương cao hoặc thấp có kéo giá trị trung bình hay không.
>
> Theo chức danh, Executive có lương trung bình khoảng **183.415**, còn Intern khoảng **35.802**. Theo học vấn, các mức trung bình lần lượt là khoảng **69.530** với Bachelor, **134.234** với Master và **152.137** với PhD. Đây là so sánh giữa các nhóm trong bộ dữ liệu; chưa thể kết luận riêng học vấn gây ra chênh lệch, vì chức danh và kinh nghiệm cũng có thể khác nhau.
>
> Box plot phía dưới thể hiện trung vị, khoảng 50% dữ liệu ở giữa và độ phân tán lương của từng phòng ban.

**Thao tác:** Chỉ vào bảng ANOVA.

> Để kiểm tra chênh lệch trung bình có đủ rõ về mặt thống kê hay không, project dùng ANOVA với ngưỡng p-value 0,05. Trong dữ liệu này, chức danh, học vấn và phòng ban có p-value dưới 0,05. Địa điểm có p-value khoảng **0,123** và giới tính khoảng **0,084**, nên kiểm định này chưa cho thấy khác biệt trung bình rõ ràng giữa các nhóm tương ứng. ANOVA cho thấy sự khác biệt thống kê; nó không tự chứng minh quan hệ nhân quả.

## 5. Trang Kinh nghiệm và hồi quy — 3 phút

**Thao tác:** Chuyển sang **Kinh nghiệm & hồi quy**.

> Trang cuối xem xét mối liên hệ giữa kinh nghiệm và lương. Biểu đồ phân tán biểu diễn từng nhân viên, còn đường thẳng là xu hướng mà mô hình học được.
>
> Project dùng hồi quy tuyến tính một biến, với đầu vào là **số năm kinh nghiệm**. Dữ liệu được chia **70% để huấn luyện** và **30% để kiểm tra**. Phương trình trên dữ liệu hiện tại xấp xỉ:
>
> **Lương dự đoán = 59.416 + 4.527 × số năm kinh nghiệm.**
>
> Hệ số Pearson giữa kinh nghiệm và lương là **0,898**, cho thấy hai biến có tương quan thuận mạnh. Trên tập kiểm tra, R² khoảng **0,806**, nghĩa là mô hình giải thích được khoảng **80,6% biến thiên lương** trong tập kiểm tra này. Sai số tuyệt đối trung bình, hay MAE, khoảng **16.466 đơn vị lương**.

**Thao tác:** Nhập **10** vào ô số năm kinh nghiệm.

> Nếu nhập 10 năm kinh nghiệm, ứng dụng dự đoán lương khoảng **104.689**. Đây là giá trị theo xu hướng chung của dữ liệu, không phải mức lương chắc chắn của một cá nhân.

**Thao tác:** Chỉ vào biểu đồ phần dư, nhóm kinh nghiệm, nhóm tuổi và ma trận tương quan.

> Biểu đồ phần dư giúp kiểm tra dự đoán lệch thực tế ra sao. Các biểu đồ nhóm cho thấy lương trung bình thay đổi giữa những nhóm kinh nghiệm và nhóm tuổi. Ma trận tương quan còn cho thấy tuổi và kinh nghiệm liên hệ rất mạnh, với r khoảng **0,982**. Vì vậy, nếu đưa đồng thời cả hai vào một mô hình đa biến, cần xem xét vấn đề đa cộng tuyến.

## 6. Demo tính tương tác — 1 phút

**Thao tác:** Ở thanh bên, chọn phòng ban **Finance**.

> Bộ lọc bên trái cho phép chọn phòng ban, địa điểm và giới tính. Khi chọn Finance, các chỉ số và biểu đồ được tính lại cho **1.595 nhân viên** của phòng ban này; lương trung bình lúc này khoảng **130.376**. Như vậy, người xem có thể chuyển từ toàn bộ công ty sang một nhóm cụ thể mà không cần sửa mã nguồn.

**Thao tác:** Xóa bộ lọc trước khi kết luận.

## 7. Giới hạn và hướng phát triển — 1 phút

> Project hiện phân tích một file dữ liệu có sẵn. Nguồn dữ liệu chưa ghi rõ đơn vị tiền tệ và kỳ trả lương, nên các kết quả cần được hiểu theo đơn vị gốc của file. Mô hình dự đoán mới dùng một biến là kinh nghiệm; chức danh, học vấn và các yếu tố khác cũng có thể giúp giải thích lương. Ngoài ra, các mối tương quan và kiểm định trong project không đủ để kết luận một yếu tố trực tiếp gây tăng lương.
>
> Hướng phát triển tiếp theo là bổ sung mô tả nguồn dữ liệu, thử mô hình nhiều biến và đánh giá chất lượng dự đoán trên dữ liệu mới.

## 8. Kết thúc — 30 giây

> Tóm lại, project đi theo một quy trình phân tích dữ liệu hoàn chỉnh: **đọc và làm sạch dữ liệu, thống kê mô tả, trực quan hóa, kiểm định sự khác biệt, rồi xây dựng và đánh giá mô hình dự đoán**. Điểm hữu ích của ứng dụng là người xem có thể lọc dữ liệu và đọc kết quả trực tiếp trên dashboard. Em xin cảm ơn và sẵn sàng trả lời câu hỏi.

---

**Chuẩn bị trước khi trình bày:** Chạy `streamlit run app.py`, mở trang Tổng quan và xóa hết bộ lọc để các con số trong kịch bản khớp với màn hình.
