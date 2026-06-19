# Chatbot load testing (Locust)

Load-test the chatbot **locally** with [Locust](https://locust.io/). Authentication uses a **session cookie** you copy from your browser after logging in.

---

## 1. One-time setup

1. **Python 3.10+** installed.

2. **Install dependencies** (from this project folder):

   ```bash
   pip install -r requirements.txt
   ```

3. **Environment file**

   - Copy `.env.example` to `.env`.
   - Log into the chatbot site in your browser (same host as in `config/test_config.yaml`, default `https://cfoti.org`).
   - Open DevTools → **Application** (Chrome) or **Storage** (Firefox) → **Cookies** → select the site → copy the **`session`** cookie value.
   - Put it in `.env` as:

     ```env
     SESSION_COOKIE=paste-the-value-here
     ```

   Optional: set `CHATBOT_URL` in `.env` if the base URL differs from the YAML default.

---

## 2. Run a test (web UI — recommended)

Pick a test profile with `TEST_TYPE` (`load`, `stress`, `endurance`, or `breakpoint`). Defaults for users, spawn rate, and duration are in `config/test_config.yaml` (you can still override in the Locust UI).

**PowerShell**

```powershell
$env:TEST_TYPE = "load"
python -m locust -f src/locustfile.py
```

**macOS / Linux / Git Bash**

```bash
TEST_TYPE=load python -m locust -f src/locustfile.py
```

Open **http://localhost:8089**, set **users** and **spawn rate**, start the test.

---

## 3. What to hand off (client-style deliverables)

Locust gives you two standard artifacts:

| Deliverable | What it is | How to get it |
|-------------|------------|----------------|
| **HTML report** | Locust’s report: request stats, response times, failures (charts work best from the UI). | In the UI: **Download** tab → **Download Report**. Or run headless with `--html` (see script below). |
| **`*_stats_history.csv`** | Time series of aggregated HTTP stats (same idea as a “stats history” export): RPS, percentiles, cumulative counts, etc. | Run with a `--csv` prefix (see script below). Example: `reports/client_run_stats_history.csv`. |

**Headless one-liner** (writes HTML + CSVs into `reports/`):

```powershell
.\scripts\client_locust_exports.ps1 -Users 1 -SpawnRate 1 -RunTime "3m" -Prefix "reports/client_run"
```

After it finishes, send the client at least:

- `reports/client_run.html`
- `reports/client_run_stats_history.csv`

Locust also writes `reports/client_run_stats.csv` (final stats table) and `reports/client_run_failures.csv` if there were failures.

**Client guides:**

- [docs/CLIENT_LOCUST_STATS_HISTORY.md](docs/CLIENT_LOCUST_STATS_HISTORY.md) — `*_stats_history.csv` columns (**Total Median / Average / Min / Max**, etc.).
- [docs/CLIENT_CHAT_FAILURES_EXPLAINED.md](docs/CLIENT_CHAT_FAILURES_EXPLAINED.md) — failure types, full Q&A + JSONL transcripts, DevTools mapping, and how to respond when engineering says “it works.”

---

## 4. Other files this project writes

| File | Meaning |
|------|--------|
| `reports/*_response_times_<TEST_TYPE>.csv` | One row per **chat**: **full** question and answer, timings, `failure_reason`. **Not** Locust’s `*_stats_history.csv` (that is HTTP-level aggregates). |
| `reports/*_chat_transcripts_<TEST_TYPE>.jsonl` | Same chats as JSON; **failures include `raw_sse`** (full API stream) for DevTools comparison. Optional `LOG_ALL_RAW_SSE=true` for successes too. |
| `reports/run_meta_<TEST_TYPE>.json` | Written when the test **ends**: users, spawn rate, host, run time (from the swarm you actually ran). |

---

## 5. Project layout

```
├── docs/
│   ├── CLIENT_LOCUST_STATS_HISTORY.md  # Client-facing: Locust *_stats_history.csv columns
│   └── CLIENT_CHAT_FAILURES_EXPLAINED.md  # Client-facing: chat failure types and DevTools mapping
├── .env                 # You create this (see .env.example); not committed
├── config/
│   ├── test_config.yaml # URL, API paths, default users/duration per TEST_TYPE
│   └── test_config.py   # Loads YAML + env
├── src/
│   ├── locustfile.py    # Locust user: auth, ticket, chat stream
│   └── sample_questions.py
├── scripts/
│   ├── client_locust_exports.ps1
│   └── client_locust_exports.sh
└── requirements.txt
```

---

## 6. `*_stats_history.csv` columns

See **[docs/CLIENT_LOCUST_STATS_HISTORY.md](docs/CLIENT_LOCUST_STATS_HISTORY.md)** for a full client-facing glossary (**Total Median / Average / Min / Max** response time, percentiles, counters, and how **`Aggregated`** behaves).
