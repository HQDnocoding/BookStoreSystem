import pytest
from sqlalchemy.exc import SQLAlchemyError

from app import app, db
from app.dao import count_sach, create_sach, load_products
from app.models import Sach, TacGia, TheLoai


# Test Naming and Test Discovery => PASSED
def test_create_book_success(admin_user, category_and_author):
    """Kiểm tra thêm sách mới thành công (Unit Test)."""
    with app.app_context():
        sach = create_sach(
            ten_sach="New Book",
            don_gia=300000,
            the_loai_id=category_and_author["the_loai"].id,
            tac_gia_id=category_and_author["tac_gia"].id,
            so_luong=10,
        )

        # Assertions
        assert sach is not None
        assert sach.ten_sach == "New Book"
        assert sach.don_gia == 300000
        assert sach.so_luong == 10
        assert sach.the_loai_id == category_and_author["the_loai"].id
        assert sach.tac_gia_id == category_and_author["tac_gia"].id


# Parametrized Testing => PASSED
@pytest.mark.parametrize(
    "book_name, price, amount,  expected_success, expected_error",
    [
        ("Book Z", 150000, 5, True, None),  # Trường hợp hợp lệ
        ("", 200000, 10, False, ValueError),  # Tên trống
        ("Book W", -10000, 8, False, ValueError),  # Giá âm
        ("Book V", 0, -5, False, ValueError),  # Số lượng âm
    ],
)
def test_create_book_with_different_inputs(
    admin_user,
    category_and_author,
    book_name,
    price,
    amount,
    expected_success,
    expected_error,
):
    """Kiểm tra thêm sách với các đầu vào khác nhau (Unit Test)."""
    with app.app_context():
        try:
            the_loai_id = category_and_author["the_loai"].id
            tac_gia_id = category_and_author["tac_gia"].id

            create_sach(
                ten_sach=book_name,
                don_gia=price,
                the_loai_id=the_loai_id,
                tac_gia_id=tac_gia_id,
                so_luong=amount,
            )
            result = True
        except expected_error:
            result = False
        except Exception as e:
            pytest.fail(f"Lỗi không mong đợi: {str(e)}")

        # Assertions
        assert result == expected_success
        if expected_success:
            fetched_sach = Sach.query.filter_by(ten_sach=book_name).first()
            assert fetched_sach is not None


# Skipping Tests and Markers => SKIPPED
@pytest.mark.skipif(
    app.config.get("ENV") == "production",
    reason="Không chạy trong môi trường production",
)
def test_update_and_delete_book_integration(login_admin, book):
    """Kiểm tra cập nhật và xóa sách (Integration Test)."""
    with app.app_context():
        # Cập nhật sách
        book.ten_sach = "Updated Book"
        book.don_gia = 275000
        db.session.commit()

        book_id = book.id
        updated_book = Sach.query.get(book_id)
        assert updated_book.ten_sach == "Updated Book"
        assert updated_book.don_gia == 275000

        # Xóa sách
        db.session.delete(book)
        db.session.commit()
        assert Sach.query.get(book_id) is None


# Different Types of Assertions => PASSED
def test_search_books(admin_user, book):
    """Kiểm tra tìm kiếm sách (Unit Test)."""
    with app.app_context():
        books = load_products(kw="Book Y")

        # Assertions
        assert isinstance(books, list)  # Kiểm tra kiểu dữ liệu
        assert len(books) == 1  # Kiểm tra số lượng kết quả
        assert books[0].ten_sach == "Book Y"  # Kiểm tra giá trị
        assert books[0].id == book.id  # Kiểm tra định danh


# Test đếm sách => PASSED
def test_count_sach(admin_user, book):
    """Kiểm tra chức năng đếm số lượng sách."""
    with app.app_context():
        count = count_sach(kw="Book Y")
        assert count == 1  # Số lượng sách tìm thấy không đúng

        count_all = count_sach()
        assert count_all >= 1  # Tổng số sách phải lớn hơn hoặc bằng 1


# Passing Command-line Args in Pytest => PASSED
def test_create_book_with_custom_category(admin_user, pytestconfig):
    """Kiểm tra thêm sách với thể loại từ cmd (Unit Test)."""
    category_name = pytestconfig.getoption("--category", default="Fiction")
    with app.app_context():
        the_loai = TheLoai(ten_the_loai=category_name)
        tac_gia = TacGia(ten_tac_gia="Author C")
        db.session.add_all([the_loai, tac_gia])
        db.session.commit()

        sach = create_sach(
            ten_sach="Cmd Book",
            don_gia=180000,
            the_loai_id=the_loai.id,
            tac_gia_id=tac_gia.id,
            so_luong=15,
        )

        assert (
            sach.the_loai_id
            == TheLoai.query.filter_by(ten_the_loai=category_name).first().id
        )


