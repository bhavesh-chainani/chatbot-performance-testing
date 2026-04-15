# Guide: what `src/locustfile.py` does and how scaling works

This document is for **you** (or anyone on the team with the repo). It explains the Locust script, how load is shaped, and how that ties to `config/test_config.py` / `TEST_TYPE`. It assumes basic familiarity with HTTP APIs.

---

## Role of this file

`src/locustfile.py` is the **Locust test definition**. Locust reads it when you run:

`TEST_TYPE=<load|stress|endurance|breakpoint> locust -f src/locustfile.py`

It defines **one user class** (`ChatbotUser`), optional **load shape** for breakpoint tests, **event hooks** for CSV/metadata, and helpers for **SSE parsing** and **error classification**.

---

## Configuration it depends on

At import time the file loads **`config/test_config.py`**, which:

- Reads **`config/test_config.yaml`** and **`.env`** (via `python-dotenv`).
- Exposes **`TEST_TYPE`**, **`ACTIVE_USERS`**, **`ACTIVE_SPAWN_RATE`**, **`ACTIVE_RUN_TIME`**, breakpoint knobs, **`CHATBOT_URL`**, API path fragments, **`SESSION_COOKIE`**, **`WAIT_TIME_MIN` / `WAIT_TIME_MAX`**, **`CHAT_TIMEOUT_SECONDS`**, **`REPORTS_DIR`**.

So **scaling numbers** (how many users, how fast to add them, how long to run) primarily live in **YAML + env overrides**, not hard-coded in the locustfile. The locustfile **consumes** those values for metadata, logging, and the breakpoint shape.

It also imports **`get_sample_messages`** and **`get_question_category`** from **`src/sample_questions.py`** so each chat uses a weighted pool of questions and a label like **Direct** vs **Indirect** (that label appears in Locust’s chart names as `Chat [Direct]` / `Chat [Indirect]`).

---

## Why `HttpUser` (not `FastHttpUser`)

The class **`ChatbotUser`** subclasses Locust’s **`HttpUser`**, which uses **`requests`**. The chat endpoint is consumed as a **streaming** response (`stream=True`, line-by-line read). The docstring in code notes that **`FastHttpUser`** is avoided **for compatibility with Server-Sent Events (SSE)** streaming.

---

## Virtual user behavior: `ChatbotUser`

### Host and pacing

- **`host`** is set to **`CHATBOT_URL`** so all relative paths resolve against your deployed site.
- **`wait_time = between(WAIT_TIME_MIN, WAIT_TIME_MAX)`** (defaults **2–5 seconds** from config) controls how long Locust waits **between** tasks for that user. That spaces out messages so the load pattern resembles “humans typing and reading,” not a bare-metal flood on every greenlet.

### `on_start` (once per virtual user)

When Locust spawns a new user instance:

1. **Session cookie** — If **`SESSION_COOKIE`** is missing, the user prints an error and does not authenticate.
2. **Cookies set on the client** — `session` and `isLoggedIn=true`, matching browser-style state.
3. **`GET /api/user/me`** (via **`API_ENDPOINT_USERME`**) — **`Verify Auth`**. On **200**, it sets **`is_authenticated`**, mirrors a **`user`** cookie from JSON fields, then continues. On failure, the request is marked failed and ticket setup is skipped.
4. **`_create_ticket()`** — **`POST /api/tickets`** with empty JSON (**`Create Ticket`**). If the response includes **`ticket_id`** or **`id`**, that becomes **`self.ticket_id`**. If not, it falls back to **`GET`** tickets with `offset=0&limit=1&order_by=updated_at:desc` (**`Get Tickets`**) and uses the newest ticket.

So **each Locust user** gets **one ticket context** for its lifetime (unless you extend the code to rotate tickets).

### `@task send_chat_message` (repeated)

Locust picks this task according to its scheduling (with **`wait_time`** between invocations).

1. If not authenticated or no **`ticket_id`**, it skips or retries ticket creation.
2. Picks a **random** message from **`SAMPLE_MESSAGES`** and a **category** for reporting.
3. **`POST`** to **`{API_ENDPOINT_CHAT}?ticket_id={ticket_id}`** with JSON **`{"message_content": message}`**, named **`Chat [{category}]`** in Locust stats.
4. **`stream=True`**, **`timeout=CHAT_TIMEOUT_SECONDS`** (default **240s** from config).
5. **Reads the body line by line** (`iter_lines()`), accumulating all decoded lines.
   - **TTFF (time to first feedback)** — On the first **`data:`** line that **`_is_feedback_event`** treats as user-visible (JSON **`type`** not equal to **`ticket_id`**), it records **`ttff_ms`**. That is meant to reflect when something like “Analysing your question…” appears, not internal metadata.
6. **Connection errors** during the loop are caught, marked as **`Connection lost`**, logged to CSV, and the task returns.
7. After the stream ends:
   - **200/201** — Parses **`_parse_sse_response`** over the full buffered text to find a **final answer string** from known SSE JSON shapes (`streaming_event` with successful `output`, or `message` with common content keys). If the parsed answer is **empty** or **exactly matches** known **TAIA** error strings, the request is **`failure`** with **`Content error: ...`**. Otherwise **`success`**.
   - **401** — Marks auth failed, sets **`is_authenticated = False`**, logs.
   - **Other status** — Failure with status.

