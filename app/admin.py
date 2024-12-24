import hashlib
import json
import os
from datetime import datetime, timedelta
from email.policy import default
from math import trunc
from operator import and_
from xmlrpc.client import DateTime

import cloudinary.uploader
import flask_login
import wtforms
from flask_admin import Admin, BaseView, expose
from flask_wtf import FlaskForm
from unicodedata import category

from app.dao import *
from sqlalchemy import false
from sqlalchemy.testing import fails
from wtforms.fields.datetime import DateField, DateTimeField
from wtforms.fields.simple import PasswordField
from wtforms_sqlalchemy.fields import QuerySelectField

from app import admin, db, app, dao, utils
from flask_admin.contrib.sqla import ModelView
from app.dao import get_role_name_by_role_id
from app.models import Sach, QuyDinh, TacGia, TheLoai, User, PhieuNhapSach, ChiTietPhieuNhapSach
from flask_login import current_user, logout_user, UserMixin, login_required
from flask import redirect, g, request, flash, url_for, session, jsonify
from app.models import VaiTro
from wtforms import StringField, SelectField, FileField, Form
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed
from markupsafe import Markup


class MyView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class AuthenticatedView(ModelView):
    def is_accessible(self):
        quan_ly_id = VaiTro.query.filter(VaiTro.ten_vai_tro.__eq__('QUANLY')).first()
        return current_user.is_authenticated and current_user.vai_tro_id == quan_ly_id.id

class AuthenticatedStatsView(BaseView):
    def is_accessible(self):
        quan_ly_id = VaiTro.query.filter(VaiTro.ten_vai_tro.__eq__('QUANLY')).first()
        return current_user.is_authenticated and current_user.vai_tro_id == quan_ly_id.id


class AuthenticatedNhanVienView(BaseView):
    def is_accessible(self):
        nhan_vien_id = VaiTro.query.filter(VaiTro.ten_vai_tro.__eq__('NHANVIEN')).first()
        return current_user.is_authenticated and current_user.vai_tro_id == nhan_vien_id.id


class AuthenticatedQuanLyKhoViewBV(BaseView):
    def is_accessible(self):
        qlk = VaiTro.query.filter(VaiTro.ten_vai_tro.__eq__('QUANLYKHO')).first()
        return current_user.is_authenticated and current_user.vai_tro_id == qlk.id


class AuthenticatedQuanLyKhoViewMV(ModelView):
    def is_accessible(self):
        qlk = VaiTro.query.filter(VaiTro.ten_vai_tro.__eq__('QUANLYKHO')).first()
        return current_user.is_authenticated and current_user.vai_tro_id == qlk.id


class QuyDinhView(AuthenticatedView):
    can_create = False
    can_delete = False
    column_editable_list = ['gia_tri','is_active']
    form_excluded_columns = ['ten_quy_dinh','ngay_tao']

