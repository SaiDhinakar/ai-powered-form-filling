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

# Start OCR service
info "Starting OCR service in background..."
./run_ocr_service.sh &
OCR_PID=$!
success "OCR service started with PID $OCR_PID"

# Start Agent service
info "Starting Agent service in background..."
./run_agent.sh &
AGENT_PID=$!
success "Agent service started with PID $AGENT_PID"

# Start FastAPI backend
info "Starting FastAPI backend in background..."
cd ..
uv run fastapi run ./api/main.py &
BACKEND_PID=$!
success "FastAPI backend started with PID $BACKEND_PID"

# Save PIDs to file for stopping later
cd "$SCRIPT_DIR"
echo "$OCR_PID" > .ocr_service.pid
echo "$AGENT_PID" > .agent_service.pid
echo "$BACKEND_PID" > .backend_service.pid

info "All services started in background. Use stop_server.sh to stop them."
