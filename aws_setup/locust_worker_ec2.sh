#!/bin/bash
# Setup script for Locust Worker on EC2
# This sets up a Locust worker node for distributed load testing

set -e

echo "=========================================="
echo "Setting up Locust Worker on EC2"
echo "=========================================="

# Update system
sudo yum update -y || sudo apt-get update -y

# Install Python 3 and pip
if command -v yum &> /dev/null; then
    sudo yum install -y python3 python3-pip
elif command -v apt-get &> /dev/null; then
    sudo apt-get install -y python3 python3-pip
fi

# Install Locust
pip3 install locust pyyaml python-dotenv requests boto3

# Create directory for test files
mkdir -p /home/ec2-user/chatbot-performance-testing
cd /home/ec2-user/chatbot-performance-testing

# Download or copy your test files here
# You can use S3, git clone, or scp to transfer files

echo "=========================================="
echo "Locust Worker setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy your test files to this instance:"
echo "   - src/locustfile.py"
echo "   - config/test_config.yaml"
echo "   - src/sample_questions.py"
echo ""
echo "2. Start Locust worker (replace MASTER_IP with master's private IP):"
echo "   locust -f src/locustfile.py --worker --master-host=<MASTER_IP>"
echo "=========================================="
