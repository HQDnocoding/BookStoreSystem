document.addEventListener("DOMContentLoaded", function () {
    const pieChartCanvas = document.getElementById("pieChart");

    if (pieChartCanvas && pieChartData) {
        new Chart(pieChartCanvas, {
            type: "pie",
            data: {
                labels: pieChartData.labels,
                datasets: [
                    {
                        label: "Tỉ lệ bán",
                        data: pieChartData.data,
                        backgroundColor: [
                            "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0",
                            "#9966FF", "#FF9F40",
                        ],
                        hoverOffset: 10,

                    },
                ],
            },
            options: {
                responsive: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const index = context.dataIndex;
                                const percentage = pieChartData.percentages[index];
                                return `${context.label}: ${context.raw} (${percentage || 0}%)`;
                            },
                        },
                    },
                     title: {
                display: true, // Hiển thị tiêu đề
                text: "Biểu đồ tần suất theo tháng", // Nội dung tiêu đề
                font: {
                    size: 18, // Kích thước chữ
                    weight: "bold", // Độ đậm
                },
                padding: {
                    top: 10,
                    bottom: 20,
                },
                color: "#333", // Màu chữ
            },
                },
            },
        });
    } else {
        console.error("Không có dữ liệu để hiển thị PieChart.");
    }
});
