# SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:%s@localhost/bookstoredb?charset=utf8mb4" % quote( "Admin@123")
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@127.0.0.1:3306/test_bookstore_db?charset=utf8mb4"  # Non_password_MySQL
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_POOL_SIZE = 20  # Số kết nối tối đa trong pool
SQLALCHEMY_POOL_TIMEOUT = 30  # Thời gian chờ tối đa (giây)
SQLALCHEMY_POOL_RECYCLE = 280  # Tái sử dụng kết nối sau 280s

BABEL_DEFAULT_LOCALE = "vi"  # Đặt ngôn ngữ mặc định là tiếng Việt
PAGE_SIZE = 12
DEBUG = True
CART_KEY = "CART_KEY"
BOOK_IMPORT_CART_KEY = "BOOK_IMPORT_CART_KEY"

ENV = "production"  # hoặc "development", "production", "testing" v.v.
