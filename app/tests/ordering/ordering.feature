Feature: Đặt sách
  Scenario: Khách hàng thêm sách vào giỏ hàng thành công
    Given khách hàng đã đăng nhập
    And có một cuốn sách trong kho
    When khách hàng thêm sách vào giỏ hàng
    Then giỏ hàng phải chứa sách vừa thêm
