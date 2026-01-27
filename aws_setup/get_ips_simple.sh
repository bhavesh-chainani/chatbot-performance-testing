#!/bin/bash
# Simple script to get instance IPs using CloudFormation (no EC2 permissions needed)

STACK_NAME=${1:-locust-cluster}
AWS_REGION=${AWS_REGION:-$(aws configure get region)}

if [ -z "$AWS_REGION" ]; then
    echo "Error: AWS region not set. Run 'aws configure' or set AWS_REGION"
    exit 1
fi

echo "Getting instance IPs from CloudFormation stack: $STACK_NAME"
echo ""

# Check if stack exists
STACK_STATUS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].StackStatus' \
    --output text \
    --region $AWS_REGION 2>/dev/null)

if [ -z "$STACK_STATUS" ] || [ "$STACK_STATUS" == "None" ]; then
    echo "Error: Stack '$STACK_NAME' not found!"
    echo ""
    echo "Available stacks:"
    aws cloudformation list-stacks \
        --query 'StackSummaries[?StackStatus!=`DELETE_COMPLETE`].[StackName,StackStatus]' \
        --output table \
        --region $AWS_REGION
    echo ""
    echo "If your stack has a different name, run:"
    echo "  ./aws_setup/get_ips_simple.sh <your-stack-name>"
    exit 1
fi

echo "Stack Status: $STACK_STATUS"
echo ""

# Get all outputs
OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs' \
    --output json \
    --region $AWS_REGION 2>/dev/null)

if [ -z "$OUTPUTS" ] || [ "$OUTPUTS" == "null" ] || [ "$OUTPUTS" == "[]" ]; then
    echo "⚠️  No outputs found. Stack may still be creating..."
    echo ""
    echo "Check stack status:"
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query 'Stacks[0].[StackStatus,StackStatusReason]' \
        --output table \
        --region $AWS_REGION
    echo ""
    echo "If stack is CREATE_IN_PROGRESS, wait a few minutes and try again."
    echo "Or run: ./aws_setup/troubleshoot_instances.sh"
    exit 1
fi

echo "$OUTPUTS" | python3 -m json.tool 2>/dev/null || echo "$OUTPUTS"

echo ""
echo "=========================================="
echo "SSH Commands:"
echo "=========================================="

MASTER_IP=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`MasterPublicIP`].OutputValue' \
    --output text \
    --region $AWS_REGION)

MASTER_PRIVATE_IP=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`MasterPrivateIP`].OutputValue' \
    --output text \
    --region $AWS_REGION)

if [ -n "$MASTER_IP" ] && [ "$MASTER_IP" != "None" ]; then
    echo "Master SSH:"
    echo "  ssh -i ~/.ssh/locust-load-testing.pem ec2-user@$MASTER_IP"
    echo ""
    echo "Master Private IP (for workers):"
    echo "  $MASTER_PRIVATE_IP"
    echo ""
    echo "Locust Web UI:"
    echo "  http://$MASTER_IP:8089"
else
    echo "Could not find master IP. Check stack name and region."
fi
