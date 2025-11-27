#!/usr/bin/env python3
"""
Main orchestration script for AWS Community Dashboard data scraping
"""

import os
import sys
import yaml
import argparse
import schedule
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add the scripts directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import get_logger
from utils.data_validator import DataValidator
from scrapers.heroes_scraper import HeroesScraper
from scrapers.builders_scraper import BuildersScraper
from scrapers.user_groups_scraper import UserGroupsScraper


class DataScrapingOrchestrator:
    """Main orchestrator for data scraping operations"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.logger = get_logger("orchestrator", 
                               log_dir=self.config.get('general', {}).get('log_dir', 'logs'),
                               level=self.config.get('general', {}).get('log_level', 'INFO'))
        
        # Initialize scrapers
        self.scrapers = {
            'heroes': HeroesScraper(self.config),
            'builders': BuildersScraper(self.config),
            'user_groups': UserGroupsScraper(self.config)
        }
        
        # Setup output directories
        self._setup_directories()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"Error loading config from {self.config_path}: {e}")
            sys.exit(1)
    
    def _setup_directories(self):
        """Create necessary directories"""
        directories = [
            self.config.get('general', {}).get('output_dir', '../data'),
            self.config.get('general', {}).get('static_output_dir', '../static/data'),
            self.config.get('general', {}).get('backup_dir', '../data/backups'),
            'logs'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def scrape_data_source(self, source_name: str) -> bool:
        """
        Scrape data from a specific source
        
        Args:
            source_name: Name of the data source (heroes, builders, user_groups)
            
        Returns:
            True if successful, False otherwise
        """
        if source_name not in self.scrapers:
            self.logger.error(f"Unknown data source: {source_name}")
            return False
        
        # Check if source is enabled
        source_config = self.config.get('data_sources', {}).get(source_name, {})
        if not source_config.get('enabled', True):
            self.logger.info(f"Data source {source_name} is disabled, skipping...")
            return True
        
        self.logger.info(f"Starting scraping for {source_name}...")
        
        try:
            # Backup existing data
            self._backup_existing_data(source_name)
            
            # Scrape new data
            scraper = self.scrapers[source_name]
            df = scraper.scrape()
            
            if df.empty:
                self.logger.error(f"No data scraped for {source_name}")
                return False
            
            # Save data
            success = self._save_data(source_name, df)
            
            if success:
                self.logger.info(f"Successfully completed scraping for {source_name}: {len(df)} records")
                
                # Commit to git if enabled
                if self.config.get('git', {}).get('enabled', False):
                    self._commit_changes(source_name)
                
                return True
            else:
                self.logger.error(f"Failed to save data for {source_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error scraping {source_name}: {e}")
            return False
    
    def _backup_existing_data(self, source_name: str):
        """Backup existing data files"""
        try:
            backup_dir = Path(self.config.get('general', {}).get('backup_dir', '../data/backups'))
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            source_config = self.config.get('data_sources', {}).get(source_name, {})
            output_files = [
                source_config.get('output_file', ''),
                source_config.get('complete_output_file', '')
            ]
            
            for output_file in output_files:
                if not output_file:
                    continue
                
                # Backup from both directories
                for base_dir in ['../data', '../static/data']:
                    file_path = Path(base_dir) / output_file
                    if file_path.exists():
                        backup_path = backup_dir / f"{source_name}_{output_file}_{timestamp}"
                        backup_path.write_bytes(file_path.read_bytes())
                        self.logger.debug(f"Backed up {file_path} to {backup_path}")
        
        except Exception as e:
            self.logger.warning(f"Error backing up data for {source_name}: {e}")
    
    def _save_data(self, source_name: str, df) -> bool:
        """Save scraped data to files"""
        try:
            source_config = self.config.get('data_sources', {}).get(source_name, {})
            
            # Output directories
            output_dir = Path(self.config.get('general', {}).get('output_dir', '../data'))
            static_output_dir = Path(self.config.get('general', {}).get('static_output_dir', '../static/data'))
            
            # File names
            complete_file = source_config.get('complete_output_file', f'{source_name}_complete.csv')
            simple_file = source_config.get('output_file', f'{source_name}.csv')
            
            # Save complete data to /data directory
            complete_path = output_dir / complete_file
            df.to_csv(complete_path, index=False, encoding='utf-8')
            self.logger.info(f"Saved complete data to {complete_path}")
            
            # Create simplified version for /static/data directory
            df_simple = self._create_simple_version(df, source_name)
            simple_path = static_output_dir / simple_file
            df_simple.to_csv(simple_path, index=False, encoding='utf-8')
            self.logger.info(f"Saved simple data to {simple_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving data for {source_name}: {e}")
            return False
    
    def _create_simple_version(self, df, source_name: str):
        """Create simplified version of data for the website"""
        # Keep only essential columns for the website
        if source_name == 'heroes':
            essential_columns = ['Name', 'Location', 'Category', 'Bio URL', 'Since Date', 
                               'Description', 'Image URL', 'Tags', 'Latitude', 'Longitude', 'Status', 'Video']
        elif source_name == 'builders':
            essential_columns = ['Name', 'Location', 'Category', 'Bio URL', 'Latitude', 'Longitude']
        elif source_name == 'user_groups':
            essential_columns = ['Name', 'Location', 'URL', 'Category', 'Latitude', 'Longitude', 
                               'Platform', 'Members', 'GroupImage']
        else:
            return df
        
        # Filter to only existing columns
        available_columns = [col for col in essential_columns if col in df.columns]
        return df[available_columns].copy()
    
    def _commit_changes(self, source_name: str):
        """Commit changes to git repository"""
        try:
            import subprocess
            
            git_config = self.config.get('git', {})
            if not git_config.get('auto_commit', False):
                return
            
            # Add files
            subprocess.run(['git', 'add', 'data/', 'static/data/'], 
                         cwd='..', check=True, capture_output=True)
            
            # Commit with timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_message = git_config.get('commit_message', 'Automated data update - {timestamp}')
            commit_message = commit_message.format(timestamp=timestamp, source=source_name)
            
            subprocess.run(['git', 'commit', '-m', commit_message], 
                         cwd='..', check=True, capture_output=True)
            
            self.logger.info(f"Committed changes for {source_name}")
            
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Git commit failed: {e}")
        except Exception as e:
            self.logger.error(f"Error committing changes: {e}")
    
    def scrape_all(self) -> bool:
        """Scrape all enabled data sources"""
        self.logger.info("Starting full data scraping...")
        
        results = {}
        for source_name in ['heroes', 'builders', 'user_groups']:
            results[source_name] = self.scrape_data_source(source_name)
        
        # Summary
        successful = sum(results.values())
        total = len(results)
        
        self.logger.info(f"Scraping completed: {successful}/{total} sources successful")
        
        if successful == total:
            self.logger.info("All data sources scraped successfully!")
            return True
        else:
            failed_sources = [name for name, success in results.items() if not success]
            self.logger.error(f"Failed sources: {failed_sources}")
            return False
    
    def setup_scheduling(self):
        """Setup scheduled scraping"""
        schedule_config = self.config.get('schedule', {})
        
        if not schedule_config.get('enabled', False):
            self.logger.info("Scheduling is disabled")
            return
        
        # Schedule individual sources
        heroes_time = schedule_config.get('heroes_time', '06:00')
        builders_time = schedule_config.get('builders_time', '07:00')
        user_groups_time = schedule_config.get('user_groups_time', '08:00')
        
        schedule.every().day.at(heroes_time).do(self.scrape_data_source, 'heroes')
        schedule.every().day.at(builders_time).do(self.scrape_data_source, 'builders')
        schedule.every().day.at(user_groups_time).do(self.scrape_data_source, 'user_groups')
        
        self.logger.info(f"Scheduled scraping: Heroes at {heroes_time}, Builders at {builders_time}, User Groups at {user_groups_time}")
    
    def run_scheduler(self):
        """Run the scheduler loop"""
        self.setup_scheduling()
        
        self.logger.info("Starting scheduler loop...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AWS Community Dashboard Data Scraper')
    parser.add_argument('--config', '-c', default='config/settings.yaml',
                       help='Path to configuration file')
    parser.add_argument('--source', '-s', choices=['heroes', 'builders', 'user_groups', 'all'],
                       default='all', help='Data source to scrape')
    parser.add_argument('--schedule', action='store_true',
                       help='Run in scheduling mode')
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = DataScrapingOrchestrator(args.config)
    
    if args.schedule:
        # Run scheduler
        orchestrator.run_scheduler()
    elif args.source == 'all':
        # Scrape all sources
        success = orchestrator.scrape_all()
        sys.exit(0 if success else 1)
    else:
        # Scrape specific source
        success = orchestrator.scrape_data_source(args.source)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()