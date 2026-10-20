// Load Example function that accepts requestId as parameter
async function loadRequestId(requestId) {
    // Load example data into the form
    // Add token from URL param if present
    const showJsonBtn = document.getElementById('showJsonBtn');
    showJsonBtn.style.display = 'none';
    lastReport = null;

    const params = new URLSearchParams();
    const token = getUrlParam('token');
    if (token) {
        params.append("token", token);
    }
    const logViewer = document.getElementById('logViewer');

    const statusResp = await fetch(`/briefs/status/${requestId}?${params}`);
    if (!statusResp.ok) {
        throw new Error(`Status HTTP error ${statusResp.status}`);
    }
    const statusData = await statusResp.json();
    // Render logs if available
    if (statusData.logs && Array.isArray(statusData.logs)) {
        logViewer.replaceChildren(...statusData.logs.map(renderLogLine));
        logViewer.scrollTop = logViewer.scrollHeight;
    } else if (statusData.log) {
        logViewer.textContent = statusData.log;
    } else {
        logViewer.textContent = 'No logs yet.';
    }
    // Stop polling if status is 'completed' or 'failed'
    if (statusData.status === 'completed') {
        output.replaceChildren(renderBriefReport(statusData.report));
        showJsonBtn.style.display = 'inline-block';
        lastReport = statusData.report;
    }
};