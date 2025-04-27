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
            
            // Trigger the filter functionality based on data attributes
            const filter = this.getAttribute('data-filter');
            const interviewFilter = this.getAttribute('data-interview-filter');
            
            // If this is a category filter button
            if (filter) {
                // Trigger the category filter functionality
                if (typeof filterHeroesByCategory === 'function') {
                    filterHeroesByCategory(filter);
                } else if (typeof window.filterHeroesByCategory === 'function') {
                    window.filterHeroesByCategory(filter);
                } else if (filter === 'machine learning' && document.getElementById('ml-filter-btn')) {
                    // Special handling for ML filter button
                    const event = new Event('click');
                    document.getElementById('ml-filter-btn').dispatchEvent(event);
                }
            }
            
            // If this is an interview filter button
            if (interviewFilter) {
                // Trigger the interview filter functionality
                if (typeof filterHeroesByInterviewStatus === 'function') {
                    filterHeroesByInterviewStatus(interviewFilter);
                } else if (typeof window.filterHeroesByInterviewStatus === 'function') {
                    window.filterHeroesByInterviewStatus(interviewFilter);
                }
            }
        });
    });
    
    // Define global filter functions that can be called from other scripts
    window.filterHeroesByCategory = function(filter) {
        if (typeof heroes !== 'undefined' && typeof filteredHeroes !== 'undefined') {
            if (filter === 'all') {
                filteredHeroes = [...heroes];
            } else if (filter === 'machine learning') {
                // Special handling for ML filter to catch variations
                filteredHeroes = heroes.filter(hero => {
                    const category = hero.Category ? hero.Category.toLowerCase() : '';
                    return category.includes('machine learning') || 
                           category.includes('ml') || 
                           category.includes('ai');
                });
            } else {
                filteredHeroes = heroes.filter(hero => {
                    return hero.Category && hero.Category.toLowerCase().includes(filter);
                });
            }
            
            if (typeof currentPage !== 'undefined') {
                currentPage = 1;
            }
            
            if (typeof renderHeroes === 'function') {
                renderHeroes();
            }
            
            if (typeof updateStats === 'function') {
                updateStats(filteredHeroes);
            }
        }
    };
    
    window.filterHeroesByInterviewStatus = function(filter) {
        if (typeof heroes !== 'undefined' && typeof filteredHeroes !== 'undefined') {
            if (filter === 'all') {
                filteredHeroes = [...heroes];
            } else {
                filteredHeroes = heroes.filter(hero => {
                    return hero.InterviewStatus && hero.InterviewStatus.toLowerCase() === filter;
                });
            }
            
            if (typeof currentPage !== 'undefined') {
                currentPage = 1;
            }
            
            if (typeof renderHeroes === 'function') {
                renderHeroes();
            }
            
            if (typeof updateStats === 'function') {
                updateStats(filteredHeroes);
            }
        }
    };
});
