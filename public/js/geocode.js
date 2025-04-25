/**
 * Geocoding utility for AWS Community Dashboard
 * 
 * This file contains a pre-computed mapping of locations to coordinates
 * and utility functions for geocoding.
 */

// Global geocoding cache
const geocodeCache = {};

// Common locations with pre-computed coordinates
const commonLocations = {
    // United States
    "USA": [37.0902, -95.7129],
    "United States": [37.0902, -95.7129],
    "US": [37.0902, -95.7129],
    "New York": [40.7128, -74.0060],
    "San Francisco": [37.7749, -122.4194],
    "Seattle": [47.6062, -122.3321],
    "Chicago": [41.8781, -87.6298],
    "Austin": [30.2672, -97.7431],
    "Boston": [42.3601, -71.0589],
    "Los Angeles": [34.0522, -118.2437],
    "Denver": [39.7392, -104.9903],
    "Atlanta": [33.7490, -84.3880],
    "Dallas": [32.7767, -96.7970],
    "Miami": [25.7617, -80.1918],
    "Washington": [38.9072, -77.0369],
    "Washington DC": [38.9072, -77.0369],
    "Portland": [45.5051, -122.6750],
    "Las Vegas": [36.1699, -115.1398],
    "Phoenix": [33.4484, -112.0740],
    "Philadelphia": [39.9526, -75.1652],
    "San Diego": [32.7157, -117.1611],
    "Minneapolis": [44.9778, -93.2650],
    "Detroit": [42.3314, -83.0458],
    "Tulsa": [36.1540, -95.9928],
    
    // Europe
    "UK": [55.3781, -3.4360],
    "United Kingdom": [55.3781, -3.4360],
    "London": [51.5074, -0.1278],
    "Germany": [51.1657, 10.4515],
    "Berlin": [52.5200, 13.4050],
    "France": [46.2276, 2.2137],
    "Paris": [48.8566, 2.3522],
    "Spain": [40.4637, -3.7492],
    "Madrid": [40.4168, -3.7038],
    "Italy": [41.8719, 12.5674],
    "Rome": [41.9028, 12.4964],
    "Netherlands": [52.1326, 5.2913],
    "Amsterdam": [52.3676, 4.9041],
    "Switzerland": [46.8182, 8.2275],
    "Zurich": [47.3769, 8.5417],
    "Sweden": [60.1282, 18.6435],
    "Stockholm": [59.3293, 18.0686],
    "Norway": [60.4720, 8.4689],
    "Oslo": [59.9139, 10.7522],
    "Denmark": [56.2639, 9.5018],
    "Copenhagen": [55.6761, 12.5683],
    "Finland": [61.9241, 25.7482],
    "Helsinki": [60.1699, 24.9384],
    "Belgium": [50.5039, 4.4699],
    "Brussels": [50.8503, 4.3517],
    "Ireland": [53.1424, -7.6921],
    "Dublin": [53.3498, -6.2603],
    "Romania": [45.9432, 24.9668],
    "Bucharest": [44.4268, 26.1025],
    "Timisoara": [45.7489, 21.2087],
    "Iasi": [47.1585, 27.6014],
    
    // Asia Pacific
    "India": [20.5937, 78.9629],
    "Mumbai": [19.0760, 72.8777],
    "Bangalore": [12.9716, 77.5946],
    "New Delhi": [28.6139, 77.2090],
    "Japan": [36.2048, 138.2529],
    "Tokyo": [35.6762, 139.6503],
    "Australia": [-25.2744, 133.7751],
    "Sydney": [-33.8688, 151.2093],
    "Melbourne": [-37.8136, 144.9631],
    "Singapore": [1.3521, 103.8198],
    "China": [35.8617, 104.1954],
    "Beijing": [39.9042, 116.4074],
    "Shanghai": [31.2304, 121.4737],
    "South Korea": [35.9078, 127.7669],
    "Seoul": [37.5665, 126.9780],
    "Hong Kong": [22.3193, 114.1694],
    "Taiwan": [23.6978, 120.9605],
    "Taipei": [25.0330, 121.5654],
    "Malaysia": [4.2105, 101.9758],
    "Kuala Lumpur": [3.1390, 101.6869],
    "Indonesia": [-0.7893, 113.9213],
    "Jakarta": [-6.2088, 106.8456],
    "Thailand": [15.8700, 100.9925],
    "Bangkok": [13.7563, 100.5018],
    "Vietnam": [14.0583, 108.2772],
    "Ho Chi Minh City": [10.8231, 106.6297],
    "Philippines": [12.8797, 121.7740],
    "Manila": [14.5995, 120.9842],
    
    // Africa
    "South Africa": [-30.5595, 22.9375],
    "Cape Town": [-33.9249, 18.4241],
    "Johannesburg": [-26.2041, 28.0473],
    "Egypt": [26.8206, 30.8025],
    "Cairo": [30.0444, 31.2357],
    "Nigeria": [9.0820, 8.6753],
    "Lagos": [6.5244, 3.3792],
    "Kenya": [-0.0236, 37.9062],
    "Nairobi": [-1.2921, 36.8219],
    "Morocco": [31.7917, -7.0926],
    "Casablanca": [33.5731, -7.5898],
    "Ghana": [7.9465, -1.0232],
    "Accra": [5.6037, -0.1870],
    "Ivory Coast": [7.5400, -5.5471],
    "Abidjan": [5.3600, -4.0083],
    
    // South America
    "Brazil": [-14.2350, -51.9253],
    "Sao Paulo": [-23.5505, -46.6333],
    "Rio de Janeiro": [-22.9068, -43.1729],
    "Argentina": [-38.4161, -63.6167],
    "Buenos Aires": [-34.6037, -58.3816],
    "Colombia": [4.5709, -74.2973],
    "Bogota": [4.7110, -74.0721],
    "Chile": [-35.6751, -71.5430],
    "Santiago": [-33.4489, -70.6693],
    "Peru": [-9.1900, -75.0152],
    "Lima": [-12.0464, -77.0428],
    "Mexico": [23.6345, -102.5528],
    "Mexico City": [19.4326, -99.1332],
    
    // Canada
    "Canada": [56.1304, -106.3468],
    "Toronto": [43.6532, -79.3832],
    "Vancouver": [49.2827, -123.1207],
    "Montreal": [45.5017, -73.5673],
    "Calgary": [51.0447, -114.0719],
    "Ottawa": [45.4215, -75.6972],
    
    // Default fallback
    "Unknown": [0, 0]
};

