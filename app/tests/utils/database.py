import hashlib
import json
import os
from pathlib import Path

from app import PayingMethod, Role, Rule, Status, db
from app.models import (PhuongThucThanhToan, QuyDinh, Sach, TacGia, TheLoai,
                        TrangThaiDonHang, VaiTro)


def setup_database():
    db.drop_all()
    db.create_all()

    pt1 = PhuongThucThanhToan(ten_phuong_thuc=PayingMethod.ONLINE_PAY.value)
    pt2 = PhuongThucThanhToan(ten_phuong_thuc=PayingMethod.OFFLINE_PAY.value)
    db.session.add_all([pt1, pt2])

    tt1 = TrangThaiDonHang(ten_trang_thai=Status.PAID.value)
    tt2 = TrangThaiDonHang(ten_trang_thai=Status.WAITING.value)
    tt3 = TrangThaiDonHang(ten_trang_thai=Status.FAIL.value)
    db.session.add_all([tt1, tt2, tt3])

    r1 = VaiTro(ten_vai_tro=Role.QUANLY.value)
    r2 = VaiTro(ten_vai_tro=Role.QUAN_LY_KHO.value)
    r3 = VaiTro(ten_vai_tro=Role.NHAN_VIEN.value)
    r4 = VaiTro(ten_vai_tro=Role.KHACH_HANG.value)
    db.session.add_all([r1, r2, r3, r4])

    ten_qd1 = Rule.SL_NHAP_MIN.value
    ten_qd2 = Rule.SL_MIN_TO_NHAP.value
    ten_qd3 = Rule.OUT_OF_TIME_TO_PAY.value
    qd1 = QuyDinh(
        ten_quy_dinh=ten_qd1,
        noi_dung="Số lượng tối thiểu khi nhập sách",
        gia_tri=150,
    )
    qd2 = QuyDinh(
        ten_quy_dinh=ten_qd2,
        noi_dung="Số lượng tối thiểu của đầu sách để được nhập",
        gia_tri=300,
    )
    qd3 = QuyDinh(
        ten_quy_dinh=ten_qd3,
        noi_dung="Số giờ tối đa kể từ khi đặt hàng đến lúc thanh toán",
        gia_tri=48,
    )

    db.session.add_all([qd1, qd2, qd3])

    with open(is_path_directory("the_loai.json"), "r", encoding="utf-8") as f:
        the_loai_data = json.load(f)

    # Lặp qua từng mục trong dữ liệu the_loai_data và tạo đối tượng TheLoai
    for item in the_loai_data:
        the_loai = TheLoai(ten_the_loai=item["ten_the_loai"])
        db.session.add(the_loai)

    # Lưu tất cả các đối tượng vào cơ sở dữ liệu
    db.session.commit()

    with open(is_path_directory("tac_gia.json"), "r", encoding="utf-8") as f:
        tac_gia_data = json.load(f)

    # Lặp qua từng mục trong dữ liệu tac_gia_data và tạo đối tượng TacGia
    for item in tac_gia_data:
        tac_gia = TacGia(ten_tac_gia=item["ten_tac_gia"])
        db.session.add(tac_gia)

    # Lưu tất cả các đối tượng vào cơ sở dữ liệu
    db.session.commit()

    with open(is_path_directory("sach.json"), "r", encoding="utf-8") as f:
        sach_data = json.load(f)

    # Lặp qua từng mục trong dữ liệu sach_data và tạo đối tượng Sach
    for item in sach_data:
        sach = Sach(
            ten_sach=item["ten_sach"],
            don_gia=item["don_gia"],
            bia_sach=item["bia_sach"],
            noi_dung=item["noi_dung"],
            so_luong=item["so_luong"],
            nam_phat_hanh=item["nam_phat_hanh"],
            the_loai_id=item["the_loai_id"],
            tac_gia_id=item["tac_gia_id"],
        )
        db.session.add(sach)

    db.session.commit()


def is_path_directory(filename):
    # Lấy đường dẫn gốc của dự án
    project_root = Path(__file__).resolve().parents[2]
    # Tạo đường dẫn tuyệt đối đến file JSON
    json_path = os.path.join(project_root, "virtual_data", filename)
    return json_path
