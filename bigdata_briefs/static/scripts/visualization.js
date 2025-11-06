// Info modal content for each label
const infoContents = {
    topics: `<b>Topics</b>:<br>Specify the topics you want to analyze. Each topic must include the <code>{company}</code> placeholder which will be replaced with actual company names during analysis. You can specify multiple topics, one per line.<br><i>Examples: "What key takeaways emerged from {company}'s latest earnings report?"</i>`,
    companies: `<b>Company Universe</b>:<br>The portfolio of companies you want to create the brief for. You have several input options:<br><ul class="list-disc pl-6"><li>Select one of the public watchlists using the dropdown menu</li><li>Upload a CSV file with RavenPack entity IDs (one per line)</li><li>Manually enter a list of RavenPack entity IDs separated by commas (e.g., <code>4A6F00, D8442A</code>)</li><li>Input a watchlist ID (e.g., <code>44118802-9104-4265-b97a-2e6d88d74893</code>)</li></ul><br>Watchlists can be created programmatically using the <a href='https://docs.bigdata.com/getting-started/watchlist_management' target='_blank' class='text-blue-400 underline'>Bigdata.com SDK</a> or through the <a href='https://app.bigdata.com/watchlists' target='_blank' class='text-blue-400 underline'>Bigdata app</a>.`,
    start_date: `<b>Start Date</b>:<br>The start of the time period for which you want to generate the brief. Format: <code>YYYY-MM-DD</code>.`,
    end_date: `<b>End Date</b>:<br>The end of the time period for which you want to generate the brief. Format: <code>YYYY-MM-DD</code>.`,
    novelty: '<b>Novelty Filter</b>:<br>If enabled, the brief will focus on novel information that has not been included in previously generated briefs. This helps avoid redundant content and highlights new developments.',
    sources: `<b>Sources</b>:<br>Optionally, you can filter the brief to include only events from specific sources. You can provide a list of RavenPack entity IDs separated by commas (e.g., <code>9D69F1, B5235B</code>). If left empty, events from all sources will be considered.`,
    source_rank_boost: `<b>Source Rank Boost (0-10)</b>:<br>Controls how much the source rank influences relevance. Set to 0 to ignore source rank, or up to 10 for maximum effect, boosting chunks from premium sources.`,
    freshness_boost: `<b>Freshness Boost (0-10)</b>:<br>Controls the influence of document timestamp on relevance. Set to 0 to ignore publishing time (useful for point-in-time research), or up to 10 to heavily prioritize the most recent documents.`,
    includeTitleSummary: `<b>Include Title and Summary</b>:<br>When enabled, the brief will include a title and introduction/summary section. This feature is currently being prepared for backend support.`,
    load_example: `<b>Load Example</b>:<br>By clicking this button you will load an example output that is preloaded. By using it you can get an idea of the type of output you can expect from this workflow without waiting. The input data for the example is:<br><br><div><span class="font-bold">Start date:</span> 2025-10-01 00:00:00</div><div><span class="font-bold">End date:</span> 2025-10-07 00:00:00</div><div><span class="font-bold">Topics:</span> Default topics list</div>`,
};

// Toggle advanced options
function toggleAdvancedOptions() {
    const adv = document.getElementById('advanced-options');
    const btnIcon = document.getElementById('advancedOptionsIcon');
    if (!adv || !btnIcon) return;
    
    if (adv.classList.contains('hidden')) {
        adv.classList.remove('hidden');
        btnIcon.style.transform = 'rotate(180deg)';
    } else {
        adv.classList.add('hidden');
        btnIcon.style.transform = 'rotate(0deg)';
    }
}

// Make function globally available
window.toggleAdvancedOptions = toggleAdvancedOptions;

// Toggle process logs
function toggleProcessLogs() {
    const container = document.getElementById('logViewerContainer');
    const icon = document.getElementById('logsIcon');
    if (!container || !icon) return;
    
    if (container.classList.contains('hidden')) {
        container.classList.remove('hidden');
        icon.style.transform = 'rotate(180deg)';
    } else {
        container.classList.add('hidden');
        icon.style.transform = 'rotate(0deg)';
    }
}

window.toggleProcessLogs = toggleProcessLogs;

function showInfoModal(label) {
    let container = document.getElementById('infoModalsContainer');
    const content = infoContents[label] || 'No info available.';
    container.innerHTML = `
      <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/70" onclick="if(event.target==this)this.style.display='none'">
        <div class="bg-surface border border-border rounded-lg w-full max-w-2xl p-6 relative shadow-xl">
          <button class="absolute top-4 right-4 text-text3 hover:text-text transition-colors" onclick="this.closest('.fixed').style.display='none'">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
          <div class="text-sm text-text2 leading-relaxed">${content}</div>
          <div class="mt-4 pt-4 border-t border-border text-xs text-text3">For a complete list of parameters and their descriptions, refer to the <a href='/docs' target='_blank' class='text-blue-500 underline hover:text-blue-600'>API documentation</a>.</div>
        </div>
      </div>
    `;
}

// Make function globally available
window.showInfoModal = showInfoModal;

function showDocumentModal(document_id) {
    let container = document.getElementById('infoModalsContainer');
    container.innerHTML = `
      <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" onclick="if(event.target==this)this.style.display='none'">
        <div class="bg-white rounded-lg shadow-lg w-full max-w-2xl p-6 relative">
          <button class="absolute top-3 right-3 text-gray-500 hover:text-gray-700 text-xl font-bold" onclick="this.closest('.fixed').style.display='none'">&times;</button>
          <div class="text-base font-bold text-black">DOCUMENT ID</div>
          <div class="text-base text-black">${document_id}</div>
        </div>
      </div>
    `;
}

function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const str = String(text);
    return str.replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Helper to get URL param
function getUrlParam(name) {
    const url = new URL(window.location.href);
    return url.searchParams.get(name);
}

function toggleAdvancedOptions() {
    var adv = document.getElementById('advanced-options');
    var btnIcon = document.getElementById('advancedOptionsIcon');
    if (adv.style.display === 'none' || adv.classList.contains('hidden')) {
        adv.style.display = 'block';
        adv.classList.remove('hidden');
        btnIcon.textContent = '-';
    } else {
        adv.style.display = 'none';
        adv.classList.add('hidden');
        btnIcon.textContent = '+';
    }
}

function closeModal() {
    document.getElementById('jsonModal').style.display = 'none';
}

function copyJson() {
    const jsonContent = document.getElementById('jsonContent');
    if (!jsonContent) return;
    const text = jsonContent.innerText || jsonContent.textContent;
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            const btn = document.getElementById('copyBtn');
            if (btn) {
                const orig = btn.textContent;
                btn.textContent = 'Copied!';
                setTimeout(() => { btn.textContent = orig; }, 1200);
            }
        });
    } else {
        // fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.setAttribute('readonly', '');
        textarea.style.position = 'absolute';
        textarea.style.left = '-9999px';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            const btn = document.getElementById('copyBtn');
            if (btn) {
                const orig = btn.textContent;
                btn.textContent = 'Copied!';
                setTimeout(() => { btn.textContent = orig; }, 1200);
            }
        } catch (err) { }
        document.body.removeChild(textarea);
    }
};

function renderBoldText(text) {
    if (text === null || text === undefined) return '';
    const str = String(text);
    return str.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
};