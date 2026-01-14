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
# AWS Configuration
# ============================================================================
# Set AWS_REGION if your chatbot is hosted on AWS
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_PROFILE = os.getenv("AWS_PROFILE", "default")

# AWS API Gateway endpoint (if using API Gateway)
AWS_API_GATEWAY_URL = os.getenv("AWS_API_GATEWAY_URL", "")

# AWS CloudFront distribution (if using CloudFront)
AWS_CLOUDFRONT_DISTRIBUTION = os.getenv("AWS_CLOUDFRONT_DISTRIBUTION", "")

# AWS Cognito configuration (if using Cognito for authentication)
AWS_COGNITO_USER_POOL_ID = os.getenv("AWS_COGNITO_USER_POOL_ID", "")
AWS_COGNITO_CLIENT_ID = os.getenv("AWS_COGNITO_CLIENT_ID", "")
AWS_COGNITO_REGION = os.getenv("AWS_COGNITO_REGION", AWS_REGION)

# ============================================================================
# API Configuration
# ============================================================================
# Use AWS API Gateway URL if provided, otherwise use CHATBOT_URL
CHATBOT_URL = os.getenv("CHATBOT_URL", AWS_API_GATEWAY_URL or "https://your-chatbot-url.com")
API_ENDPOINT_LOGIN = os.getenv("API_ENDPOINT_LOGIN", "/api/auth/login")
API_ENDPOINT_SEND = os.getenv("API_ENDPOINT_SEND", "/api/chat")

# ============================================================================
# Authentication Configuration
# ============================================================================
LOGIN_EMAIL = os.getenv("LOGIN_EMAIL", "")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "")

# AWS Cognito authentication (alternative to email/password)
USE_AWS_COGNITO = os.getenv("USE_AWS_COGNITO", "false").lower() == "true"

# ============================================================================
# Load Test Configuration
# Normal expected load conditions - baseline performance testing
# ============================================================================
LOAD_TEST_USERS = int(os.getenv("LOAD_TEST_USERS", "5"))
LOAD_TEST_SPAWN_RATE = float(os.getenv("LOAD_TEST_SPAWN_RATE", "1"))
LOAD_TEST_RUN_TIME = os.getenv("LOAD_TEST_RUN_TIME", "2m")

# ============================================================================
# Endurance Test Configuration
# Long duration test with moderate load to check for memory leaks and degradation
# ============================================================================
ENDURANCE_TEST_USERS = int(os.getenv("ENDURANCE_TEST_USERS", "3"))
ENDURANCE_TEST_SPAWN_RATE = float(os.getenv("ENDURANCE_TEST_SPAWN_RATE", "0.5"))
ENDURANCE_TEST_RUN_TIME = os.getenv("ENDURANCE_TEST_RUN_TIME", "10m")

# ============================================================================
# Stress Test Configuration
# High load beyond normal capacity to find breaking point
# ============================================================================
STRESS_TEST_USERS = int(os.getenv("STRESS_TEST_USERS", "10"))
STRESS_TEST_SPAWN_RATE = float(os.getenv("STRESS_TEST_SPAWN_RATE", "2"))
STRESS_TEST_RUN_TIME = os.getenv("STRESS_TEST_RUN_TIME", "5m")

# ============================================================================
# Breakpoint Test Configuration
# Gradually increase load until system fails - finds exact breaking point
# ============================================================================
BREAKPOINT_TEST_START_USERS = int(os.getenv("BREAKPOINT_TEST_START_USERS", "1"))
BREAKPOINT_TEST_MAX_USERS = int(os.getenv("BREAKPOINT_TEST_MAX_USERS", "150"))
BREAKPOINT_TEST_SPAWN_RATE = float(os.getenv("BREAKPOINT_TEST_SPAWN_RATE", "1"))
BREAKPOINT_TEST_STEP_DURATION = os.getenv("BREAKPOINT_TEST_STEP_DURATION", "1m")
BREAKPOINT_TEST_USER_INCREMENT = int(os.getenv("BREAKPOINT_TEST_USER_INCREMENT", "20"))

# ============================================================================
# Legacy Defaults (for backward compatibility)
# ============================================================================
DEFAULT_USERS = LOAD_TEST_USERS
DEFAULT_SPAWN_RATE = LOAD_TEST_SPAWN_RATE
DEFAULT_RUN_TIME = LOAD_TEST_RUN_TIME

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
