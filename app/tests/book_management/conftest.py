import pytest

from app import app, db
from app.dao import auth_user, get_id_tac_gia, get_id_the_loai, get_sach_by_id
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
    with app.test_client() as client:
        yield client


@pytest.fixture
def admin_user(app_context):
    """Fixture tạo một quản trị viên."""
    user = auth_user(username="admin1", password="123")
    return user


@pytest.fixture
def book(app_context):
    """Fixture tạo một cuốn sách."""
    return get_sach_by_id(sach_id=1)


@pytest.fixture
def category_and_author(app_context):
    """Fixture tạo thể loại và tác giả."""
    the_loai = get_id_the_loai(name="Trinh thám")
    tac_gia = get_id_tac_gia(name="Aoyama Gosho")
    return {"the_loai": the_loai, "tac_gia": tac_gia}
