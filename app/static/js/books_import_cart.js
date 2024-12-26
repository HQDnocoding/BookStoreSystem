

function addBook(id, ten_sach, bia_sach, so_luong){
    console.log({
        "id": id,
        "ten_sach": ten_sach,
        "bia_sach": bia_sach,
        "so_luong": so_luong
    })
    fetch('/admin/nhapphieuview/api/cart',{
        method:"post",
        body: JSON.stringify({
            "id": id,
            "ten_sach": ten_sach,
            "bia_sach": bia_sach,
            "so_luong": so_luong
        }),
        headers:{
            "Content-Type":"application/json"
        }
    }).then(res=>res.json()).then(data =>{
        console.info(data)
        if (data["add"] && Object.keys(data["add"]).length > 0) {
            updateCart(data["add"]);
        }
        if (data["error"] && Object.keys(data["error"]).length > 0) {
            alert(data["error"]);
        }
    })
}

function updateBook(product_id, obj){
console.info("updateBook!!!")
    fetch(`/admin/nhapphieuview/api/cart/${product_id}`,{
        method:"put",
        body: JSON.stringify({
            "so_luong": obj.value
        }),
        headers:{
            "Content-Type":"application/json"
        }
    }).then(res=>res.json()).then(data =>{
        console.info(data)
    })
}

function deleteBookInBooksImportCart(id){
    fetch(`/admin/nhapphieuview/api/cart/${id}`, {
        method:"delete",
    }).then(res => res.json()).then(data =>{
        console.info(data)
    })
    let c = document.getElementById(`book_import_cart${id}`)
    c.style.display="none"
}

function updateCart(book) {
    // Tạo mã HTML cho sản phẩm mới
    const itemHTML = `
        <div class="row" id="book_import_cart${book.id}">
            <div class="col-3 d-flex align-items-center">
                <img src="${book.bia_sach}" class="img-fluid" alt="Book Image">
            </div>
            <div class="col-4 d-flex align-items-center">
                <h6>${book.ten_sach}</h6>
            </div>
            <div class="col-2 d-flex align-items-center">
                <input type="number" class="input-text qty text" title="SL" size="4" min="1" max="99" step="1" value="${book.so_luong}"
                onblur="updateBook(${book.id}, this)"/>
            </div>
            <div class="col-1 d-flex align-items-center">
                <a onclick="deleteBookInBooksImportCart(${book.id})" class="btn btn-accent d-flex align-items-center justify-content-center">
                    <i class="fa-solid fa-trash"></i>
                </a>
            </div>
        </div>`;

    // Cập nhật nội dung của #cart-items
    const cartItems = document.getElementById('nhung_code_html');
    cartItems.innerHTML += itemHTML;  // Thêm sản phẩm mới vào cuối nội dung hiện tại
}