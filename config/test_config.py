"""
Test Configuration
Loads from test_config.yaml with environment variable overrides
"""
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load YAML configuration
_config_path = Path(__file__).parent / "test_config.yaml"
_config = {}

if _config_path.exists():
    with open(_config_path, 'r') as f:
        _config = yaml.safe_load(f) or {}
else:
    print(f"Warning: {_config_path} not found. Using defaults.")

def _get_config(key_path, default=None, env_key=None):
    """Get config value from YAML, with environment variable override"""
    if env_key:
        env_value = os.getenv(env_key)
        if env_value is not None:
            if isinstance(default, bool):
                return env_value.lower() in ('true', '1', 'yes', 'on')
            elif isinstance(default, int):
                try:
                    return int(env_value)
                except ValueError:
                    return default
            elif isinstance(default, float):
                try:
                    return float(env_value)
                except ValueError:
                    return default
            return env_value
    
    keys = key_path.split('.')
    value = _config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value if value is not None else default

# Chatbot API Configuration
CHATBOT_URL = _get_config('chatbot.url', 'https://your-chatbot-url.com', 'CHATBOT_URL')
API_ENDPOINT_LOGIN = _get_config('chatbot.api_endpoints.login', '/api/auth/login', 'API_ENDPOINT_LOGIN')
API_ENDPOINT_SEND = _get_config('chatbot.api_endpoints.send', '/api/chat', 'API_ENDPOINT_SEND')

# Authentication (from .env)
LOGIN_EMAIL = _get_config('authentication.email', '', 'LOGIN_EMAIL')
LOGIN_PASSWORD = _get_config('authentication.password', '', 'LOGIN_PASSWORD')

# Load Test
LOAD_TEST_USERS = _get_config('load_test.users', 5, 'LOAD_TEST_USERS')
LOAD_TEST_SPAWN_RATE = _get_config('load_test.spawn_rate', 1.0, 'LOAD_TEST_SPAWN_RATE')
LOAD_TEST_RUN_TIME = _get_config('load_test.run_time', '2m', 'LOAD_TEST_RUN_TIME')

# Endurance Test
ENDURANCE_TEST_USERS = _get_config('endurance_test.users', 3, 'ENDURANCE_TEST_USERS')
ENDURANCE_TEST_SPAWN_RATE = _get_config('endurance_test.spawn_rate', 0.5, 'ENDURANCE_TEST_SPAWN_RATE')
ENDURANCE_TEST_RUN_TIME = _get_config('endurance_test.run_time', '10m', 'ENDURANCE_TEST_RUN_TIME')

# Stress Test
STRESS_TEST_USERS = _get_config('stress_test.users', 10, 'STRESS_TEST_USERS')
STRESS_TEST_SPAWN_RATE = _get_config('stress_test.spawn_rate', 2.0, 'STRESS_TEST_SPAWN_RATE')
STRESS_TEST_RUN_TIME = _get_config('stress_test.run_time', '5m', 'STRESS_TEST_RUN_TIME')

# Breakpoint Test
BREAKPOINT_TEST_START_USERS = _get_config('breakpoint_test.start_users', 1, 'BREAKPOINT_TEST_START_USERS')
BREAKPOINT_TEST_MAX_USERS = _get_config('breakpoint_test.max_users', 150, 'BREAKPOINT_TEST_MAX_USERS')
BREAKPOINT_TEST_SPAWN_RATE = _get_config('breakpoint_test.spawn_rate', 1.0, 'BREAKPOINT_TEST_SPAWN_RATE')
BREAKPOINT_TEST_STEP_DURATION = _get_config('breakpoint_test.step_duration', '1m', 'BREAKPOINT_TEST_STEP_DURATION')
BREAKPOINT_TEST_USER_INCREMENT = _get_config('breakpoint_test.user_increment', 20, 'BREAKPOINT_TEST_USER_INCREMENT')

# Legacy defaults
DEFAULT_USERS = LOAD_TEST_USERS
DEFAULT_SPAWN_RATE = LOAD_TEST_SPAWN_RATE
DEFAULT_RUN_TIME = LOAD_TEST_RUN_TIME

# User Behavior
WAIT_TIME_MIN = _get_config('user_behavior.wait_time.min', 2.0, 'WAIT_TIME_MIN')
WAIT_TIME_MAX = _get_config('user_behavior.wait_time.max', 5.0, 'WAIT_TIME_MAX')
TASK_WEIGHT_CHAT_PAGE = _get_config('user_behavior.task_weights.chat_page', 3, 'TASK_WEIGHT_CHAT_PAGE')
TASK_WEIGHT_SEND_MESSAGE = _get_config('user_behavior.task_weights.send_message', 5, 'TASK_WEIGHT_SEND_MESSAGE')

# Reporting
REPORTS_DIR = _get_config('reporting.reports_dir', 'reports', 'REPORTS_DIR')
HTML_REPORT_PATH = _get_config('reporting.html_report_path', f'{REPORTS_DIR}/load_test_report.html', 'HTML_REPORT_PATH')
TTF_DATA_PATH = _get_config('reporting.ttf_data_path', f'{REPORTS_DIR}/ttf_data.csv', 'TTF_DATA_PATH')

# Login fallbacks
LOGIN_ENDPOINT_FALLBACKS = [
    "/api/auth/login",
    "/api/login",
    "/login",
    "/"
]

CUSTOM_HEADERS = {}
