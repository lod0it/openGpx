#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "=== open-gpx - Setup iniziale ==="
echo ""

# Su macOS con Python moderno (PEP 668) pip3 system-wide è bloccato.
# Usa un venv minimo per il launcher se rich non è disponibile.
if ! python3 -c "import rich" 2>/dev/null; then
    LAUNCHER_VENV="$PROJECT_DIR/.launcher-venv"
    if [ ! -d "$LAUNCHER_VENV" ]; then
        echo "Creo venv launcher per rich..."
        python3 -m venv "$LAUNCHER_VENV"
        "$LAUNCHER_VENV/bin/pip" install rich --quiet
    fi
    PYTHON="$LAUNCHER_VENV/bin/python"
else
    PYTHON="python3"
fi

"$PYTHON" setup.py "$@"
