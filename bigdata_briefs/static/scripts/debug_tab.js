// Debug Tab functionality for visualizing novelty filtering process

/**
 * Load and render debug data for the Debug tab
 */
async function loadDebugTab(requestId) {
    const debugContent = document.getElementById('debugTabContent');
    
    if (!debugContent) {
        console.error('Debug tab content element not found');
        return;
    }
    
    // Show loading state
    debugContent.innerHTML = `
        <div class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-2 border-blue-600 border-t-transparent"></div>
            <span class="ml-3 text-text3">Loading debug information...</span>
        </div>
    `;
    
    try {
        const response = await fetch(`/briefs/debug/${requestId}`);
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('No debug data found for this brief');
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const debugData = await response.json();
        renderDebugData(debugData);
        
    } catch (error) {
        console.error('Error loading debug data:', error);
        debugContent.innerHTML = `
            <div class="text-center py-12">
                <div class="text-yellow-500 mb-4">
                    <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                    </svg>
                </div>
                <h3 class="text-lg font-semibold text-text mb-2">Debug Data Not Available</h3>
                <p class="text-text3 mb-4">${error.message}</p>
                <p class="text-sm text-text3">Debug data is only collected when novelty filtering is enabled.</p>
            </div>
        `;
    }
}

/**
 * Render the debug data in an organized format
 */
function renderDebugData(debugData) {
    const debugContent = document.getElementById('debugTabContent');
    
    if (!debugData.entities || Object.keys(debugData.entities).length === 0) {
        debugContent.innerHTML = `
            <div class="text-center py-12">
                <p class="text-text3">No debug data available (novelty filtering may have been disabled)</p>
            </div>
        `;
        return;
    }
    
    // Create accordion for each entity
    let html = '<div class="space-y-4">';
    
    for (const [entityId, entityData] of Object.entries(debugData.entities)) {
        html += renderEntityDebugSection(entityId, entityData);
    }
    
    html += '</div>';
    debugContent.innerHTML = html;
}

/**
 * Render debug information for a single entity
 */
function renderEntityDebugSection(entityId, entityData) {
    const sectionId = `debug-entity-${entityId.replace(/[^a-zA-Z0-9]/g, '')}`;
    const entityName = entityData.entity_name || entityId;
    
    const generatedCount = entityData.generated_texts?.length || 0;
    const comparedCount = entityData.compared_with?.length || 0;
    const discardedCount = entityData.discarded?.length || 0;
    const keptCount = entityData.kept_texts?.length || 0;
    
    return `
        <div class="border border-border rounded-lg bg-surface overflow-hidden">
            <button onclick="toggleDebugSection('${sectionId}')" 
                class="w-full flex items-center justify-between px-6 py-4 hover:bg-surface2 transition-colors">
                <div class="flex items-center gap-3">
                    <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                    </svg>
                    <h3 class="text-lg font-semibold text-text">${escapeHtml(entityName)}</h3>
                    <span class="text-xs text-text3 font-mono">(${entityId})</span>
                </div>
                <div class="flex items-center gap-4">
                    <span class="text-sm text-text3">
                        Generated: ${generatedCount} | Compared: ${comparedCount} | Discarded: ${discardedCount} | Kept: ${keptCount}
                    </span>
                    <svg id="${sectionId}-icon" class="w-5 h-5 text-text3 transform transition-transform duration-200" 
                         fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                </div>
            </button>
            
            <div id="${sectionId}" class="hidden px-6 pb-6">
                <div class="space-y-6">
                    ${renderGeneratedSection(entityData.generated_texts)}
                    ${renderComparedSection(entityData.compared_with)}
                    ${renderDiscardedSection(entityData.discarded)}
                    ${renderKeptSection(entityData.kept_texts)}
                </div>
            </div>
        </div>
    `;
}

/**
 * Render Generated texts section
 */
