
import locale

from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont

from app.models import DonHang



def cart_stats(cart):
    total_amount, total_quantity = 0,0





    if cart:
        for c in cart.values():
            total_quantity+=c['so_luong']
            total_amount+=c['so_luong']*c['don_gia']
    else:
        cart={}

    return {
        "cart": list(cart.values()),
        "total_amount":total_amount,
        "total_quantity":total_quantity
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

