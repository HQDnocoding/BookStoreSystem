from flask import render_template, redirect, request, session ,jsonify
from app import app ,login
from app.admin import *
import os
import app.dao as dao
from flask_login import login_user, logout_user




@app.route("/")
def hello_world():
    return "Hello World"

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
    return redirect('/admin')



if __name__ == "__main__":
    with app.app_context():

        app.run(debug=True)
