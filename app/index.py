import hmac
import math
import random
import urllib
from enum import Enum

from flask import jsonify, redirect, render_template, request, session
from flask_login import current_user, login_user, logout_user

import app.dao as dao
from app import (VNPAY_API_KEY, VNPAY_MERCHANT_ID, VNPAY_PAYMENT_URL,
                 VNPAY_RETURN_URL, PayingMethod, Role, Rule, Status, app,
                 login, utils)
from app.admin import *
from app.decorators import customer_login_required
from app.utils import (cart_stats, check_if_expire_orders,
                       update_so_luong_by_ct_don_hang)

# from decorators import annonymous_user, login_required


class Role(Enum):
    QUANLY = "QUANLY"
    NHAN_VIEN = "NHANVIEN"
    QUAN_LY_KHO = "QUANLYKHO"
    KHACH_HANG = "KHACHHANG"


@app.route("/")
def hello_world():
    return render_template("index.html")


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id=user_id)


@app.route("/login-admin", methods=["post"])
def login_admin_process():
    username = request.form.get("username")
    password = request.form.get("password")
    roles = [Role.QUANLY.value, Role.NHAN_VIEN.value, Role.QUAN_LY_KHO.value]
    user = dao.auth_user(username=username, password=password, roles=roles)
    if user:
        login_user(user)
    return redirect("/admin")


@app.route("/register/", methods=["get", "post"])
# @annonymous_user
def register():
    err_msg = ""
    if request.method.__eq__("POST"):
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        if password.__eq__(confirm):
            # avatar
            avatar = ""
            if request.files.get("avatar"):
                res = cloudinary.uploader.upload(request.files.get("avatar"))
                avatar = res.get("secure_url")

            # save user
            try:
                if dao.user_exists(request.form["username"]):
                    err_msg = "Tài khoản đã tồn tại"
                else:
                    dao.create_user(
                        ten=request.form["firstname"],
                        ho=request.form["lastname"],
                        username=request.form["username"],
                        password=password,
                        avatar=avatar,
                        vai_tro=Role.KHACH_HANG.value,
                    )
                    return redirect("/login")
            except:
                err_msg = "Hệ thống có lỗi"
        else:
            err_msg = "mật khẩu KHÔNG khớp"
    return render_template("register.html", err_msg=err_msg)


@app.route("/login/", methods=["GET", "POST"])
# @annonymous_user
def login_my_user():
    err_msg = ""
    success_msg = request.args.get("success_msg")
    if request.method.__eq__("POST"):
        print("POST request received")
        print(f"Form data: {request.form}")
        print(f"Username from form: {request.form.get('username', 'NOT FOUND')}")
        print(f"Password from form: {request.form.get('password', 'NOT FOUND')}")

        success_msg = ""
        username = request.form["username"]
        password = request.form["password"]
        user = dao.auth_user(username, password)
        if user:
            login_user(user=user)
            next_page = request.args.get("next")
            return redirect(next_page if next_page else "/")
        else:
            if not dao.user_exists(username):
                err_msg = "Tài khoản KHÔNG tồn tại"
            else:
                err_msg = "SAI mật khẩu"
    return render_template("login.html", err_msg=err_msg, success_msg=success_msg)


@app.route("/logout/")
def logout_my_user():
    logout_user()
    return redirect("/login")


@app.route("/update_password/", methods=["get", "post"])
def update_password():
    err_msg = ""
    if request.method.__eq__("POST"):
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        confirm = request.form["confirm"]
        if not new_password.__eq__(confirm):
            err_msg = "Mật khẩu KHÔNG khớp"
            return render_template("update_password.html", err_msg=err_msg)
        if old_password.__eq__(new_password):
            err_msg = "Mật khẩu mới phải KHÁC mật khẩu cũ "
            return render_template("update_password.html", err_msg=err_msg)
        user = dao.auth_user(current_user.username, old_password)

        if user:
            update_user_password(current_user.id, new_password)
            logout_user()
            return redirect(
                "/login?success_msg=Đã đổi mật khẩu thành công, vui lòng đăng nhập"
            )
        else:
            err_msg = "SAI mật khẩu"
    return render_template("update_password.html", err_msg=err_msg)


@app.route("/profile/")
@login_required
def profile():
    user = get_user_by_id(current_user.get_id())

    return render_template("profile.html", user=user)


