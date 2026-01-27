"""
Endurance Test Configuration
Long duration test with moderate load to check for memory leaks and degradation over time

This test runs for an extended period with moderate load to identify:
- Memory leaks
- Performance degradation over time
- Resource exhaustion issues
- Stability problems

This file uses the centralized test_config.py for configuration.
Configuration is loaded from test_config.yaml (with env var overrides).
"""
from config.test_config import (
    CHATBOT_URL,
    ENDURANCE_TEST_USERS,
    ENDURANCE_TEST_SPAWN_RATE,
    ENDURANCE_TEST_RUN_TIME,
    HTML_REPORT_PATH,
)

# Endurance test parameters - moderate load, long duration
# Suitable for Locust Cloud free tier
# These can be overridden via environment variables or test_config.yaml
ENDURANCE_TEST_CONFIG = {
    "users": ENDURANCE_TEST_USERS,  # Moderate number of concurrent users
    "spawn_rate": ENDURANCE_TEST_SPAWN_RATE,  # Slow spawn rate
    "run_time": ENDURANCE_TEST_RUN_TIME,  # Long duration (10 minutes default)
    "host": CHATBOT_URL,
    "web_ui": True,  # Enable web UI
    "html_report": "reports/endurance_test_report.html"
}
