"""
Locust performance testing for chatbot
Supports 4 test types: load, stress, endurance, breakpoint
Primary metric: End-to-End Response Time

Usage:
  TEST_TYPE=load       locust -f src/locustfile.py
  TEST_TYPE=stress     locust -f src/locustfile.py
  TEST_TYPE=endurance  locust -f src/locustfile.py
  TEST_TYPE=breakpoint locust -f src/locustfile.py
"""
import csv
import json
import math
import random
import time
from datetime import datetime
from pathlib import Path

from locust import task, between, events, LoadTestShape
from locust.contrib.fasthttp import FastHttpUser

import sys
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
    LOGIN_ENDPOINT_FALLBACKS,
    TEST_TYPE,
    ACTIVE_USERS,
    ACTIVE_SPAWN_RATE,
    ACTIVE_RUN_TIME,
    BREAKPOINT_MAX_USERS,
    BREAKPOINT_RAMP_USERS_PER_STEP,
    BREAKPOINT_STEP_DURATION,
    REPORTS_DIR,
)

from src.sample_questions import get_sample_messages, get_question_category

SAMPLE_MESSAGES = get_sample_messages()

# ---------------------------------------------------------------------------
# CSV logging – captures question, answer, and e2e response time
# ---------------------------------------------------------------------------
RESPONSE_TIME_CSV = None


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    global RESPONSE_TIME_CSV
    reports = Path(REPORTS_DIR)
    reports.mkdir(parents=True, exist_ok=True)
    RESPONSE_TIME_CSV = reports / f"response_times_{TEST_TYPE}.csv"

    if not RESPONSE_TIME_CSV.exists() or RESPONSE_TIME_CSV.stat().st_size == 0:
        with open(RESPONSE_TIME_CSV, "w", newline="") as f:
            csv.writer(f).writerow([
                "timestamp",
                "test_type",
                "question_category",
                "question",
                "answer",
                "response_time_ms",
                "status_code",
                "status",
            ])
    print(
        f"=== Running {TEST_TYPE.upper()} test | "
        f"users={ACTIVE_USERS} | run_time={ACTIVE_RUN_TIME} ==="
    )


# ---------------------------------------------------------------------------
# Breakpoint test shape – step-ramp until cap
# ---------------------------------------------------------------------------
class BreakpointShape(LoadTestShape):
    """Ramps users in steps until max_users or run_time is reached.
    Only activates when TEST_TYPE=breakpoint."""

    def tick(self):
        if TEST_TYPE != "breakpoint":
            return None

        run_time = self.get_run_time()
        total_seconds = _parse_run_time(ACTIVE_RUN_TIME)
        if run_time > total_seconds:
            return None

        current_step = math.floor(run_time / BREAKPOINT_STEP_DURATION)
        target_users = min(
            (current_step + 1) * BREAKPOINT_RAMP_USERS_PER_STEP,
            BREAKPOINT_MAX_USERS,
        )
        return (target_users, max(BREAKPOINT_RAMP_USERS_PER_STEP, 1))


def _parse_run_time(rt: str) -> int:
    """Convert '20m' / '8h' / '30s' to seconds."""
    rt = rt.strip().lower()
    if rt.endswith("h"):
        return int(rt[:-1]) * 3600
    if rt.endswith("m"):
        return int(rt[:-1]) * 60
    if rt.endswith("s"):
        return int(rt[:-1])
    return int(rt)