@app.route("/shop", defaults={"cate": "None"}, strict_slashes=False)
@app.route("/shop/<cate>", strict_slashes=False)
def shopping(cate):
    the_loai = dao.get_the_loai()
    kw = request.args.get("kw", "")

    sort = False if kw else True

    print(f"kw: {kw}")
    page = request.args.get("page", 1, type=int)
    sort_by = request.args.get("sort_by", "")
    if cate is not None:
        the_loai_id = dao.get_id_the_loai(cate)
        prods = dao.load_products(
            cate_id=the_loai_id, kw=kw, page=page, sort_by=sort_by
        )
        total = dao.count_sach(kw=kw, the_loai_id=the_loai_id)
    else:
        prods = dao.load_products(kw=kw, page=page, sort_by=sort_by)
        total = dao.count_sach(kw=kw)

    page_size = app.config.get("PAGE_SIZE", 2)
    return render_template(
        "shop.html",
        products=prods,
        pages=math.ceil(total / page_size),
        cates=the_loai,
        kw=kw,
        sort_by=sort_by,
        the_loais=the_loai,
        count=total,
        sort=sort,
    )


@app.route("/search/")
def search():
    the_loai = dao.get_the_loai()

    the_loai_id = request.args.get("the_loai_id", 1)
    kw = request.args.get("kw")

    page = request.args.get("page", 1)

    prods = dao.load_products(cate_id=the_loai_id, kw=kw, page=int(page))

    page_size = app.config.get("PAGE_SIZE", 2)
    total = dao.count_sach()

    return render_template(
        "search_results.html",
        products=prods,
        pages=math.ceil(total / page_size),
        cates=the_loai,
    )


@app.route("/filter/")
def filter_genre():
    pass


@app.route("/books/<int:sach_id>")
def details(sach_id):
    sach = Sach.query.get(sach_id)
    return render_template(
        "book_details.html", sach=sach, comments=dao.load_comments(sach_id)
    )


@app.route("/api/books/<int:sach_id>/comments", methods=["post"])
def add_comment(sach_id):
    content = request.json.get("content")

    c = dao.create_comment(content, sach_id, current_user)

    return jsonify(
        {
            "content": c.content,
            "ngay_tao": c.ngay_tao,
            "user": {
                "avatar": c.user.avatar,
                "ho": c.user.ho,
                "ten": c.user.ten,
            },
        }
    )


@app.route("/cart/")
def cart():
    return render_template("cart.html")


@app.route("/api/cart", methods=["post"])
def add_to_cart():
    data = request.json
    id = str(data["id"])

    # Lấy số lượng từ dữ liệu JSON, mặc định là 1 nếu không có số lượng được cung cấp
    so_luong_moi = data.get("so_luong", 1)

    key = app.config["CART_KEY"]
    cart = session[key] if key in session else {}

    if id in cart:
        if cart[id]["so_luong"] + so_luong_moi > data["so_luong_con_lai"]:
            response = utils.cart_stats(cart=cart)
            response["alert"] = " KHÔNG đủ sách để mua "
            return jsonify(response)
        cart[id]["so_luong"] += so_luong_moi
    else:
        if so_luong_moi > data["so_luong_con_lai"]:
            response = utils.cart_stats(cart=cart)
            response["alert"] = " Đã HẾT sách."
            return jsonify(response)
        ten_sach = data["ten_sach"]
        don_gia = data["don_gia"]
        bia_sach = data["bia_sach"]
        so_luong_con_lai = data["so_luong_con_lai"]

        cart[id] = {
            "id": id,
            "ten_sach": ten_sach,
            "don_gia": don_gia,
            "so_luong": so_luong_moi,
            "bia_sach": bia_sach,
            "so_luong_con_lai": so_luong_con_lai,
        }

    session[key] = cart
    return jsonify(utils.cart_stats(cart=cart))


@app.route("/api/cart/<product_id>", methods=["put"])
def update_cart(product_id):
    data = request.json
    key = app.config["CART_KEY"]
    cart = session.get(key)

    if cart and product_id in cart:

        if int(data["so_luong"]) > cart[product_id]["so_luong_con_lai"]:
            response = utils.cart_stats(cart=cart)
            response["old_quantity"] = cart[product_id]["so_luong"]
            response["p_id"] = product_id
            return jsonify(response)

        cart[product_id]["so_luong"] = int(data["so_luong"])

    session[key] = cart

    return jsonify(utils.cart_stats(cart=cart))


