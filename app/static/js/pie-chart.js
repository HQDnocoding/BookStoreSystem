document.addEventListener("DOMContentLoaded", function () {
    const pieChartCanvas = document.getElementById("pieChart");

    // Hàm tạo màu sắc ngẫu nhiên
    function generateRandomColor() {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

    // Tạo mảng màu sắc cho biểu đồ dựa trên số lượng phần tử
    const generateColors = (numColors) => {
        let colors = [];
        for (let i = 0; i < numColors; i++) {
            colors.push(generateRandomColor());
        }
        return colors;
    };

    if (pieChartCanvas && pieChartData) {
        new Chart(pieChartCanvas, {
            type: "pie",
            data: {
                labels: pieChartData.labels,
                datasets: [
                    {
                        label: "Tỉ lệ bán",
                        data: pieChartData.data,
                        backgroundColor: generateColors(pieChartData.data.length), // Tạo màu sắc tự động
                        hoverOffset: 10,
                    },
                ],
            },
            options: {
                responsive: true,
                 aspectRatio: 1.5,
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
                            top: 30,
                            bottom: 30,
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
