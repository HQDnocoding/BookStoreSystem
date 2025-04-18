class AuthenticationError(Exception):
    """Ngoại lệ cho các lỗi xác thực người dùng."""

    pass


class PasswordError(AuthenticationError):
    """Ngoại lệ cho các lỗi liên quan đến mật khẩu."""

    pass


class UserNotFoundError(AuthenticationError):
    """Ngoại lệ khi không tìm thấy người dùng."""

    pass


class AccountLockedError(AuthenticationError):
    """Ngoại lệ khi tài khoản bị khóa."""

    pass


class ValidationError(Exception):
    """Ngoại lệ khi dữ liệu không hợp lệ."""

    pass
