// Info modal content for each label
const infoContents = {
    topics: `<b>Topics</b>:<br>Specify the topics you want to analyze. Each topic must include the <code>{entity}</code> placeholder, which is replaced with each entity name during analysis. You can specify multiple topics, one per line.<br><i>Examples: "What key takeaways emerged from {entity}'s latest earnings report?"</i>`,
    companies: `<b>Company Universe</b>:<br>Choose how to define the universe:<br><ul class="list-disc pl-6"><li><b>Dropdown</b> — pick a preconfigured watchlist (AI Scene, Commodities, Countries, Magnificent 7, etc.)</li><li><b>Watchlist ID</b> — paste a Bigdata.com watchlist UUID</li><li><b>Entity IDs</b> — comma-separated RavenPack IDs (e.g. <code>4A6F00, D8442A</code>)</li></ul><br>Watchlists: <a href='https://app.bigdata.com/watchlists' target='_blank'>app.bigdata.com/watchlists</a>`,
    start_date: `<b>Start/End Date</b>:<br>The start and end of the time sample during which you want to generate the brief. Format: <code>YYYY-MM-DD</code>.`,
    novelty: '<b>Novelty</b>:<br>If set to true, the analysis will focus on novel events that have not been widely reported before, helping to identify emerging risks. If false, all relevant events will be considered, including those that have been frequently reported.',
    sources: `<b>Sources</b>:<br>Optionally, you can filter the analysis to include only events from specific sources. You can provide a list of RavenPack entity IDs separated by commas (e.g., <code>9D69F1, B5235B</code>). If left empty, events from all sources will be considered.`,
    load_example: `<b>Quick demos</b>:<br>Load a precomputed brief instantly — no wait.<br><br>
      <div class="mb-2"><span class="font-bold">AI Scene</span> — tech/AI leaders (period: 2026-07-02 → 2026-07-09)</div>
      <div class="mb-2"><span class="font-bold">Commodities</span> — oil, gold, copper, natural gas (period: 2026-07-02 → 2026-07-09)<br>
      <a href="https://app.bigdata.com/watchlists/e3e9d089-0668-4e2b-85f6-4179a447e3c9" target="_blank" class="text-blue-600 underline">Open watchlist</a></div>
      <div><span class="font-bold">Countries</span> — US, China, Germany, Japan, India (period: 2026-07-02 → 2026-07-09)<br>
      <a href="https://app.bigdata.com/watchlists/164fa89e-1aa6-4a38-a84f-ce6063c61023" target="_blank" class="text-blue-600 underline">Open watchlist</a></div>`,
};

document.addEventListener('DOMContentLoaded', function () {
    const dragbar = document.getElementById('dragbar');
    const sidebar = document.getElementById('sidebar');
    const outputarea = document.getElementById('outputarea');
    let dragging = false;

    dragbar.addEventListener('mousedown', function (e) {
        dragging = true;
        document.body.classList.add('cursor-ew-resize');
        document.body.style.userSelect = 'none';
    });

    document.addEventListener('mousemove', function (e) {
        if (!dragging) return;
        const minSidebar = 250;
        const maxSidebar = 600;
        let newWidth = Math.min(Math.max(e.clientX - sidebar.getBoundingClientRect().left, minSidebar), maxSidebar);
        sidebar.style.width = newWidth + 'px';
        // outputarea will flex to fill remaining space
    });

    document.addEventListener('mouseup', function (e) {
        if (dragging) {
            dragging = false;
            document.body.classList.remove('cursor-ew-resize');
            document.body.style.userSelect = '';
        }
    });
});

function showInfoModal(label) {
    let container = document.getElementById('infoModalsContainer');
    container.innerHTML = `
      <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" onclick="if(event.target==this)this.style.display='none'">
        <div class="bg-white rounded-lg shadow-lg w-full max-w-2xl p-6 relative">
          <button class="absolute top-3 right-3 text-gray-500 hover:text-gray-700 text-xl font-bold" onclick="this.closest('.fixed').style.display='none'">&times;</button>
          <div class="text-base text-black">${infoContents[label] || 'No info available.'}</div>
          <div class="mt-4 text-sm text-black">For a complete list of parameters and their descriptions, refer to the <a href='/docs' target='_blank' class='text-blue-600 underline'>API documentation</a>.</div>
        </div>
      </div>
    `;
}

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
    const modal = document.getElementById('jsonModal');
    if (!modal) return;
    modal.style.display = 'none';
    modal.classList.add('hidden');
}

function downloadBriefJson() {
    const report = window.lastReport;
    if (!report) {
        alert('No brief loaded yet. Open a Quick Demo or generate a brief first.');
        return;
    }
    try {
        const text = JSON.stringify(report, null, 2);
        const name = String(report.watchlist_name || 'brief')
            .replace(/[^a-z0-9_-]+/gi, '_')
            .replace(/^_+|_+$/g, '')
            .toLowerCase() || 'brief';
        const filename = `${name}_brief.json`;

        // IE / legacy Edge
        if (window.navigator && typeof window.navigator.msSaveOrOpenBlob === 'function') {
            window.navigator.msSaveOrOpenBlob(
                new Blob([text], { type: 'application/json' }),
                filename
            );
            return;
        }

        const blob = new Blob([text], { type: 'application/json;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.rel = 'noopener';
        a.style.cssText = 'position:fixed;left:-9999px;top:0;';
        document.body.appendChild(a);
        a.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
        setTimeout(() => {
            a.remove();
            URL.revokeObjectURL(url);
        }, 2000);
    } catch (err) {
        alert(`Download failed: ${err.message || err}`);
    }
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

window.closeModal = closeModal;
window.copyJson = copyJson;
window.downloadBriefJson = downloadBriefJson;