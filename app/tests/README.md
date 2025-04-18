### Phân tích đặc tả và đề xuất phân nhánh

Dựa trên các **use case quan trọng** trong đặc tả (Đặt sách, Bán sách, Nhập sách, Quản lý sách, Xem thống kê báo cáo, Thay đổi quy định), tôi đề xuất phân nhánh thành **7 thư mục** chính để kiểm thử. Mỗi thư mục sẽ tương ứng với một nhóm chức năng hoặc use case, đồng thời bao quát các luồng chính, luồng thay thế và luồng ngoại lệ. Dưới đây là chi tiết:

#### 1. `ordering` (Đặt sách)

- **Mô tả**: Kiểm thử chức năng khách hàng đặt sách trực tuyến, từ chọn sách, thêm vào giỏ hàng, đến thanh toán và lập đơn hàng.
- **Use case liên quan**: "Đặt sách".
- **File liên quan**:
  - Các tuyến đường trong `app.py`: `/shop`, `/books/<sach_id>`, `/cart`, `/api/cart`, `/payment`, `/process_payment`, `/payment_offline`.
  - Hàm trong `dao.py`: `create_donhang`, `create_chitietdonhang`, `create_thongtinnhanhang`.
  - Hàm trong `utils.py`: `cart_stats`, `check_if_expire_orders`.
- **Kiểm thử**:
  - **Luồng chính**: Chọn sách → Thêm vào giỏ hàng → Chọn phương thức thanh toán → Điền thông tin nhận hàng → Xác nhận đơn hàng.
  - **Luồng thay thế**:
    - Số lượng sách không đủ → Báo lỗi thiếu sách.
    - Chưa đăng nhập → Yêu cầu đăng nhập.
    - Thiếu thông tin nhận hàng → Thông báo lỗi và không lập đơn.
  - **Luồng ngoại lệ**: Lỗi hệ thống → Hiển thị thông báo lỗi.

#### 2. `inventory` (Nhập sách)

- **Mô tả**: Kiểm thử chức năng quản lý kho nhập sách và cập nhật số lượng tồn kho.
- **Use case liên quan**: "Nhập sách".
- **File liên quan**:
  - Các model trong `models.py`: `PhieuNhapSach`, `ChiTietPhieuNhapSach`.
  - Hàm trong `dao.py`: `create_phieunhapsach`, `create_chitietphieunhapsach`, `add_so_luong`.
  - Hàm trong `utils.py`: `create_pdf_export_nhap_sach`.
- **Kiểm thử**:
  - **Luồng chính**: Chọn "Nhập sách" → Nhập thông tin sách/số lượng → Xác nhận → In phiếu nhập sách.
  - **Luồng thay thế**:
    - Số lượng sách trong kho vượt quy định (`SL_NHAP_MIN`) → Báo lỗi và không nhập.
    - Số lượng sách dưới quy định (`SL_MIN_TO_NHAP`) → Báo lỗi và không nhập.
  - **Luồng ngoại lệ**: Lỗi hệ thống → Quay về giao diện nhập sách.

#### 3. `book_management` (Quản lý sách)

- **Mô tả**: Kiểm thử chức năng quản trị viên thêm, xóa, cập nhật, và tìm kiếm sách.
- **Use case liên quan**: "Quản lý sách".
- **File liên quan**:
  - Các tuyến đường trong `app.py`: Chưa có tuyến đường cụ thể (có thể liên quan đến `/admin`).
  - Hàm trong `dao.py`: `create_sach`, `load_products`, `count_sach`, `get_id_the_loai`, `get_id_tac_gia`.
- **Kiểm thử**:
  - **Luồng chính**: Chọn "Quản lý sách" → Xem danh sách → Chỉnh sửa → Xác nhận.
  - **Luồng thay thế**:
    - Xóa sách → Xác nhận → Cập nhật danh sách.
    - Tìm kiếm sách → Nhập từ khóa → Hiển thị kết quả.
  - **Luồng ngoại lệ**: Lỗi hệ thống → Báo lỗi và không thực hiện thao tác.

#### 4. `reports` (Xem thống kê báo cáo)

- **Mô tả**: Kiểm thử chức năng xem và xuất báo cáo tần suất bán sách/doanh thu.
- **Use case liên quan**: "Xem thống kê báo cáo".
- **File liên quan**:
  - Hàm trong `utils.py`: `create_pdf_export_freq`, `create_pdf_export_rev`.
  - Hàm trong `dao.py`: `get_stats`, `get_frequency_stats`.
- **Kiểm thử**:
  - **Luồng chính**: Chọn loại báo cáo → Lọc theo tháng/năm/thể loại → Xem/xuất PDF.
  - **Luồng thay thế**: Không có dữ liệu → Hiển thị thông báo và các giá trị bằng 0.
  - **Luồng ngoại lệ**: Lỗi hệ thống → Thông báo lỗi.

#### 5. `rules_management` (Thay đổi quy định)

- **Mô tả**: Kiểm thử chức năng quản trị viên thay đổi các quy định của hệ thống.
- **Use case liên quan**: "Thay đổi quy định".
- **File liên quan**:
  - Model trong `models.py`: `QuyDinh`.
  - Hàm trong `dao.py`: `create_quydinh`, `get_quy_dinh`.
- **Kiểm thử**:
  - **Luồng chính**: Chọn "Quản lý quy định" → Tìm quy định → Thay đổi → Xác nhận → Lưu.
  - **Luồng thay thế**: Lỗi khi thay đổi → Không lưu và thông báo.
  - **Luồng ngoại lệ**: Lỗi hệ thống → Báo lỗi và không thực hiện thay đổi.

#### 6. `auth` (Xác thực và phân quyền)

- **Mô tả**: Kiểm thử đăng nhập và phân quyền cho các vai trò (khách hàng, nhân viên, quản lý kho, quản trị viên).
- **Use case liên quan**: Điều kiện tiên quyết của tất cả use case.
- **File liên quan**:
  - Các tuyến đường trong `app.py`: `/login`, `/register`, `/logout`.
  - Hàm trong `dao.py`: `auth_user`, `create_user`.
  - Decorators trong `decorators.py`.
- **Kiểm thử**:
  - Đăng nhập thành công/thất bại với các vai trò.
  - Phân quyền truy cập chức năng theo vai trò (`KHACHHANG`, `NHANVIEN`, `QUANLYKHO`, `QUANLY`).

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
