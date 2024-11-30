import cloudinary.uploader
import wtforms
from flask_admin import Admin, BaseView, expose
from app import admin, db
from flask_admin.contrib.sqla import ModelView

from app.dao import get_role_name_by_role_id
from app.models import Sach, QuyDinh, SoLuongCuonConLai, TacGia, TheLoai
from flask_login import current_user, logout_user
from flask import redirect
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

class AuthenticatedQuanLyKhoView(BaseView):
    def is_accessible(self):
        qlk = VaiTro.query.filter(VaiTro.ten_vai_tro.__eq__('QUANLYKHO')).first()
        return current_user.is_authenticated and current_user.vai_tro_id == qlk.id



class QuyDinhView(AuthenticatedView):
    can_create = True
    can_edit = True


class StatsView(MyView):
    @expose("/")
    def index(self):
        return self.render("admin/stats.html")


class Logout(MyView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect("/admin")


#


class SachForm(Form):
    ten_sach = StringField('Tên sách', validators=[DataRequired()])
    don_gia = StringField('Đơn giá', validators=[DataRequired()])
    tac_gia_id = SelectField('Tác giả', coerce=int, validators=[DataRequired()])
    the_loai_id = SelectField('Thể loại', coerce=int, validators=[DataRequired()])
    bia_sach = FileField('Bìa sách', validators=[
        DataRequired(),FileAllowed(['jpg', 'jpeg', 'png', 'gif'], "Chỉ được phép upload file hình ảnh!") ])


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

class NhapSach(AuthenticatedQuanLyKhoView):
    @expose("/")
    def index(self):
        return self.render("admin/bookimport.html")



admin.add_view(SachView(Sach, db.session, name='Sách', category='Quản lý sách'))
admin.add_view(TheLoaiView(TheLoai, db.session, name='Thể loại', category='Quản lý sách'))
admin.add_view(TacGiaView(TacGia, db.session, name='Tác giả', category='Quản lý sách'))
admin.add_view(QuyDinhView(QuyDinh, db.session, name='Quy định'))

admin.add_view(NhapSach(name='Nhập sách'))

admin.add_view(StatsView(name='Thống kê doanh thu', category='Thống kê báo cáo'))
admin.add_view(Logout(name="Đăng xuất"))
