from datetime import datetime
from xmlrpc.client import DateTime

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.models import TheLoai, VaiTro, QuyDinh, TacGia, TrangThaiDonHang, PhuongThucThanhToan, User, HoaDonBanSach, \
    Sach, ChiTietDonHang, ChiTietHoaDon, SoLuongCuonConLai, PhieuNhapSach, ChiTietPhieuNhapSach, DonHang, \
    ThongTinNhanHang
from app import db, admin, app
import hashlib



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


def create_user(ho, ten, username, password, avatar, vai_tro):  # Da test
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())  # Bâm mật khẩu
    vt = VaiTro.query.filter(VaiTro.ten_vai_tro == vai_tro.strip()).with_entities(VaiTro.id).scalar()
    new_user = User(ho=ho, ten=ten, username=username, password=password, avatar=avatar, vai_tro_id=vt)
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


def auth_user(username, password, roles=None):
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



# lấy tổng doanh của từng tựa sách thu từ hóa đơn theo tháng, năm
def get_revenue_by_month_year(thang, nam):
    # Chuyển tháng, năm thành chuỗi tháng/năm
    start_date = datetime(nam, thang, 1)
    # Lấy ngày cuối tháng
    end_date = datetime(nam, thang + 1, 1) if thang < 12 else datetime(nam + 1, 1, 1)

    ket_qua = db.session.query(
        TheLoai.ten_the_loai,
        func.sum(ChiTietHoaDon.so_luong).label('so_luong_ban'),
        func.sum(ChiTietHoaDon.tong_tien).label('doanh_thu')
    ).join(
        Sach, Sach.id == ChiTietHoaDon.sach_id
    ).join(
        TheLoai, TheLoai.id == Sach.the_loai_id
    ).join(
        HoaDonBanSach, HoaDonBanSach.id == ChiTietHoaDon.hoa_don_id
    ).filter(
        HoaDonBanSach.ngay_tao_hoa_don >= start_date,
        HoaDonBanSach.ngay_tao_hoa_don < end_date
    ).group_by(
        TheLoai.ten_the_loai
    ).all()

    return ket_qua


def get_frequency_stats(thang, nam):
    start_date = datetime(nam, thang, 1)
    if thang == 12:
        end_date = datetime(nam + 1, 1, 1)  # Nếu là tháng 12, chuyển sang tháng 1 năm sau.
    else:
        end_date = datetime(nam, thang + 1, 1)

    # Truy vấn tổng số lượng bán trong tháng và năm
    total_sales_subquery = db.session.query(
        func.sum(ChiTietHoaDon.so_luong).label('tong_so_luong')
    ).join(
        HoaDonBanSach, HoaDonBanSach.id == ChiTietHoaDon.hoa_don_id
    ).filter(
        HoaDonBanSach.ngay_tao_hoa_don >= start_date,
        HoaDonBanSach.ngay_tao_hoa_don < end_date
    ).scalar()  # Trả về một giá trị tổng

    # Truy vấn dữ liệu cho từng sách
    results = db.session.query(
        Sach.id.label('ma_sach'),
        Sach.ten_sach,
        TheLoai.ten_the_loai,
        func.sum(ChiTietHoaDon.so_luong).label('so_luong_ban'),
        (func.sum(ChiTietHoaDon.so_luong) / total_sales_subquery * 100).label('ti_le_ban')  # Tính tỉ lệ
    ).join(
        ChiTietHoaDon, Sach.id == ChiTietHoaDon.sach_id
    ).join(
        HoaDonBanSach, HoaDonBanSach.id == ChiTietHoaDon.hoa_don_id
    ).join(
        TheLoai, TheLoai.id == Sach.the_loai_id
    ).filter(
        HoaDonBanSach.ngay_tao_hoa_don >= start_date,
        HoaDonBanSach.ngay_tao_hoa_don < end_date
    ).group_by(
        Sach.id, Sach.ten_sach
    ).all()

    return results


def get_id_from_ten_vai_tro(ten_vai_tro):
    vai_tro = VaiTro.query.filter_by(ten_vai_tro=ten_vai_tro).first()
    return vai_tro.id if vai_tro else None


def get_the_loai():
    return TheLoai.query.order_by('id').all()

def load_products(cate_id=None, kw=None, page=1):
    query = Sach.query

    if kw:
        query = query.filter(Sach.ten_sach.contains(kw))

    # if cate_id:
    #     query = query.filter(Sach.the_loai_id == cate_id)
    #
    page_size = app.config.get('PAGE_SIZE')
    start = (page - 1) * page_size
    query = query.slice(start, start + page_size)

    return query.all()

def count_sach():
    return Sach.query.count()

def load_all_tacgia():
    return TacGia.query.all()

def load_all_theloai():
    return TheLoai.query.all()

def load_sach(ten_the_loai = None, ten_tac_gia = None):
    query = Sach.query.options(
        joinedload(Sach.the_loai),  # Tải trước thông tin thể loại
        joinedload(Sach.tac_gia)  # Tải trước thông tin tác giả
    )

    # Lọc theo tên thể loại nếu có
    if ten_the_loai:
        query = query.join(TheLoai).filter(TheLoai.ten_the_loai == ten_the_loai)

    # Lọc theo tên tác giả nếu có
    if ten_tac_gia:
        query = query.join(TacGia).filter(TacGia.ten_tac_gia == ten_tac_gia)

    # Thực thi truy vấn và trả về danh sách sách
    return query.all()

def user_exists(username):
    return db.session.query(User).filter_by(username=username).first() is not None