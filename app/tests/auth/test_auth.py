import pytest
from flask import url_for

from app import app, db
from app.dao import auth_user

# from app.decorators import login_required_admin, login_required_employee


# Test Naming and Test Discovery
def test_login_success(test_users):
    """Kiểm tra đăng nhập thành công với thông tin hợp lệ (Unit Test)."""
    with app.app_context():
        user = auth_user(username="customer1", password="123")

        # Assertions
        assert user is not None
        assert user.username == "customer1"
        assert user.vai_tro.ten_vai_tro == "KHACHHANG"


# Parametrized Testing
@pytest.mark.parametrize(
    "username, password, role, expected_success",
    [
        ("customer1", "123", "KHACHHANG", True),  # Đăng nhập đúng
        ("employee1", "123", "NHANVIEN", True),  # Đăng nhập đúng
        ("admin1", "wrongpass", "QUANLY", False),  # Sai mật khẩu
        ("nonexistent", "123", None, False),  # Tài khoản không tồn tại
    ],
)
def test_login_with_different_credentials(
    test_users, username, password, role, expected_success
):
    """Kiểm tra đăng nhập với các thông tin khác nhau (Unit Test)."""
    with app.app_context():
        user = auth_user(username=username, password=password)

        # Assertions
        assert (user is not None) == expected_success
        if expected_success:
            assert user.vai_tro.ten_vai_tro == role


# Skipping Tests and Markers => FAILED
@pytest.mark.skipif(
    app.config.get("ENV") != "testing",
    reason="Không chạy trong môi trường testing",
)
def test_login_and_access_control_integration(test_users):
    """Kiểm tra đăng nhập và phân quyền truy cập (Integration Test)."""
    with app.test_client() as client:
        # Đăng nhập với vai trò quản trị viên
        response = client.post("/login", data={"username": "admin1", "password": "123"})
        print(f"Login response: {response.status_code}")
        print(f"Response data: {response.data}")
        assert response.status_code == 302  # Chuyển hướng sau đăng nhập thành công

        # Truy cập route chỉ dành cho admin
        with client.session_transaction() as sess:
            sess["user_id"] = test_users["admin"].id
        response = client.get("/admin")  # Giả định route /admin yêu cầu quyền QUANLY
        assert response.status_code == 200

        # Đăng xuất
        client.get("/logout")
        response = client.get("/admin")
        print(f"Admin access after logout: {response.status_code}")
        assert response.status_code == 302  # Chuyển hướng vì chưa đăng nhập


# Different Types of Assertions => FAILED
def test_auth_user_invalid(test_users):
    """Kiểm tra xác thực với thông tin không hợp lệ (Unit Test)."""
    with app.app_context():
        user = auth_user(username="invaliduser", password="wrongpass")

        # Assertions
        assert user is None  # Kiểm tra không tồn tại
        assert isinstance(user, User) is False  # Kiểm tra kiểu dữ liệu
        assert user != test_users["customer"]  # Kiểm tra không bằng user khác


# Passing Command-line Args in Pytest
def test_login_with_custom_role(test_users, pytestconfig):
    """Kiểm tra đăng nhập với vai trò từ cmd (Unit Test)."""
    role = pytestconfig.getoption("--role", default="KHACHHANG")
    username = {
        "KHACHHANG": "customer1",
        "NHANVIEN": "employee1",
        "QUANLYKHO": "warehouse1",
        "QUANLY": "admin1",
    }[role]

    with app.app_context():
        user = auth_user(username=username, password="123")
        assert user.vai_tro.ten_vai_tro == role


# Pytest-BDD => FAILED
from pytest_bdd import given, scenarios, then, when

scenarios("auth.feature")


@given("có một người dùng với vai trò nhân viên")
def employee_exists(test_users):
    return {"user": test_users["employee"]}


@when("người dùng đăng nhập với thông tin đúng")
def login_with_correct_credentials(employee_exists, client):
    response = client.post("/login", data={"username": "employee1", "password": "123"})
    return {"response": response}


@then("đăng nhập thành công và vai trò được xác nhận")
def login_successful(login_with_correct_credentials, employee_exists):
    assert login_with_correct_credentials["response"].status_code == 302
    with app.app_context():
        user = User.query.get(employee_exists["user"].id)
        assert user.vai_tro.ten_vai_tro == "NHANVIEN"
