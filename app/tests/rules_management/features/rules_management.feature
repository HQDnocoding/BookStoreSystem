Feature: Thay đổi quy định
  Scenario: Quản trị viên thay đổi quy định thành công
    Given quản trị viên đã đăng nhập
    And có quy định hiện tại trong hệ thống
    When quản trị viên thay đổi quy định
    Then quy định được cập nhật trong hệ thống
