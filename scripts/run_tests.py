#!/usr/bin/env python3
"""
Performance Testing Script for Chatbot
Supports 4 test types: load, endurance, stress, breakpoint

Usage:
    python scripts/run_tests.py load                    # Run load test with defaults
    python scripts/run_tests.py endurance              # Run endurance test with defaults
    python scripts/run_tests.py stress                 # Run stress test with defaults
    python scripts/run_tests.py breakpoint             # Run breakpoint test with defaults
    
    # Override defaults with custom parameters:
    python scripts/run_tests.py load [users] [spawn_rate] [duration]
    python scripts/run_tests.py endurance [users] [spawn_rate] [duration]
    python scripts/run_tests.py stress [users] [spawn_rate] [duration]
    
    # Example:
    python scripts/run_tests.py load 10 2 5m
"""
import os
import sys
import subprocess
import time
import csv
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Create reports directory
Path("reports").mkdir(exist_ok=True)

from config.test_config import CHATBOT_URL


def run_load_test(users=None, spawn_rate=None, run_time=None):
    """Run load test - normal expected load conditions"""
    # Load defaults from config if not provided
    if users is None or spawn_rate is None or run_time is None:
        try:
            from config.config_load_test import LOAD_TEST_CONFIG
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
        "-f", "src/locustfile.py",
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
            from config.config_endurance_test import ENDURANCE_TEST_CONFIG
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
        "-f", "src/locustfile.py",
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
            from config.config_stress_test import STRESS_TEST_CONFIG
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
        "-f", "src/locustfile.py",
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


