# Simple Setup Guide - 10 Concurrent Users

Quick guide to set up EC2 and run load testing for 10 concurrent users.

## Prerequisites

1. AWS Account
2. AWS CLI configured (`aws configure`)
3. EC2 Key Pair created

## Step 1: Create EC2 Key Pair

```bash
aws ec2 create-key-pair --key-name locust-testing --query 'KeyMaterial' --output text > ~/.ssh/locust-testing.pem
chmod 400 ~/.ssh/locust-testing.pem
```

## Step 2: Deploy EC2 Instance

```bash
./aws_setup/deploy_locust.sh
```

When prompted:
- Stack name: `locust-cluster` (or any name)
- Key Pair name: `locust-testing` (or your key name)
- Master instance type: `t3.small` (default)
- Worker instance type: `t3.small` (default)
- Number of workers: `1` (for 10 users, 1 worker is enough)

Wait 2-3 minutes for instance to be created.

## Step 3: Get Instance IP

```bash
./aws_setup/get_ips_simple.sh
```

Note the master's public IP.

## Step 4: Copy Files to Instance

```bash
MASTER_IP=<ip-from-step-3>
scp -i ~/.ssh/locust-testing.pem -r src/ config/ .env ec2-user@$MASTER_IP:/home/ec2-user/chatbot-performance-testing/
```

## Step 5: Start Locust Master

```bash
ssh -i ~/.ssh/locust-testing.pem ec2-user@$MASTER_IP
cd /home/ec2-user/chatbot-performance-testing
locust -f src/locustfile.py --master --host=https://your-chatbot-url.com
```

## Step 6: Start Worker (in new terminal)

```bash
# Get worker IP from get_ips_simple.sh output
WORKER_IP=<worker-ip>
ssh -i ~/.ssh/locust-testing.pem ec2-user@$WORKER_IP
cd /home/ec2-user/chatbot-performance-testing
# Copy files first: scp -i ~/.ssh/locust-testing.pem -r src/ config/ ec2-user@$WORKER_IP:...
locust -f src/locustfile.py --worker --master-host=<master-private-ip>
```

## Step 7: Run Test

Open browser: `http://<master-ip>:8089`

Enter:
- Number of users: **10**
- Spawn rate: **2**
- Host: Your chatbot URL

Click "Start swarming"

## Step 8: Cleanup

```bash
aws cloudformation delete-stack --stack-name locust-cluster
```

Done!
