#!/usr/bin/env bash
set -euo pipefail

# Color palette
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
RESET='\033[0m'

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
backend_dir="$(cd "$script_dir/.." && pwd)"

printf "${BLUE}${BOLD}→ Starting ADK API server${RESET}\n"
printf "${YELLOW}Changing to backend directory: %s${RESET}\n" "$backend_dir"
cd "$backend_dir"

if ! command -v uv >/dev/null 2>&1; then
    printf "${RED}ERROR:${RESET} 'uv' not found. Activate your environment or install required tooling.\n"
    exit 1
fi

printf "${GREEN}Running:${RESET} ${BOLD}uv run fastapi run ai_agents/serve.py --host 0.0.0.0 --port 8907${RESET}\n"
uv run fastapi run ai_agents/serve.py --host 0.0.0.0 --port 8907
rc=$?

if [ $rc -eq 0 ]; then
    printf "${GREEN}ADK API server exited successfully.${RESET}\n"
else
    printf "${RED}ADK API server exited with status %d.${RESET}\n" "$rc"
fi

exit $rc