class CashierView(AuthenticatedNhanVienView):
    @expose('/')
    def index(self):
        return self.render('admin/cashier.html')

    @expose('/cart', methods=['GET'])
    def get_cart(self):
        """Lấy thông tin giỏ hàng"""
        cart = session.get('cart', {})
        return jsonify(utils.cart_stats(cart))

    @expose('/cart', methods=['POST'])
    def add_to_cart(self):
        """Thêm sản phẩm vào giỏ hàng"""
        data = request.json
        product_id = str(data['id'])
        quantity = int(data.get('so_luong', 1))

        # Khởi tạo giỏ hàng nếu chưa có
        cart = session.get('cart', {})

        # Thêm hoặc cập nhật sản phẩm
        if product_id in cart:
            cart[product_id]['so_luong'] += quantity
        else:
            cart[product_id] = {
                "id": data['id'],
                "ten_sach": data['ten_sach'],
                "don_gia": data['don_gia'],
                "bia_sach": data['bia_sach'],
                "the_loai_id": data['the_loai_id'],
                "so_luong": quantity
            }

        # Lưu lại giỏ hàng
        session['cart'] = cart
        session.modified = True

        # Trả về trạng thái giỏ hàng
        return jsonify(utils.cart_stats(cart))

    @expose('/cart', methods=['DELETE'])
    def clear_cart(self):
        """Xóa toàn bộ giỏ hàng"""
        session['cart'] = {}
        session.modified = True
        return jsonify({"message": "Giỏ hàng đã được xóa."}), 204

    @expose('/cart/<int:product_id>', methods=['PUT'])
    def update_cart(self, product_id):
        """Cập nhật số lượng sản phẩm trong giỏ hàng"""
        data = request.json
        new_quantity = int(data.get('so_luong', 0))  # Lấy số lượng mới từ request
        cart = session.get('cart', {})

        # Kiểm tra nếu sản phẩm tồn tại trong giỏ hàng
        if str(product_id) in cart:
            if new_quantity > 0:
                cart[str(product_id)]['so_luong'] = new_quantity  # Cập nhật số lượng
            else:
                del cart[str(product_id)]  # Xóa sản phẩm nếu số lượng = 0

        # Lưu lại giỏ hàng vào session
        session['cart'] = cart
        session.modified = True

        # Trả về trạng thái giỏ hàng hiện tại
        return jsonify({
            "cart": list(cart.values()),
            "total_quantity": sum(item['so_luong'] for item in cart.values()),
            "total_amount": sum(item['don_gia'] * item['so_luong'] for item in cart.values())
        })

    @expose('/cart/<int:product_id>', methods=['DELETE'])
    def remove_from_cart(self, product_id):
        """Xóa sản phẩm khỏi giỏ hàng"""
        cart = session.get('cart', {})

        # Xóa sản phẩm khỏi giỏ hàng nếu tồn tại
        if str(product_id) in cart:
            del cart[str(product_id)]

        # Lưu lại giỏ hàng vào session
        session['cart'] = cart
        session.modified = True

        # Trả về trạng thái giỏ hàng hiện tại
        return jsonify({
            "cart": list(cart.values()),
            "total_quantity": sum(item['so_luong'] for item in cart.values()),
            "total_amount": sum(item['don_gia'] * item['so_luong'] for item in cart.values())
        })

    @expose('/search', methods=['GET'])
    def search_products(self):
        """Tìm kiếm sản phẩm"""
        query = request.args.get('query', '').strip()
        products = Sach.query.filter(Sach.ten_sach.ilike(f'%{query}%')).all()

        return jsonify([
            {
                'id': p.id,
                'name': p.ten_sach,
                'price': p.don_gia,
                'image': p.bia_sach,
                'the_loai_id': p.the_loai_id,
            } for p in products
        ])

    @expose('/cart/cash', methods=['GET'])
    @login_required
    def cashier(self, **kwargs):

        nv = dao.get_user_by_id(current_user.id)

        if nv is not None:
            ten_nv = f"{nv.ho} {nv.ten}"
        else:
            ten_nv = "Chưa có thông tin nhân viên"

        ten_kh = "Khách hàng mua tại nhà sách"

        cart = session.get('cart', {})
        print("Cart contents:", cart)
        print("Cart values:", cart.values())

        cart_list_dict = []

        for sach in cart.values():
            if not isinstance(sach, dict):
                app.logger.error(f"Giỏ hàng chứa phần tử không hợp lệ: {sach}")
                continue

            the_loai = TheLoai.query.filter_by(id=sach['the_loai_id']).first()
            the_loai_ten = the_loai.ten_the_loai if the_loai else "Không có"

            cart_list_dict.append({
                "ten_sach": sach.get('ten_sach', 'Không rõ'),
                "the_loai": the_loai_ten,
                "don_gia": sach.get('don_gia', 0),
                "so_luong": sach.get('so_luong', 0)
            })

        try:

            app.logger.error(cart_list_dict.__str__())

            hoa_don = create_invoice_from_cart()

            output_dir = "bieu_mau_hoa_don_mua_tai_cua_hang"
            os.makedirs(output_dir, exist_ok=True)
            output_filename = os.path.join(output_dir, f"tch_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")

            utils.create_invoice_pdf(ten_kh, hoa_don.ngay_tao_hoa_don, cart_list_dict ,ten_nv ,output_filename)
            flash("Hóa đơn đã được tạo thành công.", "success")
        except Exception as e:
            app.logger.error(f"Lỗi khi tạo hóa đơn: {e}")
            flash("Đã xảy ra lỗi khi tạo hóa đơn.", "danger")
        return redirect('/admin/cashierview')


