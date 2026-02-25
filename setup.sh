#!/bin/bash
# Local setup for Chatbot Performance Testing

set -e

echo "=========================================="
echo "Chatbot Performance Testing Setup"
echo "=========================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python $PYTHON_VERSION found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
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

# Create reports directory
mkdir -p reports
echo "Reports directory ready"

# Make scripts executable
chmod +x aws_setup/*.sh 2>/dev/null || true

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env with your chatbot credentials"
echo "2. Activate venv: source venv/bin/activate"
echo "3. Run a test: TEST_TYPE=load locust -f src/locustfile.py"
echo "4. Open http://localhost:8089"
echo ""
echo "For AWS deployment, see SIMPLE_SETUP.md"
echo "=========================================="
