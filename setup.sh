#!/bin/bash
# Setup script for Chatbot Performance Testing

set -e

echo "=========================================="
echo "Chatbot Performance Testing Setup"
echo "=========================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo "Please install Python 3.7 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
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

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env file with your configuration"
else
    echo "✅ .env file already exists"
fi

# Create reports directory
mkdir -p reports
echo "✅ Reports directory created"

# Make scripts executable
chmod +x scripts/run_tests.py
chmod +x aws_setup/*.sh 2>/dev/null || true
chmod +x aws_setup/*.py 2>/dev/null || true

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your chatbot configuration"
echo "2. If using AWS, run: ./aws_setup/setup_aws.sh"
echo "3. Activate virtual environment: source venv/bin/activate"
echo "4. Run tests: python scripts/run_tests.py load"
echo ""
echo "For detailed instructions, see README.md"
echo "=========================================="
