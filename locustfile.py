import random

from locust import HttpUser, LoadTestShape, between, task


class WebsiteUser(HttpUser):
    wait_time = between(1, 5)  # Thời gian chờ giữa các tác vụ (1-5 giây)

    def on_start(self):
        """Mô phỏng đăng nhập khi người dùng bắt đầu"""
        self.client.post("/login", data={"username": "admin1", "password": "123"})

    @task(3)
    def view_homepage(self):
        """Truy cập trang chủ"""
        self.client.get("/")

    @task(3)
    def view_item(self):
        """Xem chi tiết ngẫu nhiên của sách"""
        for item_id in range(10):
            self.client.get(f"/books/{item_id}", name="/books")

    @task(2)
    def browse_shop(self):
        """Duyệt cửa hàng với tham số danh mục ngẫu nhiên"""
        categories = ["Trinh thám", "Tình cảm", "Kinh tế"]
        category = random.choice(categories)
        self.client.get(f"/shop/{category}")

    @task(2)
    def view_profile(self):
        """Truy cập trang thông tin cá nhân"""
        self.client.get("/profile")

    @task(1)
    def add_to_cart(self):
        """Thêm sản phẩm vào giỏ hàng"""
        product_id = 1
        self.client.post(
            "/api/cart",
            json={
                "id": product_id,
                "ten_sach": "Conan",
                "don_gia": 25000,
                "so_luong": 1,
                "bia_sach": "https://res.cloudinary.com/dmbvjjg5a/image/upload/v1735027448/upload/bia_sach/c5aaxgoimjhiv5uqi1md.jpg",
                "so_luong_con_lai": 10,
            },
        )

    @task(1)
    def view_cart(self):
        """Xem giỏ hàng"""
        self.client.get("/cart")


class CustomLoadShape(LoadTestShape):
    """Tăng giảm người dùng theo các giai đoạn mô phỏng hành vi người dùng thực tế."""

    stages = [
        {"duration": 30, "users": 10, "spawn_rate": 2},  # * Start with 10 users
        {"duration": 60, "users": 50, "spawn_rate": 5},  # * Ramp up to 50 users
        {"duration": 30, "users": 20, "spawn_rate": 2},  # * Drop to 20 users
        {"duration": 40, "users": 80, "spawn_rate": 10},  # * Spike to 80 users
        {"duration": 20, "users": 30, "spawn_rate": 3},  # * Drop to 30 users
        {"duration": 30, "users": 0, "spawn_rate": 5},  # * Gradual shutdown
    ]

    def tick(self):
        """Determines how many users should be active at a given time."""
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]
            run_time -= stage["duration"]

        return None  # Dừng test khi hoàn thành toàn bộ stages


class BreakpointStressShape(LoadTestShape):
    """
    Stress test để xác định điểm phá vỡ của hệ thống.
    Tăng đều người dùng theo từng chu kỳ, không có giai đoạn nghỉ.
    """

    step_time = 60  # Tăng mỗi 60 giây
    step_load = 200  # Mỗi lần tăng thêm 200 người dùng
    spawn_rate = 50  # Tốc độ sinh người dùng
    max_users = 5000  # Tối đa để test điểm gãy

    def tick(self):
        run_time = self.get_run_time()
        current_step = run_time // self.step_time
        user_count = (current_step + 1) * self.step_load

        if user_count > self.max_users:
            return None  # Dừng test khi đạt ngưỡng

        return int(user_count), self.spawn_rate
