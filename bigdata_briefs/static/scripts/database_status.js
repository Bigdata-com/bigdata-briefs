// Database Status Viewer functionality

let databaseData = null;
let currentDatabaseTab = 'runs';

/**
 * Toggle the database status section visibility
 */
function toggleDatabaseStatus() {
  const container = document.getElementById('databaseStatusContainer');
  const icon = document.getElementById('databaseStatusIcon');
  
  if (container.classList.contains('hidden')) {
    container.classList.remove('hidden');
    icon.classList.add('rotate-180');
    // Auto-load data when opening for the first time
    if (!databaseData) {
      loadDatabaseStatus();
    }
  } else {
    container.classList.add('hidden');
    icon.classList.remove('rotate-180');
  }
}

/**
 * Load database status from the API
 */
async function loadDatabaseStatus() {
  const contentDiv = document.getElementById('databaseStatusContent');
  const summarySpan = document.getElementById('dbStatusSummary');
  
  // Show loading state
  contentDiv.innerHTML = `
    <div class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-2 border-blue-600 border-t-transparent"></div>
      <span class="ml-3 text-text3">Loading database status...</span>
    </div>
  `;
  
  try {
    const response = await fetch('/briefs/database-status');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    databaseData = await response.json();
    
    // Update summary
    summarySpan.textContent = `${databaseData.total_workflow_runs} runs | ${databaseData.total_reports} reports | ${databaseData.total_bullet_points} bullet points`;
    
    // Render the current tab
    renderDatabaseTab(currentDatabaseTab);
    
  } catch (error) {
    console.error('Error loading database status:', error);
    contentDiv.innerHTML = `
      <div class="text-center text-red-500 py-8">
        <p class="mb-2">Failed to load database status</p>
        <p class="text-sm text-text3">${error.message}</p>
      </div>
    `;
  }
}

/**
 * Switch between database tabs
 */
function switchDatabaseTab(tabName) {
  currentDatabaseTab = tabName;
  
  // Update tab button styles
  ['runs', 'reports', 'bullets'].forEach(tab => {
    const button = document.getElementById(`dbTab-${tab}`);
    if (tab === tabName) {
      button.classList.remove('border-transparent', 'text-text3');
      button.classList.add('border-blue-600', 'text-blue-500');
    } else {
      button.classList.remove('border-blue-600', 'text-blue-500');
      button.classList.add('border-transparent', 'text-text3');
    }
  });
  
  // Render the selected tab
  if (databaseData) {
    renderDatabaseTab(tabName);
  }
}

/**
 * Render a specific database tab
 */
function renderDatabaseTab(tabName) {
  const contentDiv = document.getElementById('databaseStatusContent');
  
  if (!databaseData) {
    contentDiv.innerHTML = '<div class="text-center text-text3 py-8">No data loaded</div>';
    return;
  }
  
  switch (tabName) {
    case 'runs':
      renderWorkflowRuns(contentDiv);
      break;
    case 'reports':
      renderReports(contentDiv);
      break;
    case 'bullets':
      renderBulletPoints(contentDiv);
      break;
  }
}

/**
 * Render workflow runs table
 */
function renderWorkflowRuns(container) {
  const runs = databaseData.workflow_runs || [];
  
  if (runs.length === 0) {
    container.innerHTML = '<div class="text-center text-text3 py-8">No workflow runs found</div>';
    return;
  }
  
  // Sort by last_updated descending
  const sortedRuns = [...runs].sort((a, b) => new Date(b.last_updated) - new Date(a.last_updated));
  
  const tableHTML = `
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-surface border-b border-border">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-semibold text-text3 uppercase">ID</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-text3 uppercase">Status</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-text3 uppercase">Last Updated</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-text3 uppercase">Logs</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border">
          ${sortedRuns.map(run => `
            <tr class="hover:bg-surface transition-colors">
              <td class="px-4 py-3 text-text2 font-mono text-xs">${run.id.substring(0, 8)}...</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded text-xs font-medium ${getStatusColor(run.status)}">
                  ${run.status}
                </span>
              </td>
              <td class="px-4 py-3 text-text2">${formatDateTime(run.last_updated)}</td>
              <td class="px-4 py-3 text-text2">${run.log_count} logs</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
  
  container.innerHTML = tableHTML;
}

