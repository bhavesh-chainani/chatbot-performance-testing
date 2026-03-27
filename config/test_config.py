"""
Test Configuration
Loads from test_config.yaml with environment variable overrides

Set TEST_TYPE env var to select a profile: load, stress, endurance, breakpoint
"""
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

_config_path = Path(__file__).parent / "test_config.yaml"
_config = {}

if _config_path.exists():
    with open(_config_path, 'r') as f:
        _config = yaml.safe_load(f) or {}

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

# ---- Chatbot API ----
CHATBOT_URL = _get_config('chatbot.url', 'https://cfoti.org', 'CHATBOT_URL')
API_ENDPOINT_CHAT = _get_config('chatbot.api_endpoints.chat', '/api/chat/stream')
API_ENDPOINT_TICKETS = _get_config('chatbot.api_endpoints.tickets', '/api/tickets')
API_ENDPOINT_USERME = _get_config('chatbot.api_endpoints.userme', '/api/user/me')

# ---- SSO Authentication ----
LOGIN_EMAIL = os.getenv('LOGIN_EMAIL', '')
LOGIN_PASSWORD = os.getenv('LOGIN_PASSWORD', '')
SSO_LOGIN_URL = _get_config('chatbot.sso.login_url', '', 'SSO_LOGIN_URL')
SESSION_COOKIE = os.getenv('SESSION_COOKIE', '')

# ---- Active Test Type ----
TEST_TYPE = os.getenv('TEST_TYPE', 'load').lower()

# ---- Test Profiles (full-scale AWS defaults; override via env or YAML) ----
LOAD_TEST_USERS = _get_config('load_test.users', 500)
LOAD_TEST_SPAWN_RATE = _get_config('load_test.spawn_rate', 25)
LOAD_TEST_RUN_TIME = _get_config('load_test.run_time', '20m')

STRESS_TEST_USERS = _get_config('stress_test.users', 750)
STRESS_TEST_SPAWN_RATE = _get_config('stress_test.spawn_rate', 38)
STRESS_TEST_RUN_TIME = _get_config('stress_test.run_time', '20m')

ENDURANCE_TEST_USERS = _get_config('endurance_test.users', 500)
ENDURANCE_TEST_SPAWN_RATE = _get_config('endurance_test.spawn_rate', 25)
ENDURANCE_TEST_RUN_TIME = _get_config('endurance_test.run_time', '2h')

BREAKPOINT_MAX_USERS = _get_config('breakpoint_test.max_users', 1000)
BREAKPOINT_RAMP_USERS_PER_STEP = _get_config('breakpoint_test.ramp_users_per_step', 50)
BREAKPOINT_STEP_DURATION = _get_config('breakpoint_test.step_duration_seconds', 120)
BREAKPOINT_RUN_TIME = _get_config('breakpoint_test.run_time', '30m')

_PROFILES = {
    'load': {
        'users': LOAD_TEST_USERS,
        'spawn_rate': LOAD_TEST_SPAWN_RATE,
        'run_time': LOAD_TEST_RUN_TIME,
    },
    'stress': {
        'users': STRESS_TEST_USERS,
        'spawn_rate': STRESS_TEST_SPAWN_RATE,
        'run_time': STRESS_TEST_RUN_TIME,
    },
    'endurance': {
        'users': ENDURANCE_TEST_USERS,
        'spawn_rate': ENDURANCE_TEST_SPAWN_RATE,
        'run_time': ENDURANCE_TEST_RUN_TIME,
    },
    'breakpoint': {
        'users': BREAKPOINT_MAX_USERS,
        'spawn_rate': BREAKPOINT_RAMP_USERS_PER_STEP,
        'run_time': BREAKPOINT_RUN_TIME,
    },
}

_active = _PROFILES.get(TEST_TYPE, _PROFILES['load'])
ACTIVE_USERS = _active['users']
ACTIVE_SPAWN_RATE = _active['spawn_rate']
ACTIVE_RUN_TIME = _active['run_time']

# ---- User Behavior ----
WAIT_TIME_MIN = _get_config('user_behavior.wait_time.min', 2.0, 'WAIT_TIME_MIN')
WAIT_TIME_MAX = _get_config('user_behavior.wait_time.max', 5.0, 'WAIT_TIME_MAX')

# ---- Reporting ----
REPORTS_DIR = _get_config('reporting.reports_dir', 'reports', 'REPORTS_DIR')

# ---- Request Timeouts ----
CHAT_TIMEOUT_SECONDS = _get_config('chatbot.request_timeout_seconds', 240, 'CHAT_TIMEOUT_SECONDS')
