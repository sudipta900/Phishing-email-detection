const DEFAULT_API_BASE = "https://sudip900-ml-model.hf.space";
const API_BASE = (
    window.PHISHGUARD_CONFIG
    && window.PHISHGUARD_CONFIG.apiBase
)
    ? window.PHISHGUARD_CONFIG.apiBase.replace(/\/$/, "")
    : DEFAULT_API_BASE;

const SAMPLE_EMAILS = {
    phishing: `Subject: Urgent - Verify your account now
From: security@paypa1-alerts.com

Dear Customer,

We noticed suspicious activity on your account. Your access will be suspended within 24 hours unless you confirm your password immediately.

Click here to secure your account:
http://paypa1-alerts-login.verify-user-access.com

Thank you,
Security Team`,
    legit: `Subject: Weekly project update
From: team@company.com

Hello team,

Here is this week's project summary:
- Backend API integration is in progress
- Frontend review is scheduled for Friday
- No action is required from you today

Regards,
Project Manager`
};

const verdictThemeMap = {
    PHISHING: {
        className: "phishing",
        label: "High Risk",
        icon: "!",
        subtitle: "This email strongly resembles phishing content."
    },
    SUSPICIOUS: {
        className: "suspicious",
        label: "Needs Review",
        icon: "?",
        subtitle: "This email contains warning signs and should be reviewed carefully."
    },
    SAFE: {
        className: "legitimate",
        label: "Looks Safe",
        icon: "OK",
        subtitle: "No major phishing patterns were detected in this sample."
    }
};

document.addEventListener("DOMContentLoaded", () => {
    bindUi();
    renderApiStatus();
    updateCharCount();
    updateBatchLabels();
});

function bindUi() {
    const emailInput = document.getElementById("emailInput");

    emailInput.addEventListener("input", updateCharCount);

    document
        .getElementById("batchEmails")
        .addEventListener("input", event => {
            if (event.target.classList.contains("batch-textarea")) {
                clearBatchResult(event.target.closest(".batch-item"));
            }
        });
}

function renderApiStatus() {
    const apiStatus = document.getElementById("apiStatus");
    const apiEndpoint = document.getElementById("apiEndpoint");

    apiEndpoint.textContent = API_BASE;
    apiStatus.textContent = API_BASE === DEFAULT_API_BASE
        ? "Local API target"
        : "Configured deployed API";
}

function updateCharCount() {
    const email = document.getElementById("emailInput").value;
    const count = email.length;
    const words = email.trim() ? email.trim().split(/\s+/).length : 0;

    document.getElementById("charCount").textContent = `${count} characters / ${words} words`;
}

function switchTab(tabName) {
    document.querySelectorAll(".tab").forEach(tab => {
        tab.classList.remove("active");
        tab.classList.add("hidden");
    });

    document.querySelectorAll(".pill").forEach(button => {
        button.classList.remove("active");
    });

    document.getElementById(`tab-${tabName}`).classList.add("active");
    document.getElementById(`tab-${tabName}`).classList.remove("hidden");

    document.querySelectorAll(".pill").forEach(button => {
        if (button.textContent.trim().toLowerCase() === tabName) {
            button.classList.add("active");
        }
    });
}

function loadSample(type) {
    const emailInput = document.getElementById("emailInput");
    emailInput.value = SAMPLE_EMAILS[type] || "";
    updateCharCount();
    resetSingleResult();
}

function clearInput() {
    document.getElementById("emailInput").value = "";
    updateCharCount();
    resetSingleResult();
}

function showLoading() {
    document.getElementById("emptyState").classList.add("hidden");
    document.getElementById("resultContent").classList.add("hidden");
    document.getElementById("loadingState").classList.remove("hidden");
    document.getElementById("analyzeBtn").disabled = true;
}

function hideLoading() {
    document.getElementById("loadingState").classList.add("hidden");
    document.getElementById("analyzeBtn").disabled = false;
}

function resetSingleResult() {
    document.getElementById("loadingState").classList.add("hidden");
    document.getElementById("resultContent").classList.add("hidden");
    document.getElementById("emptyState").classList.remove("hidden");
}

