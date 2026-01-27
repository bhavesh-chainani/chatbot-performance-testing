#!/bin/bash
# Troubleshoot and find Locust instances

STACK_NAME=${1:-locust-cluster}
AWS_REGION=${AWS_REGION:-$(aws configure get region)}

if [ -z "$AWS_REGION" ]; then
    echo "Error: AWS region not set. Run 'aws configure' or set AWS_REGION"
    exit 1
fi

echo "=========================================="
echo "Troubleshooting Locust Instances"
echo "=========================================="
echo "Stack: $STACK_NAME"
echo "Region: $AWS_REGION"
echo ""

# Check if stack exists
echo "1. Checking CloudFormation stack..."
STACK_STATUS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].StackStatus' \
    --output text \
    --region $AWS_REGION 2>/dev/null)

if [ -z "$STACK_STATUS" ] || [ "$STACK_STATUS" == "None" ]; then
    echo "   ❌ Stack '$STACK_NAME' not found!"
    echo ""
    echo "   Available stacks:"
    aws cloudformation list-stacks \
        --query 'StackSummaries[?StackStatus!=`DELETE_COMPLETE`].[StackName,StackStatus]' \
        --output table \
        --region $AWS_REGION
    echo ""
    echo "   If stack name is different, run:"
    echo "   ./aws_setup/get_ips_simple.sh <your-stack-name>"
    exit 1
else
    echo "   ✅ Stack found: $STACK_STATUS"
fi

echo ""
echo "2. Getting CloudFormation outputs..."
OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs' \
    --output json \
    --region $AWS_REGION 2>/dev/null)

if [ -n "$OUTPUTS" ] && [ "$OUTPUTS" != "null" ] && [ "$OUTPUTS" != "[]" ]; then
    echo "$OUTPUTS" | python3 -m json.tool
    echo ""
    
    MASTER_IP=$(echo "$OUTPUTS" | python3 -c "import sys, json; data=json.load(sys.stdin); print([o['OutputValue'] for o in data if o['OutputKey']=='MasterPublicIP'][0] if any(o['OutputKey']=='MasterPublicIP' for o in data) else '')" 2>/dev/null)
    
    if [ -n "$MASTER_IP" ] && [ "$MASTER_IP" != "None" ]; then
        echo "=========================================="
        echo "✅ Found Master IP!"
        echo "=========================================="
        echo "Master Public IP: $MASTER_IP"
        echo ""
        echo "SSH Command:"
        echo "  ssh -i ~/.ssh/locust-load-testing.pem ec2-user@$MASTER_IP"
        echo ""
        
        MASTER_PRIVATE_IP=$(echo "$OUTPUTS" | python3 -c "import sys, json; data=json.load(sys.stdin); print([o['OutputValue'] for o in data if o['OutputKey']=='MasterPrivateIP'][0] if any(o['OutputKey']=='MasterPrivateIP' for o in data) else '')" 2>/dev/null)
        if [ -n "$MASTER_PRIVATE_IP" ]; then
            echo "Master Private IP (for workers): $MASTER_PRIVATE_IP"
        fi
        
        WEB_UI=$(echo "$OUTPUTS" | python3 -c "import sys, json; data=json.load(sys.stdin); print([o['OutputValue'] for o in data if o['OutputKey']=='LocustWebUI'][0] if any(o['OutputKey']=='LocustWebUI' for o in data) else '')" 2>/dev/null)
        if [ -n "$WEB_UI" ]; then
            echo "Locust Web UI: $WEB_UI"
        else
            echo "Locust Web UI: http://$MASTER_IP:8089"
        fi
        exit 0
    fi
fi

echo ""
echo "3. Checking stack resources..."
RESOURCES=$(aws cloudformation describe-stack-resources \
    --stack-name $STACK_NAME \
    --query 'StackResources[?ResourceType==`AWS::EC2::Instance`].[LogicalResourceId,PhysicalResourceId]' \
    --output table \
    --region $AWS_REGION 2>/dev/null)

if [ -n "$RESOURCES" ]; then
    echo "$RESOURCES"
    echo ""
    echo "If instances exist but no IPs shown, they may still be starting."
    echo "Wait a few minutes and try again."
else
    echo "   No EC2 instances found in stack resources."
fi

echo ""
echo "=========================================="
echo "Alternative: Check EC2 Console"
echo "=========================================="
echo "Go to: https://console.aws.amazon.com/ec2/v2/home?region=$AWS_REGION#Instances:"
echo "Look for instances with tags:"
echo "  - Name: locust-master"
echo "  - Name: locust-worker-*"
echo ""
