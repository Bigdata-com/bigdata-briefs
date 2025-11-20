// Audit Table - Shows evidence breakdown for bullet points across entities

class AuditTable {
    constructor() {
        this.entityReports = [];
        this.sourceMetadata = {};
        this.selectedEntityId = null;
    }

    init(entityReports, sourceMetadata) {
        console.log('[AuditTable] init called with:', {
            entityReports: entityReports,
            entityReportsLength: entityReports?.length,
            sourceMetadata: sourceMetadata,
            sourceMetadataKeys: sourceMetadata ? Object.keys(sourceMetadata).length : 0
        });
        
        // Check for missing metadata (excluding compared_with as those are from previous briefs)
        if (entityReports && sourceMetadata) {
            const allSourceIds = new Set();
            const metadataKeys = new Set(Object.keys(sourceMetadata));
            
            entityReports.forEach(report => {
                ['kept', 'discarded'].forEach(type => {  // Exclude compared_with
                    (report[type] || []).forEach(bullet => {
                        (bullet.sources || []).forEach(sourceId => {
                            allSourceIds.add(sourceId);
                        });
                    });
                });
            });
            
            const missingMetadata = Array.from(allSourceIds).filter(id => !metadataKeys.has(id));
            
            if (missingMetadata.length > 0) {
                console.warn('[AuditTable] Missing metadata for', missingMetadata.length, 'source IDs (excluding compared_with):', missingMetadata.slice(0, 5));
                console.log('[AuditTable] Total sources referenced (kept + discarded):', allSourceIds.size);
                console.log('[AuditTable] Metadata available for:', metadataKeys.size);
            }
        }
        
        this.entityReports = entityReports || [];
        this.sourceMetadata = sourceMetadata || {};
        
        // Select first entity by default
        if (this.entityReports.length > 0) {
            this.selectedEntityId = this.entityReports[0].entity_id;
            console.log('[AuditTable] Selected entity:', this.selectedEntityId);
        } else {
            console.warn('[AuditTable] No entity reports found');
        }
        
        // Try to render immediately, but if container not found, will try again when tab is clicked
        this.render();
        
        // Also listen for tab changes to re-render if needed
        document.addEventListener('tabChanged', (event) => {
            if (event.detail.tab === 'audit') {
                console.log('[AuditTable] Audit tab activated, re-rendering...');
                this.render();
            }
        });
    }

