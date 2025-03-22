import pytest
from flask import url_for

from app import app, db
from app.dao import (create_chitietdonhang, create_donhang,
                     create_thongtinnhanhang)
from app.utils import cart_stats


# Test Naming and Test Discovery
# Tên test rõ ràng, bắt đầu bằng "test_" để Pytest tự động phát hiện
def test_add_to_cart_success(customer_user, book):
    """Kiểm tra thêm sách vào giỏ hàng thành công (Unit Test)."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = customer_user.id  # Giả lập đăng nhập
            sess[app.config["CART_KEY"]] = {}

        # Thêm sách vào giỏ hàng
        response = client.post(
            "/api/cart",
            json={
                "id": book.id,
                "ten_sach": book.ten_sach,
                "don_gia": book.don_gia,
                "so_luong": 2,
                "so_luong_con_lai": book.so_luong,
            },
        )

        # Assertions
        assert response.status_code == 200
        assert response.json["total_quantity"] == 2
        assert response.json["total_amount"] == book.don_gia * 2


# Parametrized Testing
@pytest.mark.parametrize(
    "quantity, expected_status, expected_alert",
    [
        (5, 200, None),  # Số lượng hợp lệ
        (15, 200, "KHÔNG đủ sách để mua"),  # Vượt quá tồn kho
        (0, 200, None),  # Số lượng không hợp lệ nhưng không có kiểm tra cụ thể
    ],
)
def test_add_to_cart_with_different_quantities(
    customer_user, book, quantity, expected_status, expected_alert
):
    """Kiểm tra thêm sách với các số lượng khác nhau (Unit Test)."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = customer_user.id
            sess[app.config["CART_KEY"]] = {}

        response = client.post(
            "/api/cart",
            json={
                "id": book.id,
                "ten_sach": book.ten_sach,
                "don_gia": book.don_gia,
                "so_luong": quantity,
                "so_luong_con_lai": book.so_luong,
            },
        )

        assert response.status_code == expected_status
        if expected_alert:
            assert response.json.get("alert") == expected_alert
        else:
            assert "alert" not in response.json


# Skipping Tests and Markers
@pytest.mark.skipif(
    app.config.get("ENV") == "production",
    reason="Không chạy trong môi trường production",
)
def test_create_order_integration(customer_user, book, payment_method, order_status):
    """Kiểm tra toàn bộ luồng đặt sách (Integration Test)."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = customer_user.id
            sess[app.config["CART_KEY"]] = {
                str(book.id): {
                    "id": book.id,
                    "ten_sach": book.ten_sach,
                    "don_gia": book.don_gia,
                    "so_luong": 1,
                    "so_luong_con_lai": book.so_luong,
                }
            }

        # Gửi yêu cầu tạo đơn hàng
        response = client.post(
            "/process_payment",
            data={
                "phone": "123456789",
                "address": "Test Address",
                "switch_isThanhToanSau": "false",
            },
        )

        # Assertions
        assert response.status_code == 302  # Chuyển hướng sau khi tạo đơn
        order = DonHang.query.filter_by(khach_hang_id=customer_user.id).first()
        assert order is not None
        assert order.phuong_thuc_id == payment_method.id
        assert order.trang_thai_id == order_status.id
        assert ChiTietDonHang.query.filter_by(don_hang_id=order.id).count() == 1


# Different Types of Assertions
def test_cart_stats_with_empty_cart():
    """Kiểm tra tính toán giỏ hàng trống (Unit Test)."""
    cart = {}
    result = cart_stats(cart)

    assert isinstance(result, dict)  # Kiểm tra kiểu dữ liệu
    assert result["total_quantity"] == 0  # Kiểm tra giá trị bằng
    assert result["total_amount"] == 0
    assert len(result["cart"]) == 0  # Kiểm tra độ dài
    assert "alert" not in result  # Kiểm tra không tồn tại key


# Passing Command-line Args in Pytest
def test_order_with_custom_payment_method(customer_user, book, pytestconfig):
    """Kiểm tra tạo đơn hàng với phương thức thanh toán từ command-line (Integration Test)."""
    payment_method_name = pytestconfig.getoption(
        "--payment-method", default="ONLINE_PAY"
    )
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = customer_user.id
            sess[app.config["CART_KEY"]] = {
                str(book.id): {
                    "id": book.id,
                    "ten_sach": book.ten_sach,
                    "don_gia": book.don_gia,
                    "so_luong": 1,
                    "so_luong_con_lai": book.so_luong,
                }
            }

        response = client.post(
            "/process_payment",
            data={
                "phone": "123456789",
                "address": "Test Address",
                "switch_isThanhToanSau": "false",
            },
        )

        order = DonHang.query.filter_by(khach_hang_id=customer_user.id).first()
        assert (
            order.phuong_thuc_id
            == PhuongThucThanhToan.query.filter_by(ten_phuong_thuc=payment_method_name)
            .first()
            .id
        )


# Pytest-BDD (Behavior-Driven Development)
from pytest_bdd import given, scenarios, then, when

scenarios("ordering.feature")


@given("khách hàng đã đăng nhập")
def customer_logged_in(customer_user):
    return {"user": customer_user}


@given("có một cuốn sách trong kho")
def book_in_stock(book):
    return {"book": book}


@when("khách hàng thêm sách vào giỏ hàng")
def add_book_to_cart(customer_logged_in, book_in_stock, client):
    with client.session_transaction() as sess:
        sess["user_id"] = customer_logged_in["user"].id
        sess[app.config["CART_KEY"]] = {}
    response = client.post(
        "/api/cart",
        json={
            "id": book_in_stock["book"].id,
            "ten_sach": book_in_stock["book"].ten_sach,
            "don_gia": book_in_stock["book"].don_gia,
            "so_luong": 1,
            "so_luong_con_lai": book_in_stock["book"].so_luong,
        },
    )
    return {"response": response}


@then("giỏ hàng phải chứa sách vừa thêm")
def cart_contains_book(add_book_to_cart):
    assert add_book_to_cart["response"].status_code == 200
    assert add_book_to_cart["response"].json["total_quantity"] == 1
