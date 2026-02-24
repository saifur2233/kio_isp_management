/** @odoo-module */
import { Component, onMounted, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const actionRegistry = registry.category("actions");

class IspDashboardAction extends Component {
    setup() {
        // NEW: ORM service to query the database
        this.orm = useService("orm");

        // CHANGED: Added left_client to reactive state
        this.state = useState({
            new_client: 0,
            left_client: 0   // NEW: for Left Clients card
        });

        onMounted(async () => {
            // CHANGED: Load both counts before rendering dashboard
            await this._loadClientCounts();
            await this._mountDashboard();
        });
    }

    // CHANGED: Renamed + now loads BOTH new and left clients
    async _loadClientCounts() {
        try {
            // New clients → total clients (you can adjust domain later, e.g. created this month)
            const newCount = await this.orm.searchCount("isp.client", []);

            // Left clients → inactive records
            const leftCount = await this.orm.searchCount("isp.client", [
                ['active', '=', false]
            ]);

            // Update reactive state → template will automatically show new values
            this.state.new_client = newCount;
            this.state.left_client = leftCount;

            // Helpful for debugging → check browser console (F12)
            console.log("Dashboard client stats loaded:", {
                new_clients: newCount,
                left_clients: leftCount
            });
        } catch (error) {
            console.error("Failed to load client counts:", error);
            // Fallback values in case of error
            this.state.new_client = 0;
            this.state.left_client = 0;
        }
    }

    async _waitForChart() {
        return new Promise((resolve) => {
            const check = () => {
                if (window.Chart) {
                    resolve();
                } else {
                    setTimeout(check, 50);
                }
            };
            check();
        });
    }

    _getRoot() {
        return this.el || document.getElementById("kio-isp-dashboard-root");
    }

    _setCurrentDate() {
        const root = this._getRoot();
        if (!root) return;
        const el = root.querySelector("#current-date");
        if (!el) return;
        const today = new Date();
        const options = { weekday: "long", year: "numeric", month: "long", day: "numeric" };
        el.textContent = today.toLocaleDateString("en-US", options);
    }

    _bindSidebar() {
        const root = this._getRoot();
        if (!root) return;
        const items = root.querySelectorAll(".sidebar-item");
        items.forEach((item) => {
            item.addEventListener("click", () => {
                items.forEach((el) => el.classList.remove("active"));
                item.classList.add("active");
            });
        });
    }

    _renderCharts() {
        const root = this._getRoot();
        if (!root) return;
        const ChartLib = window.Chart;

        // Revenue line
        const revenueCtx = root.querySelector("#revenueChart")?.getContext("2d");
        if (revenueCtx) {
            new ChartLib(revenueCtx, {
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
                    }],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { position: "top", labels: { usePointStyle: true, padding: 15 } },
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { callback: (value) => `${(value / 1000000).toFixed(0)}M` },
                        },
                    },
                },
            });
        }

        // Clients line chart
        const clientsCtx = root.querySelector("#clientsChart")?.getContext("2d");
        if (clientsCtx) {
            new ChartLib(clientsCtx, {
                type: "line",
                data: {
                    labels: ["Jan-26", "Feb-26", "Mar-26", "Apr-26", "May-26", "Jun-26", "Jul-26", "Aug-26", "Sep-26", "Oct-26", "Nov-26", "Dec-26"],
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
                            pointBackgroundColor: "#2ba3c8",
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
                            pointBackgroundColor: "#1a5f7a",
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { position: "top", labels: { usePointStyle: true, padding: 15 } },
                    },
                },
            });
        }

        // Capacity doughnut
        const capacityCtx = root.querySelector("#capacityChart")?.getContext("2d");
        if (capacityCtx) {
            new ChartLib(capacityCtx, {
                type: "doughnut",
                data: {
                    labels: ["BSIX", "40%", "IIG", "23.4%", "Data Center", "15.8%", "CDN", "23.5%"],
                    datasets: [{
                        data: [40, 23.4, 15.8, 20.8],
                        backgroundColor: ["#2ba3c8", "#1a5f7a", "#4ec8e3", "#f39c12"],
                        borderColor: "#ffffff",
                        borderWidth: 3,
                    }],
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: "bottom", labels: { padding: 15, font: { size: 12 } } },
                    },
                },
            });
        }

        // Detailed metrics bar
        const detailedCtx = root.querySelector("#detailedChart")?.getContext("2d");
        if (detailedCtx) {
            new ChartLib(detailedCtx, {
                type: "bar",
                data: {
                    labels: ["Q1", "Q2", "Q3", "Q4"],
                    datasets: [
                        {
                            label: "Revenue",
                            data: [10000000, 8000000, 12000000, 15000000],
                            backgroundColor: "#2ba3c8",
                        },
                        {
                            label: "Expenses",
                            data: [5000000, 4500000, 6000000, 7000000],
                            backgroundColor: "#4ec8e3",
                        },
                    ],
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: "top", labels: { padding: 15 } },
                    },
                    scales: {
                        y: {
                            ticks: { callback: (value) => `${(value / 1000000).toFixed(0)}M` },
                        },
                    },
                },
            });
        }
    }

    async _mountDashboard() {
        await this._waitForChart();
        this._setCurrentDate();
        this._bindSidebar();
        this._renderCharts();
    }
}

IspDashboardAction.template = "kio_isp_management.dashboard";

actionRegistry.add("kio_isp_management.dashboard", IspDashboardAction);

export default IspDashboardAction;