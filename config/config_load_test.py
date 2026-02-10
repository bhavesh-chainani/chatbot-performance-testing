"""
Load Test Configuration
"""
from config.test_config import (
    CHATBOT_URL,
    LOAD_TEST_USERS,
    LOAD_TEST_SPAWN_RATE,
    LOAD_TEST_RUN_TIME,
    HTML_REPORT_PATH,
)

LOAD_TEST_CONFIG = {
    "users": LOAD_TEST_USERS,
    "spawn_rate": LOAD_TEST_SPAWN_RATE,
    "run_time": LOAD_TEST_RUN_TIME,
    "host": CHATBOT_URL,
    "web_ui": True,
    "html_report": HTML_REPORT_PATH
}
