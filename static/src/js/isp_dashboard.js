/** @odoo-module **/

// Simple client-action script (no OWL needed for now)
// Runs when action tag "kio_isp_management.dashboard" is opened.

function formatToday() {
    const today = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return today.toLocaleDateString('en-US', options);
}

function renderTemplate(container) {
    container.innerHTML = `
        <div class="top-bar">
            <h1><i class="fas fa-chart-line"></i> Dashboard</h1>
            <button class="month-btn">
                <i class="fas fa-calendar"></i> January 2025
            </button>
        </div>

        <div class="sidebar">
            <div class="sidebar-item active"><i class="fas fa-th-large"></i> Dashboard</div>
            <div class="sidebar-item"><i class="fas fa-users"></i> Lead Management</div>
            <div class="sidebar-item"><i class="fas fa-network-wired"></i> Bandwidth Management</div>
            <div class="sidebar-item"><i class="fas fa-tasks"></i> Work Order Management</div>
            <div class="sidebar-item"><i class="fas fa-user-cog"></i> User Management</div>
            <div class="sidebar-item"><i class="fas fa-cogs"></i> Account Management</div>
            <div class="sidebar-item"><i class="fas fa-ticket-alt"></i> Ticket Management</div>
        </div>

        <div class="main-content">
            <div class="greeting">
                <h2>Good Morning, Admin!</h2>
                <p>Today is <span id="current-date"></span></p>
            </div>

            <div class="row">
                ${renderStatCard("WorkOrder", "26", "fa-briefcase")}
                ${renderStatCard("Generated Bill", "5,00,000 ৳", "fa-file-invoice")}
                ${renderStatCard("Collected Bill", "3,00,000 ৳", "fa-check-circle")}
                ${renderStatCard("Due Bill", "1,80,000 ৳", "fa-clock")}
                ${renderStatCard("Discount Bill", "20,000 ৳", "fa-tag")}
                ${renderStatCard("Upgration MRC", "2,40,000 ৳", "fa-arrow-up")}
                ${renderStatCard("Downgration MRC", "86,000 ৳", "fa-arrow-down")}
                ${renderStatCard("Bandwidth Cost", "3,00,000", "fa-wifi")}
                ${renderStatCard("New Clients", "30", "fa-user-plus")}
                ${renderStatCard("Left Clients", "02", "fa-user-minus")}
            </div>

            <div class="perf-metrics">
                <div class="metric">
                    <div>
                        <div class="metric-label">Highest monthly revenue</div>
                        <div class="metric-value">50,00,000 ৳</div>
                    </div>
                </div>
                <div class="metric">
                    <div>
                        <div class="metric-label">Lowest monthly revenue</div>
                        <div class="metric-value">10,00,000 ৳</div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-lg-6">
                    <div class="chart-card">
                        <div class="chart-title">
                            <i class="fas fa-chart-line"></i> Yearly Revenue Performance
                        </div>
                        <canvas id="revenueChart"></canvas>
                    </div>
                </div>

                <div class="col-lg-6">
                    <div class="chart-card">
                        <div class="chart-title">
                            <i class="fas fa-chart-area"></i> Yearly Clients Performance
                        </div>
                        <canvas id="clientsChart"></canvas>
                    </div>
                </div>
            </div>

            <div class="row" style="margin-top: 30px;">
                ${renderSummaryCard("Total Bill", "1,00,00,000")}
                ${renderSummaryCard("Total Due", "1,00,000")}
                ${renderSummaryCard("Total Clients", "160")}
                ${renderSummaryCard("Total Work Order", "200")}
            </div>

            <div class="row" style="margin-top: 30px; margin-bottom: 30px;">
                <div class="col-lg-4 col-md-6 col-sm-12">
                    <div class="chart-card">
                        <div class="chart-title">
                            <i class="fas fa-network-wired"></i> Service Type Capacity
                        </div>
                        <canvas id="capacityChart"></canvas>
                    </div>
                </div>
                <div class="col-lg-8 col-md-6 col-sm-12">
                    <div class="chart-card">
                        <div class="chart-title">
                            <i class="fas fa-chart-bar"></i> Detailed Metrics
                        </div>
                        <canvas id="detailedChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderStatCard(label, value, icon) {
    return `
    <div class="col-lg-3 col-md-4 col-sm-6">
        <div class="stat-card">
            <div class="stat-card-icon"><i class="fas ${icon}"></i></div>
            <div class="stat-card-label">${label}</div>
            <div class="stat-card-value">${value}</div>
        </div>
    </div>`;
}

function renderSummaryCard(label, value) {
    return `
    <div class="col-lg-3 col-md-6">
        <div class="summary-card">
            <div class="summary-card-label">${label}</div>
            <div class="summary-card-value">${value}</div>
        </div>
    </div>`;
}

function bindSidebar(container) {
    const sidebarItems = container.querySelectorAll(".sidebar-item");
    sidebarItems.forEach((item) => {
        item.addEventListener("click", function () {
            sidebarItems.forEach((el) => el.classList.remove("active"));
            this.classList.add("active");
        });
    });
}

function initCharts(container) {
    // Chart.js must be loaded
    if (!window.Chart) {
        console.error("Chart.js not loaded. Check views/assets.xml CDN script.");
        return;
    }

    // Revenue chart
    const revenueEl = container.querySelector("#revenueChart");
    if (revenueEl) {
        const revenueCtx = revenueEl.getContext("2d");
        new Chart(revenueCtx, {
            type: "line",
            data: {
                labels: ["Jan-26", "Feb-26", "Mar-26", "Apr-26", "May-26"],
                datasets: [{
                    label: "Revenue",
                    data: [5000000, 2500000, 3000000, 1500000, 4000000],
                    borderColor: "#2ba3c8",
                    backgroundColor: "rgba(43, 163, 200, 0.1)",
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 6,
                    pointBackgroundColor: "#1a5f7a",
                    pointBorderColor: "#ffffff",
                    pointBorderWidth: 2,
                    pointHoverRadius: 8,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: { legend: { position: "top", labels: { usePointStyle: true, padding: 15 } } },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: (value) => (value / 1000000).toFixed(0) + "M" }
                    }
                }
            }
        });
    }

    // Clients chart
    const clientsEl = container.querySelector("#clientsChart");
    if (clientsEl) {
        const clientsCtx = clientsEl.getContext("2d");
        new Chart(clientsCtx, {
            type: "line",
            data: {
                labels: ["Jan-26","Feb-26","Mar-26","Apr-26","May-26","Jun-26","Jul-26","Aug-26","Sep-26","Oct-26","Nov-26","Dec-26"],
                datasets: [
                    {
                        label: "New Clients",
                        data: [10, 15, 12, 20, 18, 25, 30, 28, 35, 40, 38, 42],
                        borderColor: "#2ba3c8",
                        backgroundColor: "rgba(43, 163, 200, 0.1)",
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: "#2ba3c8"
                    },
                    {
                        label: "Left Clients",
                        data: [5, 8, 10, 12, 15, 18, 20, 22, 18, 15, 12, 10],
                        borderColor: "#1a5f7a",
                        backgroundColor: "rgba(26, 95, 122, 0.1)",
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: "#1a5f7a"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: { legend: { position: "top", labels: { usePointStyle: true, padding: 15 } } }
            }
        });
    }

    // Capacity chart
    const capEl = container.querySelector("#capacityChart");
    if (capEl) {
        const capCtx = capEl.getContext("2d");
        new Chart(capCtx, {
            type: "doughnut",
            data: {
                labels: ["BSIX", "IIG", "Data Center", "CDN"],
                datasets: [{
                    data: [40, 23.4, 15.8, 20.8],
                    backgroundColor: ["#2ba3c8", "#1a5f7a", "#4ec8e3", "#f39c12"],
                    borderColor: "#ffffff",
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: "bottom", labels: { padding: 15, font: { size: 12 } } } }
            }
        });
    }

    // Detailed chart
    const detailedEl = container.querySelector("#detailedChart");
    if (detailedEl) {
        const detailedCtx = detailedEl.getContext("2d");
        new Chart(detailedCtx, {
            type: "bar",
            data: {
                labels: ["Q1", "Q2", "Q3", "Q4"],
                datasets: [
                    { label: "Revenue", data: [10000000, 8000000, 12000000, 15000000], backgroundColor: "#2ba3c8" },
                    { label: "Expenses", data: [5000000, 4500000, 6000000, 7000000], backgroundColor: "#4ec8e3" },
                ]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: "top", labels: { padding: 15 } } },
                scales: {
                    y: { ticks: { callback: (value) => (value / 1000000).toFixed(0) + "M" } }
                }
            }
        });
    }
}

/**
 * Register client action:
 * tag: "kio_isp_management.dashboard"
 */
import { registry } from "@web/core/registry";

registry.category("actions").add("kio_isp_management.dashboard", {
    /**
     * Odoo calls mount/unmount lifecycle.
     * We render HTML and then init charts.
     */
    async setup(env, { action }) {
        // no-op
    },
    async mount(env, { el }) {
        const root = el.querySelector("#kio-isp-dashboard-root") || el;

        // Render HTML
        renderTemplate(root);

        // Set date
        const dateEl = root.querySelector("#current-date");
        if (dateEl) dateEl.textContent = formatToday();

        // Bind sidebar
        bindSidebar(root);

        // Init charts after DOM render
        initCharts(root);
    },
    async unmount() {
        // If later you store chart instances, destroy them here
    },
});
