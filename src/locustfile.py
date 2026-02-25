"""
Locust performance testing for chatbot
Auth: Pre-authenticated session cookie (SSO handled externally)
Chat: POST /api/chat/stream?ticket_id=X  (Server-Sent Events)
Metric: End-to-End Response Time

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

from locust import task, between, events, LoadTestShape, HttpUser
from locust.runners import WorkerRunner

import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.test_config import (
    CHATBOT_URL,
    API_ENDPOINT_CHAT,
    API_ENDPOINT_TICKETS,
    API_ENDPOINT_USERME,
    LOGIN_EMAIL,
    LOGIN_PASSWORD,
    SESSION_COOKIE,
    WAIT_TIME_MIN,
    WAIT_TIME_MAX,
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
# CSV logging
# ---------------------------------------------------------------------------
RESPONSE_TIME_CSV = None


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    global RESPONSE_TIME_CSV
    reports = Path(REPORTS_DIR)
    reports.mkdir(parents=True, exist_ok=True)
    RESPONSE_TIME_CSV = reports / f"response_times_{TEST_TYPE}.csv"

    # Use actual run params from Locust runner when available (UI/headless), else config
    runner = getattr(environment, "runner", None)
    users = getattr(runner, "target_user_count", None) if runner is not None else None
    if users is None or users == 0:
        users = ACTIVE_USERS
    spawn_rate = getattr(runner, "spawn_rate", None) if runner is not None else None
    if spawn_rate is None or spawn_rate == 0:
        spawn_rate = ACTIVE_SPAWN_RATE
    run_time = getattr(runner, "run_time", None) if runner is not None else None
    if run_time is None:
        opts = getattr(environment, "parsed_options", None)
        run_time = getattr(opts, "run_time", None) if opts else None
    if run_time is None:
        run_time = ACTIVE_RUN_TIME
    if isinstance(run_time, (int, float)):
        run_time = f"{int(run_time)}s" if run_time else ACTIVE_RUN_TIME
    host = CHATBOT_URL

    # Write run metadata only on master (or standalone). Workers don't get UI params and would write config defaults.
    meta_path = reports / f"run_meta_{TEST_TYPE}.json"
    if not isinstance(runner, WorkerRunner):
        with open(meta_path, "w") as f:
            json.dump({
                "users": users,
                "spawn_rate": spawn_rate,
                "host": host,
                "run_time": run_time,
            }, f, indent=2)

    if not RESPONSE_TIME_CSV.exists() or RESPONSE_TIME_CSV.stat().st_size == 0:
        with open(RESPONSE_TIME_CSV, "w", newline="") as f:
            csv.writer(f).writerow([
                "timestamp", "test_type", "question_category",
                "question", "answer", "response_time_ms",
                "status_code", "status",
            ])

    if not SESSION_COOKIE:
        print("WARNING: SESSION_COOKIE is empty in .env")
        print("  1. Log into cfoti.org in your browser")
        print("  2. DevTools > Application > Cookies > cfoti.org")
        print("  3. Copy the 'session' cookie value into .env")

    print(
        f"=== Running {TEST_TYPE.upper()} test | "
        f"users={ACTIVE_USERS} | run_time={ACTIVE_RUN_TIME} ==="
    )


# ---------------------------------------------------------------------------
# Breakpoint shape – only when TEST_TYPE=breakpoint
# ---------------------------------------------------------------------------
if TEST_TYPE == "breakpoint":
    class BreakpointShape(LoadTestShape):
        """Ramps users in steps until max_users or run_time is reached."""

        def tick(self):
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
class ChatbotUser(HttpUser):
    """
    Uses HttpUser (not FastHttpUser) for SSE streaming compatibility.
    Auth via pre-set session cookie from .env.
    Each user gets their own chat ticket.
    """

    host = CHATBOT_URL
    wait_time = between(WAIT_TIME_MIN, WAIT_TIME_MAX)

    def on_start(self):
        self.ticket_id = None
        self.is_authenticated = False

        if not SESSION_COOKIE:
            print("ERROR: No SESSION_COOKIE set. Cannot authenticate.")
            return

        self.client.cookies["session"] = SESSION_COOKIE
        self.client.cookies["isLoggedIn"] = "true"

        with self.client.get(
            API_ENDPOINT_USERME, name="Verify Auth", catch_response=True
        ) as resp:
            if resp.status_code == 200:
                self.is_authenticated = True
                try:
                    user_data = resp.json()
                    user_json = json.dumps({
                        "id": user_data.get("id", ""),
                        "email": user_data.get("email", ""),
                        "full_name": user_data.get("full_name", ""),
                        "is_admin": user_data.get("is_admin", False),
                        "uen": user_data.get("uen", ""),
                        "memtype": user_data.get("memtype", ""),
                        "created_at": user_data.get("created_at", ""),
                    })
                    self.client.cookies["user"] = user_json
                except Exception:
                    pass
                resp.success()
            else:
                resp.failure(f"Auth failed: {resp.status_code} – session cookie may be expired")
                return

        self._create_ticket()

    # -- ticket management ----------------------------------------------------
    def _create_ticket(self):
        """Create a new chat ticket, or fall back to an existing one."""
        with self.client.post(
            API_ENDPOINT_TICKETS,
            json={},
            name="Create Ticket",
            catch_response=True,
        ) as resp:
            if resp.status_code in [200, 201]:
                try:
                    data = resp.json()
                    self.ticket_id = data.get("ticket_id") or data.get("id")
                except Exception:
                    pass
                if self.ticket_id:
                    resp.success()
                    return
            resp.success()

        with self.client.get(
            f"{API_ENDPOINT_TICKETS}?offset=0&limit=1&order_by=updated_at:desc",
            name="Get Tickets",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    tickets = data if isinstance(data, list) else data.get("tickets", data.get("items", []))
                    if tickets:
                        self.ticket_id = tickets[0].get("ticket_id") or tickets[0].get("id")
                except Exception:
                    pass
                resp.success()
            else:
                resp.failure(f"Failed to get tickets: {resp.status_code}")

        if not self.ticket_id:
            print("WARNING: Could not create or find a chat ticket")

    # -- primary task ---------------------------------------------------------
    @task
    def send_chat_message(self):
        if not self.is_authenticated:
            return
        if not self.ticket_id:
            self._create_ticket()
            if not self.ticket_id:
                return

        message = random.choice(SAMPLE_MESSAGES)
        category = get_question_category(message)

        payload = {"message_content": message}

        start = time.time()
        with self.client.post(
            f"{API_ENDPOINT_CHAT}?ticket_id={self.ticket_id}",
            json=payload,
            name=f"Chat [{category}]",
            catch_response=True,
            timeout=120,
        ) as resp:
            response_time_ms = (time.time() - start) * 1000
            answer_text = ""

            if resp.status_code in [200, 201]:
                resp.success()
                answer_text = _parse_sse_response(resp.text)
                self._log(category, message, answer_text, response_time_ms,
                          resp.status_code, "Success")
            elif resp.status_code == 401:
                resp.failure("401 Unauthorized – session cookie expired")
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


def _parse_sse_response(text: str) -> str:
    """Parse cfoti SSE stream to extract the chatbot's final answer.

    Event format:
      data: {"type": "streaming_event", "data": {"payload": {
        "step_type": "reasoning", "status": "success", "output": "...answer..."
      }}}
    """
    for line in text.split("\n"):
        line = line.strip()
        if not line.startswith("data:"):
            continue
        try:
            evt = json.loads(line[5:].strip())
            if evt.get("type") == "streaming_event":
                payload = evt.get("data", {}).get("payload", {})
                if payload.get("status") == "success" and isinstance(payload.get("output"), str):
                    return payload["output"]
            if evt.get("type") == "message":
                msg = evt.get("data", {})
                if isinstance(msg, dict):
                    for key in ("content", "message", "text", "response"):
                        if key in msg and isinstance(msg[key], str):
                            return msg[key]
                elif isinstance(msg, str):
                    return msg
        except (json.JSONDecodeError, TypeError):
            continue
    return ""
