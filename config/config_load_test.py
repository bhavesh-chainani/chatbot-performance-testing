"""
Load Test Configuration
Tests normal expected load conditions

This file uses the centralized test_config.py for configuration.
You can override defaults here or via environment variables.
"""
from config.test_config import (
    CHATBOT_URL,
    LOAD_TEST_USERS,
    LOAD_TEST_SPAWN_RATE,
    LOAD_TEST_RUN_TIME,
    HTML_REPORT_PATH,
)

# Load test parameters - suitable for Locust Cloud free tier
# These can be overridden via environment variables in test_config.py
LOAD_TEST_CONFIG = {
    "users": LOAD_TEST_USERS,  # Number of concurrent users
    "spawn_rate": LOAD_TEST_SPAWN_RATE,  # Users spawned per second
    "run_time": LOAD_TEST_RUN_TIME,  # Test duration
    "host": CHATBOT_URL,
    "web_ui": True,  # Enable web UI
    "html_report": HTML_REPORT_PATH
}
