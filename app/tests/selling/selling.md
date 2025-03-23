Dưới đây là phần kiểm thử cho thư mục `selling` (Bán sách) sử dụng **Pytest framework**, tập trung vào use case "Bán sách" từ đặc tả của bạn. Tôi sẽ kết hợp các chủ đề bạn liệt kê (Test Naming, Assertions, Skipping Tests, Markers, Parametrized Testing, Fixtures, Command-line Args, và Pytest-BDD nếu phù hợp) để tạo ra một bộ kiểm thử hợp lý. Tôi sẽ viết cả **unit test** và **integration test** để kiểm tra các khía cạnh quan trọng của chức năng bán sách.

---

### Cấu trúc thư mục kiểm thử

```
tests/
├── selling/
│   ├── __init__.py
│   ├── test_selling.py
│   └── conftest.py  # Để định nghĩa fixtures
```

---

### File `conftest.py` (Fixtures)

Tôi sẽ định nghĩa các **fixtures** để tái sử dụng trong các test case, chuẩn bị dữ liệu cần thiết cho việc bán sách.

---

### File `test_selling.py` (Test Case)

---

### File `selling.feature` (Pytest-BDD)

---

### Giải thích cách sử dụng các chủ đề

1. **Test Naming and Test Discovery**:
   - Tên test như `test_create_invoice_from_cart_success`, `test_sell_preordered_with_timeout` rõ ràng, bắt đầu bằng `test_` để Pytest tự động phát hiện.

2. **Different Types of Assertions**:
   - Sử dụng `assert` để kiểm tra sự tồn tại (`is not None`), giá trị bằng (`==`), chứa chuỗi (`in`), và kích thước file (`> 0`).

3. **Skipping Tests and Markers**:
   - `@pytest.mark.skip` được dùng để bỏ qua test `test_sell_at_store` vì hiện tại chưa có tuyến đường cụ thể trong mã nguồn.

4. **Parametrized or Data-Driven Testing**:
   - `@pytest.mark.parametrize` kiểm tra `test_sell_book_with_different_conditions` với các trường hợp: đủ tiền/đủ sách, không đủ sách, không đủ tiền.

5. **Fixtures**:
   - Các fixture như `employee_user`, `book`, `customer_order` chuẩn bị dữ liệu nhân viên, sách, và đơn hàng đã đặt trước.

6. **Passing Command-line Args in Pytest**:
   - `pytestconfig.getoption("--max-hours")` lấy thời gian tối đa từ dòng lệnh để kiểm tra đơn hàng quá hạn (chạy: `pytest --max-hours=24`).

7. **Pytest-BDD**:
   - Sử dụng Gherkin syntax trong `selling.feature` để mô tả hành vi bán sách tại cửa hàng, triển khai các bước `given`, `when`, `then`.

---

### Cách chạy kiểm thử

1. Cài đặt Pytest: `pip install pytest pytest-bdd`.
2. Chạy tất cả test: `pytest tests/selling/ -v`.
3. Chạy với tham số: `pytest tests/selling/ -v --max-hours=24`.
4. Chạy test BDD: `pytest tests/selling/ -v -k "test_bdd"`.

---

### Nhận xét

- Các test trên bao quát **luồng chính** (bán sách tại cửa hàng, bán đơn đặt trước), **luồng thay thế** (không đủ sách, không đủ tiền, đơn quá hạn), và một phần **luồng ngoại lệ** (lỗi hệ thống khi quá hạn).
- Hiện tại, mã nguồn chưa có tuyến đường cụ thể cho `/sell`, nên tôi sử dụng các hàm DAO (`create_invoice_from_cart`, `create_hoa_don_from_don_hang`) để mô phỏng logic bán sách.

Bạn thấy bộ kiểm thử này thế nào? Nếu cần thêm test cho các trường hợp khác (như lỗi hệ thống chi tiết hơn) hoặc điều chỉnh gì, cứ nói nhé!