@app.route("/api/cart/<product_id>", methods=["delete"])
def delete_cart(product_id):
    key = app.config["CART_KEY"]
    cart = session.get(key)

    if cart and product_id in cart:
        del cart[product_id]

    session[key] = cart

    return jsonify(utils.cart_stats(cart=cart))


@app.context_processor
def common_attr():
    return {
        "cart": utils.cart_stats(session.get(app.config["CART_KEY"])),
        "the_loais": dao.get_the_loai(),
    }


@app.route("/orders/", methods=["get"])
@customer_login_required
def orders():
    check_if_expire_orders(current_user.get_id())

    page_size = 10
    page = request.args.get("page", 1)
    expire_hours = get_quy_dinh(Rule.OUT_OF_TIME_TO_PAY.value).gia_tri

    don_hangs = get_order_by_user_id(current_user.get_id(), page, page_size)
    counter = utils.count_orders(current_user.get_id())
    order_json = []
    for o in don_hangs:
        order_json.append(
            {
                "id": o.id,
                "ngay_tao_don": o.ngay_tao_don,
                "phuong_thuc": get_phuong_thuc_by_id(o.phuong_thuc_id).ten_phuong_thuc,
                "trang_thai": get_trang_thai_by_id(o.trang_thai_id).ten_trang_thai,
                "total_price": get_order_total_price_by_id(o.id),
            }
        )

    return render_template(
        "orders_view.html",
        orders=order_json,
        pages=math.ceil(counter / page_size),
        eh=expire_hours,
    )


@app.route("/order_details/<int:order_id>", methods=["get"])
@login_required
def order_details(order_id):
    don_hang = get_don_hang(order_id)
    ct_don_hang = don_hang.sach

    total_amount = get_order_total_price_by_id(order_id)
    order_status = get_trang_thai_by_id(don_hang.trang_thai_id).ten_trang_thai
    order_paying_method = get_phuong_thuc_by_id(don_hang.phuong_thuc_id).ten_phuong_thuc

    sachs = []

    for ct in ct_don_hang:
        sachs.append(get_sach_by_id(ct.sach_id))

    order_details = []

    for s, ct in zip(sachs, ct_don_hang):
        order_details.append(
            {
                "bia_sach": s.bia_sach,
                "ten_sach": s.ten_sach,
                "so_luong": ct.so_luong,
                "tong_tien": ct.tong_tien,
            }
        )

    print(order_details)

    return render_template(
        "order_details.html",
        order=don_hang,
        order_details=order_details,
        total_amount=total_amount,
        trang_thai=order_status,
        paying_method=order_paying_method,
    )


# class vnpay để thanh toán online code mẫu dijango của VNPAY
class vnpay:
    requestData = {}
    responseData = {}

    def get_payment_url(self, vnpay_payment_url, secret_key):
        inputData = sorted(self.requestData.items())
        queryString = ""
        hasData = ""
        seq = 0
        for key, val in inputData:
            if seq == 1:
                queryString = (
                    queryString + "&" + key + "=" + urllib.parse.quote_plus(str(val))
                )
            else:
                seq = 1
                queryString = key + "=" + urllib.parse.quote_plus(str(val))

        hashValue = self.__hmacsha512(secret_key, queryString)
        return vnpay_payment_url + "?" + queryString + "&vnp_SecureHash=" + hashValue

    def validate_response(self, secret_key):
        vnp_SecureHash = self.responseData["vnp_SecureHash"]
        # Remove hash params
        if "vnp_SecureHash" in self.responseData.keys():
            self.responseData.pop("vnp_SecureHash")

        if "vnp_SecureHashType" in self.responseData.keys():
            self.responseData.pop("vnp_SecureHashType")

        inputData = sorted(self.responseData.items())
        hasData = ""
        seq = 0
        for key, val in inputData:
            if str(key).startswith("vnp_"):
                if seq == 1:
                    hasData = (
                        hasData
                        + "&"
                        + str(key)
                        + "="
                        + urllib.parse.quote_plus(str(val))
                    )
                else:
                    seq = 1
                    hasData = str(key) + "=" + urllib.parse.quote_plus(str(val))
        hashValue = self.__hmacsha512(secret_key, hasData)

        print(
            "Validate debug, HashData:"
            + hasData
            + "\n HashValue:"
            + hashValue
            + "\nInputHash:"
            + vnp_SecureHash
        )

        return vnp_SecureHash == hashValue

    @staticmethod
    def __hmacsha512(key, data):
        byteKey = key.encode("utf-8")
        byteData = data.encode("utf-8")
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()  #


