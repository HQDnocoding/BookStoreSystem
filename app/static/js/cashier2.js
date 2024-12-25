// Hàm tìm đơn hàng
async function findOrder() {



    const id = document.getElementById('don-hang-id').value;

    if (!id) {
        alert('Vui lòng nhập mã đơn hàng');
        return;
    }

    try {
        const response = await fetch(`/admin/cashier2view/don_hang/${id}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const don_hang_data = await response.json();

            renderOrderDetails(don_hang_data);
        } else if (response.status === 404) {
            alert('Không tìm thấy đơn hàng');
        } else {
            alert('Đã xảy ra lỗi khi tìm đơn hàng');
        }
    } catch (error) {
        console.error('Lỗi khi gọi API:', error);
        alert('Không thể kết nối đến máy chủ');
    }
}

// Hàm hiển thị dữ liệu đơn hàng ra giao diện

var don_hang_id = -1
var ho_ten_kh = ''

function renderOrderDetails(don_hang_data) {

    don_hang_id = don_hang_data.don_hang_id
    ho_ten_kh = don_hang_data.ho_khach_hang + " " + don_hang_data.ten

    document.getElementById("customer-name").textContent = (don_hang_data.ten_khach_hang + " " + don_hang_data.ho_khach_hang) || 'Không xác định';
    document.getElementById("creation-date").textContent = don_hang_data.ngay_tao || 'Không xác định';

    const orderBooksTable = document.getElementById("order-books");
    orderBooksTable.innerHTML = '';
    var tong_tien = 0
    // Thêm từng sách trong đơn hàng vào bảng
    don_hang_data.sach.forEach((s, index) => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${s.ten_sach || 'Không xác định'}</td>
            <td>${s.the_loai || 'Không xác định'}</td>
            <td>${s.so_luong || 0}</td>
            <td>${s.don_gia || 0} VND</td>
        `;
        tong_tien += s.don_gia * s.so_luong
        orderBooksTable.appendChild(row);
    });
    document.getElementById('total-price').value = tong_tien





}

async function createInvoice(id_don_hang) {

    try {
        const response = await fetch(`/admin/cashier2view/don_hang/${id_don_hang}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            window.location.href = data.path
            alert('Hóa đơn đã được tạo thành công!');
        } else {
            alert('Đã xảy ra lỗi khi tạo hóa đơn');
        }
    } catch (error) {
        console.error('Lỗi khi gọi API:', error);
        alert('Không thể kết nối đến máy chủ');
    }
}

document.addEventListener('DOMContentLoaded', () => {

    document.getElementById('btn-pay2').addEventListener('click', function (event) {
    const totalPaid = parseFloat(document.getElementById('amount-paid').value) || 0;
    const totalAmount = parseFloat(
    document.getElementById('total-price').value
        .replace(/₫/g, '') // Loại bỏ ký hiệu "₫"
        .replace(/,/g, '') // Loại bỏ tất cả dấu phẩy
) || 0;



        const changeAmount = totalPaid - totalAmount;
       if (changeAmount <= 0) {
           event.preventDefault();
           alert('Không đủ tiền');
        } else {
            createInvoice(don_hang_id) ;
        }

    });

    document.getElementById('search-don-hang-btn').addEventListener('click', function () { findOrder() });
    document.getElementById('search-don-hang-btn').addEventListener('click', function () { findOrder() });

    document.getElementById('btn-change').addEventListener('click', function () {
        const totalPaid = parseFloat(document.getElementById('amount-paid').value.replace('₫', '').replace(',', '')) || 0;
        const totalAmount = parseFloat(document.getElementById('total-price').value.replace('₫', '').replace(',', '')) || 0;



        const changeAmount = totalPaid - totalAmount;

        if (changeAmount >= 0) {
            document.getElementById('btn-pay2').disabled = false
        } else {
            document.getElementById('btn-pay2').disabled = true
        }

        document.getElementById('change').value = (changeAmount > 0 ? changeAmount.toLocaleString() : '0') + '₫';
    });

});