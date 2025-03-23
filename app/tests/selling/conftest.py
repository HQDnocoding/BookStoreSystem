import pytest

from app import app, db
from app.dao import (create_chitietdonhang, create_donhang,
                     create_invoice_from_cart, create_sach, create_user)
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
def employee_user(app_context):
    """Fixture tạo một nhân viên."""
    vai_tro = VaiTro(ten_vai_tro="NHANVIEN")
    db.session.add(vai_tro)
    db.session.commit()
    user = create_user(
        ho="Le",
        ten="Van B",
        username="employee1",
        password="123",
        avatar=None,
        vai_tro="NHANVIEN",
    )
    return user


@pytest.fixture
def book(app_context):
    """Fixture tạo một cuốn sách."""
    sach = create_sach(ten_sach="Book A", don_gia=150000, the_loai_id=1, tac_gia_id=1)
    sach.so_luong = 5  # Số lượng tồn kho
    db.session.commit()
    return sach


@pytest.fixture
def customer_order(app_context, book):
    """Fixture tạo một đơn hàng đã đặt trước bởi khách hàng."""
    vai_tro = VaiTro(ten_vai_tro="KHACHHANG")
    db.session.add(vai_tro)
    db.session.commit()
    customer = create_user(
        ho="Nguyen",
        ten="Van C",
        username="customer2",
        password="123",
        avatar=None,
        vai_tro="KHACHHANG",
    )
    pt = PhuongThucThanhToan(ten_phuong_thuc="OFFLINE_PAY")
    tt = TrangThaiDonHang(ten_trang_thai="WAITING")
    db.session.add_all([pt, tt])
    db.session.commit()
    order = create_donhang(
        ngay_tao_don=None,
        phuong_thuc_id=pt.id,
        trang_thai_id=tt.id,
        khach_hang_id=customer.id,
    )
    create_chitietdonhang(
        don_hang_id=order.id, sach_id=book.id, so_luong=2, tong_tien=book.don_gia * 2
    )
    db.session.commit()
    return order
