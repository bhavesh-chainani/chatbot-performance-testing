# Simple Local Testing (Chatbot)

Run chatbot performance tests **locally** with [Locust](https://locust.io/) — no AWS, single process, low user counts. Good for quick sanity checks and development.

**Metric:** End-to-end response time (send message → receive full answer).

---

## 1. Prerequisites

- Python 3
- `.env` in project root with chatbot URL and session auth (see below)

---

## 2. Configure `.env`

Create `.env` in the project root:

```env
CHATBOT_URL=https://your-chatbot-url.com

# Session cookie (from browser after logging in):
# DevTools → Application → Cookies → your domain → copy "session" value
SESSION_COOKIE=<paste-session-cookie-here>
```

Optional if your setup needs them:

```env
LOGIN_EMAIL=your-email@example.com
LOGIN_PASSWORD=your-password
```

Session cookie usually lasts ~24 hours; refresh it if you get 401s.

---

## 3. Install

```bash
pip install -r requirements.txt
```

---

## 4. Run a test

From the project root:

```bash
TEST_TYPE=load locust -f src/locustfile.py
```

Then open **http://localhost:8089** in your browser.

**For simple local runs use small numbers:**

- **Number of users:** e.g. `5` or `10`
- **Spawn rate:** e.g. `1` or `2`
- **Run time:** e.g. `1m` or `5m` (or leave empty to run until you stop)

Click **Start swarming**. Locust will log in (or use the session cookie), open a ticket, send sample questions, and record response times.

**Test types:** Same command, change `TEST_TYPE`:

| TEST_TYPE   | Use case              |
|------------|------------------------|
| `load`     | Baseline (default)     |
| `stress`   | Higher load            |
| `endurance`| Longer run             |
| `breakpoint` | Ramp up to find limit |

For local testing, stick to **load** with few users and short run time unless you want a longer/stress run.

---

## 5. Generate report

After a run (or after you stop it), generate the HTML report:

```bash
python src/generate_report.py
```

This reads the latest run from `reports/` and creates `reports/report_<test_type>.html` with:

- Summary stats (min / avg / median / p95 / p99 / max response time)
- Per-request table (question, answer, response time, status)

Raw data is in `reports/response_times_<test_type>.csv`.

---

## Project layout (relevant for local testing)

```
.
├── src/
│   ├── locustfile.py       # Locust scenario: auth, send messages, log times
│   ├── sample_questions.py # Question pools (simple/complex)
│   └── generate_report.py  # Builds HTML report from CSV
├── config/
│   ├── test_config.yaml    # Test profiles (users, duration — override in UI or env)
│   └── test_config.py      # Loads config + TEST_TYPE
├── .env                    # Not committed; your URL + SESSION_COOKIE
├── requirements.txt
└── simple_testing.md       # This file
```

---

## Overriding users and duration (optional)

Config defaults in `config/test_config.yaml` are for large-scale runs. For local runs you can:

- **Use the Locust UI** — set “Number of users” and “Spawn rate” and run time when you start (recommended for simple testing), or
- **Set env vars** before starting Locust, e.g.:
  - `LOAD_TEST_USERS=10` and `LOAD_TEST_RUN_TIME=5m` (for load test)
  - Same pattern for `STRESS_TEST_*`, `ENDURANCE_TEST_*`, `BREAKPOINT_*` as in `config/test_config.py`

Then run:

```bash
TEST_TYPE=load locust -f src/locustfile.py
```
