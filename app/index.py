from flask import render_template, redirect, request, session ,jsonify
from app import app ,login
from app.admin import *
import os
import app.dao as dao
from flask_login import login_user, logout_user




@app.route("/")
def hello_world():
    return 'Hello world'

@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id=user_id)

@app.route("/login-admin", methods=['post'])
def login_admin_process():
    username=request.form.get('username')
    password=request.form.get('password')

    user=dao.auth_user(username=username,password=password,role='QUANLY')
    if user:
        login_user(user)
    else:
        user=dao.auth_user(username=username,password=password,role='QUANLYKHO')
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
            err_msg='mật khẩu KHÔNG khớp'
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
            return redirect('/register')

    return render_template("login.html")


@app.route('/logout/')
def logout_my_user():
    logout_user()
    return redirect('/login')


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
