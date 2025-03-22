import pytest

from app import app, db
from app.dao import (create_chitietdonhang, create_donhang, create_sach,
                     create_user)
from app.models import (ChiTietDonHang, DonHang, PhuongThucThanhToan, Sach,
                        TrangThaiDonHang, User, VaiTro)


@pytest.fixture
def app_context():
    """Fixture để tạo ứng dụng Flask và context cơ sở dữ liệu."""
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture
def customer_user(app_context):
    """Fixture tạo một khách hàng."""
    vai_tro = VaiTro(ten_vai_tro="KHACHHANG")
    db.session.add(vai_tro)
    db.session.commit()
    user = create_user(
        ho="Nguyen",
        ten="Van A",
        username="customer1",
        password="123",
        avatar=None,
        vai_tro="KHACHHANG",
    )
    return user


@pytest.fixture
def book(app_context):
    """Fixture tạo một cuốn sách."""
    sach = create_sach(ten_sach="Book 1", don_gia=100000, the_loai_id=1, tac_gia_id=1)
    sach.so_luong = 10  # Số lượng tồn kho
    db.session.commit()
    return sach


@pytest.fixture
def payment_method(app_context):
    """Fixture tạo phương thức thanh toán."""
    pt = PhuongThucThanhToan(ten_phuong_thuc="ONLINE_PAY")
    db.session.add(pt)
    db.session.commit()
    return pt


@pytest.fixture
def order_status(app_context):
    """Fixture tạo trạng thái đơn hàng."""
    tt = TrangThaiDonHang(ten_trang_thai="WAITING")
    db.session.add(tt)
    db.session.commit()
    return tt
