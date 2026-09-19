// =========================
// Dashboard Charts
// =========================

const chartData = window.dashboardStats || {};

const deviceLabels = chartData.deviceLabels || [];
const deviceValues = chartData.deviceValues || [];
const interfaceLabels = chartData.interfaceLabels || [];
const interfaceIn = chartData.interfaceIn || [];
const interfaceOut = chartData.interfaceOut || [];
const statusLabels = chartData.statusLabels || [];
const statusValues = chartData.statusValues || [];

if (document.getElementById("deviceChart")) {
    new Chart(document.getElementById("deviceChart"), {
        type: "bar",
        data: {
            labels: deviceLabels,
            datasets: [{
                label: "Inbound Traffic (Mbps)",
                data: deviceValues,
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
                    beginAtZero: true
                }
            }
        }
    });
}

if (document.getElementById("interfaceChart") && interfaceLabels.length) {
    new Chart(document.getElementById("interfaceChart"), {
        type: "bar",
        data: {
            labels: interfaceLabels,
            datasets: [
                {
                    label: "Inbound (Mbps)",
                    data: interfaceIn,
                    borderColor: "#2563eb",
                    backgroundColor: "rgba(37, 99, 235, 0.15)",
                    borderWidth: 1
                },
                {
                    label: "Outbound (Mbps)",
                    data: interfaceOut,
                    borderColor: "#16a34a",
                    backgroundColor: "rgba(22, 163, 74, 0.15)",
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
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