/**
 * Render reports table
 */
function renderReports(container) {
  const reports = databaseData.reports || [];
  
  if (reports.length === 0) {
    container.innerHTML = '<div class="text-center text-text3 py-8">No reports found</div>';
    return;
  }
  
  // Sort by created_at descending
  const sortedReports = [...reports].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  
  const tableHTML = `
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-surface border-b border-border">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-semibold text-text3 uppercase">ID</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-text3 uppercase">Watchlist</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-text3 uppercase">Period</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-text3 uppercase">Created</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-text3 uppercase">Novelty</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-text3 uppercase">Empty</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border">
          ${sortedReports.map(report => `
            <tr class="hover:bg-surface transition-colors">
              <td class="px-4 py-3 text-text2 font-mono text-xs">${report.id.substring(0, 8)}...</td>
              <td class="px-4 py-3 text-text2 font-mono text-xs">${report.watchlist_id.substring(0, 8)}...</td>
              <td class="px-4 py-3 text-text2 text-xs">
                ${formatDate(report.report_period_start)} - ${formatDate(report.report_period_end)}
              </td>
              <td class="px-4 py-3 text-text2">${formatDateTime(report.created_at)}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded text-xs font-medium ${report.novelty_enabled ? 'bg-green-600/20 text-green-400' : 'bg-gray-600/20 text-gray-400'}">
                  ${report.novelty_enabled ? 'Yes' : 'No'}
                </span>
              </td>
              <td class="px-4 py-3">
                ${report.is_empty ? '<span class="text-yellow-500">Yes</span>' : '<span class="text-green-500">No</span>'}
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
  
  container.innerHTML = tableHTML;
}

/**
 * Render bullet points table
 */
function renderBulletPoints(container) {
  const bulletPoints = databaseData.bullet_points || [];
  
  if (bulletPoints.length === 0) {
    container.innerHTML = '<div class="text-center text-text3 py-8">No bullet points found</div>';
    return;
  }
  
  // Sort by date descending
  const sortedBullets = [...bulletPoints].sort((a, b) => new Date(b.date) - new Date(a.date));
  
  const tableHTML = `
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-surface border-b border-border">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-semibold text-text3 uppercase">ID</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-text3 uppercase">Entity ID</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-text3 uppercase">Date</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-text3 uppercase">Text</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border">
          ${sortedBullets.map(bp => `
            <tr class="hover:bg-surface transition-colors">
              <td class="px-4 py-3 text-text2 font-mono text-xs">${bp.id.substring(0, 8)}...</td>
              <td class="px-4 py-3 text-text2 font-mono text-xs">${bp.entity_id}</td>
              <td class="px-4 py-3 text-text2">${formatDate(bp.date)}</td>
              <td class="px-4 py-3 text-text2 max-w-md">
                <div class="truncate" title="${escapeHtml(bp.original_text)}">
                  ${escapeHtml(bp.original_text.substring(0, 100))}${bp.original_text.length > 100 ? '...' : ''}
                </div>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
  
  container.innerHTML = tableHTML;
}

/**
 * Helper: Get status badge color
 */
function getStatusColor(status) {
  const colors = {
    'queued': 'bg-gray-600/20 text-gray-400',
    'in_progress': 'bg-blue-600/20 text-blue-400',
    'completed': 'bg-green-600/20 text-green-400',
    'failed': 'bg-red-600/20 text-red-400'
  };
  return colors[status] || 'bg-gray-600/20 text-gray-400';
}

/**
 * Helper: Format datetime to readable string
 */
function formatDateTime(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

/**
 * Helper: Format date only
 */
function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}

/**
 * Helper: Escape HTML to prevent XSS
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Export functions to global scope
window.toggleDatabaseStatus = toggleDatabaseStatus;
window.loadDatabaseStatus = loadDatabaseStatus;
window.switchDatabaseTab = switchDatabaseTab;

