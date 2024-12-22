from datetime import datetime
from xmlrpc.client import DateTime

from flask import session, jsonify
from flask_login import current_user
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.operators import desc_op

from app.models import TheLoai, VaiTro, QuyDinh, TacGia, TrangThaiDonHang, PhuongThucThanhToan, User, HoaDonBanSach, \
    Sach, ChiTietDonHang, ChiTietHoaDon, SoLuongCuonConLai, PhieuNhapSach, ChiTietPhieuNhapSach, DonHang, \
    ThongTinNhanHang
from app import db, admin, app,Status,Role,PayingMethod
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


def create_hoadonbansach(ngay_tao_hoa_don,nhanvien_id=None):  # Da test
    new_hoadonbansach = HoaDonBanSach(ngay_tao_hoa_don=ngay_tao_hoa_don,nhan_vien= nhanvien_id)
    db.session.add(new_hoadonbansach)
    db.session.commit()

    return new_hoadonbansach


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


def load_sach(ten_the_loai=None, ten_tac_gia=None):
    if ten_the_loai == 'None' and  ten_tac_gia == 'None':
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


def get_sach_for_detail_by_id(sach_id):
    sach = Sach.query.get(sach_id)
    #vai_tro = VaiTro.query.get(role_id)
    if sach:
        return {
            'id': sach.id,
            'ten_sach': sach.ten_sach,
            'don_gia': sach.don_gia,
            'bia_sach': sach.bia_sach,
            'tac_gia': sach.tac_gia.ten_tac_gia if sach.tac_gia else None,  # Lấy tên tác giả
            'the_loai': sach.the_loai.ten_the_loai if sach.the_loai else None  # Lấy tên thể loại
        }
    return None

def update_or_add_so_luong(sach_id, so_luong):
    # Tìm bản ghi có sach_id tương ứng
    so_luong_con_lai = SoLuongCuonConLai.query.filter_by(sach_id=sach_id).first()

    # Nếu bản ghi đã tồn tại, cập nhật so_luong
    if so_luong_con_lai:
        so_luong_con_lai.so_luong += so_luong  # Cộng thêm so_luong mới vào giá trị hiện tại
        so_luong_con_lai.thoi_diem = datetime.now()  # Cập nhật thời điểm

    # Nếu không có bản ghi nào, tạo bản ghi mới
    else:
        so_luong_con_lai = SoLuongCuonConLai(sach_id=sach_id, so_luong=so_luong)
        db.session.add(so_luong_con_lai)

    # Lưu thay đổi vào cơ sở dữ liệu
    db.session.commit()


def create_invoice_from_cart():
    try:
        cart = session.get('cart', {})
        if not cart:
            raise ValueError("Giỏ hàng trống.")

        user = current_user
        if not user:
            raise ValueError("Người dùng chưa đăng nhập.")

        # Tính tổng tiền từ giỏ hàng
        tong_tien = sum(int(item['so_luong']) * float(item['don_gia']) for item in cart.values())

        # Tạo hóa đơn bán sách
        hoa_don = HoaDonBanSach(ngay_tao_hoa_don=datetime.now(), nhan_vien=user.id)
        db.session.add(hoa_don)
        db.session.flush()  # Đảm bảo `hoa_don.id` được sinh ra

        # Thêm chi tiết hóa đơn
        for item in cart.values():
            sach = Sach.query.get(int(item['id']))
            if not sach:
                raise ValueError(f"Không tìm thấy sách với ID: {item['id']}")

            chi_tiet = ChiTietHoaDon(

                sach_id=sach.id,
                hoa_don_id=hoa_don.id,
                so_luong=item['so_luong'],
                tong_tien=sach.don_gia * item['so_luong']
            )
            db.session.add(chi_tiet)

        db.session.commit()
        # Xóa giỏ hàng sau khi tạo hóa đơn
        session.pop('cart', None)
        return hoa_don

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




def create_hoa_don_from_don_hang(don_hang_id, nhan_vien_id=None):
    try:
        # Lấy thông tin đơn hàng
        don_hang = DonHang.query.get(don_hang_id)
        if not don_hang:
            return {"error": "Đơn hàng không tồn tại."}, 404

        # Lấy danh sách chi tiết đơn hàng
        chi_tiet_don_hang = ChiTietDonHang.query.filter_by(don_hang_id=don_hang_id).all()

        if not chi_tiet_don_hang:
            return {"error": "Đơn hàng không có sách nào."}, 400

        # Tạo hóa đơn
        hoa_don = HoaDonBanSach(
            ngay_tao_hoa_don=datetime.now(),
            nhan_vien=nhan_vien_id  # Nếu có thông tin nhân viên
        )
        db.session.add(hoa_don)
        db.session.flush()  # Đẩy tạm để lấy ID của hóa đơn

        # Thêm chi tiết hóa đơn từ chi tiết đơn hàng
        for chi_tiet in chi_tiet_don_hang:
            sach = Sach.query.get(chi_tiet.sach_id)
            if sach:
                chi_tiet_hoa_don = ChiTietHoaDon(
                    sach_id=sach.id,
                    hoa_don_id=hoa_don.id,
                    so_luong=chi_tiet.so_luong,
                    tong_tien=chi_tiet.tong_tien
                )
                db.session.add(chi_tiet_hoa_don)
        # status=Status.PAID.value
        # don_hang.trang_thai_id = TrangThaiDonHang.query.filter(status).first().id
        db.session.commit()
        return jsonify({
            "hoa_don_id": hoa_don.id,
            "ngay_tao_hoa_don": hoa_don.ngay_tao_hoa_don.strftime("%Y-%m-%d %H:%M:%S"),
            "nhan_vien_id": hoa_don.nhan_vien,
            "sach": [
                {
                    "sach_id": chi_tiet.sach_id,
                    "so_luong": chi_tiet.so_luong,
                    "tong_tien": chi_tiet.tong_tien
                } for chi_tiet in hoa_don.sach
            ]
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
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
    # Truy vấn các bản ghi có `sach_id` tương ứng và tính tổng `so_luong`
    total_so_luong = db.session.query(db.func.sum(SoLuongCuonConLai.so_luong)) \
        .filter(SoLuongCuonConLai.sach_id == sach_id) \
        .scalar()  # `.scalar()` trả về giá trị tổng hoặc None nếu không có kết quả

    # Nếu không có bản ghi nào, trả về 0
    if total_so_luong is None:
        return 0
    return total_so_luong

def get_order_by_order_id(order_id):
    order = DonHang.query.get(order_id)

    return order

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