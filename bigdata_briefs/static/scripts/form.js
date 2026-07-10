document.getElementById('briefForm').onsubmit = async function (e) {
    e.preventDefault();
    const output = document.getElementById('output');
    const spinner = document.getElementById('spinner');
    const submitBtn = document.querySelector('#briefForm button[type="submit"]');
    output.innerHTML = '';
    output.classList.remove('error');
    if (typeof showReportActions === 'function') {
        showReportActions(false);
    }
    window.lastReport = null;

    submitBtn.disabled = true;
    submitBtn.textContent = 'Waiting for response...';

    // Prefer free-text; fall back to dropdown selection
    let companies = document.getElementById('companies_text').value.trim();
    const selectedWatchlist = document.getElementById('companies').value;
    if (!companies && selectedWatchlist && selectedWatchlist !== '__custom__') {
        companies = selectedWatchlist;
    }
    const foundWatchlist = watchlists.find(w => w.name === companies || w.id === companies);
    if (foundWatchlist) {
        companies = foundWatchlist.id;
    } else if (!companies) {
        output.innerHTML = `<span class="error text-red-400">❌ Error: Company Universe is required.</span>`;
        output.classList.add('error');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Generate Brief';
        return;
    }
    const start_date = document.getElementById('start_date').value;
    const end_date = document.getElementById('end_date').value;

    let payload = {};

    let topicsArray = [];
    if (typeof topic_sentences !== 'undefined' && topic_sentences.length > 0) {
        topicsArray = topic_sentences;
    }

    if (topicsArray.length > 0) {
        const topicsWithoutPlaceholder = topicsArray.filter(topic => !topic.includes('{entity}'));
        if (topicsWithoutPlaceholder.length > 0) {
            const failingTopicsList = topicsWithoutPlaceholder.map(topic => `• ${escapeHtml(topic)}`).join('<br>');
            output.innerHTML = `<span class="error text-red-400">❌ Error: The following topics are missing the {entity} placeholder:<br>${failingTopicsList}</span>`;
            output.classList.add('error');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Generate Brief';
            return;
        }
        payload.topics = topicsArray;
    }
    const novelty = document.getElementById('novelty').value === 'true';
    let sources = document.getElementById('sources').value.trim();
    if (sources) {
        if (sources.includes(',')) {
            payload.sources = sources.split(',').map(s => s.trim()).filter(Boolean);
        } else {
            payload.sources = [sources];
        }
    }

    if (companies.includes(',')) {
        payload.entities = companies.split(',').map(s => s.trim()).filter(Boolean);
    } else if (companies.length === 6) {
        payload.entities = [companies];
    } else if (companies.length > 6) {
        payload.entities = companies;
    }

    if (start_date) payload.report_start_date = start_date;
    if (end_date) payload.report_end_date = end_date;
    payload.novelty = novelty;

    const params = new URLSearchParams();
    const token = getUrlParam('token');
    if (token) {
        params.append("token", token);
    }

    // Clear any Quick Demo selection and open process-log popup
    if (typeof clearActiveDemo === 'function') {
        clearActiveDemo();
    }
    if (typeof openProcessLogs === 'function') {
        openProcessLogs();
    }

    try {
        const response = await apiRequest(`/briefs/create?${params}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        const data = await response.json();
        if (data && data.request_id) {
            const requestId = data.request_id;
            let polling = true;
            const logViewer = document.getElementById('logViewer');
            async function pollStatus() {
                try {
                    const statusResp = await apiRequest(`/briefs/status/${requestId}?${params}`);
                    if (!statusResp.ok) {
                        throw new Error(`Status HTTP error ${statusResp.status}`);
                    }
                    const statusData = await statusResp.json();
                    spinner.style.display = 'block';
                    if (statusData.logs && Array.isArray(statusData.logs)) {
                        logViewer.innerHTML = statusData.logs.map(line => {
                            let base = 'mb-1';
                            let color = '';
                            if (line.toLowerCase().includes('error')) color = 'text-red-400';
                            else if (line.toLowerCase().includes('success')) color = 'text-green-400';
                            else if (line.toLowerCase().includes('info')) color = 'text-sky-400';
                            return `<div class='${base} ${color}'>${line}</div>`;
                        }).join('');
                        logViewer.scrollTop = logViewer.scrollHeight;
                    } else if (statusData.log) {
                        logViewer.textContent = statusData.log;
                    } else {
                        logViewer.textContent = 'No logs yet.';
                    }
                    if (statusData.status === 'completed' || statusData.status === 'failed') {
                        polling = false;
                        if (statusData.status === 'completed') {
                            output.innerHTML = renderBriefReport(statusData.report);
                            window.lastReport = statusData.report;
                            if (typeof showReportActions === 'function') {
                                showReportActions(true);
                            }
                        } else {
                            output.innerHTML = `<span class="text-red-400">❌ Brief generation failed. See process logs.</span>`;
                        }
                        spinner.style.display = 'none';
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Generate Brief';
                        const statusEl = document.getElementById('logsPopupStatus');
                        if (statusEl) {
                            statusEl.textContent = statusData.status === 'completed' ? 'Completed' : 'Failed';
                        }
                        // Auto-close logs popup when the run finishes
                        if (typeof closeProcessLogs === 'function') {
                            setTimeout(() => closeProcessLogs(), 800);
                        }
                        return;
                    }
                } catch (err) {
                    logViewer.innerHTML = `<div class="log-line log-error text-red-400">❌ Status Error: ${err.message}</div>`;
                }
                if (polling) {
                    setTimeout(pollStatus, 5000);
                }
            }
            pollStatus();
        }
    } catch (err) {
        output.innerHTML = `<span class="error text-red-400">❌ Error: ${err.message}</span>`;
        output.classList.add('error');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Generate Brief';
        spinner.style.display = 'none';
        if (typeof closeProcessLogs === 'function') {
            closeProcessLogs();
        }
    }
};

function showJsonModal() {
    if (!window.lastReport) {
        alert('No brief loaded yet. Open a Quick Demo or generate a brief first.');
        return;
    }
    document.getElementById('jsonContent').textContent = JSON.stringify(window.lastReport, null, 2);
    const modal = document.getElementById('jsonModal');
    modal.classList.remove('hidden');
    modal.style.display = 'block';
}
window.showJsonModal = showJsonModal;