class Cashier2View(AuthenticatedNhanVienView):

    @expose('/')
    def index(self):
        return self.render('admin/cashier.html')

    @expose('/don_hang/<int:don_hang_id>', methods=['GET'])
    def get_order_details(self, don_hang_id):
        # Truy vấn đơn hàng
        waiting_status_id = dao.get_trang_thai_by_name(Status.WAITING.value)

        don_hang = DonHang.query.filter(and_(
            DonHang.id == don_hang_id,
            DonHang.trang_thai_id == waiting_status_id.id
        )).first()
        if not don_hang:
            return jsonify({"error": "don_hang not found"}), 404

        # Lấy thông tin người nhận hàng
        thong_tin_nhan_hang = ThongTinNhanHang.query.filter_by(id=don_hang.id).first()

        khach_hang = User.query.get(don_hang.khach_hang_id)

        # Lấy danh sách sách trong đơn hàng
        chi_tiet_don_hang = ChiTietDonHang.query.filter_by(don_hang_id=don_hang.id).all()

        sach_data = [
            {
                "ten_sach": Sach.query.get(chi_tiet.sach_id).ten_sach if Sach.query.get(
                    chi_tiet.sach_id) else "Không xác định",
                "the_loai": TheLoai.query.get(
                    Sach.query.get(chi_tiet.sach_id).the_loai_id).ten_the_loai if Sach.query.get(chi_tiet.sach_id)
                                                                                  and TheLoai.query.get(
                    Sach.query.get(chi_tiet.sach_id).the_loai_id) else "Không xác định",
                "so_luong": chi_tiet.so_luong,
                "don_gia": Sach.query.get(chi_tiet.sach_id).don_gia if Sach.query.get(
                    chi_tiet.sach_id) else "Không xác định",
            }
            for chi_tiet in chi_tiet_don_hang
        ]

        session['sach_data'] = sach_data

        # Cấu trúc dữ liệu trả về
        response = {
            "don_hang_id": don_hang.id,
            "ngay_tao": don_hang.ngay_tao_don.strftime('%Y-%m-%d %H:%M:%S'),
            "phuong_thuc_thanh_toan": PhuongThucThanhToan.query.get(
                don_hang.phuong_thuc_id).ten_phuong_thuc if don_hang.phuong_thuc_id else None,
            "trang_thai_don_hang": TrangThaiDonHang.query.get(
                don_hang.trang_thai_id).ten_trang_thai if don_hang.trang_thai_id else None,
            "khach_hang_id": don_hang.khach_hang_id,
            "ten_khach_hang": khach_hang.ten,
            "ho_khach_hang": khach_hang.ho,
            "thong_tin_nhan_hang": {
                "dien_thoai": thong_tin_nhan_hang.dien_thoai_nhan_hang if thong_tin_nhan_hang else None,
                "dia_chi": thong_tin_nhan_hang.dia_chi_nhan_hang if thong_tin_nhan_hang else None,
            },
            "sach": sach_data
        }

        session['ten_kh'] = f"{khach_hang.ho} {khach_hang.ten}"

        return jsonify(response), 200

    @expose('/don_hang/<int:don_hang_id>', methods=['POST'])
    def create_invoice(self, don_hang_id):
        nhan_vien_id = current_user.id

        infor, sach = create_hoa_don_from_don_hang(don_hang_id, nhan_vien_id)

        ten_kh = session.get('ten_kh', '')
        sach_data = session.get('sach_data', [])

        nv = dao.get_nhan_vien(nhan_vien_id)
        ho_ten_nv = f"{nv.ho} {nv.ten}"

        output_dir = "bieu_mau_hoa_don_mua_tai_cua_hang"
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.join(output_dir, f"dt_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")

        utils.create_invoice_pdf(ten_kh, infor['ngay_tao_hoa_don'], sach_data, ho_ten_nv, output_filename)

        return jsonify({"path": "/admin/cashier2view"}), 200


