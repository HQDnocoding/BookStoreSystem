Feature: Quản lý nhập sách
  Là một quản lý kho, tôi muốn nhập sách vào hệ thống để cập nhật số lượng tồn kho.

  Scenario: Nhập sách thành công
    Given quản lý kho đã đăng nhập
    And có một cuốn sách trong kho
    When quản lý kho nhập sách với số lượng 5
    Then phiếu nhập sách được tạo và số lượng sách tăng