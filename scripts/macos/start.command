#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_DIR"

# Preferisce il venv del backend (già include rich dopo setup).
# Fallback: venv launcher minimo per evitare pip system-wide (PEP 668).
BACKEND_PYTHON="$PROJECT_DIR/backend/.venv/bin/python"
LAUNCHER_VENV="$PROJECT_DIR/.launcher-venv"

if [ -f "$BACKEND_PYTHON" ] && "$BACKEND_PYTHON" -c "import rich" 2>/dev/null; then
    PYTHON="$BACKEND_PYTHON"
elif python3 -c "import rich" 2>/dev/null; then
    PYTHON="python3"
else
    [ ! -d "$LAUNCHER_VENV" ] && python3 -m venv "$LAUNCHER_VENV"
    "$LAUNCHER_VENV/bin/pip" install rich --quiet
    PYTHON="$LAUNCHER_VENV/bin/python"
fi

"$PYTHON" scripts/start.py "$@"
