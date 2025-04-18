import pytest
from sqlalchemy.exc import SQLAlchemyError

from app import app, db
from app.dao import auth_user, get_quy_dinh
from app.database import setup_database


@pytest.fixture
def app_context():
    """Fixture để tạo ứng dụng Flask và context cơ sở dữ liệu."""
    with app.app_context():
        setup_database()
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_client():
    """Fixture để tạo client Flask test."""
    with app.test_request_context(), app.test_client() as client:
        yield client


@pytest.fixture
def admin_user(app_context):
    """Fixture tạo một quản trị viên."""
    user = auth_user(username="admin1", password="123")
    return user


@pytest.fixture
def initial_rules(app_context):
    """Fixture tạo quy định ban đầu."""
    return {
        "SL_NHAP_MIN": get_quy_dinh(ten_quy_dinh="SL_NHAP_MIN"),
        "SL_MIN_TO_NHAP": get_quy_dinh(ten_quy_dinh="SL_MIN_TO_NHAP"),
        "OUT_OF_TIME_TO_PAY": get_quy_dinh(ten_quy_dinh="OUT_OF_TIME_TO_PAY"),
    }
