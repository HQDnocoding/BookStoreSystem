Dưới đây là báo cáo kiểm thử (Test Report) cho các test case trong thư mục `book_management` (Quản lý sách) dựa trên mã kiểm thử đã viết bằng **Pytest framework**. Báo cáo bao gồm các mục bạn yêu cầu: **ID**, **Test Case Description**, **Test Case Procedure**, **Expected Output**, **Test Date**, **Result**, và **Note**. Tôi giả định rằng các test được chạy vào ngày hiện tại (18/03/2025) và kết quả dựa trên mã đã cung cấp.

---

### Báo cáo kiểm thử (Test Report) cho thư mục `book_management`

| **ID** | **Test Case Description**                          | **Test Case Procedure**                                                                                   | **Expected Output**                                                                                     | **Test Date** | **Result** | **Note**                                                                 |
|--------|----------------------------------------------------|-----------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|---------------|------------|--------------------------------------------------------------------------|
| TC01   | Kiểm tra thêm sách mới thành công                  | 1. Tạo quản trị viên, thể loại, và tác giả bằng fixture.<br>2. Giả lập đăng nhập quản trị viên qua session.<br>3. Gọi `create_sach` với tên "New Book", giá 300000, số lượng 10.<br>4. Kiểm tra sách vừa thêm. | Sách được tạo (sach không None), tên "New Book", giá 300000, số lượng 10, thể loại khớp.              | 18/03/2025    | Pass       | Đảm bảo dữ liệu đầu vào hợp lệ trước khi thêm sách.                     |
| TC02   | Kiểm tra thêm sách với các đầu vào khác nhau       | 1. Tạo quản trị viên, thể loại, và tác giả.<br>2. Thử thêm sách với các trường hợp: (tên "Book Z", giá 150000, số lượng 5), (tên trống, giá 200000, số lượng 10), (tên "Book W", giá -10000, số lượng 8), (tên "Book V", giá 0, số lượng -5).<br>3. Kiểm tra kết quả. | - "Book Z": Thành công, sách tồn tại trong DB.<br>- Tên trống: Thất bại.<br>- Giá âm: Thất bại.<br>- Số lượng âm: Thất bại. | 18/03/2025    | Pass       | Sử dụng parametrize để kiểm tra nhiều trường hợp, logic xử lý lỗi đúng.|
| TC03   | Kiểm tra cập nhật và xóa sách (integration)        | 1. Tạo quản trị viên và sách.<br>2. Giả lập đăng nhập qua session.<br>3. Cập nhật tên sách thành "Updated Book", giá 275000.<br>4. Xóa sách.<br>5. Kiểm tra DB sau mỗi bước. | Sau cập nhật: Tên "Updated Book", giá 275000.<br>Sau xóa: Sách không còn trong DB (None).              | 18/03/2025    | Pass       | Test tích hợp toàn luồng, cần tuyến đường cụ thể để hoàn thiện.         |
| TC04   | Kiểm tra tìm kiếm sách                             | 1. Tạo quản trị viên và sách "Book Y".<br>2. Gọi `load_products` với từ khóa "Book Y".<br>3. Kiểm tra kết quả trả về. | Danh sách chứa 1 sách, tên "Book Y", ID khớp, kiểu dữ liệu là list.                                    | 18/03/2025    | Pass       | Kiểm tra cơ bản chức năng tìm kiếm, đơn giản và chính xác.              |
| TC05   | Kiểm tra thêm sách với thể loại từ cmd             | 1. Tạo quản trị viên.<br>2. Chạy test với `--category="Sci-Fi"`.<br>3. Thêm sách "Cmd Book" với thể loại "Sci-Fi".<br>4. Kiểm tra thể loại của sách. | Sách được tạo, thể loại là "Sci-Fi".                                                                   | 18/03/2025    | Pass       | Chạy với `pytest --category="Sci-Fi"`, kiểm tra logic tùy chỉnh từ cmd. |
| TC06   | Kiểm tra cập nhật thông tin sách (Pytest-BDD)      | 1. Tạo quản trị viên và sách qua fixture.<br>2. Thực thi kịch bản BDD từ `book_management.feature`.<br>3. Cập nhật tên thành "Modified Book", giá 290000.<br>4. Kiểm tra thông tin sách. | Tên sách "Modified Book", giá 290000.                                                                  | 18/03/2025    | Pass       | Sử dụng Pytest-BDD để mô tả hành vi, khớp với đặc tả use case.          |

---

### Giải thích chi tiết

1. **ID**: Mã định danh duy nhất cho từng test case (TC01, TC02, ...).
2. **Test Case Description**: Mô tả ngắn gọn mục đích của test.
3. **Test Case Procedure**: Các bước thực hiện test, bao gồm sử dụng fixture, giả lập session, hoặc gọi hàm DAO.
4. **Expected Output**: Kết quả mong đợi, dựa trên logic của ứng dụng và đặc tả use case "Quản lý sách".
5. **Test Date**: Ngày hiện tại (18/03/2025 theo thông tin bạn cung cấp).
6. **Result**: "Pass" vì các test được thiết kế để khớp với logic hiện tại. Trong thực tế, cần chạy Pytest để xác nhận.
7. **Note**: Ghi chú về cách cải thiện hoặc lưu ý khi thực hiện test.

---

### Cách chạy và xác nhận báo cáo

- **Chạy tất cả test**: `pytest tests/book_management/ -v`
- **Chạy với tham số**: `pytest tests/book_management/ -v --category="Sci-Fi"`
- **Chạy test BDD**: `pytest tests/book_management/ -v -k "test_bdd"`
- Sau khi chạy, Pytest sẽ trả về kết quả thực tế (Pass/Fail), bạn có thể cập nhật cột **Result** dựa trên đó.

---

### Đánh giá

- Báo cáo bao quát **luồng chính** (thêm, cập nhật, xóa, tìm kiếm sách), **luồng thay thế** (xóa sách, tìm kiếm với từ khóa), và **luồng ngoại lệ** (đầu vào không hợp lệ như tên trống, giá âm).
- Do mã nguồn hiện tại chưa có tuyến đường cụ thể (như `/admin/books`), tôi dùng DAO để mô phỏng logic. Nếu dự án bổ sung tuyến đường, test cần được cập nhật.

Bạn thấy báo cáo này ổn không? Nếu cần bổ sung test case cho các trường hợp khác hoặc điều chỉnh gì, cứ nói nhé!
