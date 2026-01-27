# Implementation Guide

Simple guide for chatbot API load testing on AWS.

## What You Need

1. **Chatbot API URL** - Base URL of your chatbot API
2. **API Endpoints** - Login and chat endpoints
3. **Login credentials** - Email and password
4. **AWS Account** - For running EC2 instances

## How It Works

1. **Deploy Locust on AWS** - Creates EC2 instances
2. **Configure API** - Set URL, endpoints, and credentials
3. **Run tests** - Use Locust web UI to start load testing

## Configuration

### 1. API Settings

Edit `config/test_config.yaml`:
```yaml
chatbot:
  url: "https://your-chatbot-url.com"
  api_endpoints:
    login: "/api/auth/login"    # Login API endpoint
    send: "/api/chat"           # Chat message API endpoint
```

### 2. Credentials and API Endpoints

Create `.env`:
```env
CHATBOT_URL=https://your-chatbot-url.com
LOGIN_EMAIL=your-email@example.com
LOGIN_PASSWORD=your-password
API_ENDPOINT_LOGIN=/api/auth/login
API_ENDPOINT_SEND=/api/chat
```

### 3. Test Parameters

Edit `config/test_config.yaml`:
```yaml
load_test:
  users: 5          # Concurrent users
  spawn_rate: 1.0   # Users per second
  run_time: "2m"    # Duration
```

## Deployment

### Deploy on AWS

```bash
./aws_setup/deploy_locust.sh
```

### Copy Files

```bash
scp -r src/ config/ .env ec2-user@<master-ip>:...
```

### Start Master

```bash
ssh ec2-user@<master-ip>
cd /home/ec2-user/chatbot-performance-testing
locust -f src/locustfile.py --master --host=https://your-chatbot-url.com
```

### Start Workers

On each worker:
```bash
locust -f src/locustfile.py --worker --master-host=<master-private-ip>
```

### Access Web UI

Open: `http://<master-ip>:8089`

## Project Structure

```
.
├── src/
│   ├── locustfile.py          # Main test (handles API login + chat)
│   └── sample_questions.py    # Test questions
├── config/
│   ├── test_config.yaml      # API endpoints & test parameters
│   └── test_config.py        # Config loader
├── aws_setup/
│   ├── deploy_locust.sh      # Deploy script
│   └── cloudformation/       # AWS templates
└── scripts/
    └── run_tests.py          # Local test runner (optional)
```

## API Endpoints

The test will:
1. **Login**: POST to `{CHATBOT_URL}{API_ENDPOINT_LOGIN}` with email/password
2. **Send messages**: POST to `{CHATBOT_URL}{API_ENDPOINT_SEND}` with chat messages

Configure these in `.env` file (or `config/test_config.yaml` as defaults).

## Cost

- Small setup: ~$0.08/hour
- Medium setup: ~$0.15/hour

**Always terminate instances when done!**

## Cleanup

```bash
aws cloudformation delete-stack --stack-name locust-cluster
```

That's it! Simple API load testing on AWS.
