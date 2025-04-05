import locale
import textwrap
from datetime import datetime, timedelta

from flask import jsonify, session
from flask_login import current_user
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from app import PayingMethod, Rule, Status, app, db
from app.admin import SachForm
from app.dao import (create_chitietdonhang, create_donhang,
                     create_thongtinnhanhang, get_or_create_phuong_thuc_id,
                     get_or_create_trang_thai_id, get_quy_dinh, get_sach_by_id,
                     get_trang_thai_by_name)
from app.models import DonHang, Sach, User


def process_offline_payment(cart_items, phone, address="THANH TOÁN TẠI CỬA HÀNG"):
    if not cart_items:
        raise ValueError("Giỏ hàng trống")

    # Tạo đơn hàng
    donhang = create_donhang(
        ngay_tao_don=datetime.now(),
        phuong_thuc_id=get_or_create_phuong_thuc_id(PayingMethod.OFFLINE_PAY.value),
        trang_thai_id=get_or_create_trang_thai_id(Status.WAITING.value),
        khach_hang_id=current_user.get_id(),
    )

    # Tạo thông tin nhận hàng
    create_thongtinnhanhang(
        id=donhang.id,
        dien_thoai_nhan_hang=phone,
        dia_chi_nhan_hang=address,
    )

    # Tạo chi tiết đơn hàng từ giỏ hàng
    for ci in cart_items.values():
        create_chitietdonhang(
            don_hang_id=donhang.id,
            sach_id=ci["id"],
            so_luong=ci["so_luong"],
            tong_tien=ci["don_gia"] * ci["so_luong"],
        )

    return donhang.id


def cart_stats(cart):
    """Tính toán thông tin thống kê của giỏ hàng."""
    if cart is None:
        cart = {}
    total_quantity = 0
    total_amount = 0.0
    updated_cart = cart.copy()

    for book_id, item in updated_cart.items():
        so_luong = item.get("so_luong", 0)
        don_gia = item.get("don_gia", 0)
        total_quantity += so_luong
        total_amount += don_gia * so_luong

    return {
        "total_quantity": total_quantity,
        "total_amount": total_amount,
        "cart": updated_cart,
    }


def add_to_cart(book, so_luong, cart_session):
    """Hàm xử lý thêm sách vào giỏ hàng."""
    key = "CART_KEY"
    so_luong_con_lai = book.so_luong

    # Kiểm tra số lượng hợp lệ
    if so_luong <= 0:
        return jsonify({"alert": "Số lượng không hợp lệ"}), 400

    if so_luong > so_luong_con_lai:
        data = cart_stats(cart_session.get(key, {}))
        data["alert"] = "Đã HẾT sách hoặc không đủ số lượng trong kho"
        return jsonify(data), 400

    # Lấy giỏ hàng từ session
    cart = cart_session.get(key, {})

    if book.id in cart:
        new_quantity = cart[book.id]["so_luong"] + so_luong
        if new_quantity > so_luong_con_lai:
            data = cart_stats(cart)
            data["alert"] = "KHÔNG đủ sách để mua"
            return jsonify(data), 400
        cart[book.id]["so_luong"] = new_quantity
    else:
        cart[book.id] = {
            "id": book.id,
            "ten_sach": book.ten_sach,
            "don_gia": book.don_gia,
            "so_luong": so_luong,
            "bia_sach": book.bia_sach,
            "so_luong_con_lai": so_luong_con_lai,
        }

    cart_session[key] = cart
    return jsonify(cart_stats(cart)), 200


# def get_stats(nam: int, thang: int, ten_the_loai: str) -> list:
#     try:
#         start_date = datetime(nam, thang, 1)
#         end_date = datetime(nam + 1, 1, 1) if thang == 12 else datetime(nam, thang + 1, 1)

