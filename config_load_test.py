"""
Load Test Configuration
Tests normal expected load conditions
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Load test parameters - suitable for Locust Cloud free tier
LOAD_TEST_CONFIG = {
    "users": 5,  # Number of concurrent users (start simple)
    "spawn_rate": 1,  # Users spawned per second (start slow)
    "run_time": "2m",  # Test duration: 2 minutes (start short)
    "host": os.getenv("CHATBOT_URL", "https://cfoti.org"),
    "web_ui": True,  # Enable web UI
    "html_report": "reports/load_test_report.html"
}

