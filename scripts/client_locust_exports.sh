#!/usr/bin/env bash
# Same as client_locust_exports.ps1 — run from repo root:
#   chmod +x scripts/client_locust_exports.sh
#   ./scripts/client_locust_exports.sh
#
# Optional env: USERS SPAWN_RATE RUN_TIME PREFIX (default prefix: reports/client_locust_run)

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

USERS="${USERS:-1}"
SPAWN_RATE="${SPAWN_RATE:-1}"
RUN_TIME="${RUN_TIME:-3m}"
PREFIX="${PREFIX:-reports/client_locust_run}"

mkdir -p "$(dirname "$PREFIX")"

EXTRA=()
if [[ "${CSV_FULL_HISTORY:-}" == "1" ]]; then
  EXTRA+=(--csv-full-history)
fi

exec python -m locust -f src/locustfile.py --headless \
  -u "$USERS" -r "$SPAWN_RATE" -t "$RUN_TIME" \
  --csv "$PREFIX" \
  --html "${PREFIX}.html" \
  "${EXTRA[@]}"
