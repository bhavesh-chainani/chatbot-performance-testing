# Cost Analysis for Chatbot Performance Testing Plan

**Date:** January 27, 2026  
**AWS Pricing:** Latest as of January 27, 2026

## Test Plan Summary

| Test Type | Runs | Concurrent Users (Max) | Duration per Run | Total Duration |
|-----------|------|------------------------|------------------|----------------|
| Load Test | 2 | 500 | ~20 minutes | 40 minutes |
| Stress Test | 2 | 750 | ~20 minutes | 40 minutes |
| Endurance Test | 2 | 500 | 8 hours | 16 hours |
| Breakpoint Test | 2 | Up to 1000 | 45-60 minutes | ~2 hours |
| **TOTAL** | **8 runs** | - | - | **~18.3 hours** |

## Infrastructure Requirements

### Locust Infrastructure (EC2 Instances)

For the maximum load (1000 concurrent users), we need:

**Recommended Setup:**
- **Master Instance**: 1x t3.large (2 vCPU, 8 GB RAM)
  - Can handle coordination of 1000+ users
  - Cost: ~$0.0832/hour (us-east-1)

- **Worker Instances**: 10x t3.small (2 vCPU, 2 GB RAM each)
  - Each worker handles ~100 users
  - Cost: ~$0.0208/hour each
  - Total workers: 10x = $0.208/hour

**Total Infrastructure Cost per Hour:**
- Master: $0.0832/hour
- Workers: $0.208/hour
- **Total: ~$0.29/hour**

### Scaling by Test Type

| Test Type | Max Users | Master | Workers | Cost/Hour |
|-----------|-----------|--------|---------|-----------|
| Load Test | 500 | t3.medium | 5x t3.small | $0.15 |
| Stress Test | 750 | t3.large | 8x t3.small | $0.25 |
| Endurance Test | 500 | t3.medium | 5x t3.small | $0.15 |
| Breakpoint Test | 1000 | t3.large | 10x t3.small | $0.29 |

## Detailed Cost Breakdown

### 1. Load Test (2 runs × 20 minutes)

**Infrastructure:**
- Master: 1x t3.medium = $0.0416/hour
- Workers: 5x t3.small = $0.104/hour
- **Total: $0.1456/hour**

**Duration:** 2 runs × 20 minutes = 40 minutes = 0.67 hours

**Cost:**
- EC2 Infrastructure: $0.1456/hour × 0.67 hours = **$0.10**
- For 2 runs: **$0.20**

### 2. Stress Test (2 runs × 20 minutes)

**Infrastructure:**
- Master: 1x t3.large = $0.0832/hour
- Workers: 8x t3.small = $0.1664/hour
- **Total: $0.2496/hour**

**Duration:** 2 runs × 20 minutes = 40 minutes = 0.67 hours

**Cost:**
- EC2 Infrastructure: $0.2496/hour × 0.67 hours = **$0.17**
- For 2 runs: **$0.34**

### 3. Endurance Test (2 runs × 8 hours)

**Infrastructure:**
- Master: 1x t3.medium = $0.0416/hour
- Workers: 5x t3.small = $0.104/hour
- **Total: $0.1456/hour**

**Duration:** 2 runs × 8 hours = 16 hours

**Cost:**
- EC2 Infrastructure: $0.1456/hour × 16 hours = **$2.33**
- For 2 runs: **$2.33**

### 4. Breakpoint Test (2 runs × 60 minutes)

**Infrastructure:**
- Master: 1x t3.large = $0.0832/hour
- Workers: 10x t3.small = $0.208/hour
- **Total: $0.2912/hour**

**Duration:** 2 runs × 60 minutes = 120 minutes = 2 hours

**Cost:**
- EC2 Infrastructure: $0.2912/hour × 2 hours = **$0.58**
- For 2 runs: **$0.58**

## Total EC2 Infrastructure Costs

| Test Type | Cost per Run | Runs | Total Cost |
|-----------|--------------|------|------------|
| Load Test | $0.10 | 2 | $0.20 |
| Stress Test | $0.17 | 2 | $0.34 |
| Endurance Test | $2.33 | 2 | $2.33 |
| Breakpoint Test | $0.58 | 2 | $1.16 |
| **TOTAL** | - | **8** | **$4.04** |

## Chatbot API Costs (If Using AWS Services)

### API Gateway Costs

**Assumptions:**
- Average 2 requests per user per minute
- Load Test: 500 users × 2 req/min × 20 min = 20,000 requests
- Stress Test: 750 users × 2 req/min × 20 min = 30,000 requests
- Endurance Test: 500 users × 2 req/min × 480 min = 480,000 requests
- Breakpoint Test: Average 500 users × 2 req/min × 60 min = 60,000 requests

**Total Requests:**
- Load Test (2 runs): 40,000 requests
- Stress Test (2 runs): 60,000 requests
- Endurance Test (2 runs): 960,000 requests
- Breakpoint Test (2 runs): 120,000 requests
- **Total: ~1,180,000 requests**

**API Gateway Pricing (as of Jan 2026):**
- First 1 million requests/month: **FREE** (if within free tier)
- After free tier: **$3.50 per million requests**

**Cost:**
- First 1M requests: $0.00
- Remaining 180,000 requests: (180,000 / 1,000,000) × $3.50 = **$0.63**