function renderGeneratedSection(texts) {
    if (!texts || texts.length === 0) {
        return '<div class="text-text3 text-sm">No generated texts</div>';
    }
    
    return `
        <div>
            <h4 class="text-sm font-semibold text-text mb-3 flex items-center gap-2">
                <span class="w-3 h-3 bg-blue-500 rounded-full"></span>
                Generated Texts (${texts.length})
            </h4>
            <div class="bg-surface2 rounded-lg p-4 space-y-2">
                ${texts.map((text, idx) => `
                    <div class="flex gap-3">
                        <span class="text-text3 text-xs mt-1">${idx + 1}.</span>
                        <p class="text-text2 text-sm">${escapeHtml(text)}</p>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

/**
 * Render Compared With section
 */
function renderComparedSection(texts) {
    if (!texts || texts.length === 0) {
        return `
            <div>
                <h4 class="text-sm font-semibold text-text mb-3 flex items-center gap-2">
                    <span class="w-3 h-3 bg-gray-500 rounded-full"></span>
                    Compared With (0)
                </h4>
                <div class="bg-surface2 rounded-lg p-4">
                    <p class="text-text3 text-sm italic">No previous embeddings found in database</p>
                </div>
            </div>
        `;
    }
    
    return `
        <div>
            <h4 class="text-sm font-semibold text-text mb-3 flex items-center gap-2">
                <span class="w-3 h-3 bg-gray-500 rounded-full"></span>
                Compared With (${texts.length})
            </h4>
            <div class="bg-surface2 rounded-lg p-4 space-y-2 max-h-64 overflow-y-auto enhanced-scrollbar">
                ${texts.map((text, idx) => `
                    <div class="flex gap-3">
                        <span class="text-text3 text-xs mt-1">${idx + 1}.</span>
                        <p class="text-text2 text-sm">${escapeHtml(text)}</p>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

/**
 * Render Discarded section
 */
function renderDiscardedSection(discarded) {
    if (!discarded || discarded.length === 0) {
        return `
            <div>
                <h4 class="text-sm font-semibold text-text mb-3 flex items-center gap-2">
                    <span class="w-3 h-3 bg-red-500 rounded-full"></span>
                    Discarded (0)
                </h4>
                <div class="bg-surface2 rounded-lg p-4">
                    <p class="text-green-500 text-sm">All generated texts were novel!</p>
                </div>
            </div>
        `;
    }
    
    return `
        <div>
            <h4 class="text-sm font-semibold text-text mb-3 flex items-center gap-2">
                <span class="w-3 h-3 bg-red-500 rounded-full"></span>
                Discarded (${discarded.length})
            </h4>
            <div class="bg-surface2 rounded-lg p-4 space-y-4">
                ${discarded.map((item, idx) => `
                    <div class="border-l-2 border-red-500 pl-4">
                        <div class="flex items-start justify-between gap-4 mb-2">
                            <p class="text-text2 text-sm flex-1">${escapeHtml(item.text)}</p>
                            <span class="text-xs font-mono text-red-400 whitespace-nowrap">
                                Similarity: ${(item.max_similarity * 100).toFixed(1)}%
                            </span>
                        </div>
                        <div class="text-xs text-text3 mt-2">
                            <span class="font-semibold">Most similar to:</span>
                            <p class="mt-1 italic">${escapeHtml(item.most_similar_text)}</p>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

/**
 * Render Kept section
 */
function renderKeptSection(texts) {
    if (!texts || texts.length === 0) {
        return `
            <div>
                <h4 class="text-sm font-semibold text-text mb-3 flex items-center gap-2">
                    <span class="w-3 h-3 bg-green-500 rounded-full"></span>
                    Kept (0)
                </h4>
                <div class="bg-surface2 rounded-lg p-4">
                    <p class="text-red-500 text-sm">All texts were discarded as non-novel</p>
                </div>
            </div>
        `;
    }
    
    return `
        <div>
            <h4 class="text-sm font-semibold text-text mb-3 flex items-center gap-2">
                <span class="w-3 h-3 bg-green-500 rounded-full"></span>
                Kept (${texts.length})
            </h4>
            <div class="bg-surface2 rounded-lg p-4 space-y-2">
                ${texts.map((text, idx) => `
                    <div class="flex gap-3 border-l-2 border-green-500 pl-4">
                        <span class="text-text3 text-xs mt-1">${idx + 1}.</span>
                        <p class="text-text2 text-sm">${escapeHtml(text)}</p>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

/**
 * Toggle debug section visibility
 */
function toggleDebugSection(sectionId) {
    const section = document.getElementById(sectionId);
    const icon = document.getElementById(`${sectionId}-icon`);
    
    if (section && icon) {
        section.classList.toggle('hidden');
        icon.classList.toggle('rotate-180');
    }
}

/**
 * Helper: Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Export functions to global scope
window.loadDebugTab = loadDebugTab;
window.toggleDebugSection = toggleDebugSection;

// Listen for tab changes and load debug data when debug tab is activated
document.addEventListener('tabChanged', function(event) {
    if (event.detail.tab === 'debug') {
        // Try to find the request ID from the current URL or last report
        let requestId = window.lastRequestId;
        
        // If not available, try to extract from the status polling
        if (!requestId && window.lastReport) {
            // Check if there's a request ID in the page
            const statusCalls = document.querySelectorAll('[data-request-id]');
            if (statusCalls.length > 0) {
                requestId = statusCalls[0].getAttribute('data-request-id');
            }
        }
        
        if (requestId) {
            loadDebugTab(requestId);
        } else {
            // Show a message that no report has been loaded yet
            const debugContent = document.getElementById('debugTabContent');
            if (debugContent) {
                debugContent.innerHTML = `
                    <div class="text-center py-12">
                        <div class="text-text3 mb-4">
                            <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-semibold text-text mb-2">No Brief Loaded</h3>
                        <p class="text-text3">Generate a brief first to see debug information</p>
                    </div>
                `;
            }
        }
    }
});

// Also integrate with the visualization system to load debug data when report is loaded
document.addEventListener('reportLoaded', function(event) {
    if (event.detail.requestId) {
        window.lastRequestId = event.detail.requestId;
        // If debug tab is currently active, load the data
        if (window.tabController && window.tabController.getCurrentTab() === 'debug') {
            loadDebugTab(event.detail.requestId);
        }
    }
});

