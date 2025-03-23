Feature: Xác thực và phân quyền
  Scenario: Nhân viên đăng nhập thành công
    Given có một người dùng với vai trò nhân viên
    When người dùng đăng nhập với thông tin đúng
    Then đăng nhập thành công và vai trò được xác nhận
