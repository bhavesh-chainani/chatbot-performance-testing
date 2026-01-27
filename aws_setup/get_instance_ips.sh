#!/bin/bash
# Get EC2 instance IPs for Locust cluster

STACK_NAME=${1:-locust-cluster}
AWS_REGION=${AWS_REGION:-$(aws configure get region)}

if [ -z "$AWS_REGION" ]; then
    echo "Error: AWS region not set. Run 'aws configure' or set AWS_REGION"
    exit 1
fi

echo "=========================================="
echo "Locust Cluster Instance IPs"
echo "=========================================="
echo "Stack: $STACK_NAME"
echo "Region: $AWS_REGION"
echo ""

# Try CloudFormation first (doesn't require ec2:DescribeInstances)
MASTER_IP=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`MasterPublicIP`].OutputValue' \
    --output text \
    --region $AWS_REGION 2>/dev/null)

if [ -n "$MASTER_IP" ] && [ "$MASTER_IP" != "None" ]; then
    echo "Master Instance:"
    echo "  Public IP: $MASTER_IP"
    
    MASTER_PRIVATE_IP=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query 'Stacks[0].Outputs[?OutputKey==`MasterPrivateIP`].OutputValue' \
        --output text \
        --region $AWS_REGION)
    echo "  Private IP: $MASTER_PRIVATE_IP"
    echo ""
    
    echo "SSH Command:"
    echo "  ssh -i ~/.ssh/locust-load-testing.pem ec2-user@$MASTER_IP"
    echo ""
    
    echo "Worker Instances:"
    aws ec2 describe-instances \
        --filters "Name=tag:Name,Values=locust-worker-*" "Name=instance-state-name,Values=running" \
        --query 'Reservations[*].Instances[*].[Tags[?Key==`Name`].Value|[0],PublicIpAddress,PrivateIpAddress]' \
        --output table \
        --region $AWS_REGION
else
    # Fallback: query by tags (requires ec2:DescribeInstances permission)
    echo "Querying instances by tags..."
    echo ""
    
    # Check if we have permission
    if ! aws ec2 describe-instances --filters "Name=tag:Name,Values=locust-master" --max-items 1 --region $AWS_REGION &>/dev/null; then
        echo "Error: Missing ec2:DescribeInstances permission"
        echo ""
        echo "Quick fix:"
        echo "1. Go to IAM Console → Users → chatbot-testing-user"
        echo "2. Add policy: AmazonEC2FullAccess"
        echo ""
        echo "Or see: docs/IAM_PERMISSIONS.md for custom policy"
        echo ""
        echo "Alternative: Get IPs from CloudFormation outputs:"
        echo "  aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs' --region $AWS_REGION"
        exit 1
    fi
    
    echo "Master Instance:"
    aws ec2 describe-instances \
        --filters "Name=tag:Name,Values=locust-master" "Name=instance-state-name,Values=running" \
        --query 'Reservations[*].Instances[*].[InstanceId,PublicIpAddress,PrivateIpAddress]' \
        --output table \
        --region $AWS_REGION
    
    echo ""
    echo "Worker Instances:"
    aws ec2 describe-instances \
        --filters "Name=tag:Name,Values=locust-worker-*" "Name=instance-state-name,Values=running" \
        --query 'Reservations[*].Instances[*].[InstanceId,PublicIpAddress,PrivateIpAddress]' \
        --output table \
        --region $AWS_REGION
fi

echo ""
echo "=========================================="
