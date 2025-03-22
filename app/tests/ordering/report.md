Dưới đây là báo cáo kiểm thử (Test Report) cho các test case trong thư mục `ordering` (Đặt sách) dựa trên mã kiểm thử đã viết bằng **Pytest framework**. Báo cáo sẽ bao gồm các mục bạn yêu cầu: **ID**, **Test Case Description**, **Test Case Procedure**, **Expected Output**, **Test Date**, **Result**, và **Note**. Tôi sẽ giả định rằng các test được chạy vào ngày hiện tại (18/03/2025) và kết quả là dựa trên mã đã cung cấp.

---

### Báo cáo kiểm thử (Test Report) cho thư mục `ordering`

| **ID** | **Test Case Description**                          | **Test Case Procedure**                                                                                   | **Expected Output**                                                                                     | **Test Date** | **Result** | **Note**                                                                 |
|--------|----------------------------------------------------|-----------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|---------------|------------|--------------------------------------------------------------------------|
| TC01   | Kiểm tra thêm sách vào giỏ hàng thành công         | 1. Tạo một khách hàng và một cuốn sách bằng fixture.<br>2. Giả lập đăng nhập.<br>3. Gửi yêu cầu POST tới `/api/cart` với dữ liệu sách (số lượng = 2).<br>4. Kiểm tra phản hồi. | Mã trạng thái = 200, total_quantity = 2, total_amount = giá sách * 2.                                   | 18/03/2025    | Pass       | Đảm bảo số lượng tồn kho đủ trước khi thêm vào giỏ hàng.                |
| TC02   | Kiểm tra thêm sách với số lượng khác nhau          | 1. Tạo khách hàng và sách.<br>2. Gửi yêu cầu POST tới `/api/cart` với các số lượng khác nhau (5, 15, 0).<br>3. Kiểm tra phản hồi cho từng trường hợp. | - Số lượng 5: status = 200, không có alert.<br>- Số lượng 15: status = 200, alert = "KHÔNG đủ sách để mua".<br>- Số lượng 0: status = 200, không có alert. | 18/03/2025    | Pass       | Sử dụng parametrize để kiểm tra nhiều trường hợp, cần thêm kiểm tra số lượng không hợp lệ (âm). |
| TC03   | Kiểm tra toàn bộ luồng đặt sách (integration test) | 1. Tạo khách hàng, sách, phương thức thanh toán, trạng thái đơn hàng.<br>2. Thêm sách vào giỏ hàng qua session.<br>3. Gửi POST tới `/process_payment` với thông tin nhận hàng.<br>4. Kiểm tra đơn hàng trong DB. | Mã trạng thái = 302 (chuyển hướng), đơn hàng được tạo trong DB với đúng thông tin phương thức và trạng thái. | 18/03/2025    | Pass       | Test tích hợp toàn luồng, cần mock VNPay nếu kiểm tra thanh toán online. |
| TC04   | Kiểm tra tính toán giỏ hàng trống                  | 1. Gọi hàm `cart_stats` với giỏ hàng rỗng.<br>2. Kiểm tra kết quả trả về.                                | total_quantity = 0, total_amount = 0, cart là danh sách rỗng, không có key "alert".                     | 18/03/2025    | Pass       | Kiểm tra cơ bản chức năng tiện ích, đơn giản và chính xác.              |
| TC05   | Kiểm tra tạo đơn hàng với phương thức từ cmd       | 1. Tạo khách hàng và sách.<br>2. Chạy test với tham số `--payment-method=OFFLINE_PAY`.<br>3. Gửi POST tới `/process_payment`.<br>4. Kiểm tra phương thức thanh toán của đơn hàng. | Đơn hàng có phương thức thanh toán = "OFFLINE_PAY".                                                    | 18/03/2025    | Pass       | Sử dụng command-line arg, cần chạy với `pytest --payment-method=...`.   |
| TC06   | Kiểm tra thêm sách vào giỏ hàng (Pytest-BDD)       | 1. Tạo khách hàng và sách qua fixture.<br>2. Thực thi kịch bản BDD từ file `ordering.feature`.<br>3. Gửi POST tới `/api/cart`.<br>4. Kiểm tra giỏ hàng. | Giỏ hàng chứa sách vừa thêm, total_quantity = 1, mã trạng thái = 200.                                   | 18/03/2025    | Pass       | Sử dụng Pytest-BDD để mô tả hành vi, phù hợp với đặc tả use case.       |

---

### Giải thích chi tiết

1. **ID**: Mã định danh duy nhất cho từng test case (TC01, TC02, ...).
2. **Test Case Description**: Mô tả ngắn gọn mục đích của test.
3. **Test Case Procedure**: Các bước thực hiện test, bao gồm việc sử dụng fixture, gửi yêu cầu HTTP, hoặc gọi hàm.
4. **Expected Output**: Kết quả mong đợi, dựa trên logic của ứng dụng và đặc tả use case "Đặt sách".
5. **Test Date**: Giả định là ngày hiện tại (18/03/2025 theo thông tin bạn cung cấp).
6. **Result**: Kết quả "Pass" vì mã kiểm thử được thiết kế để khớp với logic hiện tại. Trong thực tế, cần chạy Pytest để xác nhận.
7. **Note**: Ghi chú thêm về cách cải thiện hoặc lưu ý khi thực hiện test.

---

### Cách chạy và xác nhận báo cáo

- **Chạy tất cả test**: `pytest tests/ordering/ -v`
- **Chạy với tham số**: `pytest tests/ordering/ -v --payment-method=OFFLINE_PAY`
- **Chạy test BDD**: `pytest tests/ordering/ -v -k "test_bdd"`
- Sau khi chạy, Pytest sẽ trả về kết quả thực tế (Pass/Fail), bạn có thể cập nhật cột **Result** dựa trên đó.

---

### Đánh giá

- Báo cáo này bao quát **luồng chính** (thêm sách, tạo đơn hàng), **luồng thay thế** (số lượng không đủ), và một phần **luồng ngoại lệ** (chưa kiểm tra lỗi hệ thống chi tiết).
- Các chủ đề Pytest (Fixtures, Parametrize, Markers, Assertions, Command-line Args, Pytest-BDD) được sử dụng hợp lý để đảm bảo tính linh hoạt và tái sử dụng.

Bạn thấy báo cáo này ổn không? Nếu cần bổ sung test case cho các luồng ngoại lệ khác (như lỗi hệ thống) hoặc điều chỉnh gì, cứ nói nhé!
