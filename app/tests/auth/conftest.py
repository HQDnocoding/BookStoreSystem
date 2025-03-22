import pytest

from app import app, db
from app.dao import auth_user, create_user
from app.models import User, VaiTro
from app.tests.utils.database import setup_database


@pytest.fixture
def app_context():
    """Fixture để tạo ứng dụng Flask và context cơ sở dữ liệu."""
    with app.app_context():
        setup_database()
        yield
        # db.session.remove()
        # db.drop_all()


@pytest.fixture
def roles(app_context):
    """Fixture tạo các vai trò."""
    roles = [
        VaiTro(ten_vai_tro="KHACHHANG"),
        VaiTro(ten_vai_tro="NHANVIEN"),
        VaiTro(ten_vai_tro="QUANLYKHO"),
        VaiTro(ten_vai_tro="QUANLY"),
    ]
    db.session.add_all(roles)
    db.session.commit()
    return roles


@pytest.fixture
def test_users(app_context, roles):
    """Fixture tạo các người dùng với vai trò khác nhau."""
    users = {
        "customer": create_user(
            ho="Nguyen",
            ten="Van A",
            username="customer1",
            password="123",
            avatar=None,
            vai_tro="KHACHHANG",
        ),
        "employee": create_user(
            ho="Le",
            ten="Van B",
            username="employee1",
            password="123",
            avatar=None,
            vai_tro="NHANVIEN",
        ),
        "warehouse": create_user(
            ho="Tran",
            ten="Van C",
            username="warehouse1",
            password="123",
            avatar=None,
            vai_tro="QUANLYKHO",
        ),
        "admin": create_user(
            ho="Pham",
            ten="Van D",
            username="admin1",
            password="123",
            avatar=None,
            vai_tro="QUANLY",
        ),
    }
    return users
