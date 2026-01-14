# AWS Cost Estimation for Chatbot Performance Testing

This document provides detailed cost estimates for running performance tests on AWS-hosted chatbots.

## Cost Breakdown by AWS Service

### 1. API Gateway

**Free Tier:**
- 1 million API calls/month for first 12 months
- After free tier: $3.50 per million API calls

**Cost Calculation:**
```
Cost = (API Calls / 1,000,000) × $3.50
```

**Examples:**
- 10,000 requests: $0.035
- 100,000 requests: $0.35
- 1,000,000 requests: $3.50

### 2. AWS Lambda

**Free Tier:**
- 1 million requests/month
- 400,000 GB-seconds compute time/month

**Pricing After Free Tier:**
- $0.20 per 1 million requests
- $0.0000166667 per GB-second

**Cost Calculation:**
```
Request Cost = (Requests / 1,000,000) × $0.20
Compute Cost = (GB-seconds / 1,000,000) × $16.67
Total = Request Cost + Compute Cost
```

**Example:**
- 100,000 requests
- 1GB memory, 1 second average duration
- Compute: 100,000 × 1GB × 1s = 100,000 GB-seconds
- Request Cost: $0.02
- Compute Cost: $1.67
- **Total: $1.69**

### 3. CloudFront

**Free Tier:**
- 1TB data transfer out/month
- 10 million HTTP/HTTPS requests/month

**Pricing After Free Tier:**
- First 10TB: $0.085 per GB
- Next 40TB: $0.080 per GB
- Next 100TB: $0.060 per GB

**Cost Calculation:**
```
Cost = Data Transfer (GB) × Price per GB
```

**Example:**
- 10GB data transfer: $0.85
- 100GB data transfer: $8.50

### 4. EC2 Instances

**Free Tier:**
- 750 hours/month of t2.micro or t3.micro (first 12 months)

**Pricing After Free Tier (us-east-1):**
- t3.micro: $0.0104/hour
- t3.small: $0.0208/hour
- t3.medium: $0.0416/hour
- t3.large: $0.0832/hour

**Cost Calculation:**
```
Cost = Instance Hours × Hourly Rate
```

**Example:**
- t3.small running for 1 hour: $0.0208
- t3.small running for 24 hours: $0.50

### 5. ECS (Elastic Container Service)

**ECS itself is free**, but you pay for:
- EC2 instances running containers
- Fargate compute (if using Fargate)

**Fargate Pricing:**
- vCPU: $0.04048/hour
- Memory: $0.004445/GB-hour

**Example:**
- 0.5 vCPU, 1GB memory, 1 hour: $0.024

### 6. AWS Cognito

**Free Tier:**
- 50,000 Monthly Active Users (MAU)

**Pricing After Free Tier:**
- $0.0055 per MAU

**Cost Calculation:**
```
Cost = MAU × $0.0055
```

**Example:**
- 1,000 MAU: $5.50
- 10,000 MAU: $55.00

### 7. Data Transfer

**Free Tier:**
- 1GB out to internet/month (first 12 months)

**Pricing After Free Tier:**
- First 1GB/month: Free
- Next 9.999TB/month: $0.09 per GB
- Next 40TB/month: $0.085 per GB

## Real-World Test Scenarios

### Scenario 1: Small Load Test
**Configuration:**
- 5 concurrent users
- 2 minutes duration
- ~100 API requests total

**Costs:**
- API Gateway: $0.00 (free tier)
- Lambda: $0.00 (free tier)
- Data Transfer: $0.00 (free tier)
- **Total: $0.00**

### Scenario 2: Medium Load Test
**Configuration:**
- 10 concurrent users
- 5 minutes duration
- ~500 API requests total

**Costs:**
- API Gateway: $0.00 (free tier)
- Lambda: $0.00 (free tier)
- Data Transfer: $0.00 (free tier)
- **Total: $0.00**

### Scenario 3: Large Load Test
**Configuration:**
- 50 concurrent users
- 10 minutes duration
- ~5,000 API requests total