class RevenueStatsView(AuthenticatedStatsView):
    @expose("/")
    def index(self):
        return self.render("admin/revenue-stats.html", tl=get_the_loai())


class FrequencyStatsView(AuthenticatedStatsView):
    @expose("/")
    def index(self):
        now = datetime.now()

        current_year=now.year+1

        last_month = (now - timedelta(days=now.day)).month
        last_year = (now - timedelta(days=now.day)).year

        # Lấy thông tin lọc từ người dùng
        thang = request.args.get("sel_monthf", last_month, type=int)

        session['thang_stat']=thang

        nam = request.args.get("sel_yearf", last_year, type=int)

        session['nam_stat']=nam
        the_loai = request.args.get("the_loaif", "Tất cả")

        # Dữ liệu thống kê
        fstats = get_frequency_stats(thang, nam)


        # Lọc theo thể loại (nếu có)
        if the_loai != "Tất cả":
            fstats = [s for s in fstats if s[2] == the_loai]

        # Truyền dữ liệu cho biểu đồ
        labels = [s[1] for s in fstats] or []  # Tên sách
        data = [s[3] for s in fstats]  # Số lượng bán
        percentages = [s[4] for s in fstats]  # Tỉ lệ
        data = [float(d) for d in data] or []
        percentages = [float(p) for p in percentages] or []
        # Danh sách thể loại để hiển thị trong form lọc
        tl = get_the_loai()

        return self.render(
            "admin/frequency-stats.html",
            fstats=fstats,
            tl=tl,
            thang=thang,
            nam=nam,
            the_loai=the_loai,
            labels=labels,
            data=data,
            percentages=percentages,
            current_year=current_year
        )

    @expose('/export/', methods=['get'])
    def export(self):
        try:
            thang = session.get('thang_stat', 1)
            nam = session.get('nam_stat', 2004)
            fstats = get_frequency_stats(thang, nam)

            output_dir = "bieu mau thong ke tan suat"
            os.makedirs(output_dir, exist_ok=True)
            output_filename = os.path.join(output_dir, f"tch_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")

            utils.create_pdf_export_freq(fstats, output_filename, thang, nam)

            # Trả về file PDF cho người dùng tải về
            return 200

        except Exception as e:
            flash(f"Tạo biểu mẫu thống kê tần suất thất bại {e}", "error")
            return redirect(request.referrer)  # Quay lại trang trước nếu có lỗi


class Logout(MyView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect("/admin")





class SachForm(Form):
    ten_sach = StringField('Tên sách', validators=[DataRequired()])
    don_gia = StringField('Đơn giá', validators=[DataRequired()])
    noi_dung = StringField('Nội dung', validators=[DataRequired()])
    tac_gia_id = SelectField('Tác giả', coerce=int, validators=[DataRequired()])
    new_tac_gia = StringField('Tác giả mới (nếu không có)', validators=[DataRequired()])
    the_loai_id = SelectField('Thể loại', coerce=int, validators=[DataRequired()])
    new_the_loai = StringField('Thể loại mới (nếu không có)', validators=[DataRequired()])
    bia_sach = FileField('Bìa sách', validators=[
        DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], "Chỉ được phép upload file hình ảnh!")])


