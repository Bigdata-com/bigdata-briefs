// Calculate maximum number of days based on frequency (maximum 4 times the frequency)
function calculateMaxDays(frequency) {
    const frequencyToDays = {
        // Here we tweak this values to get reasonable max ranges
        'D': 14,     // 2 weeks
        'W': 120,     // 4 months
        'M': 180,    // Half a year
        '3M': 365,   // Quarterly: 1 year
        'Y': 1460    // 4 years
    };

    const baseDays = frequencyToDays[frequency] || 90; // Default to quarterly if unknown
    return baseDays
}



// Validate date range based on frequency
function validateDateRange(startDate, endDate, frequency) {
    if (!startDate || !endDate || !frequency) {
        return { isValid: true, message: '' }; // Skip validation if any value is missing
    }

    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    const maxDays = calculateMaxDays(frequency);

    if (diffDays > maxDays) {
        const frequencyNames = {
            'D': 'Daily',
            'W': 'Weekly',
            'M': 'Monthly',
            '3M': 'Quarterly',
            'Y': 'Yearly'
        };
        const frequencyName = frequencyNames[frequency] || frequency;

        return {
            isValid: false,
            message: `Date range exceeds maximum allowed for ${frequencyName} frequency. <br>Maximum: ${maxDays} days.<br>Current range: ${diffDays} days.<br>Use the endpoint directly for full control`
        };
    }

    return { isValid: true, message: '' };
}


// Add event listeners for date range validation
function validateAndShowError() {
    const startDateValue = document.getElementById('start_date').value;
    const endDateValue = document.getElementById('end_date').value;
    const frequencyValue = document.getElementById('frequency').value;

    const validation = validateDateRange(startDateValue, endDateValue, frequencyValue);

    // Remove any existing error message
    const existingError = document.getElementById('dateRangeError');
    if (existingError) {
        existingError.remove();
    }

    if (!validation.isValid) {
        // Create and show error message
        const errorDiv = document.createElement('div');
        errorDiv.id = 'dateRangeError';
        errorDiv.className = 'mb-5 p-3 bg-red-800 text-white rounded-lg border border-red-600';
        errorDiv.innerHTML = `<strong>⚠️ Date Range Error:</strong> <br> ${validation.message}`;

        // Insert after the frequency field
        const frequencyField = document.getElementById('frequency').closest('.mb-5');
        frequencyField.parentNode.insertBefore(errorDiv, frequencyField.nextSibling);
    }
}

// Add event listeners after the DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    //document.getElementById('start_date').addEventListener('change', validateAndShowError);
    //document.getElementById('end_date').addEventListener('change', validateAndShowError);
    //document.getElementById('frequency').addEventListener('change', validateAndShowError);
});