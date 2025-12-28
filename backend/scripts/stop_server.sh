#!/usr/bin/env bash
set -euo pipefail

# Color helpers
RESET="\033[0m"
RED="\033[1;31m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
CYAN="\033[1;36m"
BOLD="\033[1m"

info(){ printf "%b\n" "${CYAN}[INFO]${RESET} $*"; }
warn(){ printf "%b\n" "${YELLOW}[WARN]${RESET} $*"; }
err(){ printf "%b\n" "${RED}[ERROR]${RESET} $*" >&2; }
success(){ printf "%b\n" "${GREEN}[SUCCESS]${RESET} $*"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

stop_service() {
    local name="$1"
    local pidfile="$2"
    if [ -f "$pidfile" ]; then
        local pid
        pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            warn "Stopping $name (PID $pid)..."
            kill "$pid"
            success "$name stopped."
        else
            warn "$name (PID $pid) is not running."
        fi
        rm -f "$pidfile"
    else
        warn "$name PID file not found: $pidfile"
    fi
}

stop_service "OCR service" .ocr_service.pid
stop_service "Agent service" .agent_service.pid
stop_service "FastAPI backend" .backend_service.pid

info "All services stopped."
