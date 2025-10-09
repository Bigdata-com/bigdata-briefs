function renderBriefReport(data) {
    if (!data || typeof data !== 'object') return '<span class="error">No data to display.</span>';
    let html = '<h2 class="text-3xl font-bold text-white mb-4">General Report</h2>';
    // Report overview
    html += '<div class="max-h-[500px] overflow-y-auto">'
    html += '<table class="table-auto text-sm">';
    html += '<tr><th class="sticky top-0 z-10 bg-zinc-900">Watchlist</th><th class="sticky top-0 z-10 bg-zinc-900">Title</th><th class="sticky top-0 z-10 bg-zinc-900">Introduction</th><th class="sticky top-0 z-10 bg-zinc-900">Start Date</th><th class="sticky top-0 z-10 bg-zinc-900">End Date</th><th class="sticky top-0 z-10 bg-zinc-900">Novelty</th></tr>';
    html += `<tr class="divide-y divide-white"><td>${escapeHtml(data.watchlist_name || data.watchlist_id)}</td><td>${escapeHtml(data.report_title)}</td><td>${escapeHtml(data.introduction)}</td><td>${escapeHtml(data.start_date)}</td><td>${escapeHtml(data.end_date)}</td><td>${data.novelty ? 'Yes' : 'No'}</td></tr>`;
    html += '</table>';

    // Entity reports table
    if (Array.isArray(data.entity_reports) && data.entity_reports.length > 0) {
        html += '<h2 class="text-3xl font-bold text-white mb-4">Entity Reports</h2>';
        html += '<div class="max-h-[500px] overflow-y-auto">'
        html += '<table class="table-auto text-sm">';
        html += '<tr class="divide-y divide-white"><th class="sticky top-0 z-10 bg-zinc-900">Entity</th><th class="sticky top-0 z-10 bg-zinc-900">Bullet Point</th><th class="sticky top-0 z-10 bg-zinc-900">Sources</th></tr>';
        data.entity_reports.forEach(entity => {
            const entityName = (entity.entity_info && (entity.entity_info.name || entity.entity_info.id)) ? escapeHtml(entity.entity_info.name || entity.entity_info.id) : escapeHtml(entity.entity_id);
            if (Array.isArray(entity.content) && entity.content.length > 0) {
                entity.content.forEach((bp, idx) => {
                    html += `<tr class="divide-y divide-white"><td>${idx === 0 ? entityName : ''}</td><td>${escapeHtml(bp.bullet_point)}</td><td>${Array.isArray(bp.sources) ? bp.sources.map(escapeHtml).join(', ') : ''}</td></tr>`;
                });
            } else {
                html += `<tr class="divide-y divide-white"><td>${entityName}</td><td colspan="2"><em>No bullet points</em></td></tr>`;
            }
        });
        html += '</table>';
    } else {
        html += '<p><em>No entity reports available.</em></p>';
    }
    return html;
};