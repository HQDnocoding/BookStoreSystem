import hashlib
from datetime import datetime
from email.policy import default
from xmlrpc.client import DateTime

import cloudinary.uploader
import flask_login
import wtforms
from flask_admin import Admin, BaseView, expose
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
from flask import redirect ,g
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


class AuthenticatedQuanLyKhoView(ModelView):
    def is_accessible(self):
        qlk = VaiTro.query.filter(VaiTro.ten_vai_tro.__eq__('QUANLYKHO')).first()
        return current_user.is_authenticated and current_user.vai_tro_id == qlk.id



class QuyDinhView(AuthenticatedView):
    can_create = True
    can_edit = True


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


class PhieuNhapSachForm(Form):
    ngay_nhap = DateTimeField('Ngày nhập', default=datetime.now(), format='%Y-%m-%d %H:%M:%S',
                              validators=[DataRequired()])

    # Trường này sẽ được tự động gán cho current_user.id khi tạo
    quan_ly_kho_id = QuerySelectField('Quản lý kho', query_factory=lambda: User.query.all(),
                              get_label='ten', allow_blank=False)



class PhieuNhapSachView(AuthenticatedQuanLyKhoView):
    column_list = ['id','quan_ly_kho_id','ngay_nhap']
    form_excluded_columns = ['sach']
    can_view_details = True
    column_searchable_list = ['id','quan_ly_kho_id']
    can_edit = False
    can_create = True


    form = PhieuNhapSachForm
    def create_form(self):
        form = super().create_form()
        form.ngay_nhap = datetime.now()
        form.quan_ly_kho_id.data = current_user.get_id()
        return form

    def on_model_change(self, form, model, is_created):
        if is_created:
            form.ngay_nhap = datetime.now()
            model.quan_ly_kho_id = current_user.get_id()
        super().on_model_change(form, model, is_created)

    form_widget_args = {
        'ngay_nhap':{
            'disabled' : True
        },
        'quan_ly_kho_id':{
            'disabled': True,
        }

    }
    column_labels = {
        'id': 'Mã phiếu',
        'quan_ly_kho_id': 'Mã người quản lý kho',
        'ngay_nhap': 'Ngày nhập'
    }


class ChiTietPhieuNhapSachView(AuthenticatedQuanLyKhoView):
    column_list = ['phieu_nhap_sach_id','sach_id','so_luong']
    column_labels = {
        'phieu_nhap_sach_id' : 'Mã phiếu nhập sách',
        'sach_id' : 'Sách',
        'so_luong' : 'số lượng'
    }
    form_widget_args = {
        'so_luong': {
            'min': 150,
            'step': 1
        }
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


admin.add_view(SachView(Sach, db.session, name='Sách', category='Quản lý sách'))
admin.add_view(TheLoaiView(TheLoai, db.session, name='Thể loại', category='Quản lý sách'))
admin.add_view(TacGiaView(TacGia, db.session, name='Tác giả', category='Quản lý sách'))
admin.add_view(QuyDinhView(QuyDinh, db.session, name='Quy định'))
admin.add_view(UserView(User,db.session,name='Quản lý User'))
admin.add_view(VaitroView(VaiTro,db.session,name='Vai trò'))

admin.add_view(PhieuNhapSachView(PhieuNhapSach,db.session,name='Phiếu nhập sách',category='Nhập sách'))#
admin.add_view(ChiTietPhieuNhapSachView(ChiTietPhieuNhapSach,db.session,name='Chi tiết nhập sách',category='Nhập sách'))

admin.add_view(RevenueStatsView(name='Thống kê doanh thu', category='Thống kê báo cáo'))
admin.add_view(FrequencyStatsView(name='Thống kê tần suất', category='Thống kê báo cáo'))

admin.add_view(Logout(name="Đăng xuất"))
