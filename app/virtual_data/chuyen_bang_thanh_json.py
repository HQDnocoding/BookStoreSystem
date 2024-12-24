import json

from app import app as my_app, db
from app.models import Sach, TacGia, TheLoai


def sach_to_json():
    # Lấy tất cả sách từ cơ sở dữ liệu
    sach_list = db.session.query(Sach).all()

    # Chuyển đổi danh sách sách thành một danh sách dict
    sach_data = []
    for sach in sach_list:
        sach_data.append({
            'id': sach.id,
            'ten_sach': sach.ten_sach,
            'don_gia': sach.don_gia,
            'bia_sach': sach.bia_sach,
            'noi_dung': sach.noi_dung,
            'so_luong': sach.so_luong,
            'the_loai_id': sach.the_loai_id,
            'tac_gia_id': sach.tac_gia_id,
        })

    # Lưu dữ liệu vào file sach.json
    with open('sach.json', 'w', encoding='utf-8') as f:
        json.dump(sach_data, f, ensure_ascii=False, indent=4)

    print("Dữ liệu sách đã được lưu vào sach.json")


def tac_gia_to_json():
    # Lấy tất cả tác giả từ cơ sở dữ liệu
    tac_gia_list = db.session.query(TacGia).all()

    # Chuyển đổi danh sách tác giả thành một danh sách dict
    tac_gia_data = []
    for tac_gia in tac_gia_list:
        tac_gia_data.append({
            'id': tac_gia.id,
            'ten_tac_gia': tac_gia.ten_tac_gia
        })

    # Lưu dữ liệu vào file tac_gia.json
    with open('tac_gia.json', 'w', encoding='utf-8') as f:
        json.dump(tac_gia_data, f, ensure_ascii=False, indent=4)

    print("Dữ liệu tác giả đã được lưu vào tac_gia.json")


def the_loai_to_json():
    # Lấy tất cả thể loại từ cơ sở dữ liệu
    the_loai_list = db.session.query(TheLoai).all()

    # Chuyển đổi danh sách thể loại thành một danh sách dict
    the_loai_data = []
    for the_loai in the_loai_list:
        the_loai_data.append({
            'id': the_loai.id,
            'ten_the_loai': the_loai.ten_the_loai
        })

    # Lưu dữ liệu vào file the_loai.json
    with open('the_loai.json', 'w', encoding='utf-8') as f:
        json.dump(the_loai_data, f, ensure_ascii=False, indent=4)

    print("Dữ liệu thể loại đã được lưu vào the_loai.json")

if __name__ == "__main__":
    with my_app.app_context():
        the_loai_to_json()
        tac_gia_to_json()
        sach_to_json()