class SachView(AuthenticatedView):
    can_edit = True
    can_view_details = True
    column_searchable_list = ['id', 'ten_sach']
    form = SachForm

    def create_form(self):
        form = super().create_form()
        form.tac_gia_id.choices = [(a.id, a.ten_tac_gia) for a in TacGia.query.all()]
        form.the_loai_id.choices = [(a.id, a.ten_the_loai) for a in TheLoai.query.all()]

        return form

    def edit_form(self, obj):
        form = super().edit_form(obj)  # Gọi phương thức gốc
        form.tac_gia_id.choices = [(a.id, a.ten_tac_gia) for a in TacGia.query.all()]  # Thêm danh sách tác giả
        form.the_loai_id.choices = [(a.id, a.ten_the_loai) for a in TheLoai.query.all()]

        return form


    column_list = ['id', 'ten_sach', 'don_gia', 'so_luong','tac_gia_id']  # cot hiển thị

    column_labels = {  # sua ten hien thi
        'id': 'Mã SP',
        'ten_sach': 'Tên sách',
        'don_gia': 'Đơn giá',
        'tac_gia_id': 'Tác giả',
        'the_loai_id': 'Thể loại',
        'so_luong': 'Số lượng',
    }

    column_formatters = {
        'so_luong_cuon_con_lai': lambda v, c, m, p: (
                db.session.query(Sach.so_luong).filter(Sach.id == m.id).order_by(
                    Sach.thoi_diem.desc()).first() or 'NaN'
        )
    }
    column_formatters_detail = {
        'bia_sach': lambda v, c, m, p: Markup(
            f'<img src="{m.bia_sach}" style="max-width: 200px; max-height: 150px;" alt="Bìa sách">'
        ) if m.bia_sach else Markup('<p>No Image</p>')
    }

    def on_model_change(self, form, model, is_created):
        if form.new_tac_gia.data:
            # Kiểm tra xem tác giả có tồn tại chưa
            tac_gia = TacGia.query.filter_by(ten_tac_gia=form.new_tac_gia.data).first()
            if not tac_gia:
                # Nếu không có tác giả, tạo tác giả mới
                tac_gia = TacGia(ten_tac_gia=form.new_tac_gia.data)
                db.session.add(tac_gia)
                db.session.commit()

                flash(f"Đã tạo tác giả mới: {tac_gia.ten_tac_gia}", 'success')

            # Gán tác giả vào sách
            model.tac_gia_id = tac_gia.id
        else:
            # Nếu người dùng không nhập tác giả mới, gán tác giả đã chọn
            model.tac_gia_id = form.tac_gia_id.data

        if form.new_the_loai.data:
            the_loai = TheLoai.query.filter_by(ten_the_loai=form.new_the_loai.data).first()
            if not the_loai:
                # Nếu không có tác giả, tạo tác giả mới
                the_loai = TheLoai(ten_the_loai=form.new_the_loai.data)
                db.session.add(the_loai)
                db.session.commit()

                flash(f"Đã tạo thể loại mới: {the_loai.ten_the_loai}", 'success')

            model.the_loai_id = the_loai.id
        else:
            model.the_loai_id = form.the_loai_id.data

        file_data = form.bia_sach.data
        if file_data:

            if not file_data.content_type.startswith("image/"):
                raise ValueError("Chỉ được upload hình ảnh (JPEG, PNG, GIF, v.v.)")

            upload_result = cloudinary.uploader.upload(file_data, folder="upload/bia_sach")
            model.bia_sach = upload_result.get('secure_url')

        return super().on_model_change(form, model, is_created)


class TacGiaView(AuthenticatedView):
    column_searchable_list = ['ten_tac_gia']
    form_excluded_columns = ['sach']
    column_list = ['id', 'ten_tac_gia']
    column_labels = {
        'id': 'Mã tác giả',
        'ten_tac_gia': 'Tên tác giả'
    }


class TheLoaiView(AuthenticatedView):
    column_searchable_list = ['ten_the_loai']
    form_excluded_columns = ['sach']
    column_list = ['id', 'ten_the_loai']
    column_labels = {
        'id': 'Mã thể loại',
        'ten_the_loai': 'Tên thể loại'
    }


