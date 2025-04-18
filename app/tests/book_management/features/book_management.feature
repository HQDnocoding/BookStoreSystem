Feature: Quản lý sách
  Là một quản trị viên, tôi muốn quản lý thông tin sách trong hệ thống
  để đảm bảo dữ liệu sách luôn chính xác và cập nhật.

  Background:
    Given quản trị viên đã đăng nhập với vai trò "QUANLY"

  Scenario: Quản trị viên cập nhật thông tin sách thành công
    Given có một cuốn sách trong hệ thống với thông tin ban đầu:
      | Tên sách     | Đơn giá | Số lượng | Thể loại  | Tác giả  |
      | Old Book     | 250000  | 10       | Fiction   | Author A |
    When quản trị viên cập nhật thông tin sách thành:
      | Tên sách     | Đơn giá | Số lượng |
      | Updated Book | 275000  | 15       |
    Then thông tin sách được cập nhật trong hệ thống với các giá trị:
      | Tên sách     | Đơn giá | Số lượng |
      | Updated Book | 275000  | 15       |

  Scenario Outline: Quản trị viên cập nhật thông tin sách với nhiều giá trị khác nhau
    Given có một cuốn sách trong hệ thống với thông tin ban đầu:
      | Tên sách  | Đơn giá | Số lượng | Thể loại    | Tác giả  |
      | Test Book | 200000  | 5        | Non-Fiction | Author B |
    When quản trị viên cập nhật thông tin sách thành:
      | Tên sách   | Đơn giá   | Số lượng   |
      | <ten_sach> | <don_gia> | <so_luong> |
    Then thông tin sách được cập nhật trong hệ thống với các giá trị:
      | Tên sách   | Đơn giá   | Số lượng   |
      | <ten_sach> | <don_gia> | <so_luong> |

    Examples:
      | ten_sach       | don_gia | so_luong |
      | New Book Title | 300000  | 20       |
      | Short Title    | 150000  | 8        |
      | Special Book   | 500000  | 50       |

  Scenario: Quản trị viên cập nhật sách thất bại do thông tin không hợp lệ
    Given có một cuốn sách trong hệ thống với thông tin ban đầu:
      | Tên sách     | Đơn giá | Số lượng | Thể loại  | Tác giả  |
      | Valid Book   | 200000  | 10       | Fiction   | Author C |
    When quản trị viên cập nhật thông tin sách thành:
      | Tên sách | Đơn giá | Số lượng |
      | ""       | -10000  | -5       |
    Then hệ thống từ chối cập nhật và thông báo lỗi:
      | Thông báo lỗi                    |
      | Tên sách không được rỗng.        |
      | Đơn giá phải là số không âm.     |
      | Số lượng phải là số không âm.    |

  Scenario: Quản trị viên cập nhật sách không tồn tại
    Given không có sách nào trong hệ thống với ID "9999"
    When quản trị viên cố gắng cập nhật sách với ID "9999" thành:
      | Tên sách     | Đơn giá | Số lượng |
      | Ghost Book   | 300000  | 10       |
    Then hệ thống từ chối cập nhật và thông báo lỗi:
      | Thông báo lỗi                   |
      | Sách với ID 9999 không tồn tại  |

  Scenario: Quản trị viên chỉ cập nhật tên sách
  Given có một cuốn sách trong hệ thống với thông tin ban đầu:
    | Tên sách      | Đơn giá | Số lượng | Thể loại  | Tác giả  |
    | Original Book | 100000  | 20       | Mystery   | Author D |
  When quản trị viên cập nhật thông tin sách thành:
    | Tên sách  | Đơn giá | Số lượng |
    | New Title | 100000  | 20       |
  Then thông tin sách được cập nhật trong hệ thống với các giá trị:
    | Tên sách  | Đơn giá | Số lượng |
    | New Title | 100000  | 20       |