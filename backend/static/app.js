document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    loadDashboardMetrics();
    initSimulator();
    loadBenchmarks();
    loadClusterTopology();
});

// Global state cache
const state = {
    topPages: [],
    pageFilter: "all",
    pageSearch: "",
    navigation: [],
    navSearch: "",
    sessions: [],
    sessionHostSearch: "",
    sessionMinHits: 0,
    currentSimStage: 1,
    simData: null,
    isSimulating: false
};

// ============================================================================
// Tab Navigation
// ============================================================================
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

function formatNumber(num) {
    return Number(num).toLocaleString();
}

// ============================================================================
// TAB 1: Executive Analytics & Charts
// ============================================================================
async function loadDashboardMetrics() {
    // 1. KPI Summary & Ribbon
    try {
        const res = await fetch("/api/summary");
        const data = await res.json();
        if (data.total_requests) {
            document.getElementById("kpi-requests").textContent = formatNumber(data.total_requests);
            document.getElementById("ribbon-records").textContent = formatNumber(data.total_requests);
            document.getElementById("kpi-sessions").textContent = formatNumber(data.total_sessions);
            document.getElementById("ribbon-sessions").textContent = formatNumber(data.total_sessions);
            document.getElementById("kpi-error-rate").textContent = `${data.error_rate_percent}%`;
            
            const gb = (data.total_response_bytes / (1024 * 1024 * 1024)).toFixed(2);
            document.getElementById("kpi-total-bytes").textContent = `${gb} GB`;
        }
    } catch (e) {
        console.error("Error loading summary:", e);
    }

    // 2. Top Requested URLs
    try {
        const res = await fetch("/api/top-pages?limit=30");
        state.topPages = await res.json();
        renderTopPages();
        setupTopPagesListeners();
    } catch (e) {
        console.error("Error loading top pages:", e);
    }

    // 3. Navigation Transitions
    try {
        const res = await fetch("/api/navigation?limit=25");
        state.navigation = await res.json();
        renderNavigation();
        setupNavigationListeners();
    } catch (e) {
        console.error("Error loading navigation patterns:", e);
    }

    // 4. Mined User Sessions
    try {
        const res = await fetch("/api/sessions?limit=50");
        state.sessions = await res.json();
        renderSessions();
        setupSessionListeners();
    } catch (e) {
        console.error("Error loading sessions:", e);
    }

    // 5. Render Chart.js Visualizations
    renderCharts();
}

// Render Top Pages with filtering
function renderTopPages() {
    const tbody = document.getElementById("top-pages-body");
    if (!tbody || !Array.isArray(state.topPages)) return;

    let filtered = state.topPages.filter(p => {
        // Search filter
        if (state.pageSearch && !p.url.toLowerCase().includes(state.pageSearch.toLowerCase())) {
            return false;
        }
        // Type filter
        if (state.pageFilter === "image") {
            return p.url.endsWith(".gif") || p.url.endsWith(".jpg") || p.url.endsWith(".xbm");
        }
        if (state.pageFilter === "html") {
            return p.url.endsWith(".html") || p.url.endsWith("/") || p.url === "/";
        }
        if (state.pageFilter === "script") {
            return p.url.includes("/htbin/") || p.url.endsWith(".pl");
        }
        return true;
    });

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="loading-cell">No matching URLs found.</td></tr>`;
        return;
    }

    const maxReqs = state.topPages[0]?.request_count || 1;
    tbody.innerHTML = filtered.map(p => {
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

function setupTopPagesListeners() {
    const searchInput = document.getElementById("filter-top-pages");
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            state.pageSearch = e.target.value.trim();
            renderTopPages();
        });
    }

    const pillBtns = document.querySelectorAll("#page-type-filters .pill-btn");
    pillBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            pillBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            state.pageFilter = btn.getAttribute("data-filter");
            renderTopPages();
        });
    });
}

// Render Navigation Transitions
function renderNavigation() {
    const tbody = document.getElementById("navigation-body");
    if (!tbody || !Array.isArray(state.navigation)) return;

    let filtered = state.navigation.filter(n => {
        if (!state.navSearch) return true;
        const q = state.navSearch.toLowerCase();
        return n.source_url.toLowerCase().includes(q) || n.destination_url.toLowerCase().includes(q);
    });

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="loading-cell">No matching navigation paths found.</td></tr>`;
        return;
    }

    tbody.innerHTML = filtered.map(n => `
        <tr>
            <td><span class="url-code" title="${n.source_url}">${n.source_url}</span></td>
            <td style="color: var(--accent-cyan); text-align: center;">➔</td>
            <td><span class="url-code" title="${n.destination_url}">${n.destination_url}</span></td>
            <td><span class="kpi-tag tag-cyan"><strong>${formatNumber(n.count)}</strong> hits</span></td>
        </tr>
    `).join("");
}

