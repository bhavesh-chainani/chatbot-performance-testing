# Chatbot Performance Testing

End-to-end performance testing for chatbot APIs using [Locust](https://locust.io/) on AWS EC2.

Simulates real users logging in, sending questions, and receiving answers — then measures response time across 4 test types.

## Test Types

Config defaults are set for full-scale AWS (500–1000 users).

| Test | Users (full-scale) | Duration | Purpose |
|------|-------------------|----------|---------|
| **Load** | 500 | 20 min | Baseline under expected traffic |
| **Stress** | 750 | 20 min | Beyond normal capacity |
| **Endurance** | 500 | 2 hours | Sustained load (2h keeps within 70M token budget) |
| **Breakpoint** | ramp to 1000 | 30 min | Find the breaking point |

## Quick Start

### 1. Configure `.env`

```env
CHATBOT_URL=https://your-chatbot-url.com
LOGIN_EMAIL=your-email@example.com
LOGIN_PASSWORD=your-password
```

### 2. Install & Run Locally

```bash
pip install -r requirements.txt

# Pick a test type:
TEST_TYPE=load locust -f src/locustfile.py
```

Open `http://localhost:8089`, enter 10 users / spawn rate 2, and click Start.

### 3. Run on AWS

```bash
./aws_setup/deploy_locust.sh
```

Deploys 1 master + 5 workers (full-scale). See **[AWS_SETUP.md](AWS_SETUP.md)** for step-by-step instructions.

### 4. Generate Report

After a test finishes:

```bash
python src/generate_report.py
```

Generates `reports/report_<test_type>.html` — shows every question asked, the chatbot's answer, and e2e response time with summary statistics.

## Project Structure

```
.
├── src/
│   ├── locustfile.py          # Locust test — login, send messages, record responses
│   ├── sample_questions.py    # Simple & Complex question pools + weights
│   └── generate_report.py     # HTML report generator
├── config/
│   ├── test_config.yaml       # All 4 test profiles
│   └── test_config.py         # Loads config, selects active profile via TEST_TYPE
├── aws_setup/
│   ├── cloudformation/
│   │   └── locust-cluster-full.yaml  # Master + workers
│   ├── deploy_locust.sh         # Deploy full-scale cluster
│   └── get_ips_simple.sh        # Get master + worker IPs
├── .env                         # Your credentials (not committed)
├── requirements.txt
├── AWS_SETUP.md                 # AWS setup walkthrough
└── README.md
```

## Key Metric

**End-to-End Response Time** — measured from the moment the chat message is sent to the moment the full response is received. Tracked per request in CSV, aggregated in the HTML report as min / avg / median / p95 / p99 / max.

## Reports

Each test run produces:

- `reports/response_times_<test_type>.csv` — raw data (timestamp, question, answer, response time, status)
- `reports/report_<test_type>.html` — visual report with summary cards, category breakdown, and full request table