    render() {
        const container = document.querySelector('[data-tab-content="audit"] .tab-actual-content');
        console.log('[AuditTable] render() - container found:', !!container);
        
        if (!container) {
            console.error('[AuditTable] Container not found: [data-tab-content="audit"] .tab-actual-content');
            return;
        }

        console.log('[AuditTable] render() - entityReports.length:', this.entityReports.length);
        
        if (this.entityReports.length === 0) {
            console.warn('[AuditTable] No entity reports to display');
            container.innerHTML = `
                <div class="text-center py-20">
                    <p class="text-text3 text-lg">No audit data available</p>
                </div>
            `;
            return;
        }

        // Calculate missing metadata stats
        const stats = this.calculateMetadataStats();
        
        let html = `
            <div class="mb-6">
                <h2 class="text-2xl font-bold text-text mb-4">Audit Trail</h2>
                <p class="text-text3 text-sm mb-4">Detailed evidence breakdown for each bullet point and its sources</p>
                
                ${stats.missingCount > 0 ? `
                    <div class="mb-4 bg-orange-900/20 border border-orange-700/50 rounded-lg p-4">
                        <div class="flex items-start gap-3">
                            <svg class="w-5 h-5 text-orange-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                            </svg>
                            <div class="flex-1">
                                <p class="text-sm font-medium text-orange-300">Missing Metadata Warning</p>
                                <p class="text-xs text-orange-400/80 mt-1">
                                    ${stats.missingCount} out of ${stats.totalSources} source references (${Math.round(stats.missingPercentage)}%) in kept and discarded bullet points are missing metadata. 
                                    This typically happens when sources are used during processing but not marked as referenced in the final report serialization.
                                    Sources with missing metadata are highlighted with <span class="text-orange-400">⚠️</span> icon.
                                    <em>(Note: Compared With sources are excluded from this count as they're from previous briefs)</em>
                                </p>
                            </div>
                        </div>
                    </div>
                ` : ''}
                
                <!-- Entity Selector -->
                ${this.renderEntitySelector()}
            </div>
            
            <!-- Audit Tables -->
            <div id="auditTablesContainer">
                ${this.renderAuditTables()}
            </div>
        `;

        container.innerHTML = html;
    }

    calculateMetadataStats() {
        const allSourceIds = new Set();
        const metadataKeys = new Set(Object.keys(this.sourceMetadata));
        
        // Only count kept and discarded, exclude compared_with (those are from previous briefs)
        this.entityReports.forEach(report => {
            ['kept', 'discarded'].forEach(type => {
                (report[type] || []).forEach(bullet => {
                    (bullet.sources || []).forEach(sourceId => {
                        allSourceIds.add(sourceId);
                    });
                });
            });
        });
        
        const totalSources = allSourceIds.size;
        const missingCount = Array.from(allSourceIds).filter(id => !metadataKeys.has(id)).length;
        const missingPercentage = totalSources > 0 ? (missingCount / totalSources) * 100 : 0;
        
        return {
            totalSources,
            missingCount,
            missingPercentage,
            availableCount: totalSources - missingCount
        };
    }

    renderEntitySelector() {
        const entities = this.entityReports.map(report => ({
            id: report.entity_id,
            name: report.entity_info?.name || 'Unknown Entity',
            ticker: report.entity_info?.ticker || null
        }));

        return `
            <div class="bg-surface border border-border rounded-lg p-4">
                <label for="auditEntitySelect" class="block text-sm font-medium text-text mb-2">
                    Select Entity
                </label>
                <select id="auditEntitySelect" 
                    onchange="window.auditTable.selectEntity(this.value)"
                    class="w-full md:w-96 bg-surface2 border border-border text-text text-sm rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none cursor-pointer">
                    ${entities.map(entity => `
                        <option value="${this.escapeHtml(entity.id)}" ${entity.id === this.selectedEntityId ? 'selected' : ''}>
                            ${this.escapeHtml(entity.name)}${entity.ticker ? ` (${this.escapeHtml(entity.ticker)})` : ''}
                        </option>
                    `).join('')}
                </select>
            </div>
        `;
    }

    selectEntity(entityId) {
        this.selectedEntityId = entityId;
        
        // Re-render only the tables container
        const container = document.getElementById('auditTablesContainer');
        if (container) {
            container.innerHTML = this.renderAuditTables();
        }
    }

    renderAuditTables() {
        const selectedReport = this.entityReports.find(r => r.entity_id === this.selectedEntityId);
        
        console.log('[AuditTable] renderAuditTables for entity:', this.selectedEntityId, selectedReport);
        
        if (!selectedReport) {
            console.error('[AuditTable] Entity not found:', this.selectedEntityId);
            return '<p class="text-text3">Entity not found</p>';
        }

        const entityName = selectedReport.entity_info?.name || 'Unknown Entity';
        const keptBullets = selectedReport.kept || [];
        const discardedBullets = selectedReport.discarded || [];
        const comparedWithBullets = selectedReport.compared_with || [];
        
        console.log('[AuditTable] Bullet counts:', {
            kept: keptBullets.length,
            discarded: discardedBullets.length,
            compared: comparedWithBullets.length
        });

        let html = '';

        // Kept Bullet Points Table
        if (keptBullets.length > 0) {
            html += this.renderTable(
                'Kept Bullet Points (After Novelty Filtering)',
                keptBullets,
                entityName,
                'kept',
                'border-green-700'
            );
        }

        // Discarded Bullet Points Table
        if (discardedBullets.length > 0) {
            html += this.renderTable(
                'Discarded Bullet Points (By Novelty Filtering)',
                discardedBullets,
                entityName,
                'discarded',
                'border-red-700'
            );
        }

        // Compared With Table
        if (comparedWithBullets.length > 0) {
            html += this.renderTable(
                'Compared With (From Previous Briefs)',
                comparedWithBullets,
                entityName,
                'compared',
                'border-border'
            );
        }

        if (keptBullets.length === 0 && discardedBullets.length === 0 && comparedWithBullets.length === 0) {
            html = '<p class="text-text3 italic">No bullet points available for this entity.</p>';
        }

        return html;
    }

    renderTable(title, bulletPoints, entityName, tableType, borderColor) {
        const totalSources = bulletPoints.reduce((sum, bp) => sum + (bp.sources?.length || 0), 0);
        
        return `
            <div class="mb-8 bg-surface border ${borderColor} rounded-lg overflow-hidden">
                <div class="bg-surface2 px-6 py-4 border-b ${borderColor}">
                    <h3 class="text-xl font-bold text-text">${title}</h3>
                    <p class="text-text3 text-sm mt-1">
                        ${bulletPoints.length} bullet point${bulletPoints.length !== 1 ? 's' : ''}, 
                        ${totalSources} source${totalSources !== 1 ? 's' : ''}
                    </p>
                </div>
                
                <div class="overflow-x-auto">
                    <table class="w-full border-collapse">
                        <thead class="bg-surface2 sticky top-0 z-10">
                            <tr>
                                <th class="px-4 py-3 text-left text-sm font-semibold text-text border-b border-border">Entity</th>
                                <th class="px-4 py-3 text-left text-sm font-semibold text-text border-b border-border">Generated Bullet Point</th>
                                <th class="px-4 py-3 text-left text-sm font-semibold text-text border-b border-border">Source ID</th>
                                <th class="px-4 py-3 text-left text-sm font-semibold text-text border-b border-border">Source Text</th>
                                <th class="px-4 py-3 text-left text-sm font-semibold text-text border-b border-border">Source Headline</th>
                                <th class="px-4 py-3 text-left text-sm font-semibold text-text border-b border-border">Additional Details</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-border">
                            ${this.renderTableRows(bulletPoints, entityName, tableType)}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    renderTableRows(bulletPoints, entityName, tableType) {
        let html = '';
        let globalRowIndex = 0;

        bulletPoints.forEach((bullet, bulletIndex) => {
            const bulletText = bullet.bullet_point || '';
            const sources = bullet.sources || [];
            
            // Additional fields for discarded bullets
            const comparisonSimilarity = bullet.comparison_similarity;
            const comparisonSentence = bullet.comparison_sentence;
            
            // Additional field for compared_with bullets
            const creationDate = bullet.creation_date;

            if (sources.length === 0) {
                // Bullet point without sources (shouldn't happen but handle gracefully)
                const bgClass = globalRowIndex % 2 === 0 ? 'bg-surface' : 'bg-surface2';
                html += `
                    <tr class="${bgClass} hover:bg-surface2 transition-colors">
                        <td class="px-4 py-3 text-sm font-medium text-text2">${this.escapeHtml(entityName)}</td>
                        <td class="px-4 py-3 text-sm text-text2">${this.escapeHtml(bulletText)}</td>
                        <td colspan="4" class="px-4 py-3 text-sm text-text3 italic">No sources available</td>
                    </tr>
                `;
                globalRowIndex++;
            } else {
                // Render one row per source
                sources.forEach((sourceId, sourceIndex) => {
                    const isFirstSource = sourceIndex === 0;
                    const bgClass = globalRowIndex % 2 === 0 ? 'bg-surface' : 'bg-surface2';
                    const sourceData = this.sourceMetadata[sourceId];
                    
                    html += `
                        <tr class="${bgClass} hover:bg-surface2 transition-colors">
                    `;

                    // Entity column (only in first row with rowspan)
                    if (isFirstSource) {
                        html += `
                            <td rowspan="${sources.length}" class="px-4 py-3 text-sm font-medium text-text2 align-top border-r border-border">
                                ${this.escapeHtml(entityName)}
                            </td>
                        `;
                    }

                    // Bullet Point column (only in first row with rowspan)
                    if (isFirstSource) {
                        let bulletContent = this.escapeHtml(bulletText);
                        
                        // Add comparison info for discarded bullets
                        if (tableType === 'discarded' && (comparisonSimilarity !== null || comparisonSentence)) {
                            bulletContent += `
                                <div class="mt-2 pt-2 border-t border-orange-700/30 text-xs">
                                    <span class="font-semibold text-orange-400">Comparison:</span>
                                    ${comparisonSentence ? `<div class="text-text3 mt-1 italic">"${this.escapeHtml(comparisonSentence)}"</div>` : ''}
                                    ${comparisonSimilarity !== null ? `<div class="text-orange-300 mt-1">Similarity: ${(comparisonSimilarity * 100).toFixed(2)}%</div>` : ''}
                                </div>
                            `;
                        }
                        
                        // Add creation date for compared_with bullets
                        if (tableType === 'compared' && creationDate) {
                            bulletContent += `
                                <div class="mt-2 pt-2 border-t border-border text-xs text-text3">
                                    <span class="font-semibold">From brief dated:</span> ${this.escapeHtml(creationDate)}
                                </div>
                            `;
                        }
                        
                        html += `
                            <td rowspan="${sources.length}" class="px-4 py-3 text-sm text-text2 align-top border-r border-border">
                                ${bulletContent}
                            </td>
                        `;
                    }

                    // Source ID column (with warning if no metadata)
                    html += `
                        <td class="px-4 py-3 text-xs font-mono ${sourceData ? 'text-text3' : 'text-orange-400'}">
                            ${this.escapeHtml(sourceId)}
                            ${!sourceData ? '<span class="ml-1" title="Metadata not available">⚠️</span>' : ''}
                        </td>
                    `;

                    // Source Text column
                    const sourceText = sourceData?.text || '';
                    html += `
                        <td class="px-4 py-3 text-sm ${sourceData ? 'text-text2' : 'text-text3 italic'} max-w-md">
                            ${sourceData ? `<div class="line-clamp-3">${this.escapeHtml(sourceText)}</div>` : 'Metadata not available'}
                        </td>
                    `;

                    // Source Headline column
                    const sourceHeadline = sourceData?.headline || '';
                    html += `
                        <td class="px-4 py-3 text-sm ${sourceData ? 'text-text2' : 'text-text3 italic'} max-w-xs">
                            ${sourceData ? this.escapeHtml(sourceHeadline) : 'Metadata not available'}
                        </td>
                    `;

                    // Additional Details column (collapsible)
                    const detailsId = `details-${this.sanitizeId(sourceId)}-${bulletIndex}-${sourceIndex}`;
                    html += `
                        <td class="px-4 py-3 text-sm">
                            ${this.renderAdditionalDetails(sourceData, detailsId)}
                        </td>
                    `;

                    html += `
                        </tr>
                    `;

                    globalRowIndex++;
                });
            }
        });

        return html || '<tr><td colspan="6" class="px-4 py-3 text-sm text-text3 italic text-center">No data available</td></tr>';
    }

    renderAdditionalDetails(sourceData, detailsId) {
        if (!sourceData) {
            return `
                <div class="text-xs text-orange-400 flex items-center gap-1">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                    </svg>
                    <span>Metadata not found</span>
                </div>
                <div class="text-[10px] text-text3 mt-1">
                    This source was referenced but metadata was not serialized by the backend
                </div>
            `;
        }

        const hasDetails = sourceData.ts || sourceData.source_name || sourceData.source_key || 
                          sourceData.source_rank !== null || sourceData.document_id || sourceData.chunk_id !== null;

        if (!hasDetails) {
            return '<span class="text-text3 text-xs italic">No additional details</span>';
        }

        return `
            <button onclick="window.auditTable.toggleDetails('${detailsId}')" 
                class="flex items-center gap-1 text-blue-400 hover:text-blue-300 transition-colors text-xs">
                <svg id="${detailsId}-icon" class="w-3 h-3 transform transition-transform" 
                    fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
                Show Details
            </button>
            <div id="${detailsId}" class="hidden mt-2 space-y-1 text-xs bg-surface2 p-3 rounded border border-border">
                ${sourceData.ts ? `<div><span class="text-text3">Date:</span> <span class="text-text2">${this.formatDate(sourceData.ts)}</span></div>` : ''}
                ${sourceData.source_name ? `<div><span class="text-text3">Source:</span> <span class="text-text2">${this.escapeHtml(sourceData.source_name)}</span></div>` : ''}
                ${sourceData.source_key ? `<div><span class="text-text3">Source Key:</span> <span class="font-mono text-text2">${this.escapeHtml(sourceData.source_key)}</span></div>` : ''}
                ${sourceData.source_rank !== null && sourceData.source_rank !== undefined ? `<div><span class="text-text3">Source Rank:</span> <span class="text-text2">${sourceData.source_rank}</span></div>` : ''}
                ${sourceData.document_id ? `<div><span class="text-text3">Document ID:</span> <span class="font-mono text-text2 text-[10px] break-all">${this.escapeHtml(sourceData.document_id)}</span></div>` : ''}
                ${sourceData.chunk_id !== null && sourceData.chunk_id !== undefined ? `<div><span class="text-text3">Chunk ID:</span> <span class="text-text2">${sourceData.chunk_id}</span></div>` : ''}
            </div>
        `;
    }

    toggleDetails(detailsId) {
        const details = document.getElementById(detailsId);
        const icon = document.getElementById(`${detailsId}-icon`);
        const button = icon?.closest('button');
        
        if (details && icon) {
            const isHidden = details.classList.contains('hidden');
            details.classList.toggle('hidden');
            icon.classList.toggle('rotate-180');
            
            if (button) {
                button.innerHTML = isHidden 
                    ? `<svg id="${detailsId}-icon" class="w-3 h-3 transform rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg> Hide Details`
                    : `<svg id="${detailsId}-icon" class="w-3 h-3 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg> Show Details`;
            }
        }
    }

    formatDate(isoString) {
        try {
            const date = new Date(isoString);
            return date.toLocaleString();
        } catch (e) {
            return isoString;
        }
    }

    sanitizeId(str) {
        return str.replace(/[^a-zA-Z0-9]/g, '-');
    }

    escapeHtml(text) {
        if (text === null || text === undefined) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize audit table
window.auditTable = new AuditTable();

