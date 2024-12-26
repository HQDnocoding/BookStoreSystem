function addToCart(id, ten_sach, don_gia, bia_sach, quantity = 1, so_luong_con_lai) {
    console.log({
    "id": id,
    "ten_sach": ten_sach,
    "don_gia": don_gia,
    "bia_sach": bia_sach,
    "so_luong": quantity,
    "so_luong_con_lai": so_luong_con_lai
});
    fetch('/api/cart', {
        method: "post",
        body: JSON.stringify({
            "id": id,
            "ten_sach": ten_sach,
            "don_gia": don_gia,
            "bia_sach": bia_sach,
            "so_luong": quantity,
            "so_luong_con_lai": so_luong_con_lai
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        console.info(data);
        if (data.alert) {
            alert(data.alert);
        }

        let d = document.getElementsByClassName("cart-counter");
        for (let i = 0; i < d.length; i++) {
            d[i].innerText = data.total_quantity;
        }
    }).catch(error => {
        console.error('Có lỗi xảy ra:', error);
    });
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
        if (data.old_quantity) {
            let d = document.getElementById(`cartQuantity${data.p_id}`);
            d.value=data.old_quantity;
            alert(" KHÔNG đủ số lượng sách ");
            //cartQuantity{{ c.id }}
        }
        else{
            let d = document.getElementsByClassName("cart-counter")
            for (let i = 0; i<d.length;i++)
                d[i].innerText = data.total_quantity

            let d2 = document.getElementsByClassName("cart-amount")
            for (let i = 0; i<d2.length;i++)
                d2[i].innerText = data.total_amount.toLocaleString("en-US") + "₫"
        }
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

function changeInputNumericValue(delta, quantityInput){
    let quantity = parseInt(quantityInput.value);

    let newQuantity = quantity+delta;

    let minQuantity = parseInt(quantityInput.min);
    let maxQuantity = parseInt(quantityInput.max);

    if (newQuantity >= minQuantity && newQuantity <= maxQuantity) {
        quantityInput.value = newQuantity; // Cập nhật giá trị mới cho ô nhập liệu
    }
}