document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    loadDashboardMetrics();
    loadPipelineStages();
    loadClusterTopology();
});

// Tab Navigation Switching
function initTabs() {
    const buttons = document.querySelectorAll(".tab-btn");
    const panes = document.querySelectorAll(".tab-pane");

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            buttons.forEach(b => b.classList.remove("active"));
            panes.forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            const targetId = btn.getAttribute("data-tab");
            const targetPane = document.getElementById(targetId);
            if (targetPane) {
                targetPane.classList.add("active");
            }
        });
    });
}

// Format Numbers with Commas
function formatNumber(num) {
    return Number(num).toLocaleString();
}

// Load Tab 1: Executive Analytics
async function loadDashboardMetrics() {
    // 1. KPI Summary
    try {
        const res = await fetch("/api/summary");
        const data = await res.json();
        if (data.total_requests) {
            document.getElementById("kpi-requests").textContent = formatNumber(data.total_requests);
            document.getElementById("kpi-sessions").textContent = formatNumber(data.total_sessions);
            document.getElementById("kpi-error-rate").textContent = `${data.error_rate_percent}%`;
            
            // Format GB
            const gb = (data.total_response_bytes / (1024 * 1024 * 1024)).toFixed(2);
            document.getElementById("kpi-total-bytes").textContent = `${gb} GB`;
        }
    } catch (e) {
        console.error("Error loading summary:", e);
    }

    // 2. Top Requested URLs (Hive)
    try {
        const res = await fetch("/api/top-pages?limit=10");
        const pages = await res.json();
        const tbody = document.getElementById("top-pages-body");
        if (Array.isArray(pages) && pages.length > 0) {
            const maxReqs = pages[0].request_count || 1;
            tbody.innerHTML = pages.map(p => {
                const percent = p.percentage || ((p.request_count / maxReqs) * 100).toFixed(1);
                const barWidth = Math.min(100, Math.round((p.request_count / maxReqs) * 100));
                return `
                    <tr>
                        <td><span class="url-code" title="${p.url}">${p.url}</span></td>
                        <td><strong>${formatNumber(p.request_count)}</strong></td>
                        <td>${percent}%</td>
                        <td class="progress-bar-cell">
                            <div class="mini-bar-bg">
                                <div class="mini-bar-fill" style="width: ${barWidth}%"></div>
                            </div>
                        </td>
                    </tr>
                `;
            }).join("");
        }
    } catch (e) {
        console.error("Error loading top pages:", e);
    }

    // 3. Mined Navigation Transitions (MapReduce)
    try {
        const res = await fetch("/api/navigation?limit=10");
        const navs = await res.json();
        const tbody = document.getElementById("navigation-body");
        if (Array.isArray(navs) && navs.length > 0) {
            tbody.innerHTML = navs.map(n => `
                <tr>
                    <td><span class="url-code" title="${n.source_url}">${n.source_url}</span></td>
                    <td><span class="url-code" title="${n.destination_url}">${n.destination_url}</span></td>
                    <td><span class="kpi-tag tag-cyan"><strong>${formatNumber(n.count)}</strong> hits</span></td>
                </tr>
            `).join("");
        }
    } catch (e) {
        console.error("Error loading navigation patterns:", e);
    }

    // 4. Mined User Sessions (MapReduce)
    try {
        const res = await fetch("/api/sessions?limit=15");
        const sessions = await res.json();
        const tbody = document.getElementById("sessions-body");
        if (Array.isArray(sessions) && sessions.length > 0) {
            tbody.innerHTML = sessions.map(s => `
                <tr>
                    <td><code>${s.host}</code></td>
                    <td><span class="kpi-tag tag-indigo">${s.session_id}</span></td>
                    <td>${s.start_time}</td>
                    <td>${s.end_time}</td>
                    <td><strong>${s.request_count}</strong> hits</td>
                    <td>${s.duration_seconds}s</td>
                    <td>${formatNumber(s.total_bytes)}</td>
                </tr>
            `).join("");
        }
    } catch (e) {
        console.error("Error loading sessions:", e);
    }

    // 5. Render Chart.js Diurnal Traffic & Error Charts
    try {
        const [trafficRes, errorRes] = await Promise.all([
            fetch("/api/traffic"),
            fetch("/api/errors")
        ]);
        const trafficData = await trafficRes.json();
        const errorData = await errorRes.json();

        // Traffic Chart
        const ctxTraffic = document.getElementById("trafficChart").getContext("2d");
        new Chart(ctxTraffic, {
            type: "line",
            data: {
                labels: trafficData.map(d => `${d.hour}:00`),
                datasets: [{
                    label: "Requests / Hour",
                    data: trafficData.map(d => d.requests),
                    borderColor: "#38bdf8",
                    backgroundColor: "rgba(56, 189, 248, 0.12)",
                    fill: true,
                    tension: 0.35,
                    borderWidth: 2.5,
                    pointRadius: 3,
                    pointBackgroundColor: "#38bdf8"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` ${formatNumber(ctx.raw)} requests`
                        }
                    }
                },
                scales: {
                    x: { grid: { color: "rgba(55, 65, 81, 0.3)" }, ticks: { color: "#9ca3af" } },
                    y: { grid: { color: "rgba(55, 65, 81, 0.3)" }, ticks: { color: "#9ca3af" } }
                }
            }
        });

        // Error Chart
        const ctxError = document.getElementById("errorChart").getContext("2d");
        new Chart(ctxError, {
            type: "bar",
            data: {
                labels: errorData.map(d => `${d.hour}:00`),
                datasets: [{
                    label: "HTTP Errors (4xx/5xx)",
                    data: errorData.map(d => d.errors),
                    backgroundColor: "rgba(244, 63, 94, 0.8)",
                    hoverBackgroundColor: "#f43f5e",
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` ${formatNumber(ctx.raw)} errors`
                        }
                    }
                },
                scales: {
                    x: { grid: { color: "rgba(55, 65, 81, 0.3)" }, ticks: { color: "#9ca3af" } },
                    y: { grid: { color: "rgba(55, 65, 81, 0.3)" }, ticks: { color: "#9ca3af" } }
                }
            }
        });
    } catch (e) {
        console.error("Error rendering charts:", e);
    }
}

