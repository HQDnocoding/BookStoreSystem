import json

from app import app as my_app, db
from app.models import Sach, TacGia, TheLoai

def load_sach_from_json(file_path):
    # Đọc dữ liệu từ file JSON
    with open(file_path, 'r', encoding='utf-8') as f:
        sach_data = json.load(f)

    # Lặp qua từng mục trong dữ liệu sach_data và tạo đối tượng Sach
    for item in sach_data:
        sach = Sach(
            ten_sach=item['ten_sach'],
            don_gia=item['don_gia'],
            bia_sach=item['bia_sach'],
            noi_dung=item['noi_dung'],
            so_luong=item['so_luong'],
            the_loai_id=item['the_loai_id'],
            tac_gia_id=item['tac_gia_id']
        )
        db.session.add(sach)

    # Lưu tất cả các đối tượng vào cơ sở dữ liệu
    db.session.commit()


def load_tac_gia_from_json(file_path):
    # Đọc dữ liệu từ file JSON
    with open(file_path, 'r', encoding='utf-8') as f:
        tac_gia_data = json.load(f)

    # Lặp qua từng mục trong dữ liệu tac_gia_data và tạo đối tượng TacGia
    for item in tac_gia_data:
        tac_gia = TacGia(
            ten_tac_gia=item['ten_tac_gia']
        )
        db.session.add(tac_gia)

    # Lưu tất cả các đối tượng vào cơ sở dữ liệu
    db.session.commit()


def load_the_loai_from_json(file_path):
    # Đọc dữ liệu từ file JSON
    with open(file_path, 'r', encoding='utf-8') as f:
        the_loai_data = json.load(f)

    # Lặp qua từng mục trong dữ liệu the_loai_data và tạo đối tượng TheLoai
    for item in the_loai_data:
        the_loai = TheLoai(
            ten_the_loai=item['ten_the_loai']
        )
        db.session.add(the_loai)

    # Lưu tất cả các đối tượng vào cơ sở dữ liệu
    db.session.commit()


if __name__ == "__main__":
    with my_app.app_context():
        load_tac_gia_from_json('tac_gia.json') # Đường dẫn đến file JSON tác giả
        load_the_loai_from_json('the_loai.json') # Đường dẫn đến file JSON thể loại
        load_sach_from_json('sach.json')
        print("Dữ liệu đã được tải thành công!")