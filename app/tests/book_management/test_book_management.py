import pytest
from flask import url_for

from app import app, db
from app.dao import count_sach, create_sach, load_products


# Test Naming and Test Discovery
def test_create_book_success(admin_user, category_and_author):
    """Kiểm tra thêm sách mới thành công (Unit Test)."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = admin_user.id  # Giả lập đăng nhập quản trị viên

        # Thêm sách mới
        with app.app_context():
            sach = create_sach(
                ten_sach="New Book",
                don_gia=300000,
                the_loai_id=category_and_author["the_loai"].id,
                tac_gia_id=category_and_author["tac_gia"].id,
            )
            sach.so_luong = 10

        # Assertions
        assert sach is not None
        assert sach.ten_sach == "New Book"
        assert sach.don_gia == 300000
        assert sach.so_luong == 10
        assert sach.the_loai_id == category_and_author["the_loai"].id


# Parametrized Testing
@pytest.mark.parametrize(
    "book_name, price, stock, expected_success",
    [
        ("Book Z", 150000, 5, True),  # Thêm sách hợp lệ
        ("", 200000, 10, False),  # Tên sách trống
        ("Book W", -10000, 8, False),  # Giá âm
        ("Book V", 0, -5, False),  # Số lượng âm
    ],
)
def test_create_book_with_different_inputs(
    admin_user, category_and_author, book_name, price, stock, expected_success
):
    """Kiểm tra thêm sách với các đầu vào khác nhau (Unit Test)."""
    with app.app_context():
        try:
            sach = create_sach(
                ten_sach=book_name,
                don_gia=price,
                the_loai_id=category_and_author["the_loai"].id,
                tac_gia_id=category_and_author["tac_gia"].id,
            )
            sach.so_luong = stock
            db.session.commit()
            result = True
        except ValueError:
            db.session.rollback()
            result = False

        # Assertions
        assert result == expected_success
        if expected_success:
            assert Sach.query.filter_by(ten_sach=book_name).first() is not None


# Skipping Tests and Markers
@pytest.mark.skipif(
    app.config.get("ENV") == "production",
    reason="Không chạy trong môi trường production",
)
def test_update_and_delete_book_integration(admin_user, book):
    """Kiểm tra cập nhật và xóa sách (Integration Test)."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = admin_user.id

        # Cập nhật sách
        with app.app_context():
            book.ten_sach = "Updated Book"
            book.don_gia = 275000
            db.session.commit()
            assert Sach.query.get(book.id).ten_sach == "Updated Book"
            assert Sach.query.get(book.id).don_gia == 275000

            # Xóa sách
            db.session.delete(book)
            db.session.commit()
            assert Sach.query.get(book.id) is None


# Different Types of Assertions
def test_search_books(admin_user, book):
    """Kiểm tra tìm kiếm sách (Unit Test)."""
    with app.app_context():
        books = load_products(kw="Book Y")

        # Assertions
        assert isinstance(books, list)  # Kiểm tra kiểu dữ liệu
        assert len(books) == 1  # Kiểm tra số lượng kết quả
        assert books[0].ten_sach == "Book Y"  # Kiểm tra giá trị
        assert books[0].id == book.id  # Kiểm tra định danh


# Passing Command-line Args in Pytest
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
        )
        sach.so_luong = 15

        assert (
            sach.the_loai_id
            == TheLoai.query.filter_by(ten_the_loai=category_name).first().id
        )


# Pytest-BDD
from pytest_bdd import given, scenarios, then, when

scenarios("book_management.feature")


@given("quản trị viên đã đăng nhập")
def admin_logged_in(admin_user):
    return {"admin": admin_user}


@given("có một cuốn sách trong hệ thống")
def book_in_system(book):
    return {"book": book}


@when("quản trị viên cập nhật thông tin sách")
def update_book(admin_logged_in, book_in_system):
    with app.app_context():
        book_in_system["book"].ten_sach = "Modified Book"
        book_in_system["book"].don_gia = 290000
        db.session.commit()
    return {"book": book_in_system["book"]}


@then("thông tin sách được cập nhật trong hệ thống")
def book_info_updated(update_book):
    updated_book = Sach.query.get(update_book["book"].id)
    assert updated_book.ten_sach == "Modified Book"
    assert updated_book.don_gia == 290000
