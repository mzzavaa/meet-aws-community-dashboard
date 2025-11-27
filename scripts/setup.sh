#!/bin/bash

# Setup script for AWS Community Dashboard Scraper

set -e

echo "AWS Community Dashboard Scraper Setup"
echo "====================================="
echo

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python version: $python_version"

# Check if Python 3.8+ is available
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "Error: Python 3.8 or higher is required"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p config
mkdir -p ../data/backups

# Check if configuration exists
if [ ! -f "config/settings.yaml" ]; then
    echo "Configuration file not found. Running interactive setup..."
    python configure.py --interactive
else
    echo "Configuration file found. Validating..."
    python configure.py --validate
fi

# Test basic functionality
echo "Testing scraper functionality..."
python -c "
import sys
sys.path.insert(0, '.')
from utils.logger import get_logger
from utils.geocoder import Geocoder
from utils.data_validator import DataValidator

# Test logger
logger = get_logger('test')
logger.info('Logger test successful')

# Test geocoder
geocoder = Geocoder()
lat, lng = geocoder.geocode('New York, USA')
if lat and lng:
    print(f'Geocoder test successful: {lat}, {lng}')
else:
    print('Geocoder test failed - this is normal if no internet connection')

print('Basic functionality test completed')
"

echo
echo "Setup completed successfully!"
echo
echo "Next steps:"
echo "1. Configure your settings: python configure.py --interactive"
echo "2. Test a single data source: python main.py --source heroes"
echo "3. Run full scraping: python main.py"
echo "4. Set up GitHub Actions for automation (see .github/workflows/data-scraping.yml)"
echo
echo "For scheduling, you can also use cron:"
echo "# Add to crontab (crontab -e):"
echo "0 6 * * * cd $(pwd) && source venv/bin/activate && python main.py"
echo