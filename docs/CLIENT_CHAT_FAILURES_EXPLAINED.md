# How chat failures are detected in load tests

This document explains, in plain language:

- How the load test decides a chat **failed**
- What the Locust error messages mean
- **Where to find the full question and full response** after a run
- How that relates to **browser DevTools** (and what it does *not* read from the frontend)
- How to respond when a developer says **“the chatbot works as expected”**

Written for business stakeholders, QA, and engineering leads reviewing results such as:


| Count | Method | Request name    | Error message                                                          |
| ----- | ------ | --------------- | ---------------------------------------------------------------------- |
| 21    | POST   | Chat [Direct]   | `CatchResponseError('Stream read failed: Response ended prematurely')` |
| 2     | POST   | Chat [Indirect] | `CatchResponseError('Content error: Empty Response')`                  |
| 73    | POST   | Chat [Indirect] | `CatchResponseError('Stream read failed: Response ended prematurely')` |


---

## Executive summary


| Question                                        | Answer                                                                                                                                                               |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Can we log full questions and responses?**    | **Yes.** Every chat is written to `*_response_times_*.csv` (Excel) and `*_chat_transcripts_*.jsonl` (evidence). Failures include the **raw API stream** (`raw_sse`). |
| **Does the test read the chat page HTML?**      | **No.** It reads `POST /api/chat/stream` — the same streamed `data:` lines as DevTools → **Network → stream → Response**.                                            |
| **Why HTTP 200 but still a failure?**           | 200 only means the connection started OK. We also require a **complete stream** and a **final answer** in the events.                                                |
| **Why “works for dev” but fails in load test?** | Manual tests are usually **one user, low load**. The test runs **many concurrent** streams; timeouts and cut-offs show up under pressure.                            |


**After each run, use this workflow:**

1. `*_failures.csv` → how many of each error type
2. `*_response_times_*.csv` → filter failures → see **full question + answer**
3. `*_chat_transcripts_*.jsonl` → same failed chats → copy `**raw_sse`** as proof for engineering

> **Note:** Runs completed *before* the full-logging update may have truncated questions (200 chars) and answers (500 chars) in CSV only. Re-run the test to get full CSV rows and the JSONL transcript file.

---

## Contents

