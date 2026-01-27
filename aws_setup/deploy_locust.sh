#!/bin/bash
# Deploy Locust cluster using CloudFormation
# This script creates EC2 instances for distributed load testing

set -e

echo "=========================================="
echo "Deploying Locust Cluster on AWS"
echo "=========================================="

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed"
    exit 1
fi

# Get region
AWS_REGION=${AWS_REGION:-$(aws configure get region)}
if [ -z "$AWS_REGION" ]; then
    echo "Error: AWS region not set. Run 'aws configure' or set AWS_REGION"
    exit 1
fi

echo "AWS Region: $AWS_REGION"

# Get parameters
read -p "Stack name (default: locust-cluster): " STACK_NAME
STACK_NAME=${STACK_NAME:-locust-cluster}

read -p "EC2 Key Pair name (required): " KEY_PAIR
if [ -z "$KEY_PAIR" ]; then
    echo "Error: Key pair name is required"
    exit 1
fi

read -p "Master instance type (default: t3.medium): " MASTER_TYPE
MASTER_TYPE=${MASTER_TYPE:-t3.medium}

read -p "Worker instance type (default: t3.small): " WORKER_TYPE
WORKER_TYPE=${WORKER_TYPE:-t3.small}

read -p "Number of workers (default: 2): " WORKER_COUNT
WORKER_COUNT=${WORKER_COUNT:-2}

# Get AMI ID for the region (Amazon Linux 2)
# Try to get latest AMI, fallback to hardcoded values if permission denied
AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" "Name=state,Values=available" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text \
    --region $AWS_REGION 2>/dev/null)

# If AMI lookup failed, use region-specific defaults
if [ -z "$AMI_ID" ] || [ "$AMI_ID" == "None" ]; then
    echo "Warning: Could not query AMI. Using default AMI IDs for region."
    echo "If deployment fails, you may need to add ec2:DescribeImages permission or specify AMI manually."
    
    # Common Amazon Linux 2 AMI IDs by region (update these if needed)
    case $AWS_REGION in
        us-east-1)
            AMI_ID="ami-0c55b159cbfafe1f0"  # N. Virginia
            ;;
        us-west-2)
            AMI_ID="ami-0c2ab3c8efb1f0a91"  # Oregon
            ;;
        eu-west-1)
            AMI_ID="ami-0c94864ba8d3946e7"  # Ireland
            ;;
        ap-southeast-1)
            AMI_ID="ami-0c7388116d47466e0"  # Singapore
            ;;
        *)
            echo "Error: Unknown region. Please specify AMI ID manually or add ec2:DescribeImages permission."
            echo "You can find AMI IDs at: https://aws.amazon.com/amazon-linux-2/release-notes/"
            exit 1
            ;;
    esac
fi

echo "Using AMI: $AMI_ID"

# Update CloudFormation template with correct AMI
sed "s/ami-0c55b159cbfafe1f0/$AMI_ID/g" aws_setup/cloudformation/locust-cluster.yaml > /tmp/locust-cluster.yaml

# Deploy CloudFormation stack
echo ""
echo "Deploying CloudFormation stack..."
aws cloudformation create-stack \
    --stack-name $STACK_NAME \
    --template-body file:///tmp/locust-cluster.yaml \
    --parameters \
        ParameterKey=InstanceTypeMaster,ParameterValue=$MASTER_TYPE \
        ParameterKey=InstanceTypeWorker,ParameterValue=$WORKER_TYPE \
        ParameterKey=WorkerCount,ParameterValue=$WORKER_COUNT \
        ParameterKey=KeyPairName,ParameterValue=$KEY_PAIR \
    --capabilities CAPABILITY_IAM \
    --region $AWS_REGION

echo ""
echo "Waiting for stack creation to complete..."
aws cloudformation wait stack-create-complete \
    --stack-name $STACK_NAME \
    --region $AWS_REGION

# Get outputs
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

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Master Public IP: $MASTER_IP"
echo "Master Private IP: $MASTER_PRIVATE_IP"
echo "Locust Web UI: http://$MASTER_IP:8089"
echo ""
echo "Next Steps:"
echo "1. Copy test files to master:"
echo "   scp -r src/ config/ .env ec2-user@$MASTER_IP:/home/ec2-user/chatbot-performance-testing/"
echo ""
echo "2. SSH into master and start Locust:"
echo "   ssh ec2-user@$MASTER_IP"
echo "   cd /home/ec2-user/chatbot-performance-testing"
echo "   locust -f src/locustfile.py --master --host=https://your-chatbot-url.com"
echo ""
echo "3. Get worker instance IPs:"
echo "   aws ec2 describe-instances --filters \"Name=tag:Name,Values=locust-worker-*\" --query 'Reservations[*].Instances[*].[PublicIpAddress,PrivateIpAddress]' --output table --region $AWS_REGION"
echo ""
echo "4. SSH into each worker and start:"
echo "   ssh ec2-user@<worker-ip>"
echo "   cd /home/ec2-user/chatbot-performance-testing"
echo "   locust -f src/locustfile.py --worker --master-host=$MASTER_PRIVATE_IP"
echo ""
echo "5. Access Locust web UI:"
echo "   http://$MASTER_IP:8089"
echo "=========================================="