# Tìm kiếm không có kết quả => PASSED
def test_search_books_no_results(admin_user):
    """Kiểm tra tìm kiếm sách khi không có kết quả."""
    with app.app_context():
        books = load_products(kw="NonExistentBook")
        assert isinstance(books, list)  # Kết quả phải là danh sách
        assert len(books) == 0  # Không nên tìm thấy sách nào


# Pytest-BDD
from pytest_bdd import given, parsers, scenarios, then, when

# Khai báo feature file
scenarios("./features/book_management.feature")


# Background: Quản trị viên đăng nhập => PASSED
@given(
    parsers.parse('quản trị viên đã đăng nhập với vai trò "{role}"'),
    target_fixture="admin_logged_in",
)
def admin_logged_in(admin_user, role):
    """Giả lập quản trị viên đăng nhập."""
    assert admin_user.vai_tro.ten_vai_tro == role
    return {"admin": admin_user}


# Step: Tạo sách ban đầu trong hệ thống => PASSED
@given(
    parsers.parse("có một cuốn sách trong hệ thống với thông tin ban đầu:"),
    target_fixture="book_in_system",
)
def book_in_system(app_context, datatable):
    """Tạo một cuốn sách trong hệ thống với dữ liệu ban đầu từ bảng."""
    print("\nbook_in_system: ")
    
    # Lấy header và row đầu tiên (dữ liệu thực tế)
    headers = datatable[0]  # ['Tên sách', 'Đơn giá', 'Số lượng', 'Thể loại', 'Tác giả']
    values = datatable[1]   # ['Test Book', '200000', '5', 'Non-Fiction', 'Author B']

    # Chuyển list thành dictionary
    data = dict(zip(headers, values))
    print(data)
    
    the_loai = TheLoai(ten_the_loai=data["Thể loại"])
    tac_gia = TacGia(ten_tac_gia=data["Tác giả"])
    db.session.add_all([the_loai, tac_gia])
    db.session.commit()

    book = create_sach(
        ten_sach=data["Tên sách"],
        don_gia=int(data["Đơn giá"]),
        so_luong=int(data["Số lượng"]),
        the_loai_id=the_loai.id,
        tac_gia_id=tac_gia.id,
    )
    return {"book": book}


# Step: Quản trị viên cập nhật thông tin sách => PASSED
@when(
    parsers.parse("quản trị viên cập nhật thông tin sách thành:"),
    target_fixture="update_result",
)
def update_book(app_context, admin_logged_in, book_in_system, datatable):
    """Cập nhật thông tin sách và trả về kết quả."""
    print("\nupdate_book: ")
    # Lấy header và row đầu tiên (dữ liệu thực tế)
    headers = datatable[0]  # ['Tên sách', 'Đơn giá', 'Số lượng', 'Thể loại', 'Tác giả']
    values = datatable[1]   # ['Test Book', '200000', '5', 'Non-Fiction', 'Author B']

    # Chuyển list thành dictionary
    data = dict(zip(headers, values))
    print(data)
    
    errors = []

    # Kiểm tra dữ liệu hợp lệ
    if not data["Tên sách"].strip():
        errors.append("Tên sách không được rỗng.")
    try:
        don_gia = int(data["Đơn giá"])
        if don_gia < 0:
            errors.append("Đơn giá phải là số không âm.")
    except ValueError:
        errors.append("Đơn giá phải là một số hợp lệ.")

    try:
        so_luong = int(data["Số lượng"])
        if so_luong < 0:
            errors.append("Số lượng phải là số không âm.")
    except ValueError:
        errors.append("Số lượng phải là một số hợp lệ.")

    # Nếu có lỗi, không cập nhật dữ liệu
    if errors:
        return {"success": False, "book": book_in_system["book"], "errors": errors}
    
    # Cập nhật sách nếu không có lỗi
    book = book_in_system["book"]
    book.ten_sach = data["Tên sách"]
    book.don_gia = don_gia
    book.so_luong = so_luong

    try:
        db.session.commit()
        return {"success": True, "book": book, "errors": []}
    except Exception as e:
        db.session.rollback()  # Đảm bảo không commit dữ liệu sai
        return {"success": False, "book": book, "errors": [str(e)]}