1. [What the test is doing](#1-what-the-test-is-doing-big-picture)
2. [DevTools / Inspect Element mapping](#2-where-this-appears-in-browser-devtools-inspect-element) — includes [Network tab checklist](#devtools-checklist-success-vs-failure-in-the-network-tab)
3. [Chat Direct vs Indirect](#3-what-chat-direct-and-chat-indirect-mean)
4. [Success vs failure rules](#4-what-counts-as-success-vs-failure)
5. [Failure type A: Stream read failed](#5-failure-type-a-stream-read-failed-response-ended-prematurely)
6. [Failure type B: Empty Response](#6-failure-type-b-content-error-empty-response)
7. [Other content errors](#7-other-content-errors-same-family-as-empty-response)
8. [How errors reach Locust reports](#8-how-the-error-text-reaches-the-locust-failures-table)
9. [Full Q&A logging after every run](#9-full-question--response-logging-after-every-test-run)
10. [API stream vs frontend elements](#10-api-stream-vs-frontend-elements-critical-for-developer-discussions)
11. [All report files](#11-relating-failures-to-all-report-files)
12. [Example: 100-user run](#12-reading-your-100-user-example)
13. [What is not a failure](#13-what-this-test-does-not-flag-as-failure)
14. [Talking points for client / dev meetings](#14-talking-points-for-client--dev-meetings)
15. [Glossary](#15-quick-glossary)
16. [For engineers: code references](#16-for-engineers-where-this-lives-in-code)

---

## 1. What the test is doing (big picture)

Think of the load test as **many virtual users** using the chatbot at the same time.

Each virtual user:

1. Logs in using the same kind of **session cookie** a real browser gets after you sign in.
2. Opens or reuses a **chat ticket** (the conversation thread).
3. Sends a **sample trade question** to the chatbot.
4. Waits for the **full streamed reply** — the same kind of live response you see in the website UI.
5. Decides whether that reply counts as **success** or **failure**.

The test does **not** click buttons in Chrome. It calls the **same backend API** the website uses when you type a message and press Send.


| Item         | Value                                                                                        |
| ------------ | -------------------------------------------------------------------------------------------- |
| **URL**      | `POST /api/chat/stream?ticket_id=<id>`                                                       |
| **Body**     | `{"message_content": "<your question>"}`                                                     |
| **Response** | A **stream** of server-sent events (SSE) — many `data: {...}` lines, not one plain JSON blob |


When we say “the test read the response,” we mean it read the **same network stream** you would see in browser DevTools for that chat request.

---

## 2. Where this appears in browser DevTools (Inspect Element)

### What the test uses vs does not use


| DevTools area                                   | Used by load test?                          |
| ----------------------------------------------- | ------------------------------------------- |
| **Network → `stream` → Response / EventStream** | **Yes** — primary source of truth           |
| **Network → Status, Headers**                   | **Yes** — HTTP code, `text/event-stream`    |
| **Elements** (HTML, chat bubbles, spinners)     | **No**                                      |
| **Console** (JS errors)                         | **No**                                      |
| **Application → Cookies**                       | Only to copy `session` into `.env` for auth |


### Step-by-step in Chrome

1. Log into the chatbot site (e.g. cfoti.org).
2. Open **DevTools** (F12 or right-click → Inspect).
3. Go to the **Network** tab.
4. Send a chat message in the UI.
5. Find the request named `**stream`** (path: `/api/chat/stream`).

### What to look at on that request


| DevTools area                  | What it shows                            | How the load test uses it                                 |
| ------------------------------ | ---------------------------------------- | --------------------------------------------------------- |
| **Headers → Request URL**      | `.../api/chat/stream?ticket_id=...`      | Same endpoint and ticket pattern                          |
| **Headers → Request Method**   | `POST`                                   | Same method (shown as `POST` in failures)                 |
| **Headers → Response headers** | Often `content-type: text/event-stream`  | Confirms streaming chat response                          |
| **Response / EventStream**     | Many lines starting with `data: { ... }` | Test reads **every line** until the stream ends or breaks |
| **Status**                     | Usually `200`                            | HTTP OK — but **200 alone is not enough**                 |


### Example stream

```text
data: {"type": "ticket_id", "data": "..."}
data: {"type": "streaming_event", "data": {"payload": {"step_type": "...", "status": "...", "output": "..."}}}
data: {"type": "streaming_event", "data": {"payload": {"step_type": "reasoning", "status": "success", "output": "Thank you for your enquiry..."}}}
```

The load test:

- Reads **all** of these lines (equivalent to watching the Response tab fill up).
- Parses them to find the **final chatbot answer text**.
- Marks **failed** if the stream breaks early **or** no valid final answer can be extracted.

**Important:** Failures are **not** taken from the HTML of the chat page. They come from **Network → stream → `data:` lines** and whether that stream completed cleanly.

### DevTools checklist: success vs failure in the Network tab

`**ChunkedEncodingError` and `Response ended prematurely` are not labels in DevTools.** Those names come from Python’s HTTP client when the response body ends before the chunked stream finishes. In Chrome, the same underlying problem shows up on the `**stream`** request in the **Network** tab — mainly in **Response**, **Status**, and sometimes **Console**.

Open `**POST /api/chat/stream?ticket_id=...`** → use **Headers**, **Response** (or **EventStream**), and **Timing**.

#### Side-by-side: what the Network tab shows


| Scenario                                                                   | Network **Status** column                       | **Response** tab                                                                                                                     | Request row / Console                                                                       | Load test result                                          |
| -------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| **Full success**                                                           | `200`                                           | Stream ends normally; last useful event has `"status": "success"` and a full `"output": "..."`                                       | Normal finished row                                                                         | `Success`                                                 |
| **Stream cut off** (`ChunkedEncodingError` / “Response ended prematurely”) | Often still `**200`**, sometimes `**(failed)**` | **Stops mid-stream** — partial `data:` lines, may cut off mid-JSON; **no final success `output`**                                    | Row may be **red** with `(failed)`; Console may show `net::ERR_INCOMPLETE_CHUNKED_ENCODING` | `Stream read failed: Response ended prematurely`          |
| **Empty response** (stream finished, no answer)                            | `200`                                           | Stream **looks complete** (connection closed cleanly), but only progress/metadata events — **no** `"status": "success"` + `"output"` | Normal finished row — **hard to spot without reading JSON**                                 | `Content error: Empty Response`                           |
| **Known error text** (connection / system / insufficient info)             | `200`                                           | Stream **complete**; final `"output"` is one of the fixed TAIA error strings                                                         | Normal finished row                                                                         | `Content error: Connection Error` / `System Error` / etc. |
| **Auth failure**                                                           | `**401`**                                       | Little or no SSE body                                                                                                                | Clear non-200 status                                                                        | `401 Unauthorized`                                        |
| **Other HTTP error**                                                       | `4xx` / `5xx`                                   | Error body, not a normal chat stream                                                                                                 | Clear non-200 status                                                                        | `Error <code>`                                            |


#### The two cases people confuse most

**1. Stream cut off (becomes “Stream read failed” in the test)**

In DevTools, the Response tab may look like:

```text
data: {"type": "ticket_id", "data": "..."}
data: {"type": "streaming_event", "data": {"payload": {"step_type": "reasoning", "status": "in_progress", ...}}}
data: {"type": "streaming_event", "data": {"payload": {"step_type": "reasoning", "status": "in_progress", ...
```

…and then **nothing more**. The stream **stops growing** and never reaches a final success line.

Signals at the network level:

- Response body is **truncated** (ends abruptly).
- Chrome may mark the row `**(failed)`** even when Status was 200.
- **Console** may show `net::ERR_INCOMPLETE_CHUNKED_ENCODING`.
- **Timing → Content Download** may end early compared to a good chat.

In the UI you may see a stuck spinner, partial text, or no final bubble — the frontend depends on the same stream.

**2. Full completed response (success)**

Status `**200`**. Response runs through the full sequence and ends with something like:

```text
data: {"type": "streaming_event", "data": {"payload": {"step_type": "reasoning", "status": "success", "output": "Thank you for your enquiry. For exporting ..."}}}
```

Signals it completed cleanly:

- Request **finishes** (not stuck pending forever).
- Last `streaming_event` has `**"status": "success"`** and a non-empty `**"output"**`.
- No `(failed)` row and no `ERR_INCOMPLETE_CHUNKED_ENCODING` in Console.

#### HTTP 200 alone is not success

You must read the **Response** body, not only the status code:


| What you see in DevTools                         | Network “complete”?   | Load test result              |
| ------------------------------------------------ | --------------------- | ----------------------------- |
| 200 + truncated Response                         | **No** (stream broke) | **Fail** — stream read failed |
| 200 + full Response but no success `output`      | **Yes**               | **Fail** — empty response     |
| 200 + full Response + error template in `output` | **Yes**               | **Fail** — content error      |
| 200 + full Response + real answer in `output`    | **Yes**               | **Pass**                      |


#### Four-step checklist (Response tab)

On the `**stream`** request → **Response** tab:

1. **Did the stream stop abruptly?** → matches “Stream read failed” in the test.
2. **Did it finish but the last event lacks `"status": "success"` + `"output"`?** → “Empty Response”.
3. **Did it finish but `output` is a TAIA error string?** → “Content error”.
4. **Did it finish with a real answer in `output`?** → success.

For load-test failures, compare JSONL `**raw_sse`** to DevTools **Response** — they should match what arrived before the connection ended.

---

## 3. What “Chat [Direct]” and “Chat [Indirect]” mean

These are **question categories**, not different APIs.


| Label               | Meaning                                                                              |
| ------------------- | ------------------------------------------------------------------------------------ |
| **Chat [Direct]**   | Simpler trade question (single product, route, or concept).                          |
| **Chat [Indirect]** | More complex scenario (multi-country routing, back-to-back PCO, verification, etc.). |


Both use the **same** `POST /api/chat/stream` call. The label only helps you see whether one question type fails more often under load.

In the default test mix, **Indirect** questions appear more often than **Direct**, which is why Indirect stream failures (e.g. 73) can outnumber Direct ones (e.g. 21) even when the root cause is the same.

---

## 4. What counts as success vs failure

A chat is **successful** only when **all** of the following are true:

1. HTTP status is **200 or 201**.
2. The **entire stream** is read without a connection/stream error.
3. The test extracts a **non-empty final answer** from the stream.
4. That answer is **not** a known chatbot **error message** (see [section 7](#7-other-content-errors-same-family-as-empty-response)).

If any check fails, Locust records a **failure** in `*_failures.csv`.

### Decision flow (three checks)

```text
POST /api/chat/stream
        ↓
Read stream line by line
        ↓
┌───────────────────────────────────────┐
│ CHECK 1: Did the stream finish?     │
│   No  → Stream read failed            │
│   Yes → continue                      │
├───────────────────────────────────────┤
│ CHECK 2: HTTP 200/201?                │
│   No  → Status failure (401, etc.)    │
│   Yes → continue                      │
├───────────────────────────────────────┤
│ CHECK 3: Final answer in stream?      │
│   Blank     → Content error: Empty      │
│   Error msg → Content error: System…    │
│   Valid     → Success                   │
└───────────────────────────────────────┘
```

### Why HTTP 200 can still be a failure

The server can return **200 OK** and still:

- Close the stream before the final answer → **Stream read failed**
- Send only progress events, no final `output` → **Empty Response**
- Send a known “sorry, something went wrong” template → **Connection / System / Insufficient Information**

The test asks: **“Did the user get a real, complete answer?”** — not merely “did the server return 200?”

---

## 5. Failure type A: `Stream read failed: Response ended prematurely`

### Plain English

The connection **started** delivering the chat stream but **stopped before the test finished reading it**.

Like a call that drops mid-sentence: you may have heard “Analysing your question…”, but the full answer never arrived.

### What the user may see in the UI

- Spinner that never finishes
- Partial message then nothing more
- Apparent “freeze” while waiting

The frontend depends on the same stream; if it cuts off, the UI may not show a complete bubble even when Status is 200.

### Technical detail

While reading the stream line by line, the test can hit:

- `**ChunkedEncodingError: Response ended prematurely`** (most common in reports)
- Incomplete read / protocol errors
- Connection reset or dropped connection

### Typical causes under load

- Backend or gateway **timeout** on long Indirect answers
- **Connection limits** at 100+ concurrent users
- **Proxy / load balancer** closing long-running streams
- Network issues between load generator and site

### Clues in the detailed logs

In `*_response_times_*.csv` / JSONL:


| Field              | Typical value                                                                   |
| ------------------ | ------------------------------------------------------------------------------- |
| `status`           | `Stream interrupted – chunked stream closed early (server/proxy/load)`          |
| `answer`           | Often blank; may contain **partial** text if some events arrived before cut-off |
| `status_code`      | Often still `200`                                                               |
| `response_time_ms` | Can be very large (e.g. ~300,000 ms ≈ 5 minutes)                                |
| `failure_reason`   | `Stream read failed: Response ended prematurely`                                |


In JSONL, `raw_sse` shows exactly what arrived before the connection died — compare to DevTools Response tab.

### In DevTools

See [DevTools checklist: success vs failure in the Network tab](#devtools-checklist-success-vs-failure-in-the-network-tab) (section 2). In short:

- Status may show **200**
- Response tab shows **partial** `data:` lines
- Stream stops growing; connection closes
- Console may show `net::ERR_INCOMPLETE_CHUNKED_ENCODING`

---

## 6. Failure type B: `Content error: Empty Response`

### Plain English

The HTTP request **completed** and the stream **finished**, but the test could **not find a final chatbot answer** in any `data:` line.

Like the network tab showing a “complete” request while the message bubble never gets real content.

### How “empty” is defined

After the full stream is collected, the parser looks for a **final answer**. It succeeds only if it finds:

- A `streaming_event` where `payload.status` is `"success"` and `payload.output` is a non-empty string, **or**
- A `message` event with text in `message_content`, `content`, `message`, `text`, or `response`.

**Empty Response** means:

```text
final answer text == ""   (blank)
```

That includes:

- No matching event in the stream
- Only metadata (`ticket_id`) or progress steps without final `output`
- JSON shape the parser does not recognise as an answer

It does **not** mean “zero bytes in the HTTP body.” The stream may have many lines; none yielded a usable **final answer string**.

### Example from a real run


| Field              | Value                                         |
| ------------------ | --------------------------------------------- |
| `status_code`      | `200`                                         |
| `answer`           | *(blank)*                                     |
| `ttff_ms`          | ~10,000 ms (first feedback may have appeared) |
| `response_time_ms` | ~65,000 ms                                    |
| `status`           | `Error - Empty Response`                      |
| `failure_reason`   | `Content error: Empty Response`               |


The user may have seen “Analysing your question…”, but the test never received the final `output` it treats as the completed reply.

### In DevTools

See [DevTools checklist](#devtools-checklist-success-vs-failure-in-the-network-tab) — **Empty Response** rows look like a **normal finished `200` request**. The Response tab has data, but you will not find a final line with `"status": "success"` and a non-empty `"output"`.

### Typical causes

- Backend stopped mid-flow but closed the stream cleanly
- Answer in a **new event shape** the parser does not yet recognise
- Internal errors that omit the final `streaming_event` with `status: success`
- Heavy load: answer never lands in the stream the client receives

---

## 7. Other content errors (same family as Empty Response)

The content check also fails if the extracted answer **exactly matches** known chatbot error strings shown to real users:


| If the answer text equals…                                     | Reported as                  |
| -------------------------------------------------------------- | ---------------------------- |
| *(blank or whitespace only)*                                   | **Empty Response**           |
| “TAIA has encountered a connection error…”                     | **Connection Error**         |
| “TAIA has encountered an error, please try again later…”       | **System Error**             |
| “I am unable to retrieve sufficient information at this time…” | **Insufficient Information** |


These are **business-visible failures**: the user sees an error in the chat bubble, not a helpful trade answer. The test does not invent these strings — they are copied from known product error copy.

---

## 8. How the error text reaches the Locust failures table

Locust wraps custom failure reasons in `CatchResponseError('...')`. That is normal Locust formatting.

```text
Virtual user sends question
        ↓
POST /api/chat/stream (stream=True)
        ↓
Read SSE lines (like DevTools Response tab)
        ↓
   ┌────┴────┐
   │         │
Stream     Full stream
breaks     received
   │         │
   │         ├─ HTTP not 200/201 → failure (e.g. 401)
   │         ├─ Parse answer
   │         │     ├─ empty / known error → Content error: ...
   │         │     └─ valid answer → success
   │         │
   └─→ Stream read failed: ...
        ↓
Locust *_failures.csv:
  Method, Name, Error, Occurrences
```


| Column in failures CSV         | Meaning                                     |
| ------------------------------ | ------------------------------------------- |
| **POST**                       | HTTP method of the chat API                 |
| **Chat [Direct] / [Indirect]** | Request name including question category    |
| **CatchResponseError('...')**  | Locust wrapper around our `failure_reason`  |
| **Count**                      | How many chats failed for that exact reason |


---

## 9. Full question + response logging (after every test run)

**Every chat is logged** as the test runs. No extra step at the end — files are complete when the run finishes.

### Output files


| File                                       | Best for               | Contents                                                                          |
| ------------------------------------------ | ---------------------- | --------------------------------------------------------------------------------- |
| `***_response_times_<test_type>.csv`**     | Excel / filtering      | **Full question**, **full extracted answer**, timings, `status`, `failure_reason` |
| `***_chat_transcripts_<test_type>.jsonl`** | Evidence / engineering | Same chats as JSON + `sse_event_summary` + `**raw_sse` on failures**              |


Example paths (headless run with prefix `reports/100_users/client_run`):

```text
reports/100_users/client_run_response_times_load.csv
reports/100_users/client_run_chat_transcripts_load.jsonl
```

### CSV columns


| Column              | Meaning                                                                      |
| ------------------- | ---------------------------------------------------------------------------- |
| `question_category` | Direct or Indirect                                                           |
| `question`          | **Full** question sent to the API                                            |
| `answer`            | **Full** extracted answer (blank if none)                                    |
| `response_time_ms`  | Send → stream end or break                                                   |
| `ttff_ms`           | Time to first user-visible feedback (excludes `ticket_id`)                   |
| `status_code`       | HTTP status (often 200 even when content failed)                             |
| `status`            | Human label: `Success`, `Error - Empty Response`, `Stream interrupted – ...` |
| `failure_reason`    | Locust string (empty on success); matches `*_failures.csv`                   |


### JSONL fields


| Field                   | Meaning                                                                                             |
| ----------------------- | --------------------------------------------------------------------------------------------------- |
| `question`              | Complete question text                                                                              |
| `extracted_answer`      | Final answer parsed from stream                                                                     |
| `failure_reason`        | Exact Locust failure reason                                                                         |
| `locust_marked_failure` | `true` / `false`                                                                                    |
| `sse_event_summary`     | e.g. `["ticket_id", "streaming_event:reasoning:in_progress", ...]`                                  |
| `raw_sse`               | **Failures only (default):** full `data:` lines — compare to DevTools → Network → stream → Response |
| `evidence_note`         | Reminder that data is from the API stream, not HTML                                                 |


### Example JSONL record (failure)

```json
{
  "timestamp": "2026-06-05T15:11:12.218409",
  "concurrent_users": 100,
  "question_category": "Indirect",
  "question": "If our PCO application is rejected by Singapore Customs...",
  "extracted_answer": "",
  "response_time_ms": 301056.84,
  "ttff_ms": 2531.85,
  "status_code": 200,
  "status": "Stream interrupted – chunked stream closed early (server/proxy/load)",
  "failure_reason": "Stream read failed: Response ended prematurely",
  "locust_marked_failure": true,
  "sse_event_summary": ["ticket_id", "streaming_event:reasoning:in_progress"],
  "raw_sse": "data: {...}\ndata: {...}\n..."
}
```

### Optional: log raw stream for successes too

In `.env`:

```env
LOG_ALL_RAW_SSE=true
```

Includes `raw_sse` for **every** chat. Files become **very large** — use only for short debug runs.

### How to review failures after a run

1. Open `***_response_times_*.csv`** → filter `status` ≠ `Success` or `failure_reason` not empty.
2. Open `***_chat_transcripts_*.jsonl**` → find the same `timestamp` + `question`.
3. Share `question`, `failure_reason`, and `raw_sse` with engineering.
4. Ask them to replay the question with DevTools → Network → `stream` and compare Response to `raw_sse`.

You then have **question + answer + raw API proof** for each failed chat.

---

## 10. API stream vs frontend “elements” (critical for developer discussions)

The load test **does not** read chat page HTML. It does **not** inspect DOM elements, CSS classes, or React state.


| What developers often check | What the load test checks                            |
| --------------------------- | ---------------------------------------------------- |
| UI looks fine in browser    | `**/api/chat/stream`** response the UI is built from |
| One manual test at a time   | **Many concurrent** virtual users                    |
| “I got an answer”           | Stream delivered a **complete final answer**         |
| Spinner / toast on screen   | Stream finished with `output` and `status: success`  |


### How this maps to the frontend

```text
User types question → frontend POSTs to /api/chat/stream
                              ↓
                    Server sends data: { ... } lines
                              ↓
         ┌────────────────────┴────────────────────┐
         │                                         │
   Frontend JS                           Load test parser
   renders bubbles,                       extracts final output,
   spinners, error text                  marks success/failure
```

The test checks **the contract the frontend depends on**, not pixels on screen.

### When the developer says “it works on my machine”

Both views can be true at once:


| Developer view                 | Load test view                                       |
| ------------------------------ | ---------------------------------------------------- |
| Works for **1 user**, low load | Same API **fails at 100+ concurrent streams**        |
| UI eventually shows something  | Stream **cut off** before final `output`             |
| Server returns **HTTP 200**    | Stream ended with **no parseable final answer**      |
| Different question tested      | Failures tied to **specific questions** in CSV/JSONL |


### How to settle a dispute

Pick one failed row from `*_chat_transcripts_*.jsonl`. Send engineering:

1. Exact `question`
2. `failure_reason`
3. `raw_sse` (or ask them to replay with DevTools at similar load)

If `raw_sse` stops mid-stream or never has `status: success` + `output`, the API did not complete the reply — regardless of whether the UI sometimes hides that.

### Known error messages = real UI copy

**Content error** failures (except stream cuts) match **exact strings** users see in chat — not test-invented errors.

---

## 11. Relating failures to all report files


| File                                               | Audience             | Purpose                                                                                  |
| -------------------------------------------------- | -------------------- | ---------------------------------------------------------------------------------------- |
| `***_failures.csv`** (Locust)                      | Summary              | **Counts** by error type                                                                 |
| `***_stats.csv` / `*_stats_history.csv`** (Locust) | Summary              | HTTP timings, RPS — see [CLIENT_LOCUST_STATS_HISTORY.md](CLIENT_LOCUST_STATS_HISTORY.md) |
| `***_response_times_<test_type>.csv**`             | Excel / QA           | **Per chat:** full Q&A, timings, `failure_reason`                                        |
| `***_chat_transcripts_<test_type>.jsonl`**         | Engineering evidence | Per chat + `raw_sse` on failures                                                         |
| `**run_meta_<test_type>.json**`                    | Context              | Users, spawn rate, host, run time actually used                                          |



| Need                        | Use                          |
| --------------------------- | ---------------------------- |
| Dashboard / counts          | `*_failures.csv`             |
| Spreadsheet analysis        | `*_response_times_*.csv`     |
| Prove what the API returned | `*_chat_transcripts_*.jsonl` |


---

## 12. Reading your 100-user example


| Failure                           | Count | Likely interpretation                                                                   |
| --------------------------------- | ----- | --------------------------------------------------------------------------------------- |
| Stream read failed — **Indirect** | 73    | Complex questions run longer; streams **cut off** under load (timeouts, proxy, limits). |
| Stream read failed — **Direct**   | 21    | Same mechanism; fewer due to shorter flows and lower Direct share in the mix.           |
| Empty Response — **Indirect**     | 2     | Stream **finished** with HTTP 200 but **no final answer** in `data:` events.            |


**Takeaway:** 94 of 96 chat failures are **streams ending early under load**, not “empty HTTP bodies.” The two Empty Response cases are separate: connection completed, answer payload missing.

---

## 13. What this test does *not* flag as failure

- Slow but **complete** answers (`status: Success` with high `response_time_ms`)
- “Analysing your question…” **if** a later event still delivers valid final `output`
- Auth / ticket steps — separate Locust requests (`Verify Auth`, `Create Ticket`, etc.)
- Visual-only UI bugs (layout, CSS) — test does not render the page
- JavaScript console errors — unless they prevent the API from returning a valid stream

---

## 14. Talking points for client / dev meetings

Use this wording when presenting results:

> “The load test does not guess from the UI. It records every question and the **API stream** the website uses — the same data as DevTools Network tab on the `stream` request. For each failure we have the exact question, the failure reason, and the raw response body. Please replay question X from the transcript file with DevTools open; if the stream ends at the same point under similar load, the issue is in the API or infrastructure under concurrency, not in the test methodology.”

**Proof pack for one failure:**

1. Screenshot or export of the CSV row (`question`, `status`, `failure_reason`)
2. JSONL snippet with `raw_sse`
3. Optional: side-by-side with DevTools Response tab from a manual replay

**If they say “our parser might be wrong”:**

- Share `sse_event_summary` — shows which event types arrived
- Ask if production added a new event shape not yet handled in `_parse_sse_response()` in `src/locustfile.py`
- If `raw_sse` clearly contains `status: success` + `output` but we marked Empty Response, that is a **test parser bug** — worth fixing
- If `raw_sse` lacks that event, it is a **product/API bug** under load

---

## 15. Quick glossary


| Term                   | Meaning                                                                     |
| ---------------------- | --------------------------------------------------------------------------- |
| **SSE / event stream** | Server pushes JSON events over one HTTP response; lines start with `data:`. |
| **Stream read failed** | Network stream broke before the test finished reading it.                   |
| **Empty Response**     | Stream completed; no final answer text found in events.                     |
| **TTFF**               | Time to first feedback — first non-metadata `data:` event.                  |
| **Direct / Indirect**  | Question complexity label for reporting.                                    |
| **CatchResponseError** | Locust label for `resp.failure("reason")`.                                  |
| **raw_sse**            | Full API stream text saved in JSONL for failures.                           |
| **extracted_answer**   | Final answer text parsed from `raw_sse`.                                    |


---

## 16. For engineers: where this lives in code


| Behaviour                            | Location in `src/locustfile.py`                              |
| ------------------------------------ | ------------------------------------------------------------ |
| Stream read / **Stream read failed** | `send_chat_message()`, `resp.iter_lines()` exception handler |
| Answer parsing                       | `_parse_sse_response()`                                      |
| Empty + known error templates        | `_classify_error()`                                          |
| Success / failure marking            | `resp.success()` / `resp.failure(...)`                       |
| CSV + JSONL logging                  | `_log()`, `CHAT_TRANSCRIPT_JSONL`                            |
| SSE event summary                    | `_summarize_sse_events()`                                    |
| Log all raw SSE (optional)           | `LOG_ALL_RAW_SSE` in `.env` / `config/test_config.py`        |


If production changes event formats, update `_parse_sse_response()` so “empty” still means “no answer for the user,” not “unrecognised JSON shape.”

---

## Related documents

- [CLIENT_LOCUST_STATS_HISTORY.md](CLIENT_LOCUST_STATS_HISTORY.md) — Locust `*_stats_history.csv` columns (HTTP-level aggregates; separate from per-chat answer quality).
- [README.md](../README.md) — how to run tests and where output files are written.

