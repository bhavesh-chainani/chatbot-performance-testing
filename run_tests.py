#!/usr/bin/env python3
"""
Performance Testing Script for Chatbot
Supports 4 test types: load, endurance, stress, breakpoint

Usage:
    python run_tests.py load                    # Run load test with defaults
    python run_tests.py endurance              # Run endurance test with defaults
    python run_tests.py stress                 # Run stress test with defaults
    python run_tests.py breakpoint             # Run breakpoint test with defaults
    
    # Override defaults with custom parameters:
    python run_tests.py load [users] [spawn_rate] [duration]
    python run_tests.py endurance [users] [spawn_rate] [duration]
    python run_tests.py stress [users] [spawn_rate] [duration]
    
    # Example:
    python run_tests.py load 10 2 5m
"""
import os
import sys
import subprocess
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create reports directory
Path("reports").mkdir(exist_ok=True)

CHATBOT_URL = os.getenv("CHATBOT_URL", "https://cfoti.org")


def run_load_test(users=None, spawn_rate=None, run_time=None):
    """Run load test - normal expected load conditions"""
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
    print("  • Test normal expected load conditions")
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
    
    report_path = Path("reports/load_test_report.html")
    
    try:
        result = subprocess.run(cmd, check=False)
        
        # Check if reports were generated (test completed successfully)
        if report_path.exists():
            print("\n" + "=" * 60)
            print("LOAD TEST COMPLETED!")
            print("=" * 60)
            if result.returncode != 0:
                print("\n⚠️  Note: Some requests failed (this is normal in performance testing)")
                print("   Check the HTML report for detailed failure information.")
            print("\nReports generated:")
            print("  • HTML Report: reports/load_test_report.html")
            print("  • CSV Stats: reports/load_test_report_stats.csv")
            print("  • TTF Data: reports/ttf_data.csv")
            print("\nOpen reports/load_test_report.html in your browser to view results.")
            return True
        else:
            print(f"\n❌ Error: Test did not complete successfully (exit code: {result.returncode})")
            print("Reports were not generated. Check the error messages above.")
            return False
    except KeyboardInterrupt:
        print("\n\nLoad test interrupted by user")
        return False


def run_endurance_test(users=None, spawn_rate=None, run_time=None):
    """Run endurance test - long duration with moderate load"""
    # Load defaults from config if not provided
    if users is None or spawn_rate is None or run_time is None:
        try:
            from config_endurance_test import ENDURANCE_TEST_CONFIG
            users = users or ENDURANCE_TEST_CONFIG["users"]
            spawn_rate = spawn_rate or ENDURANCE_TEST_CONFIG["spawn_rate"]
            run_time = run_time or ENDURANCE_TEST_CONFIG["run_time"]
        except ImportError:
            # Fallback defaults
            users = users or 3
            spawn_rate = spawn_rate or 0.5
            run_time = run_time or "10m"
    
    print("=" * 60)
    print("CHATBOT ENDURANCE TEST")
    print("=" * 60)
    print(f"Users: {users}")
    print(f"Spawn Rate: {spawn_rate} users/second")
    print(f"Duration: {run_time}")
    print(f"Host: {CHATBOT_URL}")
    print("-" * 60)
    print("\nThis test will:")
    print("  • Run for extended duration with moderate load")
    print("  • Identify memory leaks and performance degradation")
    print("  • Check for resource exhaustion over time")
    print("  • Test system stability under sustained load")
    print("\nStarting test...\n")
    
    cmd = [
        "locust",
        "-f", "locustfile.py",
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", run_time,
        "--host", CHATBOT_URL,
        "--headless",
        "--html", "reports/endurance_test_report.html",
        "--csv", "reports/endurance_test_report"
    ]
    
    report_path = Path("reports/endurance_test_report.html")
    
    try:
        result = subprocess.run(cmd, check=False)
        
        # Check if reports were generated (test completed successfully)
        if report_path.exists():
            print("\n" + "=" * 60)
            print("ENDURANCE TEST COMPLETED!")
            print("=" * 60)
            if result.returncode != 0:
                print("\n⚠️  Note: Some requests failed (this is normal in performance testing)")
                print("   Check the HTML report for detailed failure information.")
            print("\nReports generated:")
            print("  • HTML Report: reports/endurance_test_report.html")
            print("  • CSV Stats: reports/endurance_test_report_stats.csv")
            print("  • TTF Data: reports/ttf_data.csv")
            print("\nOpen reports/endurance_test_report.html in your browser to view results.")
            return True
        else:
            print(f"\n❌ Error: Test did not complete successfully (exit code: {result.returncode})")
            print("Reports were not generated. Check the error messages above.")
            return False
    except KeyboardInterrupt:
        print("\n\nEndurance test interrupted by user")
        return False