# Step: Kiểm tra thông tin sách được cập nhật => PASSED
@then(
    parsers.parse(
        "thông tin sách được cập nhật trong hệ thống với các giá trị:"
    )
)
def book_info_updated(app_context, update_result, datatable):
    """Kiểm tra thông tin sách đã được cập nhật thành công."""
    print("\nbook_info_updated: ")
    
    # Lấy header và row đầu tiên (dữ liệu thực tế)
    headers = datatable[0]  # ['Tên sách', 'Đơn giá', 'Số lượng', 'Thể loại', 'Tác giả']
    values = datatable[1]   # ['Test Book', '200000', '5', 'Non-Fiction', 'Author B']

    # Chuyển list thành dictionary
    data = dict(zip(headers, values))
    print(data)
    
    assert update_result["success"], "Cập nhật sách thất bại"
    book = update_result["book"]
    assert (
        book.ten_sach == data["Tên sách"]
    ), f"Tên sách không khớp: {book.ten_sach} != {data['Tên sách']}"
    assert book.don_gia == int(
        data["Đơn giá"]
    ), f"Đơn giá không khớp: {book.don_gia} != {data['Đơn giá']}"
    assert book.so_luong == int(
        data["Số lượng"]
    ), f"Số lượng không khớp: {book.so_luong} != {data['Số lượng']}"


# Step: Kiểm tra lỗi khi cập nhật thông tin không hợp lệ
@then(parsers.parse("hệ thống từ chối cập nhật và thông báo lỗi:"))
def check_update_failure(app_context, update_result, datatable):
    """Kiểm tra hệ thống từ chối cập nhật và trả về lỗi chính xác."""
    print("\ncheck_update_failure: ")
    # Kiểm tra nếu datatable có header thì bỏ qua
    expected_errors = [row[0] for row in datatable[1:]] if len(datatable) > 1 else [] # Bỏ qua dòng đầu tiên
    print("Expected Errors:", expected_errors)
    print("update_result:", update_result)

    assert not update_result["success"] # Cập nhật lẽ ra phải thất bại
    # Kiểm tra nếu ít nhất một lỗi mong đợi có trong lỗi thực tế
    if any(error in update_result["errors"] for error in expected_errors):
        return True  # Thành công nếu có ít nhất một lỗi mong đợi xuất hiện

    # Nếu không có lỗi mong đợi nào khớp, báo lỗi chi tiết
    assert False, (
        f"Không có lỗi mong đợi nào trong danh sách lỗi thực tế.\n"
        f"- Mong đợi: {expected_errors}\n"
        f"- Nhận được: {update_result['errors']}"
    )


# Step: Không có sách với ID cụ thể
@given(
    parsers.parse('không có sách nào trong hệ thống với ID "{book_id}"'),
    target_fixture="no_book",
)
def no_book_in_system(app_context, book_id):
    """Xác nhận không có sách với ID được cung cấp."""
    book = Sach.query.get(book_id)
    assert book is None, f"Sách với ID {book_id} không được tồn tại"
    return {"book_id": book_id}


# Step: Cố gắng cập nhật sách không tồn tại
@when(
    parsers.parse(
        'quản trị viên cố gắng cập nhật sách với ID "{book_id}" thành:'
    ),
    target_fixture="update_result",
)
def update_nonexistent_book(app_context, admin_logged_in, no_book, book_id, datatable):
    """Thử cập nhật một cuốn sách không tồn tại."""
    print("\nupdate_nonexistent_book: ")
    # Lấy header và row đầu tiên (dữ liệu thực tế)
    headers = datatable[0]  # ['Tên sách', 'Đơn giá', 'Số lượng', 'Thể loại', 'Tác giả']
    values = datatable[1]   # ['Test Book', '200000', '5', 'Non-Fiction', 'Author B']

    # Chuyển list thành dictionary
    data = dict(zip(headers, values))
    print(data)
    
    try:
        book = Sach.query.get(book_id)
        if book is None:
            return {
                "success": False,
                "errors": [f"Sách với ID {book_id} không tồn tại"],
            }
        book.ten_sach = data["Tên sách"]
        book.don_gia = int(data["Đơn giá"])
        book.so_luong = int(data["Số lượng"])
        db.session.commit()
        return {"success": True, "book": book, "errors": []}
    except Exception as e:
        return {"success": False, "errors": [f"Sách với ID {book_id} không tồn tại"]}
