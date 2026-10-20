// Build a DOM element without parsing HTML strings, so dynamic values are always inserted as text
function el(tag, attrs = {}, ...children) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs)) {
        if (key === 'className') node.className = value;
        else if (key.startsWith('on') && typeof value === 'function') node.addEventListener(key.slice(2), value);
        else node.setAttribute(key, value);
    }
    for (const child of children.flat()) {
        if (child === null || child === undefined || child === false) continue;
        node.append(child instanceof Node ? child : String(child));
    }
    return node;
}

// Join text lines with <br> elements
function linesWithBreaks(lines) {
    return lines.flatMap((line, i) => (i > 0 ? [el('br'), line] : [line]));
}

// Only allow http(s) links, so values like "javascript:" URLs are never rendered as hrefs
function safeUrl(url) {
    try {
        const parsed = new URL(url, window.location.href);
        return ['http:', 'https:'].includes(parsed.protocol) ? parsed.href : null;
    } catch (e) {
        return null;
    }
}

function externalLink(href, text, className = '') {
    return el('a', { href, target: '_blank', rel: 'noopener noreferrer', className }, text);
}

// Info modal content for each label
const infoContents = {
    topics: () => [
        el('b', {}, 'Topics'), ':', el('br'),
        'Specify the topics you want to analyze. Each topic must include the ', el('code', {}, '{company}'),
        ' placeholder which will be replaced with actual company names during analysis. You can specify multiple topics, one per line.',
        el('br'),
        el('i', {}, 'Examples: "What key takeaways emerged from {company}\'s latest earnings report?"'),
    ],
    companies: () => [
        el('b', {}, 'Company Universe'), ':', el('br'),
        'The portfolio of companies you want to create the brief for. You have several input options:',
        el('ul', { className: 'list-disc pl-6' },
            el('li', {}, 'Select one of the public watchlists using the dropdown menu'),
            el('li', {}, 'Write list of RavenPack entity IDs (e.g., ', el('code', {}, '4A6F00, D8442A'), ')'),
            el('li', {}, 'Input a watchlist ID (e.g., ', el('code', {}, '44118802-9104-4265-b97a-2e6d88d74893'), ' )'),
        ),
        el('br'),
        'Watchlists can be created programmatically using the ',
        externalLink('https://docs.bigdata.com/getting-started/watchlist_management', 'Bigdata.com SDK'),
        ' or through the ',
        externalLink('https://app.bigdata.com/watchlists', 'Bigdata app'),
        '.',
    ],
    start_date: () => [
        el('b', {}, 'Start/End Date'), ':', el('br'),
        'The start and end of the time sample during which you want to generate the brief. Format: ', el('code', {}, 'YYYY-MM-DD'), '.',
    ],
    novelty: () => [
        el('b', {}, 'Novelty'), ':', el('br'),
        'If set to true, the analysis will focus on novel events that have not been widely reported before, helping to identify emerging risks. If false, all relevant events will be considered, including those that have been frequently reported.',
    ],
    sources: () => [
        el('b', {}, 'Sources'), ':', el('br'),
        'Optionally, you can filter the analysis to include only events from specific sources. You can provide a list of RavenPack entity IDs separated by commas (e.g., ',
        el('code', {}, '9D69F1, B5235B'),
        '). If left empty, events from all sources will be considered.',
    ],
    load_example: () => [
        el('b', {}, 'Load Example'), ':', el('br'),
        'By clicking this button you will load an example output that is preloaded. By using it you can get an idea of the type of output you can expect from this workflow without waiting. The input data for the example is:',
        el('br'), el('br'),
        el('div', {}, el('span', { className: 'font-bold' }, 'Start date:'), ' 2025-10-01 00:00:00'),
        el('div', {}, el('span', { className: 'font-bold' }, 'End date:'), ' 2025-10-07 00:00:00'),
        el('div', {}, el('span', { className: 'font-bold' }, 'Topics:'), ' Default topics list'),
    ],
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

function renderModal(...content) {
    const overlay = el('div', { className: 'fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50' });
    overlay.addEventListener('click', (event) => {
        if (event.target === overlay) overlay.style.display = 'none';
    });
    const closeButton = el('button', { className: 'absolute top-3 right-3 text-gray-500 hover:text-gray-700 text-xl font-bold' }, '\u00d7');
    closeButton.addEventListener('click', () => { overlay.style.display = 'none'; });
    overlay.append(el('div', { className: 'bg-white rounded-lg shadow-lg w-full max-w-2xl p-6 relative' }, closeButton, ...content));
    document.getElementById('infoModalsContainer').replaceChildren(overlay);
}

function showInfoModal(label) {
    const content = infoContents[label] ? infoContents[label]() : ['No info available.'];
    renderModal(
        el('div', { className: 'text-base text-black' }, content),
        el('div', { className: 'mt-4 text-sm text-black' },
            'For a complete list of parameters and their descriptions, refer to the ',
            externalLink('http://localhost:8000/docs', 'API documentation', 'text-blue-600 underline'),
            '.',
        ),
    );
}

function showDocumentModal(document_id) {
    renderModal(
        el('div', { className: 'text-base font-bold text-black' }, 'DOCUMENT ID'),
        el('div', { className: 'text-base text-black' }, document_id),
    );
}

// Render a status log line as text, colored by its level
function renderLogLine(line) {
    let color = '';
    if (line.toLowerCase().includes('error')) color = 'text-red-400';
    else if (line.toLowerCase().includes('success')) color = 'text-green-400';
    else if (line.toLowerCase().includes('info')) color = 'text-sky-400';
    return el('div', { className: `mb-1 ${color}` }, line);
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

// Convert **bold** markers into <strong> elements, keeping everything else as text
function renderBoldText(text) {
    if (text === null || text === undefined) return [];
    return String(text).split(/\*\*(.*?)\*\*/g).map((part, i) => (i % 2 === 1 ? el('strong', {}, part) : part));
};
