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

#### 2. `selling` (Bán sách)

- **Mô tả**: Kiểm thử chức năng nhân viên bán sách tại cửa hàng hoặc xử lý đơn hàng đã đặt trước.
- **Use case liên quan**: "Bán sách".
- **File liên quan**:
  - Các tuyến đường trong `app.py`: Chưa có tuyến đường cụ thể cho "Bán hàng" (có thể cần bổ sung như `/sell`).
  - Hàm trong `dao.py`: `create_invoice_from_cart`, `create_hoa_don_from_don_hang`, `get_don_hang`.
  - Hàm trong `utils.py`: `create_invoice_pdf`, `update_so_luong_by_ct_don_hang`.
- **Kiểm thử**:
  - **Luồng chính**: Chọn "Bán hàng" → Tìm sách/mã đơn hàng → Nhập số tiền → Thanh toán → Xuất hóa đơn.
  - **Luồng thay thế**:
    - Không tìm thấy sách/mã đơn hàng → Báo không tìm thấy.
    - Số tiền không đủ → Không cho thanh toán.
    - Đơn hàng quá hạn/sách không đủ → Không thanh toán.
  - **Luồng ngoại lệ**: Lỗi hệ thống → Báo lỗi và quay về giao diện bán hàng.

#### 3. `inventory` (Nhập sách)

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

#### 4. `book_management` (Quản lý sách)

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

#### 5. `reports` (Xem thống kê báo cáo)

- **Mô tả**: Kiểm thử chức năng xem và xuất báo cáo tần suất bán sách/doanh thu.
- **Use case liên quan**: "Xem thống kê báo cáo".
- **File liên quan**:
  - Hàm trong `utils.py`: `create_pdf_export_freq`, `create_pdf_export_rev`.
  - Hàm trong `dao.py`: `get_stats`, `get_frequency_stats`.
- **Kiểm thử**:
  - **Luồng chính**: Chọn loại báo cáo → Lọc theo tháng/năm/thể loại → Xem/xuất PDF.
  - **Luồng thay thế**: Không có dữ liệu → Hiển thị thông báo và các giá trị bằng 0.
  - **Luồng ngoại lệ**: Lỗi hệ thống → Thông báo lỗi.

#### 6. `rules_management` (Thay đổi quy định)

- **Mô tả**: Kiểm thử chức năng quản trị viên thay đổi các quy định của hệ thống.
- **Use case liên quan**: "Thay đổi quy định".
- **File liên quan**:
  - Model trong `models.py`: `QuyDinh`.
  - Hàm trong `dao.py`: `create_quydinh`, `get_quy_dinh`.
- **Kiểm thử**:
  - **Luồng chính**: Chọn "Quản lý quy định" → Tìm quy định → Thay đổi → Xác nhận → Lưu.
  - **Luồng thay thế**: Lỗi khi thay đổi → Không lưu và thông báo.
  - **Luồng ngoại lệ**: Lỗi hệ thống → Báo lỗi và không thực hiện thay đổi.

#### 7. `auth` (Xác thực và phân quyền)

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

### Tổng cộng: 7 thư mục

Với **7 thư mục** này, tôi đã bao quát toàn bộ các use case quan trọng trong đặc tả, đồng thời đảm bảo mỗi thư mục tập trung vào một nhóm chức năng cụ thể. So với lần phân nhánh trước (10 thư mục), cách này gộp một số chức năng liên quan để phù hợp hơn với đặc tả:

- Gộp `cart` và `orders` vào `ordering`.
- Gộp `comments` vào `ordering` (vì liên quan đến chi tiết sách).
- Gộp `payment` vào `ordering` và `selling` (tùy ngữ cảnh).
- Tập trung vào các use case chính thay vì phân chia quá chi tiết.

---

### Cấu trúc thư mục kiểm thử

```
tests/
├── auth/
├── ordering/
├── selling/
├── inventory/
├── book_management/
├── reports/
└── rules_management/
```

- **Công cụ**: Sử dụng `pytest` hoặc `unittest` để viết test case.
- **Ví dụ test case**:
  - `tests/ordering/test_ordering.py`: Kiểm tra đặt sách với số lượng đủ/thiếu.
  - `tests/selling/test_selling.py`: Kiểm tra bán sách với đơn hàng hợp lệ/quá hạn.
  - `tests/reports/test_reports.py`: Kiểm tra xuất báo cáo với dữ liệu có/không.

---

### Gợi ý kiểm thử chi tiết

1. **ordering**: Kiểm tra toàn bộ luồng đặt sách, bao gồm cả thanh toán qua VNPay và offline.
2. **selling**: Thêm tuyến đường `/sell` nếu chưa có để khớp với đặc tả.
3. **inventory**: Đảm bảo quy định `SL_NHAP_MIN` và `SL_MIN_TO_NHAP` được áp dụng đúng.
4. **reports**: Kiểm tra xuất PDF với font tiếng Việt và dữ liệu trống.

Bạn thấy cách phân nhánh này có phù hợp với đặc tả không? Nếu cần tôi viết test case mẫu cho một thư mục cụ thể hoặc điều chỉnh gì thêm, hãy cho tôi biết nhé!
