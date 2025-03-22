Feature: Nhập sách
  Scenario: Quản lý kho nhập sách thành công
    Given quản lý kho đã đăng nhập
    And có một cuốn sách trong kho
    When quản lý kho nhập sách
    Then phiếu nhập sách được tạo và số lượng sách tăng
