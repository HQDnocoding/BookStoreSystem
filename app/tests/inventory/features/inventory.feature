Feature: Quản lý kho - Cập nhật số lượng sách

  Background:
    Given quản trị viên đã đăng nhập với vai trò "QUANLYKHO"

  Scenario: Quản lý kho cập nhật số lượng sách thành công
    Given có một cuốn sách trong kho
    When quản lý kho cập nhật số lượng sách với số lượng 5
    Then số lượng sách tăng thêm 5

  Scenario: Quản lý kho nhập số lượng âm
    Given có một cuốn sách trong kho
    When quản lý kho cập nhật số lượng sách với số lượng -3
    Then hệ thống báo lỗi và không cập nhật số lượng sách
