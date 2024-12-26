function addComment(sachId) {
    fetch(`/api/books/${sachId}/comments`, {
        method: "post",
        body: JSON.stringify({
            "content": document.getElementById("comment").value
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(c => {
    document.getElementById("comment").value=""
        let html = `
        <li class="list-group-item">
            <div class="row">
                <div class="col-md-1 col-4">
                    <img src="${ c.user.avatar }" class="img-fluid rounded-circle"
                     onError="this.onerror=null; this.src='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-vector-600nw-1745180411.jpg';"/>
                </div>
                <div class="col-md-11 col-8">
                    <p> <strong>${c.user.ho} ${c.user.ten}</strong>   ${c.ngay_tao}</p>
                    <p>${ c.content }</p>
                </div>
            </div>

        </li>
        `;

        let t = document.getElementById("comments");
        t.innerHTML = html + t.innerHTML;
    })
}