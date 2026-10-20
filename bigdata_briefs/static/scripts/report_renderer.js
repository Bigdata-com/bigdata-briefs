function toggleHighlights(button) {
    const highlights = button.closest('.highlights');
    const isCollapsed = highlights.classList.contains('collapsed');
    const extraItems = highlights.querySelectorAll('.extra');

    if (isCollapsed) {
        highlights.classList.remove('collapsed');
        extraItems.forEach(item => {
            item.classList.remove('hidden');
        });
        button.textContent = 'Show Less';
    } else {
        highlights.classList.add('collapsed');
        extraItems.forEach(item => {
            item.classList.add('hidden');
        });
        button.textContent = 'Show More';
    }
}

// Build an SVG icon (Heroicons) from static path definitions
function svgIcon(paths) {
    const SVG_NS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(SVG_NS, 'svg');
    svg.setAttribute('class', 'h-5 w-5 mr-2 text-slate-400');
    svg.setAttribute('viewBox', '0 0 20 20');
    svg.setAttribute('fill', 'currentColor');
    paths.forEach(({ d, evenodd }) => {
        const path = document.createElementNS(SVG_NS, 'path');
        path.setAttribute('d', d);
        if (evenodd) {
            path.setAttribute('fill-rule', 'evenodd');
            path.setAttribute('clip-rule', 'evenodd');
        }
        svg.appendChild(path);
    });
    return svg;
}

const ICON_SOURCE = [{ d: 'M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z', evenodd: true }];
const ICON_TITLE = [{ d: 'M9 2a1 1 0 000 2h2a1 1 0 100-2H9z' }, { d: 'M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3z', evenodd: true }];
const ICON_URL = [{ d: 'M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z' }, { d: 'M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z' }];

function formatIntroduction(text) {
    if (!text) return [];

    // Split by newlines to get individual lines, strip leading * and any whitespace after it
    const lines = text.split('\n').map(line => renderBoldText(line.replace(/^\*\s*/, '')));
    return linesWithBreaks(lines);
}

function renderSourceTooltip(sources, sourceMetadataById) {
    const tooltip = el('div', { className: 'source-tooltip absolute bottom-full right-0 bg-slate-800/95 backdrop-blur-md text-slate-300 p-3 rounded-lg w-[500px] text-xs leading-snug opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 z-50 shadow-xl mb-2 border border-slate-600' });

    sources.forEach((sourceId, sourceIndex) => {
        // Use optional chaining and provide a default empty object for robustness
        const sourceMetadata = sourceMetadataById?.[sourceId] || {};

        // Destructure properties with default values
        const {
            text = "No text available",
            headline = 'No headline available',
            source_name: sourceName = 'Unknown Source',
            url
        } = sourceMetadata;

        // Use a container for each source to handle spacing, removing the need for <hr>
        // This creates a more modern, card-based layout
        const card = el('div', { className: `p-3 rounded-lg bg-slate-800 border border-slate-700/50 hover:bg-slate-700/50 hover:border-slate-600 transition-all duration-200 ease-in-out ${sourceIndex > 0 ? 'mt-3' : ''}` });

        if (sourceName !== 'Unknown Source') {
            card.append(el('div', { className: 'flex items-center text-base font-semibold text-sky-400 mb-2 pb-2 border-b border-slate-700' },
                svgIcon(ICON_SOURCE),
                el('span', {}, sourceName),
            ));
            const details = el('div', { className: 'space-y-2 text-sm' },
                el('div', { className: 'flex items-start' },
                    el('div', { className: 'flex-shrink-0' }, svgIcon(ICON_TITLE)),
                    el('span', { className: 'text-slate-300' }, text),
                ),
            );
            const href = url ? safeUrl(url) : null;
            if (href) {
                details.append(el('div', { className: 'flex items-start' },
                    el('div', { className: 'flex-shrink-0' }, svgIcon(ICON_URL)),
                    externalLink(href, url, 'text-blue-400 hover:text-blue-300 underline break-all'),
                ));
            }
            card.append(details);
        } else {
            // A styled fallback for sources without metadata
            card.append(el('div', { className: 'text-slate-500 italic' }, `Source reference: ${sourceId}`));
        }

        tooltip.append(card);
    });

    tooltip.append(el('div', { className: 'absolute top-full right-4 w-0 h-0 border-x-[6px] border-x-transparent border-t-[6px] border-t-slate-800' }));
    return tooltip;
}

