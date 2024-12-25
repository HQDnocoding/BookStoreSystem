import locale
from datetime import datetime
from xmlrpc.client import DateTime

from flask import session, jsonify
from flask_login import current_user
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.operators import desc_op

from app.models import TheLoai, VaiTro, QuyDinh, TacGia, TrangThaiDonHang, PhuongThucThanhToan, User, \
    Sach, ChiTietDonHang, PhieuNhapSach, ChiTietPhieuNhapSach, DonHang, \
    ThongTinNhanHang
from app import db, admin, app, Status, Role, PayingMethod
import hashlib

locale.setlocale(locale.LC_ALL, 'vi_VN')


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


# def create_hoadonbansach(ngay_tao_hoa_don,nhanvien_id=None):  # Da test
#     new_hoadonbansach = HoaDonBanSach(ngay_tao_hoa_don=ngay_tao_hoa_don,nhan_vien= nhanvien_id)
#     db.session.add(new_hoadonbansach)
#     db.session.commit()
#
#     return new_hoadonbansach


def create_sach(tenSach, donGia, the_loai_id, tac_gia_id):  # Da test
    new_sach = Sach(tenSach=tenSach, donGia=donGia, the_loai_id=the_loai_id, tac_gia_id=tac_gia_id)
    db.session.add(new_sach)
    db.session.commit()


# def create_chitiethoadon(sach_id, hoa_don_id, so_luong, tong_tien):  # Da test
#     new_chitiethoadon = ChiTietHoaDon(sach_id=sach_id, hoa_don_id=hoa_don_id, so_luong=so_luong, tong_tien=tong_tien)
#     db.session.add(new_chitiethoadon)
#     db.session.commit()


# def create_soluongconlai(so_luong, sach_id):
#     new_soluongconlai = SoLuongCuonConLai(so_luong=so_luong, sach_id=sach_id)
#     db.session.add(new_soluongconlai)
#     db.session.commit()


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

    return  new_donhang



def create_thongtinnhanhang( id,dien_thoai_nhan_hang, dia_chi_nhan_hang):
    new_thongtinnhanhang = ThongTinNhanHang(id=id, dien_thoai_nhan_hang=dien_thoai_nhan_hang,
                                            dia_chi_nhan_hang=dia_chi_nhan_hang)
    db.session.add(new_thongtinnhanhang)
    db.session.commit()
    return new_thongtinnhanhang


def create_chitietdonhang( don_hang_id, sach_id, so_luong, tong_tien):
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
def update_user_password(user_id, new_password):
    user = get_user_by_id(user_id)
    new_password_hash = str(hashlib.md5(new_password.strip().encode('utf-8')).hexdigest())
    user.password = new_password_hash
    db.session.commit()

def get_stats(nam, thang, ten_the_loai):
    from sqlalchemy.exc import SQLAlchemyError

    try:
        # Xác định start_date và end_date
        start_date = datetime(nam, thang, 1)
        end_date = datetime(nam + 1, 1, 1) if thang == 12 else datetime(nam, thang + 1, 1)

        # Truy vấn tổng số lượng bán
        total_sales_subquery = db.session.query(
            func.sum(ChiTietDonHang.tong_tien).label('tong_doanh_thu')
        ).join(
            DonHang, DonHang.id == ChiTietDonHang.don_hang_id
        ).filter(
            DonHang.ngay_tao_don >= start_date,
            DonHang.ngay_tao_don < end_date,
            DonHang.trang_thai_id == get_id_by_trang_thai(Status.PAID.value)
        ).scalar()

        if not total_sales_subquery or total_sales_subquery == 0:
            return [["Không có dữ liệu", 0, 0.0, 0.0]]

        query = db.session.query(
            TheLoai.ten_the_loai,
            func.sum(ChiTietDonHang.so_luong).label('so_luong_ban'),
            func.sum(ChiTietDonHang.so_luong * func.coalesce(Sach.don_gia, 0)).label('doanh_thu'),
            (func.sum(ChiTietDonHang.tong_tien) / total_sales_subquery * 100).label('ti_le_ban')
        ).join(
            Sach, Sach.id == ChiTietDonHang.sach_id  # Thêm join bảng Sach
        ).join(
            DonHang, DonHang.id == ChiTietDonHang.don_hang_id
        ).join(
            TheLoai, TheLoai.id == Sach.the_loai_id  # Giữ liên kết the_loai với Sach
        ).filter(
            DonHang.ngay_tao_don >= start_date,
            DonHang.ngay_tao_don < end_date,
            DonHang.trang_thai_id == get_id_by_trang_thai(Status.PAID.value)
        )

        if ten_the_loai != "Tất cả":
            if not db.session.query(TheLoai).filter(TheLoai.ten_the_loai == ten_the_loai).first():
                return [["Thể loại không tồn tại", 0, 0.0, 0.0]]
            query = query.filter(TheLoai.ten_the_loai == ten_the_loai)

        # Nhóm theo thể loại
        results = query.group_by(TheLoai.ten_the_loai).all()

        stats = []
        for result in results:
            ten_the_loai, so_luong_ban, doanh_thu, ti_le_ban = result
            stats.append([ten_the_loai, so_luong_ban, doanh_thu, ti_le_ban])

        return stats

    except SQLAlchemyError as e:
        print(e)
        return [["Lỗi hệ thống", 0, 0.0, 0.0]]


