// Company Browser - Handles browsing and searching through company reports

class CompanyBrowser {
    constructor() {
        this.companies = [];
        this.filteredCompanies = [];
        this.searchTerm = '';
        this.expandedCompany = null;
        this.sourceMetadata = {};
    }

    init(companyReports, sourceMetadata) {
        this.companies = companyReports || [];
        this.filteredCompanies = [...this.companies];
        this.sourceMetadata = sourceMetadata || {};
        this.render();
    }

    filter(searchTerm) {
        this.searchTerm = searchTerm.toLowerCase().trim();
        
        if (!this.searchTerm) {
            this.filteredCompanies = [...this.companies];
        } else {
            this.filteredCompanies = this.companies.filter(company => {
                const name = (company.entity_info?.name || '').toLowerCase();
                const ticker = (company.entity_info?.ticker || '').toLowerCase();
                const sector = (company.entity_info?.sector || '').toLowerCase();
                const entityId = (company.entity_id || '').toLowerCase();
                
                return name.includes(this.searchTerm) ||
                       ticker.includes(this.searchTerm) ||
                       sector.includes(this.searchTerm) ||
                       entityId.includes(this.searchTerm);
            });
        }
        
        this.render();
    }

    toggleCompany(entityId) {
        if (this.expandedCompany === entityId) {
            this.expandedCompany = null;
        } else {
            this.expandedCompany = entityId;
        }
        this.render();
    }

    render() {
        const container = document.querySelector('[data-tab-content="companies"] .tab-actual-content');
        if (!container) return;

        // Create search bar
        let searchHtml = `
            <div class="mb-6">
                <div class="relative">
                    <input type="text" id="companySearch" placeholder="Search by name, ticker, sector, or entity ID..."
                        class="w-full bg-zinc-900 border border-zinc-600 text-white text-sm rounded-lg px-4 py-3 pl-10 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        oninput="window.companyBrowser.filter(this.value)" />
                    <svg class="w-5 h-5 text-zinc-400 absolute left-3 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                </div>
                <div class="mt-2 text-sm text-zinc-400">
                    Showing ${this.filteredCompanies.length} of ${this.companies.length} companies
                </div>
            </div>
        `;

        // Create company list
        if (this.filteredCompanies.length === 0) {
            searchHtml += `
                <div class="text-center py-12">
                    <p class="text-zinc-400 text-lg">No companies found matching "${this.searchTerm}"</p>
                </div>
            `;
        } else {
            searchHtml += '<div class="space-y-3">';
            
            this.filteredCompanies.forEach(company => {
                const entityId = company.entity_id;
                const entityInfo = company.entity_info || {};
                const name = entityInfo.name || 'Unknown Company';
                const ticker = entityInfo.ticker || 'N/A';
                const sector = entityInfo.sector || 'N/A';
                const bulletCount = (company.content || []).length;
                const isExpanded = this.expandedCompany === entityId;
                
                searchHtml += `
                    <div class="bg-zinc-800/50 border border-zinc-700 rounded-lg overflow-hidden">
                        <button onclick="window.companyBrowser.toggleCompany('${entityId}')"
                            class="w-full flex items-center justify-between p-4 hover:bg-zinc-700/50 transition-colors text-left">
                            <div class="flex-1">
                                <div class="flex items-center gap-3 mb-2">
                                    <h3 class="text-lg font-bold text-white">${this.escapeHtml(name)}</h3>
                                    ${ticker !== 'N/A' ? `<span class="text-sm text-zinc-400 bg-zinc-700 px-2 py-1 rounded">${this.escapeHtml(ticker)}</span>` : ''}
                                    ${sector !== 'N/A' ? `<span class="text-sm text-zinc-400 bg-zinc-700 px-2 py-1 rounded">${this.escapeHtml(sector)}</span>` : ''}
                                </div>
                                <div class="flex items-center gap-4 text-xs text-zinc-400">
                                    <span>${bulletCount} bullet point${bulletCount !== 1 ? 's' : ''}</span>
                                </div>
                            </div>
                            <svg class="w-5 h-5 text-zinc-400 transform transition-transform ${isExpanded ? 'rotate-180' : ''}" 
                                fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                            </svg>
                        </button>
                        
                        ${isExpanded ? this.renderCompanyDetails(company) : ''}
                    </div>
                `;
            });
            
            searchHtml += '</div>';
        }

        container.innerHTML = searchHtml;
    }

