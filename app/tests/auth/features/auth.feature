# features/auth.feature
Feature: Kiểm tra hệ thống đăng nhập
  Là một người dùng hệ thống
  Tôi muốn đăng nhập vào hệ thống
  Để có thể sử dụng các chức năng tương ứng với vai trò của mình

  Background:
    Given hệ thống đã khởi tạo dữ liệu người dùng

  Scenario Outline: Đăng nhập vào hệ thống với các tài khoản khác nhau
    Given người dùng nhập "<username>" và "<password>"
    When hệ thống kiểm tra thông tin đăng nhập
    Then người dùng sẽ nhận kết quả "<kết quả mong đợi>"

    Examples:
      | username   | password   | kết quả mong đợi                        |
      | admin1     | 123        | đăng nhập thành công                    |
      | admin1     | wrongpass  | lỗi "Không tìm thấy người dùng"         |
      | employee1  | 123        | đăng nhập thành công                    |
      | customer1  | 123        | đăng nhập thành công                    |
      | warehouse1 | 123        | đăng nhập thành công                    |
      | nonexist   | anypass    | lỗi "Không tìm thấy người dùng"         |
      | employee1  | __         | lỗi "Không tìm thấy người dùng"         |
      | __         | 123        | lỗi "Không tìm thấy người dùng"         |

  Scenario: Đăng nhập với vai trò nhân viên
    Given một người dùng có vai trò là nhân viên
    When người dùng đăng nhập bằng thông tin đăng nhập chính xác
    Then đăng nhập thành công và vai trò đã được xác minh