async function analyzeEmail() {
    const email = document.getElementById("emailInput").value;

    if (!email.trim()) {
        alert("Please enter email content before analysis.");
        return;
    }

    try {
        showLoading();

        const data = await postJson("/predict", { email });
        renderResult(data);
    } catch (error) {
        console.error(error);
        renderError(error.message);
    } finally {
        hideLoading();
    }
}

async function analyzeBatch() {
    const batchButton = document.getElementById("batchAnalyzeBtn");
    const areas = document.querySelectorAll(".batch-textarea");
    const emails = [];

    areas.forEach(area => {
        if (area.value.trim()) {
            emails.push(area.value.trim());
        }
    });

    if (!emails.length) {
        alert("Add at least one email before batch analysis.");
        return;
    }

    batchButton.disabled = true;

    try {
        const data = await postJson("/batch-predict", { emails });
        renderBatchResults(data.results || []);
        switchTab("batch");
    } catch (error) {
        console.error(error);
        alert(error.message);
    } finally {
        batchButton.disabled = false;
    }
}

async function postJson(path, payload) {
    const response = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        const detail = data.detail || data.message || "Request failed.";
        throw new Error(`API error: ${detail}`);
    }

    return data;
}

function renderResult(data) {
    const theme = verdictThemeMap[data.verdict] || verdictThemeMap.SUSPICIOUS;
    const confidence = normalizePercent(data.confidence);
    const verdictBanner = document.getElementById("verdictBanner");

    document.getElementById("emptyState").classList.add("hidden");
    document.getElementById("loadingState").classList.add("hidden");
    document.getElementById("resultContent").classList.remove("hidden");

    verdictBanner.className = `verdict-banner ${theme.className}`;
    document.getElementById("verdictIcon").textContent = theme.icon;
    document.getElementById("verdictLabel").textContent = `${data.verdict} - ${theme.label}`;
    document.getElementById("verdictSub").textContent = theme.subtitle;
    document.getElementById("scoreNumber").textContent = `${Math.round(confidence)}%`;

    const circumference = 201;
    const offset = circumference - (confidence / 100) * circumference;
    document.getElementById("scoreArc").style.strokeDashoffset = `${offset}`;

    renderThreats(data.threats || []);
    renderStats(data);
    document.getElementById("analysisMode").textContent = `Live API response from ${API_BASE}`;
}

function renderThreats(threats) {
    const list = document.getElementById("indicatorsList");
    list.innerHTML = "";

    if (!threats.length) {
        list.innerHTML = `<div class="no-indicators">No explicit threat indicators were returned.</div>`;
        return;
    }

    threats.forEach((threat, index) => {
        const item = document.createElement("div");
        const severity = inferThreatSeverity(threat);
        item.className = `indicator-item ${severity}`;
        item.style.animationDelay = `${index * 60}ms`;

        const category = document.createElement("div");
        category.className = "ind-cat";
        category.textContent = severity.toUpperCase();

        const detail = document.createElement("div");
        detail.className = "ind-detail";
        detail.textContent = typeof threat === "string"
            ? threat
            : JSON.stringify(threat);

        item.append(category, detail);
        list.appendChild(item);
    });
}

function renderStats(data) {
    const statsRow = document.getElementById("statsRow");
    const stats = [
        {
            key: "Confidence",
            value: `${normalizePercent(data.confidence).toFixed(1)}%`
        },
        {
            key: "Text Model",
            value: `${normalizePercent(data.xgb_score).toFixed(1)}%`
        },
        {
            key: "BERT Model",
            value: `${normalizePercent(data.bert_score).toFixed(1)}%`
        }
    ];

    if (data.url_score !== null && data.url_score !== undefined) {
        stats.push({
            key: "URL Score",
            value: `${normalizePercent(data.url_score).toFixed(1)}%`
        });
    }

    statsRow.innerHTML = stats.map(stat => `
        <div class="stat-item">
            <div class="stat-val">${stat.value}</div>
            <div class="stat-key">${stat.key}</div>
        </div>
    `).join("");
}