/**
 * Get coordinates for a location string
 * @param {string} locationStr - Location string (e.g. "New York, USA")
 * @returns {Array} - [latitude, longitude]
 */
function getCoordinates(locationStr) {
    if (!locationStr) return commonLocations["Unknown"];
    
    // Check cache first
    if (geocodeCache[locationStr]) {
        return geocodeCache[locationStr];
    }
    
    // Clean up the location string
    const cleanLocation = locationStr.trim();
    
    // Check if the exact location is in our common locations
    if (commonLocations[cleanLocation]) {
        geocodeCache[locationStr] = commonLocations[cleanLocation];
        return commonLocations[cleanLocation];
    }
    
    // Try to extract city and country
    const parts = cleanLocation.split(',').map(part => part.trim());
    const city = parts[0];
    const country = parts.length > 1 ? parts[parts.length - 1] : '';
    
    // Check if city is in our common locations
    if (commonLocations[city]) {
        geocodeCache[locationStr] = commonLocations[city];
        return commonLocations[city];
    }
    
    // Check if country is in our common locations
    if (country && commonLocations[country]) {
        // Add a small random offset to avoid all points in a country being at the same spot
        const baseCoords = commonLocations[country];
        const randomLat = (Math.random() - 0.5) * 5; // +/- 2.5 degrees
        const randomLng = (Math.random() - 0.5) * 5;
        const coords = [baseCoords[0] + randomLat, baseCoords[1] + randomLng];
        
        geocodeCache[locationStr] = coords;
        return coords;
    }
    
    // If all else fails, generate a deterministic but distributed position
    const hash = locationStr.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const lat = (hash % 140) - 70; // Range from -70 to 70
    const lng = (hash * 31 % 320) - 160; // Range from -160 to 160
    
    geocodeCache[locationStr] = [lat, lng];
    return [lat, lng];
}

/**
 * Group items by country
 * @param {Array} items - Array of items with Location property
 * @returns {Object} - Object with countries as keys and arrays of items as values
 */
function groupByCountry(items) {
    const groups = {};
    
    items.forEach(item => {
        if (!item.Location) return;
        
        const parts = item.Location.split(',');
        const country = parts.length > 1 ? parts[parts.length - 1].trim() : 'Unknown';
        
        if (!groups[country]) {
            groups[country] = [];
        }
        
        groups[country].push(item);
    });
    
    return groups;
}

/**
 * Create a marker cluster for a map
 * @param {Object} map - Leaflet map object
 * @param {Array} items - Array of items with Location property
 * @param {string} color - Marker color (hex code)
 * @param {Function} popupFormatter - Function to format popup content
 */
function createMarkers(map, items, color, popupFormatter) {
    items.forEach(item => {
        if (!item.Location) return;
        
        const coords = getCoordinates(item.Location);
        const marker = L.circleMarker(coords, {
            radius: 8,
            fillColor: color,
            color: '#fff',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map);
        
        marker.bindPopup(popupFormatter(item));
    });
}

/**
 * Create country clusters for a map
 * @param {Object} map - Leaflet map object
 * @param {Array} items - Array of items with Location property
 * @param {string} color - Marker color (hex code)
 * @param {string} label - Label for the type of items
 */
function createCountryClusters(map, items, color, label) {
    const countries = groupByCountry(items);
    
    Object.entries(countries).forEach(([country, countryItems]) => {
        if (country === 'Unknown') return;
        
        const coords = getCoordinates(country);
        const marker = L.circleMarker(coords, {
            radius: Math.min(Math.max(Math.sqrt(countryItems.length) * 3, 8), 20),
            fillColor: color,
            color: '#fff',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map);
        
        const popupContent = `
            <div class="map-popup">
                <h3>${country}</h3>
                <p><strong>${countryItems.length}</strong> ${label}</p>
                <ul class="map-list">
                    ${countryItems.slice(0, 5).map(item => `<li>${item.Name}</li>`).join('')}
                    ${countryItems.length > 5 ? `<li>and ${countryItems.length - 5} more...</li>` : ''}
                </ul>
            </div>
        `;
        
        marker.bindPopup(popupContent);
    });
}
