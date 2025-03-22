import pytest

from app import app, db
from app.dao import create_quydinh, create_user, get_quy_dinh
from app.models import QuyDinh, User, VaiTro


@pytest.fixture
def app_context():
    """Fixture để tạo ứng dụng Flask và context cơ sở dữ liệu."""
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture
def admin_user(app_context):
    """Fixture tạo một quản trị viên."""
    vai_tro = VaiTro(ten_vai_tro="QUANLY")
    db.session.add(vai_tro)
    db.session.commit()
    user = create_user(
        ho="Hoang",
        ten="Van H",
        username="admin3",
        password="123",
        avatar=None,
        vai_tro="QUANLY",
    )
    return user


@pytest.fixture
def initial_rules(app_context):
    """Fixture tạo quy định ban đầu."""
    quy_dinh = QuyDinh(
        SL_NHAP_MIN=5,  # Số lượng tối thiểu khi nhập
        SL_MIN_TO_NHAP=20,  # Số lượng tồn tối thiểu trước khi nhập
        OUT_OF_TIME_TO_PAY=48,  # Thời gian tối đa để thanh toán
    )
    db.session.add(quy_dinh)
    db.session.commit()
    return quy_dinh