class VaitroView(AuthenticatedView):
    can_create = True
    can_edit = True


class UserForm(FlaskForm):
    ho = StringField('Họ', validators=[DataRequired()])
    ten = StringField('Tên', validators=[DataRequired()])
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    password = StringField('Mật khẩu', validators=[DataRequired()])
    ngay_tao = ngay_tao = DateTimeField('Ngày tạo', format='%Y-%m-%d %H:%M:%S', default=datetime.now)  # Gán ngày giờ mặc định
    avatar = FileField('Avatar', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'],
                                                                         "Chỉ được phép upload file hình ảnh!")])
    vai_tro_id = QuerySelectField('Vai trò', query_factory=lambda: VaiTro.query.all(),
                                  get_label='ten_vai_tro', allow_blank=False)


class UserView(AuthenticatedView):
    column_searchable_list = ['id', 'ho', 'ten', 'username']
    form_excluded_columns = ['phieu_nhap_sach', 'don_hang']

    can_edit = True
    can_create = True
    can_view_details = True

    form = UserForm

    def create_form(self):
        form = super().create_form()
        form.ngay_tao.flags.hidden = True
        return form

    def edit_form(self, obj):
        form = super().edit_form(obj)
        form.password.flags.hidden = True
        form.username.render_kw = {"readonly": True}
        form.password.render_kw = {"readonly": True}
        del form.password
        form.ngay_tao.render_kw = {"readonly": True}
        return form

    def get_detail_view(self, obj):
        # Tạo view detail mà không có mật khẩu
        return {
            'Họ': obj.ho,
            'Tên': obj.ten,
            'Tên đăng nhập': obj.username,
            'Ngày tạo': obj.ngay_tao.strftime('%Y-%m-%d %H:%M:%S'),  # Định dạng ngày
            'Avatar': obj.avatar,  # Nếu cần hiển thị ảnh, có thể thêm xử lý hiển thị
            'Vai trò': obj.vai_tro_id.ten_vai_tro if obj.vai_tro_id else None,
        }

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.ngay_tao = datetime.now()  # Gán giá trị khi tạo mới
            model.password = str(hashlib.md5(form.password.data.encode('utf-8')).hexdigest())
        model.vai_tro_id = form.vai_tro_id.data.id
        file_data = form.avatar.data
        if file_data:

            if not file_data.content_type.startswith("image/"):
                raise ValueError("Chỉ được upload hình ảnh (JPEG, PNG, GIF, v.v.)")

            upload_result = cloudinary.uploader.upload(file_data, folder="upload/avatar")
            model.avatar = upload_result.get('secure_url')

        return super().on_model_change(form, model, is_created)

    column_formatters_detail = {
        'avatar': lambda v, c, m, p: Markup(
            f'<img src="{m.avatar}" style="max-width: 200px; max-height: 150px;" alt="Bìa sách">'
        ) if m.avatar else Markup('<p>No Image</p>')
    }
    form_widget_args = {
        'avatar': {

        }
    }


class XemPhieuNhapSach(AuthenticatedQuanLyKhoViewMV):
    can_view_details = True
    can_create = False
    can_edit = False
    can_delete = False


# column_list = ['id','ngay_nhap','quan_ly_kho_id']

class XemChiTietPhieuNhapSach(AuthenticatedQuanLyKhoViewMV):
    can_view_details = True
    can_create = False
    can_edit = False
    can_delete = False


