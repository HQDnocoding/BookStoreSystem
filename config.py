# SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:%s@localhost/bookstoredb?charset=utf8mb4" % quote( "Admin@123")
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@127.0.0.1:3306/test_bookstore_db?charset=utf8mb4"  # Non_password_MySQL
SQLALCHEMY_TRACK_MODIFICATIONS = False
BABEL_DEFAULT_LOCALE = "vi"  # Đặt ngôn ngữ mặc định là tiếng Việt
PAGE_SIZE = 12
DEBUG = True
CART_KEY = "CART_KEY"
BOOK_IMPORT_CART_KEY = "BOOK_IMPORT_CART_KEY"

ENV = "production"  # hoặc "development", "production", "testing" v.v.
