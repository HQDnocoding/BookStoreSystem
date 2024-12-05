from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_login import LoginManager
from flask_babel import Babel
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

app=Flask(__name__)
app.secret_key="##%#%FGE~EBb$enb?jn##3323290!!@vdv;vd.;ư"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/bookstoredb?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['BABEL_DEFAULT_LOCALE'] = 'vi'  # Đặt ngôn ngữ mặc định là tiếng Việt
app.config["PAGE_SIZE"] = 4
app.config['DEBUG'] = True

babel = Babel(app)


cloudinary.config(
    cloud_name = "dmbvjjg5a",
    api_key = "463513198463353",
    api_secret = "HsIK1yhx7av6BeoVqVjKKVceikY", # Click 'View API Keys' above to copy your API secret
    secure=True
)



db=SQLAlchemy(app=app)

admin=Admin(app=app,name='Quản trị hệ thống nhà sách',template_mode='bootstrap4')

login=LoginManager(app=app)