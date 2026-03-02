#!/usr/bin/env python3
"""
Generate an HTML report from Locust CSV results.

Each report shows:
  - Summary statistics (min / avg / median / p95 / p99 / max response times)
  - Per-category breakdown (Direct vs Indirect)
  - Full table of every request: question asked, answer received, e2e response time

Usage:
  python src/generate_report.py                       # all CSV files in reports/
  python src/generate_report.py reports/response_times_load.csv
"""

import csv
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.test_config import REPORTS_DIR

_ERROR_ANSWERS = [
    "TAIA has encountered a connection error, please click message button on the right and we will contact you.",
    "TAIA has encountered an error, please try again later. If you continue to experience this problem, please reach out to our support team via the message button for assistance. We appreciate your patience and apologize for any inconvenience.",
    "I am unable to retrieve sufficient information at this time. For further guidance, please click the 'Email' button in the bottom right corner of the screen to arrange a call or a one-to-one advisory session. Our specialists can provide tailored insights based on your product and trade needs and help address any related queries or challenges.",
]

_ERROR_LABELS = {
    _ERROR_ANSWERS[0]: "Connection Error",
    _ERROR_ANSWERS[1]: "System Error",
    _ERROR_ANSWERS[2]: "Insufficient Information",
}


def classify_error(answer: str) -> str:
    """Return error label if the answer is blank or matches a known error, else empty string."""
    if not answer or not answer.strip():
        return "Empty Response"
    stripped = answer.strip()
    for msg, label in _ERROR_LABELS.items():
        if stripped == msg:
            return label
    return ""