// Load Tab 2: Pipeline Stages Stepper
async function loadPipelineStages() {
    try {
        const res = await fetch("/api/pipeline-stages");
        const stages = await res.json();
        const container = document.getElementById("pipeline-stepper");
        if (Array.isArray(stages) && container) {
            container.innerHTML = stages.map(st => `
                <div class="step-card">
                    <div class="step-number">${st.step}</div>
                    <div class="step-content">
                        <div class="step-title-row">
                            <span class="step-title">${st.name}</span>
                            <span class="step-tech">${st.technology}</span>
                        </div>
                        <div class="step-desc">${st.details}</div>
                        <div class="step-metrics">
                            <span>Input: <strong>${st.input}</strong></span>
                            <span>Output: <strong>${st.output}</strong></span>
                            <span>Runtime: <strong style="color: var(--accent-emerald);">${st.runtime}</strong></span>
                            <span>Status: <span class="kpi-tag tag-emerald">${st.status}</span></span>
                        </div>
                    </div>
                </div>
            `).join("");
        }
    } catch (e) {
        console.error("Error loading pipeline stages:", e);
    }
}

// Load Tab 3: Cluster Topology Map
async function loadClusterTopology() {
    try {
        const res = await fetch("/api/cluster");
        const data = await res.json();
        const grid = document.getElementById("cluster-nodes-grid");
        if (data.nodes && grid) {
            grid.innerHTML = data.nodes.map(n => `
                <div class="node-card">
                    <div class="node-header">
                        <span class="node-name">${n.name}</span>
                        <span class="kpi-tag tag-emerald">${n.status}</span>
                    </div>
                    <div class="node-role">${n.role}</div>
                    <div class="node-desc">${n.desc}</div>
                    <div class="node-ports">
                        <span>Web UI: :${n.port}</span>
                        <span>RPC: :${n.rpc}</span>
                    </div>
                </div>
            `).join("");
        }
    } catch (e) {
        console.error("Error loading cluster topology:", e);
    }
}