#         # Sử dụng with_entities để giảm tải dữ liệu
#         total_sales = (
#             db.session.query(func.sum(ChiTietDonHang.tong_tien))
#             .join(DonHang)
#             .filter(
#                 DonHang.ngay_tao_don >= start_date,
#                 DonHang.ngay_tao_don < end_date,
#                 DonHang.trang_thai_id == get_id_by_trang_thai(Status.PAID.value),
#             )
#             .scalar() or 0
#         )

#         if total_sales == 0:
#             return [["Không có dữ liệu", 0, 0.0, 0.0]]

#         query = (
#             db.session.query(
#                 TheLoai.ten_the_loai,
#                 func.sum(ChiTietDonHang.so_luong).label("so_luong_ban"),
#                 func.sum(ChiTietDonHang.tong_tien).label("doanh_thu"),
#                 (func.sum(ChiTietDonHang.tong_tien) / total_sales * 100).label("ti_le_ban"),
#             )
#             .select_from(ChiTietDonHang)
#             .join(DonHang)
#             .join(Sach)
#             .join(TheLoai)
#             .filter(
#                 DonHang.ngay_tao_don >= start_date,
#                 DonHang.ngay_tao_don < end_date,
#                 DonHang.trang_thai_id == get_id_by_trang_thai(Status.PAID.value),
#             )
#         )

#         if ten_the_loai != "Tất cả":
#             query = query.filter(TheLoai.ten_the_loai == ten_the_loai)

#         return query.group_by(TheLoai.ten_the_loai).all()

#     except SQLAlchemyError as e:
#         app.logger.error(f"Lỗi khi lấy thống kê: {str(e)}")
#         return [["Lỗi hệ thống", 0, 0.0, 0.0]]


# Đăng ký font Tahoma
font_path = "C:\\Windows\\Fonts\\Tahoma.ttf"
pdfmetrics.registerFont(TTFont("Tahoma", font_path))

font_path2 = "C:\\Windows\\Fonts\\arial.ttf"
pdfmetrics.registerFont(TTFont("arial", font_path))
font_path3 = "C:\\Windows\\Fonts\\DejaVuSans.ttf"
pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))


def draw_wrapped_text(pdf, x, y, text, max_width, line_height):
    """
    Vẽ văn bản tự động xuống dòng và trả về tọa độ y cuối cùng.
    """
    lines = textwrap.wrap(text, width=max_width)
    for line in lines:
        pdf.drawString(x, y, line)
        y -= line_height
    return y, len(lines) * line_height


def create_invoice_pdf(
    customer_name, invoice_date, items, cashier_name, output_filename="invoice.pdf"
):
    pdf = canvas.Canvas(output_filename, pagesize=letter)
    pdf.setTitle("Hóa đơn bán sách")
    pdf.setFont("Tahoma", 10)

    page_width, page_height = letter

    # Tiêu đề
    pdf.drawCentredString(page_width / 2, 750, "HÓA ĐƠN BÁN SÁCH")

    # Thông tin khách hàng
    pdf.setFont("Tahoma", 8)
    pdf.drawString(50, 720, f"Họ tên khách hàng: {customer_name}")

    pdf.drawString(350, 720, f"Ngày lập hóa đơn: {str(invoice_date)}")

    # Bảng tiêu đề
    pdf.line(50, 710, 550, 710)
    pdf.setFont("Tahoma", 10)
    pdf.drawString(60, 690, "STT")
    pdf.drawString(100, 690, "Sách")
    pdf.drawString(250, 690, "Thể loại")
    pdf.drawString(370, 690, "Số lượng")
    pdf.drawString(470, 690, "Đơn giá")
    pdf.line(50, 680, 550, 680)

    # Nội dung bảng
    pdf.setFont("Tahoma", 8)
    y_position = 660
    line_height = 12

    try:
        locale.setlocale(locale.LC_ALL, "vi_VN.UTF-8")
    except locale.Error:
        print("Không thể thiết lập locale. Sử dụng định dạng mặc định.")

    for idx, item in enumerate(items):
        stt_height = line_height
        ten_sach_height = len(textwrap.wrap(item["ten_sach"], width=30)) * line_height
        the_loai_height = len(textwrap.wrap(item["the_loai"], width=20)) * line_height
        max_height = max(stt_height, ten_sach_height, the_loai_height)

        pdf.drawString(60, y_position, str(idx + 1))

        _, used_height_ten_sach = draw_wrapped_text(
            pdf,
            100,
            y_position,
            item["ten_sach"],
            max_width=30,
            line_height=line_height,
        )

        _, used_height_the_loai = draw_wrapped_text(
            pdf,
            250,
            y_position,
            item["the_loai"],
            max_width=20,
            line_height=line_height,
        )

        pdf.drawRightString(400, y_position, str(item["so_luong"]))

        formatted_price = locale.format_string("%d", item["don_gia"], grouping=True)
        pdf.drawRightString(510, y_position, f"{formatted_price} VND")

        y_position -= max_height

    pdf.line(50, y_position - 10, 550, y_position - 10)
    pdf.drawString(50, y_position - 40, f"Nhân viên thanh toán: {cashier_name}")

    pdf.save()


