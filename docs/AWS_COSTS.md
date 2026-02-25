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
| Endurance  | 2 hours  | 500 users (2h keeps tokens under 70M) |
| Breakpoint | 30 min   | Ramp to 1000 users       |
| **Total**  | **~3h 10m** | Sequential run time   |

Add **~30–60 minutes** for: deploy, copy files, start master/workers, and optional buffer between tests.

### Scenario A: One deployment, all 4 tests in one go (recommended)

- Cluster uptime: **~4–5 hours** (~3h 10m tests + ~1h setup/buffer).
- **Compute:** 4–5 × $0.94 ≈ **$3.80–$4.70**.
- **EBS + data transfer:** roughly **$1**.
- **Total (ballpark): ~$5–$6** for the full run.

### Scenario B: One test per day (deploy → run → teardown each time)

- 4 deployments, 4 teardowns.
- Approximate uptime: ~1h (load) + ~0.5h (stress) + ~2.5h (endurance) + ~1h (breakpoint) + buffers ⇒ about **6–7 hours** cluster time total.
- **Compute:** ~6–7 × $0.94 ≈ **$6–$7**.
- **Total (ballpark): ~$7–$8** (more than Scenario A due to extra deploy/teardown time).

---

## Summary Table

| Scenario                          | Cluster time (approx) | Estimated total cost |
|-----------------------------------|------------------------|----------------------|
| All 4 tests in one session (A)    | ~4–5 hours             | **~$5–$6**           |
| One test per day, 4 sessions (B)  | ~6–7 hours             | **~$7–$8**           |

---

## Token consumption (estimated)

The Locust reports don’t include token counts; the chatbot API (cfoti.org) would need to expose those. The estimates below use your **baseline run** to scale **request counts**, then apply a **typical tokens-per-request** range.

**Reference docs (copies):**
- **[TOKEN_SCOPE_ORIGINAL.md](TOKEN_SCOPE_ORIGINAL.md)** – Original scope (8h Endurance): ~252k requests, ~176M tokens.
- **[TOKEN_SCOPE_70M_BUDGET.md](TOKEN_SCOPE_70M_BUDGET.md)** – Scope to stay under 70M (2h Endurance): ~90k requests, ~63M tokens.

### Baseline (from `reports/old/report_load.html`)

- **10 concurrent users**, 1 ramp up/s, **3 min** runtime  
- **27 successful requests** (chat messages sent, full response received)  
- **Requests per user-minute:** 27 ÷ (10 × 3) ≈ **0.9** req/(user·min)

So for any test: **total requests ≈ 0.9 × (concurrent users × duration in minutes)**.  
(Concurrency for breakpoint is approximated as average users over the ramp.)

### Estimated requests per full-scale test

| Test        | Users (approx) | Duration | User-minutes   | Est. total requests |
|------------|----------------|----------|----------------|----------------------|
| Load       | 500            | 20 min   | 10,000         | **~9,000**          |
| Stress     | 750            | 20 min   | 15,000         | **~13,500**         |
| Endurance  | 500            | 2 h      | 60,000         | **~54,000**         |
| Breakpoint | ~500 (avg ramp)| 30 min   | ~15,000        | **~13,500**         |

### Tokens per request (assumption)

The chatbot likely uses an LLM behind the API. Without real token metadata we assume:

- **Input:** user question + system/context (e.g. 200–600 tokens) → use **~400** as a mid estimate.  
- **Output:** answers in your report are ~100–400+ words → **~200–400** tokens typical.  
- **Total per request:** **~500–1,000** tokens (low/avg/high).

Use your actual model and average prompt/response length to tune these.

### Estimated token consumption per test

| Test        | Est. requests | Tokens/request (range) | Est. total tokens (low) | Est. total tokens (mid) | Est. total tokens (high) |
|------------|----------------|-------------------------|--------------------------|--------------------------|---------------------------|
| Load       | ~9,000         | 500 – 1,000             | **~4.5M**                | **~6.3M**                | **~9M**                   |
| Stress     | ~13,500        | 500 – 1,000             | **~6.8M**                | **~9.5M**                | **~13.5M**                |
| Endurance  | ~54,000        | 500 – 1,000             | **~27M**                 | **~38M**                 | **~54M**                  |
| Breakpoint | ~13,500        | 500 – 1,000             | **~6.8M**                | **~9.5M**                | **~13.5M**                |

**All 4 tests (mid estimate, 2h Endurance):** ~9,000 + 13,500 + 54,000 + 13,500 ≈ **90,000 requests** → **~63M tokens** (mid), under a **70M token** budget.

---

### Token budget: 70M (client allocation)

If the client has allocated **70M tokens** for performance testing, the full-scale plan above exceeds it (Endurance alone is ~151M at 8h). Recommendation:

**Keep Load, Stress, and Breakpoint as-is.** Use the remaining budget for **Endurance** only.

| Test        | Est. tokens (mid) | Action / duration      |
|------------|--------------------|-------------------------|
| Load       | ~6.3M              | No change (20 min)      |
| Stress     | ~9.5M              | No change (20 min)      |
| Breakpoint | ~9.5M              | No change (30 min)      |
| **Subtotal** | **~25.3M**        |                         |
| Endurance  | **~38M**           | **Shorten to 2 hours**  |
| **Total**  | **~63M**           | **Under 70M (≈7M buffer)** |

**Endurance at 2h:** 500 users × 120 min × 0.9 req/(user·min) × ~700 tokens ≈ **37.8M tokens**.  
Total for all 4 tests ≈ **63M tokens**, leaving ~7M buffer for variance.

- **Config change:** Set `endurance_test.run_time` to **`"2h"`** (see `config/test_config.yaml`). This is applied in the repo so runs stay within the 70M cap.
- **If you need longer endurance:** You’d have to reduce users (e.g. 500 → 250 for 4h) or get a higher token allocation. At 70M, **2h at 500 users** is the recommended compromise so you still validate sustained load without blowing the budget.

---

### How to get real token counts

If the chatbot API returns token usage (e.g. in response headers or a usage field), you can:

1. Log **input_tokens** and **output_tokens** (or **total_tokens**) in the Locust user (e.g. from the SSE stream or final JSON).
2. Write them to the CSV or a separate token log.
3. Aggregate per run and report in `generate_report.py`.

Then you can replace these estimates with actuals and track cost per test if your LLM provider charges by token.

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
