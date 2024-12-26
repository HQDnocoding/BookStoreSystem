from functools import wraps
from flask_login import current_user
from flask import redirect

from app.models import VaiTro


def annonymous_user(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect('/')
        return f(*args, **kwargs)

    return decorated_func


def login_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect('/')
        return f(*args, **kwargs)

    return decorated_func


def customer_login_required (f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        khach_hang = VaiTro.query.filter(VaiTro.ten_vai_tro.__eq__('KHACHHANG')).first()
        if not current_user.is_authenticated:
            return redirect('/')
        if current_user.vai_tro_id != khach_hang.id:
            return redirect('/')
        return f(*args, **kwargs)

    return decorated_func