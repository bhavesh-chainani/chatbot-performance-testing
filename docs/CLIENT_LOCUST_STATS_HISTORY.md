# Locust stats history CSV (`*_stats_history.csv`)

This document describes the file produced when Locust runs with **`--csv PREFIX`** (replace `PREFIX` with your chosen base path, e.g. `reports/client_run`). Example output file: **`reports/client_run_stats_history.csv`**. The same column layout is used for any prefix.

Official reference: [Retrieve test statistics in CSV format](https://docs.locust.io/en/stable/retrieving-stats.html) (Locust documentation).

---

## What this file is

- A **time series**: Locust appends **one row per sampling interval** while the test runs (default interval is on the order of **one second**; exact timing depends on Locust version and settings).
- Each row is a **snapshot** of statistics **at that moment** in the test.
- Rows with **`Name` = `Aggregated`** combine **all HTTP requests** Locust is tracking (for example: authentication, ticket creation, chat stream calls), unless you enabled options that also emit separate rows per endpoint.

**Important:** These metrics are **Locust HTTP-level** measurements (what the load generator records for each named request). They are **not** the same as a separate application log of “chat answer text length,” unless your test is defined that way.

---

## Column reference

### Time and load

| Column | Meaning |
|--------|--------|
| **Timestamp** | Unix time (seconds) when Locust wrote this snapshot row. |
| **User Count** | Number of **simulated users** Locust had running at that moment (may be **0** on the very first interval before users finish spawning). |
| **Type** | Often **empty** on **`Aggregated`** rows. When present on other rows, it can indicate request type (for example HTTP method) depending on Locust version and export options. |
| **Name** | Locust’s **request label**. **`Aggregated`** means “all requests combined” in that row. |
| **Requests/s** | Locust’s estimate of **current throughput** (requests per second) over its **short internal window** for that snapshot—not the same as “total requests ÷ entire test duration” on every row. |
| **Failures/s** | Same idea as **Requests/s**, but for **failed** requests in Locust’s window. |

### Response time percentiles (`50%` … `100%`)

| Column | Meaning |
|--------|--------|
| **50%, 66%, 75%, 80%, 90%, 95%, 98%, 99%, 99.9%, 99.99%, 100%** | **Response time percentiles in milliseconds** for the requests included in this row’s scope (for **`Aggregated`**, across **all** request types Locust is aggregating). |

**How to read them:**  
If **50%** = 32 ms, then about half of the (relevant) response times recorded up to that snapshot were **≤ 32 ms**. **100%** is the **slowest** response time in the distribution Locust is using for that statistic at that moment.

**`N/A`:** Locust may write **`N/A`** when there is **not enough data yet** (for example before the first requests complete).

### Cumulative counters and “Total *” response fields

These columns describe **cumulative** information for the **`Aggregated`** view **since the start of the test run** (as Locust maintains it—not a rolling window).

| Column | Meaning |
|--------|--------|
| **Total Request Count** | Total number of **completed** requests Locust has counted so far (**success + failure**), for the scope of that row (for **`Aggregated`**, **all** tracked requests). |
| **Total Failure Count** | Total number of **failed** requests so far (Locust’s definition of failure: HTTP/error events Locust marks as failed). |

The following four columns summarize **response time** over the **same** set of requests Locust uses for the aggregate **at that snapshot**. All values are in **milliseconds (ms)**.

| Column | Meaning |
|--------|--------|
| **Total Median Response Time** | **Median (50th percentile)** of response times for the **cumulative** set of requests included in the aggregate. Half of those requests were faster than or equal to this value; half were slower. |
| **Total Average Response Time** | **Arithmetic mean** of response times for that cumulative set: sum of all response times ÷ number of requests. More sensitive to **slow outliers** than the median. |
| **Total Min Response Time** | **Fastest** response time observed so far among those requests (**smallest** latency). |
| **Total Max Response Time** | **Slowest** response time observed so far among those requests (**largest** latency). |

**Practical interpretation for clients**

- **Median** = typical experience under load; **average** = overall mean (can be pulled up by a few very slow calls).  
- **Min / Max** = best and worst case **so far**, not a guarantee for all future requests.  
- Because **`Aggregated`** mixes **all** named operations (for example a fast **auth** check and a **long chat stream**), the **median and average are dominated by the mix of operations**, not by “chat only,” unless the test exports separate rows per name.

| Column | Meaning |
|--------|--------|
| **Total Average Content Size** | Average **HTTP response body size in bytes** for the aggregate (as Locust measures it). For **streaming** or chunked responses, this may not match “size of the final chat text” in a simple way. |

---

## How this file differs from other exports

| Artifact | Contents |
|----------|-----------|
| **`*_stats_history.csv`** (this file) | **Time series** of aggregate (and optionally per-endpoint) HTTP stats **during** the run. |
| **`*_stats.csv`** | **Final** summary table at **end** of the run (one row per request name + aggregated). |
| **`response_times_*.csv`** (this project) | **Per chat** log from the custom test script (questions, answers, end-to-end time, TTFF). **Not** generated by Locust’s `--csv` flag. |

---

## Version note

Exact behavior (sampling interval, sliding window length for **Requests/s**, and rounding) can vary slightly with **Locust version**. For the authoritative behavior of your installed version, see the Locust documentation version that matches `python -m locust --version`.
