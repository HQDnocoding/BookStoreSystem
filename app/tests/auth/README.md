# kiểm thử và báo cáo kiểm thử cho thư mục `auth` (Xác thực và phân quyền)

## Cách chạy và xác nhận báo cáo

- **Chạy tất cả test**: `pytest app/tests/auth/ -v`
- **Chạy với tham số**: `pytest app/tests/auth/ -v --role=QUANLY`
- **Chạy test BDD**: `pytest app/tests/auth/ -v -k "test_bdd"`
- Sau khi chạy, Pytest sẽ trả về kết quả thực tế (Pass/Fail), bạn có thể cập nhật cột **Result** dựa trên đó.

### Đánh giá

- Báo cáo bao quát **luồng chính** (đăng nhập thành công, phân quyền), **luồng thay thế** (sai thông tin, vai trò khác nhau), và **luồng ngoại lệ** (đăng nhập thất bại).
