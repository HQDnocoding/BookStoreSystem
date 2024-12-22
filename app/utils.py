from app.models import DonHang


def cart_stats(cart):
    total_amount, total_quantity = 0,0

    if cart:
        for c in cart.values():
            total_quantity+=c['so_luong']
            total_amount+=c['so_luong']*c['don_gia']

    return {
        "total_amount":total_amount,
        "total_quantity":total_quantity
    }


def count_orders(khach_hang_id):
    return DonHang.query.filter_by(khach_hang_id=khach_hang_id).count()