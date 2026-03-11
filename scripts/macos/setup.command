#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "=== open-gpx - Setup iniziale ==="
echo ""

# Su macOS con Python moderno (PEP 668) pip3 system-wide è bloccato.
# Usa un venv minimo per il launcher se rich non è disponibile.
LAUNCHER_VENV="$PROJECT_DIR/.launcher-venv"

if python3 -c "import rich" 2>/dev/null; then
    PYTHON="python3"
else
    [ ! -d "$LAUNCHER_VENV" ] && python3 -m venv "$LAUNCHER_VENV"
    "$LAUNCHER_VENV/bin/pip" install rich --quiet
    PYTHON="$LAUNCHER_VENV/bin/python"
fi

"$PYTHON" scripts/setup.py "$@"
