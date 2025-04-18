import pytest
from sqlalchemy.exc import OperationalError

from app import app, db


# Test Naming and Test Discovery => PASSED
def test_update_rules_success(test_client, admin_user, initial_rules):
    """Kiểm tra cập nhật quy định thành công (Unit Test)."""
    # Cập nhật quy định
    initial_rules["SL_NHAP_MIN"].gia_tri = 10
    initial_rules["SL_MIN_TO_NHAP"].gia_tri = 30
    initial_rules["OUT_OF_TIME_TO_PAY"].gia_tri = 72
    db.session.commit()

    # Assertions
    updated_rules = initial_rules
    assert updated_rules["SL_NHAP_MIN"].gia_tri == 10
    assert updated_rules["SL_MIN_TO_NHAP"].gia_tri == 30
    assert updated_rules["OUT_OF_TIME_TO_PAY"].gia_tri == 72


from sqlalchemy.exc import IntegrityError


# Parametrized Testing => PASSED
@pytest.mark.parametrize(
    "min_import, min_stock, timeout, expected_success",
    [
        (10, 30, 72, True),  # Hợp lệ
        (-5, 20, 48, False),  # SL_NHAP_MIN âm
        (5, -10, 48, False),  # SL_MIN_TO_NHAP âm
        (5, 20, -24, False),  # OUT_OF_TIME_TO_PAY âm
    ],
)
def test_update_rules_with_different_values(
    test_client,
    admin_user,
    initial_rules,
    min_import,
    min_stock,
    timeout,
    expected_success,
):
    """Kiểm tra cập nhật quy định với các giá trị khác nhau (Unit Test)."""
    try:
        initial_rules["SL_NHAP_MIN"].gia_tri = min_import
        initial_rules["SL_MIN_TO_NHAP"].gia_tri = min_stock
        initial_rules["OUT_OF_TIME_TO_PAY"].gia_tri = timeout
        db.session.commit()
        result = True
    except OperationalError:
        db.session.rollback()
        result = False

    # Kết quả mong đợi
    assert result == expected_success

    if expected_success:
        updated_rules = initial_rules
        assert updated_rules["SL_NHAP_MIN"].gia_tri == min_import
        assert updated_rules["SL_MIN_TO_NHAP"].gia_tri == min_stock
        assert updated_rules["OUT_OF_TIME_TO_PAY"].gia_tri == timeout


# Skipping Tests and Markers => SKIPPED
@pytest.mark.skipif(
    app.config.get("ENV") == "production",
    reason="Không chạy trong môi trường production",
)
def test_rules_management_integration(test_client, admin_user, initial_rules):
    """Kiểm tra toàn bộ luồng thay đổi quy định (Integration Test)."""
    # Cập nhật quy định
    initial_rules["SL_NHAP_MIN"].gia_tri = 15
    initial_rules["SL_MIN_TO_NHAP"].gia_tri = 25
    initial_rules["OUT_OF_TIME_TO_PAY"].gia_tri = 96
    db.session.commit()

    # Assertions
    updated_rules = initial_rules
    assert updated_rules.SL_NHAP_MIN == 15
    assert updated_rules.SL_MIN_TO_NHAP == 25
    assert updated_rules.OUT_OF_TIME_TO_PAY == 96


# Different Types of Assertions
def test_get_rules(test_client, admin_user, initial_rules):
    """Kiểm tra lấy thông tin quy định (Unit Test)."""
    rules = initial_rules

    # Assertions
    assert rules is not None  # Kiểm tra sự tồn tại
    assert isinstance(rules["SL_NHAP_MIN"].gia_tri, int)  # Kiểm tra kiểu dữ liệu
    assert rules["SL_NHAP_MIN"].gia_tri == 5  # Kiểm tra giá trị
    assert rules["SL_MIN_TO_NHAP"].gia_tri > 0  # Kiểm tra điều kiện logic


# Passing Command-line Args in Pytest
def test_update_rules_with_custom_timeout(admin_user, initial_rules, pytestconfig):
    """Kiểm tra cập nhật quy định với thời gian tối đa từ cmd (Unit Test)."""
    custom_timeout = int(pytestconfig.getoption("--timeout", default=48))
    initial_rules["OUT_OF_TIME_TO_PAY"] = custom_timeout
    db.session.commit()

    updated_rules = initial_rules
    assert updated_rules["OUT_OF_TIME_TO_PAY"] == custom_timeout


# Pytest-BDD
from pytest_bdd import given, scenarios, then, when

scenarios("./features/rules_management.feature")


@given("quản trị viên đã đăng nhập", target_fixture="admin_logged_in")
def admin_logged_in(admin_user):
    return {"admin": admin_user}


@given("có quy định hiện tại trong hệ thống", target_fixture="rules_exist")
def rules_exist(initial_rules):
    return {"rules": initial_rules}


@when("quản trị viên thay đổi quy định", target_fixture="change_rules")
def change_rules(admin_logged_in, rules_exist):
    rules_exist["rules"]["SL_NHAP_MIN"].gia_tri = 12
    rules_exist["rules"]["SL_MIN_TO_NHAP"].gia_tri = 35
    rules_exist["rules"]["OUT_OF_TIME_TO_PAY"].gia_tri = 60
    db.session.commit()
    return {"rules": rules_exist["rules"]}


@then("quy định được cập nhật trong hệ thống")
def rules_updated(change_rules):
    updated_rules = change_rules["rules"]
    assert updated_rules["SL_NHAP_MIN"].gia_tri == 12
    assert updated_rules["SL_MIN_TO_NHAP"].gia_tri == 35
    assert updated_rules["OUT_OF_TIME_TO_PAY"].gia_tri == 60
