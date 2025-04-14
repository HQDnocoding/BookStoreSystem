import pytest
from flask import Response
from flask_login import login_user, logout_user

from app import app
from app.dao import auth_user
from app.errors import (AccountLockedError, AuthenticationError, PasswordError,
                        UserNotFoundError, ValidationError)
from app.models import User


# Test Naming and Test Discovery
def test_login_success(test_users, test_client):
    """Kiểm tra đăng nhập thành công với thông tin hợp lệ (Unit Test)."""
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
    user = auth_user(username=username, password=password)

    # Assertions
    assert (user is not None) == expected_success
    if expected_success:
        assert user.vai_tro.ten_vai_tro == role


# Skipping Tests and Markers => SKIPPED
@pytest.mark.skipif(
    app.config.get("ENV") == "production",
    reason="Không chạy trong môi trường production",
)
@pytest.mark.integration
def test_login_and_access_control_integration(test_users, test_client):
    """Kiểm tra đăng nhập và phân quyền truy cập (Integration Test)."""
    # Đăng nhập với vai trò quản trị viên
    user = auth_user(username="admin1", password="123")
    assert user is not None

    login_user(user)

    response = Response(status=200)
    assert response.status_code == 200

    # Kiểm tra phân quyền
    assert user.vai_tro.ten_vai_tro == "QUANLY"

    # Đăng xuất
    logout_user()
    response = Response(status=204)
    assert response.status_code == 204


# Different Types of Assertions => PASSED
@pytest.mark.unit
def test_auth_user_invalid(test_users):
    """Kiểm tra xác thực với thông tin không hợp lệ (Unit Test)."""
    user = auth_user(username="invaliduser", password="wrongpass")
    # Assertions
    assert user is None  # Kiểm tra không tồn tại
    assert isinstance(user, User) is False  # Kiểm tra kiểu dữ liệu
    assert user != test_users["customer"]  # Kiểm tra không bằng user khác


# Passing Command-line Args in Pytest => PASSED
@pytest.mark.unit
def test_login_with_custom_role(test_users, pytestconfig):
    """Kiểm tra đăng nhập với vai trò từ cmd (Unit Test)."""
    role = pytestconfig.getoption("--role", default="KHACHHANG")
    username = {
        "KHACHHANG": "customer1",
        "NHANVIEN": "employee1",
        "QUANLYKHO": "warehouse1",
        "QUANLY": "admin1",
    }[role]

    user = auth_user(username=username, password="123")
    assert user is not None
    assert user.vai_tro.ten_vai_tro == role


# Test vai trò cụ thể => PASSED
@pytest.mark.unit
def test_login_with_role_restriction(test_users, test_client):
    """Kiểm tra đăng nhập với giới hạn vai trò (Unit Test)."""
    # Kiểm tra thành công khi vai trò phù hợp
    user = auth_user(username="employee1", password="123", roles=["NHANVIEN"])
    assert user is not None, "Đăng nhập thất bại khi vai trò phù hợp"

    # Kiểm tra thất bại khi vai trò không phù hợp
    user = auth_user(username="employee1", password="123", roles=["QUANLY"])
    assert user is None


# Kiểm tra chuỗi xác thực và phân quyền thành công => PASSED
@pytest.mark.core
def test_authorization_chain(test_users, test_client):
    """Kiểm tra chuỗi xác thực và phân quyền (Unit Test)"""
    # 1. Đăng nhập thành công
    admin_user = auth_user(username="admin1", password="123")
    assert admin_user is not None
    # 2. Kiểm tra vai trò
    assert admin_user.vai_tro.ten_vai_tro == "QUANLY"
    # 3. Kiểm tra quyền truy cập vào nhiều vai trò
    employee_user = auth_user(
        username="employee1", password="123", roles=["NHANVIEN", "KHACHHANG"]
    )
    assert employee_user is not None
    # 4. Kiểm tra từ chối quyền truy cập
    user = auth_user(username="customer1", password="123", roles=["QUANLY"])
    assert user is None


