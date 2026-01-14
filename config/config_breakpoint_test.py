"""
Breakpoint Test Configuration
Gradually increase load until system fails - finds exact breaking point

This test gradually increases load to identify:
- Exact breaking point (maximum capacity)
- How gracefully the system handles overload
- Error rates at different load levels
- Recovery behavior

This file uses the centralized test_config.py for configuration.
You can override defaults here or via environment variables.
"""
from config.test_config import (
    CHATBOT_URL,
    BREAKPOINT_TEST_START_USERS,
    BREAKPOINT_TEST_MAX_USERS,
    BREAKPOINT_TEST_SPAWN_RATE,
    BREAKPOINT_TEST_STEP_DURATION,
    BREAKPOINT_TEST_USER_INCREMENT,
    HTML_REPORT_PATH,
)

# Breakpoint test parameters - gradual load increase
# Suitable for Locust Cloud free tier
# These can be overridden via environment variables in test_config.py
BREAKPOINT_TEST_CONFIG = {
    "start_users": BREAKPOINT_TEST_START_USERS,  # Starting number of users
    "max_users": BREAKPOINT_TEST_MAX_USERS,  # Maximum users to test
    "spawn_rate": BREAKPOINT_TEST_SPAWN_RATE,  # Users spawned per second
    "step_duration": BREAKPOINT_TEST_STEP_DURATION,  # Duration at each load level
    "user_increment": BREAKPOINT_TEST_USER_INCREMENT,  # Users added per step
    "host": CHATBOT_URL,
    "web_ui": True,  # Enable web UI
    "html_report": "reports/breakpoint_test_report.html"
}
