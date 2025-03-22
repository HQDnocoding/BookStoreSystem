import pytest

from app import app, db
from app.dao import create_quydinh, get_quy_dinh


# Test Naming and Test Discovery
def test_update_rules_success(admin_user, initial_rules):
    """Kiểm tra cập nhật quy định thành công (Unit Test)."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = admin_user.id  # Giả lập đăng nhập quản trị viên

        # Cập nhật quy định
        with app.app_context():
            initial_rules.SL_NHAP_MIN = 10
            initial_rules.SL_MIN_TO_NHAP = 30
            initial_rules.OUT_OF_TIME_TO_PAY = 72
            db.session.commit()

        # Assertions
        updated_rules = get_quy_dinh()
        assert updated_rules.SL_NHAP_MIN == 10
        assert updated_rules.SL_MIN_TO_NHAP == 30
        assert updated_rules.OUT_OF_TIME_TO_PAY == 72


# Parametrized Testing
@pytest.mark.parametrize(
    "min_import, min_stock, timeout, expected_success",
    [
        (10, 30, 72, True),  # Giá trị hợp lệ
        (-5, 20, 48, False),  # SL_NHAP_MIN âm
        (5, -10, 48, False),  # SL_MIN_TO_NHAP âm
        (5, 20, -24, False),  # OUT_OF_TIME_TO_PAY âm
    ],
)
def test_update_rules_with_different_values(
    admin_user, initial_rules, min_import, min_stock, timeout, expected_success
):
    """Kiểm tra cập nhật quy định với các giá trị khác nhau (Unit Test)."""
    with app.app_context():
        try:
            initial_rules.SL_NHAP_MIN = min_import
            initial_rules.SL_MIN_TO_NHAP = min_stock
            initial_rules.OUT_OF_TIME_TO_PAY = timeout
            db.session.commit()
            result = True
        except ValueError:
            db.session.rollback()
            result = False

        # Assertions
        assert result == expected_success
        if expected_success:
            updated_rules = get_quy_dinh()
            assert updated_rules.SL_NHAP_MIN == min_import
            assert updated_rules.SL_MIN_TO_NHAP == min_stock
            assert updated_rules.OUT_OF_TIME_TO_PAY == timeout


# Skipping Tests and Markers
@pytest.mark.skipif(
    app.config.get("ENV") == "production",
    reason="Không chạy trong môi trường production",
)
def test_rules_management_integration(admin_user, initial_rules):
    """Kiểm tra toàn bộ luồng thay đổi quy định (Integration Test)."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = admin_user.id

        # Cập nhật quy định
        with app.app_context():
            initial_rules.SL_NHAP_MIN = 15
            initial_rules.SL_MIN_TO_NHAP = 25
            initial_rules.OUT_OF_TIME_TO_PAY = 96
            db.session.commit()

            # Kiểm tra lại bằng get_quy_dinh
            updated_rules = get_quy_dinh()

        # Assertions
        assert updated_rules.SL_NHAP_MIN == 15
        assert updated_rules.SL_MIN_TO_NHAP == 25
        assert updated_rules.OUT_OF_TIME_TO_PAY == 96


# Different Types of Assertions
def test_get_rules(admin_user, initial_rules):
    """Kiểm tra lấy thông tin quy định (Unit Test)."""
    with app.app_context():
        rules = get_quy_dinh()

        # Assertions
        assert rules is not None  # Kiểm tra sự tồn tại
        assert isinstance(rules.SL_NHAP_MIN, int)  # Kiểm tra kiểu dữ liệu
        assert rules.SL_NHAP_MIN == 5  # Kiểm tra giá trị
        assert rules.SL_MIN_TO_NHAP > 0  # Kiểm tra điều kiện logic


# Passing Command-line Args in Pytest
def test_update_rules_with_custom_timeout(admin_user, initial_rules, pytestconfig):
    """Kiểm tra cập nhật quy định với thời gian tối đa từ cmd (Unit Test)."""
    custom_timeout = int(pytestconfig.getoption("--timeout", default=48))
    with app.app_context():
        initial_rules.OUT_OF_TIME_TO_PAY = custom_timeout
        db.session.commit()

        updated_rules = get_quy_dinh()
        assert updated_rules.OUT_OF_TIME_TO_PAY == custom_timeout


# Pytest-BDD
from pytest_bdd import given, scenarios, then, when

scenarios("rules_management.feature")


@given("quản trị viên đã đăng nhập")
def admin_logged_in(admin_user):
    return {"admin": admin_user}


@given("có quy định hiện tại trong hệ thống")
def rules_exist(initial_rules):
    return {"rules": initial_rules}


@when("quản trị viên thay đổi quy định")
def change_rules(admin_logged_in, rules_exist):
    with app.app_context():
        rules_exist["rules"].SL_NHAP_MIN = 12
        rules_exist["rules"].SL_MIN_TO_NHAP = 35
        rules_exist["rules"].OUT_OF_TIME_TO_PAY = 60
        db.session.commit()
    return {"rules": rules_exist["rules"]}


@then("quy định được cập nhật trong hệ thống")
def rules_updated(change_rules):
    with app.app_context():
        updated_rules = get_quy_dinh()
        assert updated_rules.SL_NHAP_MIN == 12
        assert updated_rules.SL_MIN_TO_NHAP == 35
        assert updated_rules.OUT_OF_TIME_TO_PAY == 60
