#!/bin/bash
# Deploy Locust cluster on AWS for chatbot performance testing
# Sized for 500-1000 concurrent users (load / stress / endurance / breakpoint)

set -e

echo "=========================================="
echo "  Deploy Locust Cluster on AWS"
echo "=========================================="
echo ""
echo "Test profiles this cluster supports:"
echo "  load       – 500 users,  20 min"
echo "  stress     – 750 users,  20 min"
echo "  endurance  – 500 users,  8 hours"
echo "  breakpoint – ramp to 1000, 30 min"
echo ""

# -- Pre-flight checks -------------------------------------------------------

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

# -- Parameters ---------------------------------------------------------------

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

read -p "Number of workers (2 for 500 users, 3 for 750, 4 for 1000) [3]: " WORKER_COUNT
WORKER_COUNT=${WORKER_COUNT:-3}

echo ""
echo "Cluster: 1x $MASTER_TYPE master + ${WORKER_COUNT}x $WORKER_TYPE workers"

# -- Resolve AMI for the region -----------------------------------------------

AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" "Name=state,Values=available" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text \
    --region "$AWS_REGION" 2>/dev/null)

if [ -z "$AMI_ID" ] || [ "$AMI_ID" == "None" ]; then
    echo "Warning: Could not query AMI. Using region defaults."
    case $AWS_REGION in
        us-east-1)      AMI_ID="ami-0c55b159cbfafe1f0" ;;
        us-west-2)      AMI_ID="ami-0c2ab3c8efb1f0a91" ;;
        eu-west-1)      AMI_ID="ami-0c94864ba8d3946e7" ;;
        ap-southeast-1) AMI_ID="ami-0c7388116d47466e0" ;;
        *)
            echo "Error: Unknown region – specify AMI manually."
            exit 1
            ;;
    esac
fi

echo "AMI: $AMI_ID"

# -- Deploy CloudFormation ----------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
sed "s/ami-0c55b159cbfafe1f0/$AMI_ID/g" "$SCRIPT_DIR/cloudformation/locust-cluster.yaml" > /tmp/locust-cluster.yaml

echo ""
echo "Deploying CloudFormation stack..."
aws cloudformation create-stack \
    --stack-name "$STACK_NAME" \
    --template-body file:///tmp/locust-cluster.yaml \
    --parameters \
        ParameterKey=InstanceTypeMaster,ParameterValue="$MASTER_TYPE" \
        ParameterKey=InstanceTypeWorker,ParameterValue="$WORKER_TYPE" \
        ParameterKey=WorkerCount,ParameterValue="$WORKER_COUNT" \
        ParameterKey=KeyPairName,ParameterValue="$KEY_PAIR" \
    --capabilities CAPABILITY_IAM \
    --region "$AWS_REGION"

echo "Waiting for stack creation..."
aws cloudformation wait stack-create-complete \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION"

# -- Print outputs ------------------------------------------------------------

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
echo "  Deployment Complete!"
echo "=========================================="
echo ""
echo "Master Public IP:  $MASTER_IP"
echo "Master Private IP: $MASTER_PRIVATE_IP"
echo "Locust Web UI:     http://$MASTER_IP:8089"
echo ""
echo "Next steps – see SIMPLE_SETUP.md for full guide:"
echo ""
echo "1. Copy files to master:"
echo "   scp -i ~/.ssh/$KEY_PAIR.pem -r src/ config/ .env requirements.txt \\"
echo "       ec2-user@$MASTER_IP:/home/ec2-user/chatbot-performance-testing/"
echo ""
echo "2. SSH into master:"
echo "   ssh -i ~/.ssh/$KEY_PAIR.pem ec2-user@$MASTER_IP"
echo ""
echo "3. Start master (pick a test type):"
echo "   cd /home/ec2-user/chatbot-performance-testing"
echo "   TEST_TYPE=load locust -f src/locustfile.py --master"
echo ""
echo "4. On each worker:"
echo "   TEST_TYPE=load locust -f src/locustfile.py --worker --master-host=$MASTER_PRIVATE_IP"
echo ""
echo "5. Open web UI: http://$MASTER_IP:8089"
echo "=========================================="