def count_orders(khach_hang_id):
    return DonHang.query.filter_by(khach_hang_id=khach_hang_id).count()


def check_if_expire_orders(user_id):
    don_hangs = User.query.get(user_id).don_hang_kh

    expire_hours = get_quy_dinh(Rule.OUT_OF_TIME_TO_PAY.value).gia_tri

    for d in don_hangs:
        if (
            datetime.now() - d.ngay_tao_don > timedelta(hours=expire_hours)
        ) and d.trang_thai_id == get_trang_thai_by_name(Status.WAITING.value):
            d.trang_thai_id = get_trang_thai_by_name(Status.FAIL.value).id

    db.session.commit()


def get_freq(tu, mau):
    return tu / mau


# Hàm tạo PDF
def create_pdf_export_freq(data, file_name, month, year):
    pdf = canvas.Canvas(file_name, pagesize=letter)
    pdf.setFont("Tahoma", 12)
    width, height = letter

    # Tiêu đề
    pdf.setFont("Tahoma", 14)
    pdf.drawString(200, height - 50, "BÁO CÁO TẦN SUẤT SÁCH BÁN")
    pdf.setFont("Tahoma", 12)
    pdf.drawString(250, height - 80, f"Tháng: {month}/{year}")

    # Vẽ bảng
    x_start = 50
    y_start = height - 120
    col_widths = [50, 200, 150, 100, 100]  # Độ rộng từng cột
    row_height = 30

    # Tiêu đề bảng
    headers = ["STT", "Tên sách", "Thể loại", "Số lượng", "Tỷ lệ"]
    pdf.setFont("Tahoma", 8)
    y = y_start
    pdf.rect(x_start, y, sum(col_widths), -row_height)  # Vẽ ô tiêu đề
    x = x_start
    for i, header in enumerate(headers):
        pdf.drawString(x + 5, y - 20, header)
        x += col_widths[i]

    # Hàm xử lý xuống dòng tên sách
    def draw_multiline_text(x, y, text, width, pdf):
        # Chia nhỏ text thành các dòng nếu dài hơn chiều rộng cột
        lines = []
        current_line = ""
        for word in text.split():
            if pdf.stringWidth(current_line + word, "Tahoma", 8) < width - 10:
                current_line += " " + word
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)  # thêm dòng cuối cùng
        # Vẽ từng dòng
        for line in lines:
            pdf.drawString(x + 5, y, line)
            y -= 10  # Dịch xuống cho dòng tiếp theo

    # Nội dung bảng
    index = 1
    for row in data:
        y -= row_height
        pdf.rect(x_start, y, sum(col_widths), -row_height)  # Vẽ từng hàng
        x = x_start
        for i, cell in enumerate(row):
            if i == 1:  # Cột "Tên sách" xử lý xuống dòng
                draw_multiline_text(x, y - 15, str(cell), col_widths[i], pdf)
            elif i == 0:
                pdf.drawString(x + 5, y - 20, str(index))
                index += 1
            else:
                pdf.drawString(x + 5, y - 20, str(cell))
            x += col_widths[i]

    # Kết thúc PDF
    pdf.save()


