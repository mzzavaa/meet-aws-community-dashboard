# Scripts Directory

This directory contains the automated data scraping and processing scripts for the AWS Community Dashboard.

## Structure

- `scrapers/` - Individual scraping modules for each data source
- `utils/` - Utility functions for data processing, geocoding, and validation
- `config/` - Configuration files for scraping parameters
- `logs/` - Log files for monitoring scraping activities
- `main.py` - Main orchestration script
- `requirements.txt` - Python dependencies

## Usage

1. Install dependencies: `pip install -r requirements.txt`
2. Configure settings in `config/settings.yaml`
3. Run the scraper: `python main.py`
4. Check logs in `logs/` directory for monitoring

## Automation

The scraper can be automated using cron jobs or GitHub Actions for regular data updates.