# Implementation Guide

This document provides a complete overview of what has been created and how to use it.

## Project Structure

The project has been recreated from scratch with a clear folder structure:

```
chatbot-performance-testing/
├── src/                          # Source code
│   ├── __init__.py
│   ├── locustfile.py            # Main Locust test file
│   └── sample_questions.py      # Sample questions
├── config/                       # Configuration files
│   ├── __init__.py
│   ├── test_config.py           # Centralized configuration
│   ├── config_load_test.py      # Load test config
│   ├── config_endurance_test.py # Endurance test config
│   ├── config_stress_test.py    # Stress test config
│   └── config_breakpoint_test.py # Breakpoint test config
├── scripts/                      # Utility scripts
│   └── run_tests.py             # Test runner
├── aws_setup/                    # AWS setup scripts
│   ├── setup_aws.sh             # AWS setup script
│   ├── get_api_gateway_url.py   # Get API Gateway URLs
│   └── get_cognito_info.py      # Get Cognito info
├── docs/                         # Documentation
│   ├── AWS_SETUP.md             # AWS setup guide
│   └── COSTS.md                 # Cost estimation
├── reports/                      # Generated reports (created on first run)
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── setup.sh                     # Setup script
├── README.md                     # Main documentation
├── QUICKSTART.md                # Quick start guide
└── IMPLEMENTATION_GUIDE.md      # This file
```

## What Has Been Created

### 1. Source Code (`src/`)

- **`locustfile.py`**: Main Locust test file that:
  - Handles authentication (login flow)
  - Simulates user interactions
  - Tracks Time To First Token (TTF)
  - Supports AWS-hosted chatbots

- **`sample_questions.py`**: Sample questions organized by category:
  - Simple questions (quick responses)
  - Common questions (typical queries)
  - Complex questions (detailed multi-part queries)

### 2. Configuration (`config/`)

- **`test_config.py`**: Centralized configuration with:
  - AWS settings (region, API Gateway, Cognito)
  - API endpoints
  - Authentication credentials
  - Test parameters
  - Environment variable support

- **Test-specific configs**: Separate config files for each test type

### 3. Scripts (`scripts/`)

- **`run_tests.py`**: Test runner that supports:
  - Load testing
  - Endurance testing
  - Stress testing
  - Breakpoint testing

### 4. AWS Setup (`aws_setup/`)

- **`setup_aws.sh`**: Automated AWS setup script
- **`get_api_gateway_url.py`**: Lists all API Gateway URLs
- **`get_cognito_info.py`**: Lists Cognito User Pool information

### 5. Documentation (`docs/`)

- **`AWS_SETUP.md`**: Complete AWS setup guide with:
  - AWS account setup
  - IAM user creation
  - Credentials configuration
  - Endpoint identification
  - Troubleshooting

- **`COSTS.md`**: Detailed cost estimation:
  - AWS service costs
  - Free tier coverage
  - Real-world scenarios
  - Cost optimization tips

## How to Use

### Step 1: Initial Setup

```bash
# Run setup script
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env  # or your favorite editor
```

**Required settings:**
- `CHATBOT_URL`: Your chatbot URL
- `LOGIN_EMAIL`: Login email
- `LOGIN_PASSWORD`: Login password
- `API_ENDPOINT_LOGIN`: Login endpoint path
- `API_ENDPOINT_SEND`: Chat endpoint path

### Step 3: AWS Setup (If Testing AWS Chatbot)

```bash
# Configure AWS credentials
aws configure

# Get API Gateway URL (if using API Gateway)
python aws_setup/get_api_gateway_url.py

# Update .env with the URL
```

See `docs/AWS_SETUP.md` for detailed instructions.

### Step 4: Run Tests

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

### Step 5: View Results

```bash
# Open HTML report
open reports/load_test_report.html  # macOS
```

## AWS Connection Steps

### 1. Create AWS Account

1. Go to https://aws.amazon.com
2. Sign up for an account
3. Complete payment information (required even for free tier)

### 2. Create IAM User

1. Go to AWS Console → IAM
2. Create a new user with programmatic access
3. Attach policies:
   - `AmazonAPIGatewayReadOnlyAccess`
   - `AmazonCognitoReadOnlyAccess` (if using Cognito)
   - `CloudWatchReadOnlyAccess`
4. Save Access Key ID and Secret Access Key

### 3. Configure AWS CLI

```bash
aws configure
# Enter Access Key ID
# Enter Secret Access Key
# Enter region (e.g., us-east-1)
# Enter output format (json)
```

