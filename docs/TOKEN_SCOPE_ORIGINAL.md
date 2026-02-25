# Token Scope – Original (Full-Scale)

This document records **total estimated token consumption for the original scope** of the four performance tests (Endurance at 8 hours). Use it for reference when no token budget cap applies.

---

## Test definitions (original scope)

| Test        | Users (approx) | Duration | Notes                    |
|------------|----------------|----------|--------------------------|
| Load       | 500            | 20 min   | Baseline under expected load |
| Stress     | 750            | 20 min   | Beyond normal capacity   |
| Endurance  | 500            | **8 hours** | Sustained load, extended period |
| Breakpoint | ramp to 1000   | 30 min   | Ramp until failure       |

---

## Baseline (request rate)

From `reports/old/report_load.html`:

- **10 concurrent users**, 1 ramp up/s, **3 min** runtime → **27 successful requests**
- **Requests per user-minute:** 27 ÷ (10 × 3) ≈ **0.9** req/(user·min)
- **Total requests** ≈ 0.9 × (concurrent users × duration in minutes)

Tokens per request (assumption, no API metadata): **~500–1,000** (mid **~700**).

---

## Estimated requests (original scope)

| Test        | Users (approx) | Duration | User-minutes   | Est. total requests |
|------------|----------------|----------|----------------|----------------------|
| Load       | 500            | 20 min   | 10,000         | **~9,000**          |
| Stress     | 750            | 20 min   | 15,000         | **~13,500**         |
| Endurance  | 500            | **8 h**  | **240,000**    | **~216,000**        |
| Breakpoint | ~500 (avg ramp)| 30 min   | ~15,000        | **~13,500**         |
| **Total**  |                |          | **280,000**    | **~252,000**        |

---

## Estimated token consumption (original scope)

| Test        | Est. requests | Tokens/request (range) | Est. total tokens (low) | Est. total tokens (mid) | Est. total tokens (high) |
|------------|----------------|-------------------------|--------------------------|--------------------------|---------------------------|
| Load       | ~9,000         | 500 – 1,000             | **~4.5M**                | **~6.3M**                | **~9M**                   |
| Stress     | ~13,500        | 500 – 1,000             | **~6.8M**                | **~9.5M**                | **~13.5M**                |
| Endurance  | **~216,000**   | 500 – 1,000             | **~108M**                | **~151M**                | **~216M**                 |
| Breakpoint | ~13,500        | 500 – 1,000             | **~6.8M**                | **~9.5M**                | **~13.5M**                |
| **Total**  | **~252,000**   |                         | **~126M**                | **~176M**                | **~252M**                 |

**Summary (mid estimate):** **~252,000 requests** → **~176M tokens** total.

---

## Config (original)

- `endurance_test.run_time`: **`"8h"`**
- Override with env: `ENDURANCE_TEST_RUN_TIME=8h`
