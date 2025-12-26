#!/bin/bash
# Quick setup script for Viral Video Processor

echo "Setting up Viral Video Processor..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Copy environment template
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.template .env
    echo "Please edit .env and add your ANTHROPIC_API_KEY"
fi

# Create directories
echo "Creating directories..."
mkdir -p downloads videos clips

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your ANTHROPIC_API_KEY"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python app.py --help"
echo ""
