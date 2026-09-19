// =========================
// Dashboard Charts
// =========================

const chartData = window.dashboardStats || {};

const cpuLabels = chartData.cpuLabels || [];
const cpuValues = chartData.cpuValues || [];
const interfaceLabels = chartData.interfaceLabels || [];
const interfaceIn = chartData.interfaceIn || [];
const interfaceOut = chartData.interfaceOut || [];
const statusLabels = chartData.statusLabels || [];
const statusValues = chartData.statusValues || [];

if (document.getElementById("cpuChart")) {
    new Chart(document.getElementById("cpuChart"), {
        type: "bar",
        data: {
            labels: cpuLabels,
            datasets: [{
                label: "Inbound Traffic (Mbps)",
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
                    beginAtZero: true
                }
            }
        }
    });
}

if (document.getElementById("interfaceChart") && interfaceLabels.length) {
    new Chart(document.getElementById("interfaceChart"), {
        type: "line",
        data: {
            labels: interfaceLabels,
            datasets: [
                {
                    label: "Inbound (Mbps)",
                    data: interfaceIn,
                    borderColor: "#2563eb",
                    backgroundColor: "rgba(37, 99, 235, 0.15)",
                    fill: true,
                    tension: 0.3
                },
                {
                    label: "Outbound (Mbps)",
                    data: interfaceOut,
                    borderColor: "#16a34a",
                    backgroundColor: "rgba(22, 163, 74, 0.15)",
                    fill: true,
                    tension: 0.3
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

if (window.location.pathname.includes("dashboard")) {
    window.setInterval(() => {
        window.location.reload();
    }, 10000);
}