**Costs:**
- API Gateway: $0.00 (free tier)
- Lambda: $0.00 (free tier)
- Data Transfer: $0.00 (free tier)
- **Total: $0.00**

### Scenario 4: Stress Test
**Configuration:**
- 100 concurrent users
- 5 minutes duration
- ~10,000 API requests total

**Costs:**
- API Gateway: $0.00 (free tier)
- Lambda: $0.00 (free tier)
- Data Transfer: $0.00 (free tier)
- **Total: $0.00**

### Scenario 5: Breakpoint Test (High Load)
**Configuration:**
- Up to 500 concurrent users
- Multiple steps, 30 minutes total
- ~50,000 API requests total

**Costs:**
- API Gateway: $0.00 (free tier)
- Lambda: $0.00 (free tier)
- Data Transfer: $0.00 (free tier)
- **Total: $0.00**

### Scenario 6: Extended Endurance Test
**Configuration:**
- 20 concurrent users
- 1 hour duration
- ~50,000 API requests total

**Costs:**
- API Gateway: $0.00 (free tier)
- Lambda: $0.00 (free tier)
- Data Transfer: $0.00 (free tier)
- **Total: $0.00**

## Cost After Free Tier Expiration

### Example: Monthly Testing Schedule
**Assumptions:**
- 10 load tests/month
- 5 stress tests/month
- 2 endurance tests/month
- Average 10,000 requests per test
- Total: ~170,000 requests/month

**Costs:**
- API Gateway: 170,000 / 1,000,000 × $3.50 = **$0.60**
- Lambda: 170,000 / 1,000,000 × $0.20 = **$0.03**
- Compute (assuming 1GB, 1s): 170,000 GB-seconds × $0.0000166667 = **$2.83**
- **Total: ~$3.46/month**

### Example: Heavy Testing Schedule
**Assumptions:**
- 50 load tests/month
- 20 stress tests/month
- 10 endurance tests/month
- Average 50,000 requests per test
- Total: ~4,000,000 requests/month

**Costs:**
- API Gateway: 4,000,000 / 1,000,000 × $3.50 = **$14.00**
- Lambda: 4,000,000 / 1,000,000 × $0.20 = **$0.80**
- Compute (assuming 1GB, 1s): 4,000,000 GB-seconds × $0.0000166667 = **$66.67**
- **Total: ~$81.47/month**

## Cost Optimization Tips

1. **Use Free Tier**: Most testing fits within AWS free tier limits
2. **Choose Right Region**: Some regions have lower costs
3. **Monitor Usage**: Set up billing alerts
4. **Optimize Lambda**: Use appropriate memory allocation
5. **Use API Gateway Caching**: Reduce backend calls
6. **Schedule Tests**: Run during off-peak hours if possible

## Cost Monitoring

### Set Up Billing Alerts

1. Go to AWS Console → Billing → Preferences
2. Enable "Receive Billing Alerts"
3. Go to CloudWatch → Billing
4. Create alarm for estimated charges
5. Set threshold (e.g., $10)

### Use AWS Cost Explorer

1. Go to AWS Console → Cost Management → Cost Explorer
2. View costs by service
3. Filter by date range
4. Export reports

### Use AWS Budgets

1. Go to AWS Console → Budgets
2. Create budget
3. Set spending limit
4. Configure alerts

## Important Notes

1. **Free Tier**: Available for first 12 months after account creation
2. **Regional Pricing**: Costs vary by AWS region
3. **Data Transfer**: Can be significant if transferring large amounts
4. **Reserved Capacity**: Not applicable for testing scenarios
5. **Spot Instances**: Can reduce EC2 costs but not suitable for testing

## Disclaimer

Costs are estimates based on AWS pricing as of 2024. Actual costs may vary based on:
- Your specific AWS region
- Current AWS pricing
- Your chatbot's architecture
- Data transfer volumes
- Actual resource usage

Always check current AWS pricing: https://aws.amazon.com/pricing/
