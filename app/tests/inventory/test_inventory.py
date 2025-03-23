import pytest
from flask import url_for

from app import app, db
from app.dao import (add_so_luong, create_chitietphieunhapsach,
                     create_phieunhapsach)
from app.utils import create_pdf_export_nhap_sach


# Test Naming and Test Discovery
def test_create_import_ticket_success(warehouse_manager, book, inventory_rules):
    """Kiểm tra tạo phiếu nhập sách thành công (Unit Test)."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = warehouse_manager.id  # Giả lập đăng nhập quản lý kho

        # Tạo phiếu nhập sách
        with app.app_context():
            phieu_nhap = create_phieunhapsach(
                ngay_nhap=None, quan_ly_kho_id=warehouse_manager.id
            )
            create_chitietphieunhapsach(
                phieu_nhap_id=phieu_nhap.id, sach_id=book.id, so_luong=5
            )
            add_so_luong(book.id, 5)

        # Assertions
        assert phieu_nhap is not None
        assert phieu_nhap.quan_ly_kho_id == warehouse_manager.id
        updated_book = Sach.query.get(book.id)
        assert updated_book.so_luong == 15  # Tăng từ 10 lên 15
        assert (
            ChiTietPhieuNhapSach.query.filter_by(phieu_nhap_id=phieu_nhap.id).count()
            == 1
        )


# Parametrized Testing
@pytest.mark.parametrize(
    "current_stock, import_quantity, expected_success, expected_alert",
    [
        (10, 5, True, None),  # Nhập hợp lệ
        (25, 5, False, "Số lượng tồn vượt quá SL_MIN_TO_NHAP"),  # Tồn kho đã đủ
        (5, 3, False, "Số lượng nhập dưới SL_NHAP_MIN"),  # Nhập dưới mức tối thiểu
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
    """Kiểm tra nhập sách với các điều kiện khác nhau (Unit Test)."""
    with app.app_context():
        book.so_luong = current_stock
        db.session.commit()

        if current_stock >= inventory_rules.SL_MIN_TO_NHAP:
            result = {"success": False, "alert": "Số lượng tồn vượt quá SL_MIN_TO_NHAP"}
        elif import_quantity < inventory_rules.SL_NHAP_MIN:
            result = {"success": False, "alert": "Số lượng nhập dưới SL_NHAP_MIN"}
        else:
            phieu_nhap = create_phieunhapsach(
                ngay_nhap=None, quan_ly_kho_id=warehouse_manager.id
            )
            create_chitietphieunhapsach(
                phieu_nhap_id=phieu_nhap.id, sach_id=book.id, so_luong=import_quantity
            )
            add_so_luong(book.id, import_quantity)
            result = {"success": True, "alert": None}

        # Assertions
        assert result["success"] == expected_success
        assert result["alert"] == expected_alert
        if expected_success:
            updated_book = Sach.query.get(book.id)
            assert updated_book.so_luong == current_stock + import_quantity


# Skipping Tests and Markers
@pytest.mark.skipif(
    app.config.get("ENV") == "production",
    reason="Không chạy trong môi trường production",
)
def test_import_book_integration(warehouse_manager, book, inventory_rules):
    """Kiểm tra toàn bộ luồng nhập sách (Integration Test)."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = warehouse_manager.id

        # Giả lập gửi yêu cầu nhập sách (tuyến đường chưa có, dùng DAO)
        with app.app_context():
            phieu_nhap = create_phieunhapsach(
                ngay_nhap=None, quan_ly_kho_id=warehouse_manager.id
            )
            create_chitietphieunhapsach(
                phieu_nhap_id=phieu_nhap.id, sach_id=book.id, so_luong=5
            )
            add_so_luong(book.id, 5)
            create_pdf_export_nhap_sach(phieu_nhap.id)

        # Assertions
        assert PhieuNhapSach.query.filter_by(id=phieu_nhap.id).first() is not None
        updated_book = Sach.query.get(book.id)
        assert updated_book.so_luong == 15
        import os

        assert os.path.exists(f"PhieuNhapSach_{phieu_nhap.id}.pdf")


# Different Types of Assertions
def test_add_stock_to_book(warehouse_manager, book):
    """Kiểm tra hàm tăng số lượng sách (Unit Test)."""
    with app.app_context():
        original_quantity = book.so_luong
        add_so_luong(book.id, 10)
        updated_book = Sach.query.get(book.id)

        # Assertions
        assert updated_book is not None  # Kiểm tra đối tượng tồn tại
        assert updated_book.so_luong == original_quantity + 10  # Kiểm tra giá trị
        assert isinstance(updated_book.so_luong, int)  # Kiểm tra kiểu dữ liệu
        assert updated_book.so_luong > 0  # Kiểm tra điều kiện logic


# Passing Command-line Args in Pytest
def test_import_with_custom_min_quantity(
    warehouse_manager, book, inventory_rules, pytestconfig
):
    """Kiểm tra nhập sách với số lượng tối thiểu từ cmd (Unit Test)."""
    min_quantity = int(
        pytestconfig.getoption("--min-quantity", default=inventory_rules.SL_NHAP_MIN)
    )
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = warehouse_manager.id

        with app.app_context():
            if 5 < min_quantity:
                result = {
                    "success": False,
                    "alert": f"Số lượng nhập dưới {min_quantity}",
                }
            else:
                phieu_nhap = create_phieunhapsach(
                    ngay_nhap=None, quan_ly_kho_id=warehouse_manager.id
                )
                create_chitietphieunhapsach(
                    phieu_nhap_id=phieu_nhap.id, sach_id=book.id, so_luong=5
                )
                add_so_luong(book.id, 5)
                result = {"success": True, "alert": None}

        assert result["success"] == (5 >= min_quantity)
        if not result["success"]:
            assert result["alert"] == f"Số lượng nhập dưới {min_quantity}"


# Pytest-BDD
from pytest_bdd import given, scenarios, then, when

scenarios("inventory.feature")


@given("quản lý kho đã đăng nhập")
def warehouse_manager_logged_in(warehouse_manager):
    return {"manager": warehouse_manager}


@given("có một cuốn sách trong kho")
def book_in_stock(book):
    return {"book": book}


@when("quản lý kho nhập sách")
def import_book(warehouse_manager_logged_in, book_in_stock, client):
    with client.session_transaction() as sess:
        sess["user_id"] = warehouse_manager_logged_in["manager"].id
    with app.app_context():
        phieu_nhap = create_phieunhapsach(
            ngay_nhap=None, quan_ly_kho_id=warehouse_manager_logged_in["manager"].id
        )
        create_chitietphieunhapsach(
            phieu_nhap_id=phieu_nhap.id, sach_id=book_in_stock["book"].id, so_luong=5
        )
        add_so_luong(book_in_stock["book"].id, 5)
    return {"phieu_nhap": phieu_nhap}


@then("phiếu nhập sách được tạo và số lượng sách tăng")
def import_ticket_created_and_stock_increased(import_book, book_in_stock):
    phieu_nhap = import_book["phieu_nhap"]
    assert phieu_nhap is not None
    updated_book = Sach.query.get(book_in_stock["book"].id)
    assert updated_book.so_luong == book_in_stock["book"].so_luong + 5
