import random
from datetime import datetime, timedelta
from app import app as my_app, db
from app.models import User


def create_random_users(num_users: int, vai_tro_id: int = 4):
    total_users = db.session.query(User).count()
    for i in range(1, num_users + 1):
        username = f"kh{total_users+i}"  # Tạo username theo định dạng "khX", với X là id
        password = "123"  # Mật khẩu cố định
        ho = f"Họ {i}"  # Tùy chỉnh họ cho người dùng
        ten = f"Tên {i}"  # Tùy chỉnh tên cho người dùng

        new_user = User(
            ho=ho,
            ten=ten,
            username=username,
            password=password,
            vai_tro_id=vai_tro_id
        )

        db.session.add(new_user)
        print(f"Đã tạo user có username = {username}")

    db.session.commit()  # Lưu tất cả người dùng đã tạo

    print(f"Đã tạo {num_users} người dùng.")


if __name__ == "__main__":
    with my_app.app_context():
        so_luong_user_can_tao = 10
        create_random_users(so_luong_user_can_tao)