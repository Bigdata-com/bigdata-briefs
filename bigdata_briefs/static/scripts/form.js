// Form submission handler
document.addEventListener('DOMContentLoaded', function() {
    const briefForm = document.getElementById('briefForm');
    if (!briefForm) return;
    
    briefForm.onsubmit = async function (e) {
        e.preventDefault();
        
        const spinner = document.getElementById('spinner');
        const submitBtn = document.querySelector('button[type="submit"]');
        const logViewer = document.getElementById('logViewer');

        // Close config panel
        if (window.closeConfigPanel) {
            closeConfigPanel();
        }

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

        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2 inline-block"></div>
            Generating...
        `;
        
        // Show spinner
        if (spinner) spinner.classList.remove('hidden');
        
        // Open logs
        const logViewerContainer = document.getElementById('logViewerContainer');
        if (logViewerContainer && logViewerContainer.classList.contains('hidden')) {
            toggleProcessLogs();
        }
        
        if (logViewer) logViewer.innerHTML = '<div class="text-text3">Starting brief generation...</div>';

        // Get companies based on selected input method
        let companies = null;
        if (currentCompanyInputMethod === 'watchlist') {
            const companiesText = document.getElementById('companies_text')?.value.trim();
            const foundWatchlist = watchlists.find(w => w.name === companiesText);
            if (foundWatchlist) {
                companies = foundWatchlist.id;
            } else if (companiesText) {
                // Could be a watchlist ID
                companies = companiesText;
            }
        } else if (currentCompanyInputMethod === 'csv') {
            const csvEntities = window.csvEntities || [];
            if (csvEntities.length > 0) {
                companies = csvEntities;
            }
        } else if (currentCompanyInputMethod === 'manual') {
            const manualInput = document.getElementById('companies_manual')?.value.trim();
            if (manualInput) {
                companies = manualInput.split(',').map(s => s.trim()).filter(Boolean);
            }
        }

        if (!companies || (Array.isArray(companies) && companies.length === 0)) {
            showError('Company Universe is required. Please select a watchlist, upload a CSV, or enter entity IDs manually.');
            resetFormState();
            return;
        }

        const start_date = document.getElementById('start_date')?.value;
        const end_date = document.getElementById('end_date')?.value;

        if (!start_date || !end_date) {
            showError('Start date and end date are required.');
            resetFormState();
            return;
        }

        // Build request payload
        let payload = {
            companies: companies,
            report_start_date: start_date,
            report_end_date: end_date
        };
        
        // Topics
        if (typeof topic_sentences !== 'undefined' && topic_sentences && topic_sentences.length > 0) {
            // Validate that ALL topics contain the {company} placeholder
            const topicsWithoutPlaceholder = topic_sentences.filter(topic => !topic.includes('{company}'));
            if (topicsWithoutPlaceholder.length > 0) {
                const failingTopicsList = topicsWithoutPlaceholder.map(topic => `• ${escapeHtml(topic)}`).join('<br>');
                showError(`The following topics are missing the {company} placeholder:<br>${failingTopicsList}`);
                resetFormState();
                return;
            }
            payload.topics = topic_sentences;
        }
        
        // Novelty
        const novelty = document.getElementById('novelty')?.checked || false;
        payload.novelty = novelty;
        
        // Sources
        const sourcesInput = document.getElementById('sources')?.value.trim();
        if (sourcesInput) {
            payload.sources = sourcesInput.split(',').map(s => s.trim()).filter(Boolean);
        }
        
        // Source Rank Boost
        const sourceRankBoost = document.getElementById('source_rank_boost')?.value;
        if (sourceRankBoost && sourceRankBoost !== '') {
            const value = parseInt(sourceRankBoost);
            if (!isNaN(value) && value >= 0 && value <= 10) {
                payload.source_rank_boost = value;
            }
        }
        
        // Freshness Boost
        const freshnessBoost = document.getElementById('freshness_boost')?.value;
        if (freshnessBoost && freshnessBoost !== '') {
            const value = parseInt(freshnessBoost);
            if (!isNaN(value) && value >= 0 && value <= 10) {
                payload.freshness_boost = value;
            }
        }

        // Include Title and Summary (for future backend support)
        const includeTitleSummary = document.getElementById('includeTitleSummary')?.checked;
        // Store for future use when backend supports it
        // payload.include_title_summary = includeTitleSummary;

        // Update header info
        updateHeaderInfo(start_date, end_date, companies);

        // Add token from URL param if present
        const params = new URLSearchParams();
        const token = getUrlParam('token');
        if (token) {
            params.append("token", token);
        }

        try {
            const response = await fetch(`/briefs/create?${params}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP error ${response.status}`);
            }
            
            const data = await response.json();
            
            // Start polling status endpoint
            if (data && data.request_id) {
                const requestId = data.request_id;
                pollStatus(requestId, params, submitBtn, spinner);
            } else {
                throw new Error('No request_id received from server');
            }
        } catch (err) {
            showError(`Error: ${err.message}`);
            resetFormState();
        }
    };
});

function showError(message) {
    const overviewContent = document.querySelector('[data-tab-content="overview"] .tab-actual-content');
    if (overviewContent) {
        overviewContent.innerHTML = `
            <div class="bg-red-900/20 border border-red-700/50 rounded-lg p-4">
                <p class="text-red-300">${message}</p>
            </div>
        `;
    }
    document.querySelectorAll('.loading-indicator').forEach(indicator => {
        indicator.classList.add('hidden');
    });
}

function resetFormState() {
    const submitBtn = document.querySelector('button[type="submit"]');
    const spinner = document.getElementById('spinner');
    
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            Generate Brief
        `;
    }
    if (spinner) spinner.classList.add('hidden');
}

function updateHeaderInfo(startDate, endDate, companies) {
    const dateRangeEl = document.getElementById('currentDateRange');
    const companiesEl = document.getElementById('currentCompanies');
    
    if (dateRangeEl) {
        const start = new Date(startDate).toLocaleDateString();
        const end = new Date(endDate).toLocaleDateString();
        dateRangeEl.textContent = `${start} - ${end}`;
    }
    
    if (companiesEl) {
        if (Array.isArray(companies)) {
            companiesEl.textContent = `${companies.length} companies`;
        } else {
            const watchlist = watchlists.find(w => w.id === companies);
            companiesEl.textContent = watchlist ? watchlist.name : 'Custom';
        }
    }
}

async function pollStatus(requestId, params, submitBtn, spinner) {
    const logViewer = document.getElementById('logViewer');
    let polling = true;
    
    async function poll() {
        try {
            const statusResp = await fetch(`/briefs/status/${requestId}?${params}`);
            if (!statusResp.ok) {
                throw new Error(`Status HTTP error ${statusResp.status}`);
            }
            
            const statusData = await statusResp.json();
            
            // Render logs if available
            if (logViewer && statusData.logs && Array.isArray(statusData.logs)) {
                logViewer.innerHTML = statusData.logs.map(line => {
                    let color = 'text-text2';
                    if (line.toLowerCase().includes('error')) color = 'text-red-400';
                    else if (line.toLowerCase().includes('success') || line.toLowerCase().includes('complete')) color = 'text-green-400';
                    else if (line.toLowerCase().includes('info')) color = 'text-blue-400';
                    return `<div class='mb-1 ${color}'>${escapeHtml(line)}</div>`;
                }).join('');
                logViewer.scrollTop = logViewer.scrollHeight;
            }
            
            // Stop polling if status is 'completed' or 'failed'
            if (statusData.status === 'completed' || statusData.status === 'failed') {
                polling = false;
                
                if (statusData.status === 'completed' && statusData.report) {
                    // Hide loading indicators
                    document.querySelectorAll('.loading-indicator').forEach(indicator => {
                        indicator.classList.add('hidden');
                    });
                    
                    // Render the report
                    if (window.renderBriefReport) {
                        renderBriefReport(statusData.report);
                    }
                    window.lastReport = statusData.report;
                } else if (statusData.status === 'failed') {
                    showError('Brief generation failed. Check logs for details.');
                }
                
                if (spinner) spinner.classList.add('hidden');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = `
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        Generate Brief
                    `;
                }
                return;
            }
        } catch (err) {
            if (logViewer) {
                logViewer.innerHTML += `<div class="text-red-400">❌ Status Error: ${escapeHtml(err.message)}</div>`;
            }
        }
        
        if (polling) {
            setTimeout(poll, 5000);
        }
    }
    
    poll();
}

// Show JSON button handler
document.addEventListener('DOMContentLoaded', function() {
    const showJsonBtn = document.getElementById('showJsonBtn');
    if (showJsonBtn) {
        showJsonBtn.onclick = function () {
            if (window.lastReport) {
                const jsonContent = document.getElementById('jsonContent');
                const jsonModal = document.getElementById('jsonModal');
                if (jsonContent && jsonModal) {
                    jsonContent.textContent = JSON.stringify(window.lastReport, null, 2);
                    jsonModal.classList.remove('hidden');
                }
            }
        };
    }
});
