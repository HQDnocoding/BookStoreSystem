from datetime import datetime

import pytest
import requests
from flask import session
from flask_login import current_user, login_user, logout_user

from app import PayingMethod, app, db
from app.models import (ChiTietDonHang, DonHang, PhuongThucThanhToan, Sach,
                        ThongTinNhanHang, User)
from app.utils import add_to_cart, cart_stats, process_offline_payment

BASE_URL = "http://127.0.0.1:5001"
headers = {"Content-Type": "application/json"}


# Test Naming and Test Discovery => PASSED
def test_add_to_cart_success(test_client, customer_user, book):
    """Kiểm tra thêm sách vào giỏ hàng thành công (Unit Test)."""
    url = f"{BASE_URL}/api/cart"
    payload = {
        "id": book.id,
        "ten_sach": book.ten_sach,
        "don_gia": book.don_gia,
        "so_luong": 2,
        "so_luong_con_lai": book.so_luong,
        "bia_sach": book.bia_sach,
    }

    response = requests.post(url, headers=headers, json=payload)
    try:
        data = response.json()
    except ValueError:
        pytest.fail("Phản hồi không phải JSON hợp lệ.")

    # Kiểm tra mã trạng thái HTTP từ đối tượng Response
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"

    assert data["total_quantity"] == 2
    assert data["total_amount"] == book.don_gia * 2
    assert "cart" in data


# Test Naming and Test Discovery => PASSED
def test_add_to_cart_exceeds_quantity(test_client, book):
    url = f"{BASE_URL}/api/cart"
    payload = {
        "id": book.id,
        "ten_sach": book.ten_sach,
        "don_gia": book.don_gia,
        "so_luong": 20,
        "so_luong_con_lai": book.so_luong,
        "bia_sach": book.bia_sach,
    }

    response = requests.post(url, headers=headers, json=payload)
    try:
        data = response.json()
    except ValueError:
        pytest.fail("Phản hồi không phải JSON hợp lệ.")

    # Kiểm tra mã trạng thái HTTP từ đối tượng Response
    assert response.status_code == 409
    assert response.headers["Content-Type"] == "application/json"

    assert "alert" in data
    assert data["alert"] == "Đã HẾT sách hoặc không đủ số lượng trong kho"


# Parametrized Testing => PASSED
@pytest.mark.parametrize(
    "quantity, expected_status, expected_alert",
    [
        (5, 200, None),  # Số lượng hợp lệ
        (15, 409, "Đã HẾT sách hoặc không đủ số lượng trong kho"),  # Vượt quá tồn kho
        (0, 400, "Số lượng không hợp lệ"),  # Số lượng không hợp lệ
        (-1, 400, "Số lượng không hợp lệ"),  # Số lượng âm
    ],
)
def test_add_to_cart_with_different_quantities(
    customer_user, book, test_client, quantity, expected_status, expected_alert
):
    """Kiểm tra thêm sách với các số lượng khác nhau."""
    url = f"{BASE_URL}/api/cart"
    payload = {
        "id": book.id,
        "ten_sach": book.ten_sach,
        "don_gia": book.don_gia,
        "so_luong": quantity,
        "so_luong_con_lai": book.so_luong,
        "bia_sach": book.bia_sach,
    }

    response = requests.post(url, headers=headers, json=payload)
    try:
        data = response.json()
    except ValueError:
        pytest.fail("Phản hồi không phải JSON hợp lệ.")

    assert response.status_code == expected_status
    if expected_alert:
        assert data["alert"] == expected_alert
    else:
        assert "alert" not in data


# Skipping Tests and Markers => SKIPPED
@pytest.mark.skipif(
    app.config.get("ENV") == "production",
    reason="Login Required không hoạt động bên trong request context. => FAILED",
)
def test_create_order_integration(
    customer_user, book, payment_method, order_status, test_client
):
    """Kiểm tra toàn bộ luồng đặt sách."""
    # 1. Giả lập login bằng cách can thiệp trực tiếp session
    login_user(customer_user)

    # 2. Thêm vào giỏ hàng
    response = requests.post(
        f"{BASE_URL}/api/cart",
        headers=headers,
        json={
            "id": book.id,
            "ten_sach": book.ten_sach,
            "don_gia": book.don_gia,
            "so_luong": 2,
            "so_luong_con_lai": book.so_luong,
            "bia_sach": book.bia_sach,
        },
    )
    assert response.status_code == 200

    # 3. Gửi request thanh toán offline => FAILED
    url = f"{BASE_URL}/payment_offline_done"
    response = requests.get(
        url,
        headers=headers,
        json={
            "phone": "123456789",
        },
    )

    # 4. Kiểm tra response
    assert response.status_code == 302

    # 5. Kiểm tra đơn hàng
    order = DonHang.query.filter_by(khach_hang_id=customer_user.id).first()
    assert order is not None
    assert order.phuong_thuc_id == payment_method.id
    assert order.trang_thai_id == order_status.id
    assert ChiTietDonHang.query.filter_by(don_hang_id=order.id).count() == 1


# Different Types of Assertions => PASSED
def test_cart_stats_with_empty_cart():
    """Kiểm tra tính toán giỏ hàng trống."""
    cart = {}
    result = cart_stats(cart)

    assert isinstance(result, dict)
    assert result["total_quantity"] == 0
    assert result["total_amount"] == 0
    assert len(result["cart"]) == 0
    assert "alert" not in result


# Passing Command-line Args in Pytest => PASSED
def test_order_with_custom_payment_method(
    customer_user, book, test_client, pytestconfig, payment_method, order_status
):
    """Kiểm tra tạo đơn hàng với phương thức thanh toán từ command-line."""
    # Đăng nhập user để current_user hoạt động đúng
    payment_method_name = pytestconfig.getoption(
        "--payment-method", default="OFFLINE_PAY"
    ).upper()

    login_user(customer_user)
    # Giả lập cart
    cart_items = {
        str(book.id): {
            "id": book.id,
            "ten_sach": book.ten_sach,
            "don_gia": book.don_gia,
            "so_luong": 2,
            "so_luong_con_lai": book.so_luong,
        }
    }

    # Gọi hàm xử lý đơn
    if payment_method_name == payment_method:
        order_id = process_offline_payment(cart_items, phone="0123456789")
    else:
        pytest.skip(f"Phương thức chưa hỗ trợ: {payment_method_name}")

    # Kiểm tra đơn hàng
    order = DonHang.query.get(order_id)
    assert order is not None
    assert order.khach_hang_id == customer_user.id

    # Kiểm tra phương thức thanh toán
    payment = PhuongThucThanhToan.query.get(order.phuong_thuc_id)
    assert payment.ten_phuong_thuc == payment_method_name

    # Kiểm tra chi tiết đơn hàng
    details = ChiTietDonHang.query.filter_by(don_hang_id=order.id).first()
    assert details is not None
    assert details.sach_id == book.id
    assert details.so_luong == 2
    assert details.tong_tien == book.don_gia * 2

    # Kiểm tra thông tin nhận hàng
    shipping_info = ThongTinNhanHang.query.get(order.id)
    assert shipping_info.dien_thoai_nhan_hang == "0123456789"


def test_process_offline_payment_empty_cart():
    with pytest.raises(ValueError, match="Giỏ hàng trống"):
        process_offline_payment({}, phone="0123456789")


# Pytest-BDD để kiểm thử chức năng giỏ hàng
from pytest_bdd import given, parsers, scenarios, then, when

# Tải tất cả các kịch bản từ tệp tính năng
# scenarios("./features/ordering.feature")