def load_run_meta(csv_path: Path, test_type: str) -> dict:
    """Load run metadata (users, spawn_rate, host, run_time) if present."""
    meta_path = csv_path.parent / f"run_meta_{test_type}.json"
    if not meta_path.exists():
        return {}
    try:
        with open(meta_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def load_csv(csv_path: Path) -> list[dict]:
    rows = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["response_time_ms"] = float(row["response_time_ms"])
            except (ValueError, KeyError):
                row["response_time_ms"] = 0.0
            rows.append(row)
    return rows


def compute_stats(times: list[float]) -> dict:
    if not times:
        return {k: 0 for k in ("count", "min", "avg", "median", "p95", "p99", "max")}
    s = sorted(times)
    n = len(s)
    return {
        "count": n,
        "min": round(s[0], 1),
        "avg": round(statistics.mean(s), 1),
        "median": round(statistics.median(s), 1),
        "p95": round(s[int(n * 0.95)] if n > 1 else s[0], 1),
        "p99": round(s[int(n * 0.99)] if n > 1 else s[0], 1),
        "max": round(s[-1], 1),
    }


def _esc(text: str) -> str:
    """HTML-escape a string."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def generate_html(
    rows: list[dict],
    test_type: str,
    exclude_empty_answers: bool = False,
    run_meta: dict = None,
) -> str:
    run_meta = run_meta or {}
    if exclude_empty_answers:
        rows = [r for r in rows if r.get("answer", "").strip()]
    success_rows = [r for r in rows if r.get("status") == "Success"]
    error_rows = [r for r in rows if r.get("status") != "Success"]
    all_times = [r["response_time_ms"] for r in success_rows]

    overall = compute_stats(all_times)

    for r in rows:
        r["error_type"] = classify_error(r.get("answer", ""))
    content_errors = [r for r in rows if r["error_type"]]
    total_requests = len(rows)
    failed_requests = len(content_errors)
    successful_requests = total_requests - failed_requests
    error_rate = round((failed_requests / total_requests * 100), 1) if total_requests > 0 else 0.0
    error_rate_color = "var(--red)" if error_rate > 5 else "var(--yellow)" if error_rate > 0 else "var(--green)"
    error_breakdown = {}
    for r in content_errors:
        et = r["error_type"]
        error_breakdown[et] = error_breakdown.get(et, 0) + 1

    categories = sorted(set(r.get("question_category", "Unknown") for r in success_rows))
    cat_stats = {}
    for cat in categories:
        cat_times = [r["response_time_ms"] for r in success_rows if r.get("question_category") == cat]
        cat_stats[cat] = compute_stats(cat_times)

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Test run parameters (if available)
    params_html = ""
    if run_meta:
        params_html = """
<h2>Test Parameters</h2>
<table class="params-table">
<tbody>
  <tr><td>Number of users (peak concurrency)</td><td>{users}</td></tr>
  <tr><td>Spawn rate (users started/second)</td><td>{spawn_rate}</td></tr>
  <tr><td>Host</td><td>{host}</td></tr>
  <tr><td>Run time</td><td>{run_time}</td></tr>
</tbody>
</table>
""".format(
            users=run_meta.get("users", "—"),
            spawn_rate=run_meta.get("spawn_rate", "—"),
            host=_esc(str(run_meta.get("host", "—"))),
            run_time=run_meta.get("run_time", "—"),
        )

    cat_rows_html = ""
    for cat in categories:
        s = cat_stats[cat]
        cat_rows_html += f"""
            <tr>
                <td>{_esc(cat)}</td>
                <td>{s['count']}</td>
                <td>{s['min']}</td>
                <td>{s['avg']}</td>
                <td>{s['median']}</td>
                <td>{s['p95']}</td>
                <td>{s['p99']}</td>
                <td>{s['max']}</td>
            </tr>"""

    error_breakdown_rows = ""
    for etype in sorted(error_breakdown):
        count = error_breakdown[etype]
        pct = round(count / total_requests * 100, 1) if total_requests > 0 else 0.0
        error_breakdown_rows += f"""
            <tr>
                <td>{_esc(etype)}</td>
                <td>{count}</td>
                <td>{pct}%</td>
            </tr>"""

    error_table_html = ""
    if error_breakdown_rows:
        error_table_html = f"""
<table>
<thead><tr>
  <th>Error Type</th><th>Count</th><th>% of Total</th>
</tr></thead>
<tbody>{error_breakdown_rows}
</tbody>
</table>"""

    detail_rows_html = ""
    for r in rows:
        rt = r["response_time_ms"]
        status = r.get("status", "")
        error_type = r.get("error_type", "")
        is_ok = status == "Success" and not error_type
        status_cls = "success" if is_ok else "error"
        rt_cls = ""
        if is_ok:
            if rt > 10000:
                rt_cls = "rt-slow"
            elif rt > 5000:
                rt_cls = "rt-warn"
            else:
                rt_cls = "rt-ok"

        answer_preview = _esc(r.get("answer", ""))[:300]
        error_type_cell = f'<span class="error">{_esc(error_type)}</span>' if error_type else '—'

        detail_rows_html += f"""
            <tr>
                <td class="ts">{_esc(r.get('timestamp', '')[:19])}</td>
                <td>{_esc(r.get('question_category', ''))}</td>
                <td class="question">{_esc(r.get('question', ''))}</td>
                <td class="answer">{answer_preview}</td>
                <td class="{rt_cls}">{round(rt, 1)}</td>
                <td class="{status_cls}">{_esc(status)}</td>
                <td>{error_type_cell}</td>
            </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chatbot Performance Report – {_esc(test_type.upper())}</title>
<style>
  :root {{
    --bg: #0f172a; --surface: #1e293b; --border: #334155;
    --text: #e2e8f0; --muted: #94a3b8; --accent: #38bdf8;
    --green: #4ade80; --yellow: #fbbf24; --red: #f87171;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.6;
    padding: 2rem; max-width: 1400px; margin: 0 auto;
  }}
  h1 {{ color: var(--accent); font-size: 1.8rem; margin-bottom: .25rem; }}
  .subtitle {{ color: var(--muted); font-size: .9rem; margin-bottom: 2rem; }}

  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 1.2rem; text-align: center;
  }}
  .card .value {{ font-size: 2rem; font-weight: 700; color: var(--accent); }}
  .card .label {{ font-size: .8rem; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; }}

  h2 {{ font-size: 1.2rem; margin: 2rem 0 1rem; color: var(--accent); }}

  table {{
    width: 100%; border-collapse: collapse; font-size: .85rem;
    background: var(--surface); border-radius: 8px; overflow: hidden;
  }}
  th {{
    background: #0f172a; color: var(--muted); text-transform: uppercase;
    font-size: .75rem; letter-spacing: .05em; padding: .75rem 1rem; text-align: left;
  }}
  td {{ padding: .6rem 1rem; border-top: 1px solid var(--border); }}
  tr:hover td {{ background: rgba(56, 189, 248, 0.04); }}

  .question {{ max-width: 320px; word-break: break-word; }}
  .answer {{ max-width: 380px; word-break: break-word; color: var(--muted); font-size: .8rem; }}
  .ts {{ white-space: nowrap; color: var(--muted); font-size: .8rem; }}

  .success {{ color: var(--green); font-weight: 600; }}
  .error   {{ color: var(--red); font-weight: 600; }}
  .rt-ok   {{ color: var(--green); font-weight: 600; }}
  .rt-warn {{ color: var(--yellow); font-weight: 600; }}
  .rt-slow {{ color: var(--red); font-weight: 600; }}

  .footer {{ margin-top: 3rem; text-align: center; color: var(--muted); font-size: .8rem; }}

  .params-table {{ max-width: 480px; margin-bottom: 2rem; }}
  .params-table td:first-child {{ color: var(--muted); font-size: .85rem; }}
  .params-table td:last-child {{ font-weight: 600; }}
