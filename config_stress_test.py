"""
Stress Test Configuration
High load beyond normal capacity to find breaking point

This test pushes the system beyond normal capacity to identify:
- Maximum capacity limits
- Performance bottlenecks under stress
- Error handling under high load
- System recovery capabilities

This file uses the centralized test_config.py for configuration.
You can override defaults here or via environment variables.
"""
from test_config import (
    CHATBOT_URL,
    STRESS_TEST_USERS,
    STRESS_TEST_SPAWN_RATE,
    STRESS_TEST_RUN_TIME,
    HTML_REPORT_PATH,
)

# Stress test parameters - high load, shorter duration
# Suitable for Locust Cloud free tier
# These can be overridden via environment variables in test_config.py
STRESS_TEST_CONFIG = {
    "users": STRESS_TEST_USERS,  # High number of concurrent users
    "spawn_rate": STRESS_TEST_SPAWN_RATE,  # Faster spawn rate
    "run_time": STRESS_TEST_RUN_TIME,  # Shorter duration (5 minutes default)
    "host": CHATBOT_URL,
    "web_ui": True,  # Enable web UI
    "html_report": "reports/stress_test_report.html"
}

