Feature: Quản lý sách
  Scenario: Quản trị viên cập nhật thông tin sách thành công
    Given quản trị viên đã đăng nhập
    And có một cuốn sách trong hệ thống
    When quản trị viên cập nhật thông tin sách
    Then thông tin sách được cập nhật trong hệ thống
