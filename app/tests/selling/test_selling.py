import pytest
from flask import session, url_for

from app import app, db
from app.dao import (create_hoa_don_from_don_hang, create_invoice_from_cart,
                     get_don_hang)
from app.utils import create_invoice_pdf


# Test Naming and Test Discovery
def test_create_invoice_from_cart_success(employee_user, book):
    """Kiểm tra tạo hóa đơn từ giỏ hàng thành công (Unit Test)."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = employee_user.id  # Giả lập đăng nhập nhân viên
            sess["cart_admin"] = {
                str(book.id): {
                    "id": book.id,
                    "ten_sach": book.ten_sach,
                    "don_gia": book.don_gia,
                    "so_luong": 1,
                }
            }

        # Giả lập gọi hàm tạo hóa đơn
        with app.app_context():
            order = create_invoice_from_cart()

        # Assertions
        assert order is not None
        assert order.nhan_vien_id == employee_user.id
        assert (
            order.phuong_thuc_id
            == PhuongThucThanhToan.query.filter_by(ten_phuong_thuc="OFFLINE_PAY")
            .first()
            .id
        )
        assert ChiTietDonHang.query.filter_by(don_hang_id=order.id).count() == 1
        updated_book = Sach.query.get(book.id)
        assert updated_book.so_luong == book.so_luong - 1  # Số lượng giảm đi 1


# Parametrized Testing
@pytest.mark.parametrize(
    "quantity, money_paid, expected_success",
    [
        (2, 300000, True),  # Đủ tiền, đủ sách
        (6, 900000, False),  # Không đủ sách (tồn kho chỉ có 5)
        (2, 200000, False),  # Không đủ tiền
    ],
)
def test_sell_book_with_different_conditions(
    employee_user, book, quantity, money_paid, expected_success
):
    """Kiểm tra bán sách với các điều kiện khác nhau (Unit Test)."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = employee_user.id
            sess["cart_admin"] = {
                str(book.id): {
                    "id": book.id,
                    "ten_sach": book.ten_sach,
                    "don_gia": book.don_gia,
                    "so_luong": quantity,
                }
            }

        # Giả lập bán sách
        with app.app_context():
            if money_paid >= (book.don_gia * quantity) and quantity <= book.so_luong:
                order = create_invoice_from_cart()
                result = order is not None
            else:
                try:
                    order = create_invoice_from_cart()
                    result = False  # Nếu không raise exception thì thất bại
                except ValueError:
                    result = (
                        True  # Nếu raise exception thì thành công (không đủ sách/tiền)
                    )

        assert result == expected_success


# Skipping Tests and Markers
@pytest.mark.skip(reason="Chưa có tuyến đường cụ thể cho bán hàng tại cửa hàng")
def test_sell_at_store(employee_user, book):
    """Kiểm tra bán sách tại cửa hàng (Integration Test - Bỏ qua do thiếu route)."""
    pass  # Nếu có tuyến đường /sell, sẽ triển khai sau


# Different Types of Assertions
def test_create_invoice_pdf(employee_user, book):
    """Kiểm tra tạo PDF hóa đơn bán sách (Unit Test)."""
    items = [
        {
            "ten_sach": book.ten_sach,
            "the_loai": "Test Genre",
            "so_luong": 1,
            "don_gia": book.don_gia,
        }
    ]
    with app.app_context():
        create_invoice_pdf(
            "Customer Name",
            "2025-03-18",
            items,
            employee_user.ten,
            output_filename="test_invoice.pdf",
        )

    # Assertions (giả định file được tạo, không kiểm tra nội dung chi tiết)
    import os

    assert os.path.exists("test_invoice.pdf")  # Kiểm tra file tồn tại
    assert os.path.getsize("test_invoice.pdf") > 0  # Kiểm tra file không rỗng
    os.remove("test_invoice.pdf")  # Dọn dẹp


# Passing Command-line Args in Pytest
def test_sell_preordered_with_timeout(employee_user, customer_order, pytestconfig):
    """Kiểm tra bán đơn hàng đã đặt trước với thời gian tối đa từ cmd (Integration Test)."""
    max_hours = int(
        pytestconfig.getoption("--max-hours", default=48)
    )  # Mặc định 48 giờ
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = employee_user.id

        # Giả lập đơn hàng đã tạo cách đây hơn max_hours
        with app.app_context():
            customer_order.ngay_tao_don = db.func.now() - db.func.interval(
                f"{max_hours + 1} hours"
            )
            db.session.commit()
            result, status = create_hoa_don_from_don_hang(customer_order.id)

        # Assertions
        assert status == 500  # Đơn hàng quá hạn
        assert "error" in result
        assert "Thời hạn trả quá" in result["error"]


# Pytest-BDD
from pytest_bdd import given, scenarios, then, when

scenarios("selling.feature")


@given("nhân viên đã đăng nhập")
def employee_logged_in(employee_user):
    return {"employee": employee_user}


@given("có một cuốn sách trong kho")
def book_in_stock(book):
    return {"book": book}


@when("nhân viên bán sách tại cửa hàng")
def sell_book_at_store(employee_logged_in, book_in_stock, client):
    with client.session_transaction() as sess:
        sess["user_id"] = employee_logged_in["employee"].id
        sess["cart_admin"] = {
            str(book_in_stock["book"].id): {
                "id": book_in_stock["book"].id,
                "ten_sach": book_in_stock["book"].ten_sach,
                "don_gia": book_in_stock["book"].don_gia,
                "so_luong": 1,
            }
        }
    with app.app_context():
        order = create_invoice_from_cart()
    return {"order": order}


@then("hóa đơn được tạo và số lượng sách giảm")
def invoice_created_and_stock_reduced(sell_book_at_store, book_in_stock):
    order = sell_book_at_store["order"]
    assert order is not None
    updated_book = Sach.query.get(book_in_stock["book"].id)
    assert updated_book.so_luong == book_in_stock["book"].so_luong - 1
