# Quick Start Guide

Get API load testing running in 5 minutes.

## Step 1: Configure API (1 minute)

Edit `config/test_config.yaml`:
```yaml
chatbot:
  url: "https://your-chatbot-url.com"
  api_endpoints:
    login: "/api/auth/login"    # Your login API endpoint
    send: "/api/chat"           # Your chat API endpoint
```

Create `.env`:
```env
CHATBOT_URL=https://your-chatbot-url.com
LOGIN_EMAIL=your-email@example.com
LOGIN_PASSWORD=your-password
API_ENDPOINT_LOGIN=/api/auth/login
API_ENDPOINT_SEND=/api/chat
```

## Step 2: Set Up IAM Permissions

Your IAM user needs EC2 and CloudFormation permissions:

**Quick fix:**
```bash
aws iam attach-user-policy --user-name chatbot-testing-user --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess
aws iam attach-user-policy --user-name chatbot-testing-user --policy-arn arn:aws:iam::aws:policy/AWSCloudFormationFullAccess
```

**Or AWS Console:**
1. IAM Console → Users → `chatbot-testing-user`
2. Add permissions → Attach `AmazonEC2FullAccess`
3. Add permissions again → Attach `AWSCloudFormationFullAccess`

See [IAM Permissions Guide](docs/IAM_PERMISSIONS.md) for details.

## Step 3: Create EC2 Key Pair (if needed)

If you don't have an EC2 key pair yet:

**Option A: AWS Console**
1. Go to AWS Console → EC2 → Key Pairs
2. Click "Create key pair"
3. Name it (e.g., `locust-load-testing`)
4. Download the `.pem` file
5. Set permissions: `chmod 400 ~/.ssh/locust-load-testing.pem`

**Option B: AWS CLI**
```bash
aws ec2 create-key-pair --key-name locust-load-testing --query 'KeyMaterial' --output text > ~/.ssh/locust-load-testing.pem
chmod 400 ~/.ssh/locust-load-testing.pem
```

See [EC2 Setup Guide](docs/EC2_SETUP.md) for details.

## Step 4: Deploy on AWS (2 minutes)

```bash
./aws_setup/deploy_locust.sh
```

Follow prompts. You'll need:
- **EC2 Key Pair name**: The name you created (e.g., `locust-load-testing`)
- **Master instance type**: `t3.medium` (default, recommended)
- **Worker instance type**: `t3.small` (default, recommended)
- **Number of workers**: `2` (default, increase for more load)

**Wait 2-3 minutes** for instances to be created before getting IPs.

## Step 5: Get Instance IPs

**After deployment completes (wait 2-3 minutes):**

```bash
# Get IPs from CloudFormation
./aws_setup/get_ips_simple.sh

# If no IPs found, troubleshoot:
./aws_setup/troubleshoot_instances.sh
```

**Or check CloudFormation outputs manually:**
```bash
aws cloudformation describe-stacks --stack-name locust-cluster --query 'Stacks[0].Outputs' --output table
```

Note the master's **public IP** (for SSH) and **private IP** (for workers).

## Step 6: Copy Files (1 minute)

```bash
# Replace <master-ip> with actual IP from above
MASTER_IP=<master-ip>

# Copy files
scp -i ~/.ssh/locust-load-testing.pem -r src/ config/ .env ec2-user@$MASTER_IP:/home/ec2-user/chatbot-performance-testing/
```

## Step 7: Start Master (1 minute)

```bash
# SSH to master (replace <master-ip> with actual IP)
ssh -i ~/.ssh/locust-load-testing.pem ec2-user@<master-ip>

# Once connected, start Locust master
cd /home/ec2-user/chatbot-performance-testing
locust -f src/locustfile.py --master --host=https://your-chatbot-url.com
```

**Note**: Keep this terminal open. The master will wait for workers to connect.

## Step 8: Start Workers

Get worker IPs from `./aws_setup/get_instance_ips.sh` output, then:

**In a NEW terminal window for each worker:**

```bash
# Copy files to worker (replace <worker-ip>)
scp -i ~/.ssh/locust-load-testing.pem -r src/ config/ ec2-user@<worker-ip>:/home/ec2-user/chatbot-performance-testing/

# SSH to worker
ssh -i ~/.ssh/locust-load-testing.pem ec2-user@<worker-ip>

# Start worker (use master's PRIVATE IP, not public!)
cd /home/ec2-user/chatbot-performance-testing
locust -f src/locustfile.py --worker --master-host=<master-private-ip>
```

**Important**: Use the master's **private IP** (not public IP) for `--master-host`.

## Step 9: Run Tests

Open: `http://<master-ip>:8089`

Enter:
- Number of users
- Spawn rate
- Host: Your chatbot URL

Click "Start swarming"!

## Cleanup

```bash
aws cloudformation delete-stack --stack-name locust-cluster
```

Done! 🎉
