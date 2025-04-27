/**
 * Filter Buttons Functionality
 * Handles the active state for filter buttons across the site
 */
document.addEventListener('DOMContentLoaded', function() {
    // Apply to all filter buttons across the site
    document.querySelectorAll('.filter-btn').forEach(btn => {
        // Set initial active state
        if (btn.classList.contains('active')) {
            btn.style.backgroundColor = '#FF9900'; // AWS Orange
            btn.style.color = 'white';
            btn.style.borderColor = '#FF9900';
        }
        
        // Add click event listener
        btn.addEventListener('click', function() {
            // Find all buttons in the same filter group
            const filterGroup = this.closest('.filters');
            if (filterGroup) {
                // Remove active state from all buttons in this group
                filterGroup.querySelectorAll('.filter-btn').forEach(b => {
                    b.classList.remove('active');
                    b.style.backgroundColor = '';
                    b.style.color = '';
                    b.style.borderColor = '';
                });
            }
            
            // Add active state to clicked button
            this.classList.add('active');
            this.style.backgroundColor = '#FF9900'; // AWS Orange
            this.style.color = 'white';
            this.style.borderColor = '#FF9900';
        });
    });
});