**Note:** `LOGIN_EMAIL` / `LOGIN_PASSWORD` are imported from config in this file but **not used** in the current script; **live auth is cookie-based** via **`SESSION_COOKIE`**.

---

## Metrics recorded

| Metric | Meaning |
|--------|--------|
| **End-to-end time** | Wall clock from **start** of **`POST`** until **end** of reading the stream (success path) or until error handling. |
| **TTFF** | Time until first **user-visible** `data:` SSE line (per `_is_feedback_event`). |
| **Locust success/failure** | Drives Locust’s built-in stats; failures include HTTP errors, connection loss, known bad answer text, and empty parsed answers. |

---

## Logging and run metadata

### CSV (`reports/response_times_{TEST_TYPE}.csv`)

On **`test_start`**, the script ensures **`REPORTS_DIR`** exists, sets **`RESPONSE_TIME_CSV`**, and writes a header row if the file is new. Each completed **`send_chat_message`** appends a row via **`_log`** (timestamp, test type, category, truncated question/answer, response time, TTFF, status code, status string).

### `run_meta_{TEST_TYPE}.json`

- **At test start** (master/standalone only, not workers): writes initial **`users`**, **`spawn_rate`**, **`host`**, **`run_time`** using runner/options when available, else YAML-derived **`ACTIVE_*`**.
- **At test stop** (same restriction): overwrites metadata with values that reflect the **actual swarm** when possible.

### **`Runner.start` monkey-patch**

Locust’s **`Runner.start`** is wrapped so **`user_count`** and **`spawn_rate`** from **Start Swarm** in the web UI are stored in **`_swarm_params`**. That works around **`LocalRunner`** not persisting **`spawn_rate`** so **`run_meta`** can still show what you clicked.

---

## How “scaling” and test profiles work

### Default profiles (`TEST_TYPE`)

| `TEST_TYPE` | What Locust uses (from `test_config`) |
|-------------|----------------------------------------|
| **`load`** | Fixed **users**, **spawn_rate**, **run_time** (e.g. 500 / 25 per sec / 20m in YAML). |
| **`stress`** | Higher users / spawn / same idea. |
| **`endurance`** | Same style, longer **run_time** (e.g. 2h). |
| **`breakpoint`** | Uses a **`LoadTestShape`** (see below), not a single flat user cap from the UI in the same way. |

You can override many YAML values with **environment variables** (see comments in `test_config.yaml`, e.g. `LOAD_TEST_USERS`).

### Fixed profiles (load / stress / endurance)

Locust’s **target user count** and **spawn rate** come from:

- **Web UI / CLI** when you start a swarm (preferred for local ad-hoc runs), or
- **Headless** flags if you use them, or
- **Fallback** to **`ACTIVE_USERS`** / **`ACTIVE_SPAWN_RATE`** from config when the runner does not yet have values.

**“Scaling up users”** here means: Locust **starts more concurrent `ChatbotUser` instances** up to the target; each instance runs **`on_start` once**, then loops **`send_chat_message`** with **`wait_time`** gaps. More users ⇒ more overlapping **`POST /api/chat/stream`** calls.

### Breakpoint profile (`TEST_TYPE=breakpoint` only)

If **`TEST_TYPE == "breakpoint"`** at **import time**, the module defines **`BreakpointShape(LoadTestShape)`**. Locust then uses **`tick()`** on a timer to return **`(target_users, spawn_rate)`**:

- Every **`BREAKPOINT_STEP_DURATION`** seconds (default **120s**), the **target** increases by **`BREAKPOINT_RAMP_USERS_PER_STEP`** (default **50**), capped at **`BREAKPOINT_MAX_USERS`** (default **1000**).
- When elapsed test time exceeds **`ACTIVE_RUN_TIME`** parsed from config (e.g. **30m**), **`tick`** returns **`None`** and Locust stops ramping / ends the shape phase per Locust rules.

So **breakpoint scaling is scripted inside the locustfile** as a **step ramp**, unlike load/stress/endurance where you typically set a flat user count (unless you also use other Locust features).

### Distributed runs (master / workers)

The locustfile does **not** configure EC2 or worker count. **Locust itself** splits virtual users across workers when you run **`--master`** / **`--worker`**. The script only avoids writing **`run_meta`** from **workers** (`WorkerRunner`) so only the controller writes authoritative swarm metadata.

---

## Quick mental model

1. **`test_config`** picks **environment**, **timeouts**, **wait between messages**, and **profile** (users/spawn/time or breakpoint ladder).
2. **`ChatbotUser`** = **one concurrent “person”**: cookie auth → ticket → repeated streaming chats with **realistic questions**.
3. **Scaling** = **more `ChatbotUser` instances** (and for breakpoint, **time-based increases** in the shape class). **Distributed mode** = same script on multiple processes/machines sharing the swarm.

---

## Related files

| File | Relation |
|------|----------|
| `config/test_config.py` / `test_config.yaml` | Numbers, URLs, timeouts, profile selection. |
| `src/sample_questions.py` | Question pools and **Direct / Indirect** labels. |
| `src/generate_report.py` | Post-processes CSV into HTML (not part of the locustfile). |
| `AWS_SETUP.md` | How to run Locust on multiple EC2 nodes (infrastructure around this same file). |

If you change **API response shape**, update **`_parse_sse_response`** and possibly **`_is_feedback_event`** so TTFF and “final answer” detection stay correct.
