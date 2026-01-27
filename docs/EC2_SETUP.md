# EC2 Instance Types and Key Pair Setup

Guide for choosing EC2 instances and creating key pairs for Locust load testing.

## EC2 Instance Types

### Recommended Instance Types

**For Locust Master:**
- **t3.medium** (Recommended) - 2 vCPU, 4 GB RAM
  - Cost: ~$0.0416/hour
  - Good for: Up to 1000 concurrent users
- **t3.small** - 2 vCPU, 2 GB RAM
  - Cost: ~$0.0208/hour
  - Good for: Up to 500 concurrent users
- **t3.large** - 2 vCPU, 8 GB RAM
  - Cost: ~$0.0832/hour
  - Good for: 2000+ concurrent users

**For Locust Workers:**
- **t3.small** (Recommended) - 2 vCPU, 2 GB RAM
  - Cost: ~$0.0208/hour per worker
  - Good for: ~500 users per worker
- **t3.micro** - 2 vCPU, 1 GB RAM
  - Cost: ~$0.0104/hour per worker
  - Good for: ~200 users per worker (free tier eligible)
- **t3.medium** - 2 vCPU, 4 GB RAM
  - Cost: ~$0.0416/hour per worker
  - Good for: ~1000 users per worker

### Instance Type Selection Guide

| Test Size | Master | Workers | Total Cost/Hour |
|-----------|--------|---------|-----------------|
| Small (100-500 users) | t3.small | 2x t3.small | ~$0.06 |
| Medium (500-2000 users) | t3.medium | 2-5x t3.small | ~$0.10-0.15 |
| Large (2000-5000 users) | t3.medium | 5-10x t3.small | ~$0.15-0.25 |
| Very Large (5000+ users) | t3.large | 10+ t3.small | ~$0.30+ |

**Default in deployment script:**
- Master: `t3.medium`
- Workers: `t3.small`
- Worker count: 2

## Creating EC2 Key Pair

### Method 1: AWS Console (Recommended)

1. **Log in to AWS Console**
   - Go to https://console.aws.amazon.com
   - Sign in to your account

2. **Navigate to EC2**
   - Search for "EC2" in the top search bar
   - Click on "EC2" service

3. **Go to Key Pairs**
   - In the left sidebar, under "Network & Security", click "Key Pairs"
   - Or go directly: https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#KeyPairs:

4. **Create Key Pair**
   - Click "Create key pair" button (top right)
   - **Name**: Enter a name (e.g., `locust-load-testing` or `my-key-pair`)
   - **Key pair type**: Select "RSA" (recommended)
   - **Private key file format**: Select "pem" (for Linux/Mac) or "ppk" (for Windows PuTTY)
   - Click "Create key pair"

5. **Download Key**
   - The key file will automatically download
   - **Important**: Save this file securely! You cannot download it again.
   - For Linux/Mac: Save as `~/.ssh/locust-load-testing.pem`
   - Set permissions: `chmod 400 ~/.ssh/locust-load-testing.pem`

### Method 2: AWS CLI

```bash
# Create key pair
aws ec2 create-key-pair \
    --key-name locust-load-testing \
    --query 'KeyMaterial' \
    --output text > ~/.ssh/locust-load-testing.pem

# Set permissions (Linux/Mac)
chmod 400 ~/.ssh/locust-load-testing.pem

# Verify
aws ec2 describe-key-pairs --key-names locust-load-testing
```

### Method 3: Using Existing SSH Key

If you already have an SSH key pair:

```bash
# Import your public key to AWS
aws ec2 import-key-pair \
    --key-name locust-load-testing \
    --public-key-material fileb://~/.ssh/id_rsa.pub
```

## Key Pair Name

**What is it?**
- A name you give to your key pair in AWS
- Used to identify which key to use when launching EC2 instances
- Examples: `locust-load-testing`, `my-key-pair`, `test-key`

**Where to find it?**
- AWS Console → EC2 → Key Pairs
- Lists all your key pairs with their names

**What to use?**
- Use the exact name as shown in AWS Console
- Case-sensitive
- No spaces (use hyphens or underscores)

## Using Key Pair in Deployment

When running `./aws_setup/deploy_locust.sh`, you'll be prompted:

```
EC2 Key Pair name (required for SSH): 
```

Enter the exact name from AWS Console, for example:
- `locust-load-testing`
- `my-key-pair`
- `test-key`

## SSH Access After Deployment

Once instances are created, SSH using:

```bash
# Linux/Mac
ssh -i ~/.ssh/locust-load-testing.pem ec2-user@<instance-ip>

# Or if key is in default location
ssh -i ~/.ssh/locust-load-testing.pem ec2-user@<instance-ip>
```

**Note**: Replace `locust-load-testing.pem` with your actual key file name.

## IAM Permissions

Your IAM user needs EC2 permissions. If you get "UnauthorizedOperation" errors:

**Quick fix:**
- Go to IAM Console → Users → Your user
- Attach policy: `AmazonEC2FullAccess`

**Or see:** [IAM Permissions Guide](IAM_PERMISSIONS.md) for custom policy.

## Troubleshooting

### "UnauthorizedOperation" or "Access Denied"

You need IAM permissions. See [IAM Permissions Guide](IAM_PERMISSIONS.md).

### "Key pair not found"
- Verify key pair name is correct (case-sensitive)
- Check you're in the correct AWS region
- List key pairs: `aws ec2 describe-key-pairs`

### "Permission denied" when SSHing
- Set correct permissions: `chmod 400 ~/.ssh/your-key.pem`
- Verify key file path is correct
- Check instance security group allows SSH (port 22)

### "Key pair already exists"
- Use existing key pair name
- Or create new one with different name
- List existing: `aws ec2 describe-key-pairs`

## Best Practices

1. **Use descriptive names**: `locust-load-testing`, `prod-load-test`, etc.
2. **Store keys securely**: Never commit `.pem` files to git
3. **Use different keys**: Separate keys for different environments
4. **Set permissions**: Always `chmod 400` on key files
5. **Backup keys**: Store key files in secure location (password manager, encrypted storage)

## Quick Reference

**Create key pair:**
```bash
aws ec2 create-key-pair --key-name locust-load-testing --query 'KeyMaterial' --output text > ~/.ssh/locust-load-testing.pem
chmod 400 ~/.ssh/locust-load-testing.pem
```

**List key pairs:**
```bash
aws ec2 describe-key-pairs
```

**Use in deployment:**
- When prompted, enter: `locust-load-testing` (or your key name)

That's it! You're ready to deploy.
