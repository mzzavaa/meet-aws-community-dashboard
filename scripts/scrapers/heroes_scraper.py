"""
AWS Heroes scraper for AWS Community Dashboard
"""

import re
import pandas as pd
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from urllib.parse import urljoin

from .base_scraper import BaseScraper


class HeroesScraper(BaseScraper):
    """Scraper for AWS Heroes data"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('data_sources', {}).get('aws_heroes', {}).get('url', 
                                   'https://aws.amazon.com/developer/community/heroes/')
    
    def get_data_type(self) -> str:
        return "heroes"
    
    def scrape(self) -> pd.DataFrame:
        """
        Scrape AWS Heroes data from the official directory
        
        Returns:
            DataFrame with heroes data
        """
        self.logger.info("Starting AWS Heroes scraping...")
        
        try:
            # Get the main heroes page
            response = self.make_request(self.base_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find hero cards/links
            heroes_data = []
            hero_links = self._extract_hero_links(soup)
            
            self.logger.info(f"Found {len(hero_links)} hero profiles to scrape")
            
            # Scrape each hero's detailed page
            for i, hero_link in enumerate(hero_links):
                if i % 10 == 0:
                    self.logger.info(f"Scraping hero {i+1}/{len(hero_links)}")
                
                try:
                    hero_data = self._scrape_hero_details(hero_link)
                    if hero_data:
                        heroes_data.append(hero_data)
                except Exception as e:
                    self.logger.error(f"Error scraping hero {hero_link}: {e}")
                    continue
            
            # Convert to DataFrame
            df = pd.DataFrame(heroes_data)
            
            if df.empty:
                self.logger.error("No heroes data scraped")
                return df
            
            self.logger.info(f"Successfully scraped {len(df)} heroes")
            
            # Process the data
            df_processed = self.process_data(df)
            
            return df_processed
            
        except Exception as e:
            self.logger.error(f"Error in heroes scraping: {e}")
            return pd.DataFrame()
    
    def _extract_hero_links(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract hero profile links from the main page
        
        Args:
            soup: BeautifulSoup object of the main heroes page
            
        Returns:
            List of hero profile URLs
        """
        hero_links = []
        
        # Look for hero cards - these patterns may need adjustment based on actual HTML structure
        # Common patterns for AWS hero pages
        selectors = [
            'a[href*="/developer/community/heroes/"]',
            '.hero-card a',
            '.community-hero a',
            '[data-hero-name] a'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            if links:
                self.logger.debug(f"Found {len(links)} links with selector: {selector}")
                for link in links:
                    href = link.get('href')
                    if href and '/developer/community/heroes/' in href:
                        full_url = urljoin(self.base_url, href)
                        if full_url not in hero_links:
                            hero_links.append(full_url)
                break  # Use first successful selector
        
        # Fallback: look for any links containing hero names or IDs
        if not hero_links:
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                if '/developer/community/heroes/' in href and '?' not in href:
                    full_url = urljoin(self.base_url, href)
                    if full_url not in hero_links:
                        hero_links.append(full_url)
        
        return hero_links
    
    def _scrape_hero_details(self, hero_url: str) -> Dict[str, Any]:
        """
        Scrape detailed information from a hero's profile page
        
        Args:
            hero_url: URL of the hero's profile page
            
        Returns:
            Dictionary with hero data
        """
        try:
            response = self.make_request(hero_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            hero_data = {
                'Bio URL': hero_url
            }
            
            # Extract name
            name_selectors = [
                'h1',
                '.hero-name',
                '.profile-name',
                '[data-hero-name]'
            ]
            hero_data['Name'] = self._extract_text_by_selectors(soup, name_selectors)
            
            # Extract location
            location_selectors = [
                '.hero-location',
                '.location',
                '[data-location]',
                'span:contains("Location")',
                'div:contains("Location")'
            ]
            hero_data['Location'] = self._extract_text_by_selectors(soup, location_selectors)
            
            # Extract category
            category_selectors = [
                '.hero-category',
                '.category',
                '[data-category]',
                'span:contains("Hero")',
                'div:contains("Hero")'
            ]
            hero_data['Category'] = self._extract_text_by_selectors(soup, category_selectors)
            
            # Extract since date
            since_selectors = [
                '.hero-since',
                '.since-date',
                'span:contains("since")',
                'div:contains("since")'
            ]
            hero_data['Since Date'] = self._extract_text_by_selectors(soup, since_selectors)
            
            # Extract description/bio
            desc_selectors = [
                '.hero-bio',
                '.hero-description',
                '.bio',
                '.description',
                'p'
            ]
            hero_data['Description'] = self._extract_text_by_selectors(soup, desc_selectors)
            
            # Extract image URL
            img_selectors = [
                '.hero-image img',
                '.profile-image img',
                '.hero-photo img',
                'img[alt*="hero"]',
                'img[src*="hero"]'
            ]
            hero_data['Image URL'] = self._extract_image_url(soup, img_selectors)
            
            # Extract tags/specialties
            tags_selectors = [
                '.hero-tags',
                '.specialties',
                '.skills',
                '.tags'
            ]
            hero_data['Tags'] = self._extract_text_by_selectors(soup, tags_selectors)
            
            # Clean up the data
            hero_data = self._clean_hero_data(hero_data)
            
            return hero_data
            
        except Exception as e:
            self.logger.error(f"Error scraping hero details from {hero_url}: {e}")
            return {}
    
    def _extract_text_by_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        """
        Extract text using multiple CSS selectors as fallbacks
        
        Args:
            soup: BeautifulSoup object
            selectors: List of CSS selectors to try
            
        Returns:
            Extracted text or empty string
        """
        for selector in selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    text = elements[0].get_text(strip=True)
                    if text:
                        return text
            except Exception:
                continue
        return ""
    
    def _extract_image_url(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        """
        Extract image URL using multiple CSS selectors
        
        Args:
            soup: BeautifulSoup object
            selectors: List of CSS selectors to try
            
        Returns:
            Image URL or empty string
        """
        for selector in selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    src = elements[0].get('src')
                    if src:
                        return urljoin(self.base_url, src)
            except Exception:
                continue
        return ""
    
    def _clean_hero_data(self, hero_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and standardize hero data
        
        Args:
            hero_data: Raw hero data dictionary
            
        Returns:
            Cleaned hero data dictionary
        """
        # Clean name
        if hero_data.get('Name'):
            hero_data['Name'] = re.sub(r'\s+', ' ', hero_data['Name']).strip()
        
        # Clean location
        if hero_data.get('Location'):
            location = hero_data['Location']
            # Remove common prefixes
            location = re.sub(r'^(Location:?\s*)', '', location, flags=re.IGNORECASE)
            hero_data['Location'] = location.strip()
        
        # Clean category
        if hero_data.get('Category'):
            category = hero_data['Category']
            # Ensure it contains "Hero"
            if 'Hero' not in category:
                category = f"AWS {category} Hero"
            hero_data['Category'] = category
        
        # Clean since date
        if hero_data.get('Since Date'):
            since_date = hero_data['Since Date']
            # Extract year if present
            year_match = re.search(r'(\d{4})', since_date)
            if year_match:
                hero_data['Since Date'] = f"Hero since {year_match.group(1)}"
        
        # Clean description
        if hero_data.get('Description'):
            desc = hero_data['Description']
            # Limit description length
            if len(desc) > 500:
                desc = desc[:497] + "..."
            hero_data['Description'] = desc
        
        # Set default values for missing fields
        hero_data.setdefault('Status', '')
        hero_data.setdefault('Video', '')
        hero_data.setdefault('Latitude', None)
        hero_data.setdefault('Longitude', None)
        
        return hero_data