### Lambda Costs (If Chatbot Uses Lambda)

**Assumptions:**
- Average execution time: 2 seconds
- Memory: 1 GB
- 1,180,000 invocations

**Lambda Pricing (as of Jan 2026):**
- Requests: $0.20 per 1M requests
- Compute: $0.0000166667 per GB-second

**Cost Calculation:**
- Request cost: (1,180,000 / 1,000,000) × $0.20 = $0.24
- Compute cost: 1,180,000 × 1 GB × 2 seconds = 2,360,000 GB-seconds
- Compute cost: (2,360,000 / 1,000,000) × $16.67 = **$39.34**
- **Total Lambda: $39.58**

### CloudFront Costs (If Using CloudFront)

**Assumptions:**
- Average response size: 10 KB
- Total data transfer: 1,180,000 requests × 10 KB = 11.8 GB

**CloudFront Pricing (as of Jan 2026):**
- First 1 TB/month: **FREE** (if within free tier)
- After free tier: $0.085 per GB (first 10 TB)

**Cost:**
- 11.8 GB within free tier: **$0.00**

## Total Cost Summary

### Scenario 1: Only EC2 Infrastructure (Locust Testing)

| Component | Cost |
|-----------|------|
| EC2 Instances (Locust) | $4.04 |
| **TOTAL** | **$4.04** |

### Scenario 2: EC2 + API Gateway

| Component | Cost |
|-----------|------|
| EC2 Instances (Locust) | $4.04 |
| API Gateway | $0.63 |
| **TOTAL** | **$4.67** |

### Scenario 3: EC2 + API Gateway + Lambda

| Component | Cost |
|-----------|------|
| EC2 Instances (Locust) | $4.04 |
| API Gateway | $0.63 |
| Lambda | $79.14 |
| **TOTAL** | **$83.81** |

### Scenario 4: Full AWS Stack (EC2 + API Gateway + Lambda + CloudFront)

| Component | Cost |
|-----------|------|
| EC2 Instances (Locust) | $4.04 |
| API Gateway | $0.63 |
| Lambda | $79.14 |
| CloudFront | $0.00 (within free tier) |
| **TOTAL** | **$83.81** |

## Cost Breakdown by Test Type

### Load Test (2 runs)
- EC2: $0.20
- API Gateway: $0.07
- Lambda: $6.72
- **Subtotal: $6.99**

### Stress Test (2 runs)
- EC2: $0.34
- API Gateway: $0.11
- Lambda: $10.08
- **Subtotal: $10.53**

### Endurance Test (2 runs)
- EC2: $2.33
- API Gateway: $1.68
- Lambda: $161.28
- **Subtotal: $165.29**

### Breakpoint Test (2 runs)
- EC2: $1.16
- API Gateway: $0.21
- Lambda: $20.16
- **Subtotal: $21.53**

## Cost Optimization Recommendations

1. **Use Reserved Instances** (if testing monthly):
   - Can save up to 72% on EC2 costs
   - 1-year term: ~$1.16 instead of $4.03

2. **Use Spot Instances** (for non-critical tests):
   - Can save up to 90% on EC2 costs
   - Risk: Instances can be terminated
   - Estimated: ~$0.40 instead of $4.03

3. **Optimize Lambda**:
   - Reduce memory allocation if possible
   - Optimize execution time
   - Use provisioned concurrency for consistent performance

4. **Schedule Tests**:
   - Run during off-peak hours if possible
   - Batch tests together to maximize instance utilization

5. **Terminate Immediately**:
   - Always terminate instances immediately after tests
   - Don't leave them running overnight

## Monthly Cost Estimate (If Running This Plan Monthly)

**One-time per month:**
- EC2: $4.03
- API Gateway: $0.63
- Lambda: $39.58
- **Total: ~$44.24/month**

**With Reserved Instances (1-year term):**
- EC2: ~$1.16/month
- API Gateway: $0.63/month
- Lambda: $39.58/month
- **Total: ~$41.37/month**

## Important Notes

1. **Pricing is region-specific**: Costs shown are for us-east-1 (N. Virginia). Other regions may vary.

2. **Free Tier**: If within AWS free tier (first 12 months):
   - EC2: 750 hours/month of t2.micro/t3.micro
   - API Gateway: 1M requests/month
   - Lambda: 1M requests/month, 400K GB-seconds
   - **Potential savings: ~$4-5**

3. **Data Transfer**: Costs not included. Typically minimal for API testing.

4. **Storage**: EBS volumes for EC2 instances (~$0.10/GB/month) not included. Minimal for this use case.

5. **Actual costs may vary** based on:
   - Actual request patterns
   - Response sizes
   - Lambda execution time
   - Region selection

## Cost Monitoring

Set up AWS Cost Explorer and billing alerts:
- Alert threshold: $50/month (to catch unexpected costs)
- Monitor daily spending
- Review after each test run

## Summary

**Most Likely Scenario (EC2 + API Gateway + Lambda):**
- **Total Cost: ~$83.81** for complete test plan
- **Per Test Run Average: ~$10.48**
- **Most Expensive:** Endurance Test ($66.73 for 2 runs)
- **Least Expensive:** Load Test ($2.88 for 2 runs)

**If only using EC2 for Locust infrastructure:**
- **Total Cost: ~$4.04** for complete test plan
