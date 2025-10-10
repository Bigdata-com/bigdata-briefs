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
    if (!data || typeof data !== 'object') return '<span class="error">No data to display.</span>';

    let html = '';

    // Header section with watchlist badge and date range
    html += '<div class="mb-8">';
    html += `<div class="mb-4">
        <span class="inline-block bg-gradient-to-br from-blue-500 to-blue-700 text-white px-5 py-2 rounded-full text-2xl font-semibold mr-4">
            ${escapeHtml(data.watchlist_name || data.watchlist_id)}
        </span>
        <span>📅</span>
        <span>${escapeHtml(data.end_date)}</span>
    </div>`;

    html += `<div class="flex items-center gap-2 text-gray-400 text-sm mb-5">
        
        
    </div>`;

    // Title
    html += `<h1 class="text-4xl font-bold text-gray-200 mb-5">${escapeHtml(data.report_title)}</h1>`;
    html += '</div>';

    // Introduction section
    if (data.introduction) {
        html += `<div class="bg-slate-800/50 rounded-2xl p-6 mb-8 border border-slate-700">
            <h2 class="text-3xl font-bold text-slate-100 mb-4 flex items-center gap-3">
                <span>Highlights</span>
            </h2>
            <div class="leading-relaxed text-slate-300">
                ${formatIntroduction(data.introduction)}
            </div>
        </div>`;
    }

    // Entity reports as cards
    if (Array.isArray(data.entity_reports) && data.entity_reports.length > 0) {
        html += '<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">';

        data.entity_reports.forEach(entity => {
            const entityName = (entity.entity_info && (entity.entity_info.name || entity.entity_info.id))
                ? escapeHtml(entity.entity_info.name || entity.entity_info.id)
                : escapeHtml(entity.entity_id);

            // Extract entity metadata if available
            const ticker = entity.entity_info?.ticker || entity.entity_info?.symbol || '';
            const country = entity.entity_info?.country || entity.entity_info?.location || '';
            const industry = entity.entity_info?.industry || entity.entity_info?.sector || '';

            const highlights = Array.isArray(entity.content) ? entity.content : [];

            // Build card: Changed to a dark, blurred background with refined padding and borders.
            html += `<div class="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-8 shadow-2xl text-white">`;

            // Company header section
            html += '<div class="mb-5">';
            // Updated typography for the entity name.
            html += `<div class="text-3xl font-bold text-slate-100 mb-3">${entityName}</div>`;

            html += '<div class="flex flex-wrap items-center gap-4">';
            if (ticker) {
                // Polished ticker style.
                html += `<span class="inline-block bg-slate-700 text-blue-400 text-xs font-bold px-3 py-1 rounded-full">${escapeHtml(ticker)}</span>`;
            }
            if (country) {
                // Replaced emoji with a cleaner SVG icon.
                html += `<span class="text-sm text-slate-400 flex items-center gap-1.5">
                            ${escapeHtml(country)}
                        </span>`;
            }
            if (industry) {
                // Polished industry tag style.
                html += `<span class="bg-blue-500/20 text-blue-300 text-xs font-semibold px-3 py-1 rounded-full">${escapeHtml(industry)}</span>`;
            }
            html += '</div>';
            html += '</div>';

            // Divider for better separation.
            html += '<hr class="border-slate-700 my-6">';

            // Highlights section
            if (highlights.length > 0) {
                const hasMore = highlights.length > 2;
                html += `<div class="highlights space-y-4 ${hasMore ? 'collapsed' : ''}">`;

                highlights.forEach((bp, i) => {
                    const isExtra = i >= 2;
                    // Updated highlight box style to match the dark theme.
                    html += `<div class="relative bg-slate-900/50 p-5 rounded-lg border-l-4 border-blue-500 ${isExtra ? 'extra hidden' : ''}">`;
                    html += `<p class="text-slate-300 leading-relaxed">`; // Set base text color for highlights.

                    // Source indicator with a restyled tooltip for the dark theme.
                    if (Array.isArray(bp.sources) && bp.sources.length > 0) {
                        let tooltipContent = '';

                        // Define SVG icons for a cleaner look (Heroicons)
                        const iconSource = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-slate-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clip-rule="evenodd" /></svg>`;
                        const iconTitle = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-slate-400" viewBox="0 0 20 20" fill="currentColor"><path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" /><path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3z" clip-rule="evenodd" /></svg>`;
                        const iconUrl = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-slate-400" viewBox="0 0 20 20" fill="currentColor"><path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" /><path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" /></svg>`;

                        bp.sources.forEach((sourceId, sourceIndex) => {
                            // Use optional chaining and provide a default empty object for robustness
                            const sourceMetadata = data.source_metadata?.[sourceId] || {};

                            // Destructure properties with default values
                            const {
                                text = "No text available",
                                headline = 'No headline available',
                                source_name: sourceName = 'Unknown Source',
                                url
                            } = sourceMetadata;

                            // Use a container for each source to handle spacing, removing the need for <hr>
                            // This creates a more modern, card-based layout
                            tooltipContent += `
        <div class="p-3 rounded-lg bg-slate-800 border border-slate-700/50 
                    hover:bg-slate-700/50 hover:border-slate-600 
                    transition-all duration-200 ease-in-out
                    ${sourceIndex > 0 ? 'mt-3' : ''}">`;

                            if (sourceName !== 'Unknown Source') {
                                tooltipContent += `
            <div class="flex items-center text-base font-semibold text-sky-400 mb-2 pb-2 border-b border-slate-700">
                ${iconSource}
                <span>${escapeHtml(sourceName)}</span>
            </div>
            <div class="space-y-2 text-sm">
                <div class="flex items-start">
                    <div class="flex-shrink-0">${iconTitle}</div>
                    <span class="text-slate-300">${escapeHtml(text)}</span>
                </div>`;

                                if (url) {
                                    tooltipContent += `
                <div class="flex items-start">
                    <div class="flex-shrink-0">${iconUrl}</div>
                    <a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" 
                       class="text-blue-400 hover:text-blue-300 underline break-all">
                       ${escapeHtml(url)}
                    </a>
                </div>`;
                                }
                                tooltipContent += `</div>`; // Closes space-y-2
                            } else {
                                // A styled fallback for sources without metadata
                                tooltipContent += `
            <div class="text-slate-500 italic">
                Source reference: ${escapeHtml(sourceId)}
            </div>`;
                            }

                            tooltipContent += `</div>`; // Closes the main container div
                        });

                        html += `<div class="source-indicator absolute -top-2 -right-2 w-7 h-7 bg-blue-600 rounded-full flex items-center justify-center text-sm font-bold text-white shadow-md cursor-help group">
                            ${bp.sources.length}
                            <div class="source-tooltip absolute bottom-full right-0 bg-slate-800/95 backdrop-blur-md text-slate-300 p-3 rounded-lg w-[500px] text-xs leading-snug opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 z-50 shadow-xl mb-2 border border-slate-600">
                                ${tooltipContent}
                                <div class="absolute top-full right-4 w-0 h-0 border-x-[6px] border-x-transparent border-t-[6px] border-t-slate-800"></div>
                            </div>
                        </div>`;
                    }

                    html += renderBoldText(escapeHtml(bp.bullet_point));
                    html += '</p></div>';
                });

                // "Show More" button with updated styling.
                if (hasMore) {
                    html += `<button class="w-full bg-blue-600 hover:bg-blue-700 transition-all duration-300 text-white font-semibold py-3 px-6 rounded-lg shadow-lg shadow-blue-600/20 mt-4" onclick="toggleHighlights(this)">Show More</button>`;
                }

                html += '</div>';
            } else {
                html += '<p class="text-sm text-slate-400 italic">No highlights available.</p>';
            }

            html += '</div>'; // End of card
        });

        html += '</div>'; // End of grid
    } else {
        html += '<p class="text-slate-400 italic">No entity reports available.</p>';
    }
    // Add custom styles for collapsed state
    html += `<style>
        .extra.hidden {
            display: none !important;
        }
    </style>`;

    return html;
};