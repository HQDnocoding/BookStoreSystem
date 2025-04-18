import os

import pytest

from app import app, db
from app.dao import (auth_user, create_chitietdonhang, create_donhang,
                     get_phuong_thuc_by_id, get_sach_by_id, get_the_loai_by_id,
                     get_trang_thai_by_id)
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
def sales_data(app_context):
    """Fixture tạo dữ liệu bán hàng cho báo cáo."""
    the_loai = get_the_loai_by_id(id=6)
    customer = auth_user(
        username="customer1",
        password="123",
    )
    pt = get_phuong_thuc_by_id(phuong_thuc_id=2)
    tt = get_trang_thai_by_id(trang_thai_id=1)

    sach1 = get_sach_by_id(3)
    sach2 = get_sach_by_id(4)
    sach3 = get_sach_by_id(10)

    order = create_donhang(
        ngay_tao_don="2025-03-01",
        phuong_thuc_id=pt.id,
        trang_thai_id=tt.id,
        khach_hang_id=customer.id,
    )
    create_chitietdonhang(
        don_hang_id=order.id, sach_id=sach1.id, so_luong=2, tong_tien=(50000.0 * 2)
    )
    create_chitietdonhang(
        don_hang_id=order.id, sach_id=sach2.id, so_luong=1, tong_tien=50000.0
    )
    create_chitietdonhang(
        don_hang_id=order.id, sach_id=sach3.id, so_luong=1, tong_tien=84000.0
    )
    return {"order": order, "sach1": sach1, "sach2": sach2, "the_loai": the_loai}


@pytest.fixture
def output_dir():
    """Fixture tạo thư mục output cho báo cáo và dọn dẹp sau test."""
    output_dir = "test_statistics_form"
    os.makedirs(output_dir, exist_ok=True)
    yield output_dir
    # Dọn dẹp thư mục sau khi tất cả các test trong module hoàn thành
    # Lưu ý: Nếu bạn muốn dọn dẹp sau mỗi test, hãy di chuyển đoạn này vào teardown của test function
    # import shutil
    # shutil.rmtree(output_dir)
