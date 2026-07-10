async function loadRequestId(requestId) {
    const output = document.getElementById('output');
    if (typeof showReportActions === 'function') {
        showReportActions(false);
    }
    window.lastReport = null;

    const params = new URLSearchParams();
    const token = getUrlParam('token');
    if (token) {
        params.append("token", token);
    }
    const logViewer = document.getElementById('logViewer');
    if (logViewer) {
        logViewer.textContent = 'Loading demo brief…';
    }

    const statusResp = await apiRequest(`/briefs/status/${requestId}?${params}`);
    if (!statusResp.ok) {
        throw new Error(`Status HTTP error ${statusResp.status}`);
    }
    const statusData = await statusResp.json();
    if (logViewer) {
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
            logViewer.textContent = 'Demo loaded.';
        }
    }
    if (statusData.status === 'completed') {
        output.innerHTML = renderBriefReport(statusData.report);
        window.lastReport = statusData.report;
        if (typeof showReportActions === 'function') {
            showReportActions(true);
        }
        // Keep logs collapsed for instant demos
        if (typeof closeProcessLogs === 'function') {
            closeProcessLogs();
        }
    } else if (statusData.status === 'failed') {
        output.innerHTML = `<span class="text-red-400">❌ Demo brief failed to load.</span>`;
    } else {
        output.innerHTML = `<span class="text-amber-300">Demo is not ready yet (status: ${escapeHtml(statusData.status || 'unknown')}).</span>`;
    }
}
