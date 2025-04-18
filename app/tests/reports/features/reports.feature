Feature: Xem thống kê báo cáo
  Scenario: Quản trị viên tạo báo cáo tần suất bán sách thành công
    Given quản trị viên đã đăng nhập
    And có dữ liệu bán hàng trong hệ thống
    When quản trị viên tạo báo cáo tần suất bán sách
    Then báo cáo tần suất được tạo với dữ liệu chính xác
