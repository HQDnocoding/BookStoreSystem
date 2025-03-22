import pytest

from app import app, db
from app.dao import get_frequency_stats, get_stats
from app.utils import create_pdf_export_freq, create_pdf_export_rev


# Test Naming and Test Discovery
def test_generate_revenue_report_success(admin_user, sales_data):
    """Kiểm tra tạo báo cáo doanh thu thành công (Unit Test)."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = admin_user.id  # Giả lập đăng nhập quản trị viên

        # Tạo báo cáo doanh thu
        with app.app_context():
            create_pdf_export_rev(
                month=3, year=2025, category=sales_data["the_loai"].id
            )

        # Assertions
        import os

        assert os.path.exists("DoanhThu_03_2025.pdf")  # File PDF được tạo
        assert os.path.getsize("DoanhThu_03_2025.pdf") > 0  # File không rỗng
        os.remove("DoanhThu_03_2025.pdf")  # Dọn dẹp


# Parametrized Testing
@pytest.mark.parametrize(
    "month, year, category_id, expected_total, expected_file",
    [
        (
            3,
            2025,
            1,
            350000,
            "DoanhThu_03_2025.pdf",
        ),  # Có dữ liệu, tổng doanh thu = 200000 + 150000
        (4, 2025, 1, 0, "DoanhThu_04_2025.pdf"),  # Không có dữ liệu
        (3, 2025, 999, 0, "DoanhThu_03_2025.pdf"),  # Thể loại không tồn tại
    ],
)
def test_revenue_report_with_different_filters(
    admin_user, sales_data, month, year, category_id, expected_total, expected_file
):
    """Kiểm tra báo cáo doanh thu với các bộ lọc khác nhau (Unit Test)."""
    with app.app_context():
        stats = get_stats(month, year, category_id)
        create_pdf_export_rev(month=month, year=year, category=category_id)

        # Assertions
        assert sum(stat["doanh_thu"] for stat in stats) == expected_total
        import os

        assert os.path.exists(expected_file)
        os.remove(expected_file)


# Skipping Tests and Markers
@pytest.mark.skipif(
    app.config.get("ENV") == "production",
    reason="Không chạy trong môi trường production",
)
def test_frequency_report_integration(admin_user, sales_data):
    """Kiểm tra toàn bộ luồng tạo báo cáo tần suất bán sách (Integration Test)."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = admin_user.id

        # Tạo báo cáo tần suất
        with app.app_context():
            stats = get_frequency_stats(
                month=3, year=2025, category=sales_data["the_loai"].id
            )
            create_pdf_export_freq(
                month=3, year=2025, category=sales_data["the_loai"].id
            )

        # Assertions
        assert len(stats) == 2  # Hai sách được bán
        assert stats[0]["so_luong"] == 2  # Book 1 bán 2 cuốn
        assert stats[1]["so_luong"] == 1  # Book 2 bán 1 cuốn
        import os

        assert os.path.exists("TanSuat_03_2025.pdf")
        os.remove("TanSuat_03_2025.pdf")


# Different Types of Assertions
def test_get_stats_no_data(admin_user):
    """Kiểm tra lấy thống kê khi không có dữ liệu (Unit Test)."""
    with app.app_context():
        stats = get_stats(month=1, year=2025, category=1)  # Không có dữ liệu tháng 1

        # Assertions
        assert isinstance(stats, list)  # Kiểm tra kiểu dữ liệu
        assert len(stats) == 0  # Kiểm tra độ dài
        assert stats == []  # Kiểm tra giá trị bằng
        assert not stats  # Kiểm tra falsy


# Passing Command-line Args in Pytest
def test_revenue_report_with_custom_month(admin_user, sales_data, pytestconfig):
    """Kiểm tra báo cáo doanh thu với tháng từ cmd (Unit Test)."""
    custom_month = int(pytestconfig.getoption("--month", default=3))
    with app.app_context():
        stats = get_stats(
            month=custom_month, year=2025, category=sales_data["the_loai"].id
        )
        create_pdf_export_rev(
            month=custom_month, year=2025, category=sales_data["the_loai"].id
        )

        # Assertions
        expected_total = 350000 if custom_month == 3 else 0
        assert sum(stat["doanh_thu"] for stat in stats) == expected_total
        import os

        assert os.path.exists(f"DoanhThu_{custom_month:02d}_2025.pdf")
        os.remove(f"DoanhThu_{custom_month:02d}_2025.pdf")


# Pytest-BDD
from pytest_bdd import given, scenarios, then, when

scenarios("reports.feature")


@given("quản trị viên đã đăng nhập")
def admin_logged_in(admin_user):
    return {"admin": admin_user}


@given("có dữ liệu bán hàng trong hệ thống")
def sales_data_available(sales_data):
    return {"sales": sales_data}


@when("quản trị viên tạo báo cáo tần suất bán sách")
def generate_frequency_report(admin_logged_in, sales_data_available):
    with app.app_context():
        stats = get_frequency_stats(
            month=3, year=2025, category=sales_data_available["sales"]["the_loai"].id
        )
        create_pdf_export_freq(
            month=3, year=2025, category=sales_data_available["sales"]["the_loai"].id
        )
    return {"stats": stats}


@then("báo cáo tần suất được tạo với dữ liệu chính xác")
def frequency_report_created(generate_frequency_report):
    stats = generate_frequency_report["stats"]
    assert len(stats) == 2
    assert stats[0]["so_luong"] == 2
    assert stats[1]["so_luong"] == 1
    import os

    assert os.path.exists("TanSuat_03_2025.pdf")
    os.remove("TanSuat_03_2025.pdf")
