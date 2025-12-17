#!/usr/bin/env python3
"""
Simple load testing script for chatbot performance testing
Usage: python run_tests.py [users] [spawn_rate] [duration]
   or: python run_tests.py (uses config_load_test.py defaults)
"""
import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create reports directory
Path("reports").mkdir(exist_ok=True)

CHATBOT_URL = os.getenv("CHATBOT_URL", "https://cfoti.org")


def run_load_test(users=None, spawn_rate=None, run_time=None):
    """Run load test with specified or default parameters"""
    # Load defaults from config if not provided
    if users is None or spawn_rate is None or run_time is None:
        try:
            from config_load_test import LOAD_TEST_CONFIG
            users = users or LOAD_TEST_CONFIG["users"]
            spawn_rate = spawn_rate or LOAD_TEST_CONFIG["spawn_rate"]
            run_time = run_time or LOAD_TEST_CONFIG["run_time"]
        except ImportError:
            # Fallback defaults
            users = users or 5
            spawn_rate = spawn_rate or 1
            run_time = run_time or "2m"
    
    print("=" * 60)
    print("CHATBOT LOAD TEST")
    print("=" * 60)
    print(f"Users: {users}")
    print(f"Spawn Rate: {spawn_rate} users/second")
    print(f"Duration: {run_time}")
    print(f"Host: {CHATBOT_URL}")
    print("-" * 60)
    print("\nThis test will:")
    print("  • Login with credentials from .env")
    print("  • Send chat messages (Simple, Common, Complex questions)")
    print("  • Track Time To First Token (TTF) for each question")
    print("  • Generate performance reports")
    print("\nStarting test...\n")
    
    cmd = [
        "locust",
        "-f", "locustfile.py",
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", run_time,
        "--host", CHATBOT_URL,
        "--headless",
        "--html", "reports/load_test_report.html",
        "--csv", "reports/load_test_report"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n" + "=" * 60)
        print("LOAD TEST COMPLETED!")
        print("=" * 60)
        print("\nReports generated:")
        print("  • HTML Report: reports/load_test_report.html")
        print("  • CSV Stats: reports/load_test_report_stats.csv")
        print("  • TTF Data: reports/ttf_data.csv")
        print("\nOpen reports/load_test_report.html in your browser to view results.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nError running load test: {e}")
        return False
    except KeyboardInterrupt:
        print("\n\nLoad test interrupted by user")
        return False


def main():
    """Main function"""
    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            users = int(sys.argv[1])
            spawn_rate = float(sys.argv[2]) if len(sys.argv) > 2 else None
            run_time = sys.argv[3] if len(sys.argv) > 3 else None
            run_load_test(users, spawn_rate, run_time)
        except ValueError:
            print("Usage: python run_tests.py [users] [spawn_rate] [duration]")
            print("Example: python run_tests.py 10 2 5m")
            print("\nOr use defaults from config_load_test.py:")
            print("  python run_tests.py")
            sys.exit(1)
    else:
        # Use defaults from config
        run_load_test()


if __name__ == "__main__":
    main()

