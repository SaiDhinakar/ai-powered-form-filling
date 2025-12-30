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
cd "$SCRIPT_DIR/.." || exit 1

# PIDs
OCR_PID=""
AGENT_PID=""
BACKEND_PID=""

# Cleanup function
cleanup() {
    echo ""
    warn "Stopping all services..."
    if [ -n "$BACKEND_PID" ]; then kill "$BACKEND_PID" 2>/dev/null || true; fi
    if [ -n "$AGENT_PID" ]; then kill "$AGENT_PID" 2>/dev/null || true; fi
    if [ -n "$OCR_PID" ]; then kill "$OCR_PID" 2>/dev/null || true; fi
    exit 0
}

# Trap Ctrl+C (SIGINT) and SIGTERM
trap cleanup INT TERM

info "Starting AI Powered Form Filling Stack (Dev Mode)..."

# 1. Start OCR Service
# Check if ocr/server.py exists
if [ -f "ocr/server.py" ]; then
    info "Starting OCR Service (Port 8001)..."
    ./scripts/run_ocr_service.sh &
    OCR_PID=$!
else
    warn "ocr/server.py not found, skipping OCR service."
fi

# 2. Start Agent Service
# Check if ai_agents/serve.py exists
if [ -f "ai_agents/serve.py" ]; then
    info "Starting AI Agent Service (Port 8907)..."
    ./scripts/run_agent.sh &
    AGENT_PID=$!
else
    warn "ai_agents/serve.py not found, skipping AI Agent service."
fi

# 3. Start Main Backend
info "Starting Main Backend (Port 8000)..."
uv run fastapi run api/main.py &
BACKEND_PID=$!

success "All services running. Logs will appear below. Press Ctrl+C to stop."
wait
