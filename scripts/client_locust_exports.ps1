# =============================================================================
# Client deliverables (Locust-native only — no custom report generator)
#
# Produces:
#   1) HTML report  →  <prefix>.html          (same class of artifact as UI "Download Report")
#   2) Stats history →  <prefix>_stats_history.csv  (same shape as Breakpoint_stats_history.csv)
#
# Plus Locust also writes: <prefix>_stats.csv, <prefix>_failures.csv, <prefix>_exceptions.csv
#
# Usage (from repo root, after activating your venv / pip install -r requirements.txt):
#   .\scripts\client_locust_exports.ps1
#   .\scripts\client_locust_exports.ps1 -Users 1 -SpawnRate 1 -RunTime "3m" -Prefix "reports/client_run"
#
# Web UI alternative (no script):
#   locust -f src/locustfile.py
#   Then: Download Data tab → HTML report + CSVs, or open http://localhost:8089 and use Download Report.
# =============================================================================

param(
    [int] $Users = 1,
    [double] $SpawnRate = 1,
    [string] $RunTime = "3m",
    [string] $Prefix = "reports/client_locust_run",
    [switch] $CsvFullHistory
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Prefix) -ErrorAction SilentlyContinue | Out-Null

$args = @(
    "-m", "locust",
    "-f", "src/locustfile.py",
    "--headless",
    "-u", "$Users",
    "-r", "$SpawnRate",
    "-t", "$RunTime",
    "--csv", $Prefix,
    "--html", "$Prefix.html"
)

# Omit -CsvFullHistory for rows that look like Breakpoint_stats_history.csv (mostly "Aggregated" over time).
# Add --csv-full-history if the client wants every named endpoint on every interval as well.
if ($CsvFullHistory) {
    $args += "--csv-full-history"
}

Write-Host "Running: python $($args -join ' ')"
& python @args

Write-Host ""
Write-Host "Deliverables:"
Write-Host "  HTML report:        $Prefix.html"
Write-Host "  Stats history CSV:  ${Prefix}_stats_history.csv"
Write-Host "  Final stats CSV:    ${Prefix}_stats.csv"