function renderError(message) {
    document.getElementById("emptyState").classList.add("hidden");
    document.getElementById("loadingState").classList.add("hidden");
    document.getElementById("resultContent").classList.remove("hidden");

    const verdictBanner = document.getElementById("verdictBanner");
    verdictBanner.className = "verdict-banner suspicious";
    document.getElementById("verdictIcon").textContent = "API";
    document.getElementById("verdictLabel").textContent = "Connection Error";
    document.getElementById("verdictSub").textContent = message;
    document.getElementById("scoreNumber").textContent = "--";
    document.getElementById("scoreArc").style.strokeDashoffset = "201";
    document.getElementById("indicatorsList").innerHTML = `
        <div class="no-indicators">
            Update <code>frontend/config.js</code> with your deployed backend URL when it is ready.
        </div>
    `;
    document.getElementById("statsRow").innerHTML = `
        <div class="stat-item">
            <div class="stat-val">POST</div>
            <div class="stat-key">Expected method</div>
        </div>
        <div class="stat-item">
            <div class="stat-val">/predict</div>
            <div class="stat-key">Single endpoint</div>
        </div>
        <div class="stat-item">
            <div class="stat-val">/batch-predict</div>
            <div class="stat-key">Batch endpoint</div>
        </div>
    `;
    document.getElementById("analysisMode").textContent = `Unable to reach ${API_BASE}`;
}

function addBatchItem() {
    const batchEmails = document.getElementById("batchEmails");
    const item = document.createElement("div");

    item.className = "batch-item";
    item.innerHTML = `
        <div class="batch-item-header">
            <span class="batch-num"></span>
            <button class="ghost-btn" onclick="removeBatchItem(this)">Remove</button>
        </div>
        <textarea class="batch-textarea" placeholder="Paste email content here..."></textarea>
        <div class="batch-result hidden"></div>
    `;

    batchEmails.appendChild(item);
    updateBatchLabels();
}

function removeBatchItem(button) {
    const batchEmails = document.getElementById("batchEmails");

    if (batchEmails.children.length === 1) {
        const textarea = batchEmails.querySelector(".batch-textarea");
        const result = batchEmails.querySelector(".batch-result");
        textarea.value = "";
        clearBatchResult(result.closest(".batch-item"));
        return;
    }

    button.closest(".batch-item").remove();
    updateBatchLabels();
}

function updateBatchLabels() {
    document.querySelectorAll(".batch-item").forEach((item, index) => {
        item.querySelector(".batch-num").textContent = `Email ${index + 1}`;
    });
}

function renderBatchResults(results) {
    const items = document.querySelectorAll(".batch-item");

    items.forEach((item, index) => {
        const resultBox = item.querySelector(".batch-result");
        const result = results[index];

        if (!result) {
            clearBatchResult(item);
            return;
        }

        const theme = verdictThemeMap[result.verdict] || verdictThemeMap.SUSPICIOUS;
        const threats = Array.isArray(result.threats) ? result.threats.length : 0;

        resultBox.className = `batch-result ${theme.className}`;
        resultBox.classList.remove("hidden");
        resultBox.textContent = `${result.verdict} - ${normalizePercent(result.confidence).toFixed(1)}% confidence - ${threats} indicator(s) found`;
    });
}

function clearBatchResult(item) {
    const result = item.querySelector(".batch-result");
    result.className = "batch-result hidden";
    result.textContent = "";
}

function inferThreatSeverity(threat) {
    const text = String(threat).toLowerCase();

    if (
        text.includes("urgent")
        || text.includes("password")
        || text.includes("suspended")
        || text.includes("credential")
        || text.includes("bank")
    ) {
        return "high";
    }

    if (
        text.includes("link")
        || text.includes("verify")
        || text.includes("click")
        || text.includes("account")
    ) {
        return "medium";
    }

    return "low";
}

function normalizePercent(value) {
    const numeric = Number(value);

    if (Number.isNaN(numeric)) {
        return 0;
    }

    if (numeric <= 1) {
        return numeric * 100;
    }

    return numeric;
}
