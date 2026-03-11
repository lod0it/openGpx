#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "=== open-gpx - Aggiornamento ==="
echo ""

# Installa rich se mancante
python3 -c "import rich" 2>/dev/null || pip3 install rich --quiet

python3 update.py "$@"