def create_pdf_export_rev(data, file_name, month, year):
    pdf = canvas.Canvas(file_name, pagesize=letter)
    pdf.setFont("DejaVuSans", 12)
    width, height = letter

    # Tiêu đề
    pdf.drawCentredString(width / 2, height - 50, "BÁO CÁO DOANH THU THEO THÁNG")

    # Tháng và năm
    pdf.setFont("DejaVuSans", 8)
    text = f"Tháng: {month} , Năm: {year}"
    x_position = (width - pdf.stringWidth(text, "DejaVuSans", 8)) / 2
    pdf.drawString(x_position, height - 80, text)

    # Dữ liệu bảng
    table_data = [
        ["STT", "Thể loại sách", "Số lượng bán", "Doanh thu (VNĐ)", "Tỷ lệ (%)"]
    ]
    total_revenue = 0

    for idx, row in enumerate(data, start=1):
        table_data.append(
            [
                idx,
                row[0],
                f"{row[1]:,}",
                locale.format_string("%d", row[2], grouping=True),
                f"{row[3]:.2f}",
            ]
        )
        total_revenue += row[2]

    # Tổng doanh thu
    table_data.append(
        [
            "Tổng doanh thu",
            "",
            "",
            f"{locale.format_string("%d", total_revenue, grouping=True)}VNĐ",
            "",
        ]
    )

    # Tạo bảng
    table = Table(table_data, colWidths=[50, 150, 150, 100, 100])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("SPAN", (0, -1), (2, -1)),  # Gộp cột cho dòng tổng
                ("SPAN", (3, -1), (4, -1)),
                ("ALIGN", (0, -1), (0, -1), "CENTER"),  # Căn giữa "Tổng doanh thu"
                ("ALIGN", (3, -1), (3, -1), "CENTER"),  # Căn giữa giá trị tổng
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    # Vẽ bảng vào PDF
    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, 50, height - 250)

    # Lưu file PDF
    pdf.save()


def update_so_luong_by_ct_don_hang(ct_don_hang):
    sachs = []
    for ct in ct_don_hang:
        sachs.append(get_sach_by_id(ct.sach_id))
    for s, ct in zip(sachs, ct_don_hang):
        s.so_luong -= ct.so_luong

    db.session.commit()


def create_pdf_export_nhap_sach(data, file_name):

    pdf = canvas.Canvas(file_name, pagesize=letter)
    pdf.setFont("DejaVuSans", 12)
    width, height = letter

    # Dữ liệu bảng
    table_data = [["PHIẾU NHẬP SÁCH", "", "", "", ""]]  # Tiêu đề gộp 5 cột
    current_date = datetime.now().strftime("%d/%m/%Y")  # Lấy ngày hiện tại
    table_data.append(
        [f"Ngày nhập: {current_date}", "", "", "", ""]
    )  # Ngày nhập gộp 5 cột
    table_data.append(["STT", "Sách", "Thể loại", "Tác giả", "Số lượng"])

    if data:  # Kiểm tra xem data có dữ liệu không
        for idx, row in enumerate(data, start=1):
            if len(row) >= 4:  # Đảm bảo mỗi hàng đủ số cột
                table_data.append(
                    [
                        idx,
                        row[0],
                        row[1],
                        row[2],
                        row[3],  # Chuyển Decimal sang float nếu cần
                    ]
                )

    # Tạo bảng
    table = Table(table_data, colWidths=[50, 150, 150, 100, 100])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("SPAN", (0, 0), (4, 0)),
                ("SPAN", (0, 1), (4, 1)),
                ("WORDRAP", (0, 0), (-1, -1), "CJK"),
            ]
        )
    )

    # Vẽ bảng vào PDF
    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, 50, height - 250)

    # Lưu file PDF
    pdf.save()
