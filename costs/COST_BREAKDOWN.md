# Detailed Cost Breakdown - Chatbot Performance Testing

**Date:** January 27, 2026  
**AWS Pricing:** Latest as of January 27, 2026

## Executive Summary

**Total Estimated Cost: $44.24** (for complete test plan)

Breakdown:
- EC2 Infrastructure (Locust): $4.03
- API Gateway: $0.63
- Lambda (if applicable): $39.58

## Test Plan Overview

| Test Type | Runs | Max Users | Duration | Total Time |
|-----------|------|-----------|----------|------------|
| Load | 2 | 500 | 20 min | 40 min |
| Stress | 2 | 750 | 20 min | 40 min |
| Endurance | 2 | 500 | 8 hours | 16 hours |
| Breakpoint | 2 | 1000 | 60 min | 120 min |
| **TOTAL** | **8** | - | - | **18.3 hours** |

## Infrastructure Sizing

### EC2 Instance Requirements

**Load Test (500 users):**
- Master: t3.medium (2 vCPU, 4 GB)
- Workers: 5x t3.small (2 vCPU, 2 GB each)
- Total: 1 master + 5 workers

**Stress Test (750 users):**
- Master: t3.large (2 vCPU, 8 GB)
- Workers: 8x t3.small (2 vCPU, 2 GB each)
- Total: 1 master + 8 workers

**Endurance Test (500 users):**
- Master: t3.medium (2 vCPU, 4 GB)
- Workers: 5x t3.small (2 vCPU, 2 GB each)
- Total: 1 master + 5 workers

**Breakpoint Test (up to 1000 users):**
- Master: t3.large (2 vCPU, 8 GB)
- Workers: 10x t3.small (2 vCPU, 2 GB each)
- Total: 1 master + 10 workers

## AWS Pricing (us-east-1, January 2026)

### EC2 On-Demand Pricing

| Instance Type | vCPU | RAM | Price/Hour |
|---------------|------|-----|------------|
| t3.medium | 2 | 4 GB | $0.0416 |
| t3.large | 2 | 8 GB | $0.0832 |
| t3.small | 2 | 2 GB | $0.0208 |

### API Gateway Pricing

- First 1M requests/month: **FREE**
- After free tier: **$3.50 per million requests**

### Lambda Pricing

- Requests: **$0.20 per 1M requests**
- Compute: **$0.0000166667 per GB-second**

## Detailed Cost Calculation

### 1. Load Test Costs

**Infrastructure:**
- Master (t3.medium): $0.0416/hour × 0.67 hours = $0.028
- Workers (5x t3.small): $0.104/hour × 0.67 hours = $0.070
- **EC2 Subtotal: $0.098**

**For 2 runs: $0.20**

**API Requests:**
- 500 users × 2 req/min × 20 min = 20,000 requests per run
- 2 runs = 40,000 requests
- Cost: FREE (within 1M/month free tier)

**Lambda (if applicable):**
- 40,000 invocations × 2 seconds × 1 GB = 80,000 GB-seconds
- Request cost: (40,000 / 1M) × $0.20 = $0.008
- Compute cost: (80,000 / 1M) × $16.67 = $1.33
- **Lambda Subtotal: $1.34**

**Total Load Test (2 runs):**
- EC2: $0.20
- API Gateway: $0.00
- Lambda: $2.68
- **Total: $2.88**

### 2. Stress Test Costs

**Infrastructure:**
- Master (t3.large): $0.0832/hour × 0.67 hours = $0.056
- Workers (8x t3.small): $0.1664/hour × 0.67 hours = $0.111
- **EC2 Subtotal: $0.167**

**For 2 runs: $0.33**

**API Requests:**
- 750 users × 2 req/min × 20 min = 30,000 requests per run
- 2 runs = 60,000 requests
- Cost: FREE (within 1M/month free tier)

**Lambda (if applicable):**
- 60,000 invocations × 2 seconds × 1 GB = 120,000 GB-seconds
- Request cost: (60,000 / 1M) × $0.20 = $0.012
- Compute cost: (120,000 / 1M) × $16.67 = $2.00
- **Lambda Subtotal: $2.01**

**Total Stress Test (2 runs):**
- EC2: $0.33
- API Gateway: $0.00
- Lambda: $4.02
- **Total: $4.35**

### 3. Endurance Test Costs

**Infrastructure:**
- Master (t3.medium): $0.0416/hour × 16 hours = $0.67
- Workers (5x t3.small): $0.104/hour × 16 hours = $1.66
- **EC2 Subtotal: $2.33**

**For 2 runs: $2.33** (same infrastructure reused)

**API Requests:**
- 500 users × 2 req/min × 480 min = 480,000 requests per run
- 2 runs = 960,000 requests
- Cost: FREE (within 1M/month free tier)

**Lambda (if applicable):**
- 960,000 invocations × 2 seconds × 1 GB = 1,920,000 GB-seconds
- Request cost: (960,000 / 1M) × $0.20 = $0.192
- Compute cost: (1,920,000 / 1M) × $16.67 = $32.01
- **Lambda Subtotal: $32.20**

