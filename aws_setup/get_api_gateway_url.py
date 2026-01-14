#!/usr/bin/env python3
"""
Script to retrieve AWS API Gateway URL
Helps identify the correct endpoint for your chatbot
"""
import boto3
import json
import sys
from botocore.exceptions import ClientError

def get_api_gateway_urls():
    """Get all API Gateway URLs in the current region"""
    try:
        apigateway = boto3.client('apigateway')
        apigatewayv2 = boto3.client('apigatewayv2')
        
        print("=" * 60)
        print("AWS API Gateway URLs")
        print("=" * 60)
        print()
        
        # Get REST APIs
        print("REST APIs:")
        print("-" * 60)
        try:
            rest_apis = apigateway.get_rest_apis()
            if rest_apis['items']:
                for api in rest_apis['items']:
                    api_id = api['id']
                    api_name = api['name']
                    region = boto3.Session().region_name
                    url = f"https://{api_id}.execute-api.{region}.amazonaws.com"
                    print(f"  Name: {api_name}")
                    print(f"  URL:  {url}")
                    print(f"  ID:   {api_id}")
                    print()
            else:
                print("  No REST APIs found")
                print()
        except ClientError as e:
            print(f"  Error retrieving REST APIs: {e}")
            print()
        
        # Get HTTP APIs (API Gateway v2)
        print("HTTP APIs (v2):")
        print("-" * 60)
        try:
            http_apis = apigatewayv2.get_apis()
            if http_apis['Items']:
                for api in http_apis['Items']:
                    api_id = api['ApiId']
                    api_name = api.get('Name', 'Unnamed')
                    api_endpoint = api.get('ApiEndpoint', '')
                    if api_endpoint:
                        print(f"  Name: {api_name}")
                        print(f"  URL:  {api_endpoint}")
                        print(f"  ID:   {api_id}")
                        print()
            else:
                print("  No HTTP APIs found")
                print()
        except ClientError as e:
            print(f"  Error retrieving HTTP APIs: {e}")
            print()
        
        print("=" * 60)
        print("To use one of these URLs, update your .env file:")
        print("  AWS_API_GATEWAY_URL=<url-from-above>")
        print("  CHATBOT_URL=<url-from-above>")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. AWS credentials are configured (run: aws configure)")
        print("2. You have permissions to list API Gateways")
        print("3. You're in the correct AWS region")
        sys.exit(1)

if __name__ == "__main__":
    get_api_gateway_urls()
