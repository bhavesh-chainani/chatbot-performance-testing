# IAM Permissions Setup

Required IAM permissions for deploying and running Locust on AWS EC2.

## Required Permissions

Your IAM user needs these permissions:

### EC2 Permissions
- `ec2:DescribeImages` - To find Amazon Linux 2 AMI
- `ec2:DescribeInstances` - To check instance status
- `ec2:DescribeVpcs` - To find default VPC
- `ec2:DescribeSecurityGroups` - To check/create security groups
- `ec2:CreateSecurityGroup` - To create security group
- `ec2:AuthorizeSecurityGroupIngress` - To add security group rules
- `ec2:RunInstances` - To launch EC2 instances
- `ec2:TerminateInstances` - To stop instances (for cleanup)
- `ec2:CreateTags` - To tag instances
- `ec2:DescribeKeyPairs` - To verify key pairs

### CloudFormation Permissions (if using CloudFormation)
- `cloudformation:CreateStack`
- `cloudformation:DescribeStacks`
- `cloudformation:DeleteStack`
- `cloudformation:DescribeStackEvents`

## Quick Fix: Add Permissions

### Option 1: Attach AWS Managed Policies (Easiest)

1. **Go to IAM Console**
   - Navigate to: https://console.aws.amazon.com/iam/
   - Click "Users" → Select your user (`chatbot-testing-user`)

2. **Add EC2 Policy**
   - Click "Add permissions" → "Attach policies directly"
   - Search for and select: **`AmazonEC2FullAccess`**
   - Click "Next" → "Add permissions"

3. **Add CloudFormation Policy**
   - Click "Add permissions" again → "Attach policies directly"
   - Search for and select: **`AWSCloudFormationFullAccess`**
   - Click "Next" → "Add permissions"

**Note**: These give full access. For production, use custom policy below.

### Option 2: Custom Policy (Recommended)

1. **Create Custom Policy**
   - Go to IAM → Policies → "Create policy"
   - Click "JSON" tab
   - Paste the policy below:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeImages",
                "ec2:DescribeInstances",
                "ec2:DescribeVpcs",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeKeyPairs",
                "ec2:CreateSecurityGroup",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:RunInstances",
                "ec2:TerminateInstances",
                "ec2:CreateTags"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "cloudformation:CreateStack",
                "cloudformation:DescribeStacks",
                "cloudformation:DeleteStack",
                "cloudformation:DescribeStackEvents"
            ],
            "Resource": "*"
        }
    ]
}
```

2. **Name the Policy**
   - Name: `LocustLoadTestingPolicy`
   - Description: "Permissions for Locust load testing on EC2"
   - Click "Create policy"

3. **Attach to User**
   - Go to Users → `chatbot-testing-user`
   - Click "Add permissions" → "Attach policies directly"
   - Search for `LocustLoadTestingPolicy`
   - Select and attach

### Option 3: AWS CLI (Quick Fix)

**Add both policies via CLI:**

```bash
# Attach EC2 policy
aws iam attach-user-policy \
    --user-name chatbot-testing-user \
    --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess

# Attach CloudFormation policy
aws iam attach-user-policy \
    --user-name chatbot-testing-user \
    --policy-arn arn:aws:iam::aws:policy/AWSCloudFormationFullAccess
```

**Or create custom policy:**

```bash
# Create policy file
cat > locust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeImages",
                "ec2:DescribeInstances",
                "ec2:DescribeVpcs",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeKeyPairs",
                "ec2:CreateSecurityGroup",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:RunInstances",
                "ec2:TerminateInstances",
                "ec2:CreateTags"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "cloudformation:CreateStack",
                "cloudformation:DescribeStacks",
                "cloudformation:DeleteStack",
                "cloudformation:DescribeStackEvents"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Create policy
aws iam create-policy \
    --policy-name LocustLoadTestingPolicy \
    --policy-document file://locust-policy.json

# Attach to user (replace ACCOUNT_ID with your account ID)
aws iam attach-user-policy \
    --user-name chatbot-testing-user \
    --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/LocustLoadTestingPolicy
```

## Verify Permissions

Test if permissions are working:

```bash
# Test EC2 permissions
aws ec2 describe-images --owners amazon --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" --query 'Images[0].ImageId' --output text

# Test CloudFormation permissions
aws cloudformation list-stacks --max-items 1
```

If these commands work, you're good to go!

## Workaround: Use Hardcoded AMI

If you can't add permissions, the deployment script will use hardcoded AMI IDs for common regions. If your region isn't supported, you can:

1. **Find AMI ID manually:**
   - Go to: https://aws.amazon.com/amazon-linux-2/release-notes/
   - Find your region's AMI ID
   - Or use AWS Console → EC2 → Launch Instance → Amazon Linux 2 → Copy AMI ID

2. **Edit deployment script:**
   - Open `aws_setup/deploy_locust.sh`
   - Find the region case statement
   - Add your region and AMI ID

3. **Or edit CloudFormation template:**
   - Open `aws_setup/cloudformation/locust-cluster.yaml`
   - Replace `ami-0c55b159cbfafe1f0` with your region's AMI ID

## Common AMI IDs (Amazon Linux 2)

Update these in the deployment script if needed:

- **us-east-1** (N. Virginia): `ami-0c55b159cbfafe1f0`
- **us-west-2** (Oregon): `ami-0c2ab3c8efb1f0a91`
- **eu-west-1** (Ireland): `ami-0c94864ba8d3946e7`
- **ap-southeast-1** (Singapore): `ami-0c7388116d47466e0`

Find latest AMIs: https://aws.amazon.com/amazon-linux-2/release-notes/

## Troubleshooting

### "Access Denied" errors

1. **Check policy attachment:**
   ```bash
   aws iam list-attached-user-policies --user-name chatbot-testing-user
   ```

2. **Verify policy permissions:**
   - Go to IAM → Policies → Your policy
   - Check JSON tab matches requirements above

3. **Wait a few minutes** - IAM changes can take 1-2 minutes to propagate

### Still having issues?

- Use AWS Console to attach `AmazonEC2FullAccess` (temporary, for testing)
- Or ask your AWS admin to add the required permissions

## Security Best Practices

For production:
- Use least-privilege principle (custom policy above)
- Restrict resources to specific VPCs/regions if possible
- Use IAM roles instead of user credentials when possible
- Rotate access keys regularly
