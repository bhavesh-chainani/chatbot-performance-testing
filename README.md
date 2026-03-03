# Chatbot Performance Testing

Local performance testing for chatbot APIs using [Locust](https://locust.io/). Simulates users sending questions and measures end-to-end response time.

**→ See [simple_testing.md](simple_testing.md) for setup and how to run tests locally.**

## Quick summary

1. **Configure** `.env` (chatbot URL + `SESSION_COOKIE` from browser).
2. **Install** `pip install -r requirements.txt`.
3. **Run** `TEST_TYPE=load locust -f src/locustfile.py` → open http://localhost:8089, set few users (e.g. 5–10), start.
4. **Report** `python src/generate_report.py` → `reports/report_<test_type>.html`.
