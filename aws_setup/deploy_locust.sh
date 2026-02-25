#!/bin/bash
# Deploy Locust on AWS – full-scale (1 master + workers)

set -e

echo "=========================================="
echo "  Deploy Locust on AWS (full-scale)"
echo "=========================================="
echo ""
echo "  Test profiles:"
echo "    load      – 500 users,  20 min"
echo "    stress    – 750 users,  20 min"
echo "    endurance – 500 users,  2 hours (70M token budget)"
echo "    breakpoint – ramp to 1000, 30 min"
echo ""

# -- Pre-flight ---------------------------------------------------------------

if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed"
    exit 1
fi

AWS_REGION=${AWS_REGION:-$(aws configure get region)}
if [ -z "$AWS_REGION" ]; then
    echo "Error: AWS region not set. Run 'aws configure' or set AWS_REGION"
    exit 1
fi

echo "AWS Region: $AWS_REGION"
echo ""

read -p "Stack name [locust-cluster]: " STACK_NAME
STACK_NAME=${STACK_NAME:-locust-cluster}

read -p "EC2 Key Pair name (required): " KEY_PAIR
if [ -z "$KEY_PAIR" ]; then
    echo "Error: Key pair name is required"
    exit 1
fi

read -p "Master instance type [c5.large]: " MASTER_TYPE
MASTER_TYPE=${MASTER_TYPE:-c5.large}

read -p "Worker instance type [c5.xlarge]: " WORKER_TYPE
WORKER_TYPE=${WORKER_TYPE:-c5.xlarge}

read -p "Number of workers (2-5, use 5 for 1000 users) [5]: " WORKER_COUNT
WORKER_COUNT=${WORKER_COUNT:-5}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# -- Resolve AMI (SSM = latest AL2, then fallbacks) --------------------------

AMI_ID=$(aws ssm get-parameters \
    --names /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2 \
    --query 'Parameters[0].Value' --output text \
    --region "$AWS_REGION" 2>/dev/null) || true

if [ -z "$AMI_ID" ] || [ "$AMI_ID" == "None" ]; then
    AMI_ID=$(aws ec2 describe-images \
        --owners amazon \
        --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" "Name=state,Values=available" \
        --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
        --output text \
        --region "$AWS_REGION" 2>/dev/null) || true
fi

if [ -z "$AMI_ID" ] || [ "$AMI_ID" == "None" ]; then
    case $AWS_REGION in
        us-east-1)      AMI_ID="ami-0c55b159cbfafe1f0" ;;
        us-west-2)      AMI_ID="ami-0c2ab3c8efb1f0a91" ;;
        eu-west-1)      AMI_ID="ami-0c94864ba8d3946e7" ;;
        ap-southeast-1) AMI_ID="ami-0c7388116d47466e0" ;;
        *)
            echo "Error: Unknown region. Set AMI manually or add ec2:DescribeImages."
            exit 1
            ;;
    esac
fi

echo "AMI: $AMI_ID"
echo "Deploying: 1x $MASTER_TYPE master + ${WORKER_COUNT}x $WORKER_TYPE workers"
echo ""

sed "s/ami-0c55b159cbfafe1f0/$AMI_ID/g" "$SCRIPT_DIR/cloudformation/locust-cluster-full.yaml" > /tmp/locust-cluster-full.yaml

aws cloudformation create-stack \
    --stack-name "$STACK_NAME" \
    --template-body file:///tmp/locust-cluster-full.yaml \
    --parameters \
        ParameterKey=InstanceTypeMaster,ParameterValue="$MASTER_TYPE" \
        ParameterKey=InstanceTypeWorker,ParameterValue="$WORKER_TYPE" \
        ParameterKey=WorkerCount,ParameterValue="$WORKER_COUNT" \
        ParameterKey=KeyPairName,ParameterValue="$KEY_PAIR" \
    --capabilities CAPABILITY_IAM \
    --region "$AWS_REGION"

echo "Waiting for stack creation (3-5 min)..."
if ! aws cloudformation wait stack-create-complete --stack-name "$STACK_NAME" --region "$AWS_REGION"; then
    echo ""
    echo "Stack creation failed (ROLLBACK_COMPLETE). Recent failures:"
    aws cloudformation describe-stack-events \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`].[LogicalResourceId,ResourceStatusReason]' \
        --output table 2>/dev/null || true
    echo ""
    echo "Full events: aws cloudformation describe-stack-events --stack-name $STACK_NAME --region $AWS_REGION"
    echo "Delete before retry: aws cloudformation delete-stack --stack-name $STACK_NAME --region $AWS_REGION"
    exit 1
fi

MASTER_IP=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`MasterPublicIP`].OutputValue' \
    --output text --region "$AWS_REGION")

MASTER_PRIVATE_IP=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`MasterPrivateIP`].OutputValue' \
    --output text --region "$AWS_REGION")

echo ""
echo "=========================================="
echo "  Deployment Complete"
echo "=========================================="
echo ""
echo "Master Public IP:  $MASTER_IP  (SSH + web UI)"
echo "Master Private IP: $MASTER_PRIVATE_IP  (use for workers: --master-host=$MASTER_PRIVATE_IP)"
echo "Locust Web UI:     http://$MASTER_IP:8089"
echo ""
echo "Next steps (see AWS_SETUP.md):"
echo ""
echo "1. Copy files to master:"
echo "   scp -i ~/.ssh/$KEY_PAIR.pem -r src/ config/ .env requirements.txt ec2-user@$MASTER_IP:~/chatbot-performance-testing/"
echo ""
echo "2. SSH to master, install deps, start master:"
echo "   ssh -i ~/.ssh/$KEY_PAIR.pem ec2-user@$MASTER_IP"
echo "   cd ~/chatbot-performance-testing && pip3 install -r requirements.txt"
echo "   TEST_TYPE=load locust -f src/locustfile.py --master"
echo ""
echo "3. Copy files to each worker, start worker on each:"
echo "   TEST_TYPE=load locust -f src/locustfile.py --worker --master-host=$MASTER_PRIVATE_IP"
echo ""
echo "4. Open web UI: http://$MASTER_IP:8089"
echo "=========================================="
