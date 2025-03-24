from locust import HttpUser, between, events, task
from locust.runners import MasterRunner


class BookstoreUser(HttpUser):
    # Thời gian chờ giữa các tác vụ (từ 1 đến 5 giây)
    wait_time = between(1, 5)

    # Giả lập đăng nhập khi người dùng bắt đầu
    def on_start(self):
        self.client.post("/login", json={"username": "customer1", "password": "123"})

    # Tác vụ 1: Tìm kiếm sách
    @task(3)  # Tỷ lệ chạy cao hơn (3 lần thường xuyên hơn các task khác)
    def search_books(self):
        self.client.get("/books/search?q=python")

    # Tác vụ 2: Thêm sách vào giỏ hàng
    @task(2)
    def add_to_cart(self):
        self.client.post("/cart/add", json={"book_id": 1, "quantity": 1})

    # Tác vụ 3: Thanh toán
    @task(1)
    def checkout(self):
        self.client.post(
            "/payment/checkout", json={"method": "OFFLINE_PAY", "total": 150000}
        )

    # Tác vụ 4: Xem báo cáo (chỉ dành cho quản trị viên)
    @task(1)
    def view_report(self):
        self.client.get("/admin/reports?month=3&year=2025")


# Sự kiện ghi lại khi hệ thống bắt đầu lỗi
@events.request.add_listener
def my_request_handler(name, response, exception):
    if exception:
        print(f"Request to {name} failed with exception {exception}")
    else:
        print(f"Successfully made a request to: {name}")
        print(f"The response was {response.text}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    if not isinstance(environment.runner, MasterRunner):
        print("Beginning test setup")
    else:
        print("Started test from Master node")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    if not isinstance(environment.runner, MasterRunner):
        print("Cleaning up test data")
    else:
        print("Stopped test from Master node")
