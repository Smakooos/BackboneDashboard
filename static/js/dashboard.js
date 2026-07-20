// =========================
// Dashboard Charts
// =========================

const chartData = window.dashboardStats || {};

const cpuLabels = chartData.cpuLabels || [];
const cpuValues = chartData.cpuValues || [];
const statusLabels = chartData.statusLabels || [];
const statusValues = chartData.statusValues || [];

if (document.getElementById("cpuChart")) {
    new Chart(document.getElementById("cpuChart"), {
        type: "bar",
        data: {
            labels: cpuLabels,
            datasets: [{
                label: "CPU Usage (%)",
                data: cpuValues,
                backgroundColor: "#d71920",
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

if (document.getElementById("statusChart")) {
    new Chart(document.getElementById("statusChart"), {
        type: "doughnut",
        data: {
            labels: statusLabels,
            datasets: [{
                data: statusValues,
                backgroundColor: [
                    "#22c55e",
                    "#f59e0b",
                    "#ef4444"
                ]
            }]
        },
        options: {
            responsive: true
        }
    });
}