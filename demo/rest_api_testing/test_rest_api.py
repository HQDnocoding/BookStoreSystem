import requests

BASE_URL = "https://simple-books-api.glitch.me"
# Biến để lưu trữ access token sau khi đăng ký client. Token sẽ hết hạn trong 7 ngày.
ACCESS_TOKEN = "647f73c6fb8f05936f1abf4eec98e2dd497a1dd4c24848147e423e9ad06e15cc"

# def register_api_client(client_name, client_email):
#     """Đăng ký API client và trả về access token."""
#     url = f"{BASE_URL}/api-clients/"
#     payload = {
#         "clientName": client_name,
#         "clientEmail": client_email
#     }
#     response = requests.post(url, json=payload)
#     response.raise_for_status()  # Gây ra ngoại lệ cho các lỗi HTTP
#     return response.json().get("accessToken")

# def test_register_api_client():
#     """Kiểm tra đăng ký API client."""
#     global ACCESS_TOKEN
#     client_name = "TestClient"
#     client_email = "test.client@example.com"  # Đảm bảo email này chưa được dùng
#     ACCESS_TOKEN = register_api_client(client_name, client_email)
#     assert ACCESS_TOKEN is not None
#     assert isinstance(ACCESS_TOKEN, str)


def test_submit_order():
    """Kiểm tra việc tạo đơn hàng mới."""
    global ACCESS_TOKEN
    if not ACCESS_TOKEN:
        # Nếu chưa có token, hãy đăng ký client trước
        # ACCESS_TOKEN = register_api_client("TempClient", "temp.client@example.com")
        assert ACCESS_TOKEN is not None

    url = f"{BASE_URL}/orders"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    payload = {"bookId": 1, "customerName": "Test Customer"}
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 201
    assert response.headers["Content-Type"] == "application/json; charset=utf-8"
    data = response.json()
    assert "orderId" in data
    return data["orderId"]  # Trả về orderId để dùng cho các test khác


def test_get_all_orders():
    """Kiểm tra việc lấy danh sách tất cả đơn hàng."""
    global ACCESS_TOKEN
    if not ACCESS_TOKEN:
        # ACCESS_TOKEN = register_api_client("TempClient", "temp.client@example.com")
        assert ACCESS_TOKEN is not None

    url = f"{BASE_URL}/orders"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json; charset=utf-8"
    data = response.json()
    assert isinstance(data, list)


def test_get_order_by_id():
    """Kiểm tra việc lấy thông tin một đơn hàng cụ thể theo ID."""
    order_id = test_submit_order()  # Tạo một đơn hàng trước để lấy ID
    global ACCESS_TOKEN
    if not ACCESS_TOKEN:
        # ACCESS_TOKEN = register_api_client("TempClient", "temp.client@example.com")
        assert ACCESS_TOKEN is not None

    url = f"{BASE_URL}/orders/{order_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json; charset=utf-8"
    data = response.json()
    assert "id" in data
    assert data["id"] == order_id
    assert "bookId" in data
    assert "customerName" in data


def test_update_order():
    """Kiểm tra việc cập nhật thông tin một đơn hàng."""
    order_id = test_submit_order()  # Tạo một đơn hàng trước để cập nhật
    global ACCESS_TOKEN
    if not ACCESS_TOKEN:
        # ACCESS_TOKEN = register_api_client("TempClient", "temp.client@example.com")
        assert ACCESS_TOKEN is not None

    url = f"{BASE_URL}/orders/{order_id}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"customerName": "Updated Customer Name"}
    response = requests.patch(url, headers=headers, json=payload)
    assert response.status_code in [200, 204]  # Có thể trả về 200 hoặc 204 tùy API
    if response.status_code == 200:
        assert response.headers["Content-Type"] == "application/json; charset=utf-8"
        data = response.json()
        assert data["customerName"] == "Updated Customer Name"
    else:
        # Kiểm tra lại bằng cách GET order
        get_response = requests.get(f"{BASE_URL}/orders/{order_id}", headers=headers)
        assert get_response.status_code == 200
        assert get_response.json()["customerName"] == "Updated Customer Name"


def test_delete_order():
    """Kiểm tra việc xóa một đơn hàng."""
    order_id = test_submit_order()  # Tạo một đơn hàng trước để xóa
    global ACCESS_TOKEN
    if not ACCESS_TOKEN:
        # ACCESS_TOKEN = register_api_client("TempClient", "temp.client@example.com")
        assert ACCESS_TOKEN is not None

    url = f"{BASE_URL}/orders/{order_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.delete(url, headers=headers)
    assert response.status_code == 204

    # Kiểm tra lại xem đơn hàng đã bị xóa chưa
    get_response = requests.get(f"{BASE_URL}/orders/{order_id}", headers=headers)
    assert get_response.status_code == 404


# Các test cho endpoint /books (nếu bạn muốn)
def test_get_book_by_id():
    """Kiểm tra endpoint lấy thông tin sách theo ID."""
    url = f"{BASE_URL}/books/1"
    response = requests.get(url)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json; charset=utf-8"
    data = response.json()
    assert isinstance(data, dict)
    assert "id" in data
    assert "name" in data
    assert "author" in data


def test_get_book_list():
    """Kiểm tra endpoint lấy danh sách sách."""
    url = f"{BASE_URL}/books"
    response = requests.get(url)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json; charset=utf-8"
    data = response.json()
    assert isinstance(data, list)


def test_get_book_list_with_filter():
    """Kiểm tra endpoint lấy danh sách sách với bộ lọc."""
    url = f"{BASE_URL}/books?type=fiction&limit=5"
    response = requests.get(url)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json; charset=utf-8"
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5
    for book in data:
        assert book.get("type") == "fiction"  # Chú ý chữ hoa/thường có thể khác
    assert all(book.get("id") for book in data)
