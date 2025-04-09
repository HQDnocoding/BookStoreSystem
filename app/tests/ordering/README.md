# Phần kiểm thử (Test Report) cho các test case trong thư mục `ordering` (Đặt sách)

## Cách chạy và xác nhận báo cáo

- **Chạy tất cả test**: `pytest tests/ordering/ -v`
- **Chạy với tham số**: `pytest tests/ordering/ -v --payment-method=OFFLINE_PAY`
- **Chạy test BDD**: `pytest tests/ordering/ -v -k "test_bdd"`
- Sau khi chạy, Pytest sẽ trả về kết quả thực tế (Pass/Fail), bạn có thể cập nhật cột **Result** dựa trên đó.

### Đánh giá

- Báo cáo này bao quát **luồng chính** (thêm sách, tạo đơn hàng), **luồng thay thế** (số lượng không đủ), và một phần **luồng ngoại lệ** (chưa kiểm tra lỗi hệ thống chi tiết).
- Các chủ đề Pytest (Fixtures, Parametrize, Markers, Assertions, Command-line Args, Pytest-BDD) được sử dụng hợp lý để đảm bảo tính linh hoạt và tái sử dụng.
