import json
import os

from app import app as my_app
from app import db
from app.models import Sach, TacGia, TheLoai


def load_sach_from_json(file_name):
    try:
        # Lấy thư mục hiện tại của script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Tạo đường dẫn tương đối tới file JSON
        file_path = os.path.join(current_dir, file_name)

        # Đọc dữ liệu từ file JSON
        with open(file_path, "r", encoding="utf-8") as f:
            sach_data = json.load(f)

        # Lặp qua từng mục trong dữ liệu sach_data và tạo đối tượng Sach
        for item in sach_data:
            sach = Sach(
                ten_sach=item["ten_sach"],
                don_gia=item["don_gia"],
                bia_sach=item["bia_sach"],
                noi_dung=item["noi_dung"],
                so_luong=item["so_luong"],
                nam_phat_hanh=item["nam_phat_hanh"],
                the_loai_id=item["the_loai_id"],
                tac_gia_id=item["tac_gia_id"],
            )
            db.session.add(sach)

        # Lưu tất cả các đối tượng vào cơ sở dữ liệu
        db.session.commit()
        print(f"Đã tải dữ liệu sách từ {file_name} thành công!")
    except FileNotFoundError:
        print(f"Không tìm thấy file: {file_name}")
    except json.JSONDecodeError:
        print(f"Lỗi định dạng JSON trong file: {file_name}")
    except Exception as e:
        print(f"Lỗi khi tải dữ liệu sách: {e}")


def load_tac_gia_from_json(file_name):
    try:
        # Lấy thư mục hiện tại của script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Tạo đường dẫn tương đối tới file JSON
        file_path = os.path.join(current_dir, file_name)

        # Đọc dữ liệu từ file JSON
        with open(file_path, "r", encoding="utf-8") as f:
            tac_gia_data = json.load(f)

        # Lặp qua từng mục trong dữ liệu tac_gia_data và tạo đối tượng TacGia
        for item in tac_gia_data:
            tac_gia = TacGia(ten_tac_gia=item["ten_tac_gia"])
            db.session.add(tac_gia)

        # Lưu tất cả các đối tượng vào cơ sở dữ liệu
        db.session.commit()
        print(f"Đã tải dữ liệu tác giả từ {file_name} thành công!")
    except FileNotFoundError:
        print(f"Không tìm thấy file: {file_name}")
    except json.JSONDecodeError:
        print(f"Lỗi định dạng JSON trong file: {file_name}")
    except Exception as e:
        print(f"Lỗi khi tải dữ liệu tác giả: {e}")


def load_the_loai_from_json(file_name):
    try:
        # Lấy thư mục hiện tại của script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Tạo đường dẫn tương đối tới file JSON
        file_path = os.path.join(current_dir, file_name)

        # Đọc dữ liệu từ file JSON
        with open(file_path, "r", encoding="utf-8") as f:
            the_loai_data = json.load(f)

        # Lặp qua từng mục trong dữ liệu the_loai_data và tạo đối tượng TheLoai
        for item in the_loai_data:
            the_loai = TheLoai(ten_the_loai=item["ten_the_loai"])
            db.session.add(the_loai)

        # Lưu tất cả các đối tượng vào cơ sở dữ liệu
        db.session.commit()
        print(f"Đã tải dữ liệu thể loại từ {file_name} thành công!")
    except FileNotFoundError:
        print(f"Không tìm thấy file: {file_name}")
    except json.JSONDecodeError:
        print(f"Lỗi định dạng JSON trong file: {file_name}")
    except Exception as e:
        print(f"Lỗi khi tải dữ liệu thể loại: {e}")


if __name__ == "__main__":
    with my_app.app_context():
        # Sử dụng tên file thay vì đường dẫn cứng
        load_tac_gia_from_json("tac_gia.json")  # File JSON tác giả
        load_the_loai_from_json("the_loai.json")  # File JSON thể loại
        load_sach_from_json("sach.json")  # File JSON sách
        print("Tất cả dữ liệu đã được tải thành công!")
