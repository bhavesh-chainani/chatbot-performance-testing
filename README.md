# Chatbot Performance Testing

End-to-end performance testing for chatbot APIs using [Locust](https://locust.io/) on AWS EC2.

Simulates real users logging in, sending questions, and receiving answers — then measures response time across 4 test types.

## Test Types

| Test | Users | Duration | Purpose |
|------|------:|----------|---------|
| **Load** | 500 | 20 min | Baseline under expected traffic |
| **Stress** | 750 | 20 min | Beyond normal capacity |
| **Endurance** | 500 | 8 hours | Sustained load, memory leaks |
| **Breakpoint** | ramp → 1000 | 30 min | Find the breaking point |

## Quick Start

### 1. Configure `.env`

```env
CHATBOT_URL=https://your-chatbot-url.com
LOGIN_EMAIL=your-email@example.com
LOGIN_PASSWORD=your-password
API_ENDPOINT_LOGIN=/api/auth/login
API_ENDPOINT_SEND=/api/chat
```

### 2. Run Locally (single machine)

```bash
pip install -r requirements.txt

# Pick a test type:
TEST_TYPE=load locust -f src/locustfile.py
```

Open `http://localhost:8089` and enter the user count / spawn rate for your test.

### 3. Run on AWS (for full scale)

```bash
./aws_setup/deploy_locust.sh
```

See **[SIMPLE_SETUP.md](SIMPLE_SETUP.md)** for the complete step-by-step AWS guide.

### 4. Generate Report

After a test finishes:

```bash
python src/generate_report.py
```

Opens `reports/report_<test_type>.html` — shows every question asked, the chatbot's answer, and e2e response time with summary statistics.

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
│   │   └── locust-cluster.yaml  # CloudFormation template (c5 instances)
│   ├── deploy_locust.sh         # One-command cluster deploy
│   └── get_ips_simple.sh        # Retrieve master/worker IPs
├── .env                         # Your credentials (not committed)
├── requirements.txt
├── SIMPLE_SETUP.md              # Full AWS setup walkthrough
└── README.md
```

## Key Metric

**End-to-End Response Time** — measured from the moment the chat message is sent to the moment the full response is received. Tracked per request in CSV, aggregated in the HTML report as min / avg / median / p95 / p99 / max.

## Reports

Each test run produces:

- `reports/response_times_<test_type>.csv` — raw data (timestamp, question, answer, response time, status)
- `reports/report_<test_type>.html` — visual report with summary cards, category breakdown, and full request table
