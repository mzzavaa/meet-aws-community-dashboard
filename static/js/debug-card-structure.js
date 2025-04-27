/**
 * Debug Card Structure
 * This script helps debug the structure of hero and community builder cards
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Debug Card Structure: Initializing');
    
    // Wait for heroes data to be loaded
    const checkForHeroes = setInterval(function() {
        const heroesList = document.getElementById('heroesList');
        if (heroesList && heroesList.querySelectorAll('.card').length > 0) {
            console.log('Debug Card Structure: Heroes loaded, proceeding with debugging');
            clearInterval(checkForHeroes);
            
            // Debug hero cards
            debugCardStructure('heroesList', 'Heroes');
            
            // Debug community builder cards
            debugCardStructure('buildersList', 'Community Builders');
        }
    }, 1000); // Check every second
    
    // Set a timeout to stop checking after 30 seconds
    setTimeout(function() {
        clearInterval(checkForHeroes);
        console.log('Debug Card Structure: Timed out waiting for heroes to load');
    }, 30000);
});

function debugCardStructure(containerId, containerName) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.log(`Debug Card Structure: Container ${containerId} not found`);
        return;
    }
    
    console.log(`Debug Card Structure: Found ${containerName} container`);
    
    // Find all cards in the container
    const cards = container.querySelectorAll('.card');
    console.log(`Debug Card Structure: Found ${cards.length} cards in ${containerName} container`);
    
    if (cards.length === 0) {
        // Try to find any elements in the container
        const allElements = container.children;
        console.log(`Debug Card Structure: Container has ${allElements.length} child elements`);
        
        if (allElements.length > 0) {
            console.log('Debug Card Structure: First few elements in container:');
            for (let i = 0; i < Math.min(3, allElements.length); i++) {
                console.log(`Element ${i}:`, allElements[i].outerHTML);
            }
        }
    } else {
        // Debug the first card
        const firstCard = cards[0];
        console.log(`Debug Card Structure: First ${containerName} card structure:`, firstCard.outerHTML);
        
        // Check for h3 elements
        const nameElements = firstCard.querySelectorAll('h3');
        console.log(`Debug Card Structure: Found ${nameElements.length} h3 elements in first card`);
        
        if (nameElements.length > 0) {
            nameElements.forEach((el, i) => {
                console.log(`Debug Card Structure: h3 element ${i} text:`, el.textContent);
            });
        }
        
        // Check for card-content elements
        const contentElements = firstCard.querySelectorAll('.card-content');
        console.log(`Debug Card Structure: Found ${contentElements.length} .card-content elements in first card`);
        
        // Look for Chris Williams specifically
        let chrisFound = false;
        cards.forEach((card, i) => {
            const nameEl = card.querySelector('h3');
            if (nameEl && nameEl.textContent.includes('Chris Williams')) {
                console.log(`Debug Card Structure: Found Chris Williams card at index ${i}`);
                console.log('Debug Card Structure: Chris Williams card structure:', card.outerHTML);
                chrisFound = true;
            }
        });
        
        if (!chrisFound) {
            console.log('Debug Card Structure: Chris Williams card not found');
        }
    }
}
