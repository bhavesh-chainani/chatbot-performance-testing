# Chatbot Performance Testing

End-to-end performance testing for the **cfoti.org** chatbot using [Locust](https://locust.io/).

Simulates real users sending questions and receiving answers, then measures **end-to-end response time** across 4 test types.

## Test Types

These are the logical test types; the exact users/durations depend on your config/branch.

| Test        | Purpose                               |
|------------|----------------------------------------|
| **Load**   | Baseline under expected traffic       |
| **Stress** | Beyond normal capacity                |
| **Endurance** | Sustained load, detect degradation |
| **Breakpoint** | Ramp up until failure             |

See `config/test_config.yaml` for the current users/durations.

## 1. Configure `.env` (session cookie)

Authentication is via a **session cookie** from the browser (SSO happens outside this project).

Example `.env`:

```env
CHATBOT_URL=https://cfoti.org

# Paste from browser: DevTools > Application > Cookies > cfoti.org > \"session\"
SESSION_COOKIE=<paste-session-cookie-here>
```

How to get the cookie:

1. Log in to **https://cfoti.org** in Chrome (or another browser).  
2. Open DevTools → **Application** → **Cookies** → `https://cfoti.org`.  
3. Find the cookie named **`session`**, copy its **Value**, and paste into `SESSION_COOKIE` in `.env`.  

If you start seeing 401s or auth failures, grab a fresh cookie and update `.env`.

## 2. Install & Run Locally

From the project root:

```bash
pip install -r requirements.txt

# Pick a test type (load, stress, endurance, breakpoint)
TEST_TYPE=load locust -f src/locustfile.py
```

Open `http://localhost:8089`, set users/spawn rate/run time if needed, and click **Start swarming**.

To run headless:

```bash
TEST_TYPE=load locust -f src/locustfile.py --headless -u 10 -r 2 --run-time 5m
```

## 3. Run on AWS (full-scale)

To run full-scale (master + workers on EC2), use:

```bash
./aws_setup/deploy_locust.sh
```

Then follow **`AWS_SETUP.md`** for:

- Getting master/worker IPs.  
- Copying files to master and workers.  
- Starting master (`--master`) and workers (`--worker --master-host=<master-private-ip>`).  
- Downloading reports and cleaning up the stack.  

## 4. Generate HTML Report

After copying reports back to your machine:

```bash
python src/generate_report.py
```

Use `--exclude-empty` to drop rows where no answer was recorded:

```bash
python src/generate_report.py --exclude-empty
```

This generates `reports/report_<test_type>.html` with:

- Summary stats (avg, median, p95, p99, max).  
- Per-category breakdown (Simple vs Complex).  
- Full table of each question, answer, and end-to-end response time.  

## Project Structure

```text
.
├── src/
│   ├── locustfile.py          # Locust test – auth via session cookie, send messages, record responses
│   ├── sample_questions.py    # Simple & Complex question pools + weights
│   └── generate_report.py     # HTML report generator
├── config/
│   ├── test_config.yaml       # Test profiles (users, spawn rate, run_time)
│   └── test_config.py         # Loads config, selects active profile via TEST_TYPE
├── aws_setup/
│   ├── cloudformation/
│   │   └── locust-cluster-full.yaml  # Full-scale: master + workers
│   ├── deploy_locust.sh              # Deploy full-scale cluster
│   └── get_ips_simple.sh             # Get master + worker IPs (SSH / commands)
├── docs/
│   ├── AWS_COSTS.md                  # EC2 cost + token estimates
│   ├── TOKEN_SCOPE_ORIGINAL.md       # Original token scope (8h endurance)
│   └── TOKEN_SCOPE_70M_BUDGET.md     # 70M token budget scope (2h endurance)
├── reports/                          # CSV + HTML reports (created at runtime)
├── .env                              # Local config (session cookie, URL)
├── requirements.txt
└── README.md
```

## Key Metric

**End-to-End Response Time** — measured from when the chat message is sent to when the full response is received. Tracked per request in CSV and summarized in the HTML report as min / avg / median / p95 / p99 / max.

## Outputs

Each test run produces (per test type):

- `reports/response_times_<test_type>.csv` — raw rows (timestamp, category, question, answer, response_time_ms, status).  
- `reports/run_meta_<test_type>.json` — users / spawn rate / run_time used for that run.  
- `reports/report_<test_type>.html` — visual report for sharing with stakeholders.  
