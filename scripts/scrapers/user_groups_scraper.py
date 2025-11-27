"""
AWS User Groups scraper for AWS Community Dashboard
"""

import json
import pandas as pd
from typing import Dict, Any, List
import requests
from urllib.parse import quote

from .base_scraper import BaseScraper


class UserGroupsScraper(BaseScraper):
    """Scraper for AWS User Groups data from Meetup.com"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.meetup_api_key = config.get('data_sources', {}).get('user_groups', {}).get('meetup_api_key', '')
        self.search_terms = config.get('data_sources', {}).get('user_groups', {}).get('search_terms', 
                                      ['AWS', 'Amazon Web Services', 'Cloud Computing'])
        
        # Meetup API endpoints
        self.find_groups_url = "https://api.meetup.com/find/groups"
        self.group_details_url = "https://api.meetup.com/{urlname}"
    
    def get_data_type(self) -> str:
        return "user_groups"
    
    def scrape(self) -> pd.DataFrame:
        """
        Scrape AWS User Groups data from Meetup.com
        
        Returns:
            DataFrame with user groups data
        """
        self.logger.info("Starting AWS User Groups scraping...")
        
        if not self.meetup_api_key:
            self.logger.warning("No Meetup API key provided, attempting alternative methods...")
            return self._scrape_without_api()
        
        try:
            all_groups = []
            
            # Search for groups using different terms
            for term in self.search_terms:
                self.logger.info(f"Searching for groups with term: {term}")
                groups = self._search_groups_by_term(term)
                all_groups.extend(groups)
            
            # Deduplicate groups
            unique_groups = self._deduplicate_groups(all_groups)
            
            # Get detailed information for each group
            detailed_groups = []
            for i, group in enumerate(unique_groups):
                if i % 10 == 0:
                    self.logger.info(f"Getting details for group {i+1}/{len(unique_groups)}")
                
                detailed_group = self._get_group_details(group)
                if detailed_group:
                    detailed_groups.append(detailed_group)
            
            # Convert to DataFrame
            df = pd.DataFrame(detailed_groups)
            
            if df.empty:
                self.logger.error("No user groups data scraped")
                return df
            
            self.logger.info(f"Successfully scraped {len(df)} user groups")
            
            # Process the data
            df_processed = self.process_data(df)
            
            return df_processed
            
        except Exception as e:
            self.logger.error(f"Error in user groups scraping: {e}")
            return pd.DataFrame()
    
    def _search_groups_by_term(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for groups using a specific term
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of group data dictionaries
        """
        try:
            params = {
                'key': self.meetup_api_key,
                'text': search_term,
                'category': '34',  # Tech category
                'radius': 'global',
                'page': 200  # Maximum results per request
            }
            
            response = self.make_request(self.find_groups_url, params=params)
            data = response.json()
            
            groups = []
            for group in data.get('data', []):
                group_data = self._parse_group_basic(group)
                if group_data and self._is_aws_related(group_data):
                    groups.append(group_data)
            
            self.logger.info(f"Found {len(groups)} AWS-related groups for term '{search_term}'")
            return groups
            
        except Exception as e:
            self.logger.error(f"Error searching groups for term '{search_term}': {e}")
            return []
    
    def _parse_group_basic(self, group: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse basic group information from search results
        
        Args:
            group: Raw group data from API
            
        Returns:
            Parsed group data dictionary
        """
        try:
            group_data = {
                'id': group.get('id'),
                'Name': group.get('name', ''),
                'urlname': group.get('urlname', ''),
                'URL': group.get('link', ''),
                'Members': group.get('members', 0),
                'Location': self._format_location(group),
                'Category': 'General AWS User Groups',
                'Platform': 'meetup',
                'GroupImage': ''
            }
            
            return group_data
            
        except Exception as e:
            self.logger.error(f"Error parsing basic group data: {e}")
            return {}
    
    def _format_location(self, group: Dict[str, Any]) -> str:
        """
        Format location from group data
        
        Args:
            group: Group data dictionary
            
        Returns:
            Formatted location string
        """
        location_parts = []
        
        # Get city
        city = group.get('city', '')
        if city:
            location_parts.append(city)
        
        # Get country
        country = group.get('country', '')
        if country:
            location_parts.append(country)
        
        # Get state/region if available
        state = group.get('state', '')
        if state and country == 'US':
            location_parts.insert(-1, state)  # Insert before country
        
        return ', '.join(location_parts) if location_parts else ''
    
    def _is_aws_related(self, group_data: Dict[str, Any]) -> bool:
        """
        Check if a group is AWS-related based on name and description
        
        Args:
            group_data: Group data dictionary
            
        Returns:
            True if group is AWS-related
        """
        name = group_data.get('Name', '').lower()
        
        # AWS-related keywords
        aws_keywords = [
            'aws', 'amazon web services', 'amazon cloud', 'cloud computing',
            'serverless', 'lambda', 'ec2', 'cloudformation', 's3'
        ]
        
        return any(keyword in name for keyword in aws_keywords)
    
    def _get_group_details(self, group: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed information for a specific group
        
        Args:
            group: Basic group data
            
        Returns:
            Detailed group data dictionary
        """
        try:
            urlname = group.get('urlname')
            if not urlname:
                return group
            
            url = self.group_details_url.format(urlname=urlname)
            params = {'key': self.meetup_api_key}
            
            response = self.make_request(url, params=params)
            details = response.json()
            
            # Update group data with detailed information
            group['Description'] = details.get('description', '')
            
            # Get group photo
            group_photo = details.get('group_photo', {})
            if group_photo:
                group['GroupImage'] = group_photo.get('photo_link', '')
            
            # Update member count
            group['Members'] = details.get('members', group.get('Members', 0))
            
            # Categorize based on description and name
            group['Category'] = self._categorize_group(group['Name'], group.get('Description', ''))
            
            return group
            
        except Exception as e:
            self.logger.error(f"Error getting group details for {group.get('urlname')}: {e}")
            return group
    
    def _categorize_group(self, name: str, description: str) -> str:
        """
        Categorize group based on name and description
        
        Args:
            name: Group name
            description: Group description
            
        Returns:
            Category string
        """
        text = f"{name} {description}".lower()
        
        # Category keywords
        categories = {
            'Serverless User Groups': ['serverless', 'lambda', 'faas', 'function'],
            'Container User Groups': ['container', 'docker', 'kubernetes', 'ecs', 'fargate'],
            'Machine Learning User Groups': ['machine learning', 'ml', 'ai', 'artificial intelligence', 'sagemaker'],
            'Data User Groups': ['data', 'analytics', 'big data', 'redshift', 'athena'],
            'Security User Groups': ['security', 'iam', 'compliance', 'governance'],
            'DevOps User Groups': ['devops', 'ci/cd', 'deployment', 'infrastructure']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'General AWS User Groups'
    
    def _deduplicate_groups(self, groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate groups based on ID or URL
        
        Args:
            groups: List of group data dictionaries
            
        Returns:
            Deduplicated list of groups
        """
        seen_ids = set()
        seen_urls = set()
        unique_groups = []
        
        for group in groups:
            group_id = group.get('id')
            group_url = group.get('URL', '').lower()
            
            # Check for duplicates
            if group_id and group_id in seen_ids:
                continue
            if group_url and group_url in seen_urls:
                continue
            
            # Add to unique list
            if group_id:
                seen_ids.add(group_id)
            if group_url:
                seen_urls.add(group_url)
            
            unique_groups.append(group)
        
        self.logger.info(f"Deduplicated {len(groups)} -> {len(unique_groups)} groups")
        
        return unique_groups
    
    def _scrape_without_api(self) -> pd.DataFrame:
        """
        Alternative scraping method without Meetup API
        This could use web scraping or other data sources
        
        Returns:
            DataFrame with user groups data
        """
        self.logger.info("Attempting to scrape user groups without API...")
        
        try:
            # For now, return existing data or implement web scraping
            # This is a placeholder for alternative data collection methods
            
            # Could implement:
            # 1. Web scraping from Meetup.com search results
            # 2. Using other event platforms (Eventbrite, Facebook Events, etc.)
            # 3. Manual curation from known AWS community resources
            
            self.logger.warning("Alternative scraping methods not implemented yet")
            return pd.DataFrame()
            
        except Exception as e:
            self.logger.error(f"Alternative scraping failed: {e}")
            return pd.DataFrame()