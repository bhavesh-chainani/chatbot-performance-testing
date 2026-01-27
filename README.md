# Chatbot API Load Testing on AWS

Load testing for your chatbot API using AWS EC2. Simple setup: URL, login endpoint, send endpoint, and credentials.

## Quick Start

### 1. Configure Your Chatbot API

Edit `config/test_config.yaml`:
```yaml
chatbot:
  url: "https://your-chatbot-url.com"
  api_endpoints:
    login: "/api/auth/login"    # Your login API endpoint
    send: "/api/chat"           # Your chat message API endpoint
```

Create `.env` file:
```env
CHATBOT_URL=https://your-chatbot-url.com
LOGIN_EMAIL=your-email@example.com
LOGIN_PASSWORD=your-password
API_ENDPOINT_LOGIN=/api/auth/login
API_ENDPOINT_SEND=/api/chat
```

### 2. Set Up IAM Permissions

Your IAM user needs EC2 and CloudFormation permissions:

**Quick fix (AWS Console):**
1. Go to IAM Console → Users → `chatbot-testing-user`
2. Add permissions → Attach policies directly
3. Attach: **`AmazonEC2FullAccess`**
4. Add permissions again → Attach: **`AWSCloudFormationFullAccess`**

**Or AWS CLI:**
```bash
aws iam attach-user-policy --user-name chatbot-testing-user --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess
aws iam attach-user-policy --user-name chatbot-testing-user --policy-arn arn:aws:iam::aws:policy/AWSCloudFormationFullAccess
```

See [IAM Permissions Guide](docs/IAM_PERMISSIONS.md) for details.

### 3. Create EC2 Key Pair (if needed)

If you don't have an EC2 key pair:

**AWS Console:**
1. Go to AWS Console → EC2 → Key Pairs
2. Click "Create key pair"
3. Name it (e.g., `locust-load-testing`)
4. Download and save the `.pem` file securely

**Or AWS CLI:**
```bash
aws ec2 create-key-pair --key-name locust-load-testing --query 'KeyMaterial' --output text > ~/.ssh/locust-load-testing.pem
chmod 400 ~/.ssh/locust-load-testing.pem
```

See [EC2 Setup Guide](docs/EC2_SETUP.md) for details.

### 4. Deploy Locust on AWS

```bash
./aws_setup/deploy_locust.sh
```

When prompted:
- **EC2 Key Pair name**: Enter the name you created (e.g., `locust-load-testing`)
- **Instance types**: Use defaults (`t3.medium` for master, `t3.small` for workers)
- **Number of workers**: Start with 2, increase for more load

This creates EC2 instances (1 master + workers) for distributed load testing.

### 4. Copy Files and Run

```bash
# Get master IP from output, then:
MASTER_IP=<master-ip-from-output>

# Copy test files
scp -r src/ config/ .env ec2-user@$MASTER_IP:/home/ec2-user/chatbot-performance-testing/

# SSH and start master
ssh ec2-user@$MASTER_IP
cd /home/ec2-user/chatbot-performance-testing
locust -f src/locustfile.py --master --host=https://your-chatbot-url.com
```

### 5. Start Workers

On each worker instance:
```bash
ssh ec2-user@<worker-ip>
cd /home/ec2-user/chatbot-performance-testing
# Copy files first: scp -r src/ config/ ec2-user@<worker-ip>:...
locust -f src/locustfile.py --worker --master-host=<master-private-ip>
```

### 6. Access Web UI

Open: `http://<master-ip>:8089`

Enter test parameters and start testing!

## Configuration

### Required Settings

**In `config/test_config.yaml`:**
- `chatbot.url` - Your chatbot API base URL
- `chatbot.api_endpoints.login` - Login API endpoint (e.g., `/api/auth/login`)
- `chatbot.api_endpoints.send` - Chat message API endpoint (e.g., `/api/chat`)

**In `.env`:**
- `CHATBOT_URL` - Your chatbot API base URL
- `LOGIN_EMAIL` - Your login email
- `LOGIN_PASSWORD` - Your login password
- `API_ENDPOINT_LOGIN` - Login API endpoint (e.g., `/api/auth/login`)
- `API_ENDPOINT_SEND` - Chat message API endpoint (e.g., `/api/chat`)

### Test Parameters

Edit `config/test_config.yaml` to adjust:
- Number of concurrent users
- Spawn rate (users/second)
- Test duration

## Test Types

- **Load Test**: Normal load (5 users, 2 min)
- **Endurance Test**: Long duration (3 users, 10 min)
- **Stress Test**: High load (10 users, 5 min)
- **Breakpoint Test**: Find breaking point (1→150 users)

## Cost

**For your test plan (see costs/ folder for details):**
- Complete test plan: ~$83.18 (with Lambda) or ~$4.04 (EC2 only)
- Per test run average: ~$10.40 or ~$0.51

**See detailed cost breakdown:** [Costs Documentation](costs/TEST_PLAN_COSTS.md)

**Remember**: Terminate instances when done to avoid charges!

## Cleanup

```bash
aws cloudformation delete-stack --stack-name locust-cluster
```

## Documentation

- [EC2 Setup Guide](docs/EC2_SETUP.md) - **Instance types and key pair creation**
- [IAM Permissions](docs/IAM_PERMISSIONS.md) - **Required AWS permissions** (if you get access errors)
- [AWS Infrastructure Guide](docs/AWS_LOAD_TESTING_INFRASTRUCTURE.md) - Detailed AWS setup
- [Cost Estimation](docs/COSTS.md) - Cost breakdown
- [Quick Start](QUICKSTART.md) - Step-by-step guide

## Project Structure

```
.
├── src/                    # Test code
│   ├── locustfile.py      # Main test (handles API login + chat)
│   └── sample_questions.py
├── config/                 # Configuration
│   ├── test_config.yaml   # API endpoints & test parameters
│   └── test_config.py     # Config loader
├── aws_setup/             # AWS deployment
│   ├── deploy_locust.sh   # Deploy script
│   └── cloudformation/    # CloudFormation templates
└── scripts/               # Test runner (optional)
    └── run_tests.py
```

That's it! Simple API load testing on AWS.
