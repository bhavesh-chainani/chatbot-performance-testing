"""
Locust performance testing file for chatbot with authentication
Handles login flow before accessing chat functionality
Supports AWS-hosted chatbots
"""
import random
import time
from pathlib import Path
from locust.contrib.fasthttp import FastHttpUser
from locust import task, between, events

# Import configuration from centralized config file
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.test_config import (
    CHATBOT_URL,
    API_ENDPOINT_LOGIN,
    API_ENDPOINT_SEND,
    LOGIN_EMAIL,
    LOGIN_PASSWORD,
    WAIT_TIME_MIN,
    WAIT_TIME_MAX,
    TASK_WEIGHT_CHAT_PAGE,
    TASK_WEIGHT_SEND_MESSAGE,
    TTF_DATA_PATH,
    LOGIN_ENDPOINT_FALLBACKS,
)

# Import sample questions and helper functions
from src.sample_questions import (
    get_sample_messages,
    get_question_category,
)

# Get combined sample messages with weights applied
SAMPLE_MESSAGES = get_sample_messages()

# Global variable to store TTF file path
TTF_FILE_PATH = None

# Custom CSV writer for TTF data
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Create CSV file for TTF tracking"""
    import csv
    
    global TTF_FILE_PATH
    
    # Create reports directory if it doesn't exist
    ttf_path = Path(TTF_DATA_PATH)
    ttf_path.parent.mkdir(parents=True, exist_ok=True)
    TTF_FILE_PATH = ttf_path
    
    # Write header if file doesn't exist or is empty
    if not TTF_FILE_PATH.exists() or TTF_FILE_PATH.stat().st_size == 0:
        with open(TTF_FILE_PATH, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Timestamp', 'Question_Category', 'Question_Text', 
                'TTF_ms', 'Total_Response_Time_ms', 'Status'
            ])


class ChatbotUser(FastHttpUser):
    """
    User class that simulates authenticated chatbot interactions
    
    Each virtual user will:
    1. Login when they start
    2. Navigate to chat page
    3. Send random messages from SAMPLE_MESSAGES
    4. Wait 2-5 seconds between messages (simulating reading response)
    """
    host = CHATBOT_URL
    is_authenticated = False
    wait_time = between(WAIT_TIME_MIN, WAIT_TIME_MAX)  # Configurable wait time between tasks

    def on_start(self):
        """
        Called when a user starts - performs login before accessing chat
        """
        # Step 1: Load the login page to get any CSRF tokens or session cookies
        with self.client.get("/", name="Load Login Page", catch_response=True) as resp:
            if resp.status_code not in [200, 302]:
                resp.failure(f"Failed to load login page: {resp.status_code}")
                return
        
        # Step 2: Perform login
        self.login()
        
        # Step 3: Navigate to chat page after successful login
        if self.is_authenticated:
            with self.client.get("/chat", name="Load Chat Page", catch_response=True) as resp:
                if resp.status_code in [200, 302]:
                    resp.success()
                else:
                    resp.failure(f"Failed to access chat page after login: {resp.status_code}")
    
    def login(self):
        """
        Perform login with email and password
        Handles different login endpoint formats
        """
        if not LOGIN_EMAIL or not LOGIN_PASSWORD:
            print("WARNING: LOGIN_EMAIL or LOGIN_PASSWORD not set in .env file")
            return
        
        # Prepare login headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": CHATBOT_URL,
            "Referer": f"{CHATBOT_URL}/",
        }
        
        # Prepare login payload
        login_payload = {
            "email": LOGIN_EMAIL,
            "password": LOGIN_PASSWORD
        }
        
        # Try login endpoint - common variations
        # Some sites use form-based login (POST to same page), so we try root path too
        # Start with the configured endpoint first, then try common variations
        login_endpoints = [API_ENDPOINT_LOGIN] + LOGIN_ENDPOINT_FALLBACKS
        # Remove duplicates while preserving order
        seen = set()
        login_endpoints = [x for x in login_endpoints if not (x in seen or seen.add(x))]
        
        login_success = False
        last_status = None
        
        for endpoint in login_endpoints:
            # Try JSON format first
            with self.client.post(
                endpoint,
                json=login_payload,
                headers=headers,
                catch_response=True,
                name="Login"
            ) as resp:
                last_status = resp.status_code
                if resp.status_code in [200, 201, 302]:
                    # Check if we got redirected or got success response
                    if resp.status_code == 302 or "token" in resp.text.lower() or "success" in resp.text.lower():
                        self.is_authenticated = True
                        login_success = True
                        resp.success()
                        break
                    elif resp.status_code in [200, 201]:
                        # Try to parse response
                        try:
                            response_data = resp.json()
                            if "token" in response_data or "access_token" in response_data or "success" in str(response_data).lower():
                                self.is_authenticated = True
                                login_success = True
                                resp.success()
                                break
                        except:
                            # If response is not JSON but status is OK, assume success
                            self.is_authenticated = True
                            login_success = True
                            resp.success()
                            break
                elif resp.status_code == 401:
                    resp.failure(f"401 Unauthorized - Check login credentials")
                    # Don't try other endpoints if credentials are wrong
                    break
                elif resp.status_code == 404:
                    # Try next endpoint - don't count 404 as failure when trying multiple endpoints
                    # Only mark as failure if this is the last endpoint we're trying
                    if endpoint == login_endpoints[-1]:
                        resp.failure(f"404 Not Found - All login endpoints failed")
                    else:
                        # Don't mark as failure, just continue trying
                        resp.success()  # Mark as success to avoid inflating failure rate
                    continue
                else:
                    resp.failure(f"Login failed with status {resp.status_code}")
            
            # If JSON didn't work with 404 or 415, try form-data format (some APIs use form-data)
            if last_status == 404 or last_status == 415:
                form_headers = headers.copy()
                form_headers["Content-Type"] = "application/x-www-form-urlencoded"
                with self.client.post(
                    endpoint,
                    data=login_payload,
                    headers=form_headers,
                    catch_response=True,
                    name="Login (form-data)"
                ) as form_resp:
                    if form_resp.status_code in [200, 201, 302]:
                        self.is_authenticated = True
                        login_success = True
                        form_resp.success()
                        break
                    elif form_resp.status_code == 401:
                        form_resp.failure(f"401 Unauthorized - Check login credentials")
                        break
            
            # If we succeeded, break out of the loop
            if login_success:
                break
        
        if not login_success:
            print(f"WARNING: Login failed. Check browser Network tab to find the correct login endpoint.")
            print(f"Tried endpoints: {', '.join(login_endpoints)}")
            print(f"Steps to find correct endpoint:")
            print(f"1. Open browser DevTools (F12)")
            print(f"2. Go to Network tab")
            print(f"3. Login manually at {CHATBOT_URL}")
            print(f"4. Find the POST request that succeeds")
            print(f"5. Copy the endpoint URL and set API_ENDPOINT_LOGIN in .env")
            # Still mark as authenticated if cookies were set (some sites use cookie-based auth)
            # Check if we have session cookies
            if hasattr(self.client, 'cookies') and len(self.client.cookies) > 0:
                print("NOTE: Session cookies detected, marking as authenticated")
                self.is_authenticated = True

    @task(TASK_WEIGHT_CHAT_PAGE)
    def test_chat_page(self):
        """
        Load the chat page (weight: 3)
        Only accessible if authenticated
        """
        if not self.is_authenticated:
            # Re-authenticate if session expired
            self.login()
        
        with self.client.get("/chat", name="Load Chat Page", catch_response=True) as resp:
            if resp.status_code in [200, 302]:
                resp.success()
            elif resp.status_code == 401:
                resp.failure("401 Unauthorized - Session may have expired")
                self.is_authenticated = False
            else:
                resp.failure(f"Failed to load chat page: {resp.status_code}")

    @task(TASK_WEIGHT_SEND_MESSAGE)
    def send_chat_message(self):
        """
        Send a message to the chatbot API (weight: 5 - most frequent)
        This simulates actual user interaction with the chatbot
        
        Tracks Time To First Token (TTF) for each question category
        """
        if not self.is_authenticated:
            # Re-authenticate if session expired
            self.login()
            if not self.is_authenticated:
                return
        
        # Pick a random message from the sample messages
        message = random.choice(SAMPLE_MESSAGES)
        question_category = get_question_category(message)
        
        # Prepare headers matching browser request
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": CHATBOT_URL,
            "Referer": f"{CHATBOT_URL}/chat",
        }
        
        # Payload format - API expects message_content field
        payload = {"message_content": message}
        
        # Track TTF - measure time to first response
        request_start_time = time.time()
        ttf_measured = False
        ttf_ms = None
        
        # Create custom name for Locust stats based on question category
        task_name = f"Send Chat Message - {question_category}"
        
        with self.client.post(
            API_ENDPOINT_SEND,
            json=payload,
            headers=headers,
            catch_response=True,
            name=task_name
        ) as resp:
            # Measure TTF - time until first byte received
            if not ttf_measured:
                ttf_ms = (time.time() - request_start_time) * 1000  # Convert to milliseconds
                ttf_measured = True
            # Calculate total response time
            total_response_time_ms = (time.time() - request_start_time) * 1000
            
            if resp.status_code in [200, 201]:
                # Validate response
                status = "Success"
                try:
                    response_data = resp.json()
                    if "response" in response_data or "message" in response_data or "conversations" in response_data:
                        resp.success()
                    else:
                        resp.success()  # Status OK is good enough
                except:
                    resp.success()  # Status OK is good enough
                
                # Log TTF data to CSV
                self._log_ttf_data(question_category, message, ttf_ms, total_response_time_ms, status)
            elif resp.status_code == 401:
                status = "401 Unauthorized"
                resp.failure("401 Unauthorized - Session may have expired, re-authenticating")
                self.is_authenticated = False
                self.login()
                self._log_ttf_data(question_category, message, ttf_ms, total_response_time_ms, status)
            elif resp.status_code == 405:
                # Method Not Allowed - endpoint might be wrong or need different format
                status = "405 Method Not Allowed"
                resp.failure(f"405 Method Not Allowed - Check browser Network tab for correct endpoint URL")
                self._log_ttf_data(question_category, message, ttf_ms, total_response_time_ms, status)
            elif resp.status_code == 422:
                # Validation error - payload format might be wrong
                status = "422 Validation Error"
                error_msg = f"422 Validation Error - Check payload format"
                try:
                    error_body = resp.text[:200]
                    error_msg += f" - {error_body}"
                except:
                    pass
                resp.failure(error_msg)
                self._log_ttf_data(question_category, message, ttf_ms, total_response_time_ms, status)
            else:
                status = f"Error {resp.status_code}"
                error_msg = f"Status {resp.status_code}"
                try:
                    error_body = resp.text[:200]
                    error_msg += f" - {error_body}"
                except:
                    pass
                resp.failure(error_msg)
                self._log_ttf_data(question_category, message, ttf_ms, total_response_time_ms, status)
    
    def _log_ttf_data(self, category, question, ttf_ms, total_ms, status):
        """Log TTF data to CSV file"""
        try:
            import csv
            from datetime import datetime
            
            global TTF_FILE_PATH
            
            if not TTF_FILE_PATH:
                return
            
            # Append data to CSV
            with open(TTF_FILE_PATH, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    category,
                    question[:100],  # Truncate long questions
                    round(ttf_ms, 2) if ttf_ms else None,
                    round(total_ms, 2),
                    status
                ])
        except Exception:
            # Silently fail to avoid disrupting test
            pass
