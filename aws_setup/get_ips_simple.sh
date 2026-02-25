#!/bin/bash
# Get master and worker IPs from CloudFormation stack (full-scale)

STACK_NAME=${1:-locust-cluster}
AWS_REGION=${AWS_REGION:-$(aws configure get region)}
KEY_PAIR=${KEY_PAIR:-locust-testing}

if [ -z "$AWS_REGION" ]; then
    echo "Error: AWS region not set. Run 'aws configure' or set AWS_REGION"
    exit 1
fi

echo "Stack: $STACK_NAME (region: $AWS_REGION)"
echo ""

STACK_STATUS=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].StackStatus' \
    --output text \
    --region "$AWS_REGION" 2>/dev/null)

if [ -z "$STACK_STATUS" ] || [ "$STACK_STATUS" == "None" ]; then
    echo "Error: Stack '$STACK_NAME' not found!"
    echo ""
    echo "Available stacks:"
    aws cloudformation list-stacks \
        --query 'StackSummaries[?StackStatus!=`DELETE_COMPLETE`].[StackName,StackStatus]' \
        --output table \
        --region "$AWS_REGION"
    echo ""
    echo "Usage: ./aws_setup/get_ips_simple.sh [stack-name]"
    exit 1
fi

if [ "$STACK_STATUS" == "CREATE_IN_PROGRESS" ] || [ "$STACK_STATUS" == "UPDATE_IN_PROGRESS" ]; then
    echo "Stack is still updating. Wait a few minutes and try again."
    exit 1
fi

MASTER_PUBLIC=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`MasterPublicIP`].OutputValue' \
    --output text \
    --region "$AWS_REGION")

MASTER_PRIVATE=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`MasterPrivateIP`].OutputValue' \
    --output text \
    --region "$AWS_REGION")

if [ -z "$MASTER_PUBLIC" ] || [ "$MASTER_PUBLIC" == "None" ]; then
    echo "Could not find master IP. Check stack name and region."
    exit 1
fi

echo "=========================================="
echo "  Master + workers"
echo "=========================================="
echo ""
echo "Master Public IP:  $MASTER_PUBLIC  (SSH + web UI)"
echo "Master Private IP: $MASTER_PRIVATE  (use for workers: --master-host=$MASTER_PRIVATE)"
echo ""
echo "Locust Web UI:     http://$MASTER_PUBLIC:8089"
echo ""
echo "SSH to master:"
echo "  ssh -i ~/.ssh/${KEY_PAIR}.pem ec2-user@$MASTER_PUBLIC"
echo ""
echo "Copy project to master:"
echo "  scp -i ~/.ssh/${KEY_PAIR}.pem -r src/ config/ .env requirements.txt ec2-user@$MASTER_PUBLIC:~/chatbot-performance-testing/"
echo ""
echo "On master:  TEST_TYPE=load locust -f src/locustfile.py --master"
echo "On workers: TEST_TYPE=load locust -f src/locustfile.py --worker --master-host=$MASTER_PRIVATE"
echo "=========================================="
echo ""
echo "Worker instances (for copying files / starting workers):"
aws ec2 describe-instances \
    --region "$AWS_REGION" \
    --filters "Name=tag:aws:cloudformation:stack-name,Values=$STACK_NAME" "Name=instance-state-name,Values=running" \
    --query 'Reservations[*].Instances[*].[Tags[?Key==`Name`].Value | [0], PublicIpAddress]' \
    --output text 2>/dev/null | while read -r name ip; do
    [ -n "$ip" ] && echo "  $name  $ip"
done
