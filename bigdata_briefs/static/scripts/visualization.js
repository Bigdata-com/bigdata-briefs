// Info modal content for each label
const infoContents = {
    topics: `<b>Topics</b>:<br>Specify the topics you want to analyze. Each topic must include the <code>{company}</code> placeholder which will be replaced with actual company names during analysis. You can specify multiple topics, one per line.<br><i>Examples: "What key takeaways emerged from {company}'s latest earnings report?"</i>`,
    companies: `<b>Company Universe</b>:<br>The portfolio of companies you want to create the brief for. You have several input options:<br><ul class="list-disc pl-6"><li>Select one of the public watchlists using the dropdown menu</li><li>Write list of RavenPack entity IDs (e.g., <code>4A6F00, D8442A</code>)</li><li>Input a watchlist ID (e.g., <code>44118802-9104-4265-b97a-2e6d88d74893</code> )</li></ul><br>Watchlists can be created programmatically using the <a href='https://docs.bigdata.com/getting-started/watchlist_management' target='_blank'>Bigdata.com SDK</a> or through the <a href='https://app.bigdata.com/watchlists' target='_blank'>Bigdata app</a>.`,
    start_date: `<b>Start/End Date</b>:<br>The start and end of the time sample during which you want to generate the brief. Format: <code>YYYY-MM-DD</code>.`,
    novelty: '<b>Novelty</b>:<br>If set to true, the analysis will focus on novel events that have not been widely reported before, helping to identify emerging risks. If false, all relevant events will be considered, including those that have been frequently reported.',
    sources: `<b>Sources</b>:<br>Optionally, you can filter the analysis to include only events from specific sources. You can provide a list of RavenPack entity IDs separated by commas (e.g., <code>9D69F1, B5235B</code>). If left empty, events from all sources will be considered.`,
    load_example: `<b>Load Example</b>:<br>By clicking this button you will load an example output that is preloaded. By using it you can get an idea of the type of output you can expect from this workflow without waiting. The input data for the example is:<br><br><div><span class="font-bold">Start date:</span> 2025-10-01 00:00:00</div><div><span class="font-bold">End date:</span> 2025-10-07 00:00:00</div><div><span class="font-bold">Topics:</span> Default topics list</div>`,
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
          <div class="mt-4 text-sm text-black">For a complete list of parameters and their descriptions, refer to the <a href='http://localhost:8000/docs' target='_blank' class='text-blue-600 underline'>API documentation</a>.</div>
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