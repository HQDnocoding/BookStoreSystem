from datetime import datetime

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app import app, db
from app.dao import (auth_user, create_sach, create_user, get_quy_dinh,
                     get_sach_by_id)
from app.database import setup_database
from app.models import QuyDinh, VaiTro


# Cấu hình fixture tái sử dụng
@pytest.fixture
def app_context():
    """Fixture để tạo ứng dụng Flask và context cơ sở dữ liệu."""
    with app.app_context():
        setup_database()
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client():
    """Fixture để tạo client Flask test."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def warehouse_manager(app_context):
    """Fixture tạo một quản lý kho."""
    user = auth_user(username="warehouse1", password="123")
    return user


@pytest.fixture
def book(app_context):
    book = get_sach_by_id(sach_id=1)
    return book


@pytest.fixture
def inventory_rules(app_context):
    """Fixture tạo quy định nhập sách."""
    try:
        # Dictionary để lưu trữ các quy định
        rules = {
            "SL_NHAP_MIN": get_quy_dinh("SL_NHAP_MIN"),
            "SL_MIN_TO_NHAP": get_quy_dinh("SL_MIN_TO_NHAP"),
            "OUT_OF_TIME_TO_PAY": get_quy_dinh("OUT_OF_TIME_TO_PAY"),
        }

        # Trả về object với các thuộc tính tương ứng
        class InventoryRules:
            def __init__(self, rules_dict):
                self.SL_NHAP_MIN = rules_dict["SL_NHAP_MIN"].gia_tri
                self.SL_MIN_TO_NHAP = rules_dict["SL_MIN_TO_NHAP"].gia_tri
                self.OUT_OF_TIME_TO_PAY = rules_dict["OUT_OF_TIME_TO_PAY"].gia_tri

        return InventoryRules(rules)
    except SQLAlchemyError as e:
        db.session.rollback()
        pytest.fail(f"Không tạo hoặc lấy inventory_rules được: {str(e)}")
