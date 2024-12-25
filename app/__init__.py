from enum import Enum

from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_login import LoginManager
from flask_babel import Babel
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

app = Flask(__name__)
app.secret_key = "##%#%FGE~EBb$enb?jn##3323290!!@vdv;vd.;ư"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/bookstoredb?charset=utf8mb4" % quote( "Admin@123")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['BABEL_DEFAULT_LOCALE'] = 'vi'  # Đặt ngôn ngữ mặc định là tiếng Việt
app.config["PAGE_SIZE"] = 6
app.config['DEBUG'] = True
app.config['CART_KEY'] = 'cart'


# VNPAY thông tin cấu hình
VNPAY_MERCHANT_ID = 'BGJVFP3Z'
VNPAY_API_KEY = '9JVDXL67YUMV3I01HKS36KAPKQCL7TN5'
VNPAY_PAYMENT_URL = 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'  # URL thanh toán VNPAY Sandbox
VNPAY_RETURN_URL = 'https://huymanhdatbookstoresystemcnpm.loca.lt/vnpay_return'  # URL trả về sau khi thanh toán
class PayingMethod(Enum):
    ONLINE_PAY = 'ONLINE_PAY'
    OFFLINE_PAY = 'OFFLINE_PAY'


class Status(Enum):
    "Dành cho đơn hàng online"
    PAID = 'PAID'  # đã trả tiền
    WAITING = 'WAITING'  # đang đợi trả tiền
    FAIL = 'FAIL'  # hủy vì hết thời gian trả

babel = Babel(app)

cloudinary.config(
    cloud_name="dmbvjjg5a",
    api_key="463513198463353",
    api_secret="HsIK1yhx7av6BeoVqVjKKVceikY",  # Click 'View API Keys' above to copy your API secret
    secure=True
)

db = SQLAlchemy(app=app)

admin = Admin(app=app, name='Quản trị hệ thống nhà sách', template_mode='bootstrap4')

login = LoginManager(app=app)


class Role(Enum):
    QUANLY = 'QUANLY'
    NHAN_VIEN = 'NHANVIEN'
    QUAN_LY_KHO = 'QUANLYKHO'
    KHACH_HANG = 'KHACHHANG'


class PayingMethod(Enum):
    ONLINE_PAY = 'ONLINE_PAY'
    OFFLINE_PAY = 'OFFLINE_PAY'


class Status(Enum):
    "Dành cho đơn hàng online"
    PAID = 'PAID'  # đã trả tiền
    WAITING = 'WAITING'  # đang đợi trả tiền
    FAIL = 'FAIL'  # hủy vì hết thời gian trả

class Rule(Enum):

        SL_NHAP_MIN='SL_NHAP_MIN'
        SL_MIN_TO_NHAP='SL_MIN_TO_NHAP'
        OUT_OF_TIME_TO_PAY='OUT_OF_TIME_TO_PAY'

@app.template_filter('format_currency')
def format_currency(value):
    return f"{value:,.0f}"

class Rule(Enum):

    SL_NHAP_MIN='SL_NHAP_MIN'
    SL_MIN_TO_NHAP='SL_MIN_TO_NHAP'
    OUT_OF_TIME_TO_PAY='OUT_OF_TIME_TO_PAY'