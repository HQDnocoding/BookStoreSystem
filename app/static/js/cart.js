function addToCart(id, ten_sach, don_gia) {
    fetch('/api/cart', {
        method: "post",
        body: JSON.stringify({
            "id": id,
            "ten_sach": ten_sach,
            "don_gia": don_gia
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
}