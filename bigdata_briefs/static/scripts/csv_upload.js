// CSV Upload Handler - Additional utility functions if needed

// Validate CSV entities format
function validateCsvEntities(entities) {
    // Basic validation: check if entities are non-empty strings
    return entities.filter(entity => entity && entity.trim().length > 0);
}

// Export entities for use in form submission
function getCsvEntities() {
    return window.csvEntities || [];
}

// Clear CSV upload
function clearCsvUpload() {
    window.csvEntities = [];
    const fileInput = document.getElementById('csvFile');
    if (fileInput) {
        fileInput.value = '';
    }
    const preview = document.getElementById('csvPreview');
    if (preview) {
        preview.classList.add('hidden');
    }
}

// Make functions globally available
window.validateCsvEntities = validateCsvEntities;
window.getCsvEntities = getCsvEntities;
window.clearCsvUpload = clearCsvUpload;

