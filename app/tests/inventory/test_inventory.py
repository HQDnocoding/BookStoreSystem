import os
from datetime import datetime

import pytest
from flask import url_for
from sqlalchemy.exc import SQLAlchemyError

from app import app, db
from app.dao import (create_chitietphieunhapsach, create_phieunhapsach,
                     update_book_quantity)
from app.models import ChiTietPhieuNhapSach, PhieuNhapSach, Sach
from app.utils import create_pdf_export_nhap_sach


# Test Naming and Test Discovery => FAILED
@pytest.mark.skipif(
    app.config.get("ENV") == "production",
    reason="Chưa có hành động nào được thực hiện để tạo phiếu nhập sách",
)
def test_create_import_ticket_success(warehouse_manager, book, inventory_rules):
    """Kiểm tra tạo phiếu nhập sách thành công (Unit Test)."""
    manager = warehouse_manager
    with app.app_context():
        try:
            # Tạo phiếu nhập sách với ngày mặc định là hiện tại nếu không cung cấp
            try:
                phieu_nhap = create_phieunhapsach(quan_ly_kho_id=manager.id)
                db.session.flush()  # Đẩy dữ liệu tạm thời vào DB mà không commit

                create_chitietphieunhapsach(
                    phieu_nhap_id=phieu_nhap.id, sach_id=book.id, so_luong=5
                )
                update_book_quantity(book.id, 5)

                db.session.commit()  # Commit tất cả cùng lúc để giảm số lần truy vấn
            except Exception as e:
                db.session.rollback()  # Rollback ngay nếu có lỗi
                pytest.fail(f"Transaction error: {str(e)}")

            # Assertions với thông báo lỗi chi tiết hơn
            assert phieu_nhap is not None
            assert phieu_nhap.quan_ly_kho_id == manager.id
            updated_book = Sach.query.get(book.id)
            assert updated_book.so_luong == 15
            assert (
                ChiTietPhieuNhapSach.query.filter_by(
                    phieu_nhap_id=phieu_nhap.id
                ).count()
                == 1
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            pytest.fail(f"Database error during test: {str(e)}")


# Parametrized Testing với xử lý ngoại lệ
@pytest.mark.parametrize(
    "current_stock, import_quantity, expected_success, expected_alert",
    [
        (10, 5, True, None),  # Nhập hợp lệ # Lock wait timeout exceeded
        (25, 5, False, "Số lượng tồn vượt quá SL_MIN_TO_NHAP"),  # Tồn kho đã đủ
        (5, 3, False, "Số lượng nhập dưới SL_NHAP_MIN"),  # Nhập dưới mức tối thiểu
        (
            -1,
            5,
            False,
            "Số lượng tồn không hợp lệ",
        ),  # Thêm trường hợp lỗi # Lock wait timeout exceeded
    ],
)
def test_import_book_with_different_conditions(
    warehouse_manager,
    book,
    inventory_rules,
    current_stock,
    import_quantity,
    expected_success,
    expected_alert,
):
    with app.app_context():
        try:
            book.so_luong = current_stock
            db.session.flush()  # Không commit ngay, tránh giữ khóa lâu

            if current_stock >= inventory_rules.SL_MIN_TO_NHAP:
                result = {
                    "success": False,
                    "alert": "Số lượng tồn vượt quá SL_MIN_TO_NHAP",
                }
            elif import_quantity < inventory_rules.SL_NHAP_MIN:
                result = {"success": False, "alert": "Số lượng nhập dưới SL_NHAP_MIN"}
            else:
                phieu_nhap = create_phieunhapsach(quan_ly_kho_id=warehouse_manager.id)
                db.session.flush()

                # ✅ Dùng bulk insert thay vì add từng cái
                chi_tiet_nhap = [
                    ChiTietPhieuNhapSach(
                        phieu_nhap_sach_id=phieu_nhap.id,
                        sach_id=book.id,
                        so_luong=import_quantity,
                    )
                ]
                db.session.bulk_save_objects(chi_tiet_nhap)

                update_book_quantity(book.id, import_quantity)
                db.session.commit()
                result = {"success": True, "alert": None}

            assert result["success"] == expected_success
            assert result["alert"] == expected_alert
            if expected_success:
                updated_book = Sach.query.get(book.id)
                assert updated_book.so_luong == current_stock + import_quantity
        except SQLAlchemyError as e:
            db.session.rollback()
            pytest.fail(f"Database error: {str(e)}")


# Skipping Tests and Markers với cleanup
@pytest.mark.skipif(
    app.config.get("ENV") == "production",
    reason="Không chạy trong môi trường production",
)
def test_import_book_integration(warehouse_manager, book, inventory_rules, tmp_path):
    """Kiểm tra toàn bộ luồng nhập sách (Integration Test)."""
    manager = warehouse_manager
    with app.app_context():
        try:
            phieu_nhap = create_phieunhapsach(quan_ly_kho_id=manager.id)
            create_chitietphieunhapsach(
                phieu_nhap_id=phieu_nhap.id, sach_id=book.id, so_luong=5
            )
            update_book_quantity(book.id, 5)
            pdf_path = tmp_path / f"PhieuNhapSach_{phieu_nhap.id}.pdf"
            create_pdf_export_nhap_sach(phieu_nhap.id, output_path=str(pdf_path))

            # Assertions
            assert (
                PhieuNhapSach.query.get(phieu_nhap.id) is not None
            ), "Phiếu nhập không tồn tại."
            updated_book = Sach.query.get(book.id)
            assert updated_book.so_luong == 15, "Số lượng sách không tăng đúng."
            assert pdf_path.exists(), "File PDF không được tạo."
        except Exception as e:
            db.session.rollback()
            pytest.fail(f"Integration test failed: {str(e)}")
        finally:
            if pdf_path.exists():
                pdf_path.unlink()  # Dọn dẹp file PDF sau khi test


# Different Types of Assertions với kiểm tra ngoại lệ
def test_add_stock_to_book(warehouse_manager, book):
    """Kiểm tra hàm tăng số lượng sách (Unit Test)."""
    with app.app_context():
        original_quantity = book.so_luong
        try:
            update_book_quantity(book.id, 10)
            updated_book = Sach.query.get(book.id)

            # Assertions
            assert updated_book is not None
            assert updated_book.so_luong == original_quantity + 10
            assert isinstance(updated_book.so_luong, int)
            assert updated_book.so_luong > 0
        except SQLAlchemyError as e:
            db.session.rollback()
            pytest.fail(f"Error updating stock: {str(e)}")


# Passing Command-line Args in Pytest với validate đầu vào
def test_import_with_custom_min_quantity(
    warehouse_manager, book, inventory_rules, pytestconfig
):
    """Kiểm tra nhập sách với số lượng tối thiểu từ cmd (Unit Test)."""
    min_quantity = pytestconfig.getoption(
        "--min-quantity", default=inventory_rules.SL_NHAP_MIN
    )
    try:
        min_quantity = int(min_quantity)
        assert min_quantity > 0, "Số lượng tối thiểu phải lớn hơn 0"
    except (ValueError, AssertionError) as e:
        pytest.skip(f"Invalid min_quantity: {str(e)}")

    with app.app_context():
        try:
            if 5 < min_quantity:
                result = {
                    "success": False,
                    "alert": f"Số lượng nhập dưới {min_quantity}",
                }
            else:
                phieu_nhap = create_phieunhapsach(
                    quan_ly_kho_id=warehouse_manager.id,
                )
                create_chitietphieunhapsach(
                    phieu_nhap_id=phieu_nhap.id, sach_id=book.id, so_luong=5
                )
                update_book_quantity(book.id, 5)
                result = {"success": True, "alert": None}

            assert result["success"] == (
                5 >= min_quantity
            ), "Kết quả không khớp với điều kiện."
            if not result["success"]:
                assert (
                    result["alert"] == f"Số lượng nhập dưới {min_quantity}"
                ), "Thông báo lỗi không đúng."
        except SQLAlchemyError as e:
            db.session.rollback()
            pytest.fail(f"Database error: {str(e)}")


# Pytest-BDD với tái sử dụng fixture
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("./features/inventory.feature")


@given("quản lý kho đã đăng nhập", target_fixture="logged_in")
def warehouse_manager_logged_in(warehouse_manager):
    return warehouse_manager


@given("có một cuốn sách trong kho", target_fixture="book_data")
def book_in_stock(book):
    return {"book": book}


@when(
    parsers.parse("quản lý kho nhập sách với số lượng {quantity:d}"),
    target_fixture="import_result",
)
def import_book(logged_in, book_data, quantity):
    manager = logged_in["manager"]
    with app.app_context():
        try:
            phieu_nhap = create_phieunhapsach(quan_ly_kho_id=manager.id)
            create_chitietphieunhapsach(
                phieu_nhap_id=phieu_nhap.id,
                sach_id=book_data["book"].id,
                so_luong=quantity,
            )
            update_book_quantity(book_data["book"].id, quantity)
            return {"phieu_nhap": phieu_nhap, "success": True}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"phieu_nhap": None, "success": False, "error": str(e)}


@then("phiếu nhập sách được tạo và số lượng sách tăng")
def import_ticket_created_and_stock_increased(import_result, book_data):
    assert import_result[
        "success"
    ], f"Nhập sách thất bại: {import_result.get('error', 'Unknown error')}"
    phieu_nhap = import_result["phieu_nhap"]
    assert phieu_nhap is not None, "Phiếu nhập không được tạo."
    updated_book = Sach.query.get(book_data["book"].id)
    assert (
        updated_book.so_luong == book_data["book"].so_luong + 5
    ), f"Số lượng không tăng đúng: {updated_book.so_luong} != {book_data['book'].so_luong + 5}"
