#!/usr/bin/env python3
"""
Script to retrieve AWS Cognito User Pool information
Helps identify Cognito configuration for authentication
"""
import boto3
import sys
from botocore.exceptions import ClientError

def get_cognito_info():
    """Get Cognito User Pool information"""
    try:
        cognito = boto3.client('cognito-idp')
        
        print("=" * 60)
        print("AWS Cognito User Pools")
        print("=" * 60)
        print()
        
        # List user pools
        try:
            response = cognito.list_user_pools(MaxResults=60)
            
            if response['UserPools']:
                for pool in response['UserPools']:
                    pool_id = pool['Id']
                    pool_name = pool['Name']
                    
                    print(f"User Pool: {pool_name}")
                    print(f"  Pool ID: {pool_id}")
                    
                    # Get pool details
                    try:
                        pool_details = cognito.describe_user_pool(UserPoolId=pool_id)
                        region = boto3.Session().region_name
                        print(f"  Region: {region}")
                        
                        # Get user pool clients
                        clients = cognito.list_user_pool_clients(UserPoolId=pool_id, MaxResults=60)
                        if clients['UserPoolClients']:
                            print(f"  Clients:")
                            for client in clients['UserPoolClients']:
                                client_id = client['ClientId']
                                client_name = client.get('ClientName', 'Unnamed')
                                print(f"    - {client_name}: {client_id}")
                        else:
                            print(f"  No clients found")
                        
                        print()
                    except ClientError as e:
                        print(f"  Error getting details: {e}")
                        print()
            else:
                print("No Cognito User Pools found")
                print()
                
        except ClientError as e:
            print(f"Error retrieving User Pools: {e}")
            print()
        
        print("=" * 60)
        print("To use Cognito authentication, update your .env file:")
        print("  AWS_COGNITO_USER_POOL_ID=<pool-id-from-above>")
        print("  AWS_COGNITO_CLIENT_ID=<client-id-from-above>")
        print("  AWS_COGNITO_REGION=<region-from-above>")
        print("  USE_AWS_COGNITO=true")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. AWS credentials are configured (run: aws configure)")
        print("2. You have permissions to list Cognito User Pools")
        print("3. You're in the correct AWS region")
        sys.exit(1)

if __name__ == "__main__":
    get_cognito_info()
