# Phần kiểm thử và báo cáo kiểm thử cho thư mục `rules_management` (Thay đổi quy định)

## Cách chạy và xác nhận báo cáo

- **Chạy tất cả test**: `pytest tests/rules_management/ -v`
- **Chạy với tham số**: `pytest tests/rules_management/ -v --timeout=72`
- **Chạy test BDD**: `pytest tests/rules_management/ -v -k "test_bdd"`
- Sau khi chạy, Pytest sẽ trả về kết quả thực tế (Pass/Fail), bạn có thể cập nhật cột **Result** dựa trên đó.

### Đánh giá

- Báo cáo bao quát **luồng chính** (thay đổi quy định thành công), **luồng thay thế** (giá trị không hợp lệ), và một phần **luồng ngoại lệ** (chưa kiểm tra lỗi hệ thống chi tiết).
- Do mã nguồn hiện tại chưa có tuyến đường cụ thể (như `/admin/rules`), tôi dùng DAO để mô phỏng logic. Nếu dự án bổ sung tuyến đường, test cần được cập nhật.