function renderEntityCard(entity, data) {
    const entityName = (entity.entity_info && (entity.entity_info.name || entity.entity_info.id))
        ? (entity.entity_info.name || entity.entity_info.id)
        : entity.entity_id;

    // Extract entity metadata if available
    const ticker = entity.entity_info?.ticker || entity.entity_info?.symbol || '';
    const country = entity.entity_info?.country || entity.entity_info?.location || '';
    const industry = entity.entity_info?.industry || entity.entity_info?.sector || '';

    const highlights = Array.isArray(entity.content) ? entity.content : [];

    // Build card: Changed to a dark, blurred background with refined padding and borders.
    const card = el('div', { className: 'bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-8 shadow-2xl text-white' });

    // Company header section
    card.append(el('div', { className: 'mb-5' },
        el('div', { className: 'text-3xl font-bold text-slate-100 mb-3' }, entityName),
        el('div', { className: 'flex flex-wrap items-center gap-4' },
            ticker && el('span', { className: 'inline-block bg-slate-700 text-blue-400 text-xs font-bold px-3 py-1 rounded-full' }, ticker),
            country && el('span', { className: 'text-sm text-slate-400 flex items-center gap-1.5' }, country),
            industry && el('span', { className: 'bg-blue-500/20 text-blue-300 text-xs font-semibold px-3 py-1 rounded-full' }, industry),
        ),
    ));

    // Divider for better separation.
    card.append(el('hr', { className: 'border-slate-700 my-6' }));

    // Highlights section
    if (highlights.length === 0) {
        card.append(el('p', { className: 'text-sm text-slate-400 italic' }, 'No highlights available.'));
        return card;
    }

    const hasMore = highlights.length > 2;
    const highlightsContainer = el('div', { className: `highlights space-y-4 ${hasMore ? 'collapsed' : ''}` });

    highlights.forEach((bp, i) => {
        const isExtra = i >= 2;
        const paragraph = el('p', { className: 'text-slate-300 leading-relaxed' });

        // Source indicator with a restyled tooltip for the dark theme.
        if (Array.isArray(bp.sources) && bp.sources.length > 0) {
            paragraph.append(el('div', { className: 'source-indicator absolute -top-2 -right-2 w-7 h-7 bg-blue-600 rounded-full flex items-center justify-center text-sm font-bold text-white shadow-md cursor-help group' },
                String(bp.sources.length),
                renderSourceTooltip(bp.sources, data.source_metadata),
            ));
        }

        paragraph.append(...renderBoldText(bp.bullet_point));
        highlightsContainer.append(el('div', { className: `relative bg-slate-900/50 p-5 rounded-lg border-l-4 border-blue-500 ${isExtra ? 'extra hidden' : ''}` }, paragraph));
    });

    // "Show More" button with updated styling.
    if (hasMore) {
        const button = el('button', { className: 'w-full bg-blue-600 hover:bg-blue-700 transition-all duration-300 text-white font-semibold py-3 px-6 rounded-lg shadow-lg shadow-blue-600/20 mt-4' }, 'Show More');
        button.addEventListener('click', () => toggleHighlights(button));
        highlightsContainer.append(button);
    }

    card.append(highlightsContainer);
    return card;
}

// Render the brief report as DOM nodes, so report content is never parsed as HTML
function renderBriefReport(data) {
    const fragment = document.createDocumentFragment();
    if (!data || typeof data !== 'object') {
        fragment.append(el('span', { className: 'error' }, 'No data to display.'));
        return fragment;
    }

    // Header section with watchlist badge, date range and title
    fragment.append(el('div', { className: 'mb-8' },
        el('div', { className: 'mb-4' },
            el('span', { className: 'inline-block bg-gradient-to-br from-blue-500 to-blue-700 text-white px-5 py-2 rounded-full text-2xl font-semibold mr-4' }, data.watchlist_name || data.watchlist_id),
            el('span', {}, '📅'),
            el('span', {}, data.end_date),
        ),
        el('div', { className: 'flex items-center gap-2 text-gray-400 text-sm mb-5' }),
        el('h1', { className: 'text-4xl font-bold text-gray-200 mb-5' }, data.report_title),
    ));

    // Introduction section
    if (data.introduction) {
        fragment.append(el('div', { className: 'bg-slate-800/50 rounded-2xl p-6 mb-8 border border-slate-700' },
            el('h2', { className: 'text-3xl font-bold text-slate-100 mb-4 flex items-center gap-3' }, el('span', {}, 'Highlights')),
            el('div', { className: 'leading-relaxed text-slate-300' }, formatIntroduction(data.introduction)),
        ));
    }

    // Entity reports as cards
    if (Array.isArray(data.entity_reports) && data.entity_reports.length > 0) {
        fragment.append(el('div', { className: 'grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8' },
            data.entity_reports.map(entity => renderEntityCard(entity, data)),
        ));
    } else {
        fragment.append(el('p', { className: 'text-slate-400 italic' }, 'No entity reports available.'));
    }

    // Add custom styles for collapsed state
    const style = document.createElement('style');
    style.textContent = '.extra.hidden { display: none !important; }';
    fragment.append(style);

    return fragment;
};
