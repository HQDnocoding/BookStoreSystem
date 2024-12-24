
import locale
from datetime import datetime, timedelta

from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from sqlalchemy.testing.config import db_url

from app import Status, db
from app.admin import SachForm
from app.dao import get_trang_thai_by_name, get_sach_by_id
from app.models import DonHang, User, Sach
from app.models import DonHang

from app import app


def cart_stats(cart):
    total_amount, total_quantity = 0, 0





    if cart:
        for c in cart.values():
            total_quantity += c['so_luong']
            total_amount += c['so_luong'] * c['don_gia']
    else:
        cart = {}

    return {
        "cart": list(cart.values()),
        "total_amount": total_amount,
        "total_quantity": total_quantity
    }




# Đăng ký font Tahoma
font_path = 'C:\\Windows\\Fonts\\Tahoma.ttf'
pdfmetrics.registerFont(TTFont('Tahoma', font_path))


def create_invoice_pdf(customer_name, invoice_date, items, cashier_name, output_filename="invoice.pdf"):
    # Tạo canvas
    pdf = canvas.Canvas(output_filename, pagesize=letter)
    pdf.setTitle("Hóa đơn bán sách")

    # Tiêu đề
    pdf.setFont("Tahoma", 14)
    pdf.drawCentredString(300, 750, "HÓA ĐƠN BÁN SÁCH")

    # Thông tin khách hàng và ngày lập hóa đơn
    pdf.setFont("Tahoma", 12)
    pdf.drawString(50, 720, f"Họ tên khách hàng: {customer_name}")
    pdf.drawString(350, 720, f"Ngày lập hóa đơn: {invoice_date}")

    # Bảng tiêu đề
    pdf.line(50, 710, 550, 710)  # Dòng ngang đầu bảng
    pdf.setFont("Tahoma", 12)
    pdf.drawString(60, 690, "STT")
    pdf.drawString(100, 690, "Sách")
    pdf.drawString(250, 690, "Thể loại")
    pdf.drawString(370, 690, "Số lượng")
    pdf.drawString(470, 690, "Đơn giá")
    pdf.line(50, 680, 550, 680)

    locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')

    pdf.setFont("Tahoma", 12)
    y_position = 660
    for idx, item in enumerate(items):
        pdf.drawString(60, y_position, str(idx + 1))
        pdf.drawString(100, y_position, item['ten_sach'])
        pdf.drawString(250, y_position, item['the_loai'])
        pdf.drawString(370, y_position, str(item['so_luong']))

        formatted_price = locale.format_string("%d", item['don_gia'], grouping=True)
        pdf.drawString(470, y_position, f"{formatted_price} VND")
        y_position -= 20


    pdf.line(50, y_position - 10, 550, y_position - 10)
    pdf.drawString(50, y_position - 40, f"Nhân viên thanh toán: {cashier_name}")

    # Lưu file PDF
    pdf.save()
    print(f"Hóa đơn đã được tạo tại {output_filename}")

def count_orders(khach_hang_id):
    return DonHang.query.filter_by(khach_hang_id=khach_hang_id).count()


def check_if_expire_orders(user_id):
    don_hangs = User.query.get(user_id).don_hang

    for d in don_hangs:
        if (datetime.now() - d.ngay_tao_don > timedelta(hours=72) ) and d.trang_thai_id == get_trang_thai_by_name(Status.WAITING.value):
            d.trang_thai_id = get_trang_thai_by_name(Status.FAIL.value).id

    db.session.commit()

def get_freq(tu, mau):
    return tu / mau





# Hàm tạo PDF
def create_pdf_export_freq(data, file_name, month,year):

    pdf = canvas.Canvas(file_name, pagesize=letter)
    pdf.setFont("Tahoma", 12)
    width, height = letter

    # Tiêu đề
    pdf.setFont("Tahoma", 14)
    pdf.drawString(200, height - 50, "BÁO CÁO TẦN SUẤT SÁCH BÁN")
    pdf.setFont("Tahoma", 12)
    pdf.drawString(250, height - 80, f"Tháng: {month/year}")

    # Vẽ bảng
    x_start = 50
    y_start = height - 120
    col_widths = [50, 200, 150, 100, 100]  # Độ rộng từng cột
    row_height = 30

    # Tiêu đề bảng
    headers = ["STT", "Tên sách", "Thể loại", "Số lượng", "Tỷ lệ"]
    pdf.setFont("Tahoma", 11)
    y = y_start
    pdf.rect(x_start, y, sum(col_widths), -row_height)  # Vẽ ô tiêu đề
    x = x_start
    for i, header in enumerate(headers):
        pdf.drawString(x + 5, y - 20, header)
        x += col_widths[i]

    # Nội dung bảng
    for row in data:
        y -= row_height
        pdf.rect(x_start, y, sum(col_widths), -row_height)  # Vẽ từng hàng
        x = x_start
        for i, cell in enumerate(row):
            pdf.drawString(x + 5, y - 20, str(cell))
            x += col_widths[i]

    # Kết thúc PDF
    pdf.save()

def update_so_luong_by_ct_don_hang(ct_don_hang):
    sachs = []
    for ct in ct_don_hang:
        sachs.append(get_sach_by_id(ct.sach_id))
    for s, ct in zip(sachs, ct_don_hang):
        s.so_luong -= ct.so_luong

    db.session.commit()