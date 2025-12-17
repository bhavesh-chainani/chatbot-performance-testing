"""
Test Configuration
Centralized configuration for chatbot performance testing

To configure your tests, modify the values below or set them via environment variables.
Environment variables take precedence over the defaults here.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# API Configuration
# ============================================================================
CHATBOT_URL = os.getenv("CHATBOT_URL", "https://cfoti.org")
API_ENDPOINT_LOGIN = os.getenv("API_ENDPOINT_LOGIN", "/api/auth/login")
API_ENDPOINT_SEND = os.getenv("API_ENDPOINT_SEND", "/api/chat")

# ============================================================================
# Authentication Configuration
# ============================================================================
LOGIN_EMAIL = os.getenv("LOGIN_EMAIL", "")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "")

# ============================================================================
# Load Test Configuration
# ============================================================================
# Default load test parameters
DEFAULT_USERS = int(os.getenv("DEFAULT_USERS", "5"))
DEFAULT_SPAWN_RATE = float(os.getenv("DEFAULT_SPAWN_RATE", "1"))
DEFAULT_RUN_TIME = os.getenv("DEFAULT_RUN_TIME", "2m")

# ============================================================================
# User Behavior Configuration
# ============================================================================
# Wait time between tasks (simulates user reading response)
# Format: between(min_seconds, max_seconds)
WAIT_TIME_MIN = float(os.getenv("WAIT_TIME_MIN", "2"))
WAIT_TIME_MAX = float(os.getenv("WAIT_TIME_MAX", "5"))

# ============================================================================
# Task Weights Configuration
# ============================================================================
# These control how often each task is executed relative to others
# Higher weight = more frequent execution
TASK_WEIGHT_CHAT_PAGE = int(os.getenv("TASK_WEIGHT_CHAT_PAGE", "3"))
TASK_WEIGHT_SEND_MESSAGE = int(os.getenv("TASK_WEIGHT_SEND_MESSAGE", "5"))

# ============================================================================
# Reporting Configuration
# ============================================================================
REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")
HTML_REPORT_PATH = os.getenv("HTML_REPORT_PATH", f"{REPORTS_DIR}/load_test_report.html")
TTF_DATA_PATH = os.getenv("TTF_DATA_PATH", f"{REPORTS_DIR}/ttf_data.csv")

# ============================================================================
# Login Endpoint Fallback Configuration
# ============================================================================
# Additional login endpoints to try if the primary one fails
LOGIN_ENDPOINT_FALLBACKS = [
    "/api/auth/login",
    "/api/login",
    "/api/auth/signin",
    "/api/signin",
    "/auth/login",
    "/auth/signin",
    "/login",
    "/signin",
    "/"
]

# ============================================================================
# Request Headers Configuration
# ============================================================================
# Custom headers can be added here if needed
CUSTOM_HEADERS = {
    # Add any custom headers here
    # Example: "X-Custom-Header": "value"
}

