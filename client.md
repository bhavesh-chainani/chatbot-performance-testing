# Chatbot performance testing — what we do and how we run it

This note explains how we test your chatbot’s performance, what “more users” means in our setup, and how to read common results (including failures). You do not need our codebase or technical access to understand this document.

---

## Purpose

We measure how the chatbot behaves when **many people use it at the same time**: how long it takes to return a **full** answer, and whether requests **complete successfully** under sustained or rising load. This helps you see baseline performance, stress behavior, and where the system may start to degrade.

---

## What we simulate

We use an industry-standard load testing tool called **Locust**. It creates **virtual users**: automated sessions that follow the same path a real user would take through your product’s APIs (not a synthetic “ping” that skips the real chat flow).

For each virtual user, the test typically:

1. **Authenticates** using the same kind of session a browser would use after a normal login (so we are hitting the real authenticated experience).
2. **Confirms the account** with a standard “current user” check.
3. **Opens a chat** by creating or reusing a chat ticket, matching how the live application scopes a conversation.
4. **Sends a realistic question** from a prepared list we maintain (a mix of straightforward trade questions and broader, more complex ones).
5. **Receives the answer over the live streaming channel** the product uses (the server streams the reply in chunks until it is finished).
6. **Records timing** from the moment the message is sent until the **full** streamed response has been received.

We then aggregate results into reports: response times, success vs failure counts, and per-request detail suitable for review with engineering.

**In plain terms:** we are not guessing from the outside; we are driving the **same chat experience your users get**, at scale, and measuring speed and reliability.

---

## How we add “more users”

When we say we run with a certain number of users, we mean **concurrent virtual users** managed by Locust—not necessarily that many separate human operators or that many distinct accounts unless we explicitly agree to test that way.

- **Ramp-up:** We start low and increase concurrency at a controlled rate (for example, “add N new users per second”) so the system is not shocked by an instant spike unless a specific scenario calls for that.
- **Sustained load:** Once we reach the target concurrency, we keep that level for a defined duration so we can see steady-state behavior (queues, memory, timeouts, error rates).
- **Larger runs:** For high concurrency, we may run Locust across **multiple machines** (one controller plus additional workers) so the **testing infrastructure** itself does not become the bottleneck. You still set the target user count from the controller; workers share the load of simulating those users.

If you need a one-line explanation for stakeholders: **“We simulate many logged-in users chatting at once, using the real APIs and streaming responses, and we record how long full answers take and how often they fail.”**

---

## What we measure (primary outcomes)

- **End-to-end response time:** Time from sending a chat message until the **complete** streamed answer has been received. This reflects what a user perceives as “how long until I have the full reply,” not just time to first token.
- **Success vs failure:** Whether each chat completed normally or ended in an error / incomplete response.
- **Optional breakdowns:** We can categorize questions (for example, simpler vs more complex) to see whether latency or failures cluster in one type of workload.

---

## Test types (how runs differ)

We align runs to named profiles so results are comparable over time—for example:

- **Load:** roughly expected concurrent usage for a defined period.
- **Stress:** above-normal concurrency to see how the system behaves past typical peaks.
- **Endurance:** sustained load over a longer window to surface issues that appear only after the system runs hot for a while.
- **Breakpoint / ramp:** stepping concurrency up toward a ceiling to find where latency or errors rise sharply.

Exact user counts, duration, and ramp rules are agreed per engagement and recorded with each run so reports stay traceable.

---

## How to interpret a common failure: “stream ended prematurely”

You may see failures labeled in a way that suggests the **response stream ended before the client finished reading a complete answer**.

**What that means in user terms:** the connection for the chat reply **closed early**. The user would experience a **cut-off or missing answer**, not a slightly slow but complete reply.

**Why it often shows up under load:** the server, application, or front door (load balancer, proxy, firewall) may close idle or long-lived connections, enforce timeouts, shed load when overloaded, or hit stability limits. Network issues between the test environment and your hosting can also cause this, but **repeated** occurrences under higher concurrency usually point to **capacity, timeout, or proxy configuration** worth reviewing with your engineering team alongside server logs for the same timestamps.

**What we are *not* claiming:** this message alone does not prove a single root cause; it is a **symptom** that the streaming response did not complete. Engineering uses it together with your **infrastructure and application logs**, gateway timeouts, and LLM provider metrics to pinpoint the fix.

---

## Assumptions and limits (important for a fair read of results)

- **Authentication:** Tests use valid sessions; if a session expires mid-run, failures may cluster on auth or chat until the session is refreshed. We monitor for that.
- **Content and cost:** Heavy concurrency generates real traffic and token usage; we scope duration and concurrency with you so costs and rate limits are understood up front.
- **Environment:** Results apply to the **environment we tested** (for example staging vs production). Different environments should not be compared line-for-line without noting that difference.
- **“Users” vs “accounts”:** Unless specified, high concurrency means **many parallel sessions from the load tool**, not necessarily many unique business accounts.

---

## What we deliver after a run

- A **summary** of concurrency, duration, and ramp strategy used.
- **Response time statistics** (typical ranges and tail latencies, depending on what we configure in the report).
- **Failure counts and categories** (including incomplete streams where applicable).
- **Optional detailed tables** of questions, outcomes, and timings for engineering follow-up.

---

## Closing line you can use in email

“We run controlled, repeatable load tests that simulate real logged-in users sending questions and receiving full streamed answers over the same APIs the product uses. We ramp concurrency using Locust (and multiple worker machines when needed), measure end-to-end time to a complete response, and flag failures like incomplete streams so your team can correlate them with server, proxy, and provider logs.”

If you want this document tailored to a specific run, we can add a short appendix with **exact date, environment URL, user count, duration, and ramp** for that test only.
