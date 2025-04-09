Feature: Kiểm tra chức năng giỏ hàng
  Là một khách hàng
  Tôi muốn thêm sách vào giỏ hàng
  Để có thể tiến hành thanh toán sau này

  Background:
    Given hệ thống đã khởi tạo dữ liệu sản phẩm và giỏ hàng

  Scenario Outline: Thêm sách vào giỏ hàng với các điều kiện khác nhau
    Given khách hàng đăng nhập với tài khoản "<username>"
    And giỏ hàng hiện có "<số lượng sách hiện tại>" sản phẩm
    And có sẵn "<số lượng tồn kho>" sách trong kho
    When khách hàng thêm "<số lượng thêm>" sách vào giỏ hàng
    Then hệ thống phản hồi "<kết quả mong đợi>"

    Examples:
      | username  | số lượng sách hiện tại | số lượng tồn kho | số lượng thêm | kết quả mong đợi                                  |
      | customer1 | 0                      | 10               | 2             | Thêm thành công, giỏ hàng có 2 sách               |
      | customer1 | 3                      | 10               | 2             | Thêm thành công, giỏ hàng có 5 sách               |
      | customer1 | 0                      | 1                | 2             | Số lượng sách trong kho không đủ                  |
      | customer1 | 8                      | 10               | 5             | Số lượng sách vượt quá giới hạn                   |
      | customer1 | 0                      | 0                | 1             | Sách đã hết hàng                                  |