def _generate_breakpoint_summary_report(steps_data, breaking_point_users):
    """Generate a consolidated HTML report for breakpoint test"""
    from datetime import datetime
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Breakpoint Test Summary Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .summary {{
            background-color: #e8f5e9;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .breaking-point {{
            background-color: #ffebee;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 5px solid #f44336;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .failed {{
            background-color: #ffebee;
            font-weight: bold;
        }}
        .warning {{
            background-color: #fff3e0;
        }}
        .success {{
            background-color: #e8f5e9;
        }}
        .metric {{
            font-weight: bold;
            color: #1976D2;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Breakpoint Test Summary Report</h1>
        <div class="summary">
            <h2>Test Overview</h2>
            <p><strong>Test Date:</strong> {test_date}</p>
            <p><strong>Total Steps:</strong> {total_steps}</p>
            <p><strong>Users Tested:</strong> {start_users} to {max_users}</p>
            <p><strong>Breaking Point:</strong> <span style="color: #f44336; font-weight: bold;">{breaking_point}</span></p>
        </div>
"""
    
    if breaking_point_users:
        html_content += f"""
        <div class="breaking-point">
            <h2>⚠️ Breaking Point Detected</h2>
            <p>The system reached its breaking point at <strong>{breaking_point_users} concurrent users</strong>.</p>
            <p>Last successful load: <strong>{breaking_point_users - steps_data[-1]['user_increment'] if steps_data else 'N/A'} users</strong></p>
        </div>
"""
    
    html_content += """
        <h2>Step-by-Step Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Step</th>
                    <th>Users</th>
                    <th>Requests</th>
                    <th>Failures</th>
                    <th>Failure %</th>
                    <th>Avg Response (ms)</th>
                    <th>Median Response (ms)</th>
                    <th>95th %ile (ms)</th>
                    <th>RPS</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for step in steps_data:
        failure_rate = (step['failures'] / step['requests'] * 100) if step['requests'] > 0 else 0
        row_class = "failed" if failure_rate > 10 else ("warning" if failure_rate > 0 else "success")
        
        html_content += f"""
                <tr class="{row_class}">
                    <td>{step['step']}</td>
                    <td class="metric">{step['users']}</td>
                    <td>{step['requests']}</td>
                    <td>{step['failures']}</td>
                    <td>{failure_rate:.2f}%</td>
                    <td>{step['avg_response']:.0f}</td>
                    <td>{step['median_response']:.0f}</td>
                    <td>{step['p95_response']:.0f}</td>
                    <td>{step['rps']:.2f}</td>
                    <td>{'❌ Failed' if failure_rate > 10 else ('⚠️ Degraded' if failure_rate > 0 else '✅ OK')}</td>
                </tr>
"""
    
    # Format the HTML with actual data
    test_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_users = steps_data[0]['users'] if steps_data else 'N/A'
    max_users = steps_data[-1]['users'] if steps_data else 'N/A'
    breaking_point = f"{breaking_point_users} users" if breaking_point_users else "Not reached"
    
    html_content += """
            </tbody>
        </table>
        <div class="footer">
            <p><strong>Legend:</strong></p>
            <p><span class="success" style="padding: 5px 10px; border-radius: 3px;">✅ OK</span> - No failures detected</p>
            <p><span class="warning" style="padding: 5px 10px; border-radius: 3px;">⚠️ Degraded</span> - Some failures (&lt;10%)</p>
            <p><span class="failed" style="padding: 5px 10px; border-radius: 3px;">❌ Failed</span> - High failure rate (&gt;10%)</p>
            <p style="margin-top: 20px;"><em>Generated on """ + test_date + """</em></p>
        </div>
    </div>
</body>
</html>
"""
    
    # Format the HTML with actual data (only the placeholders, CSS is already escaped)
    html_content = html_content.format(
        test_date=test_date,
        total_steps=len(steps_data),
        start_users=start_users,
        max_users=max_users,
        breaking_point=breaking_point
    )
    
    # Write the HTML file
    report_path = Path("reports/breakpoint_test_summary.html")
    with open(report_path, 'w') as f:
        f.write(html_content)
    
    return report_path


def run_breakpoint_test():
    """Run breakpoint test - gradually increase load until system fails"""
    try:
        from config.config_breakpoint_test import BREAKPOINT_TEST_CONFIG
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
    print("  • Generate consolidated summary report")
    print("\nStarting test...\n")
    
    current_users = start_users
    step_number = 1
    steps_data = []
    breaking_point_users = None
    
    while current_users <= max_users:
        print(f"\n{'='*60}")
        print(f"STEP {step_number}: Testing with {current_users} users")
        print(f"{'='*60}\n")
        
        cmd = [
            "locust",
            "-f", "src/locustfile.py",
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
            csv_path = Path(f"reports/breakpoint_test_step_{step_number}_{current_users}users_stats.csv")
            
            if step_report_path.exists() and csv_path.exists():
                # Parse CSV to extract metrics
                try:
                    with open(csv_path, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row.get('Type') == '' and row.get('Name') == 'Aggregated':
                                # Found aggregated row
                                requests = int(row.get('Request Count', 0))
                                failures = int(row.get('Failure Count', 0))
                                avg_response = float(row.get('Average Response Time', 0))
                                median_response = float(row.get('Median Response Time', 0))
                                p95_response = float(row.get('95%', 0))
                                rps = float(row.get('Requests/s', 0))
                                
                                steps_data.append({
                                    'step': step_number,
                                    'users': current_users,
                                    'requests': requests,
                                    'failures': failures,
                                    'avg_response': avg_response,
                                    'median_response': median_response,
                                    'p95_response': p95_response,
                                    'rps': rps,
                                    'user_increment': user_increment
                                })
                                
                                failure_rate = (failures / requests * 100) if requests > 0 else 0
                                
                                if failure_rate > 10:
                                    print(f"\n⚠️  High failure rate ({failure_rate:.2f}%) detected at {current_users} users")
                                    print("This indicates the system is at or past its breaking point.")
                                    if breaking_point_users is None:
                                        breaking_point_users = current_users
                                elif failures > 0:
                                    print(f"\n⚠️  Some failures ({failures}/{requests}) detected at {current_users} users")
                                
                                break
                except Exception as e:
                    print(f"Warning: Could not parse CSV metrics: {e}")
                
                print(f"✓ Step {step_number} completed with {current_users} users")
            else:
                print(f"\n❌ Step {step_number} failed at {current_users} users - no report generated")
                if breaking_point_users is None:
                    breaking_point_users = current_users
                break
            
        except KeyboardInterrupt:
            print(f"\n\nBreakpoint test interrupted by user at {current_users} users")
            if step_number > 1:
                print(f"Last successful load: {steps_data[-1]['users'] if steps_data else current_users - user_increment} users")
            break
        except Exception as e:
            print(f"\n❌ Step {step_number} encountered an error at {current_users} users")
            print(f"Error: {e}")
            if breaking_point_users is None:
                breaking_point_users = current_users
            break
        
        # Increment for next step
        current_users += user_increment
        step_number += 1
        
        # Small delay between steps
        if current_users <= max_users:
            print(f"\nWaiting 5 seconds before next step...")
            time.sleep(5)
    
    # Generate consolidated summary report
    if steps_data:
        print("\n" + "=" * 60)
        print("Generating consolidated summary report...")
        print("=" * 60)
        
        summary_report_path = _generate_breakpoint_summary_report(steps_data, breaking_point_users)
        
        print("\n" + "=" * 60)
        print("BREAKPOINT TEST COMPLETED!")
        print("=" * 60)
        print(f"\nTested up to {steps_data[-1]['users']} users")
        if breaking_point_users:
            print(f"\n⚠️  BREAKPOINT DETECTED at {breaking_point_users} users")
            print(f"Last successful load: {breaking_point_users - user_increment} users")
        else:
            print("\n✅ No breaking point detected within tested range")
        print("\nReports generated:")
        print(f"  • 📊 Consolidated Summary: {summary_report_path}")
        print(f"  • 📁 Individual Step Reports: reports/breakpoint_test_step_*.html")
        print("\nOpen the consolidated summary report to see the breaking point analysis.")
    else:
        print("\n" + "=" * 60)
        print("BREAKPOINT TEST COMPLETED!")
        print("=" * 60)
        print("\n⚠️  No data collected. Check individual step reports for details.")
    
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
    print("  python scripts/run_tests.py [test_type] [users] [spawn_rate] [duration]")
    print("\nExamples:")
    print("  python scripts/run_tests.py load                    # Use defaults")
    print("  python scripts/run_tests.py load 10 2 5m           # Custom parameters")
    print("  python scripts/run_tests.py endurance              # Use defaults")
    print("  python scripts/run_tests.py stress                 # Use defaults")
    print("  python scripts/run_tests.py breakpoint             # Use defaults")
    print("\nConfiguration:")
    print("  Edit config/test_config.py or set environment variables to customize")
    print("  All test configurations are in config/config_*_test.py files")
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
            print("Parameters are ignored. Edit config/config_breakpoint_test.py to customize.")
        run_breakpoint_test()
    else:
        print(f"Error: Unknown test type '{test_type}'")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