def run_stress_test(users=None, spawn_rate=None, run_time=None):
    """Run stress test - high load beyond normal capacity"""
    # Load defaults from config if not provided
    if users is None or spawn_rate is None or run_time is None:
        try:
            from config_stress_test import STRESS_TEST_CONFIG
            users = users or STRESS_TEST_CONFIG["users"]
            spawn_rate = spawn_rate or STRESS_TEST_CONFIG["spawn_rate"]
            run_time = run_time or STRESS_TEST_CONFIG["run_time"]
        except ImportError:
            # Fallback defaults
            users = users or 10
            spawn_rate = spawn_rate or 2
            run_time = run_time or "5m"
    
    print("=" * 60)
    print("CHATBOT STRESS TEST")
    print("=" * 60)
    print(f"Users: {users}")
    print(f"Spawn Rate: {spawn_rate} users/second")
    print(f"Duration: {run_time}")
    print(f"Host: {CHATBOT_URL}")
    print("-" * 60)
    print("\nThis test will:")
    print("  • Push system beyond normal capacity")
    print("  • Identify maximum capacity limits")
    print("  • Find performance bottlenecks under stress")
    print("  • Test error handling and recovery capabilities")
    print("\nStarting test...\n")
    
    cmd = [
        "locust",
        "-f", "locustfile.py",
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", run_time,
        "--host", CHATBOT_URL,
        "--headless",
        "--html", "reports/stress_test_report.html",
        "--csv", "reports/stress_test_report"
    ]
    
    report_path = Path("reports/stress_test_report.html")
    
    try:
        result = subprocess.run(cmd, check=False)
        
        # Check if reports were generated (test completed successfully)
        if report_path.exists():
            print("\n" + "=" * 60)
            print("STRESS TEST COMPLETED!")
            print("=" * 60)
            if result.returncode != 0:
                print("\n⚠️  Note: Some requests failed (this is expected in stress testing)")
                print("   Check the HTML report for detailed failure information.")
            print("\nReports generated:")
            print("  • HTML Report: reports/stress_test_report.html")
            print("  • CSV Stats: reports/stress_test_report_stats.csv")
            print("  • TTF Data: reports/ttf_data.csv")
            print("\nOpen reports/stress_test_report.html in your browser to view results.")
            return True
        else:
            print(f"\n❌ Error: Test did not complete successfully (exit code: {result.returncode})")
            print("Reports were not generated. Check the error messages above.")
            return False
    except KeyboardInterrupt:
        print("\n\nStress test interrupted by user")
        return False


