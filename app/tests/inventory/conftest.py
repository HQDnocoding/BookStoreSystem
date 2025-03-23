import pytest

from app import app, db
from app.dao import (add_so_luong, create_chitietphieunhapsach,
                     create_phieunhapsach, create_sach, create_user)
from app.models import (ChiTietPhieuNhapSach, PhieuNhapSach, QuyDinh, Sach,
                        User, VaiTro)


@pytest.fixture
def app_context():
    """Fixture để tạo ứng dụng Flask và context cơ sở dữ liệu."""
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture
def warehouse_manager(app_context):
    """Fixture tạo một quản lý kho."""
    vai_tro = VaiTro(ten_vai_tro="QUANLYKHO")
    db.session.add(vai_tro)
    db.session.commit()
    user = create_user(
        ho="Tran",
        ten="Van D",
        username="warehouse1",
        password="123",
        avatar=None,
        vai_tro="QUANLYKHO",
    )
    return user


@pytest.fixture
def book(app_context):
    """Fixture tạo một cuốn sách."""
    sach = create_sach(ten_sach="Book X", don_gia=200000, the_loai_id=1, tac_gia_id=1)
    sach.so_luong = 10  # Số lượng tồn kho ban đầu
    db.session.commit()
    return sach


@pytest.fixture
def inventory_rules(app_context):
    """Fixture tạo quy định nhập sách."""
    quy_dinh = QuyDinh(
        SL_NHAP_MIN=5,  # Số lượng tối thiểu khi nhập
        SL_MIN_TO_NHAP=20,  # Số lượng tồn tối thiểu trước khi nhập
        OUT_OF_TIME_TO_PAY=48,  # Không liên quan đến nhập sách, nhưng để đồng bộ
    )
    db.session.add(quy_dinh)
    db.session.commit()
    return quy_dinh
