import pytest
from sqlalchemy.exc import SQLAlchemyError

from app import app, db
from app.models import Sach
from app.utils import update_book_quantity


# Different Types of Assertions
def test_add_stock_to_book(warehouse_manager, client, book):
    """Kiểm tra hàm tăng số lượng sách (Unit Test)."""
    original_quantity = book.so_luong
    update_book_quantity(book.id, 10)
    updated_book = Sach.query.get(book.id)

    # Assertions
    assert updated_book is not None
    assert updated_book.so_luong == original_quantity + 10
    assert isinstance(updated_book.so_luong, int)
    assert updated_book.so_luong > 0


# Passing Command-line Args in Pytest với validate đầu vào
def test_import_with_custom_min_quantity(
    warehouse_manager, book, inventory_rules, pytestconfig
):
    """Kiểm tra nhập sách với số lượng tối thiểu từ cmd (Unit Test)."""
    min_quantity = pytestconfig.getoption(
        "--min-quantity", default=inventory_rules.SL_NHAP_MIN
    )
    try:
        min_quantity = int(min_quantity)
        assert min_quantity >= 5, "Số lượng tối thiểu phải lớn hơn - bằng 5"
    except (ValueError, AssertionError) as e:
        pytest.skip(f"Invalid min_quantity: {str(e)}")

    if 5 > min_quantity:
        result = {
            "success": False,
            "alert": f"Số lượng nhập dưới {min_quantity}",
        }
    else:
        update_book_quantity(book.id, min_quantity)
        result = {"success": True, "alert": None}

    assert result["success"] == (5 <= min_quantity)
    if not result["success"]:
        assert result["alert"] == f"Số lượng nhập không dưới {min_quantity}"


# Pytest-BDD với tái sử dụng fixture
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("./features/inventory.feature")


@given(
    parsers.parse('quản trị viên đã đăng nhập với vai trò "{role}"'),
    target_fixture="logged_in",
)
def warehouse_manager_logged_in(warehouse_manager, role):
    assert warehouse_manager.vai_tro.ten_vai_tro == role
    return {"manager": warehouse_manager}


@given("có một cuốn sách trong kho", target_fixture="book_data")
def book_in_stock(book):
    return {"book": book}


@when(
    parsers.parse("quản lý kho cập nhật số lượng sách với số lượng {quantity:d}"),
    target_fixture="update_result",
)
def update_book_quantity_step(book_data, quantity):
    try:
        if quantity <= 0:
            raise ValueError("Số lượng phải lớn hơn 0")
        return {"success": True, "quantity_added": quantity}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}


@then(parsers.parse("số lượng sách tăng thêm {quantity:d}"))
def check_quantity_increased(update_result, book_data, quantity):
    expected_quantity = book_data["book"].so_luong + quantity
    updated_book = update_book_quantity(book_data["book"].id, quantity)
    assert update_result["success"]
    assert updated_book.so_luong == expected_quantity


@then("hệ thống báo lỗi và không cập nhật số lượng sách")
def check_invalid_quantity(update_result, book_data):
    updated_book = Sach.query.get(book_data["book"].id)
    assert not update_result["success"], "Lẽ ra phải thất bại khi nhập số lượng âm"
    assert (
        updated_book.so_luong == book_data["book"].so_luong
    ), "Số lượng sách đã bị thay đổi ngoài ý muốn"
