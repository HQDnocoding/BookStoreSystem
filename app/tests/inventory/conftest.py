from datetime import datetime

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app import app, db
from app.dao import create_sach, create_user
from app.models import QuyDinh, VaiTro
from app.tests.utils.database import setup_database


# Cấu hình fixture tái sử dụng
@pytest.fixture
def app_context():
    """Fixture để tạo ứng dụng Flask và context cơ sở dữ liệu."""
    with app.app_context():
        try:
            setup_database()
            yield
        except Exception as e:
            pytest.fail(f"Error in app_context setup: {str(e)}")
        finally:
            db.session.remove()
            db.drop_all()


@pytest.fixture
def client():
    """Fixture để tạo client Flask test."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def warehouse_manager(app_context, request):
    """Fixture tạo một quản lý kho."""
    params = getattr(
        request,
        "param",
        {
            "ho": "Tran",
            "ten": "Van D",
            "username": "warehouse1",
            "password": "123",
            "vai_tro": "QUANLYKHO",
            "avatar": None,
        },
    )
    try:
        vai_tro = VaiTro.query.filter_by(ten_vai_tro=params["vai_tro"]).first()
        if not vai_tro:
            vai_tro = VaiTro(ten_vai_tro=params["vai_tro"])
            db.session.add(vai_tro)
            db.session.commit()
        user = create_user(**params)
        return user
    except SQLAlchemyError as e:
        db.session.rollback()
        pytest.fail(f"Failed to create warehouse_manager: {str(e)}")


@pytest.fixture
def book(app_context, request):
    params = getattr(
        request,
        "param",
        {
            "ten_sach": "Book X",
            "don_gia": 200000,
            "so_luong": 10,
            "the_loai_id": 1,
            "tac_gia_id": 1,
        },
    )
    try:
        sach = create_sach(
            ten_sach=params["ten_sach"],
            don_gia=params["don_gia"],
            the_loai_id=params["the_loai_id"],
            tac_gia_id=params["tac_gia_id"],
            so_luong=params["so_luong"],
        )
        db.session.commit()
        return sach
    except SQLAlchemyError as e:
        db.session.rollback()
        pytest.fail(f"Failed to create book: {str(e)}")


@pytest.fixture
def inventory_rules(app_context):
    """Fixture tạo quy định nhập sách."""
    try:
        # Xóa các bản ghi hiện có để tránh xung đột từ setup_database()
        QuyDinh.query.delete()
        # Dictionary để lưu trữ các quy định
        rules = {
            "SL_NHAP_MIN": QuyDinh(
                ten_quy_dinh="SL_NHAP_MIN",
                noi_dung="Số lượng tối thiểu khi nhập",
                gia_tri=5,
            ),
            "SL_MIN_TO_NHAP": QuyDinh(
                ten_quy_dinh="SL_MIN_TO_NHAP",
                noi_dung="Số lượng tồn tối thiểu trước khi nhập",
                gia_tri=20,
            ),
            "OUT_OF_TIME_TO_PAY": QuyDinh(
                ten_quy_dinh="OUT_OF_TIME_TO_PAY",
                noi_dung="Thời gian quá hạn thanh toán",
                gia_tri=48,
            ),
        }
        db.session.add_all(rules.values())
        db.session.commit()

        # Trả về object với các thuộc tính tương ứng
        class InventoryRules:
            def __init__(self, rules_dict):
                self.SL_NHAP_MIN = rules_dict["SL_NHAP_MIN"].gia_tri
                self.SL_MIN_TO_NHAP = rules_dict["SL_MIN_TO_NHAP"].gia_tri
                self.OUT_OF_TIME_TO_PAY = rules_dict["OUT_OF_TIME_TO_PAY"].gia_tri
                self.rules = rules_dict  # Lưu bản ghi gốc nếu cần

        return InventoryRules(rules)
    except SQLAlchemyError as e:
        db.session.rollback()
        pytest.fail(f"Failed to create or fetch inventory_rules: {str(e)}")
