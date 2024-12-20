import hashlib
import json
from datetime import datetime
from email.policy import default
from math import trunc
from xmlrpc.client import DateTime

import cloudinary.uploader
import flask_login
import wtforms
from flask_admin import Admin, BaseView, expose
from unicodedata import category

from app.dao import *
from sqlalchemy import false
from sqlalchemy.testing import fails
from wtforms.fields.datetime import DateField, DateTimeField
from wtforms.fields.simple import PasswordField
from wtforms_sqlalchemy.fields import QuerySelectField

from app import admin, db, app
from flask_admin.contrib.sqla import ModelView
from app.dao import get_role_name_by_role_id
from app.models import Sach, QuyDinh, SoLuongCuonConLai, TacGia, TheLoai, User, PhieuNhapSach, ChiTietPhieuNhapSach
from flask_login import current_user, logout_user ,UserMixin
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
    can_create = True
    can_edit = True


class CashierView(BaseView):
    @expose('/')
    def index(self):
        # Trang quản lý giỏ hàng (nếu cần giao diện riêng cho admin)
        return self.render('admin/cashier.html')

    @expose('/api/cart', methods=['POST'])
    def add_to_cart(self):
        """ Thêm sản phẩm vào giỏ hàng """
        data = request.json
        product_id = str(data['id'])  # Chuyển ID thành chuỗi để làm key trong session
        quantity = int(data.get('so_luong', 1))  # Lấy số lượng, mặc định là 1

        # Khởi tạo giỏ hàng nếu chưa có
        cart = session.get('cart', {})

        # Thêm hoặc cập nhật sản phẩm trong giỏ hàng
        if product_id in cart:
            cart[product_id]['so_luong'] += quantity
        else:
            cart[product_id] = {
                "id": data['id'],
                "ten_sach": data['ten_sach'],
                "don_gia": data['don_gia'],
                "bia_sach": data['bia_sach'],
                "so_luong": quantity
            }

        # Lưu lại giỏ hàng vào session
        session['cart'] = cart
        session.modified = True

        return jsonify(self.cart_stats(cart))

    @expose('/api/cart/<int:product_id>', methods=['PUT'])
    def update_cart(self, product_id):
        """ Cập nhật số lượng sản phẩm trong giỏ hàng """
        data = request.json
        cart = session.get('cart', {})

        # Kiểm tra sản phẩm có tồn tại không
        if str(product_id) in cart:
            cart[str(product_id)]['so_luong'] = int(data['so_luong'])

        # Lưu lại giỏ hàng vào session
        session['cart'] = cart
        session.modified = True

        return jsonify(self.cart_stats(cart))

    @expose('/api/cart/<int:product_id>', methods=['DELETE'])
    def delete_cart(self, product_id):
        """ Xóa sản phẩm khỏi giỏ hàng """
        cart = session.get('cart', {})

        # Kiểm tra và xóa sản phẩm
        if str(product_id) in cart:
            del cart[str(product_id)]

        # Lưu lại giỏ hàng vào session
        session['cart'] = cart
        session.modified = True

        return jsonify(self.cart_stats(cart))

    def cart_stats(self, cart=None):
        """ Tính toán tổng số lượng và tổng tiền của giỏ hàng """
        if cart is None:
            cart = session.get('cart', {})

        total_quantity = sum(item['so_luong'] for item in cart.values())
        total_amount = sum(item['don_gia'] * item['so_luong'] for item in cart.values())

        return {
            "total_quantity": total_quantity,
            "total_amount": total_amount
        }

    def search_products(selt):
        query = request.args.get('query', '')
        products = Sach.query.filter(
            Sach.ten_sach.like(f'%{query}%') | Sach.id.like(f'%{query}%')
        ).limit(10).all()

        return jsonify([
            {'id': p.id, 'name': p.name, 'price': p.price} for p in products
        ])



class RevenueStatsView(MyView):
    @expose("/")
    def index(self):
        return self.render("admin/revenue-stats.html",tl=get_the_loai())


class FrequencyStatsView(MyView):
    @expose("/")
    def index(self):
        return self.render("admin/frequency-stats.html",tl=get_the_loai())


