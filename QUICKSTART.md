# Quick Start Guide

Get up and running with chatbot performance testing in 5 minutes!

## Step 1: Setup (2 minutes)

```bash
# Clone the repository
cd chatbot-performance-testing

# Run setup script
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Step 2: Configure (1 minute)

```bash
# Edit .env file
nano .env  # or use your favorite editor
```

**Minimum required settings:**
```env
CHATBOT_URL=https://your-chatbot-url.com
LOGIN_EMAIL=your-email@example.com
LOGIN_PASSWORD=your-password
API_ENDPOINT_LOGIN=/api/auth/login
API_ENDPOINT_SEND=/api/chat
```

## Step 3: AWS Setup (If Testing AWS Chatbot) - 2 minutes

```bash
# Configure AWS credentials
aws configure

# Get your API Gateway URL (if using API Gateway)
python aws_setup/get_api_gateway_url.py

# Update .env with the URL
# CHATBOT_URL=<url-from-above>
```

## Step 4: Run Your First Test

```bash
# Run a quick load test
python scripts/run_tests.py load

# View results
open reports/load_test_report.html  # macOS
# or
xdg-open reports/load_test_report.html  # Linux
# or
start reports/load_test_report.html  # Windows
```

## That's It! 🎉

You've successfully run your first performance test!

## Next Steps

- **Run different test types:**
  ```bash
  python scripts/run_tests.py endurance
  python scripts/run_tests.py stress
  python scripts/run_tests.py breakpoint
  ```

- **Customize tests:** Edit `config/test_config.py` or set environment variables

- **Modify questions:** Edit `src/sample_questions.py`

- **Read full documentation:** See `README.md` and `docs/` folder

## Common Issues

**"Module not found"**
- Make sure virtual environment is activated: `source venv/bin/activate`

**"Unable to locate credentials" (AWS)**
- Run: `aws configure`

**"401 Unauthorized"**
- Check login credentials in `.env` file
- Verify API endpoint paths are correct

**"Connection timeout"**
- Verify chatbot URL is correct
- Check if endpoint is publicly accessible

For more help, see `README.md` or `docs/AWS_SETUP.md`
