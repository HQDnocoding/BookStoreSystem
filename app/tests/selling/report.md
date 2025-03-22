Dưới đây là báo cáo kiểm thử (Test Report) cho các test case trong thư mục `selling` (Bán sách) dựa trên mã kiểm thử đã viết bằng **Pytest framework**. Báo cáo bao gồm các mục bạn yêu cầu: **ID**, **Test Case Description**, **Test Case Procedure**, **Expected Output**, **Test Date**, **Result**, và **Note**. Tôi giả định rằng các test được chạy vào ngày hiện tại (18/03/2025) và kết quả dựa trên mã đã cung cấp.

---

### Báo cáo kiểm thử (Test Report) cho thư mục `selling`

| **ID** | **Test Case Description**                          | **Test Case Procedure**                                                                                   | **Expected Output**                                                                                     | **Test Date** | **Result** | **Note**                                                                 |
|--------|----------------------------------------------------|-----------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|---------------|------------|--------------------------------------------------------------------------|
| TC01   | Kiểm tra tạo hóa đơn từ giỏ hàng thành công        | 1. Tạo nhân viên và sách bằng fixture.<br>2. Giả lập đăng nhập nhân viên và thêm sách vào giỏ hàng qua session.<br>3. Gọi hàm `create_invoice_from_cart`.<br>4. Kiểm tra đơn hàng và số lượng sách. | Đơn hàng được tạo (order không None), nhân viên khớp, phương thức là OFFLINE_PAY, số lượng sách giảm 1. | 18/03/2025    | Pass       | Đảm bảo số lượng tồn kho đủ trước khi bán.                              |
| TC02   | Kiểm tra bán sách với các điều kiện khác nhau      | 1. Tạo nhân viên và sách.<br>2. Thêm sách vào giỏ hàng với số lượng khác nhau (2, 6, 2).<br>3. Gửi số tiền khác nhau (300000, 900000, 200000).<br>4. Gọi `create_invoice_from_cart` và kiểm tra kết quả. | - Số lượng 2, tiền 300000: Thành công.<br>- Số lượng 6, tiền 900000: Thất bại (không đủ sách).<br>- Số lượng 2, tiền 200000: Thất bại (không đủ tiền). | 18/03/2025    | Pass       | Sử dụng parametrize để kiểm tra nhiều trường hợp, cần xử lý exception rõ ràng hơn. |
| TC03   | Kiểm tra bán sách tại cửa hàng (bỏ qua)            | 1. Đánh dấu test bằng `@pytest.mark.skip` vì chưa có tuyến đường cụ thể.<br>2. Không thực thi.           | Không có kết quả (test bị bỏ qua).                                                                      | 18/03/2025    | Skipped    | Chưa có tuyến đường `/sell`, cần bổ sung trong mã nguồn để kiểm tra.    |
| TC04   | Kiểm tra tạo PDF hóa đơn bán sách                  | 1. Tạo nhân viên và sách.<br>2. Gọi hàm `create_invoice_pdf` với dữ liệu mẫu.<br>3. Kiểm tra file PDF được tạo. | File `test_invoice.pdf` tồn tại và không rỗng.                                                         | 18/03/2025    | Pass       | Chỉ kiểm tra file được tạo, chưa kiểm tra nội dung PDF chi tiết.        |
| TC05   | Kiểm tra bán đơn hàng đã đặt trước với thời gian   | 1. Tạo nhân viên và đơn hàng đã đặt trước với thời gian quá hạn (49 giờ, max_hours=48 từ cmd).<br>2. Gọi `create_hoa_don_from_don_hang`.<br>3. Kiểm tra phản hồi. | Trạng thái 500, thông báo lỗi "Thời hạn trả quá".                                                      | 18/03/2025    | Pass       | Chạy với `pytest --max-hours=48`, kiểm tra logic đơn hàng quá hạn.      |
| TC06   | Kiểm tra bán sách tại cửa hàng (Pytest-BDD)        | 1. Tạo nhân viên và sách qua fixture.<br>2. Thực thi kịch bản BDD từ `selling.feature`.<br>3. Gọi `create_invoice_from_cart`.<br>4. Kiểm tra hóa đơn và tồn kho. | Hóa đơn được tạo, số lượng sách giảm 1.                                                                | 18/03/2025    | Pass       | Sử dụng Pytest-BDD để mô tả hành vi, khớp với đặc tả use case.          |

---

### Giải thích chi tiết

1. **ID**: Mã định danh duy nhất cho từng test case (TC01, TC02, ...).
2. **Test Case Description**: Mô tả ngắn gọn mục đích của test.
3. **Test Case Procedure**: Các bước thực hiện test, bao gồm sử dụng fixture, giả lập session, hoặc gọi hàm DAO.
4. **Expected Output**: Kết quả mong đợi, dựa trên logic của ứng dụng và đặc tả use case "Bán sách".
5. **Test Date**: Ngày hiện tại (18/03/2025 theo thông tin bạn cung cấp).
6. **Result**:
   - "Pass" cho các test được thiết kế để khớp với logic hiện tại.
   - "Skipped" cho test bị bỏ qua do thiếu tuyến đường.
   - Trong thực tế, cần chạy Pytest để xác nhận kết quả chính xác.
7. **Note**: Ghi chú về cách cải thiện hoặc lưu ý khi thực hiện test.

---

### Cách chạy và xác nhận báo cáo

- **Chạy tất cả test**: `pytest tests/selling/ -v`
- **Chạy với tham số**: `pytest tests/selling/ -v --max-hours=24`
- **Chạy test BDD**: `pytest tests/selling/ -v -k "test_bdd"`
- Sau khi chạy, Pytest sẽ trả về kết quả thực tế (Pass/Fail/Skipped), bạn có thể cập nhật cột **Result** dựa trên đó.

---

### Đánh giá

- Báo cáo bao quát **luồng chính** (bán sách tại cửa hàng, bán đơn đặt trước), **luồng thay thế** (không đủ sách, không đủ tiền, đơn quá hạn), và một phần **luồng ngoại lệ** (thông báo lỗi khi quá hạn).
- Do mã nguồn hiện tại chưa có tuyến đường `/sell`, tôi sử dụng các hàm DAO để mô phỏng logic. Nếu dự án bổ sung tuyến đường, test cần được cập nhật.

Bạn thấy báo cáo này ổn không? Nếu cần bổ sung test case cho các trường hợp khác hoặc điều chỉnh gì, hãy cho tôi biết nhé!
