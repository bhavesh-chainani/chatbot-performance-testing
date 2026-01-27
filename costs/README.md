# Cost Analysis Documentation

This folder contains detailed cost analysis for the chatbot performance testing plan.

## Files

- **TEST_PLAN_COSTS.md** - Complete cost breakdown for your specific test plan
- **COST_BREAKDOWN.md** - Detailed cost calculations and scenarios
- **README.md** - This file

## Quick Cost Summary

**Total Estimated Cost: $83.18** (for complete test plan)

Breakdown:
- EC2 Infrastructure (Locust): $4.04
- API Gateway: $0.00 (within free tier)
- Lambda: $79.14 (if chatbot uses Lambda)

**If only EC2 infrastructure needed: $4.04**

## Test Plan

- Load Test: 2 runs, 500 users, 20 min each
- Stress Test: 2 runs, 750 users, 20 min each  
- Endurance Test: 2 runs, 500 users, 8 hours each
- Breakpoint Test: 2 runs, up to 1000 users, 60 min each

## Cost Scenarios

1. **EC2 Only**: $4.04
2. **EC2 + API Gateway**: $4.04 (within free tier)
3. **EC2 + API Gateway + Lambda**: $83.18
4. **With Optimizations**: $40.70/month (if running monthly)

See detailed breakdowns in the files above.
