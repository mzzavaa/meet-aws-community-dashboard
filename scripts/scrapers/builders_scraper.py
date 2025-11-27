"""
AWS Community Builders scraper for AWS Community Dashboard
"""

import json
import pandas as pd
from typing import Dict, Any, List

from .base_scraper import BaseScraper


class BuildersScraper(BaseScraper):
    """Scraper for AWS Community Builders data"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.search_endpoint = config.get('data_sources', {}).get('community_builders', {}).get('search_endpoint',
                                         'https://aws.amazon.com/api/dirs/items/search')
        self.search_params = config.get('data_sources', {}).get('community_builders', {}).get('search_params', {})
    
    def get_data_type(self) -> str:
        return "builders"
    
    def scrape(self) -> pd.DataFrame:
        """
        Scrape AWS Community Builders data from the search API
        
        Returns:
            DataFrame with builders data
        """
        self.logger.info("Starting AWS Community Builders scraping...")
        
        try:
            builders_data = []
            
            # First query: A-Z sorted
            self.logger.info("Fetching builders A-Z...")
            params_az = self.search_params.copy()
            params_az.update({
                'sort_by': 'item.additionalFields.sortableTitle',
                'sort_order': 'asc',
                'size': 2000
            })
            
            builders_az = self._fetch_builders_batch(params_az)
            builders_data.extend(builders_az)
            
            # Second query: Z-A sorted to catch any missed entries
            self.logger.info("Fetching builders Z-A...")
            params_za = self.search_params.copy()
            params_za.update({
                'sort_by': 'item.additionalFields.sortableTitle',
                'sort_order': 'desc',
                'size': 2000
            })
            
            builders_za = self._fetch_builders_batch(params_za)
            
            # Merge and deduplicate
            all_builders = builders_data + builders_za
            unique_builders = self._deduplicate_builders(all_builders)
            
            # Convert to DataFrame
            df = pd.DataFrame(unique_builders)
            
            if df.empty:
                self.logger.error("No builders data scraped")
                return df
            
            self.logger.info(f"Successfully scraped {len(df)} unique builders")
            
            # Process the data
            df_processed = self.process_data(df)
            
            return df_processed
            
        except Exception as e:
            self.logger.error(f"Error in builders scraping: {e}")
            return pd.DataFrame()
    
    def _fetch_builders_batch(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch a batch of builders from the search API
        
        Args:
            params: Search parameters
            
        Returns:
            List of builder data dictionaries
        """
        try:
            response = self.make_request(self.search_endpoint, params=params)
            data = response.json()
            
            builders = []
            items = data.get('items', [])
            
            self.logger.info(f"Received {len(items)} builders from API")
            
            for item in items:
                builder_data = self._parse_builder_item(item)
                if builder_data:
                    builders.append(builder_data)
            
            return builders
            
        except Exception as e:
            self.logger.error(f"Error fetching builders batch: {e}")
            return []
    
    def _parse_builder_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a single builder item from the API response
        
        Args:
            item: Raw item data from API
            
        Returns:
            Parsed builder data dictionary
        """
        try:
            # Extract basic information
            builder_data = {}
            
            # Name
            builder_data['Name'] = item.get('item', {}).get('additionalFields', {}).get('title', '')
            
            # Location
            location_fields = ['location', 'city', 'country', 'region']
            location_parts = []
            additional_fields = item.get('item', {}).get('additionalFields', {})
            
            for field in location_fields:
                value = additional_fields.get(field, '')
                if value and value not in location_parts:
                    location_parts.append(value)
            
            builder_data['Location'] = ', '.join(location_parts) if location_parts else ''
            
            # Category (program and specialization)
            program = additional_fields.get('program', '')
            specialization = additional_fields.get('specialization', '')
            year = additional_fields.get('year', '')
            
            if specialization and year:
                builder_data['Category'] = f"{specialization} Builder since {year}"
            elif program:
                builder_data['Category'] = program
            else:
                builder_data['Category'] = 'Community Builder'
            
            # Bio URL (LinkedIn, personal website, etc.)
            bio_url = ''
            social_links = additional_fields.get('socialLinks', {})
            
            # Priority order for bio URL
            url_fields = ['linkedin', 'website', 'twitter', 'github']
            for field in url_fields:
                if field in social_links and social_links[field]:
                    bio_url = social_links[field]
                    break
            
            # Fallback to direct URL field
            if not bio_url:
                bio_url = additional_fields.get('url', '')
            
            builder_data['Bio URL'] = bio_url if bio_url else 'No URL'
            
            # Initialize coordinate fields
            builder_data['Latitude'] = None
            builder_data['Longitude'] = None
            
            return builder_data
            
        except Exception as e:
            self.logger.error(f"Error parsing builder item: {e}")
            return {}
    
    def _deduplicate_builders(self, builders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate builders based on name and location
        
        Args:
            builders: List of builder data dictionaries
            
        Returns:
            Deduplicated list of builders
        """
        seen = set()
        unique_builders = []
        
        for builder in builders:
            # Create a key for deduplication
            name = builder.get('Name', '').strip().lower()
            location = builder.get('Location', '').strip().lower()
            key = f"{name}|{location}"
            
            if key not in seen and name:  # Only add if name exists and not seen before
                seen.add(key)
                unique_builders.append(builder)
        
        self.logger.info(f"Deduplicated {len(builders)} -> {len(unique_builders)} builders")
        
        return unique_builders
    
    def _fallback_scraping(self) -> List[Dict[str, Any]]:
        """
        Fallback scraping method using web scraping if API fails
        
        Returns:
            List of builder data dictionaries
        """
        self.logger.info("Attempting fallback web scraping for builders...")
        
        try:
            # This would implement web scraping from the public builders page
            # For now, return empty list as the API method should work
            self.logger.warning("Fallback scraping not implemented yet")
            return []
            
        except Exception as e:
            self.logger.error(f"Fallback scraping failed: {e}")
            return []