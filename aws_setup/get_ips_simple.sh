#!/bin/bash
# Get instance IP from CloudFormation stack

STACK_NAME=${1:-locust-cluster}
AWS_REGION=${AWS_REGION:-$(aws configure get region)}

if [ -z "$AWS_REGION" ]; then
    echo "Error: AWS region not set. Run 'aws configure' or set AWS_REGION"
    exit 1
fi

echo "Getting instance IP from stack: $STACK_NAME"
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
    echo "Usage: ./aws_setup/get_ips_simple.sh <your-stack-name>"
    exit 1
fi

echo "Stack Status: $STACK_STATUS"
echo ""

if [ "$STACK_STATUS" == "CREATE_IN_PROGRESS" ]; then
    echo "Stack is still creating. Wait a few minutes and try again."
    exit 1
fi

INSTANCE_IP=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`InstancePublicIP`].OutputValue' \
    --output text \
    --region $AWS_REGION)

if [ -n "$INSTANCE_IP" ] && [ "$INSTANCE_IP" != "None" ]; then
    echo "=========================================="
    echo "Instance Public IP: $INSTANCE_IP"
    echo ""
    echo "SSH Command:"
    echo "  ssh -i ~/.ssh/locust-testing.pem ec2-user@$INSTANCE_IP"
    echo ""
    echo "Locust Web UI:"
    echo "  http://$INSTANCE_IP:8089"
    echo "=========================================="
else
    echo "Could not find instance IP. Check stack name and region."
fi
