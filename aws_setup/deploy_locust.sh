#!/bin/bash
# Deploy a single EC2 instance for chatbot performance testing
# Sized for simple tests: 10-20 concurrent users

set -e

echo "=========================================="
echo "  Deploy Locust on AWS (Single Instance)"
echo "=========================================="
echo ""
echo "Test profiles:"
echo "  load       – 10 users,  5 min"
echo "  stress     – 10 users,  5 min"
echo "  endurance  – 10 users, 10 min"
echo "  breakpoint – ramp to 20, 5 min"
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

read -p "Instance type [t3.small]: " INSTANCE_TYPE
INSTANCE_TYPE=${INSTANCE_TYPE:-t3.small}

echo ""
echo "Deploying: 1x $INSTANCE_TYPE (standalone, no workers needed)"

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
        ParameterKey=InstanceType,ParameterValue="$INSTANCE_TYPE" \
        ParameterKey=KeyPairName,ParameterValue="$KEY_PAIR" \
    --capabilities CAPABILITY_IAM \
    --region "$AWS_REGION"

echo "Waiting for stack creation..."
aws cloudformation wait stack-create-complete \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION"

# -- Print outputs ------------------------------------------------------------

INSTANCE_IP=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`InstancePublicIP`].OutputValue' \
    --output text --region "$AWS_REGION")

echo ""
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo ""
echo "Instance IP:   $INSTANCE_IP"
echo "Locust Web UI: http://$INSTANCE_IP:8089"
echo ""
echo "Next steps:"
echo ""
echo "1. Copy files:"
echo "   scp -i ~/.ssh/$KEY_PAIR.pem -r src/ config/ .env requirements.txt \\"
echo "       ec2-user@$INSTANCE_IP:~/chatbot-performance-testing/"
echo ""
echo "2. SSH in:"
echo "   ssh -i ~/.ssh/$KEY_PAIR.pem ec2-user@$INSTANCE_IP"
echo ""
echo "3. Run a test (no --master/--worker needed):"
echo "   cd ~/chatbot-performance-testing"
echo "   TEST_TYPE=load locust -f src/locustfile.py"
echo ""
echo "4. Open web UI: http://$INSTANCE_IP:8089"
echo "=========================================="
