#!/usr/bin/env python3
"""
Configuration utility for AWS Community Dashboard scraper
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any


class ScraperConfigurator:
    """Interactive configuration utility"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_default_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load existing config or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"Error loading existing config: {e}")
        
        # Return default config if file doesn't exist or can't be loaded
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'general': {
                'output_dir': '../data',
                'static_output_dir': '../static/data',
                'backup_dir': '../data/backups',
                'log_level': 'INFO',
                'max_retries': 3,
                'request_delay': 1
            },
            'data_sources': {
                'aws_heroes': {
                    'enabled': True,
                    'url': 'https://aws.amazon.com/developer/community/heroes/',
                    'output_file': 'aws_heroes.csv',
                    'complete_output_file': 'aws_heroes_final_clean.csv',
                    'update_frequency': 'daily'
                },
                'community_builders': {
                    'enabled': True,
                    'search_endpoint': 'https://aws.amazon.com/api/dirs/items/search',
                    'output_file': 'aws_community_builders.csv',
                    'complete_output_file': 'community_builders_complete.csv',
                    'update_frequency': 'daily',
                    'search_params': {
                        'item_type': 'community-builder',
                        'sort_by': 'item.additionalFields.sortableTitle',
                        'sort_order': 'asc',
                        'size': 2000
                    }
                },
                'user_groups': {
                    'enabled': True,
                    'meetup_api_key': '',
                    'output_file': 'aws_user_groups.csv',
                    'complete_output_file': 'aws_user_groups_with_members.csv',
                    'update_frequency': 'weekly',
                    'search_terms': ['AWS', 'Amazon Web Services', 'Cloud Computing']
                }
            },
            'geocoding': {
                'enabled': True,
                'service': 'nominatim',
                'api_key': '',
                'cache_results': True,
                'cache_file': 'geocoding_cache.json',
                'rate_limit': 1
            },
            'validation': {
                'required_fields': {
                    'heroes': ['Name', 'Location', 'Category', 'Bio URL'],
                    'builders': ['Name', 'Location', 'Category'],
                    'user_groups': ['Name', 'Location', 'URL', 'Category']
                },
                'min_records': {
                    'heroes': 100,
                    'builders': 500,
                    'user_groups': 200
                }
            },
            'git': {
                'enabled': True,
                'auto_commit': True,
                'commit_message': 'Automated data update - {timestamp}',
                'branch': 'main'
            },
            'schedule': {
                'enabled': False,
                'heroes_time': '06:00',
                'builders_time': '07:00',
                'user_groups_time': '08:00',
                'timezone': 'UTC'
            }
        }
    
    def interactive_setup(self):
        """Run interactive configuration setup"""
        print("AWS Community Dashboard Scraper Configuration")
        print("=" * 50)
        print()
        
        # General settings
        self._configure_general()
        
        # Data sources
        self._configure_data_sources()
        
        # Geocoding
        self._configure_geocoding()
        
        # Git integration
        self._configure_git()
        
        # Scheduling
        self._configure_scheduling()
        
        # Save configuration
        self._save_config()
        
        print("\nConfiguration completed successfully!")
        print(f"Settings saved to: {self.config_path}")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Test the scraper: python main.py --source heroes")
        print("3. Run full scraping: python main.py")
    
    def _configure_general(self):
        """Configure general settings"""
        print("General Settings")
        print("-" * 20)
        
        # Log level
        log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        current_level = self.config['general']['log_level']
        print(f"Current log level: {current_level}")
        
        new_level = self._get_choice("Select log level", log_levels, current_level)
        self.config['general']['log_level'] = new_level
        
        # Request delay
        current_delay = self.config['general']['request_delay']
        new_delay = self._get_number(f"Request delay in seconds (current: {current_delay})", 
                                   current_delay, min_val=0, max_val=10)
        self.config['general']['request_delay'] = new_delay
        
        print()
    
    def _configure_data_sources(self):
        """Configure data sources"""
        print("Data Sources Configuration")
        print("-" * 30)
        
        for source_name in ['aws_heroes', 'community_builders', 'user_groups']:
            source_config = self.config['data_sources'][source_name]
            
            print(f"\n{source_name.replace('_', ' ').title()}:")
            
            # Enable/disable source
            current_enabled = source_config['enabled']
            enabled = self._get_yes_no(f"Enable {source_name}", current_enabled)
            source_config['enabled'] = enabled
            
            if enabled:
                # Update frequency
                frequencies = ['daily', 'weekly', 'monthly']
                current_freq = source_config.get('update_frequency', 'daily')
                new_freq = self._get_choice("Update frequency", frequencies, current_freq)
                source_config['update_frequency'] = new_freq
                
                # Source-specific configuration
                if source_name == 'user_groups':
                    api_key = self._get_string("Meetup API key (optional)", 
                                             source_config.get('meetup_api_key', ''))
                    source_config['meetup_api_key'] = api_key
        
        print()
    
    def _configure_geocoding(self):
        """Configure geocoding settings"""
        print("Geocoding Configuration")
        print("-" * 25)
        
        # Enable geocoding
        current_enabled = self.config['geocoding']['enabled']
        enabled = self._get_yes_no("Enable geocoding", current_enabled)
        self.config['geocoding']['enabled'] = enabled
        
        if enabled:
            # Geocoding service
            services = ['nominatim']  # Could add more services later
            current_service = self.config['geocoding']['service']
            service = self._get_choice("Geocoding service", services, current_service)
            self.config['geocoding']['service'] = service
            
            # Rate limit
            current_rate = self.config['geocoding']['rate_limit']
            rate_limit = self._get_number(f"Rate limit (requests per second, current: {current_rate})", 
                                        current_rate, min_val=0.1, max_val=10)
            self.config['geocoding']['rate_limit'] = rate_limit
        
        print()
    
    def _configure_git(self):
        """Configure Git integration"""
        print("Git Integration")
        print("-" * 15)
        
        # Enable Git integration
        current_enabled = self.config['git']['enabled']
        enabled = self._get_yes_no("Enable Git integration", current_enabled)
        self.config['git']['enabled'] = enabled
        
        if enabled:
            # Auto commit
            current_auto = self.config['git']['auto_commit']
            auto_commit = self._get_yes_no("Enable auto-commit", current_auto)
            self.config['git']['auto_commit'] = auto_commit
            
            if auto_commit:
                # Commit message
                current_message = self.config['git']['commit_message']
                message = self._get_string("Commit message template", current_message)
                self.config['git']['commit_message'] = message
        
        print()
    
    def _configure_scheduling(self):
        """Configure scheduling"""
        print("Scheduling Configuration")
        print("-" * 25)
        
        # Enable scheduling
        current_enabled = self.config['schedule']['enabled']
        enabled = self._get_yes_no("Enable background scheduling", current_enabled)
        self.config['schedule']['enabled'] = enabled
        
        if enabled:
            print("Set scraping times (24-hour format, e.g., 06:00):")
            
            for source in ['heroes', 'builders', 'user_groups']:
                time_key = f"{source}_time"
                current_time = self.config['schedule'][time_key]
                new_time = self._get_string(f"{source.title()} scraping time", current_time)
                self.config['schedule'][time_key] = new_time
        
        print()
    
    def _get_yes_no(self, prompt: str, default: bool = True) -> bool:
        """Get yes/no input from user"""
        default_str = "Y/n" if default else "y/N"
        while True:
            response = input(f"{prompt} [{default_str}]: ").strip().lower()
            
            if not response:
                return default
            elif response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
    
    def _get_choice(self, prompt: str, choices: list, default: str = None) -> str:
        """Get choice from list"""
        print(f"\n{prompt}:")
        for i, choice in enumerate(choices, 1):
            marker = " (current)" if choice == default else ""
            print(f"  {i}. {choice}{marker}")
        
        while True:
            try:
                response = input(f"Select option [1-{len(choices)}]: ").strip()
                
                if not response and default:
                    return default
                
                index = int(response) - 1
                if 0 <= index < len(choices):
                    return choices[index]
                else:
                    print(f"Please enter a number between 1 and {len(choices)}")
            except ValueError:
                print("Please enter a valid number")
    
    def _get_string(self, prompt: str, default: str = "") -> str:
        """Get string input from user"""
        default_display = f" (current: {default})" if default else ""
        response = input(f"{prompt}{default_display}: ").strip()
        return response if response else default
    
    def _get_number(self, prompt: str, default: float, min_val: float = None, max_val: float = None) -> float:
        """Get numeric input from user"""
        while True:
            try:
                response = input(f"{prompt}: ").strip()
                
                if not response:
                    return default
                
                value = float(response)
                
                if min_val is not None and value < min_val:
                    print(f"Value must be at least {min_val}")
                    continue
                
                if max_val is not None and value > max_val:
                    print(f"Value must be at most {max_val}")
                    continue
                
                return value
                
            except ValueError:
                print("Please enter a valid number")
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            
        except Exception as e:
            print(f"Error saving configuration: {e}")
            sys.exit(1)
    
    def validate_config(self) -> bool:
        """Validate current configuration"""
        print("Validating configuration...")
        
        errors = []
        
        # Check required sections
        required_sections = ['general', 'data_sources', 'geocoding', 'git', 'schedule']
        for section in required_sections:
            if section not in self.config:
                errors.append(f"Missing required section: {section}")
        
        # Check data sources
        for source_name in ['aws_heroes', 'community_builders', 'user_groups']:
            if source_name not in self.config.get('data_sources', {}):
                errors.append(f"Missing data source configuration: {source_name}")
        
        # Check output directories exist
        output_dirs = [
            self.config.get('general', {}).get('output_dir', '../data'),
            self.config.get('general', {}).get('static_output_dir', '../static/data')
        ]
        
        for output_dir in output_dirs:
            if not Path(output_dir).exists():
                print(f"Warning: Output directory does not exist: {output_dir}")
        
        if errors:
            print("Configuration errors found:")
            for error in errors:
                print(f"  - {error}")
            return False
        else:
            print("Configuration is valid!")
            return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Configure AWS Community Dashboard Scraper')
    parser.add_argument('--config', '-c', default='config/settings.yaml',
                       help='Path to configuration file')
    parser.add_argument('--validate', action='store_true',
                       help='Validate existing configuration')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run interactive configuration')
    
    args = parser.parse_args()
    
    configurator = ScraperConfigurator(args.config)
    
    if args.validate:
        configurator.validate_config()
    elif args.interactive:
        configurator.interactive_setup()
    else:
        print("Use --interactive to run configuration setup or --validate to check existing config")


if __name__ == '__main__':
    main()