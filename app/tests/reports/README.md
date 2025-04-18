# Phần kiểm thử cho thư mục `reports` (Xem thống kê báo cáo)

## Cách chạy và xác nhận báo cáo

- **Chạy tất cả test**: `pytest tests/reports/ -v`
- **Chạy với tham số**: `pytest tests/reports/ -v --month=4`
- **Chạy test BDD**: `pytest tests/reports/ -v -k "test_bdd"`
- Sau khi chạy, Pytest sẽ trả về kết quả thực tế (Pass/Fail), bạn có thể cập nhật cột **Result** dựa trên đó.

### Đánh giá

- Báo cáo bao quát **luồng chính** (tạo báo cáo doanh thu/tần suất), **luồng thay thế** (không có dữ liệu, thể loại không tồn tại), và một phần **luồng ngoại lệ** (chưa kiểm tra lỗi hệ thống chi tiết).
- Do mã nguồn hiện tại chưa có tuyến đường cụ thể (như `/admin/reports`), tôi dùng DAO và utils để mô phỏng logic. Nếu dự án bổ sung tuyến đường, test cần được cập nhật.
