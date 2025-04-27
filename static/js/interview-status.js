/**
 * Interview Status Handler
 * Adds interview status badges to hero and community builder cards
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Interview Status Handler: Initializing');
    
    // Wait for heroes data to be loaded
    const checkForHeroes = setInterval(function() {
        const heroesList = document.getElementById('heroesList');
        if (heroesList && heroesList.querySelectorAll('.card').length > 0) {
            console.log('Interview Status Handler: Heroes loaded, proceeding with interview status');
            clearInterval(checkForHeroes);
            loadInterviewData();
        }
    }, 1000); // Check every second
    
    // Set a timeout to stop checking after 30 seconds
    setTimeout(function() {
        clearInterval(checkForHeroes);
        console.log('Interview Status Handler: Timed out waiting for heroes to load');
    }, 30000);
});

function loadInterviewData() {
    // Use the correct path to the CSV file
    fetch(window.location.origin + '/meet-aws-community/data/AWS_Community_Members.csv')
        .then(response => {
            console.log('Interview Status Handler: CSV fetch response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.text();
        })
        .then(csvText => {
            console.log('Interview Status Handler: CSV data loaded, parsing...');
            const interviewData = parseInterviewCSV(csvText);
            console.log('Interview Status Handler: Parsed interview data:', interviewData);
            
            // Apply status badges to hero cards
            console.log('Interview Status Handler: Applying badges to hero cards');
            applyStatusBadges('heroesList', interviewData);
            
            // Apply status badges to community builder cards if available
            if (document.getElementById('buildersList')) {
                console.log('Interview Status Handler: Applying badges to community builder cards');
                applyStatusBadges('buildersList', interviewData);
            } else {
                console.log('Interview Status Handler: Community builders list not found');
            }
        })
        .catch(error => {
            console.error('Error loading interview data:', error);
        });
}

// Parse the CSV data
function parseInterviewCSV(csvText) {
    console.log('Interview Status Handler: Starting CSV parsing');
    const lines = csvText.split('\n');
    const headers = lines[0].split(',');
    
    console.log('Interview Status Handler: CSV Headers:', headers);
    
    // Find the indices of the important columns
    const nameIndex = headers.findIndex(h => h.trim() === 'Name');
    const statusIndex = headers.findIndex(h => h.trim() === 'Status');
    const youtubeIndex = headers.findIndex(h => h.includes('Recording') || h.includes('YouTube'));
    
    console.log('Interview Status Handler: Column indices - Name:', nameIndex, 'Status:', statusIndex, 'YouTube:', youtubeIndex);
    
    // Parse the data
    const interviewData = {};
    
    for (let i = 1; i < lines.length; i++) {
        if (!lines[i].trim()) continue;
        
        // Handle commas within quoted fields
        const values = [];
        let inQuotes = false;
        let currentValue = '';
        
        for (let j = 0; j < lines[i].length; j++) {
            const char = lines[i][j];
            
            if (char === '"') {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                values.push(currentValue);
                currentValue = '';
            } else {
                currentValue += char;
            }
        }
        
        values.push(currentValue);
        
        // Extract the relevant data
        const name = values[nameIndex]?.replace(/^"(.*)"$/, '$1').trim();
        const status = values[statusIndex]?.replace(/^"(.*)"$/, '$1').trim();
        const youtubeLink = values[youtubeIndex]?.replace(/^"(.*)"$/, '$1').trim();
        
        if (name && status) {
            interviewData[name] = {
                status: status,
                youtubeLink: youtubeLink || null
            };
            console.log(`Interview Status Handler: Added data for ${name}, status: ${status}`);
        }
    }
    
    return interviewData;
}

// Apply status badges to cards
function applyStatusBadges(containerId, interviewData) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.log(`Interview Status Handler: Container ${containerId} not found`);
        return;
    }
    
    console.log(`Interview Status Handler: Found container ${containerId}`);
    
    // Find all cards in the container
    const cards = container.querySelectorAll('.card');
    console.log(`Interview Status Handler: Found ${cards.length} cards in ${containerId}`);
    
    cards.forEach((card, index) => {
        // Find the name in the card
        const nameElement = card.querySelector('h3');
        if (!nameElement) {
            console.log(`Interview Status Handler: No h3 element found in card ${index}`);
            return;
        }
        
        const name = nameElement.textContent.trim();
        console.log(`Interview Status Handler: Processing card for ${name}`);
        
        const interviewInfo = interviewData[name];
        
        if (interviewInfo) {
            console.log(`Interview Status Handler: Found interview data for ${name}:`, interviewInfo);
            
            // Create and add the status badge
            const badge = document.createElement('div');
            badge.className = 'interview-badge';
            
            // Style based on status
            switch (interviewInfo.status.toLowerCase()) {
                case 'done':
                    badge.classList.add('interview-done');
                    badge.innerHTML = '<i class="fas fa-video"></i> Interview Available';
                    break;
                case 'next up':
                    badge.classList.add('interview-scheduled');
                    badge.innerHTML = '<i class="fas fa-calendar-check"></i> Interview Scheduled';
                    break;
                case 'in progress':
                    badge.classList.add('interview-in-progress');
                    badge.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Interview In Progress';
                    break;
                default:
                    badge.classList.add('interview-other');
                    badge.innerHTML = '<i class="fas fa-info-circle"></i> ' + interviewInfo.status;
            }
            
            // Add YouTube link if available
            if (interviewInfo.youtubeLink) {
                const linkContainer = document.createElement('div');
                linkContainer.className = 'youtube-link';
                linkContainer.innerHTML = `<a href="${interviewInfo.youtubeLink}" target="_blank" rel="noopener">
                    <i class="fab fa-youtube"></i> Watch Interview
                </a>`;
                badge.appendChild(linkContainer);
            }
            
            // Add the badge to the card
            const cardContent = card.querySelector('.card-content') || card;
            cardContent.appendChild(badge);
            console.log(`Interview Status Handler: Added badge to card for ${name}`);
        } else {
            console.log(`Interview Status Handler: No interview data found for ${name}`);
        }
    });
}
