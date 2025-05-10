// Cache buster script
document.addEventListener('DOMContentLoaded', function() {
    // Add timestamp to all data file requests
    const timestamp = new Date().getTime();
    
    // Find all fetch requests to CSV files and add timestamp
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        if (typeof url === 'string' && url.includes('.csv')) {
            const separator = url.includes('?') ? '&' : '?';
            url = `${url}${separator}t=${timestamp}`;
        }
        return originalFetch(url, options);
    };
    
    console.log('Cache buster initialized');
});
