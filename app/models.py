import datetime
import hashlib
from datetime import date

from sqlalchemy import Column, Integer, Text, String, DateTime, Float, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from app import app as my_app, db
from flask_login import UserMixin


class VaiTro(db.Model):
    __tablename__ = 'vai_tro'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_vai_tro = Column(String(50), nullable=True, unique=True)
    user = relationship('User', backref='vai_tro', lazy=True)

    # def __int__(self):
    #     return int(self.id)

class QuyDinh(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_quy_dinh = Column(String(50), nullable=False, unique=True)
    noi_dung = Column(Text, nullable=False)
    gia_tri = Column(Integer, nullable=False, default=0)
    ngay_tao = Column(DateTime, nullable=False, default=datetime.now())
    is_active = Column(Boolean, nullable=False, default=True)


class TacGia(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_tac_gia = Column(String(225), nullable=False)
    sach = relationship('Sach', backref='tac_gia', lazy=True)

    def __str__(self):
        return self.ten_tac_gia


class TheLoai(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_the_loai = Column(String(225), nullable=False, unique=True)
    sach = relationship('Sach', backref='the_loai', lazy=True)

    def __str__(self):
        return self.ten_the_loai


class TrangThaiDonHang(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_trang_thai = Column(String(50), nullable=False)

    don_hang = relationship('DonHang', backref='trang_thai_don_hang', lazy=True)


class PhuongThucThanhToan(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_phuong_thuc = Column(String(50), nullable=False)

    don_hang = relationship('DonHang', backref='phuong_thuc_thanh_toan', lazy=True)


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ho = Column(String(50), nullable=False)
    ten = Column(String(50), nullable=False)
    username = Column(String(225), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    ngay_tao = Column(DateTime, nullable=False, default=datetime.now())
    avatar = Column(String(225))
    vai_tro_id = Column(Integer, ForeignKey(VaiTro.id), nullable=False)
    phieu_nhap_sach = relationship('PhieuNhapSach', backref='user', lazy=True)
    don_hang = relationship('DonHang', backref='user', lazy=True)
    hoa_don_ban_sach=relationship('HoaDonBanSach',backref='user',lazy=True)
    def __str__(self):
        return self.ten

class HoaDonBanSach(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ngay_tao_hoa_don = Column(DateTime, nullable=False, default=datetime.now())

    nhan_vien = Column(Integer, ForeignKey(User.id), nullable=True)
    sach = relationship('ChiTietHoaDon', backref='hoa_don_ban_sach')


class Sach(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_sach = Column(String(100), nullable=False)
    don_gia = Column(Float, nullable=False)
    bia_sach = Column(String(225))

    the_loai_id = Column(Integer, ForeignKey(TheLoai.id), nullable=False)
    tac_gia_id = Column(Integer, ForeignKey(TacGia.id), nullable=False)

    hoa_don_ban_sach = relationship('ChiTietHoaDon', backref='sach')
    so_luong_cuon_con_lai = relationship('SoLuongCuonConLai', backref='sach', lazy=True)
    phieu_nhap_sach = relationship('ChiTietPhieuNhapSach', backref='sach')
    don_hang = relationship('ChiTietDonHang', backref='sach')

    def __str__(self):
        return self.ten_sach

class ChiTietHoaDon(db.Model):
    sach_id = Column(ForeignKey(Sach.id), primary_key=True)
    hoa_don_id = Column(ForeignKey(HoaDonBanSach.id), primary_key=True)
    so_luong = Column(Integer, nullable=False)
    tong_tien = Column(Float, nullable=False)


class SoLuongCuonConLai(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    so_luong = Column(Integer, nullable=False)
    thoi_diem = Column(DateTime, nullable=False, default=datetime.now())

    sach_id = Column(Integer, ForeignKey(Sach.id), nullable=False)

    def __int__(self):
        return self.so_luong


# class ChiTietChinhSuaQuyDinh(db.Model):
#     quy_dinh_id=Column(Integer,ForeignKey(QuyDinh.id),primary_key=True)
#     user_id=Column(Integer,ForeignKey(User.id),primary_key=True)
#
#     thoi_diem_chinh_sua=Column  (DateTime,nullable=False,default=datetime.now())


class PhieuNhapSach(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ngay_nhap = Column(DateTime, nullable=False, default=datetime.now())

    quan_ly_kho_id = Column(Integer, ForeignKey(User.id), nullable=False)
    sach = relationship('ChiTietPhieuNhapSach', backref='phieu_nhap_sach')

    def __int__(self):
         return self.id

class ChiTietPhieuNhapSach(db.Model):
    phieu_nhap_sach_id = Column(Integer, ForeignKey(PhieuNhapSach.id),
                                primary_key=True)
    sach_id = Column(Integer, ForeignKey(Sach.id), primary_key=True)

    so_luong = Column(Integer, nullable=False)




class DonHang(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ngay_tao_don = Column(DateTime, nullable=False, default=datetime.now())

    phuong_thuc_id = Column(Integer, ForeignKey(PhuongThucThanhToan.id), nullable=False)
    trang_thai_id = Column(Integer, ForeignKey(TrangThaiDonHang.id), nullable=False)
    khach_hang_id = Column(Integer, ForeignKey(User.id), nullable=False)
    thong_tin_nhan_hang = relationship('ThongTinNhanHang', uselist=False, backref='don_hang')
    sach = relationship('ChiTietDonHang', backref='don_hang')


class ThongTinNhanHang(db.Model):
    id = Column(Integer, ForeignKey(DonHang.id), primary_key=True)
    dien_thoai_nhan_hang = Column(String(50), nullable=False)
    dia_chi_nhan_hang = Column(String(225), nullable=False)


class ChiTietDonHang(db.Model):
    don_hang_id = Column(Integer, ForeignKey(DonHang.id),
                         primary_key=True)
    sach_id = Column(Integer, ForeignKey(Sach.id), primary_key=True)

    so_luong = Column(Integer, nullable=False, default=0)
    tong_tien = Column(Integer, nullable=False, default=0)






if __name__ == "__main__":
    with my_app.app_context():
        
        # db.drop_all()
        db.create_all()

        db.session.commit()
        #
        # vt1=VaiTro(ten_vai_tro='QUANLY')
        # vt2=VaiTro(ten_vai_tro='NHANVIEN')
        # vt3=VaiTro(ten_vai_tro='QUANLYKHO')
        # vt4=VaiTro(ten_vai_tro='KHACHHANG')
        # db.session.add_all([vt1,vt2,vt3,vt4])
        #
        # # db.session.query(User).delete()
        #
        # pw = str(hashlib.md5('123'.encode('utf-8')).hexdigest())
        #
        # admin=User(ho='Hứa',ten="Hứa",username='admin',password=pw,vai_tro_id=1)
        # nhan_vien=User(ho='Trump',ten='Donald',username='nhanvien',password=pw,vai_tro_id=2)
        # qlk=User(ho='Trump',ten='Donald',username='qlk',password=pw,vai_tro_id=3)
        # u=User(ho='Trump',ten='Donald',username='client',password=pw,vai_tro_id=4)
        #
        # db.session.add_all([admin,nhan_vien,qlk,u])
        #
        #
        # pt1=PhuongThucThanhToan(ten_phuong_thuc='ONLINE')
        # pt2=PhuongThucThanhToan(ten_phuong_thuc='AT_STORE')
        # tt0=TrangThaiDonHang(ten_trang_thai='SHOPPING')
        # tt1=TrangThaiDonHang(ten_trang_thai='PAYING')
        # tt2=TrangThaiDonHang(ten_trang_thai='PAID')
        # tt3=TrangThaiDonHang(ten_trang_thai='CANCELED')
        # qlk = User(ho='Le', ten="Huy", username='quanlykho', password=pw, vai_tro_id=3)
        # db.session.add(qlk)
        # db.session.commit()
