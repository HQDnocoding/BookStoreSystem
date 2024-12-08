function addToCart(id, ten_sach, don_gia, bia_sach) {
    fetch('/api/cart', {
        method: "post",
        body: JSON.stringify({
            "id": id,
            "ten_sach": ten_sach,
            "don_gia": don_gia,
            "bia_sach": bia_sach
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        console.info(data)
        let d = document.getElementsByClassName("cart-counter")
        for (let i = 0; i<d.length;i++)
            d[i].innerText = data.total_quantity
    })
    console.info(bia_sach)
}

function updateCart(productId, obj){
    fetch(`/api/cart/${productId}`, {
        method: "put",
        body: JSON.stringify({
            "so_luong": obj.value
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        console.info(data)
        let d = document.getElementsByClassName("cart-counter")
        for (let i = 0; i<d.length;i++)
            d[i].innerText = data.total_quantity

        let d2 = document.getElementsByClassName("cart-amount")
        for (let i = 0; i<d2.length;i++)
            d2[i].innerText = data.total_amount.toLocaleString("en-US") + "₫"
    })
}

function deleteCart(productId){
    if(confirm("Bạn chắc chắn xoá không?")==true){
        fetch(`/api/cart/${productId}`, {
            method: "delete",
        }).then(res => res.json()).then(data => {
            console.info(data)
            let d = document.getElementsByClassName("cart-counter")
            for (let i = 0; i<d.length;i++)
                d[i].innerText = data.total_quantity

            let d2 = document.getElementsByClassName("cart-amount")
            for (let i = 0; i<d2.length;i++)
                d2[i].innerText = data.total_amount.toLocaleString("en-US")

            let c = document.getElementById(`cart${productId}`)
            c.style.display="none"
        }).catch(err => console.info(err))
    }
}

function changeQuantity(productId, delta, quantityInput) {
    let currentQuantity = parseInt(quantityInput.value);

    // Tính toán số lượng mới
    let newQuantity = currentQuantity + delta;

    // Lấy giá trị min và max từ các thuộc tính của input
    let minQuantity = parseInt(quantityInput.min);
    let maxQuantity = parseInt(quantityInput.max);

    // Kiểm tra các giới hạn
    if (newQuantity >= minQuantity && newQuantity <= maxQuantity) {
        quantityInput.value = newQuantity; // Cập nhật giá trị mới cho ô nhập liệu
        updateCart(productId, quantityInput)
    }
}