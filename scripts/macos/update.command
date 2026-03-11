#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "=== open-gpx - Aggiornamento ==="
echo ""

# Preferisce il venv del backend (già include rich dopo setup).
# Fallback: venv launcher minimo per evitare pip system-wide (PEP 668).
BACKEND_PYTHON="$PROJECT_DIR/backend/.venv/bin/python"
LAUNCHER_VENV="$PROJECT_DIR/.launcher-venv"

if [ -f "$BACKEND_PYTHON" ]; then
    PYTHON="$BACKEND_PYTHON"
elif python3 -c "import rich" 2>/dev/null; then
    PYTHON="python3"
else
    if [ ! -d "$LAUNCHER_VENV" ]; then
        echo "Creo venv launcher per rich..."
        python3 -m venv "$LAUNCHER_VENV"
        "$LAUNCHER_VENV/bin/pip" install rich --quiet
    fi
    PYTHON="$LAUNCHER_VENV/bin/python"
fi

"$PYTHON" scripts/update.py "$@"
