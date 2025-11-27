"""
Base scraper class for AWS Community Dashboard
"""

import time
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd

from ..utils.logger import get_logger
from ..utils.geocoder import Geocoder
from ..utils.data_validator import DataValidator


class BaseScraper(ABC):
    """Base class for all scrapers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger(self.__class__.__name__.lower())
        self.geocoder = Geocoder(
            service=config.get('geocoding', {}).get('service', 'nominatim'),
            api_key=config.get('geocoding', {}).get('api_key'),
            cache_file=config.get('geocoding', {}).get('cache_file', 'geocoding_cache.json'),
            rate_limit=config.get('geocoding', {}).get('rate_limit', 1)
        )
        self.validator = DataValidator(config)
        
        # Request settings
        self.max_retries = config.get('general', {}).get('max_retries', 3)
        self.request_delay = config.get('general', {}).get('request_delay', 1)
        
        # Setup session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    @abstractmethod
    def scrape(self) -> pd.DataFrame:
        """
        Main scraping method to be implemented by subclasses
        
        Returns:
            DataFrame with scraped data
        """
        pass
    
    @abstractmethod
    def get_data_type(self) -> str:
        """
        Get the data type identifier for this scraper
        
        Returns:
            String identifier (heroes, builders, user_groups)
        """
        pass
    
    def make_request(self, url: str, params: Dict = None, headers: Dict = None) -> requests.Response:
        """
        Make HTTP request with retry logic
        
        Args:
            url: URL to request
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: If all retries fail
        """
        if headers:
            session_headers = self.session.headers.copy()
            session_headers.update(headers)
        else:
            session_headers = self.session.headers
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Making request to {url} (attempt {attempt + 1})")
                
                response = self.session.get(
                    url, 
                    params=params, 
                    headers=session_headers,
                    timeout=30
                )
                response.raise_for_status()
                
                # Rate limiting
                if self.request_delay > 0:
                    time.sleep(self.request_delay)
                
                return response
                
            except requests.RequestException as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"All {self.max_retries} attempts failed for {url}")
                    raise
    
    def add_coordinates(self, df: pd.DataFrame, location_column: str = 'Location') -> pd.DataFrame:
        """
        Add latitude and longitude coordinates to DataFrame
        
        Args:
            df: DataFrame with location data
            location_column: Name of the location column
            
        Returns:
            DataFrame with added Latitude and Longitude columns
        """
        if location_column not in df.columns:
            self.logger.warning(f"Location column '{location_column}' not found in DataFrame")
            return df
        
        # Skip if coordinates already exist
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            self.logger.info("Coordinates already exist, skipping geocoding")
            return df
        
        self.logger.info(f"Adding coordinates for {len(df)} records...")
        
        # Get unique locations to minimize API calls
        unique_locations = df[location_column].dropna().unique()
        self.logger.info(f"Geocoding {len(unique_locations)} unique locations...")
        
        # Geocode locations
        location_coords = {}
        for i, location in enumerate(unique_locations):
            if i % 10 == 0:  # Progress update every 10 locations
                self.logger.info(f"Geocoding progress: {i}/{len(unique_locations)}")
            
            cleaned_location = self.geocoder.clean_location(location)
            lat, lng = self.geocoder.geocode(cleaned_location)
            location_coords[location] = (lat, lng)
        
        # Add coordinates to DataFrame
        df['Latitude'] = df[location_column].map(lambda x: location_coords.get(x, (None, None))[0])
        df['Longitude'] = df[location_column].map(lambda x: location_coords.get(x, (None, None))[1])
        
        # Count successful geocoding
        geocoded_count = df['Latitude'].notna().sum()
        self.logger.info(f"Successfully geocoded {geocoded_count}/{len(df)} records")
        
        return df
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate scraped data
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if validation passes, False otherwise
        """
        is_valid, errors = self.validator.validate_dataframe(df, self.get_data_type())
        
        if not is_valid:
            self.logger.error(f"Data validation failed for {self.get_data_type()}:")
            for error in errors:
                self.logger.error(f"  - {error}")
        
        return is_valid
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize scraped data
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        return self.validator.clean_dataframe(df, self.get_data_type())
    
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Complete data processing pipeline
        
        Args:
            df: Raw scraped DataFrame
            
        Returns:
            Processed DataFrame ready for output
        """
        self.logger.info(f"Processing {len(df)} raw records...")
        
        # Clean data
        df_clean = self.clean_data(df)
        
        # Add coordinates if geocoding is enabled
        if self.config.get('geocoding', {}).get('enabled', True):
            df_clean = self.add_coordinates(df_clean)
        
        # Validate final data
        if not self.validate_data(df_clean):
            self.logger.warning("Data validation failed, but continuing with available data")
        
        self.logger.info(f"Processing complete: {len(df_clean)} records ready")
        
        return df_clean