document.addEventListener('DOMContentLoaded', () => {
    // Tải giỏ hàng khi trang được tải
    if (window.location.pathname === '/admin/cashierview/'){
    loadCart();
    }


    // Gắn sự kiện cho ô tìm kiếm
document.addEventListener('keydown', function(event) {
    if (event.key === 'F3') {
        // Ngừng hành động mặc định của phím F3 (tránh tìm kiếm của trình duyệt)
        event.preventDefault();

        // Focus vào ô tìm kiếm
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }
});
document.addEventListener('keydown', function (event) {
        // Kiểm tra nếu phím nhấn là Esc (keyCode = 27)
        if (event.key === "Escape") {
            document.getElementById('search-input').value = '';  // Làm rỗng ô tìm kiếm
            document.getElementById('search-results').innerHTML = '';  // Xóa kết quả tìm kiếm
        }
});
document.getElementById('search-input').addEventListener('input', function () {


        const query = this.value.trim();
        if (query) {
            searchProducts(query);
        } else {
            document.getElementById('search-results').innerHTML = '';
        }
});

document.addEventListener('click', function (event) {
    if (event.target.classList.contains('add-to-cart-btn')) {
        const productId = event.target.dataset.id;
        const productName = event.target.dataset.name;
        const productPrice = parseFloat(event.target.dataset.price);
        const productImage = event.target.dataset.image;
        const productTheLoai = event.target.dataset.theloai;

        // Thêm sản phẩm vào giỏ hàng
        addToCart(productId, productName, productPrice, productImage,productTheLoai);
        loadCart()
    }
});


    // Xử lý nút xóa giỏ hàng
document.getElementById('clear-cart-btn').addEventListener('click', clearCart);
});
document.getElementById("amount-paid").addEventListener("keydown", function(event) {
    // Kiểm tra nếu phím nhấn là Enter (keyCode 13)
    if (event.key === "Enter") {
        event.preventDefault();

        const amountPaid = parseFloat(document.getElementById("amount-paid").value) || 0;
        const totalPrice = parseFloat(document.getElementById("total-price").value) || 0;

        const change = amountPaid - totalPrice;

        if(change>=0){
            document.getElementById('btn-pay').disabled=false
        }else{
        document.getElementById('btn-pay').disabled=true
        }

        document.getElementById("change").value = change >= 0 ? change : 0;
    }
});

document.getElementById('btn-pay').addEventListener('click',function(event){

     if(change>=0){
           event.preventDefault();
           alert('Không đủ tiền');
        }else{
            fetch('/admin/cashierview/cart/cash')
            .then(response=>
            window.location.href=response)
            .catch(err=>console.error(err))
        }
})


// Hàm tải giỏ hàng
function loadCart() {
    fetch('cart')
        .then(res => res.json())
        .then(data => {
            console.log("Dữ liệu giỏ hàng tải được:", data);

            if (data.cart && data.cart.length === 0) {
                renderCart([]);
                updateCartSummary(0, 0);
                document.getElementById('amount-paid').value=""
                return;
            }

            renderCart(data.cart);
            updateCartSummary(data.total_quantity, data.total_amount);
        })
        .catch(err => console.error('Lỗi khi tải giỏ hàng:', err));
}





document.getElementById('btn-change').addEventListener('click', function () {
        const totalPaid = parseFloat(document.getElementById('amount-paid').value.replace('₫', '').replace(',', '')) || 0;
        const totalAmount = parseFloat(document.getElementById('total-price').value.replace('₫', '').replace(',', '')) || 0;

        const changeAmount = totalPaid - totalAmount;
        if(changeAmount>=0) {
        document.getElementById('btn-pay').disabled=false
        }else{
        document.getElementById('btn-pay').disabled=true
        }
        document.getElementById('change').value = (changeAmount > 0 ? changeAmount.toLocaleString() : '0') + '₫';
    });



// Hàm tìm kiếm sản phẩm
function searchProducts(query) {
    fetch(`search?query=${query}`)
        .then(res => res.json())
        .then(products => {
            const resultsList = document.getElementById('search-results');
            resultsList.innerHTML = '';

            products.forEach(product => {
                resultsList.innerHTML += `
                    <li class="list-group-item d-flex align-items-center">
                        <img src="${product.image}" alt="${product.name}" class="img-thumbnail mr-3" style="width: 60px; height: 60px;">
                        <div class="flex-grow-1">
                            <h6 class="mb-1">${product.name}</h6>
                            <small class="text-muted">${product.price}₫</small>
                        </div>
                        <button class="btn btn-sm btn-primary add-to-cart-btn"
                            data-id="${product.id}"
                            data-name="${product.name}"
                            data-price="${product.price}"
                            data-image="${product.image}"
                            data-theloai="${product.the_loai_id}">
                            Thêm
                        </button>
                    </li>`;
            });

             if (products.length === 0) {
                resultsList.innerHTML = `
                    <li class="list-group-item text-center text-muted">
                        Không tìm thấy sản phẩm nào.
                    </li>`;
            } else {
                // Gán focus vào phần tử đầu tiên trong danh sách
                const firstResult = resultsList.querySelector('.list-group-item');
                if (firstResult) {
                    firstResult.focus();
                }
            }
        })
        .catch(err => console.error('Lỗi khi tìm kiếm sản phẩm:', err));
}


