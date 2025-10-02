#!/bin/bash

# Crypto Risk Alert System - Setup Script

set -e

echo "=========================================="
echo "Crypto Risk Alert System - Setup"
echo "=========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p logs
mkdir -p data
mkdir -p tmp

# Copy example config
echo ""
echo "Setting up configuration..."
if [ ! -f config/config.yml ]; then
    cp config/config.example.yml config/config.yml
    echo "✓ Created config/config.yml from example"
    echo "  Please edit config/config.yml with your API keys"
else
    echo "✓ config/config.yml already exists"
fi

# Initialize database (if needed)
echo ""
echo "Database setup..."
echo "  Run: python scripts/init_db.py (when available)"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit config/config.yml with your API keys"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the system: python src/main.py"
echo "4. Or run API server: python src/api/app.py"
echo "5. Or run bots:"
echo "   - Telegram: python src/bots/telegram_bot.py"
echo "   - Discord: python src/bots/discord_bot.py"
echo ""
echo "Run tests: pytest tests/"
echo ""