def get_frequency_stats(thang, nam, ten_the_loai):
    start_date = datetime(nam, thang, 1)
    if thang == 12:
        end_date = datetime(nam + 1, 1, 1)  # Nếu là tháng 12, chuyển sang tháng 1 năm sau.
    else:
        end_date = datetime(nam, thang + 1, 1)

    # Truy vấn tổng số lượng bán trong tháng và năm
    total_sales_subquery = db.session.query(
        func.sum(ChiTietDonHang.so_luong).label('tong_so_luong')
    ).join(
        DonHang, DonHang.id == ChiTietDonHang.don_hang_id
    ).filter(
        DonHang.ngay_tao_don >= start_date,
        DonHang.ngay_tao_don < end_date,
        DonHang.trang_thai_id == get_id_by_trang_thai(Status.PAID.value)
    ).scalar()  # Trả về một giá trị tổng

    # Nếu không có đơn hàng nào trong khoảng thời gian, trả về danh sách trống
    if not total_sales_subquery:
        return []

    # Truy vấn dữ liệu cho từng sách, lọc theo thể loại nếu có
    query = db.session.query(
        Sach.id.label('ma_sach'),
        Sach.ten_sach,
        TheLoai.ten_the_loai,
        func.sum(ChiTietDonHang.so_luong).label('so_luong_ban'),
        (func.sum(ChiTietDonHang.so_luong) / total_sales_subquery * 100).label('ti_le_ban')  # Tính tỉ lệ
    ).join(
        ChiTietDonHang, Sach.id == ChiTietDonHang.sach_id
    ).join(
        DonHang, DonHang.id == ChiTietDonHang.don_hang_id
    ).join(
        TheLoai, TheLoai.id == Sach.the_loai_id
    ).filter(
        DonHang.ngay_tao_don >= start_date,
        DonHang.ngay_tao_don < end_date,
        DonHang.trang_thai_id == get_id_by_trang_thai(Status.PAID.value)
    )

    if ten_the_loai != "Tất cả":
        query = query.filter(TheLoai.ten_the_loai == ten_the_loai)

    results = query.group_by(
        Sach.id, Sach.ten_sach, TheLoai.ten_the_loai
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


def count_sach(kw=None):
    query = Sach.query

    if kw:
        query = query.filter(Sach.ten_sach.contains(kw))

    return query.count()


def load_all_tacgia():
    return TacGia.query.all()


def load_all_theloai():
    return TheLoai.query.all()


def load_sach(ten_the_loai=None, ten_tac_gia=None):
    if ten_the_loai == 'None' and ten_tac_gia == 'None':
        return Sach.query.all()

    query = Sach.query.options(
        joinedload(Sach.the_loai),  # Tải trước thông tin thể loại
        joinedload(Sach.tac_gia)  # Tải trước thông tin tác giả
    )

    # Lọc theo tên thể loại nếu có
    if ten_the_loai and ten_tac_gia == 'None':
        query = query.join(TheLoai).filter(TheLoai.ten_the_loai == ten_the_loai)

    # Lọc theo tên tác giả nếu có
    if ten_tac_gia and ten_the_loai == 'None':
        query = query.join(TacGia).filter(TacGia.ten_tac_gia == ten_tac_gia)

    # Thực thi truy vấn và trả về danh sách sách
    return query.all()


def user_exists(username):
    return db.session.query(User).filter_by(username=username).first() is not None


def add_so_luong(sach_id, so_luong):
    sach = Sach.query.get(sach_id)
    sach.so_luong += so_luong
    db.session.commit()


def get_id_by_phuong_thuc_name(name):
    return PhuongThucThanhToan.query.filter_by(ten_phuong_thuc=name).first().id

def get_id_by_trang_thai(name):
    return TrangThaiDonHang.query.filter_by(ten_trang_thai=name).first().id

def create_invoice_from_cart():
    try:

        pt_tt = get_id_by_phuong_thuc_name(PayingMethod.OFFLINE_PAY.value)
        tt = get_id_by_trang_thai(Status.PAID.value)

        cart = session.get('cart_admin', {})
        if not cart:
            raise ValueError("Giỏ hàng trống.")

        user = current_user
        if not user:
            raise ValueError("Người dùng chưa đăng nhập.")

        # Tạo hóa đơn bán sách
        don_hang = DonHang(ngay_tao_don=datetime.now(), phuong_thuc_id=pt_tt, trang_thai_id=tt, nhan_vien_id=user.id )
        db.session.add(don_hang)
        db.session.commit()



        # Thêm chi tiết hóa đơn
        for item in cart.values():
            sach = Sach.query.get(int(item['id']))
            if not sach:
                raise ValueError(f"Không tìm thấy sách với ID: {item['id']}")

            chi_tiet = ChiTietDonHang(

                sach_id=sach.id,
                don_hang_id=don_hang.id,
                so_luong=item['so_luong'],
                tong_tien=sach.don_gia * item['so_luong']
            )
            db.session.add(chi_tiet)

        db.session.commit()
        # Xóa giỏ hàng sau khi tạo hóa đơn
        session.pop('cart_admin', None)
        return don_hang

    except Exception as e:
        db.session.rollback()  # Rollback nếu có lỗi
        app.logger.error(f"Lỗi khi tạo hóa đơn: {e}")
        raise


def get_don_hang(id):
    # Truy vấn đơn hàng theo mã đơn hàng
    return DonHang.query.filter_by(id=id).first()


def get_nhan_vien(id):
    # Truy vấn đơn hàng theo mã đơn hàng
    return User.query.filter_by(id=id).first()

def get_chi_tiet_don_hang(id):
    return ChiTietDonHang.query.filter(id=id)




def create_hoa_don_from_don_hang(don_hang_id):
    try:
        # Lấy thông tin đơn hàng
        don_hang = get_don_hang(don_hang_id)
        if not don_hang:
            raise ValueError(f"Không tìm thấy đơn hàng với ID {don_hang_id}")

        # Cập nhật phương thức thanh toán và trạng thái
        pt_tt = get_id_by_phuong_thuc_name(PayingMethod.OFFLINE_PAY.value)
        tt = get_id_by_trang_thai(Status.PAID.value)
        user = current_user

        if not pt_tt or not tt:
            raise ValueError("Không tìm thấy phương thức thanh toán hoặc trạng thái hợp lệ.")

        if not user:
            raise ValueError("Người dùng chưa đăng nhập.")

        don_hang.phuong_thuc_id = pt_tt
        don_hang.trang_thai_id = tt
        don_hang.nhan_vien_id=user.id
        don_hang.ngay_tao_don=datetime.now()

        # Lưu thay đổi vào cơ sở dữ liệu
        db.session.commit()

        # Trả về thông tin cần thiết
        return {
            "don_hang_id": don_hang_id,
            "ngay_thanh_toan": don_hang.ngay_tao_don.strftime("%Y-%m-%d %H:%M:%S"),
            "nhan_vien_id": current_user.id,
            "sach": [
                {
                    "sach_id": chi_tiet.sach_id,
                    "so_luong": chi_tiet.so_luong,
                    "tong_tien": chi_tiet.tong_tien
                } for chi_tiet in don_hang.sach
            ]
        }, 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Lỗi khi tạo hóa đơn: {str(e)}")
        return {"error": f"Lỗi hệ thống: {str(e)}"}, 500



def get_or_create_phuong_thuc_id(ten_phuong_thuc):
    # Tìm kiếm phương thức trong cơ sở dữ liệu
    phuong_thuc = PhuongThucThanhToan.query.filter_by(ten_phuong_thuc=ten_phuong_thuc).first()

    # Nếu không tìm thấy, tạo mới
    if not phuong_thuc:
        phuong_thuc = PhuongThucThanhToan(ten_phuong_thuc=ten_phuong_thuc)
        db.session.add(phuong_thuc)
        db.session.commit()

    # Trả về ID của phương thức
    return phuong_thuc.id


def get_or_create_trang_thai_id(ten_trang_thai):
    # Tìm kiếm trạng thái trong cơ sở dữ liệu
    trang_thai = TrangThaiDonHang.query.filter_by(ten_trang_thai=ten_trang_thai).first()

    # Nếu không tìm thấy, tạo mới
    if not trang_thai:
        trang_thai = TrangThaiDonHang(ten_trang_thai=ten_trang_thai)
        db.session.add(trang_thai)
        db.session.commit()

    # Trả về ID của trạng thái
    return trang_thai.id


def get_so_luong_cuon_con_lai(sach_id):
    sach = Sach.query.get(sach_id)
    return sach.so_luong

def get_order_by_order_id(order_id):
    order = DonHang.query.get(order_id)

    return order



def get_trang_thai_by_name(ten):
    return TrangThaiDonHang.query.filter_by(ten_trang_thai=ten).first()


def get_order_by_user_id(khach_hang_id,page,page_size):
    don_hangs = DonHang.query.filter_by(khach_hang_id=khach_hang_id).order_by(DonHang.id.desc())

    start = (int(page)-1)* page_size
    end = start + page_size
    return don_hangs.slice(start,end).all()

def get_phuong_thuc_by_id(phuong_thuc_id):
    phuong_thuc = PhuongThucThanhToan.query.get(phuong_thuc_id)
    return phuong_thuc

def get_trang_thai_by_id(trang_thai_id):
    trang_thai = TrangThaiDonHang.query.get(trang_thai_id)
    return trang_thai

def get_order_total_price_by_id(id):
    don_hang = DonHang.query.get(id)
    order_details = don_hang.sach

    total_amount = 0
    for o in order_details:
        total_amount += o.tong_tien

    return total_amount

def get_sach_by_id(sach_id):
    return Sach.query.get(sach_id)