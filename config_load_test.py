"""
Load Test Configuration
Tests normal expected load conditions

This file uses the centralized test_config.py for configuration.
You can override defaults here or via environment variables.
"""
from test_config import (
    CHATBOT_URL,
    DEFAULT_USERS,
    DEFAULT_SPAWN_RATE,
    DEFAULT_RUN_TIME,
    HTML_REPORT_PATH,
)

# Load test parameters - suitable for Locust Cloud free tier
# These can be overridden via environment variables in test_config.py
LOAD_TEST_CONFIG = {
    "users": DEFAULT_USERS,  # Number of concurrent users
    "spawn_rate": DEFAULT_SPAWN_RATE,  # Users spawned per second
    "run_time": DEFAULT_RUN_TIME,  # Test duration
    "host": CHATBOT_URL,
    "web_ui": True,  # Enable web UI
    "html_report": HTML_REPORT_PATH
}

