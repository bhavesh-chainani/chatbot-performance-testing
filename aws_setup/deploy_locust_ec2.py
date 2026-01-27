#!/usr/bin/env python3
"""
Deploy Locust Master and Workers on AWS EC2
Creates EC2 instances and sets them up for distributed load testing
"""
import boto3
import time
import sys
from botocore.exceptions import ClientError

def create_security_group(ec2, vpc_id, group_name="locust-load-testing"):
    """Create security group for Locust instances"""
    try:
        # Check if security group already exists
        response = ec2.describe_security_groups(
            Filters=[
                {'Name': 'group-name', 'Values': [group_name]},
                {'Name': 'vpc-id', 'Values': [vpc_id]}
            ]
        )
        
        if response['SecurityGroups']:
            print(f"Security group '{group_name}' already exists")
            return response['SecurityGroups'][0]['GroupId']
        
        # Create security group
        response = ec2.create_security_group(
            GroupName=group_name,
            Description='Security group for Locust load testing',
            VpcId=vpc_id
        )
        sg_id = response['GroupId']
        
        # Add inbound rules
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 8089,
                    'ToPort': 8089,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'Locust web UI'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 5557,
                    'ToPort': 5557,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'Locust master-worker communication'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH access'}]
                }
            ]
        )
        
        print(f"Created security group: {sg_id}")
        return sg_id
        
    except ClientError as e:
        print(f"Error creating security group: {e}")
        sys.exit(1)

def get_user_data_script(script_type="master"):
    """Get user data script for EC2 instance"""
    if script_type == "master":
        return """#!/bin/bash
yum update -y
yum install -y python3 python3-pip git
pip3 install locust pyyaml python-dotenv requests boto3
mkdir -p /home/ec2-user/chatbot-performance-testing
cd /home/ec2-user/chatbot-performance-testing
"""
    else:
        return """#!/bin/bash
yum update -y
yum install -y python3 python3-pip git
pip3 install locust pyyaml python-dotenv requests boto3
mkdir -p /home/ec2-user/chatbot-performance-testing
cd /home/ec2-user/chatbot-performance-testing
"""

def create_ec2_instances(ec2, instance_type, count, security_group_id, key_name=None, is_master=False):
    """Create EC2 instances for Locust"""
    user_data = get_user_data_script("master" if is_master else "worker")
    
    instances = []
    for i in range(count):
        try:
            response = ec2.run_instances(
                ImageId='ami-0c55b159cbfafe1f0',  # Amazon Linux 2 (update for your region)
                MinCount=1,
                MaxCount=1,
                InstanceType=instance_type,
                KeyName=key_name,
                SecurityGroupIds=[security_group_id],
                UserData=user_data,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'locust-{"master" if is_master else "worker"}-{i+1}'},
                            {'Key': 'Purpose', 'Value': 'load-testing'}
                        ]
                    }
                ]
            )
            instance_id = response['Instances'][0]['InstanceId']
            instances.append(instance_id)
            print(f"Created {'master' if is_master else 'worker'} instance: {instance_id}")
        except ClientError as e:
            print(f"Error creating instance: {e}")
    
    return instances

def get_vpc_id(ec2):
    """Get default VPC ID"""
    try:
        response = ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
        if response['Vpcs']:
            return response['Vpcs'][0]['VpcId']
        else:
            # Get first available VPC
            response = ec2.describe_vpcs()
            if response['Vpcs']:
                return response['Vpcs'][0]['VpcId']
    except ClientError as e:
        print(f"Error getting VPC: {e}")
        sys.exit(1)

def main():
    """Main deployment function"""
    print("=" * 60)
    print("Deploying Locust on AWS EC2")
    print("=" * 60)
    
    # Get AWS region
    session = boto3.Session()
    region = session.region_name or 'us-east-1'
    print(f"AWS Region: {region}")
    
    ec2 = boto3.client('ec2', region_name=region)
    
    # Get VPC ID
    vpc_id = get_vpc_id(ec2)
    print(f"Using VPC: {vpc_id}")
    
    # Create security group
    sg_id = create_security_group(ec2, vpc_id)
    
    # Configuration
    master_instance_type = input("Master instance type (default: t3.medium): ").strip() or "t3.medium"
    worker_instance_type = input("Worker instance type (default: t3.small): ").strip() or "t3.small"
    worker_count = int(input("Number of worker instances (default: 2): ").strip() or "2")
    key_name = input("EC2 Key Pair name (required for SSH): ").strip()
    
    if not key_name:
        print("Error: Key pair name is required for SSH access")
        sys.exit(1)
    
    # Create master instance
    print("\nCreating master instance...")
    master_instances = create_ec2_instances(
        ec2, master_instance_type, 1, sg_id, key_name, is_master=True
    )
    
    # Create worker instances
    print(f"\nCreating {worker_count} worker instances...")
    worker_instances = create_ec2_instances(
        ec2, worker_instance_type, worker_count, sg_id, key_name, is_master=False
    )
    
    print("\n" + "=" * 60)
    print("Instances created! Waiting for them to be running...")
    print("=" * 60)
    
    # Wait for instances to be running
    all_instances = master_instances + worker_instances
    waiter = ec2.get_waiter('instance_running')
    try:
        waiter.wait(InstanceIds=all_instances)
        print("All instances are running!")
    except Exception as e:
        print(f"Warning: {e}")
    
    # Get instance details
    response = ec2.describe_instances(InstanceIds=all_instances)
    
    print("\n" + "=" * 60)
    print("Instance Details")
    print("=" * 60)
    
    master_ip = None
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            public_ip = instance.get('PublicIpAddress', 'N/A')
            private_ip = instance.get('PrivateIpAddress', 'N/A')
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            name = tags.get('Name', 'Unknown')
            
            if 'master' in name:
                master_ip = private_ip
                print(f"\nMaster ({name}):")
            else:
                print(f"\nWorker ({name}):")
            
            print(f"  Instance ID: {instance_id}")
            print(f"  Public IP: {public_ip}")
            print(f"  Private IP: {private_ip}")
    
    print("\n" + "=" * 60)
    print("Next Steps")
    print("=" * 60)
    print("\n1. Copy your test files to the master instance:")
    print("   scp -r src/ config/ .env ec2-user@<master-public-ip>:/home/ec2-user/chatbot-performance-testing/")
    print("\n2. SSH into master instance:")
    print("   ssh ec2-user@<master-public-ip>")
    print("\n3. Start Locust master:")
    print(f"   cd /home/ec2-user/chatbot-performance-testing")
    print(f"   locust -f src/locustfile.py --master --host=https://your-chatbot-url.com")
    print("\n4. SSH into each worker and start workers:")
    print(f"   ssh ec2-user@<worker-public-ip>")
    print(f"   cd /home/ec2-user/chatbot-performance-testing")
    print(f"   locust -f src/locustfile.py --worker --master-host={master_ip}")
    print("\n5. Access Locust web UI:")
    print("   http://<master-public-ip>:8089")
    print("=" * 60)

if __name__ == "__main__":
    main()
