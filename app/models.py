from    datetime import date

from sqlalchemy import Column, Integer,Text, String,Date, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app import app,db


class QuyDinh(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenQuyDinh = Column(String(50), nullable=False, unique=True)
    noiDung=Column(Text,nullable=False)
    giaTri=Column(Integer,nullable=False,default=0)
    ngayTao=Column(Date,nullable=False)
    isActive=Column(Boolean,nullable=False,default=True)

if __name__=="__main__":
    with app.app_context():
        db.create_all()
        qd=QuyDinh(tenQuyDinh='Limit time for payment',
                   noiDung='Thời gian tối thiểu để khách hàng thanh toán cho đơn hàng, tính bằng giờ',
                   giaTri=48,
                   ngayTao=date.today())
        db.session.add(qd)
        db.session.commit()