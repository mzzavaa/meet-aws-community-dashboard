/**
 * AWS Community Map
 * 
 * This file contains the code for the interactive community map
 * that displays AWS User Groups, Community Builders, and Heroes.
 */

class CommunityMap {
    constructor(mapElementId) {
        this.mapElementId = mapElementId;
        this.map = null;
        this.userGroups = [];
        this.communityBuilders = [];
        this.heroes = [];
        this.markers = {
            userGroups: [],
            communityBuilders: [],
            heroes: []
        };
        this.layerControl = null;
        this.layers = {};
        this.colors = {
            userGroups: '#8C4799', // AWS Purple
            communityBuilders: '#FF9900', // AWS Orange
            heroes: '#1A73E8' // AWS Light Blue
        };
    }
    
    /**
     * Initialize the map
     */
    init() {
        // Create the map
        this.map = L.map(this.mapElementId).setView([20, 0], 2);
        
        // Add the tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(this.map);
        
        // Create layer groups
        this.layers.userGroups = L.layerGroup().addTo(this.map);
        this.layers.communityBuilders = L.layerGroup().addTo(this.map);
        this.layers.heroes = L.layerGroup().addTo(this.map);
        
        // Add layer control
        this.layerControl = L.control.layers(null, {
            'User Groups': this.layers.userGroups,
            'Community Builders': this.layers.communityBuilders,
            'Heroes': this.layers.heroes
        }).addTo(this.map);
        
        // Add legend
        this.addLegend();
        
        return this;
    }
    
    /**
     * Add a legend to the map
     */
    addLegend() {
        const legend = L.control({position: 'bottomright'});
        
        legend.onAdd = (map) => {
            const div = L.DomUtil.create('div', 'info legend');
            div.style.backgroundColor = 'white';
            div.style.padding = '10px';
            div.style.borderRadius = '5px';
            div.style.boxShadow = '0 1px 5px rgba(0,0,0,0.2)';
            
            div.innerHTML = `
                <div style="margin-bottom: 5px;"><strong>AWS Community</strong></div>
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: ${this.colors.userGroups}; margin-right: 5px;"></span>
                    <span>User Groups</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: ${this.colors.communityBuilders}; margin-right: 5px;"></span>
                    <span>Community Builders</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: ${this.colors.heroes}; margin-right: 5px;"></span>
                    <span>Heroes</span>
                </div>
            `;
            
            return div;
        };
        
        legend.addTo(this.map);
    }
    
    /**
     * Load data for the map
     */
    loadData() {
        return Promise.all([
            this.loadUserGroups(),
            this.loadCommunityBuilders(),
            this.loadHeroes()
        ]);
    }
    
    /**
     * Load user groups data
     */
    loadUserGroups() {
        return fetch('/static/data/aws_user_groups.csv')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.text();
            })
            .then(text => {
                this.userGroups = this.parseCSV(text);
                console.log(`Loaded ${this.userGroups.length} user groups`);
                return this.userGroups;
            })
            .catch(error => {
                console.error('Error loading user groups:', error);
                return [];
            });
    }
    
    /**
     * Load community builders data
     */
    loadCommunityBuilders() {
        return fetch('/static/data/aws_community_builders.csv')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.text();
            })
            .then(text => {
                this.communityBuilders = this.parseCSV(text);
                console.log(`Loaded ${this.communityBuilders.length} community builders`);
                return this.communityBuilders;
            })
            .catch(error => {
                console.error('Error loading community builders:', error);
                return [];
            });
    }
    
    /**
     * Load heroes data
     */
    loadHeroes() {
        return fetch('/static/data/aws_heroes.csv')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.text();
            })
            .then(text => {
                this.heroes = this.parseCSV(text);
                console.log(`Loaded ${this.heroes.length} heroes`);
                return this.heroes;
            })
            .catch(error => {
                console.error('Error loading heroes:', error);
                return [];
            });
    }
    
    /**
     * Parse CSV data
     * @param {string} text - CSV text
     * @returns {Array} - Array of objects
     */
    parseCSV(text) {
        try {
            const lines = text.split('\n');
            const headers = lines[0].split(',').map(h => h.trim());
            
            return lines.slice(1)
                .filter(line => line.trim())
                .map(line => {
                    // Handle commas within quoted fields
                    const values = [];
                    let inQuotes = false;
                    let currentValue = '';
                    
                    for (let i = 0; i < line.length; i++) {
                        const char = line[i];
                        
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
                    
                    // Create object from headers and values
                    const entry = {};
                    headers.forEach((header, i) => {
                        entry[header] = values[i] ? values[i].replace(/^"(.*)"$/, '$1') : '';
                    });
                    
                    return entry;
                });
        } catch (e) {
            console.error('CSV parsing error:', e);
            return [];
        }
    }
    
    /**
     * Render the map with all data
     */
    render() {
        this.clearLayers();
        
        // Add user groups to the map
        this.renderUserGroups();
        
        // Add community builders to the map
        this.renderCommunityBuilders();
        
        // Add heroes to the map
        this.renderHeroes();
        
        return this;
    }
    
    /**
     * Clear all layers
     */
    clearLayers() {
        this.layers.userGroups.clearLayers();
        this.layers.communityBuilders.clearLayers();
        this.layers.heroes.clearLayers();
    }
    
    /**
     * Render user groups on the map
     */
    renderUserGroups() {
        createCountryClusters(
            this.map, 
            this.userGroups, 
            this.colors.userGroups, 
            'User Groups'
        );
    }
    
    /**
     * Render community builders on the map
     */
    renderCommunityBuilders() {
        createCountryClusters(
            this.map, 
            this.communityBuilders, 
            this.colors.communityBuilders, 
            'Community Builders'
        );
    }
    
    /**
     * Render heroes on the map
     */
    renderHeroes() {
        if (this.heroes.length === 0) return;
        
        createCountryClusters(
            this.map, 
            this.heroes, 
            this.colors.heroes, 
            'Heroes'
        );
    }
    
    /**
     * Get statistics about the data
     * @returns {Object} - Statistics object
     */
    getStats() {
        const countries = new Set();
        
        // Count unique countries
        this.userGroups.forEach(group => {
            if (group.Location) {
                const country = group.Location.split(',').pop().trim();
                if (country) countries.add(country);
            }
        });
        
        this.communityBuilders.forEach(builder => {
            if (builder.Location) {
                const country = builder.Location.split(',').pop().trim();
                if (country) countries.add(country);
            }
        });
        
        this.heroes.forEach(hero => {
            if (hero.Location) {
                const country = hero.Location.split(',').pop().trim();
                if (country) countries.add(country);
            }
        });
        
        return {
            userGroups: this.userGroups.length,
            communityBuilders: this.communityBuilders.length,
            heroes: this.heroes.length,
            countries: countries.size
        };
    }
    
    /**
     * Get a random item from an array
     * @param {Array} array - Array to get random item from
     * @returns {*} - Random item
     */
    getRandomItem(array) {
        if (!array || array.length === 0) return null;
        return array[Math.floor(Math.random() * array.length)];
    }
    
    /**
     * Get a random user group
     * @returns {Object} - Random user group
     */
    getRandomUserGroup() {
        return this.getRandomItem(this.userGroups);
    }
    
    /**
     * Get a random community builder
     * @returns {Object} - Random community builder
     */
    getRandomCommunityBuilder() {
        return this.getRandomItem(this.communityBuilders);
    }
    
    /**
     * Get a random hero
     * @returns {Object} - Random hero
     */
    getRandomHero() {
        return this.getRandomItem(this.heroes);
    }
}
