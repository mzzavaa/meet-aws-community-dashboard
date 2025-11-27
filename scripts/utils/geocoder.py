"""
Geocoding utility for converting locations to coordinates
"""

import json
import time
from pathlib import Path
from typing import Tuple, Optional, Dict

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from .logger import get_logger


class Geocoder:
    """Geocoding utility with caching and rate limiting"""
    
    def __init__(self, service="nominatim", api_key=None, cache_file="geocoding_cache.json", rate_limit=1):
        self.service = service
        self.api_key = api_key
        self.cache_file = Path(cache_file)
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.logger = get_logger("geocoder")
        
        # Load cache
        self.cache = self._load_cache()
        
        # Initialize geocoder
        if service == "nominatim":
            self.geocoder = Nominatim(user_agent="aws_community_dashboard")
        else:
            raise ValueError(f"Unsupported geocoding service: {service}")
    
    def _load_cache(self) -> Dict:
        """Load geocoding cache from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"Could not load geocoding cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save geocoding cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except IOError as e:
            self.logger.error(f"Could not save geocoding cache: {e}")
    
    def _rate_limit_wait(self):
        """Implement rate limiting"""
        if self.rate_limit > 0:
            time_since_last = time.time() - self.last_request_time
            min_interval = 1.0 / self.rate_limit
            if time_since_last < min_interval:
                time.sleep(min_interval - time_since_last)
        self.last_request_time = time.time()
    
    def geocode(self, location: str, max_retries: int = 3) -> Tuple[Optional[float], Optional[float]]:
        """
        Geocode a location string to latitude and longitude
        
        Args:
            location: Location string to geocode
            max_retries: Maximum number of retry attempts
            
        Returns:
            Tuple of (latitude, longitude) or (None, None) if failed
        """
        if not location or location.strip() == "":
            return None, None
        
        # Normalize location for cache key
        cache_key = location.strip().lower()
        
        # Check cache first
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            return cached.get('lat'), cached.get('lng')
        
        # Geocode with retries
        for attempt in range(max_retries):
            try:
                self._rate_limit_wait()
                
                result = self.geocoder.geocode(location, timeout=10)
                
                if result:
                    lat, lng = result.latitude, result.longitude
                    
                    # Cache the result
                    self.cache[cache_key] = {
                        'lat': lat,
                        'lng': lng,
                        'display_name': result.address
                    }
                    self._save_cache()
                    
                    self.logger.debug(f"Geocoded '{location}' to ({lat}, {lng})")
                    return lat, lng
                else:
                    self.logger.warning(f"No results found for location: {location}")
                    break
                    
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                self.logger.warning(f"Geocoding attempt {attempt + 1} failed for '{location}': {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue
            except Exception as e:
                self.logger.error(f"Unexpected error geocoding '{location}': {e}")
                break
        
        # Cache negative result to avoid repeated failures
        self.cache[cache_key] = {'lat': None, 'lng': None}
        self._save_cache()
        
        return None, None
    
    def batch_geocode(self, locations: list, progress_callback=None) -> Dict[str, Tuple[Optional[float], Optional[float]]]:
        """
        Geocode multiple locations
        
        Args:
            locations: List of location strings
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dictionary mapping locations to (lat, lng) tuples
        """
        results = {}
        total = len(locations)
        
        for i, location in enumerate(locations):
            if progress_callback:
                progress_callback(i + 1, total, location)
            
            results[location] = self.geocode(location)
        
        return results
    
    def clean_location(self, location: str) -> str:
        """
        Clean and normalize location string
        
        Args:
            location: Raw location string
            
        Returns:
            Cleaned location string
        """
        if not location:
            return ""
        
        # Basic cleaning
        location = location.strip()
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = ["Remote", "Remote -", "Virtual", "Online"]
        for prefix in prefixes_to_remove:
            if location.startswith(prefix):
                location = location[len(prefix):].strip()
        
        # Handle "City, Country" format
        if "," in location:
            parts = [part.strip() for part in location.split(",")]
            # Remove empty parts
            parts = [part for part in parts if part]
            location = ", ".join(parts)
        
        return location