async function addToCart(productId, productName, productPrice, productImage,theLoaiId) {
    try {
        // Gửi yêu cầu thêm sản phẩm
        const response = await fetch('/admin/cashierview/cart', {
            method: 'POST',
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                id: productId,
                ten_sach: productName,
                don_gia: productPrice,
                bia_sach: productImage,
                the_loai_id:theLoaiId,
                so_luong: 1
            })
        });

        const data = await response.json();
        console.log("Dữ liệu trả về từ server:", data);

        loadCart()
    } catch (error) {
        console.error('Lỗi khi thêm sản phẩm vào giỏ hàng:', error);
    }
}



// Hàm xóa toàn bộ giỏ hàng
function clearCart() {
    fetch('/admin/cashierview/cart', { method: 'DELETE' })
        .then(() => {
            loadCart()
            document.getElementById('change').value =0
        });
}

function renderCart(cart) {
    const cartItems = document.getElementById("cart-items");
    cartItems.innerHTML = ""; // Xóa nội dung cũ

    if (cart.length === 0) {
        cartItems.innerHTML = '<li class="list-group-item text-center">Giỏ hàng trống!</li>';
        return;
    }

    cart.forEach(item => {
        const cartItem = document.createElement("li");
        cartItem.classList.add("list-group-item", "d-flex", "align-items-center");

        cartItem.innerHTML = `
            <img src="${item.bia_sach}" alt="${item.ten_sach}" class="img-thumbnail" style="width: 50px; height: 50px; object-fit: cover;">
            <div class="ml-3" style="flex: 1;">
                <h6 class="mb-0">${item.ten_sach}</h6>
                <small class="text-muted">${item.don_gia.toLocaleString()} VND</small>
            </div>
            <div class="d-flex align-items-center">
                <button class="btn btn-sm btn-secondary" onclick="updateCart(${item.id}, ${item.so_luong - 1})">-</button>
                <span class="mx-2">${item.so_luong}</span>
                <button class="btn btn-sm btn-secondary" onclick="updateCart(${item.id}, ${item.so_luong + 1})">+</button>
                <button class="btn btn-sm btn-danger ml-2" onclick="removeFromCart(${item.id})">X</button>
            </div>
        `;

        cartItems.appendChild(cartItem);
    });
}



function updateCartView(cart) {
    const cartItems = document.getElementById('cart-items');
    cartItems.innerHTML = ''; // Xóa nội dung cũ

    for (const productId in cart) {
        const item = cart[productId];
        cartItems.innerHTML += `
            <li class="list-group-item d-flex align-items-center">
                <img src="${item.bia_sach}" alt="${item.ten_sach}" class="img-thumbnail mr-3" style="width: 50px; height: 50px;">
                <div class="flex-grow-1">
                    <h6 class="mb-1">${item.ten_sach}</h6>
                    <small class="text-muted">Giá: ${item.don_gia}₫</small>
                </div>
                <span class="badge badge-primary badge-pill">${item.so_luong}</span>
            </li>`;
    }

    if (Object.keys(cart).length === 0) {
        cartItems.innerHTML = `
            <li class="list-group-item text-center text-muted">
                Giỏ hàng trống.
            </li>`;
    }

    // Cập nhật tổng tiền
    const totalPrice = document.getElementById('total-price');
    totalPrice.value = Object.values(cart).reduce((sum, item) => sum + item.don_gia * item.so_luong, 0) + '₫';
}

async function updateCart(productId, newQuantity) {
    if (newQuantity < 1) {
        // Nếu số lượng nhỏ hơn 1, xóa sản phẩm khỏi giỏ hàng
        removeFromCart(productId);
        return;
    }

    try {
        // Gửi yêu cầu cập nhật số lượng sản phẩm
        const response = await fetch(`/admin/cashierview/cart/${productId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ so_luong: newQuantity }) // Cập nhật số lượng mới
        });

        const data = await response.json();
        console.log('Cập nhật sản phẩm trong giỏ hàng:', data);

        loadCart();
    } catch (error) {
        console.error('Lỗi khi cập nhật số lượng sản phẩm:', error);
    }
}



function removeFromCart(productId) {
    fetch(`/admin/cashierview/cart/${productId}`, { method: 'DELETE' })
    .then(response => response.json())
    .then(data => {
        console.info("Đã xóa sản phẩm:", data.cart);
        loadCart()
    })
    .catch(error => console.error("Lỗi khi xóa sản phẩm:", error));
}


function updateCartSummary(totalQuantity, totalPrice) {
    // Cập nhật tổng số lượng sản phẩm trong giỏ hàng
    const quantityElement = document.getElementById('total-quantity');
    if (quantityElement) {
        quantityElement.textContent = totalQuantity;
    }

    // Cập nhật tổng số tiền trong giỏ hàng
    const priceElement = document.getElementById('total-price');
    if (priceElement) {
        priceElement.value = `${totalPrice.toLocaleString()}₫`;
    }
}