    renderCompanyDetails(company) {
        const entityInfo = company.entity_info || {};
        const keptBullets = company.kept || [];
        const discardedBullets = company.discarded || [];
        const comparedWith = company.compared_with || [];
        
        let html = `
            <div class="border-t border-zinc-700 p-4 bg-zinc-900/30">
        `;
        
        // Add collapsible "Additional company details" section with ALL fields
        html += this.renderAdditionalCompanyDetails(company.entity_id, entityInfo);
        
        // Add hierarchical Report Bullet Points section
        html += this.renderReportBulletPointsSection(company.entity_id, keptBullets, discardedBullets, comparedWith);
        
        html += `
            </div>
        `;
        
        return html;
    }
    
    renderAdditionalCompanyDetails(entityId, entityInfo) {
        const sectionId = `additional-details-${entityId.replace(/[^a-zA-Z0-9]/g, '')}`;
        
        // Filter fields that exist (all fields except 'name')
        const fieldsToShow = Object.entries(entityInfo).filter(([key, value]) => 
            key !== 'name' && value !== null && value !== undefined && value !== ''
        );
        
        if (fieldsToShow.length === 0) {
            return ''; // Don't show the section if there are no fields
        }
        
        let html = `
            <div class="mb-4">
                <button onclick="window.companyBrowser.toggleSection('${sectionId}')"
                    class="flex items-center gap-2 text-sm text-zinc-400 hover:text-zinc-300 transition-colors">
                    <svg id="${sectionId}-icon" class="w-4 h-4 transform transition-transform" 
                        fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                    <span>Additional company details</span>
                </button>
                <div id="${sectionId}" class="hidden mt-2 space-y-2 text-sm">
        `;
        
        // Display all fields in a single column
        for (const [key, value] of fieldsToShow) {
            // Format the key label
            let keyLabel = this.formatKey(key);
            if (key === 'id') {
                keyLabel = 'Entity ID';
            }
            
            // Format the value - add spaces after commas
            let formattedValue = String(value);
            if (formattedValue.includes(',')) {
                formattedValue = formattedValue.replace(/,/g, ', ');
            }
            
            html += `
                <div>
                    <span class="text-zinc-400">${keyLabel}:</span>
                    <span class="text-white ml-2">${this.escapeHtml(formattedValue)}</span>
                </div>
            `;
        }
        
        html += `
                </div>
            </div>
        `;
        
        return html;
    }
    
    renderReportBulletPointsSection(entityId, keptBullets, discardedBullets, comparedWith) {
        const mainSectionId = `report-bullets-${entityId.replace(/[^a-zA-Z0-9]/g, '')}`;
        const totalCount = keptBullets.length + discardedBullets.length + comparedWith.length;
        
        if (totalCount === 0) {
            return '<p class="text-zinc-400 text-sm italic mt-4">No bullet points available for this company.</p>';
        }
        
        let html = `
            <div class="mt-4">
                <button onclick="window.companyBrowser.toggleSection('${mainSectionId}')"
                    class="w-full flex items-center justify-between p-4 bg-zinc-800/50 hover:bg-zinc-700/50 rounded-lg border border-zinc-700 transition-colors">
                    <h4 class="text-base font-semibold text-blue-400">Report Bullet Points</h4>
                    <svg id="${mainSectionId}-icon" class="w-5 h-5 text-zinc-400 transform transition-transform" 
                        fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                </button>
                <div id="${mainSectionId}" class="hidden mt-2 ml-4 space-y-3">
        `;
        
        // Add Kept section (nested)
        if (keptBullets.length > 0) {
            html += this.renderCollapsibleSection(
                'kept',
                entityId,
                'Kept (After Novelty Filtering)',
                keptBullets,
                'green'
            );
        }
        
        // Add Discarded section (nested)
        if (discardedBullets.length > 0) {
            html += this.renderCollapsibleSection(
                'discarded',
                entityId,
                'Discarded (By Novelty Filtering)',
                discardedBullets,
                'red'
            );
        }
        
        // Add Compared With section (nested)
        if (comparedWith.length > 0) {
            html += this.renderComparedWithSection(entityId, comparedWith);
        }
        
        html += `
                </div>
            </div>
        `;
        
        return html;
    }
    
