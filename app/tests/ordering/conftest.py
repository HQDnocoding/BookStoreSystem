import pytest

from app import app, db
from app.dao import auth_user, get_sach_by_id
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
def setup_test_data(app_context):
    """Tạo dữ liệu dùng chung cho toàn bộ module test."""
    try:
        user = auth_user(username="customer1", password="123")
        sach = get_sach_by_id(sach_id=1)

        return {
            "user": user,
            "book": sach,
            "payment_method": "OFFLINE_PAY",
            "order_status": "WAITING",
        }
    except Exception as e:
        pytest.fail(f"Không thể tạo dữ liệu test: {str(e)}")


@pytest.fixture
def customer_user(test_client, setup_test_data):
    return setup_test_data["user"]


@pytest.fixture
def book(test_client, setup_test_data):
    return setup_test_data["book"]


@pytest.fixture
def payment_method(test_client, setup_test_data):
    return setup_test_data["payment_method"]


@pytest.fixture
def order_status(test_client, setup_test_data):
    return setup_test_data["order_status"]