</style>
</head>
<body>

<h1>Chatbot Performance Report — {_esc(test_type.upper())} Test</h1>
<p class="subtitle">Generated {generated_at} &middot; {len(rows)} total requests &middot; {len(error_rows)} errors</p>
{params_html}

<div class="cards">
  <div class="card"><div class="value">{overall['count']}</div><div class="label">Successful Requests</div></div>
  <div class="card"><div class="value">{overall['avg']} ms</div><div class="label">Avg Response Time</div></div>
  <div class="card"><div class="value">{overall['median']} ms</div><div class="label">Median (p50)</div></div>
  <div class="card"><div class="value">{overall['p95']} ms</div><div class="label">p95 Response Time</div></div>
  <div class="card"><div class="value">{overall['p99']} ms</div><div class="label">p99 Response Time</div></div>
  <div class="card"><div class="value">{overall['max']} ms</div><div class="label">Max Response Time</div></div>
</div>

<h2>Response Time by Category</h2>
<table>
<thead><tr>
  <th>Category</th><th>Count</th><th>Min (ms)</th><th>Avg (ms)</th>
  <th>Median (ms)</th><th>p95 (ms)</th><th>p99 (ms)</th><th>Max (ms)</th>
</tr></thead>
<tbody>{cat_rows_html}
</tbody>
</table>

<h2>Error Metrics</h2>
<div class="cards">
  <div class="card"><div class="value">{total_requests}</div><div class="label">Total Requests</div></div>
  <div class="card"><div class="value" style="color: var(--green)">{successful_requests}</div><div class="label">Successful</div></div>
  <div class="card"><div class="value" style="color: var(--red)">{failed_requests}</div><div class="label">Failed</div></div>
  <div class="card"><div class="value" style="color: {error_rate_color}">{error_rate}%</div><div class="label">Error Rate</div></div>
</div>
{error_table_html}

<h2>Request Details</h2>
<table>
<thead><tr>
  <th>Time</th><th>Category</th><th>Question</th><th>Answer</th>
  <th>Response Time (ms)</th><th>Status</th><th>Error Type</th>
</tr></thead>
<tbody>{detail_rows_html}
</tbody>
</table>

<div class="footer">Chatbot Performance Testing &middot; {_esc(test_type)} test</div>
</body>
</html>"""


def main():
    reports_dir = Path(REPORTS_DIR)

    exclude_empty = "--exclude-empty" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--exclude-empty"]

    if args:
        csv_files = [Path(a) for a in args]
    else:
        csv_files = sorted(reports_dir.glob("response_times_*.csv"))

    if not csv_files:
        print(f"No CSV files found in {reports_dir}/")
        print("Run a test first:  TEST_TYPE=load locust -f src/locustfile.py")
        sys.exit(1)

    for csv_path in csv_files:
        if not csv_path.exists():
            print(f"File not found: {csv_path}")
            continue

        rows = load_csv(csv_path)
        if not rows:
            print(f"No data in {csv_path}")
            continue

        test_type = rows[0].get("test_type", csv_path.stem.replace("response_times_", ""))
        run_meta = load_run_meta(csv_path, test_type)
        html = generate_html(rows, test_type, exclude_empty_answers=exclude_empty, run_meta=run_meta)

        out_path = csv_path.with_name(f"report_{test_type}.html")
        out_path.write_text(html)
        print(f"Report generated: {out_path}  ({len(rows)} requests)")


if __name__ == "__main__":
    main()
