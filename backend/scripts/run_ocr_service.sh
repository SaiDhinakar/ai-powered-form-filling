#!/usr/bin/env bash
set -euo pipefail

# Color helpers
RESET="\033[0m"
RED="\033[1;31m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
CYAN="\033[1;36m"

info(){ printf "%b\n" "${CYAN}[INFO]${RESET} $*"; }
warn(){ printf "%b\n" "${YELLOW}[WARN]${RESET} $*"; }
err(){ printf "%b\n" "${RED}[ERROR]${RESET} $*" >&2; }

# Make script work when invoked from scripts/ directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || exit 1

# Find runner: prefer `uv`, fallback to `uvicorn` or `python -m uvicorn`
if command -v uv >/dev/null 2>&1; then
    RUNNER="uv"
elif command -v uvicorn >/dev/null 2>&1; then
    RUNNER="uvicorn"
else
    # last resort: check python can run uvicorn as module
    if python -c "import uvicorn" >/dev/null 2>&1; then
        RUNNER="python -m uvicorn"
    else
        err "No 'uv' or 'uvicorn' found in PATH. Activate your environment or install uvicorn."
        exit 2
    fi
fi

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8001}"
RELOAD="${RELOAD:-false}"
WORKERS="${WORKERS:-}"

ARGS=($RUNNER run ocr/server.py --host "$HOST" --port "$PORT")
[ "$RELOAD" = "true" ] && ARGS+=("--reload")
[ -n "$WORKERS" ] && ARGS+=("--workers" "$WORKERS")

info "Starting OCR service"
info "Command: ${GREEN}${ARGS[*]}${RESET}"

# Forward signals to child
child=0
_term() {
    warn "Stopping OCR service..."
    [ "$child" -ne 0 ] && kill -TERM "$child" 2>/dev/null || true
}
trap _term INT TERM

# Start
"${ARGS[@]}" &
child=$!
wait "$child"
exit_code=$?

if [ $exit_code -eq 0 ]; then
    info "OCR service exited normally."
else
    err "OCR service exited with code $exit_code"
fi

exit $exit_code