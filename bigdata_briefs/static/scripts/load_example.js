// Load Example function that accepts requestId as parameter
async function loadRequestId(requestId) {
    // Hide empty state and show dashboard
    const emptyState = document.getElementById('emptyState');
    const dashboardSection = document.getElementById('dashboardSection');
    if (emptyState) emptyState.style.display = 'none';
    if (dashboardSection) dashboardSection.classList.remove('hidden');

    // Clear previous results
    window.lastReport = null;
    const overviewContent = document.querySelector('[data-tab-content="overview"] .tab-actual-content');
    const companiesContent = document.querySelector('[data-tab-content="companies"] .tab-actual-content');
    if (overviewContent) overviewContent.innerHTML = '';
    if (companiesContent) companiesContent.innerHTML = '';

    // Show loading indicators
    document.querySelectorAll('.loading-indicator').forEach(indicator => {
        indicator.classList.remove('hidden');
    });

    // Add token from URL param if present
    const params = new URLSearchParams();
    const token = getUrlParam('token');
    if (token) {
        params.append("token", token);
    }
    
    const logViewer = document.getElementById('logViewer');
    const logViewerContainer = document.getElementById('logViewerContainer');
    
    // Open logs
    if (logViewerContainer && logViewerContainer.classList.contains('hidden')) {
        toggleProcessLogs();
    }

    try {
        const statusResp = await fetch(`/briefs/status/${requestId}?${params}`);
        if (!statusResp.ok) {
            throw new Error(`Status HTTP error ${statusResp.status}`);
        }
        
        const statusData = await statusResp.json();
        
        // Render logs if available
        if (logViewer && statusData.logs && Array.isArray(statusData.logs)) {
            logViewer.innerHTML = statusData.logs.map(line => {
                let color = 'text-zinc-300';
                if (line.toLowerCase().includes('error')) color = 'text-red-400';
                else if (line.toLowerCase().includes('success') || line.toLowerCase().includes('complete')) color = 'text-green-400';
                else if (line.toLowerCase().includes('info')) color = 'text-blue-400';
                return `<div class='mb-1 ${color}'>${escapeHtml(line)}</div>`;
            }).join('');
            logViewer.scrollTop = logViewer.scrollHeight;
        } else if (logViewer && statusData.log) {
            logViewer.textContent = statusData.log;
        } else if (logViewer) {
            logViewer.textContent = 'No logs available.';
        }
        
        // Render report if completed
        if (statusData.status === 'completed' && statusData.report) {
            // Hide loading indicators
            document.querySelectorAll('.loading-indicator').forEach(indicator => {
                indicator.classList.add('hidden');
            });

            // Save request ID for debug tab
            window.lastRequestId = requestId;

            // Update header info
            const report = statusData.report;
            if (window.updateHeaderInfo) {
                window.updateHeaderInfo(
                    report.start_date,
                    report.end_date,
                    report.watchlist_id,
                    report.watchlist_name
                );
            }

            // Render the report using the new renderer
            if (window.renderBriefReport) {
                window.renderBriefReport(report);
            }
            
            window.lastReport = report;
            
            // Emit event for debug tab
            const event = new CustomEvent('reportLoaded', { 
                detail: { requestId: requestId } 
            });
            document.dispatchEvent(event);
        } else if (statusData.status === 'failed') {
            showError('Failed to load example. The brief generation may have failed.');
        }
    } catch (err) {
        showError(`Error loading example: ${err.message}`);
    }
}

function showError(message) {
    const overviewContent = document.querySelector('[data-tab-content="overview"] .tab-actual-content');
    if (overviewContent) {
        overviewContent.innerHTML = `
            <div class="bg-red-900/20 border border-red-700/50 rounded-lg p-4">
                <p class="text-red-300">${escapeHtml(message)}</p>
            </div>
        `;
    }
    document.querySelectorAll('.loading-indicator').forEach(indicator => {
        indicator.classList.add('hidden');
    });
}

// Make function globally available
window.loadRequestId = loadRequestId;
