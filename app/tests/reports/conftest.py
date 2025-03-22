import pytest

from app import app, db
from app.dao import (create_chitietdonhang, create_donhang, create_sach,
                     create_user)
from app.models import (ChiTietDonHang, DonHang, PhuongThucThanhToan, Sach,
                        TheLoai, TrangThaiDonHang, User, VaiTro)


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
        ho="Nguyen",
        ten="Van F",
        username="admin2",
        password="123",
        avatar=None,
        vai_tro="QUANLY",
    )
    return user


@pytest.fixture
def sales_data(app_context):
    """Fixture tạo dữ liệu bán hàng cho báo cáo."""
    the_loai = TheLoai(ten_the_loai="Fiction")
    customer = create_user(
        ho="Le",
        ten="Van G",
        username="customer3",
        password="123",
        avatar=None,
        vai_tro="KHACHHANG",
    )
    pt = PhuongThucThanhToan(ten_phuong_thuc="OFFLINE_PAY")
    tt = TrangThaiDonHang(ten_trang_thai="PAID")
    db.session.add_all([the_loai, pt, tt])
    db.session.commit()

    sach1 = create_sach(
        ten_sach="Book 1", don_gia=100000, the_loai_id=the_loai.id, tac_gia_id=1
    )
    sach2 = create_sach(
        ten_sach="Book 2", don_gia=150000, the_loai_id=the_loai.id, tac_gia_id=1
    )
    order = create_donhang(
        ngay_tao_don="2025-03-01",
        phuong_thuc_id=pt.id,
        trang_thai_id=tt.id,
        khach_hang_id=customer.id,
    )
    create_chitietdonhang(
        don_hang_id=order.id, sach_id=sach1.id, so_luong=2, tong_tien=200000
    )
    create_chitietdonhang(
        don_hang_id=order.id, sach_id=sach2.id, so_luong=1, tong_tien=150000
    )
    db.session.commit()
    return {"order": order, "sach1": sach1, "sach2": sach2, "the_loai": the_loai}
