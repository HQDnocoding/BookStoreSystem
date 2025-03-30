# Kiểm thử cho thư mục `book_management` (Quản lý sách)

## Cách chạy kiểm thử

1. Cài đặt Pytest: `pip install pytest pytest-bdd`.
2. Chạy tất cả test: `pytest tests/book_management/ -v`.
3. Chạy với tham số: `pytest tests/book_management/ -v --category="Science"`.
4. Chạy test BDD: `pytest tests/book_management/ -v -k "test_bdd"`.

### Đáng giá

- Các test trên bao quát **luồng chính** (thêm, cập nhật, xóa, tìm kiếm sách), **luồng thay thế** (xóa sách, tìm kiếm với từ khóa), và một phần **luồng ngoại lệ** (đầu vào không hợp lệ).
- Hiện tại, mã nguồn không có tuyến đường cụ thể (như `/admin/books`), nên tôi dùng DAO để mô phỏng logic. Nếu dự án bổ sung tuyến đường, test cần được cập nhật.