### 4. Identify Your Chatbot Endpoint

**Option A: API Gateway**
```bash
python aws_setup/get_api_gateway_url.py
```

**Option B: CloudFront**
- AWS Console → CloudFront → Copy Domain Name

**Option C: EC2/ECS**
- Use public IP or load balancer URL

### 5. Update Configuration

Edit `.env`:
```env
AWS_REGION=us-east-1
AWS_API_GATEWAY_URL=https://your-api-gateway-url
CHATBOT_URL=https://your-api-gateway-url
```

### 6. Test Connection

```bash
# Verify AWS connection
aws sts get-caller-identity

# Run a test
python scripts/run_tests.py load
```

## Expected Costs

### Free Tier Coverage

Most tests fit within AWS free tier:

- **API Gateway**: 1M requests/month (first 12 months)
- **Lambda**: 1M requests/month, 400K GB-seconds
- **CloudFront**: 1TB transfer/month
- **Cognito**: 50K MAU/month

### Cost Estimates

**Small Test (5 users, 2 min):** $0.00 (free tier)
**Medium Test (10 users, 5 min):** $0.00 (free tier)
**Large Test (100 users, 10 min):** $0.00 (free tier)

**After Free Tier:**
- ~170K requests/month: ~$3.50/month
- ~4M requests/month: ~$81/month

See `docs/COSTS.md` for detailed breakdown.

## Key Features

### 1. AWS Integration

- Supports API Gateway, CloudFront, Cognito, Lambda, EC2/ECS
- Automatic endpoint discovery
- AWS credentials management
- Region-aware configuration

### 2. Multiple Test Types

- **Load Test**: Normal expected load
- **Endurance Test**: Long duration, moderate load
- **Stress Test**: High load beyond capacity
- **Breakpoint Test**: Gradual increase until failure

### 3. Authentication Support

- Email/password authentication
- AWS Cognito authentication
- Automatic session management
- Re-authentication on expiry

### 4. Performance Metrics

- Time To First Token (TTF) tracking
- Response time statistics
- Request per second (RPS)
- Error rates
- Question category breakdown

### 5. Reporting

- HTML reports with charts
- CSV statistics
- TTF data export
- Consolidated breakpoint reports

## Customization

### Modify Questions

Edit `src/sample_questions.py`:
```python
SIMPLE_MESSAGES = ["Your question here"]
COMMON_QUESTIONS = ["Your question here"]
COMPLEX_QUESTIONS = ["Your question here"]
```

### Adjust Test Parameters

Edit `config/test_config.py` or set environment variables:
```env
LOAD_TEST_USERS=10
LOAD_TEST_SPAWN_RATE=2
LOAD_TEST_RUN_TIME=5m
```

### Change API Endpoints

Edit `.env`:
```env
API_ENDPOINT_LOGIN=/api/auth/login
API_ENDPOINT_SEND=/api/chat
```

## Troubleshooting

### Common Issues

1. **"Module not found"**
   - Activate virtual environment: `source venv/bin/activate`

2. **"Unable to locate credentials"**
   - Run: `aws configure`

3. **"401 Unauthorized"**
   - Check credentials in `.env`
   - Verify endpoint paths

4. **"Connection timeout"**
   - Verify chatbot URL
   - Check security groups
   - Ensure endpoint is public

See `docs/AWS_SETUP.md` for detailed troubleshooting.

## Next Steps

1. **Read Documentation**
   - `README.md`: Main documentation
   - `QUICKSTART.md`: Quick start guide
   - `docs/AWS_SETUP.md`: AWS setup guide
   - `docs/COSTS.md`: Cost estimation

2. **Run Tests**
   - Start with load test
   - Try different test types
   - Analyze reports

3. **Customize**
   - Modify questions
   - Adjust test parameters
   - Configure for your chatbot

4. **Monitor Costs**
   - Set up billing alerts
   - Use AWS Cost Explorer
   - Track usage

## Support

For help:
1. Check documentation in `docs/` folder
2. Review test logs in `reports/` directory
3. Check AWS Console for service-specific issues

## Summary

You now have a complete, production-ready chatbot performance testing suite with:

✅ Clear folder structure
✅ AWS integration
✅ Multiple test types
✅ Comprehensive documentation
✅ Cost estimation
✅ Easy customization
✅ Detailed reporting

Everything is ready to use! Start with `QUICKSTART.md` for a 5-minute setup.