@app.route("/payment_offline/")
@login_required
def payment_offline():
    return render_template("payment_offline.html")


@app.route("/payment_offline_done", methods=["get"])
@login_required
def payment_offline_done():
    cart_key = app.config["CART_KEY"]
    dien_thoai_nhan_hang = request.args["phone"]
    dia_chi_nhan_hang = "THANH TOÁN TẠI CỬA HÀNG"
    # print(dia_chi_nhan_hang,dien_thoai_nhan_hang)
    # print('user_id : ',current_user.get_id())
    donhang = create_donhang(
        ngay_tao_don=datetime.now(),
        phuong_thuc_id=get_or_create_phuong_thuc_id(PayingMethod.OFFLINE_PAY.value),
        trang_thai_id=get_or_create_trang_thai_id(Status.WAITING.value),
        khach_hang_id=current_user.get_id(),
    )
    cart_items = session[cart_key]

    # print(donhang)
    thongtinnhanhang = create_thongtinnhanhang(
        id=donhang.id,
        dien_thoai_nhan_hang=dien_thoai_nhan_hang,
        dia_chi_nhan_hang=dia_chi_nhan_hang,
    )

    for ci in cart_items.values():
        create_chitietdonhang(
            don_hang_id=donhang.id,
            sach_id=ci["id"],
            so_luong=ci["so_luong"],
            tong_tien=ci["don_gia"] * ci["so_luong"],
        )

    session["order_id"] = donhang.id
    session.pop("cart", None)
    return redirect("/")


@app.route("/payment/")
@login_required
def payment():
    return render_template("payment.html")


@app.route("/process_payment", methods=["post"])
@login_required
def process_payment():
    cart_key = app.config["CART_KEY"]
    dien_thoai_nhan_hang = request.form["phone"]
    dia_chi_nhan_hang = request.form["address"]
    is_pay_later = request.form.get("switch_isThanhToanSau", False)
    # print(dia_chi_nhan_hang,dien_thoai_nhan_hang)
    # print('user_id : ',current_user.get_id())
    donhang = create_donhang(
        ngay_tao_don=datetime.now(),
        phuong_thuc_id=get_or_create_phuong_thuc_id(PayingMethod.ONLINE_PAY.value),
        trang_thai_id=get_or_create_trang_thai_id(Status.WAITING.value),
        khach_hang_id=current_user.get_id(),
    )
    cart_items = session[cart_key]

    # print(donhang)
    thongtinnhanhang = create_thongtinnhanhang(
        id=donhang.id,
        dien_thoai_nhan_hang=dien_thoai_nhan_hang,
        dia_chi_nhan_hang=dia_chi_nhan_hang,
    )

    for ci in cart_items.values():
        create_chitietdonhang(
            don_hang_id=donhang.id,
            sach_id=ci["id"],
            so_luong=ci["so_luong"],
            tong_tien=ci["don_gia"] * ci["so_luong"],
        )

    session["order_id"] = donhang.id

    total_amount = cart_stats(cart_items).get("total_amount")

    session.pop(cart_key, None)

    if is_pay_later:
        return redirect("/")
    else:
        pass
    #########################################
    vnp = vnpay()
    vnp.requestData["vnp_Version"] = "2.1.0"
    vnp.requestData["vnp_Command"] = "pay"
    vnp.requestData["vnp_TmnCode"] = VNPAY_MERCHANT_ID
    vnp.requestData["vnp_Amount"] = total_amount * 100
    vnp.requestData["vnp_CurrCode"] = "VND"
    vnp.requestData["vnp_TxnRef"] = str(random.randint(100000, 999999)) + str(
        donhang.id
    )
    vnp.requestData["vnp_OrderInfo"] = "Thanh toan"
    vnp.requestData["vnp_OrderType"] = "other"
    vnp.requestData["vnp_Locale"] = "vn"
    vnp.requestData["vnp_CreateDate"] = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )  # 20150410063022
    vnp.requestData["vnp_IpAddr"] = request.remote_addr
    vnp.requestData["vnp_ReturnUrl"] = VNPAY_RETURN_URL
    vnpay_payment_url = vnp.get_payment_url(VNPAY_PAYMENT_URL, VNPAY_API_KEY)
    print(vnpay_payment_url)
    return redirect(vnpay_payment_url)


