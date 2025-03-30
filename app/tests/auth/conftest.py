import pytest

from app import app, db
from app.dao import create_user
from app.tests.utils.database import setup_database


# Fixtures và bước dữ liệu nền
@pytest.fixture
def auth_context():
    """Tạo context cho quá trình xác thực"""
    return {"credentials": {}, "response": None, "error": None}


@pytest.fixture
def client():
    """Fixture để tạo client Flask test."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def app_context():
    """Fixture để tạo ứng dụng Flask và context cơ sở dữ liệu."""
    with app.app_context():
        setup_database()
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_users(app_context):
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