class Logout(MyView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect("/admin")


class SachForm(Form):
    ten_sach = StringField('Tên sách', validators=[DataRequired()])
    don_gia = StringField('Đơn giá', validators=[DataRequired()])
    tac_gia_id = SelectField('Tác giả', coerce=int, validators=[DataRequired()])
    the_loai_id = SelectField('Thể loại', coerce=int, validators=[DataRequired()])
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

    # form_excluded_columns=['hoa_don_ban_sach','phieu_nhap_sach','don_hang','hoa_don_ban_sach','so_luong_cuon_con_lai']# fields bị loại bỏ trong form

    column_list = ['id', 'ten_sach', 'don_gia', 'so_luong_cuon_con_lai']  # cot hiển thị

    column_labels = {  # sua ten hien thi
        'id': 'Mã SP',
        'ten_sach': 'Tên sách',
        'don_gia': 'Đơn giá',
        'tac_gia_id': 'Tác giả',
        'the_loai_id': 'Thể loại',
        'so_luong_cuon_con_lai': 'Số lượng',
        'bia_sach': 'Bìa sách'
    }
    #
    # form_overrides = {
    #     'bia_sach': ImageUploadField,  # cho upload file
    #     'the_loai_id':QuerySelectField
    # }
    #
    # form_args = {
    #     'bia_sach':{
    #             'label':'Upload image'
    #     },
    #     'the_loai_id': {
    #         'label':'Thể loại',
    #         'query_factory': lambda: TheLoai.query.all(),  # Truy vấn tất cả thể loại
    #         'get_label': 'ten_the_loai',  # Hiển thị tên thể loại trong dropdown
    #         'allow_blank': False  # Không cho phép bỏ trống trường này
    #     },
    #     'tac_gia_id': {
    #         'label':'Tác giả',
    #         'query_factory': lambda: TacGia.query.all(),
    #         'get_label': 'ten_tac_gia',
    #         'allow_blank': False
    #     }
    # }
    #
    column_formatters = {
        'so_luong_cuon_con_lai': lambda v, c, m, p: (
                db.session.query(SoLuongCuonConLai.so_luong).filter(SoLuongCuonConLai.sach_id == m.id).order_by(
                    SoLuongCuonConLai.thoi_diem.desc()).first() or 'NaN'
        )
    }
    column_formatters_detail = {
        'bia_sach': lambda v, c, m, p: Markup(
            f'<img src="{m.bia_sach}" style="max-width: 200px; max-height: 150px;" alt="Bìa sách">'
        ) if m.bia_sach else Markup('<p>No Image</p>')
    }

    def on_model_change(self, form, model, is_created):
        file_data = form.bia_sach.data
        if file_data:

            if not file_data.content_type.startswith("image/"):
                raise ValueError("Chỉ được upload hình ảnh (JPEG, PNG, GIF, v.v.)")

            upload_result = cloudinary.uploader.upload(file_data, folder="upload/bia_sach")
            model.bia_sach = upload_result.get('secure_url')
        model.tac_gia_id = form.tac_gia_id.data
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

class UserForm(Form):
    ho = StringField('Họ', validators=[DataRequired()])
    ten = StringField('Tên', validators=[DataRequired()])
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    password = StringField('Mật khẩu', validators=[ DataRequired()])
    ngay_tao = DateTimeField('Ngày tạo', default=datetime.now(), format='%Y-%m-%d %H:%M:%S')
    avatar = FileField('Avatar', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], "Chỉ được phép upload file hình ảnh!")])
    vai_tro_id = QuerySelectField('Vai trò', query_factory=lambda: VaiTro.query.all(),
                              get_label='ten_vai_tro', allow_blank=False)

class UserView(AuthenticatedView):
    column_searchable_list = ['id','ho','ten','username']
    form_excluded_columns = ['phieu_nhap_sach','don_hang']
    can_edit = True
    can_create = True

    form = UserForm

    def create_form(self):
        form = super().create_form()
        return form
    def edit_form(self, obj):
        form = super().edit_form(obj)
        return form

    def on_model_change(self, form, model, is_created):
        model.ngay_tao = datetime.now()
        model.vai_tro_id = form.vai_tro_id.data.id
        file_data = form.avatar.data
        if file_data:

            if not file_data.content_type.startswith("image/"):
                raise ValueError("Chỉ được upload hình ảnh (JPEG, PNG, GIF, v.v.)")

            upload_result = cloudinary.uploader.upload(file_data, folder="upload/avatar")
            model.avatar = upload_result.get('secure_url')
        model.password = str(hashlib.md5(form.password.data.encode('utf-8')).hexdigest())

        return super().on_model_change(form, model, is_created)

    column_formatters_detail = {
        'avatar': lambda v, c, m, p: Markup(
            f'<img src="{m.avatar}" style="max-width: 200px; max-height: 150px;" alt="Bìa sách">'
        ) if m.avatar else Markup('<p>No Image</p>')
    }
    form_widget_args = {
        'avatar':{

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
        sachs = load_sach(ten_the_loai = ten_the_loai , ten_tac_gia = ten_tac_gia)



        return self.render("admin/booksimport.html",theloais = theloais,tacgias = tacgias,sachs=sachs)

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
            phieu_nhap = PhieuNhapSach(quan_ly_kho_id = current_user.get_id())
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

                    update_or_add_so_luong(so_luong = book["so_luong"],sach_id = sach.id)

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

class TrangThaiDonHang(AuthenticatedView):
    can_view_details = False
    can_delete = True
    can_create = True
    form_choices = {
        'ten_trang_thai': [
            ('Đã thanh toán', 'Đã thanh toán'),
            ('Chưa thanh toán', 'Chưa thanh toán')
        ]
    }


admin.add_view(SachView(Sach, db.session, name='Sách', category='Quản lý sách'))
admin.add_view(TheLoaiView(TheLoai, db.session, name='Thể loại', category='Quản lý sách'))
admin.add_view(TacGiaView(TacGia, db.session, name='Tác giả', category='Quản lý sách'))
admin.add_view(QuyDinhView(QuyDinh, db.session, name='Quy định'))
admin.add_view(UserView(User,db.session,name='Quản lý User'))
admin.add_view(VaitroView(VaiTro,db.session,name='Vai trò'))

admin.add_view(PhuongThucThanhToanView(PhuongThucThanhToan,db.session,name='Phương thức thanh toán'))

admin.add_view(NhapPhieuView(name="Nhập sách"))
admin.add_view(XemPhieuNhapSach(PhieuNhapSach,db.session,name="Xem Phiếu Nhập sách",category="XEM PHIẾU NHẬP"))
admin.add_view(XemPhieuNhapSach(ChiTietPhieuNhapSach,db.session,name="Xem Chi Tiết Phiếu",category="XEM PHIẾU NHẬP"))

admin.add_view(RevenueStatsView(name='Thống kê doanh thu', category='Thống kê báo cáo'))
admin.add_view(FrequencyStatsView(name='Thống kê tần suất', category='Thống kê báo cáo'))

admin.add_view(CashierView(name='Bán hàng'))

admin.add_view(Logout(name="Đăng xuất"))