@app.route("/process_payment_in_order_details", methods=["post"])
@login_required
def process_payment_in_order_details():
    order_id = request.form["order_id"]

    session["order_id"] = order_id
    total_amount = get_order_total_price_by_id(order_id)

    order = get_order_by_order_id(order_id)
    # print(get_phuong_thuc_by_id(order.phuong_thuc_id).ten_phuong_thuc)
    if (
        get_trang_thai_by_id(order.trang_thai_id).ten_trang_thai.__eq__(
            Status.FAIL.value
        )
        or get_trang_thai_by_id(order.trang_thai_id).ten_trang_thai.__eq__(
            Status.PAID.value
        )
        or get_phuong_thuc_by_id(order.phuong_thuc_id).ten_phuong_thuc.__eq__(
            PayingMethod.OFFLINE_PAY.value
        )
    ):
        return "<h1>Error can't create a payment with this order !</h1>"

    ####################################
    vnp = vnpay()
    vnp.requestData["vnp_Version"] = "2.1.0"
    vnp.requestData["vnp_Command"] = "pay"
    vnp.requestData["vnp_TmnCode"] = VNPAY_MERCHANT_ID
    vnp.requestData["vnp_Amount"] = total_amount * 100
    vnp.requestData["vnp_CurrCode"] = "VND"
    vnp.requestData["vnp_TxnRef"] = str(random.randint(100000, 999999)) + str(order_id)
    vnp.requestData["vnp_OrderInfo"] = "Thanh toan"
    vnp.requestData["vnp_OrderType"] = "other"
    vnp.requestData["vnp_Locale"] = "vn"
    vnp.requestData["vnp_CreateDate"] = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )  # 20150410063022
    vnp.requestData["vnp_IpAddr"] = request.remote_addr
    vnp.requestData["vnp_ReturnUrl"] = VNPAY_RETURN_URL
    vnpay_payment_url = vnp.get_payment_url(VNPAY_PAYMENT_URL, VNPAY_API_KEY)
    # print(vnpay_payment_url)
    return redirect(vnpay_payment_url)


@app.route("/vnpay_return", methods=["get"])
def payment_return():
    input_data = request.args  # Lấy dữ liệu từ query string
    if input_data:
        vnp = vnpay()
        vnp.responseData = input_data.to_dict()  # Chuyển đổi thành dictionary
        order_id = input_data.get("vnp_TxnRef")
        amount = int(input_data.get("vnp_Amount", 0)) / 100
        order_desc = input_data.get("vnp_OrderInfo")
        vnp_transaction_no = input_data.get("vnp_TransactionNo")
        vnp_response_code = input_data.get("vnp_ResponseCode")
        vnp_tmn_code = input_data.get("vnp_TmnCode")
        vnp_pay_date = input_data.get("vnp_PayDate")
        vnp_bank_code = input_data.get("vnp_BankCode")
        vnp_card_type = input_data.get("vnp_CardType")

        # Validate response
        if vnp.validate_response(VNPAY_API_KEY):
            if vnp_response_code == "00":

                order_id = session["order_id"]

                donhang = get_order_by_order_id(order_id)

                ct_don_hang = donhang.sach

                update_so_luong_by_ct_don_hang(ct_don_hang)

                donhang.trang_thai_id = get_trang_thai_by_name(Status.PAID.value).id

                db.session.commit()

                return redirect(
                    url_for("payment_succeed")
                )  # Chuyển hướng đến trang thành công
            else:
                return redirect(
                    url_for("payment_failed")
                )  # Chuyển hướng đến trang thất bại
    return "Invalid request", 400


@app.route("/payment_succeed")
def payment_succeed():
    return render_template("payment_succeed.html")


@app.route("/payment_failed")
def payment_failed():
    return render_template("payment_failed.html")


def format_price(price):
    return f"{price:,.0f}".replace(",", ".")


@app.template_filter("format_price")
def format_price_filter(price):
    return format_price(price)


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True, port=5001)
