// Tab Controller - Manages tab navigation similar to risk analyzer

class TabController {
    constructor() {
        this.currentTab = 'overview';
        this.tabs = [];
    }

    init() {
        // Get all tab buttons
        this.tabs = document.querySelectorAll('[data-tab]');
        
        // Add click handlers
        this.tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.currentTarget.getAttribute('data-tab');
                this.switchTab(tabName);
            });
        });

        // Set initial tab
        if (this.tabs.length > 0) {
            const initialTab = this.tabs[0].getAttribute('data-tab');
            this.switchTab(initialTab);
        }
    }

    switchTab(tabName) {
        this.currentTab = tabName;

        // Update tab buttons
        this.tabs.forEach(tab => {
            const tabId = tab.getAttribute('data-tab');
            if (tabId === tabName) {
                // Active tab
                tab.classList.remove('border-transparent', 'text-zinc-400', 'hover:text-zinc-200');
                tab.classList.add('border-blue-500', 'text-blue-400', 'bg-blue-500/10');
            } else {
                // Inactive tab
                tab.classList.remove('border-blue-500', 'text-blue-400', 'bg-blue-500/10');
                tab.classList.add('border-transparent', 'text-zinc-400', 'hover:text-zinc-200');
            }
        });

        // Update tab content
        const tabContents = document.querySelectorAll('[data-tab-content]');
        tabContents.forEach(content => {
            const contentId = content.getAttribute('data-tab-content');
            if (contentId === tabName) {
                content.classList.remove('hidden');
            } else {
                content.classList.add('hidden');
            }
        });

        // Trigger custom event for tab change
        const event = new CustomEvent('tabChanged', { detail: { tab: tabName } });
        document.dispatchEvent(event);
    }

    reset() {
        if (this.tabs.length > 0) {
            const firstTab = this.tabs[0].getAttribute('data-tab');
            this.switchTab(firstTab);
        }
    }

    getCurrentTab() {
        return this.currentTab;
    }
}

// Initialize tab controller when DOM is ready
window.tabController = new TabController();
document.addEventListener('DOMContentLoaded', function() {
    window.tabController.init();
});