    renderBulletPoint(bullet, index) {
        const bulletText = bullet.bullet_point || '';
        const sources = bullet.sources || [];
        
        return `
            <div class="bg-zinc-800/50 rounded-lg p-4 border border-zinc-700">
                <div class="flex items-start gap-3">
                    <span class="text-blue-400 font-bold flex-shrink-0">${index + 1}.</span>
                    <div class="flex-1">
                        <p class="text-zinc-200 text-sm leading-relaxed">${this.escapeHtml(bulletText)}</p>
                        ${sources.length > 0 ? `
                            <div class="mt-3 pt-3 border-t border-zinc-700">
                                <p class="text-xs font-semibold text-zinc-400 mb-2">Sources:</p>
                                <div class="space-y-3">
                                    ${sources.map(sourceId => this.renderSourceDetails(sourceId)).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    renderSourceDetails(sourceId) {
        const sourceData = this.sourceMetadata[sourceId];
        const uniqueId = `source-${sourceId.replace(/[^a-zA-Z0-9]/g, '-')}`;
        
        // Se non abbiamo metadati, mostriamo solo l'ID
        if (!sourceData) {
            return `
                <div class="pl-3 border-l-2 border-zinc-600">
                    <div class="text-xs text-zinc-400">• Source ID: <span class="font-mono text-zinc-300">${this.escapeHtml(sourceId)}</span></div>
                    <div class="text-xs text-zinc-500 italic mt-1">No metadata available</div>
                </div>
            `;
        }
        
        const chunkText = sourceData.text || 'No text available';
        
        return `
            <div class="pl-3 border-l-2 border-blue-600/50">
                <div class="text-xs text-zinc-400 mb-1">• Source ID: <span class="font-mono text-zinc-300">${this.escapeHtml(sourceId)}</span></div>
                <div class="text-xs text-zinc-300 leading-relaxed mb-2 bg-zinc-900/50 p-2 rounded">
                    ${this.escapeHtml(chunkText)}
                </div>
                <button onclick="window.companyBrowser.toggleSourceDetails('${uniqueId}')" 
                    class="text-xs text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-1">
                    <svg id="${uniqueId}-icon" class="w-3 h-3 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                    Additional chunk details
                </button>
                <div id="${uniqueId}" class="hidden mt-2 text-xs text-zinc-400 bg-zinc-900/70 p-3 rounded space-y-1">
                    ${this.renderSourceMetadata(sourceData)}
                </div>
            </div>
        `;
    }
    
    renderSourceMetadata(sourceData) {
        const metadata = [];
        
        if (sourceData.headline) {
            metadata.push(`<div><span class="text-zinc-500">Headline:</span> <span class="text-zinc-300">${this.escapeHtml(sourceData.headline)}</span></div>`);
        }
        
        if (sourceData.ts) {
            const date = new Date(sourceData.ts);
            const formattedDate = date.toLocaleString();
            metadata.push(`<div><span class="text-zinc-500">Date:</span> <span class="text-zinc-300">${formattedDate}</span></div>`);
        }
        
        if (sourceData.source_name) {
            metadata.push(`<div><span class="text-zinc-500">Source:</span> <span class="text-zinc-300">${this.escapeHtml(sourceData.source_name)}</span></div>`);
        }
        
        if (sourceData.source_key) {
            metadata.push(`<div><span class="text-zinc-500">Source Key:</span> <span class="font-mono text-zinc-300">${this.escapeHtml(sourceData.source_key)}</span></div>`);
        }
        
        if (sourceData.url) {
            metadata.push(`<div><span class="text-zinc-500">URL:</span> <a href="${this.escapeHtml(sourceData.url)}" target="_blank" class="text-blue-400 hover:text-blue-300 break-all">${this.escapeHtml(sourceData.url)}</a></div>`);
        }
        
        if (sourceData.source_rank !== null && sourceData.source_rank !== undefined) {
            metadata.push(`<div><span class="text-zinc-500">Source Rank:</span> <span class="text-zinc-300">${sourceData.source_rank}</span></div>`);
        }
        
        if (sourceData.document_scope && sourceData.document_scope !== 'Unknown') {
            metadata.push(`<div><span class="text-zinc-500">Document Type:</span> <span class="text-zinc-300">${this.escapeHtml(sourceData.document_scope)}</span></div>`);
        }
        
        if (sourceData.language && sourceData.language !== 'Unknown') {
            metadata.push(`<div><span class="text-zinc-500">Language:</span> <span class="text-zinc-300">${this.escapeHtml(sourceData.language)}</span></div>`);
        }
        
        if (sourceData.document_id) {
            metadata.push(`<div><span class="text-zinc-500">Document ID:</span> <span class="font-mono text-zinc-300 text-[10px]">${this.escapeHtml(sourceData.document_id)}</span></div>`);
        }
        
        if (sourceData.chunk_id !== null && sourceData.chunk_id !== undefined) {
            metadata.push(`<div><span class="text-zinc-500">Chunk ID:</span> <span class="text-zinc-300">${sourceData.chunk_id}</span></div>`);
        }
        
        return metadata.length > 0 ? metadata.join('') : '<div class="text-zinc-500 italic">No additional metadata available</div>';
    }
    
    toggleSourceDetails(detailsId) {
        const details = document.getElementById(detailsId);
        const icon = document.getElementById(`${detailsId}-icon`);
        
        if (details && icon) {
            details.classList.toggle('hidden');
            icon.classList.toggle('rotate-180');
        }
    }
    
    renderDiscardedBulletPoint(bullet, index) {
        const bulletText = bullet.bullet_point || '';
        const sources = bullet.sources || [];
        const similarity = bullet.comparison_similarity;
        const comparisonSentence = bullet.comparison_sentence;
        
        return `
            <div class="bg-zinc-800/50 rounded-lg p-4 border border-zinc-700">
                <div class="flex items-start gap-3">
                    <span class="text-red-400 font-bold flex-shrink-0">${index + 1}.</span>
                    <div class="flex-1">
                        <p class="text-zinc-200 text-sm leading-relaxed">${this.escapeHtml(bulletText)}</p>
                        
                        ${sources.length > 0 ? `
                            <div class="mt-3 pt-3 border-t border-zinc-700">
                                <p class="text-xs font-semibold text-zinc-400 mb-2">Sources:</p>
                                <div class="space-y-3">
                                    ${sources.map(sourceId => this.renderSourceDetails(sourceId)).join('')}
                                </div>
                            </div>
                        ` : ''}
                        
                        ${similarity !== null || comparisonSentence ? `
                            <div class="mt-3 pt-3 border-t border-orange-700/30">
                                <p class="text-xs font-semibold text-orange-400 mb-2">Comparison details:</p>
                                <div class="pl-3 space-y-2">
                                    ${comparisonSentence ? `
                                        <div class="text-xs">
                                            <span class="text-zinc-500">Sentence:</span>
                                            <div class="text-zinc-300 mt-1 bg-zinc-900/50 p-2 rounded leading-relaxed">
                                                ${this.escapeHtml(comparisonSentence)}
                                            </div>
                                        </div>
                                    ` : ''}
                                    ${similarity !== null && similarity !== undefined ? `
                                        <div class="text-xs">
                                            <span class="text-zinc-500">Similarity:</span>
                                            <span class="text-orange-300 font-semibold ml-2">${(similarity * 100).toFixed(2)}%</span>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    renderComparedWithBulletPoint(bullet, index) {
        const bulletText = bullet.bullet_point || '';
        const creationDate = bullet.creation_date;
        
        return `
            <div class="bg-zinc-800/50 rounded-lg p-4 border border-zinc-700">
                <div class="flex items-start gap-3">
                    <span class="text-zinc-400 font-bold flex-shrink-0">${index + 1}.</span>
                    <div class="flex-1">
                        <p class="text-zinc-200 text-sm leading-relaxed">${this.escapeHtml(bulletText)}</p>
                        ${creationDate ? `
                            <div class="mt-2 text-xs text-zinc-500">
                                <span>From brief dated:</span>
                                <span class="text-zinc-400 ml-1">${creationDate}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    renderCollapsibleSection(sectionType, entityId, title, bullets, colorTheme) {
        const sectionId = `${sectionType}-${entityId.replace(/[^a-zA-Z0-9]/g, '')}`;
        const colorClasses = {
            'green': 'text-green-400 border-green-700',
            'red': 'text-red-400 border-red-700',
            'blue': 'text-blue-400 border-blue-700'
        };
        const colorClass = colorClasses[colorTheme] || colorClasses['blue'];
        
        return `
            <div class="mt-4">
                <button onclick="window.companyBrowser.toggleSection('${sectionId}')"
                    class="w-full flex items-center justify-between p-3 bg-zinc-800/50 hover:bg-zinc-700/50 rounded-lg border border-zinc-700 transition-colors">
                    <h4 class="text-sm font-semibold ${colorClass}">${title} (${bullets.length})</h4>
                    <svg id="${sectionId}-icon" class="w-5 h-5 text-zinc-400 transform transition-transform" 
                        fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                </button>
                <div id="${sectionId}" class="hidden mt-2 ml-4 space-y-3 pl-3 border-l-2 border-zinc-700">
                    ${bullets.map((bullet, index) => {
                        if (sectionType === 'discarded') {
                            return this.renderDiscardedBulletPoint(bullet, index);
                        } else if (sectionType === 'compared') {
                            return this.renderComparedWithBulletPoint(bullet, index);
                        } else {
                            return this.renderBulletPoint(bullet, index);
                        }
                    }).join('')}
                </div>
            </div>
        `;
    }
    
    renderComparedWithSection(entityId, bullets) {
        const sectionId = `compared-${entityId.replace(/[^a-zA-Z0-9]/g, '')}`;
        
        return `
            <div class="mt-4">
                <button onclick="window.companyBrowser.toggleSection('${sectionId}')"
                    class="w-full flex items-center justify-between p-3 bg-zinc-800/50 hover:bg-zinc-700/50 rounded-lg border border-zinc-700 transition-colors">
                    <h4 class="text-sm font-semibold text-zinc-300">Compared With (${bullets.length})</h4>
                    <svg id="${sectionId}-icon" class="w-5 h-5 text-zinc-400 transform transition-transform" 
                        fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                </button>
                <div id="${sectionId}" class="hidden mt-2 ml-4 space-y-3 pl-3 border-l-2 border-zinc-700">
                    ${bullets.map((bullet, index) => this.renderComparedWithBulletPoint(bullet, index)).join('')}
                </div>
            </div>
        `;
    }
    
    toggleSection(sectionId) {
        const section = document.getElementById(sectionId);
        const icon = document.getElementById(`${sectionId}-icon`);
        
        if (section && icon) {
            section.classList.toggle('hidden');
            icon.classList.toggle('rotate-180');
        }
    }

    formatKey(key) {
        // Convert snake_case or camelCase to Title Case
        return key
            .replace(/_/g, ' ')
            .replace(/([A-Z])/g, ' $1')
            .replace(/^./, str => str.toUpperCase())
            .trim();
    }

    escapeHtml(text) {
        if (text === null || text === undefined) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize company browser
window.companyBrowser = new CompanyBrowser();