# ---------------------------------------------------------------------------
# Virtual user
# ---------------------------------------------------------------------------
class ChatbotUser(FastHttpUser):
    """Authenticates, then sends chat messages.
    Captures the full answer and end-to-end response time."""

    host = CHATBOT_URL
    wait_time = between(WAIT_TIME_MIN, WAIT_TIME_MAX)

    def on_start(self):
        self.is_authenticated = False
        with self.client.get("/", name="Load Login Page", catch_response=True) as resp:
            if resp.status_code not in [200, 302]:
                resp.failure(f"Failed to load login page: {resp.status_code}")
                return
        self.login()
        if self.is_authenticated:
            with self.client.get("/chat", name="Load Chat Page", catch_response=True) as resp:
                if resp.status_code in [200, 302]:
                    resp.success()
                else:
                    resp.failure(f"Failed to load chat page: {resp.status_code}")

    # -- authentication -------------------------------------------------------
    def login(self):
        if not LOGIN_EMAIL or not LOGIN_PASSWORD:
            print("WARNING: LOGIN_EMAIL or LOGIN_PASSWORD not set")
            return

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": CHATBOT_URL,
            "Referer": f"{CHATBOT_URL}/",
        }
        payload = {"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD}
        endpoints = list(dict.fromkeys([API_ENDPOINT_LOGIN] + LOGIN_ENDPOINT_FALLBACKS))

        for endpoint in endpoints:
            with self.client.post(
                endpoint, json=payload, headers=headers,
                catch_response=True, name="Login",
            ) as resp:
                if resp.status_code in [200, 201, 302]:
                    self.is_authenticated = True
                    resp.success()
                    return
                if resp.status_code == 401:
                    resp.failure("401 Unauthorized – check credentials")
                    return
                if resp.status_code == 404 and endpoint != endpoints[-1]:
                    resp.success()
                    continue
                resp.failure(f"Login failed: {resp.status_code}")

            if resp.status_code in [404, 415]:
                form_headers = {**headers, "Content-Type": "application/x-www-form-urlencoded"}
                with self.client.post(
                    endpoint, data=payload, headers=form_headers,
                    catch_response=True, name="Login (form-data)",
                ) as form_resp:
                    if form_resp.status_code in [200, 201, 302]:
                        self.is_authenticated = True
                        form_resp.success()
                        return
                    if form_resp.status_code == 401:
                        form_resp.failure("401 Unauthorized")
                        return

        if hasattr(self.client, "cookies") and len(self.client.cookies) > 0:
            self.is_authenticated = True

    # -- primary task ---------------------------------------------------------
    @task
    def send_chat_message(self):
        if not self.is_authenticated:
            self.login()
            if not self.is_authenticated:
                return

        message = random.choice(SAMPLE_MESSAGES)
        category = get_question_category(message)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": CHATBOT_URL,
            "Referer": f"{CHATBOT_URL}/chat",
        }
        payload = {"message_content": message}

        start = time.time()
        with self.client.post(
            API_ENDPOINT_SEND, json=payload, headers=headers,
            catch_response=True, name=f"Chat [{category}]",
        ) as resp:
            response_time_ms = (time.time() - start) * 1000
            answer_text = ""

            if resp.status_code in [200, 201]:
                resp.success()
                answer_text = _extract_answer(resp)
                self._log(category, message, answer_text, response_time_ms,
                          resp.status_code, "Success")
            elif resp.status_code == 401:
                resp.failure("401 Unauthorized")
                self.is_authenticated = False
                self._log(category, message, "", response_time_ms,
                          resp.status_code, "401 Unauthorized")
            else:
                resp.failure(f"Status {resp.status_code}")
                self._log(category, message, "", response_time_ms,
                          resp.status_code, f"Error {resp.status_code}")

    # -- logging --------------------------------------------------------------
    def _log(self, category, question, answer, response_time_ms, status_code, status):
        try:
            if not RESPONSE_TIME_CSV:
                return
            with open(RESPONSE_TIME_CSV, "a", newline="") as f:
                csv.writer(f).writerow([
                    datetime.now().isoformat(),
                    TEST_TYPE,
                    category,
                    question[:200],
                    answer[:500] if answer else "",
                    round(response_time_ms, 2),
                    status_code,
                    status,
                ])
        except Exception:
            pass


def _extract_answer(resp) -> str:
    """Best-effort extraction of the chatbot answer from the API response."""
    try:
        data = resp.json()
        if isinstance(data, dict):
            for key in ("response", "message", "answer", "text", "content", "reply"):
                if key in data and isinstance(data[key], str):
                    return data[key]
            if "conversations" in data and isinstance(data["conversations"], list):
                convos = data["conversations"]
                if convos:
                    last = convos[-1]
                    if isinstance(last, dict):
                        for key in ("response", "message", "answer", "text", "content"):
                            if key in last:
                                return str(last[key])
            return json.dumps(data)[:500]
    except Exception:
        pass
    try:
        return resp.text[:500]
    except Exception:
        return ""
