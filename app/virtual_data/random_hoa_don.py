import random
from datetime import datetime, timedelta
from app import app as my_app, db
from app.models import DonHang, ChiTietDonHang, Sach

def random_date(start: datetime, end: datetime) -> datetime:
    """Trả về một ngày ngẫu nhiên giữa start và end."""
    return start + timedelta(days=random.randint(0, (end - start).days))


def create_random_order(min_user_id: int, max_user_id: int, min_book_id: int, max_book_id: int, start_date: datetime, end_date: datetime):
    user_id = random.randint(min_user_id, max_user_id)

    # Lấy tất cả sách trong khoảng ID
    all_books = db.session.query(Sach).filter(Sach.id >= min_book_id, Sach.id <= max_book_id).all()

    if not all_books:
        print("Không tìm thấy sách trong khoảng cho trước.")
        return

    # Chọn ngẫu nhiên từ 1 đến 10 cuốn sách
    num_books_to_select = random.randint(1, 10)
    selected_books = random.sample(all_books, min(num_books_to_select, len(all_books)))

    # Tạo ngày ngẫu nhiên cho đơn hàng
    ngay_tao_don = random_date(start_date, end_date)

    don_hang = DonHang(
        ngay_tao_don=ngay_tao_don,
        phuong_thuc_id=1,  # Thay đổi theo phương thức thanh toán thực tế
        trang_thai_id=1,   # Thay đổi theo trạng thái đơn hàng thực tế
        khach_hang_id=user_id
    )

    db.session.add(don_hang)
    db.session.commit()  # Lưu đơn hàng trước để có `id` của nó

    for book in selected_books:
        so_luong = random.randint(1, 5)
        chi_tiet_don_hang = ChiTietDonHang(
            don_hang_id=don_hang.id,
            sach_id=book.id,
            so_luong=so_luong,  # Số lượng sách ngẫu nhiên từ 1 đến 5
            tong_tien=book.don_gia * so_luong  # Tính tổng tiền cho các sách
        )
        db.session.add(chi_tiet_don_hang)

    db.session.commit()  # Lưu thông tin chi tiết đơn hàng
    print(f"Đơn hàng #{don_hang.id} đã được tạo với mã khách hàng {user_id} và {len(selected_books)} cuốn sách.")


if __name__ == "__main__":
    with my_app.app_context():
        min_user_id = 1  # Id bất đầu của user
        max_user_id = 3 # Id kết thúc của user
        #lấy user có id từ 1 đến 3, có thể sửa lại cho phù hợp

        min_book_id = 1# Id bất đầu của book
        max_book_id=32#id kết thúc của book
        # lấy book có id từ 1 đến 32, có thể sửa lại cho phù hợp

        start_date = datetime(2010, 1, 1)  # Ngày bắt đầu
        end_date = datetime.now()  # Ngày kết thúc

        so_luong_tao_hoa_don=100 #tổng số lượng tạo đơn hàng, có thể sửa lai cho phù hợp

        for _ in range(so_luong_tao_hoa_don):
            create_random_order(min_user_id, max_user_id, min_book_id, max_book_id, start_date, end_date)
        print("Hoá đơn được tạo thành công !")