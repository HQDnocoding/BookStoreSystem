import random

from locust import HttpUser, LoadTestShape, between, task


class WebsiteUser(HttpUser):
    wait_time = between(1, 5)  # Thời gian chờ giữa các tác vụ (1-5 giây)

    def on_start(self):
        """Mô phỏng đăng nhập khi người dùng bắt đầu"""
        self.client.post("/login/", data={"username": "admin1", "password": "123"})

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
        self.client.get("/cart/")
