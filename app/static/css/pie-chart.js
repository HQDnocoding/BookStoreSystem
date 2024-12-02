// Lấy canvas
const ctx = document.getElementById('myPieChart').getContext('2d');

// Tạo biểu đồ
const myPieChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: stats[1], // Sử dụng dữ liệu từ Flask
        datasets: [{
            label: 'Dataset 1',
            data: stats[2], // Sử dụng dữ liệu từ Flask
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
        }
    }
});
