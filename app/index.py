import math

from flask import render_template, redirect, request, session ,jsonify
from app import app ,login
from app.admin import *
import os
import app.dao as dao
from flask_login import login_user, logout_user




@app.route("/")
def hello_world():
    return render_template('index.html')

@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id=user_id)

@app.route("/login-admin", methods=['post'])
def login_admin_process():
    username=request.form.get('username')
    password=request.form.get('password')
    roles=['NHANVIEN','QUANLY','QUANLYKHO']
    user=dao.auth_user(username=username,password=password,roles=roles)
    if user:
        login_user(user)
    return redirect('/admin')


@app.route('/register/', methods=['get','post'])
def register():
    err_msg=''
    if request.method.__eq__('POST'):
        password = request.form['password']
        confirm = request.form['confirm']
        if password.__eq__(confirm):
            #avatar
            avatar=''
            if request.files['avatar']:
                res=cloudinary.uploader.upload(request.files['avatar'])
                avatar = res['secure_url']

            #save user
            try:
                dao.create_user(ten=request.form['firstname'],
                                ho=request.form['lastname'],
                             username=request.form['username'],
                             password=request.form['password'],
                             avatar=avatar,
                                vaitro_id=4)
                return redirect('/login')
            except:
                err_msg='Hệ thống có lỗi'
        else:
            err_msg='mật khẩu không khớp'
    return render_template("register.html", err_msg=err_msg)


@app.route('/login/', methods=['get','post'])
# @annonymous_user
def login_my_user():
    if request.method.__eq__('POST'):
        username = request.form['username']
        password = request.form['password']
        user = dao.auth_user(username, password)
        if user:
            login_user(user=user)
            return redirect('/')

    return render_template("login.html")


@app.route('/logout/')
def logout_my_user():
    logout_user()
    return redirect('/login')



@app.route('/shop/')
def shopping():
    the_loai=dao.get_the_loai()

    the_loai_id=request.args.get('the_loai_id',1)
    kw=request.args.get('kw')
    page=request.args.get('page',1)

    prods=dao.load_products(cate_id=the_loai_id,kw=kw,page=int(page))

    page_size=app.config.get('PAGE_SIZE',2)
    total=dao.count_sach()

    return render_template('shop.html',products=prods,pages=math.ceil(total/page_size),cates=the_loai)

@app.route('/search/')
def search():
    the_loai=dao.get_the_loai()

    the_loai_id=request.args.get('the_loai_id',1)
    kw=request.args.get('kw')

    page=request.args.get('page',1)

    prods=dao.load_products(cate_id=the_loai_id,kw=kw,page=int(page))

    page_size=app.config.get('PAGE_SIZE',2)
    total=dao.count_sach()

    return render_template('search_results.html',products=prods,pages=math.ceil(total/page_size),cates=the_loai)



if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
