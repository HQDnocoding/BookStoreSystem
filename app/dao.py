from datetime import datetime
from xmlrpc.client import DateTime

from app import db, admin
import hashlib
from app.models import TheLoai, VaiTro, QuyDinh, TacGia, TrangThaiDonHang, PhuongThucThanhToan, User, HoaDonBanSach, \
    Sach, ChiTietDonHang, ChiTietHoaDon, SoLuongCuonConLai, PhieuNhapSach, ChiTietPhieuNhapSach, DonHang, \
    ThongTinNhanHang


def create_vaitro(ten_vai_tro):  # Da test
    new_vaitro = VaiTro(ten_vai_tro=ten_vai_tro)
    db.session.add(new_vaitro)
    db.session.commit()


def create_quydinh(ten_quy_dinh, noi_dung, gia_tri, is_active):  # Da test
    new_quydinh = QuyDinh(ten_quy_dinh=ten_quy_dinh, noi_dung=noi_dung, gia_tri=gia_tri, is_active=is_active)
    db.session.add(new_quydinh)
    db.session.commit()


def create_tacgia(ten_tac_gia):  # Da test
    new_tacgia = TacGia(ten_tac_gia=ten_tac_gia)
    db.session.add(new_tacgia)
    db.session.commit()


def create_theloai(ten_the_loai):  # Da test
    new_theloai = TheLoai(ten_the_loai=ten_the_loai)
    db.session.add(new_theloai)
    db.session.commit()


def create_trangthaidonhang(ten_trang_thai):  # Da test
    new_trangthaidonhang = TrangThaiDonHang(ten_trang_thai=ten_trang_thai)
    db.session.add(new_trangthaidonhang)
    db.session.commit()


def create_phuongthucthanhtoan(ten_phuong_thuc):  # Da test
    new_phuongthucthanhtoan = PhuongThucThanhToan(ten_phuong_thuc=ten_phuong_thuc)
    db.session.add(new_phuongthucthanhtoan)
    db.session.commit()


def create_user(ho, ten, username, password, avatar, vai_tro_id):  # Da test
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())  # Bâm mật khẩu
    new_user = User(ho=ho, ten=ten, username=username, password=password, avatar=avatar, vai_tro_id=vai_tro_id)
    db.session.add(new_user)
    db.session.commit()


def create_hoadonbansach(ngay_tao_hoa_don):  # Da test
    new_hoadonbansach = HoaDonBanSach(ngay_tao_hoa_don=ngay_tao_hoa_don)
    db.session.add(new_hoadonbansach)
    db.session.commit()


def create_sach(tenSach, donGia, the_loai_id, tac_gia_id):  # Da test
    new_sach = Sach(tenSach=tenSach, donGia=donGia, the_loai_id=the_loai_id, tac_gia_id=tac_gia_id)
    db.session.add(new_sach)
    db.session.commit()


def create_chitiethoadon(sach_id, hoa_don_id, so_luong, tong_tien):  # Da test
    new_chitiethoadon = ChiTietHoaDon(sach_id=sach_id, hoa_don_id=hoa_don_id, so_luong=so_luong, tong_tien=tong_tien)
    db.session.add(new_chitiethoadon)
    db.session.commit()


def create_soluongconlai(so_luong, sach_id):
    new_soluongconlai = SoLuongCuonConLai(so_luong=so_luong, sach_id=sach_id)
    db.session.add(new_soluongconlai)
    db.session.commit()


def create_phieunhapsach(quan_ly_kho_id):
    new_phieunhapsach = PhieuNhapSach(quan_ly_kho_id=quan_ly_kho_id)
    db.session.add(new_phieunhapsach)
    db.session.commit()


def create_chitietphieunhapsach(phieu_nhap_sach_id, sach_id, so_luong):
    new_chitietnhapsach = ChiTietPhieuNhapSach(phieu_nhap_sach_id=phieu_nhap_sach_id, sach_id=sach_id,
                                               so_luong=so_luong)
    db.session.add(new_chitietnhapsach)
    db.session.commit()


def create_donhang(ngay_tao_don, phuong_thuc_id, trang_thai_id, khach_hang_id):
    new_donhang = DonHang(ngay_tao_don=ngay_tao_don, phuong_thuc_id=phuong_thuc_id, trang_thai_id=trang_thai_id,
                          khach_hang_id=khach_hang_id)
    db.session.add(new_donhang)
    db.session.commit()


def create_thongtinnhanhang(dien_thoai_nhan_hang, dia_chi_nhan_hang):
    new_thongtinnhanhang = ThongTinNhanHang(dien_thoai_nhan_hang=dien_thoai_nhan_hang,
                                            dia_chi_nhan_hang=dia_chi_nhan_hang)
    db.session.add(new_thongtinnhanhang)
    db.session.commit()


def create_chitietdonhang(don_hang_id, sach_id, so_luong, tong_tien):
    new_chitietdonhang = ChiTietDonHang(don_hang_id=don_hang_id, sach_id=sach_id, so_luong=so_luong,
                                        tong_tien=tong_tien)
    db.session.add(new_chitietdonhang)
    db.session.commit()


def get_role_name_by_role_id(role_id):
    vai_tro = VaiTro.query.get(role_id)
    return vai_tro.ten_vai_tro


def get_user_by_id(user_id):
    return User.query.get(user_id)


def auth_user(username, password, roles):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    users = User.query.filter(User.username.__eq__(username.strip()),
                              User.password.__eq__(password.strip()))

    if roles:
        roleID = []
        for role in roles:
            role = VaiTro.query.filter(VaiTro.ten_vai_tro.__eq__(role.strip())).first()
            if role:
                roleID.append(role.id)
        if roleID:
            users = users.filter(User.vai_tro_id.in_(roleID))

    return users.first()
