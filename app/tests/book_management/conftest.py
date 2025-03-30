import pytest

from app import app, db
from app.dao import create_sach, create_user, get_id_tac_gia, get_id_the_loai
from app.models import Sach, TacGia, TheLoai, User, VaiTro
from app.tests.utils.database import setup_database


@pytest.fixture
def app_context():
    """Fixture để tạo ứng dụng Flask và context cơ sở dữ liệu."""
    with app.app_context():
        setup_database()
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
        ho="Pham",
        ten="Van E",
        username="admin1",
        password="123",
        avatar=None,
        vai_tro="QUANLY",
    )
    return user


@pytest.fixture
def book(app_context):
    """Fixture tạo một cuốn sách."""
    the_loai = TheLoai(ten_the_loai="Fiction")
    tac_gia = TacGia(ten_tac_gia="Author A")
    db.session.add_all([the_loai, tac_gia])
    db.session.commit()
    sach = create_sach(
        ten_sach="Book Y",
        don_gia=250000,
        the_loai_id=the_loai.id,
        tac_gia_id=tac_gia.id,
        so_luong=8,  # Số lượng tồn kho ban đầu
    )
    db.session.commit()
    return sach


@pytest.fixture
def category_and_author(app_context):
    """Fixture tạo thể loại và tác giả."""
    the_loai = TheLoai(ten_the_loai="Non-Fiction")
    tac_gia = TacGia(ten_tac_gia="Author B")
    db.session.add_all([the_loai, tac_gia])
    db.session.commit()
    return {"the_loai": the_loai, "tac_gia": tac_gia}