**Total Endurance Test (2 runs):**
- EC2: $2.33
- API Gateway: $0.00
- Lambda: $64.40
- **Total: $66.73**

### 4. Breakpoint Test Costs

**Infrastructure:**
- Master (t3.large): $0.0832/hour × 2 hours = $0.17
- Workers (10x t3.small): $0.208/hour × 2 hours = $0.42
- **EC2 Subtotal: $0.59**

**For 2 runs: $1.18**

**API Requests:**
- Average 500 users × 2 req/min × 60 min = 60,000 requests per run
- 2 runs = 120,000 requests
- Cost: FREE (within 1M/month free tier)

**Lambda (if applicable):**
- 120,000 invocations × 2 seconds × 1 GB = 240,000 GB-seconds
- Request cost: (120,000 / 1M) × $0.20 = $0.024
- Compute cost: (240,000 / 1M) × $16.67 = $4.00
- **Lambda Subtotal: $4.02**

**Total Breakpoint Test (2 runs):**
- EC2: $1.18
- API Gateway: $0.00
- Lambda: $8.04
- **Total: $9.22**

## Complete Cost Summary

### By Test Type

| Test Type | EC2 | API Gateway | Lambda | Total |
|-----------|-----|-------------|---------|-------|
| Load (2 runs) | $0.20 | $0.00 | $2.68 | $2.88 |
| Stress (2 runs) | $0.33 | $0.00 | $4.02 | $4.35 |
| Endurance (2 runs) | $2.33 | $0.00 | $64.40 | $66.73 |
| Breakpoint (2 runs) | $1.18 | $0.00 | $8.04 | $9.22 |
| **TOTAL** | **$4.04** | **$0.00** | **$79.14** | **$83.18** |

### Cost Scenarios

**Scenario A: EC2 Only (Locust Infrastructure)**
- **Total: $4.04**

**Scenario B: EC2 + API Gateway**
- EC2: $4.04
- API Gateway: $0.00 (within free tier)
- **Total: $4.04**

**Scenario C: EC2 + API Gateway + Lambda**
- EC2: $4.04
- API Gateway: $0.00
- Lambda: $79.14
- **Total: $83.18**

**Scenario D: If API Gateway Exceeds Free Tier**
- EC2: $4.04
- API Gateway: ~$0.63 (if 1.18M requests)
- Lambda: $79.14
- **Total: $83.81**

## Cost Optimization Options

### Option 1: Reserved Instances (1-Year Term)

**EC2 Savings:**
- Standard Reserved: ~72% savings
- EC2 cost: $4.04 → **~$1.13**
- **Total: $80.27** (saves $2.91)

### Option 2: Spot Instances

**EC2 Savings:**
- Spot pricing: ~70-90% savings
- EC2 cost: $4.04 → **~$0.40-1.20**
- **Total: $79.54-80.34** (saves $2.84-3.64)
- **Risk:** Instances can be terminated

### Option 3: Optimize Lambda

**If Lambda execution time reduced to 1 second:**
- Current: $79.14
- Optimized: $39.57
- **Savings: $39.57**
- **Total: $43.61**

### Option 4: Combine Tests (Reduce Setup Time)

**If running all tests in sequence:**
- Setup overhead: ~10 minutes
- Can reuse same infrastructure
- **Savings: Minimal (~$0.05)**

## Monthly Recurring Cost (If Running Monthly)

**One-time execution:**
- Total: $83.18

**Monthly (with optimizations):**
- EC2 Reserved: $1.13
- Lambda Optimized: $39.57
- **Total: ~$40.70/month**

## Cost Monitoring & Alerts

**Recommended AWS Billing Alerts:**
- Alert 1: $50/month (warning threshold)
- Alert 2: $100/month (critical threshold)
- Alert 3: $150/month (emergency stop)

**Cost Tracking:**
- Use AWS Cost Explorer
- Tag resources: `Purpose=load-testing`
- Review after each test run

## Assumptions & Notes

1. **Region:** us-east-1 (N. Virginia) - cheapest region
2. **Instance Types:** On-demand pricing
3. **Lambda:** Assumes 1 GB memory, 2 second execution
4. **API Requests:** Assumes 2 requests per user per minute
5. **Free Tier:** Assumes within AWS free tier limits
6. **Data Transfer:** Not included (typically minimal)
7. **Storage:** EBS volumes not included (~$0.10/GB/month)

## Actual Cost May Vary Based On:

- Your chatbot's actual architecture
- Lambda execution time (if using Lambda)
- Response sizes
- Actual request patterns
- Region selection
- Whether free tier applies
- Data transfer volumes

## Recommendations

1. **Start with EC2 only** to validate infrastructure: **$4.04**
2. **Monitor actual API costs** during first test run
3. **Optimize Lambda** if using Lambda (biggest cost driver)
4. **Use Reserved Instances** if testing monthly
5. **Set up billing alerts** before starting tests

## Contact & Support

For questions about costs or to adjust test parameters, refer to:
- AWS Pricing Calculator: https://calculator.aws/
- AWS Cost Explorer: AWS Console → Cost Management
- This document: `costs/TEST_PLAN_COSTS.md`
