/**
 * Global Error Handler
 * Catches and logs JavaScript errors across the site
 */
window.addEventListener('error', function(e) {
    console.error('Global error caught:', e.error);
    // You could add more sophisticated error handling here
});
