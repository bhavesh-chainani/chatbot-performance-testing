# Token Scope – 70M Budget (Recommended)

This document records **total estimated token consumption when staying under the client’s 70M token allocation**. Endurance is shortened to 2 hours; Load, Stress, and Breakpoint are unchanged.

---

## Test definitions (70M budget scope)

| Test        | Users (approx) | Duration | Notes                    |
|------------|----------------|----------|--------------------------|
| Load       | 500            | 20 min   | Baseline under expected load |
| Stress     | 750            | 20 min   | Beyond normal capacity   |
| Endurance  | 500            | **2 hours** | Sustained load (shortened to fit 70M) |
| Breakpoint | ramp to 1000   | 30 min   | Ramp until failure       |

---

## Baseline (request rate)

From `reports/old/report_load.html`:

- **10 concurrent users**, 1 ramp up/s, **3 min** runtime → **27 successful requests**
- **Requests per user-minute:** 27 ÷ (10 × 3) ≈ **0.9** req/(user·min)
- **Total requests** ≈ 0.9 × (concurrent users × duration in minutes)

Tokens per request (assumption, no API metadata): **~500–1,000** (mid **~700**).

---

## Estimated requests (70M budget scope)

| Test        | Users (approx) | Duration | User-minutes   | Est. total requests |
|------------|----------------|----------|----------------|----------------------|
| Load       | 500            | 20 min   | 10,000         | **~9,000**          |
| Stress     | 750            | 20 min   | 15,000         | **~13,500**         |
| Endurance  | 500            | **2 h**  | **60,000**     | **~54,000**         |
| Breakpoint | ~500 (avg ramp)| 30 min   | ~15,000        | **~13,500**         |
| **Total**  |                |          | **100,000**    | **~90,000**         |

---

## Estimated token consumption (70M budget scope)

| Test        | Est. requests | Tokens/request (range) | Est. total tokens (low) | Est. total tokens (mid) | Est. total tokens (high) |
|------------|----------------|-------------------------|--------------------------|--------------------------|---------------------------|
| Load       | ~9,000         | 500 – 1,000             | **~4.5M**                | **~6.3M**                | **~9M**                   |
| Stress     | ~13,500        | 500 – 1,000             | **~6.8M**                | **~9.5M**                | **~13.5M**                |
| Endurance  | **~54,000**    | 500 – 1,000             | **~27M**                 | **~38M**                 | **~54M**                  |
| Breakpoint | ~13,500        | 500 – 1,000             | **~6.8M**                | **~9.5M**                | **~13.5M**                |
| **Total**  | **~90,000**    |                         | **~45M**                 | **~63M**                 | **~90M**                  |

**Summary (mid estimate):** **~90,000 requests** → **~63M tokens** total, **under 70M** (≈7M buffer).

---

## Allocation within 70M

| Test        | Est. tokens (mid) | Action / duration      |
|------------|--------------------|-------------------------|
| Load       | ~6.3M              | No change (20 min)      |
| Stress     | ~9.5M              | No change (20 min)      |
| Breakpoint | ~9.5M              | No change (30 min)      |
| **Subtotal** | **~25.3M**        |                         |
| Endurance  | **~38M**           | **Shorten to 2 hours**  |
| **Total**  | **~63M**           | **Under 70M (≈7M buffer)** |

---

## Config (70M budget)

- `endurance_test.run_time`: **`"2h"`** (current default in `config/test_config.yaml`)
- Override with env if needed: `ENDURANCE_TEST_RUN_TIME=2h`