class NhapPhieuView(AuthenticatedQuanLyKhoViewBV):
    @expose("/")
    def index(self):

        ten_the_loai = request.args.get('theloai_search')
        ten_tac_gia = request.args.get('tacgia_search')

        theloais = load_all_theloai()
        tacgias = load_all_tacgia()
        sachs = load_sach(ten_the_loai=ten_the_loai, ten_tac_gia=ten_tac_gia)

        return self.render("admin/booksimport.html", theloais=theloais, tacgias=tacgias, sachs=sachs)

    @expose("/create", methods=["POST"])
    def create_invoice(self):
        # Lấy dữ liệu từ form
        books_data = request.form.get("books_data")
        if not books_data:
            flash("Danh sách sách trống!", "error")
            return redirect(url_for(".index"))

        try:
            books = json.loads(books_data)

            # Tạo phiếu nhập mới
            phieu_nhap = PhieuNhapSach(quan_ly_kho_id=current_user.get_id())
            db.session.add(phieu_nhap)
            db.session.commit()

            # Thêm sách vào phiếu nhập
            for book in books:
                sach = Sach.query.filter_by(ten_sach=book["ten_sach"]).first()
                if sach:
                    chi_tiet = ChiTietPhieuNhapSach(
                        phieu_nhap_sach_id=phieu_nhap.id,
                        sach_id=sach.id,
                        so_luong=book["so_luong"]
                    )
                    soluongconlai = get_so_luong_cuon_con_lai(sach.id)
                    if (soluongconlai >= 300):
                        pass
                    else:
                        add_so_luong(so_luong=book["so_luong"], sach_id=sach.id)

                    db.session.add(chi_tiet)

            db.session.commit()
            flash("Tạo phiếu nhập sách thành công!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Đã xảy ra lỗi: {e}", "error")

        return redirect(url_for(".index"))


class PhuongThucThanhToanView(AuthenticatedView):
    can_view_details = True
    can_edit = False
    can_create = True
    form_excluded_columns = ['don_hang']
    form_choices = {
        'ten_phuong_thuc': [
            ('ONLINE', 'ONLINE'),
            ('TIỀN MẶT', 'TIỀN MẶT')
        ]
    }


class TrangThaiDonHangView(AuthenticatedView):
    can_view_details = False
    can_delete = True
    can_create = True
    form_excluded_columns = ['don_hang']
    form_choices = {
        'ten_trang_thai': [
            ('Đang xử lý', 'Đang xử lý'),
            ('Đã xử lý', 'Đã xử lý'),
            ('Đang giao', 'Đang giao'),
            ('Đã giao', 'Đã giao')
        ]
    }


admin.add_view(SachView(Sach, db.session, name='Sách', category='Quản lý sách'))
admin.add_view(TheLoaiView(TheLoai, db.session, name='Thể loại', category='Quản lý sách'))
admin.add_view(TacGiaView(TacGia, db.session, name='Tác giả', category='Quản lý sách'))
admin.add_view(QuyDinhView(QuyDinh, db.session, name='Quy định'))
admin.add_view(UserView(User, db.session, name='Quản lý User'))
admin.add_view(VaitroView(VaiTro, db.session, name='Vai trò'))
admin.add_view(TrangThaiDonHangView(TrangThaiDonHang, db.session, name='Trạng thái đơn hàng'))

admin.add_view(PhuongThucThanhToanView(PhuongThucThanhToan, db.session, name='Phương thức thanh toán'))

admin.add_view(NhapPhieuView(name="Nhập sách"))
admin.add_view(XemPhieuNhapSach(PhieuNhapSach, db.session, name="Xem Phiếu Nhập sách", category="XEM PHIẾU NHẬP"))
admin.add_view(XemPhieuNhapSach(ChiTietPhieuNhapSach, db.session, name="Xem Chi Tiết Phiếu", category="XEM PHIẾU NHẬP"))

admin.add_view(RevenueStatsView(name='Thống kê doanh thu', category='Thống kê báo cáo'))
admin.add_view(FrequencyStatsView(name='Thống kê tần suất', category='Thống kê báo cáo'))

admin.add_view(CashierView(name='Bán hàng mua tại cửa hàng', category='Bán hàng'))
admin.add_view(Cashier2View(name='Bán hàng đã đặt trước', category='Bán hàng'))

admin.add_view(Logout(name="Đăng xuất"))
