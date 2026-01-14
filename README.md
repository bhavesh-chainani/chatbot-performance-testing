# Chatbot Performance Testing Suite for AWS

A comprehensive load testing suite for AWS-hosted chatbots built with [Locust](https://locust.io/). Designed for testing chatbot performance with authentication support, AWS integration, and Time To First Token (TTF) tracking.

## Features

- ✅ **4 Test Types**: Load, Endurance, Stress, and Breakpoint testing
- ✅ **AWS Integration**: Support for API Gateway, CloudFront, Cognito, Lambda, EC2/ECS
- ✅ **Load Testing**: Simulate normal expected load conditions
- ✅ **Endurance Testing**: Long duration tests to identify memory leaks and degradation
- ✅ **Stress Testing**: High load beyond normal capacity to find breaking points
- ✅ **Breakpoint Testing**: Gradually increase load until system fails
- ✅ **Authentication Support**: Automatic login flow handling (email/password or AWS Cognito)
- ✅ **TTF Tracking**: Time To First Token metrics per question category
- ✅ **Question Categories**: Separate performance metrics for different question types
- ✅ **Detailed Reports**: HTML and CSV reports with comprehensive metrics
- ✅ **Customizable**: Easy to configure test parameters and sample questions
- ✅ **Cost-Effective**: Optimized for AWS free tier usage

## Project Structure

```
.
├── src/                          # Source code
│   ├── __init__.py
│   ├── locustfile.py            # Main Locust test file
│   └── sample_questions.py      # Sample questions organized by category
├── config/                       # Configuration files
│   ├── __init__.py
│   ├── test_config.py           # Centralized test configuration
│   ├── config_load_test.py      # Load test configuration
│   ├── config_endurance_test.py # Endurance test configuration
│   ├── config_stress_test.py    # Stress test configuration
│   └── config_breakpoint_test.py # Breakpoint test configuration
├── scripts/                      # Utility scripts
│   └── run_tests.py             # Test runner script
├── aws_setup/                    # AWS setup scripts
│   ├── setup_aws.sh             # AWS setup script
│   ├── get_api_gateway_url.py   # Get API Gateway URLs
│   └── get_cognito_info.py      # Get Cognito information
├── docs/                         # Documentation
│   ├── AWS_SETUP.md             # AWS setup guide
│   └── COSTS.md                 # Cost estimation guide
├── reports/                      # Generated test reports
├── .env.example                  # Environment variables template
├── requirements.txt             # Python dependencies
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- AWS Account (for AWS-hosted chatbots)
- AWS CLI (optional, for AWS setup scripts)

## Quick Start

### 1. Clone and Install

```bash
# Clone the repository
git clone <your-repo-url>
cd chatbot-performance-testing

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# See Configuration section below
```

### 3. AWS Setup (If Testing AWS-Hosted Chatbot)

```bash
# Run AWS setup script
chmod +x aws_setup/setup_aws.sh
./aws_setup/setup_aws.sh

# Or manually configure AWS credentials
aws configure
```

For detailed AWS setup instructions, see [docs/AWS_SETUP.md](docs/AWS_SETUP.md)

### 4. Run Tests

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

## Configuration

### Environment Variables (.env)

Create a `.env` file from `.env.example`:

```env
# Chatbot URL (AWS API Gateway, CloudFront, or direct URL)
CHATBOT_URL=https://your-chatbot-url.com

# API Endpoints
API_ENDPOINT_LOGIN=/api/auth/login
API_ENDPOINT_SEND=/api/chat

# Authentication Credentials
LOGIN_EMAIL=your-email@example.com
LOGIN_PASSWORD=your-password

# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default

# AWS API Gateway (if using)
AWS_API_GATEWAY_URL=https://abc123.execute-api.us-east-1.amazonaws.com/prod

# AWS Cognito (if using Cognito authentication)
USE_AWS_COGNITO=false
AWS_COGNITO_USER_POOL_ID=
AWS_COGNITO_CLIENT_ID=
AWS_COGNITO_REGION=

# Test Configuration (see config files for details)
LOAD_TEST_USERS=5
LOAD_TEST_SPAWN_RATE=1
LOAD_TEST_RUN_TIME=2m
```

### Finding Your Chatbot URL

#### If Using AWS API Gateway:

```bash
python aws_setup/get_api_gateway_url.py
```

#### If Using AWS Cognito:

```bash
python aws_setup/get_cognito_info.py
```

#### Manual Method:

1. **API Gateway**: AWS Console → API Gateway → Your API → Stages → Copy Invoke URL
2. **CloudFront**: AWS Console → CloudFront → Your Distribution → Copy Domain Name
3. **EC2/ECS**: Use public IP or load balancer URL

## Test Types

### 1. Load Test

**Purpose**: Test normal expected load conditions - baseline performance testing.

**Default Configuration:**
- Users: 5 concurrent users
- Spawn Rate: 1 user/second
- Duration: 2 minutes

**Run:**
```bash
python scripts/run_tests.py load
# or with custom parameters
python scripts/run_tests.py load 10 2 5m
```

### 2. Endurance Test

**Purpose**: Long duration test with moderate load to identify memory leaks and performance degradation.

**Default Configuration:**
- Users: 3 concurrent users
- Spawn Rate: 0.5 users/second
- Duration: 10 minutes

**Run:**
```bash
python scripts/run_tests.py endurance
```

### 3. Stress Test

**Purpose**: High load beyond normal capacity to identify maximum capacity limits.

**Default Configuration:**
- Users: 10 concurrent users
- Spawn Rate: 2 users/second
- Duration: 5 minutes

**Run:**
```bash
python scripts/run_tests.py stress
```

### 4. Breakpoint Test

**Purpose**: Gradually increase load until system fails - finds exact breaking point.

**Default Configuration:**
- Start Users: 1
- Max Users: 150
- Spawn Rate: 1 user/second
- Step Duration: 1 minute per load level
- User Increment: +20 users per step

**Run:**
```bash
python scripts/run_tests.py breakpoint
```

## AWS Integration

### Supported AWS Services

- **API Gateway**: REST APIs and HTTP APIs
- **CloudFront**: CDN distribution
- **Cognito**: User authentication
- **Lambda**: Serverless functions
- **EC2/ECS**: Containerized applications
- **Elastic Beanstalk**: Managed applications

### AWS Setup Steps

1. **Configure AWS Credentials**
   ```bash
   aws configure
   ```

2. **Identify Your Chatbot Endpoint**
   ```bash
   python aws_setup/get_api_gateway_url.py
   ```

3. **Update .env File**
   ```env
   AWS_REGION=us-east-1
   AWS_API_GATEWAY_URL=https://your-api-gateway-url
   CHATBOT_URL=https://your-api-gateway-url
   ```

4. **Run Tests**
   ```bash
   python scripts/run_tests.py load
   ```

For detailed AWS setup instructions, see [docs/AWS_SETUP.md](docs/AWS_SETUP.md)

## Cost Estimation

### AWS Free Tier Coverage

Most performance tests fit within AWS free tier limits:

- **API Gateway**: 1 million requests/month (first 12 months)
- **Lambda**: 1 million requests/month, 400K GB-seconds
- **CloudFront**: 1TB data transfer/month
- **Cognito**: 50,000 MAU/month

### Estimated Costs

**Small Test (5 users, 2 min):** ~$0.00 (free tier)
**Medium Test (10 users, 5 min):** ~$0.00 (free tier)
**Large Test (100 users, 10 min):** ~$0.00 (free tier)

For detailed cost breakdown, see [docs/COSTS.md](docs/COSTS.md)

## Reports

Test reports are saved in the `reports/` directory:

- **HTML Reports**: `reports/{test_type}_test_report.html`
- **CSV Statistics**: `reports/{test_type}_test_report_*.csv`
- **TTF Data**: `reports/ttf_data.csv` (Time To First Token metrics)

### Viewing Reports

Open HTML reports in your browser:
```bash
# macOS
open reports/load_test_report.html

# Linux
xdg-open reports/load_test_report.html

# Windows
start reports/load_test_report.html
```

## Customization

### Modify Sample Questions

Edit `src/sample_questions.py`:

```python
SIMPLE_MESSAGES = [
    "Your simple question here",
    # Add more...
]

COMMON_QUESTIONS = [
    "Your common question here",
    # Add more...
]

COMPLEX_QUESTIONS = [
    "Your complex question here",
    # Add more...
]
```

### Adjust Test Parameters

Edit `config/test_config.py` or set environment variables:

```python
LOAD_TEST_USERS = 10
LOAD_TEST_SPAWN_RATE = 2
LOAD_TEST_RUN_TIME = "5m"
```

## Troubleshooting

### AWS Connection Issues

**Problem**: "Unable to locate credentials"
```bash
# Solution: Configure AWS credentials
aws configure
```

**Problem**: "Access Denied"
- Check IAM user permissions
- Verify AWS region matches chatbot region

### Authentication Issues

**Problem**: "401 Unauthorized"
- Verify login credentials in `.env`
- Check if using correct authentication method (email/password vs Cognito)
- Verify API endpoint paths

**Problem**: "404 Not Found"
- Check chatbot URL is correct
- Verify API endpoint paths
- Ensure API Gateway stage is correct (e.g., `/prod`)

### Connection Issues

**Problem**: "Connection timeout"
- Check security groups (if using EC2/ECS)
- Verify API Gateway CORS settings
- Ensure endpoint is publicly accessible

For more troubleshooting, see [docs/AWS_SETUP.md](docs/AWS_SETUP.md)

## Documentation

- **[AWS Setup Guide](docs/AWS_SETUP.md)**: Complete AWS setup instructions
- **[Cost Estimation](docs/COSTS.md)**: Detailed cost breakdown and estimates

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is provided as-is for performance testing purposes.

## Acknowledgments

- Built with [Locust](https://locust.io/) - An open source load testing tool
- Designed for AWS-hosted chatbot performance testing
- Optimized for AWS free tier usage

## Support

For issues or questions:
1. Check documentation in `docs/` folder
2. Review test logs in `reports/` directory
3. Check AWS Console for service-specific issues