function setupNavigationListeners() {
    const navInput = document.getElementById("filter-navigation");
    if (navInput) {
        navInput.addEventListener("input", (e) => {
            state.navSearch = e.target.value.trim();
            renderNavigation();
        });
    }
}

// Render Sessions Table
function renderSessions() {
    const tbody = document.getElementById("sessions-body");
    const counter = document.getElementById("sessions-counter");
    if (!tbody || !Array.isArray(state.sessions)) return;

    let filtered = state.sessions.filter(s => {
        if (state.sessionHostSearch && !s.host.toLowerCase().includes(state.sessionHostSearch.toLowerCase())) {
            return false;
        }
        if (s.request_count < state.sessionMinHits) {
            return false;
        }
        return true;
    });

    if (counter) {
        counter.textContent = `Showing ${filtered.length} of ${state.sessions.length} sessions`;
    }

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="loading-cell">No matching user sessions found.</td></tr>`;
        return;
    }

    tbody.innerHTML = filtered.slice(0, 20).map(s => {
        const kb = (s.total_bytes / 1024).toFixed(1);
        return `
            <tr>
                <td><code style="color: var(--accent-cyan);">${s.host}</code></td>
                <td><span class="kpi-tag tag-indigo">${s.session_id}</span></td>
                <td>${s.start_time}</td>
                <td>${s.end_time}</td>
                <td><strong>${s.request_count}</strong> hits</td>
                <td>${s.duration_seconds}s</td>
                <td>${kb} KB</td>
            </tr>
        `;
    }).join("");
}

function setupSessionListeners() {
    const hostInput = document.getElementById("filter-sessions-host");
    if (hostInput) {
        hostInput.addEventListener("input", (e) => {
            state.sessionHostSearch = e.target.value.trim();
            renderSessions();
        });
    }

    const hitsSelect = document.getElementById("filter-sessions-hits");
    if (hitsSelect) {
        hitsSelect.addEventListener("change", (e) => {
            state.sessionMinHits = parseInt(e.target.value) || 0;
            renderSessions();
        });
    }
}

// Render All Charts
async function renderCharts() {
    try {
        const [trafficRes, errorRes, statusRes, durationRes] = await Promise.all([
            fetch("/api/traffic"),
            fetch("/api/errors"),
            fetch("/api/status-codes"),
            fetch("/api/session-distribution")
        ]);

        const trafficData = await trafficRes.json();
        const errorData = await errorRes.json();
        const statusData = await statusRes.json();
        const durationData = await durationRes.json();

        // 1. Traffic Chart (Line)
        const ctxTraffic = document.getElementById("trafficChart")?.getContext("2d");
        if (ctxTraffic) {
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
                        x: { grid: { color: "rgba(51, 65, 85, 0.25)" }, ticks: { color: "#94a3b8" } },
                        y: { grid: { color: "rgba(51, 65, 85, 0.25)" }, ticks: { color: "#94a3b8" } }
                    }
                }
            });
        }

        // 2. Error Chart (Bar)
        const ctxError = document.getElementById("errorChart")?.getContext("2d");
        if (ctxError) {
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
                        x: { grid: { color: "rgba(51, 65, 85, 0.25)" }, ticks: { color: "#94a3b8" } },
                        y: { grid: { color: "rgba(51, 65, 85, 0.25)" }, ticks: { color: "#94a3b8" } }
                    }
                }
            });
        }

        // 3. Status Codes Chart (Doughnut)
        const ctxStatus = document.getElementById("statusChart")?.getContext("2d");
        if (ctxStatus) {
            new Chart(ctxStatus, {
                type: "doughnut",
                data: {
                    labels: statusData.map(d => d.status),
                    datasets: [{
                        data: statusData.map(d => d.count),
                        backgroundColor: statusData.map(d => d.color),
                        borderWidth: 2,
                        borderColor: "#0f172a"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: "right",
                            labels: {
                                color: "#94a3b8",
                                font: { size: 11, family: "Inter" },
                                boxWidth: 12
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => {
                                    const item = statusData[ctx.dataIndex];
                                    return ` ${item.status}: ${formatNumber(item.count)} (${item.percentage}%)`;
                                }
                            }
                        }
                    },
                    cutout: "68%"
                }
            });
        }

        // 4. Session Duration Distribution (Bar)
        const ctxDuration = document.getElementById("durationChart")?.getContext("2d");
        if (ctxDuration) {
            new Chart(ctxDuration, {
                type: "bar",
                data: {
                    labels: durationData.map(d => d.bucket),
                    datasets: [{
                        label: "Sessions",
                        data: durationData.map(d => d.sessions),
                        backgroundColor: durationData.map(d => d.color),
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => {
                                    const item = durationData[ctx.dataIndex];
                                    return ` ${formatNumber(item.sessions)} sessions (${item.percentage}%)`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: { grid: { color: "rgba(51, 65, 85, 0.25)" }, ticks: { color: "#94a3b8", font: { size: 10 } } },
                        y: { grid: { color: "rgba(51, 65, 85, 0.25)" }, ticks: { color: "#94a3b8" } }
                    }
                }
            });
        }
    } catch (e) {
        console.error("Error initializing charts:", e);
    }
}

// ============================================================================
// TAB 2: INTERACTIVE PIPELINE & DATA FLOW SIMULATOR
// ============================================================================
function initSimulator() {
    const presets = {
        apollo: '199.72.81.55 - - [01/Jul/1995:00:00:01 -0400] "GET /history/apollo/ HTTP/1.0" 200 6245',
        logo: 'unicomp6.unicomp.net - - [01/Jul/1995:00:00:06 -0400] "GET /images/NASA-logosmall.gif HTTP/1.0" 304 0',
        error: 'burger.letters.com - - [01/Jul/1995:00:00:11 -0400] "GET /shuttle/countdown/liftoff_old.html HTTP/1.0" 404 0',
        cgi: 'd104.aa.net - - [01/Jul/1995:00:00:15 -0400] "GET /htbin/cdt_main.pl HTTP/1.0" 200 1204'
    };

    const presetBtns = document.querySelectorAll(".preset-btn");
    const logInput = document.getElementById("sample-log-input");

    presetBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            presetBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            const key = btn.getAttribute("data-preset");
            if (presets[key] && logInput) {
                logInput.value = presets[key];
            }
        });
    });

    const runBtn = document.getElementById("btn-run-simulation");
    if (runBtn) {
        runBtn.addEventListener("click", runSimulation);
    }

    // Prev / Next Stage Controls
    const prevBtn = document.getElementById("btn-prev-stage");
    const nextBtn = document.getElementById("btn-next-stage");

    if (prevBtn) {
        prevBtn.addEventListener("click", () => {
            if (state.currentSimStage > 1) {
                selectSimStage(state.currentSimStage - 1);
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener("click", () => {
            if (state.currentSimStage < 7) {
                selectSimStage(state.currentSimStage + 1);
            }
        });
    }

    // Stage flow diagram node click handlers
    const stageNodes = document.querySelectorAll(".flow-stage-node");
    stageNodes.forEach(node => {
        node.addEventListener("click", () => {
            const st = parseInt(node.getAttribute("data-stage"));
            selectSimStage(st);
        });
    });

    // Initial load of default simulation trace
    fetchSimulationTrace(logInput ? logInput.value : presets.apollo);
}

async function fetchSimulationTrace(logStr) {
    try {
        const res = await fetch(`/api/simulate-trace?log=${encodeURIComponent(logStr)}`);
        state.simData = await res.json();
        renderStageInspector(state.currentSimStage);
    } catch (e) {
        console.error("Error fetching simulation trace:", e);
    }
}

async function runSimulation() {
    if (state.isSimulating) return;
    state.isSimulating = true;

    const logInput = document.getElementById("sample-log-input");
    const logStr = logInput ? logInput.value : "";
    await fetchSimulationTrace(logStr);

    const progressBar = document.getElementById("sim-progress-bar");
    const progressFill = document.getElementById("sim-progress-fill");
    const statusText = document.getElementById("sim-status-text");

    if (progressBar) progressBar.style.display = "block";

    for (let st = 1; st <= 7; st++) {
        selectSimStage(st);
        const percent = Math.round((st / 7) * 100);
        if (progressFill) progressFill.style.width = `${percent}%`;
        if (statusText) statusText.textContent = `Executing Stage ${st} of 7: ${state.simData.stages[st - 1].name}...`;
        await new Promise(r => setTimeout(r, 650));
    }

    if (statusText) statusText.textContent = `Pipeline Trace Complete! (100% Processed across 12 Nodes)`;
    setTimeout(() => {
        if (progressBar) progressBar.style.display = "none";
        state.isSimulating = false;
    }, 2500);
}

function selectSimStage(stNumber) {
    state.currentSimStage = stNumber;

    // Highlight flow stage node
    const stageNodes = document.querySelectorAll(".flow-stage-node");
    stageNodes.forEach(n => {
        const nSt = parseInt(n.getAttribute("data-stage"));
        if (nSt === stNumber) {
            n.classList.add("active");
        } else {
            n.classList.remove("active");
        }
    });

    // Update buttons state
    const prevBtn = document.getElementById("btn-prev-stage");
    const nextBtn = document.getElementById("btn-next-stage");
    if (prevBtn) prevBtn.disabled = (stNumber === 1);
    if (nextBtn) nextBtn.disabled = (stNumber === 7);

    renderStageInspector(stNumber);
}

function renderStageInspector(stNumber) {
    if (!state.simData || !state.simData.stages) return;
    const stage = state.simData.stages[stNumber - 1];
    if (!stage) return;

    document.getElementById("insp-stage-num").textContent = `STAGE ${stage.stage} OF 7 • ${stage.technology}`;
    document.getElementById("insp-stage-title").textContent = stage.name;
    document.getElementById("insp-container").textContent = stage.container;
    document.getElementById("insp-mechanism").textContent = stage.description;

    const inputCode = document.getElementById("insp-input-code");
    const outputCode = document.getElementById("insp-output-code");

    if (stage.stage === 1) {
        inputCode.textContent = `RAW ACCESS LOG LINE:\n${state.simData.raw_input}`;
        outputCode.textContent = `PARSED NORMALIZED RECORD (TSV):\n${stage.tsv_representation}\n\nSTRUCTURED DICT:\n${JSON.stringify(stage.output_data, null, 2)}`;
    } else {
        const prevStage = state.simData.stages[stNumber - 2];
        inputCode.textContent = `INPUT FROM STAGE ${prevStage.stage} (${prevStage.name}):\n${JSON.stringify(prevStage.output_data, null, 2)}`;
        outputCode.textContent = `STAGE ${stage.stage} TRANSFORMED STATE:\n${JSON.stringify(stage.output_data, null, 2)}`;
    }
}

// ============================================================================
// TAB 3: ARCHITECTURE & SCALABILITY BENCHMARKS
// ============================================================================
async function loadBenchmarks() {
    try {
        const res = await fetch("/api/benchmarks");
        const benchmarks = await res.json();
        const tbody = document.getElementById("benchmarks-body");

        if (Array.isArray(benchmarks) && tbody) {
            tbody.innerHTML = benchmarks.map(b => `
                <tr>
                    <td><strong>${b.workload}</strong></td>
                    <td>${formatNumber(b.records)}</td>
                    <td>${b.input_size_mb} MB</td>
                    <td><span class="kpi-tag tag-cyan">${b.hdfs_blocks}</span></td>
                    <td>${b.mappers}</td>
                    <td>${b.reducers}</td>
                    <td><strong style="color: var(--accent-emerald);">${b.wall_clock_sec}s</strong></td>
                    <td>${b.cpu_time_sec}s</td>
                    <td>${b.peak_ram_gb} GB</td>
                    <td><span class="kpi-tag tag-emerald">${b.speedup_ratio}</span></td>
                </tr>
            `).join("");
        }
    } catch (e) {
        console.error("Error loading benchmarks:", e);
    }
}

// ============================================================================
// TAB 4: 12-NODE CLUSTER TOPOLOGY
// ============================================================================
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
