// Configuration Panel - Sliding Side Panel

function toggleConfigPanel() {
    const panel = document.getElementById('configPanel');
    const backdrop = document.getElementById('configBackdrop');
    
    if (panel && backdrop) {
        const isOpen = !panel.classList.contains('translate-x-full');
        
        if (isOpen) {
            // Close
            panel.classList.add('translate-x-full');
            backdrop.classList.add('hidden');
            backdrop.classList.remove('opacity-100');
        } else {
            // Open
            panel.classList.remove('translate-x-full');
            backdrop.classList.remove('hidden');
            setTimeout(() => backdrop.classList.add('opacity-100'), 10);
        }
    }
}

function closeConfigPanel() {
    const panel = document.getElementById('configPanel');
    const backdrop = document.getElementById('configBackdrop');
    
    if (panel && backdrop) {
        panel.classList.add('translate-x-full');
        backdrop.classList.add('hidden');
        backdrop.classList.remove('opacity-100');
    }
}

// Make functions globally available
window.toggleConfigPanel = toggleConfigPanel;
window.closeConfigPanel = closeConfigPanel;

// Close panel when clicking backdrop
document.addEventListener('DOMContentLoaded', function() {
    const backdrop = document.getElementById('configBackdrop');
    if (backdrop) {
        backdrop.addEventListener('click', function(e) {
            if (e.target === backdrop) {
                closeConfigPanel();
            }
        });
    }
});

