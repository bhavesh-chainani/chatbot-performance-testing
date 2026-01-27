# AWS Infrastructure for Load Testing

Deploy Locust on AWS EC2 to run distributed load tests against your chatbot API.

## Architecture

```
Your Chatbot API (any URL)
    ↑
    │ API requests (login + chat)
    │
┌───▼──────────────────┐
│  Locust Master (EC2) │ ← Web UI + Coordinator
└───┬──────────────────┘
    │
┌───┴────┬──────────┬──────────┐
│ Worker │  Worker │  Worker │ ← Generate API load
└────────┴──────────┴──────────┘
```

## Configuration

You need:
- **Chatbot URL**: Base URL of your API
- **Login API endpoint**: Path to login endpoint (e.g., `/api/auth/login`)
- **Chat API endpoint**: Path to chat endpoint (e.g., `/api/chat`)
- **Credentials**: Email and password for login

Set in `.env`:
```env
CHATBOT_URL=https://your-chatbot-url.com
LOGIN_EMAIL=your-email@example.com
LOGIN_PASSWORD=your-password
API_ENDPOINT_LOGIN=/api/auth/login
API_ENDPOINT_SEND=/api/chat
```

Note: `.env` values override `config/test_config.yaml` if both are set.

## Prerequisites

1. AWS Account
2. AWS CLI configured (`aws configure`)
3. EC2 Key Pair created

## Deployment

### Option 1: Automated Script (Recommended)

```bash
./aws_setup/deploy_locust.sh
```

Follow prompts. Script will:
- Create EC2 instances
- Set up security groups
- Install Locust
- Provide connection instructions

### Option 2: CloudFormation

```bash
aws cloudformation create-stack \
    --stack-name locust-cluster \
    --template-body file://aws_setup/cloudformation/locust-cluster.yaml \
    --parameters \
        ParameterKey=InstanceTypeMaster,ParameterValue=t3.medium \
        ParameterKey=InstanceTypeWorker,ParameterValue=t3.small \
        ParameterKey=WorkerCount,ParameterValue=2 \
        ParameterKey=KeyPairName,ParameterValue=your-key-pair
```

## Setup Steps

### 1. Deploy Infrastructure

```bash
./aws_setup/deploy_locust.sh
```

Note the master IP from output.

### 2. Copy Test Files

```bash
MASTER_IP=<master-ip-from-output>
scp -r src/ config/ .env ec2-user@$MASTER_IP:/home/ec2-user/chatbot-performance-testing/
```

### 3. Start Master

```bash
ssh ec2-user@$MASTER_IP
cd /home/ec2-user/chatbot-performance-testing
locust -f src/locustfile.py --master --host=https://your-chatbot-url.com
```

### 4. Start Workers

Get worker IPs:
```bash
aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=locust-worker-*" \
    --query 'Reservations[*].Instances[*].PublicIpAddress' \
    --output text
```

On each worker:
```bash
ssh ec2-user@<worker-ip>
cd /home/ec2-user/chatbot-performance-testing
# Copy files first: scp -r src/ config/ ec2-user@<worker-ip>:...
locust -f src/locustfile.py --worker --master-host=<master-private-ip>
```

### 5. Access Web UI

Open: `http://<master-ip>:8089`

Enter test parameters and start!

## Running Tests

1. Open web UI: `http://<master-ip>:8089`
2. Enter:
   - Number of users (total across all workers)
   - Spawn rate (users/second)
   - Host: Your chatbot URL
3. Click "Start swarming"
4. Monitor results in real-time

## Cost

- **Small** (1 master + 2 workers): ~$0.08/hour
- **Medium** (1 master + 5 workers): ~$0.15/hour
- **Large** (1 master + 10 workers): ~$0.25/hour

**Important**: Terminate instances when done!

## Cleanup

```bash
aws cloudformation delete-stack --stack-name locust-cluster
```

Or manually terminate instances in EC2 console.

## Troubleshooting

**Workers not connecting:**
- Use master's **private IP** (not public)
- Check security group allows port 5557

**Web UI not accessible:**
- Check security group allows port 8089 from your IP
- Verify instance is running

**High costs:**
- Terminate instances immediately after tests
- Use smaller instance types if possible

## Best Practices

1. **Terminate after tests** - Don't leave instances running
2. **Use private IPs** - For master-worker communication
3. **Monitor costs** - Set up billing alerts
4. **Start small** - Test with 2 workers first, then scale up

That's it! Simple distributed load testing on AWS.
