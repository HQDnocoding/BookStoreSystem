import hmac
import math
import urllib

import random
from datetime import timedelta

from flask import render_template, redirect, request, session, jsonify
from app import app, login, utils, VNPAY_MERCHANT_ID, VNPAY_RETURN_URL, VNPAY_API_KEY, VNPAY_PAYMENT_URL
from app.admin import *
import app.dao as dao
from flask_login import login_user, logout_user
from app import Role
from decorators import annonymous_user, login_required





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
@annonymous_user
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
@annonymous_user
def login_my_user():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form['username']
        password = request.form['password']
        user = dao.auth_user(username, password)
        if user:
            login_user(user=user)
            n=request.args.get('next')
            return redirect(n if n else '/')
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

    # Lấy số lượng từ dữ liệu JSON, mặc định là 1 nếu không có số lượng được cung cấp
    so_luong_moi = data.get('so_luong', 1)

    key = app.config['CART_KEY']
    cart = session[key] if key in session else {}
    if id in cart:
        cart[id]['so_luong']+=so_luong_moi
    else:
        ten_sach = data['ten_sach']
        don_gia = data['don_gia']
        bia_sach = data['bia_sach']

        cart[id] = {
            "id": id,
            "ten_sach": ten_sach,
            "don_gia": don_gia,
            "so_luong": so_luong_moi,
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
#class vnpay để thanh toán online code mẫu dijango của VNPAY
class vnpay:
    requestData = {}
    responseData = {}

    def get_payment_url(self, vnpay_payment_url, secret_key):
        inputData = sorted(self.requestData.items())
        queryString = ''
        hasData = ''
        seq = 0
        for key, val in inputData:
            if seq == 1:
                queryString = queryString + "&" + key + '=' + urllib.parse.quote_plus(str(val))
            else:
                seq = 1
                queryString = key + '=' + urllib.parse.quote_plus(str(val))

        hashValue = self.__hmacsha512(secret_key, queryString)
        return vnpay_payment_url + "?" + queryString + '&vnp_SecureHash=' + hashValue

    def validate_response(self, secret_key):
        vnp_SecureHash = self.responseData['vnp_SecureHash']
        # Remove hash params
        if 'vnp_SecureHash' in self.responseData.keys():
            self.responseData.pop('vnp_SecureHash')

        if 'vnp_SecureHashType' in self.responseData.keys():
            self.responseData.pop('vnp_SecureHashType')

        inputData = sorted(self.responseData.items())
        hasData = ''
        seq = 0
        for key, val in inputData:
            if str(key).startswith('vnp_'):
                if seq == 1:
                    hasData = hasData + "&" + str(key) + '=' + urllib.parse.quote_plus(str(val))
                else:
                    seq = 1
                    hasData = str(key) + '=' + urllib.parse.quote_plus(str(val))
        hashValue = self.__hmacsha512(secret_key, hasData)

        print(
            'Validate debug, HashData:' + hasData + "\n HashValue:" + hashValue + "\nInputHash:" + vnp_SecureHash)

        return vnp_SecureHash == hashValue

    @staticmethod
    def __hmacsha512(key, data):
        byteKey = key.encode('utf-8')
        byteData = data.encode('utf-8')
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest() #



@app.route('/payment/')
@login_required
def payment():
    return render_template('payment.html')





@app.route('/process_payment', methods=['post'])
def process_payment():
    vnp = vnpay()
    vnp.requestData['vnp_Version'] = '2.1.0'
    vnp.requestData['vnp_Command'] = 'pay'
    vnp.requestData['vnp_TmnCode'] = VNPAY_MERCHANT_ID
    vnp.requestData['vnp_Amount'] = 25000 * 100
    vnp.requestData['vnp_CurrCode'] = 'VND'
    vnp.requestData['vnp_TxnRef'] = str(random.randint(100000, 999999))
    vnp.requestData['vnp_OrderInfo'] = 'Thanh toan'
    vnp.requestData['vnp_OrderType'] = 'other'
    vnp.requestData['vnp_Locale'] = 'vn'
    vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
    vnp.requestData['vnp_IpAddr'] = request.remote_addr
    vnp.requestData['vnp_ReturnUrl'] = VNPAY_RETURN_URL
    vnpay_payment_url = vnp.get_payment_url(VNPAY_PAYMENT_URL, VNPAY_API_KEY)
    print(vnpay_payment_url)
    return redirect(vnpay_payment_url)



@app.route('/vnpay_return', methods=['get'])
def payment_return():
    input_data = request.args # Lấy dữ liệu từ query string
    if input_data:
        vnp = vnpay()
        vnp.responseData = input_data.to_dict()  # Chuyển đổi thành dictionary
        order_id = input_data.get('vnp_TxnRef')
        amount = int(input_data.get('vnp_Amount', 0)) / 100
        order_desc = input_data.get('vnp_OrderInfo')
        vnp_transaction_no = input_data.get('vnp_TransactionNo')
        vnp_response_code = input_data.get('vnp_ResponseCode')
        vnp_tmn_code = input_data.get('vnp_TmnCode')
        vnp_pay_date = input_data.get('vnp_PayDate')
        vnp_bank_code = input_data.get('vnp_BankCode')
        vnp_card_type = input_data.get('vnp_CardType')

        # Validate response
        if vnp.validate_response(VNPAY_API_KEY):
            if vnp_response_code == "00":
                return redirect(url_for('payment_succeed'))  # Chuyển hướng đến trang thành công
            else:
                return redirect(url_for('payment_failed'))  # Chuyển hướng đến trang thất bại
    return "Invalid request", 400

@app.route('/payment_succeed')
def payment_succeed():
    return "Payment succeeded!"

@app.route('/payment_failed')
def payment_failed():
    return "Payment failed!"


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True,port=5001)
