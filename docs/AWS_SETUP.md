# AWS Setup Guide for Chatbot Performance Testing

This guide will help you set up and configure AWS for chatbot performance testing.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Account Setup](#aws-account-setup)
3. [AWS CLI Installation](#aws-cli-installation)
4. [AWS Credentials Configuration](#aws-credentials-configuration)
5. [Identifying Your Chatbot Endpoint](#identifying-your-chatbot-endpoint)
6. [AWS Cognito Setup (Optional)](#aws-cognito-setup-optional)
7. [Configuration](#configuration)
8. [Running Tests](#running-tests)
9. [Cost Estimation](#cost-estimation)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

- AWS Account
- Python 3.7 or higher
- Basic understanding of AWS services

## AWS Account Setup

### 1. Create an AWS Account

If you don't have an AWS account:
1. Go to [AWS Sign Up](https://portal.aws.amazon.com/billing/signup)
2. Follow the registration process
3. Complete payment information (required even for free tier)

### 2. Create an IAM User (Recommended)

For security best practices, create an IAM user instead of using root credentials:

1. **Log in to AWS Console**
   - Go to https://console.aws.amazon.com
   - Sign in with your root account

2. **Navigate to IAM**
   - Search for "IAM" in the top search bar
   - Click on "IAM" service

3. **Create a New User**
   - Click "Users" in the left sidebar
   - Click "Add users"
   - Enter username: `chatbot-testing-user`
   - Select "Programmatic access"
   - Click "Next: Permissions"

4. **Attach Policies**
   - Select "Attach existing policies directly"
   - Add these policies (minimum required):
     - `AmazonAPIGatewayReadOnlyAccess` (to read API Gateway info)
     - `AmazonCognitoReadOnlyAccess` (if using Cognito)
     - `CloudWatchReadOnlyAccess` (to view metrics)
   - Click "Next: Tags" (optional)
   - Click "Next: Review"
   - Click "Create user"

5. **Save Credentials**
   - **IMPORTANT**: Copy the Access Key ID and Secret Access Key
   - Save them securely (you won't be able to see the secret key again)
   - Download the CSV file for backup

## AWS CLI Installation

### macOS

```bash
# Using Homebrew
brew install awscli

# Verify installation
aws --version
```

### Linux

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install awscli

# Verify installation
aws --version
```

### Windows

1. Download the AWS CLI MSI installer from: https://awscli.amazonaws.com/AWSCLIV2.msi
2. Run the installer
3. Follow the installation wizard
4. Verify installation: Open Command Prompt and run `aws --version`

## AWS Credentials Configuration

### Method 1: Using AWS Configure (Recommended)

```bash
aws configure
```

You'll be prompted for:
- **AWS Access Key ID**: Your IAM user's access key
- **AWS Secret Access Key**: Your IAM user's secret key
- **Default region name**: e.g., `us-east-1`, `us-west-2`, `eu-west-1`
- **Default output format**: `json`

Credentials are stored in `~/.aws/credentials` and `~/.aws/config`

### Method 2: Using Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your-access-key-id
export AWS_SECRET_ACCESS_KEY=your-secret-access-key
export AWS_DEFAULT_REGION=us-east-1
```

### Method 3: Using Named Profiles

```bash
aws configure --profile chatbot-testing
```

Then use the profile:
```bash
export AWS_PROFILE=chatbot-testing
```

### Verify Configuration

```bash
aws sts get-caller-identity
```

You should see output with your account ID and user ARN.

## Identifying Your Chatbot Endpoint

Your chatbot might be hosted on AWS in several ways:

### Option 1: API Gateway

If your chatbot uses AWS API Gateway:

1. **Find API Gateway URL using script:**
   ```bash
   python aws_setup/get_api_gateway_url.py
   ```

2. **Or find manually:**
   - Go to AWS Console → API Gateway
   - Select your API
   - Copy the "Invoke URL" (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com/prod`)

3. **Update .env:**
   ```env
   AWS_API_GATEWAY_URL=https://abc123.execute-api.us-east-1.amazonaws.com/prod
   CHATBOT_URL=https://abc123.execute-api.us-east-1.amazonaws.com/prod
   ```

### Option 2: CloudFront Distribution

If your chatbot uses CloudFront:

1. Go to AWS Console → CloudFront
2. Find your distribution
3. Copy the "Domain Name" (e.g., `d1234567890.cloudfront.net`)

4. **Update .env:**
   ```env
   AWS_CLOUDFRONT_DISTRIBUTION=d1234567890.cloudfront.net
   CHATBOT_URL=https://d1234567890.cloudfront.net
   ```

### Option 3: Direct URL

If your chatbot has a direct URL:

```env
CHATBOT_URL=https://your-chatbot-domain.com
```

### Option 4: EC2/ECS/Elastic Beanstalk

If your chatbot runs on EC2, ECS, or Elastic Beanstalk:

1. Find the public IP or load balancer URL
2. Use that URL in `CHATBOT_URL`

## AWS Cognito Setup (Optional)

If your chatbot uses AWS Cognito for authentication:

### 1. Find Cognito User Pool Information

```bash
python aws_setup/get_cognito_info.py
```

This will show:
- User Pool ID
- Client IDs
- Region

### 2. Update .env File

```env
USE_AWS_COGNITO=true
AWS_COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
AWS_COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxx
AWS_COGNITO_REGION=us-east-1
```

### 3. Test Cognito Authentication

Make sure your Cognito user pool allows programmatic access and has the correct app client settings.

## Configuration

### 1. Copy Environment Template

```bash
cp .env.example .env
```

### 2. Edit .env File

Update the following values:

```env
# Chatbot URL (from above steps)
CHATBOT_URL=https://your-chatbot-url.com

# API Endpoints (check your chatbot documentation)
API_ENDPOINT_LOGIN=/api/auth/login
API_ENDPOINT_SEND=/api/chat

# Authentication Credentials
LOGIN_EMAIL=your-email@example.com
LOGIN_PASSWORD=your-password

# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default  # or leave empty to use default

# If using API Gateway
AWS_API_GATEWAY_URL=https://abc123.execute-api.us-east-1.amazonaws.com/prod

# If using Cognito
USE_AWS_COGNITO=false  # set to true if using Cognito
AWS_COGNITO_USER_POOL_ID=
AWS_COGNITO_CLIENT_ID=
```

### 3. Run Setup Script

```bash
chmod +x aws_setup/setup_aws.sh
./aws_setup/setup_aws.sh
```

This script will:
- Check AWS CLI installation
- Verify AWS credentials
- Display your AWS account information
- Provide next steps

## Running Tests

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Tests

```bash
# Load test
python scripts/run_tests.py load

# Endurance test
python scripts/run_tests.py endurance

# Stress test
python scripts/run_tests.py stress

# Breakpoint test
python scripts/run_tests.py breakpoint
```

## Cost Estimation

### AWS Services Used

#### 1. API Gateway (if applicable)
- **Free Tier**: 1 million API calls/month for first 12 months
- **After Free Tier**: $3.50 per million API calls
- **Example**: 100,000 requests = $0.35

#### 2. Lambda (if chatbot uses Lambda)
- **Free Tier**: 1 million requests/month, 400,000 GB-seconds
- **After Free Tier**: $0.20 per 1M requests + compute time
- **Example**: 100,000 requests with 1GB memory, 1s duration = ~$0.20

#### 3. CloudFront (if applicable)
- **Free Tier**: 1TB data transfer out, 10 million requests/month
- **After Free Tier**: $0.085 per GB (first 10TB)
- **Example**: 10GB transfer = $0.85

#### 4. EC2/ECS (if chatbot runs on EC2/ECS)
- **EC2**: Depends on instance type
  - t3.micro: ~$0.0104/hour (free tier eligible)
  - t3.small: ~$0.0208/hour
- **ECS**: EC2 costs + $0 (ECS itself is free)

#### 5. Cognito (if using Cognito)
- **Free Tier**: 50,000 MAU (Monthly Active Users)
- **After Free Tier**: $0.0055 per MAU
- **Example**: 1,000 MAU = $5.50

### Performance Testing Cost Estimate

**Small Test (5 users, 2 minutes):**
- API Gateway: ~100 requests = **$0.00** (free tier)
- Lambda: ~100 invocations = **$0.00** (free tier)
- **Total: ~$0.00**

**Medium Test (10 users, 5 minutes):**
- API Gateway: ~500 requests = **$0.00** (free tier)
- Lambda: ~500 invocations = **$0.00** (free tier)
- **Total: ~$0.00**

**Large Test (100 users, 10 minutes):**
- API Gateway: ~10,000 requests = **$0.00** (free tier)
- Lambda: ~10,000 invocations = **$0.00** (free tier)
- **Total: ~$0.00**

**Stress Test (500 users, 5 minutes):**
- API Gateway: ~50,000 requests = **$0.00** (free tier)
- Lambda: ~50,000 invocations = **$0.00** (free tier)
- **Total: ~$0.00**

**Note**: Costs depend on:
- Your chatbot's architecture
- AWS region
- Data transfer
- Whether you're in free tier period

### Cost Monitoring

Monitor costs in AWS Cost Explorer:
1. Go to AWS Console → Cost Management → Cost Explorer
2. Set up billing alerts in AWS Billing → Preferences → Billing Alerts

## Troubleshooting

### Issue: "Unable to locate credentials"

**Solution:**
```bash
aws configure
# Enter your credentials
```

Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

### Issue: "Access Denied" when listing APIs

**Solution:**
- Ensure your IAM user has `AmazonAPIGatewayReadOnlyAccess` policy
- Check if you're using the correct AWS region

### Issue: "Invalid endpoint URL"

**Solution:**
- Verify the chatbot URL is correct
- Check if the API Gateway stage is correct (e.g., `/prod`, `/dev`)
- Ensure the endpoint is publicly accessible

### Issue: "401 Unauthorized" during login

**Solution:**
- Verify login credentials in `.env`
- Check if Cognito configuration is correct (if using Cognito)
- Ensure the login endpoint path is correct

### Issue: "Connection timeout"

**Solution:**
- Check security groups (if using EC2/ECS)
- Verify API Gateway CORS settings
- Check network connectivity
- Ensure the endpoint is publicly accessible

### Issue: "Region mismatch"

**Solution:**
- Ensure `AWS_REGION` in `.env` matches your chatbot's region
- Update AWS CLI default region: `aws configure set region us-east-1`

## Additional Resources

- [AWS Documentation](https://docs.aws.amazon.com/)
- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [AWS Cognito Documentation](https://docs.aws.amazon.com/cognito/)
- [AWS Pricing Calculator](https://calculator.aws/)

## Support

For issues specific to this testing suite, check:
- `README.md` for general usage
- `docs/` folder for additional documentation
- Test logs in `reports/` directory