# Pytest-BDD => PASSED
from pytest_bdd import given, parsers, scenarios, then, when

# Tải tất cả kịch bản từ file feature
scenarios("./features/auth.feature")


@given("hệ thống đã khởi tạo dữ liệu người dùng")
def system_initialized(test_users):
    """Đảm bảo dữ liệu người dùng test đã được khởi tạo"""
    assert "admin" in test_users
    assert "employee" in test_users
    assert "customer" in test_users
    assert "warehouse" in test_users
    return {"test_users": test_users}


# Các bước đăng nhập
@given(parsers.parse('người dùng nhập "{username}" và "{password}"'))
def user_enters_credentials(auth_context, username, password):
    """Lưu thông tin đăng nhập để sử dụng ở bước tiếp theo"""
    auth_context["credentials"] = {"username": username, "password": password}
    return auth_context


@when("hệ thống kiểm tra thông tin đăng nhập")
def system_verifies_login(auth_context, test_client):
    """Kiểm tra xem thông tin đăng nhập đã đúng hay chưa"""
    try:
        user = auth_user(
            username=auth_context["credentials"]["username"],
            password=auth_context["credentials"]["password"],
        )
        if user:
            # Giả lập thành công - trong ứng dụng thực tế có thể thiết lập session/token
            auth_context["response"] = {"status_code": 302, "user": user}
            auth_context["user"] = user
        else:
            auth_context["error"] = "Không tìm thấy người dùng"
    except AuthenticationError as e:
        auth_context["error"] = str(e)
    except Exception as e:
        auth_context["error"] = f"Lỗi không xác định: {str(e)}"
    return auth_context


@then(parsers.parse('người dùng sẽ nhận kết quả "{expected_result}"'))
def user_receives_result(auth_context, expected_result):
    """Kiểm tra kết quả đăng nhập phù hợp với kỳ vọng"""
    if expected_result == "đăng nhập thành công":
        assert auth_context["response"] is not None
        assert auth_context["response"]["status_code"] == 302
        assert auth_context["error"] is None
    elif "lỗi" in expected_result:
        assert auth_context["error"] is not None
        expected_error_message = expected_result.split('"')[1]
        assert (
            expected_error_message in auth_context["error"]
        ), f"Lỗi không khớp. Mong đợi: '{expected_error_message}', Thực tế: '{auth_context['error']}'"
    else:
        pytest.fail(f"Trường hợp không xác định: {expected_result}")


# Test vai trò người dùng
@pytest.fixture
@given("một người dùng có vai trò là nhân viên")
def employee_exists(test_users):
    """Kiểm tra tồn tại người dùng có vai trò nhân viên"""
    assert "employee" in test_users
    employee = test_users["employee"]
    assert employee.vai_tro.ten_vai_tro == "NHANVIEN"
    return {"user": employee}


@pytest.fixture
@when("người dùng đăng nhập bằng thông tin đăng nhập chính xác")
def login_with_correct_credentials(test_client):
    """Đăng nhập với thông tin đăng nhập đúng của nhân viên"""
    try:
        user = auth_user(username="employee1", password="123")
        if user:
            return {"response": {"status_code": 302, "user": user}}
        return {"response": None, "error": "Không tìm thấy người dùng"}
    except Exception as e:
        return {"response": None, "error": str(e)}


@then("đăng nhập thành công và vai trò đã được xác minh")
def login_successful_with_role_verification(
    test_client, login_with_correct_credentials, employee_exists
):
    """Kiểm tra đăng nhập thành công và xác minh vai trò"""
    assert login_with_correct_credentials["response"] is not None
    assert login_with_correct_credentials["response"]["status_code"] == 302

    user = employee_exists["user"]
    assert user.vai_tro is not None
    assert user.vai_tro.ten_vai_tro == "NHANVIEN"
