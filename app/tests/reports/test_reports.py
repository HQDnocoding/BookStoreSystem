import os
from datetime import datetime

import pytest

from app import app, db
from app.dao import get_frequency_stats, get_stats
from app.utils import create_pdf_export_freq, create_pdf_export_rev


# Test Naming and Test Discovery => PASSED
def test_generate_revenue_report_success(test_client, admin_user, output_dir):
    """Kiểm tra tạo báo cáo doanh thu thành công (Unit Test)."""
    thang = 3
    nam = 2025
    the_loai = "Tất cả"

    # Giả lập dữ liệu thống kê (nếu cần thiết, hoặc sử dụng sales_data fixture)
    stat = get_stats(nam, thang, the_loai)

    expected_filename_base = f"DoanhThu_{thang:02d}_{nam}"
    output_filename = os.path.join(output_dir, f"{expected_filename_base}.pdf")

    create_pdf_export_rev(data=stat, file_name=output_filename, month=thang, year=nam)

    # Assertions
    assert os.path.exists(
        output_filename
    ), f"File PDF không được tạo tại: {output_filename}"
    assert os.path.getsize(output_filename) > 0, f"File PDF rỗng tại: {output_filename}"
    assert (
        os.path.basename(output_filename) == "DoanhThu_03_2025.pdf"
    ), f"Tên file không đúng: {os.path.basename(output_filename)}"

    # Dọn dẹp file sau test này
    os.remove(output_filename)


# Parametrized Testing => PASSED
@pytest.mark.parametrize(
    "thang, nam, ten_the_loai, expected_total, expected_filename",
    [
        (1, 2025, "Tất cả", 0.0, "DoanhThu_01_2025.pdf"),
        (
            2,
            2025,
            "Tình cảm",
            0.0,
            "DoanhThu_02_2025.pdf",
        ),  # Giả sử không có DL Tình cảm
        (3, 2025, "Phiêu lưu", 150000.0, "DoanhThu_03_2025.pdf"),  # Tổng doanh thu
        (4, 2025, "Trinh thám", 0.0, "DoanhThu_04_2025.pdf"),  # Tháng khác
    ],
)
def test_revenue_report_with_different_filters(
    test_client,
    admin_user,
    sales_data,
    thang,
    nam,
    ten_the_loai,
    expected_total,
    expected_filename,
    output_dir,
):
    """Kiểm tra báo cáo doanh thu với các bộ lọc khác nhau (Unit Test)."""
    stats = get_stats(thang=thang, nam=nam, ten_the_loai=ten_the_loai)
    expected_filename_base = f"DoanhThu_{thang:02d}_{nam}"
    output_filename = os.path.join(output_dir, f"{expected_filename_base}.pdf")
    create_pdf_export_rev(data=stats, file_name=output_filename, month=thang, year=nam)

    # Assertions
    assert stats[0][2] == expected_total

    assert os.path.exists(output_filename)
    os.remove(output_filename)


# Skipping Tests and Markers => SKIPPED
@pytest.mark.skipif(
    app.config.get("ENV") == "production",
    reason="Không chạy trong môi trường production",
)
def test_frequency_report_integration(app_context, admin_user, sales_data, output_dir):
    """Kiểm tra toàn bộ luồng tạo báo cáo tần suất bán sách (Integration Test)."""
    # Tạo báo cáo tần suất
    stats = get_frequency_stats(month=3, year=2025, ten_the_loai="Tất cả")
    expected_filename_base = f"TanSuat_{3:02d}_{2025}"
    output_filename = os.path.join(output_dir, f"{expected_filename_base}.pdf")

    create_pdf_export_freq(
        month=3,
        year=2025,
        data=stats,
        file_name=output_filename,
    )

    print(stats)
    # Assertions
    # Số lượng từng cuốn sách
    assert len(stats) == 3  # Ba sách được bán
    assert stats[0][3] == 2  # Book 1 bán 2 cuốn
    assert stats[1][3] == 1  # Book 2 bán 1 cuốn
    assert stats[2][3] == 1  # Book 3 bán 1 cuốn

    assert os.path.exists(output_filename)  # "TanSuat_03_2025.pdf"
    os.remove(output_filename)


# Different Types of Assertions
def test_get_stats_no_data(test_client, admin_user):
    """Kiểm tra lấy thống kê khi không có dữ liệu (Unit Test)."""
    stats = get_stats(
        thang=1, nam=2025, ten_the_loai="Tất cả"
    )  # Không có dữ liệu tháng 1

    # Assertions
    assert isinstance(stats, list)  # Kiểm tra kiểu dữ liệu
    assert stats[0][0] == "Không có dữ liệu"  # Kiểm tra không có dữ liệu
    assert stats == [["Không có dữ liệu", 0, 0.0, 0.0]]  # Kiểm tra giá trị bằng
    assert stats[0][1] == 0  # Kiểm tra số lượng


# Passing Command-line Args in Pytest
def test_revenue_report_with_custom_month(
    test_client, admin_user, sales_data, pytestconfig, output_dir
):
    """Kiểm tra báo cáo doanh thu với tháng từ cmd (Unit Test)."""
    custom_month = int(pytestconfig.getoption("--month", default=3))

    expected_filename_base = f"DoanhThu_{custom_month:02d}_{2025}"
    output_filename = os.path.join(output_dir, f"{expected_filename_base}.pdf")

    stats = get_stats(thang=custom_month, nam=2025, ten_the_loai="Tất cả")
    create_pdf_export_rev(
        month=custom_month,
        year=2025,
        data=stats,
        file_name=output_filename,
    )

    # Assertions
    expected_total = 234000 if custom_month == 3 else 0
    assert sum(stat[2] for stat in stats) == expected_total

    assert os.path.exists(output_filename)
    os.remove(output_filename)


# Pytest-BDD
from pytest_bdd import given, scenarios, then, when

scenarios("./features/reports.feature")


@given("quản trị viên đã đăng nhập", target_fixture="admin_logged_in")
def admin_logged_in(admin_user):
    return {"admin": admin_user}


@given("có dữ liệu bán hàng trong hệ thống", target_fixture="sales_data_available")
def sales_data_available(sales_data):
    return {"sales": sales_data}


@when(
    "quản trị viên tạo báo cáo tần suất bán sách",
    target_fixture="generate_frequency_report",
)
def generate_frequency_report(admin_logged_in, sales_data_available, output_dir):
    stats = get_frequency_stats(
        thang=3,
        nam=2025,
        ten_the_loai="Tất cả",
    )
    return {"stats": stats}


@then("báo cáo tần suất được tạo với dữ liệu chính xác")
def frequency_report_created(generate_frequency_report, output_dir):
    expected_filename_base = f"TanSuat_{3:02d}_{2025}"
    output_filename = os.path.join(output_dir, f"{expected_filename_base}.pdf")

    stats = generate_frequency_report["stats"]

    create_pdf_export_freq(
        month=3,
        year=2025,
        data=stats,
        file_name=output_filename,
    )

    # for idx, (id_sach, ten_sach, the_loai, so_luong, ti_le) in enumerate(stats):
    #     print(f"\n{ten_sach}: {so_luong} ({ti_le}%)")

    assert len(stats) == 3
    assert stats[0][3] == 2  # số lượng 'Naruto'
    assert stats[1][3] == 1  # số lượng 'Hunter x Hunter'
    assert stats[2][3] == 1  # số lượng 'Ú Òa, Mèo Đâu Rồi?'

    assert os.path.exists(output_filename)  # TanSuat_03_2025.pdf
    os.remove(output_filename)
