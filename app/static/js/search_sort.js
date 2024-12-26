<script>
    function submitFormViaAjax(event) {
        event.preventDefault();

        var kw = document.querySelector('[name="kw"]').value;
        var sort_by = document.querySelector('[name="sort_by"]').value;
        var page = 1; // Ví dụ: trang đầu tiên

        var formData = new FormData();
        formData.append('kw', kw);
        formData.append('sort_by', sort_by);
        formData.append('page', page);

        fetch('/shop', {
            method: 'GET',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Xử lý dữ liệu trả về
            console.log(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
</script>
