Feature: Bán sách
  Scenario: Nhân viên bán sách tại cửa hàng thành công
    Given nhân viên đã đăng nhập
    And có một cuốn sách trong kho
    When nhân viên bán sách tại cửa hàng
    Then hóa đơn được tạo và số lượng sách giảm
