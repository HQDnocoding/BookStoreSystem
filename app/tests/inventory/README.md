# Phần kiểm thử (Test Report) cho các test case trong thư mục `inventory` (Nhập sách)

## Cách chạy và xác nhận báo cáo

- **Chạy tất cả test**: `pytest tests/inventory/ -v`
- **Chạy với tham số**: `pytest tests/inventory/ -v --min-quantity=10`
- **Chạy test BDD**: `pytest tests/inventory/ -v -k "test_bdd"`
- Sau khi chạy, Pytest sẽ trả về kết quả thực tế (Pass/Fail), bạn có thể cập nhật cột **Result** dựa trên đó.

### Đánh giá

- Báo cáo bao quát **luồng chính** (nhập sách thành công), **luồng thay thế** (tồn kho đủ, nhập dưới mức tối thiểu), và một phần **luồng ngoại lệ** (chưa kiểm tra lỗi hệ thống chi tiết).
- Do mã nguồn hiện tại chưa có tuyến đường cụ thể (như `/import`), tôi dùng các hàm DAO để mô phỏng logic. Nếu dự án bổ sung tuyến đường, test cần được cập nhật.
