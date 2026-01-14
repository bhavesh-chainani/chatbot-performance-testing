#!/bin/bash
# AWS Setup Script for Chatbot Performance Testing
# This script helps set up AWS credentials and configuration

set -e

echo "=========================================="
echo "AWS Setup for Chatbot Performance Testing"
echo "=========================================="
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed."
    echo "Please install AWS CLI first:"
    echo "  macOS: brew install awscli"
    echo "  Linux: sudo apt-get install awscli"
    echo "  Or visit: https://aws.amazon.com/cli/"
    exit 1
fi

echo "✅ AWS CLI is installed"
echo ""

# Check if AWS credentials are configured
if [ ! -f ~/.aws/credentials ]; then
    echo "⚠️  AWS credentials not found."
    echo "Please configure AWS credentials:"
    echo "  aws configure"
    echo ""
    echo "You'll need:"
    echo "  - AWS Access Key ID"
    echo "  - AWS Secret Access Key"
    echo "  - Default region (e.g., us-east-1)"
    echo "  - Default output format (json)"
    echo ""
    read -p "Do you want to configure AWS credentials now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        aws configure
    else
        echo "Please run 'aws configure' manually before proceeding."
        exit 1
    fi
else
    echo "✅ AWS credentials found"
fi

echo ""
echo "Testing AWS connection..."
if aws sts get-caller-identity &> /dev/null; then
    echo "✅ AWS connection successful"
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=$(aws configure get region)
    echo "  Account ID: $AWS_ACCOUNT_ID"
    echo "  Region: $AWS_REGION"
else
    echo "❌ AWS connection failed. Please check your credentials."
    exit 1
fi

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo "1. Update your .env file with AWS-specific settings:"
echo "   - AWS_REGION=$AWS_REGION"
echo "   - AWS_API_GATEWAY_URL=<your-api-gateway-url>"
echo "   - CHATBOT_URL=<your-chatbot-url>"
echo ""
echo "2. If using AWS Cognito for authentication, add:"
echo "   - AWS_COGNITO_USER_POOL_ID=<your-user-pool-id>"
echo "   - AWS_COGNITO_CLIENT_ID=<your-client-id>"
echo "   - USE_AWS_COGNITO=true"
echo ""
echo "3. Run tests:"
echo "   python scripts/run_tests.py load"
echo ""
echo "For detailed instructions, see docs/AWS_SETUP.md"
echo "=========================================="
