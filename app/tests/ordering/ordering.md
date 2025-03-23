Dưới đây là phần kiểm thử cho thư mục `ordering` (Đặt sách) sử dụng **Pytest framework**, tập trung vào use case "Đặt sách" từ đặc tả của bạn. Tôi sẽ kết hợp các chủ đề bạn liệt kê (Test Naming, Assertions, Skipping Tests, Markers, Parametrized Testing, Fixtures, Command-line Args, và Pytest-BDD nếu phù hợp) để tạo ra một bộ kiểm thử hợp lý. Tôi sẽ viết cả **unit test** và **integration test** để kiểm tra các khía cạnh quan trọng của chức năng đặt sách.

---

### Cấu trúc thư mục kiểm thử

```
tests/
├── ordering/
│   ├── __init__.py
│   ├── test_ordering.py
│   └── conftest.py  # Để định nghĩa fixtures
```

---

### File `conftest.py` (Fixtures)

Trước tiên, tôi sẽ định nghĩa một số **fixtures** để tái sử dụng trong các test case. Fixture là một trong những tính năng mạnh mẽ của Pytest, giúp chuẩn bị dữ liệu hoặc trạng thái trước khi chạy test.

---

### File `test_ordering.py` (Test Case)

---

### File `ordering.feature` (Pytest-BDD)

---

### Giải thích cách sử dụng các chủ đề

1. **Test Naming and Test Discovery**:
   - Tên test như `test_add_to_cart_success`, `test_create_order_integration` rõ ràng, bắt đầu bằng `test_` để Pytest tự động phát hiện.

2. **Different Types of Assertions**:
   - Sử dụng `assert` để kiểm tra mã trạng thái (`status_code`), giá trị (`total_quantity`), kiểu dữ liệu (`isinstance`), và sự tồn tại của key (`"alert" not in`).

3. **Skipping Tests and Markers**:
   - Sử dụng `@pytest.mark.skipif` để bỏ qua test trong môi trường production.

4. **Parametrized or Data-Driven Testing**:
   - `@pytest.mark.parametrize` kiểm tra `test_add_to_cart_with_different_quantities` với nhiều trường hợp số lượng (hợp lệ, vượt quá, không hợp lệ).

5. **Fixtures**:
   - Các fixture như `app_context`, `customer_user`, `book` được định nghĩa trong `conftest.py` để tái sử dụng, chuẩn bị dữ liệu trước test.

6. **Passing Command-line Args in Pytest**:
   - `pytestconfig.getoption` lấy giá trị `--payment-method` từ dòng lệnh (chạy: `pytest --payment-method=OFFLINE_PAY`).

7. **Pytest-BDD**:
   - Sử dụng Gherkin syntax trong `ordering.feature` và triển khai các bước `given`, `when`, `then` để mô tả hành vi đặt sách.

---

### Cách chạy kiểm thử

1. Cài đặt Pytest: `pip install pytest pytest-bdd`.
2. Chạy tất cả test: `pytest tests/ordering/`.
3. Chạy với tham số: `pytest tests/ordering/ --payment-method=OFFLINE_PAY`.
4. Chạy test BDD: `pytest tests/ordering/ -k "test_bdd"`.

---

### Nhận xét

- Các test trên bao quát **luồng chính** (thêm sách, tạo đơn hàng), **luồng thay thế** (số lượng không đủ), và có thể mở rộng để kiểm tra **luồng ngoại lệ** (lỗi hệ thống) bằng cách mock lỗi.
- Tôi tập trung vào `ordering` như bạn yêu cầu, chưa chạm đến các thư mục khác.

Bạn thấy bộ kiểm thử này thế nào? Nếu cần điều chỉnh hoặc mở rộng thêm (ví dụ: thêm test cho thanh toán VNPay), cứ nói nhé!
