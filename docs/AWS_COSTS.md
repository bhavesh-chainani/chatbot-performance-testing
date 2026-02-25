# AWS Cost Rundown – Full-Scale Load Testing

Estimated cost to run all 4 tests using the default cluster (1 master + 5 workers). Prices are **on-demand, us-east-1** and can vary by region and over time.

---

## Cluster (default)

| Resource        | Type      | Count | On-demand $/hr (us-east-1) |
|----------------|-----------|-------|----------------------------|
| Master         | c5.large  | 1     | ~$0.085                    |
| Workers        | c5.xlarge | 5     | 5 × ~$0.17 = ~$0.85       |
| **Total/hour** |           |       | **~$0.94**                 |

- **EBS:** Default root volumes (≈8 GB per instance) add a few dollars per day if the cluster runs many hours; small compared to compute.
- **Data transfer:** Outbound to the internet is typically a few dollars for this workload unless you generate huge traffic.

---

## Running All 4 Tests

| Test        | Duration | Notes                    |
|------------|----------|--------------------------|
| Load       | 20 min   | 500 users                |
| Stress     | 20 min   | 750 users                |
| Endurance  | 8 hours  | 500 users                |
| Breakpoint | 30 min   | Ramp to 1000 users       |
| **Total**  | **9h 10m** | Sequential run time   |

Add **~30–60 minutes** for: deploy, copy files, start master/workers, and optional buffer between tests.

### Scenario A: One deployment, all 4 tests in one go (recommended)

- Cluster uptime: **~10–11 hours** (9h 10m tests + ~1h setup/buffer).
- **Compute:** 10–11 × $0.94 ≈ **$9.50–$10.50**.
- **EBS + data transfer:** roughly **$1–$3**.
- **Total (ballpark): ~$11–$14** for the full run.

### Scenario B: One test per day (deploy → run → teardown each time)

- 4 deployments, 4 teardowns.
- Approximate uptime per day: ~1h (load) + ~0.5h buffer, ~1h (stress) + 0.5h, ~8.5h (endurance) + 0.5h, ~1h (breakpoint) + 0.5h ⇒ about **3 + 2 + 9 + 2 = 16 hours** cluster time.
- **Compute:** 16 × $0.94 ≈ **$15**.
- **Total (ballpark): ~$16–$19** (more than Scenario A due to extra deploy/teardown time).

---

## Summary Table

| Scenario                          | Cluster time (approx) | Estimated total cost |
|-----------------------------------|------------------------|----------------------|
| All 4 tests in one session (A)    | ~10–11 hours           | **~$11–$14**         |
| One test per day, 4 sessions (B)  | ~16 hours              | **~$16–$19**         |

---

## How to Reduce Cost

1. **Run all 4 tests in one deployment** (Scenario A) to avoid paying for multiple deploy/teardown cycles.
2. **Tear down as soon as you’re done:**  
   `aws cloudformation delete-stack --stack-name locust-cluster`
3. **Use a single region** (e.g. us-east-1) to avoid cross-region data transfer.
4. **Optional:** Use **Spot** for workers (not in the current template); can cut worker cost by ~70% with possible interruptions.

---

## Price check (before you run)

Confirm current rates for your region:

- [EC2 On-Demand Pricing](https://aws.amazon.com/ec2/pricing/on-demand/)
- Or: `aws pricing get-products --service-code AmazonEC2` (filter by instance type and region)

EBS and data transfer:

- [EBS Pricing](https://aws.amazon.com/ebs/pricing/)
- [Data Transfer Pricing](https://aws.amazon.com/ec2/pricing/on-demand/#Data_Transfer)