def run_breakpoint_test():
    """Run breakpoint test - gradually increase load until system fails"""
    try:
        from config_breakpoint_test import BREAKPOINT_TEST_CONFIG
        start_users = BREAKPOINT_TEST_CONFIG["start_users"]
        max_users = BREAKPOINT_TEST_CONFIG["max_users"]
        spawn_rate = BREAKPOINT_TEST_CONFIG["spawn_rate"]
        step_duration = BREAKPOINT_TEST_CONFIG["step_duration"]
        user_increment = BREAKPOINT_TEST_CONFIG["user_increment"]
    except ImportError:
        # Fallback defaults
        start_users = 1
        max_users = 15
        spawn_rate = 1
        step_duration = "1m"
        user_increment = 2
    
    print("=" * 60)
    print("CHATBOT BREAKPOINT TEST")
    print("=" * 60)
    print(f"Start Users: {start_users}")
    print(f"Max Users: {max_users}")
    print(f"Spawn Rate: {spawn_rate} users/second")
    print(f"Step Duration: {step_duration}")
    print(f"User Increment: {user_increment} users per step")
    print(f"Host: {CHATBOT_URL}")
    print("-" * 60)
    print("\nThis test will:")
    print("  • Gradually increase load from {} to {} users".format(start_users, max_users))
    print("  • Run {} at each load level".format(step_duration))
    print("  • Identify exact breaking point")
    print("  • Test graceful degradation under overload")
    print("\nStarting test...\n")
    
    current_users = start_users
    step_number = 1
    
    while current_users <= max_users:
        print(f"\n{'='*60}")
        print(f"STEP {step_number}: Testing with {current_users} users")
        print(f"{'='*60}\n")
        
        cmd = [
            "locust",
            "-f", "locustfile.py",
            "--users", str(current_users),
            "--spawn-rate", str(spawn_rate),
            "--run-time", step_duration,
            "--host", CHATBOT_URL,
            "--headless",
            "--html", f"reports/breakpoint_test_step_{step_number}_{current_users}users.html",
            "--csv", f"reports/breakpoint_test_step_{step_number}_{current_users}users"
        ]
        
        try:
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            
            # Check if report was generated
            step_report_path = Path(f"reports/breakpoint_test_step_{step_number}_{current_users}users.html")
            
            if step_report_path.exists():
                # Check for high failure rate (indicator of breakpoint)
                if "FAILURES" in result.stdout or result.returncode != 0:
                    print(f"\n⚠️  Failures detected at {current_users} users")
                    print("This may indicate the system is approaching its breaking point.")
                
                print(f"✓ Step {step_number} completed with {current_users} users")
            else:
                print(f"\n❌ Step {step_number} failed at {current_users} users - no report generated")
                raise subprocess.CalledProcessError(result.returncode, cmd)
            
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Step {step_number} failed at {current_users} users")
            print(f"Error: {e}")
            print(f"\n⚠️  BREAKPOINT DETECTED!")
            print(f"The system appears to have reached its breaking point at {current_users} users.")
            if step_number > 1:
                print(f"Previous successful load: {current_users - user_increment} users")
            break
        except Exception as e:
            print(f"\n❌ Step {step_number} encountered an error at {current_users} users")
            print(f"Error: {e}")
            print(f"\n⚠️  BREAKPOINT DETECTED!")
            print(f"The system appears to have reached its breaking point at {current_users} users.")
            if step_number > 1:
                print(f"Previous successful load: {current_users - user_increment} users")
            break
        
        except KeyboardInterrupt:
            print(f"\n\nBreakpoint test interrupted by user at {current_users} users")
            print(f"Last successful load: {current_users} users")
            break
        
        # Increment for next step
        current_users += user_increment
        step_number += 1
        
        # Small delay between steps
        if current_users <= max_users:
            print(f"\nWaiting 5 seconds before next step...")
            time.sleep(5)
    
    print("\n" + "=" * 60)
    print("BREAKPOINT TEST COMPLETED!")
    print("=" * 60)
    print(f"\nTested up to {current_users - user_increment} users")
    print("\nReports generated:")
    for i in range(1, step_number):
        print(f"  • Step {i}: reports/breakpoint_test_step_{i}_*.html")
    print("\nReview the reports to identify the exact breaking point.")
    return True


def print_usage():
    """Print usage information"""
    print("=" * 60)
    print("CHATBOT PERFORMANCE TESTING")
    print("=" * 60)
    print("\nAvailable test types:")
    print("  1. load       - Normal expected load conditions")
    print("  2. endurance  - Long duration, moderate load (memory leaks)")
    print("  3. stress     - High load beyond normal capacity")
    print("  4. breakpoint - Gradually increase load until failure")
    print("\nUsage:")
    print("  python run_tests.py [test_type] [users] [spawn_rate] [duration]")
    print("\nExamples:")
    print("  python run_tests.py load                    # Use defaults")
    print("  python run_tests.py load 10 2 5m           # Custom parameters")
    print("  python run_tests.py endurance              # Use defaults")
    print("  python run_tests.py stress                 # Use defaults")
    print("  python run_tests.py breakpoint             # Use defaults")
    print("\nConfiguration:")
    print("  Edit test_config.py or set environment variables to customize")
    print("  All test configurations are in config_*_test.py files")
    print("=" * 60)


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    test_type = sys.argv[1].lower()
    
    # Parse optional parameters
    users = None
    spawn_rate = None
    run_time = None
    
    if len(sys.argv) > 2:
        try:
            users = int(sys.argv[2])
            spawn_rate = float(sys.argv[3]) if len(sys.argv) > 3 else None
            run_time = sys.argv[4] if len(sys.argv) > 4 else None
        except (ValueError, IndexError):
            print("Error: Invalid parameters")
            print_usage()
            sys.exit(1)
    
    # Run appropriate test
    if test_type == "load":
        run_load_test(users, spawn_rate, run_time)
    elif test_type == "endurance":
        run_endurance_test(users, spawn_rate, run_time)
    elif test_type == "stress":
        run_stress_test(users, spawn_rate, run_time)
    elif test_type == "breakpoint":
        if users is not None or spawn_rate is not None or run_time is not None:
            print("Warning: Breakpoint test uses its own configuration.")
            print("Parameters are ignored. Edit config_breakpoint_test.py to customize.")
        run_breakpoint_test()
    else:
        print(f"Error: Unknown test type '{test_type}'")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
