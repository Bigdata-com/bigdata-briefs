// Report Renderer - Handles rendering brief reports in tabbed interface

function formatIntroduction(text) {
    if (!text) return '';

    // Split by newlines to get individual lines
    const lines = text.split('\n');

    return lines.map(line => {
        // Strip leading * and any whitespace after it
        const cleanedLine = line.replace(/^\*\s*/, '');
        
        // Use renderBoldText to handle ** formatting, then escape the result
        return renderBoldText(escapeHtml(cleanedLine));
    }).join('<br>');
}

function renderBriefReport(data) {
    if (!data || typeof data !== 'object') {
        showError('No data to display.');
        return;
    }

    // Hide loading indicators
    document.querySelectorAll('.loading-indicator').forEach(indicator => {
        indicator.classList.add('hidden');
    });

    // Render Overview tab
    renderOverviewTab(data);

    // Render Company Reports tab
    renderCompanyReportsTab(data);

    // Render Audit tab
    console.log('[ReportRenderer] Rendering Audit tab:', {
        hasEntityReports: !!data.entity_reports,
        entityReportsCount: data.entity_reports?.length,
        hasSourceMetadata: !!data.source_metadata,
        sourceMetadataType: typeof data.source_metadata,
        sourceMetadataKeys: data.source_metadata ? Object.keys(data.source_metadata).slice(0, 3) : [],
        hasAuditTable: !!window.auditTable
    });
    
    if (data.entity_reports && data.source_metadata && window.auditTable) {
        console.log('[ReportRenderer] Calling auditTable.init()');
        // Handle both direct dict and RootModel format
        const sourceMetadata = data.source_metadata.root || data.source_metadata;
        window.auditTable.init(data.entity_reports, sourceMetadata);
    } else {
        console.warn('[ReportRenderer] Cannot render Audit tab - missing dependencies:', {
            entity_reports: !data.entity_reports,
            source_metadata: !data.source_metadata,
            auditTable: !window.auditTable
        });
    }
}

function renderOverviewTab(data) {
    const overviewContent = document.querySelector('[data-tab-content="overview"] .tab-actual-content');
    if (!overviewContent) return;

    // Format dates to show only YYYY-MM-DD
    const formatDateOnly = (isoString) => {
        if (!isoString) return '';
        return isoString.split('T')[0];
    };

    let html = '';

    // Title
    if (data.report_title) {
        html += `<div class="mb-6">
            <h1 class="text-3xl font-bold text-text mb-2">${escapeHtml(data.report_title)}</h1>
        </div>`;
    }

    // Introduction section
    if (data.introduction) {
        html += `<div class="bg-surface2 border border-border rounded-lg p-6 mb-6">
            <h2 class="text-xl font-semibold text-text mb-4">Summary</h2>
            <div class="leading-relaxed text-text2 space-y-2">
                ${formatIntroduction(data.introduction)}
            </div>
        </div>`;
    } else {
        html += `<div class="bg-surface2 border border-border rounded-lg p-6 mb-6">
            <p class="text-text3 italic">No summary available for this brief.</p>
        </div>`;
    }

    // Additional metadata if available
    if (data.novelty !== undefined) {
        html += `<div class="flex items-center gap-2 text-sm text-text3">
            <span>Novelty filter: ${data.novelty ? 'Enabled' : 'Disabled'}</span>
        </div>`;
    }

    overviewContent.innerHTML = html;
}

function renderCompanyReportsTab(data) {
    const companiesContent = document.querySelector('[data-tab-content="companies"] .tab-actual-content');
    if (!companiesContent) return;

    // Use the company browser to render companies
    if (window.companyBrowser && Array.isArray(data.entity_reports) && data.entity_reports.length > 0) {
        window.companyBrowser.init(data.entity_reports, data.source_metadata);
    } else {
        companiesContent.innerHTML = `
            <div class="text-center py-12">
                <p class="text-text3 text-lg">No company reports available.</p>
            </div>
        `;
    }
}

function showError(message) {
    const overviewContent = document.querySelector('[data-tab-content="overview"] .tab-actual-content');
    if (overviewContent) {
        overviewContent.innerHTML = `
            <div class="bg-red-900/20 border border-red-700/50 rounded-lg p-4">
                <p class="text-red-400">${escapeHtml(message)}</p>
            </div>
        `;
    }
}

// Make function globally available
window.renderBriefReport = renderBriefReport;
