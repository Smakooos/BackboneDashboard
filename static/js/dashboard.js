// SNMP dashboard charts. Data is supplied safely by dashboard.html.
const chartData = window.dashboardStats || {};
const deviceLabels = chartData.deviceLabels || [];
const deviceInbound = chartData.deviceInbound || [];
const deviceOutbound = chartData.deviceOutbound || [];
const interfaceLabels = chartData.interfaceLabels || [];
const interfaceInbound = chartData.interfaceIn || [];
const interfaceOutbound = chartData.interfaceOut || [];
const deviceStatusLabels = chartData.deviceStatusLabels || [];
const deviceStatusValues = chartData.deviceStatusValues || [];

function deviceTrafficChart(elementId, label, values, color) {
    const canvas = document.getElementById(elementId);
    if (!canvas) return;

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: deviceLabels,
            datasets: [{ label, data: values, backgroundColor: color, borderRadius: 8 }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, title: { display: true, text: "Mbps" } } }
        }
    });
}

deviceTrafficChart("inboundDeviceChart", "Inbound Traffic (Mbps)", deviceInbound, "#d71920");
deviceTrafficChart("outboundDeviceChart", "Outbound Traffic (Mbps)", deviceOutbound, "#2563eb");

if (document.getElementById("interfaceChart") && interfaceLabels.length) {
    new Chart(document.getElementById("interfaceChart"), {
        type: "bar",
        data: {
            labels: interfaceLabels,
            datasets: [
                { label: "Inbound (Mbps)", data: interfaceInbound, backgroundColor: "rgba(37, 99, 235, 0.65)" },
                { label: "Outbound (Mbps)", data: interfaceOutbound, backgroundColor: "rgba(22, 163, 74, 0.65)" }
            ]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true, title: { display: true, text: "Mbps" } } }
        }
    });
}

if (document.getElementById("deviceStatusChart")) {
    new Chart(document.getElementById("deviceStatusChart"), {
        type: "doughnut",
        data: {
            labels: deviceStatusLabels,
            datasets: [{
                data: deviceStatusValues,
                backgroundColor: ["#22c55e", "#6b7280", "#f59e0b", "#ef4444"]
            }]
        },
        options: { responsive: true }
    });
}
