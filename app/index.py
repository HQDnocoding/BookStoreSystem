import math

from flask import render_template, redirect, request, session, jsonify
from app import app, login, utils
from app.admin import *
import os
import app.dao as dao
from flask_login import login_user, logout_user
from enum import Enum


class Role(Enum):
    QUANLY = 'QUANLY'
    NHAN_VIEN = 'NHANVIEN'
    QUAN_LY_KHO = 'QUANLYKHO'
    KHACH_HANG = 'KHACHHANG'


@app.route("/")
def hello_world():
    return render_template('index.html')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id=user_id)


@app.route("/login-admin", methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')
    roles = [Role.QUANLY.value, Role.NHAN_VIEN.value, Role.QUAN_LY_KHO.value]
    user = dao.auth_user(username=username, password=password, roles=roles)
    if user:
        login_user(user)
    return redirect('/admin')


@app.route('/register/', methods=['get', 'post'])
def register():
    err_msg = ''
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        if password.__eq__(confirm):
            # avatar
            avatar = ''
            if request.files.get('avatar'):
                res = cloudinary.uploader.upload(request.files.get('avatar'))
                avatar = res.get('secure_url')

            # save user
            try:
                if dao.user_exists(request.form['username']):
                    err_msg = 'Tài khoản đã tồn tại'
                else:
                    dao.create_user(ten=request.form['firstname'],
                                    ho=request.form['lastname'],
                                    username=request.form['username'],
                                    password=password,
                                    avatar=avatar,
                                    vai_tro=Role.KHACH_HANG.value)
                    return redirect('/login')
            except:
                err_msg = 'Hệ thống có lỗi'
        else:
            err_msg = 'mật khẩu KHÔNG khớp'
    return render_template("register.html", err_msg=err_msg)


@app.route('/login/', methods=['get', 'post'])
# @annonymous_user
def login_my_user():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form['username']
        password = request.form['password']
        user = dao.auth_user(username, password)
        if user:
            login_user(user=user)
            return redirect('/')
        else:
            if not dao.user_exists(request.form['username']):
                err_msg = 'Tài khoản KHÔNG tồn tại'
            else:
                err_msg = 'SAI mật khẩu'
    return render_template("login.html", err_msg=err_msg)


@app.route('/logout/')
def logout_my_user():
    logout_user()
    return redirect('/login')


@app.route('/shop/')
def shopping():
    the_loai = dao.get_the_loai()

    the_loai_id = request.args.get('the_loai_id', 1)
    kw = request.args.get('kw')
    page = request.args.get('page', 1)

    prods = dao.load_products(cate_id=the_loai_id, kw=kw, page=int(page))

    page_size = app.config.get('PAGE_SIZE', 2)
    total = dao.count_sach()

    return render_template('shop.html', products=prods, pages=math.ceil(total / page_size), cates=the_loai)


@app.route('/search/')
def search():
    the_loai = dao.get_the_loai()

    the_loai_id = request.args.get('the_loai_id', 1)
    kw = request.args.get('kw')

    page = request.args.get('page', 1)

    prods = dao.load_products(cate_id=the_loai_id, kw=kw, page=int(page))

    page_size = app.config.get('PAGE_SIZE', 2)
    total = dao.count_sach()

    return render_template('search_results.html', products=prods, pages=math.ceil(total / page_size), cates=the_loai)


@app.route('/books/<int:sach_id>')
def details(sach_id):
    sach = dao.get_sach_for_detail_by_id(sach_id)
    return render_template('book_details.html', sach=sach)


@app.route('/cart/')
def cart():
    return render_template('cart.html')


@app.route('/api/cart', methods=['post'])
def add_to_cart():

    data = request.json
    id = str(data['id'])

    key = app.config['CART_KEY']
    cart = session[key] if key in session else {}
    if id in cart:
        cart[id]['so_luong']+=1
    else:
        ten_sach = data['ten_sach']
        don_gia = data['don_gia']
        bia_sach = data['bia_sach']

        cart[id] = {
            "id": id,
            "ten_sach": ten_sach,
            "don_gia": don_gia,
            "so_luong": 1,
            "bia_sach": bia_sach
        }

    session[key] = cart
    return jsonify(utils.cart_stats(cart=cart))


@app.route('/api/cart/<product_id>', methods=['put'])
def update_cart(product_id):
    key = app.config['CART_KEY']
    cart = session.get(key)

    if cart and product_id in cart:
        cart[product_id]['so_luong'] = int(request.json['so_luong'])

    session[key] = cart

    return jsonify(utils.cart_stats(cart=cart))


@app.route('/api/cart/<product_id>', methods=['delete'])
def delete_cart(product_id):
    key = app.config['CART_KEY']
    cart = session.get(key)

    if cart and product_id in cart:
        del cart[product_id]

    session[key] = cart

    return jsonify(utils.cart_stats(cart=cart))


@app.context_processor
def common_attr():
    return {
        'cart': utils.cart_stats(session.get(app.config['CART_KEY']))
    }

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
