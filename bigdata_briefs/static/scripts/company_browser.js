// Company Browser - Handles browsing and searching through company reports

class CompanyBrowser {
    constructor() {
        this.companies = [];
        this.filteredCompanies = [];
        this.searchTerm = '';
        this.expandedCompany = null;
    }

    init(companyReports) {
        this.companies = companyReports || [];
        this.filteredCompanies = [...this.companies];
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
                                    <span>Entity ID: ${this.escapeHtml(entityId)}</span>
                                    <span>•</span>
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
        const bulletPoints = company.content || [];
        
        let html = `
            <div class="border-t border-zinc-700 p-4 bg-zinc-900/30">
                <div class="mb-4">
                    <h4 class="text-sm font-semibold text-zinc-300 mb-2">Company Information</h4>
                    <div class="grid grid-cols-2 gap-2 text-sm">
        `;
        
        // Display all available entity info fields
        for (const [key, value] of Object.entries(entityInfo)) {
            if (value !== null && value !== undefined && value !== '') {
                html += `
                    <div>
                        <span class="text-zinc-400">${this.formatKey(key)}:</span>
                        <span class="text-white ml-2">${this.escapeHtml(String(value))}</span>
                    </div>
                `;
            }
        }
        
        html += `
                    </div>
                </div>
                
                <div>
                    <h4 class="text-sm font-semibold text-zinc-300 mb-3">Report Bullet Points</h4>
                    <div class="space-y-3">
        `;
        
        if (bulletPoints.length === 0) {
            html += '<p class="text-zinc-400 text-sm italic">No bullet points available for this company.</p>';
        } else {
            bulletPoints.forEach((bullet, index) => {
                const bulletText = bullet.bullet_point || '';
                const sources = bullet.sources || [];
                
                html += `
                    <div class="bg-zinc-800/50 rounded-lg p-4 border border-zinc-700">
                        <div class="flex items-start gap-3">
                            <span class="text-blue-400 font-bold flex-shrink-0">${index + 1}.</span>
                            <div class="flex-1">
                                <p class="text-zinc-200 text-sm leading-relaxed">${this.escapeHtml(bulletText)}</p>
                                ${sources.length > 0 ? `
                                    <div class="mt-2 pt-2 border-t border-zinc-700">
                                        <p class="text-xs text-zinc-400 mb-1">Sources:</p>
                                        <div class="flex flex-wrap gap-2">
                                            ${sources.map(source => `
                                                <span class="text-xs bg-zinc-700 px-2 py-1 rounded text-zinc-300">
                                                    ${this.escapeHtml(source)}
                                                </span>
                                            `).join('')}
                                        </div>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                `;
            });
        }
        
        html += `
                    </div>
                </div>
            </div>
        `;
        
        return html;
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

