#!/bin/bash
# Avvia open-gpx in background (start.py headless, log in logs/) e chiude
# questa finestra di Terminal. Per l'output live usare start_debug.command.
#
# La chiusura della finestra usa osascript: al primo avvio macOS chiede il
# permesso "Terminal vuole controllare Terminal" (Automazione). Se negato,
# la finestra resta aperta ma l'app continua a girare; si può riattivare in
# Impostazioni di Sistema > Privacy e sicurezza > Automazione > Terminal.
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

# Esegue un comando in una nuova sessione (macOS non ha setsid(1)):
# nessun terminale di controllo, SIGHUP ignorato, stdin da /dev/null.
detach() {
    nohup "$PYTHON" -c '
import os, sys
try:
    os.setsid()
except OSError:
    pass
os.execvp(sys.argv[1], sys.argv[1:])
' "$@" </dev/null &
    DETACHED_PID=$!
    disown
}

mkdir -p "$PROJECT_DIR/logs"
LOG_FILE="$PROJECT_DIR/logs/start.log"

detach "$PYTHON" scripts/start.py "$@" >"$LOG_FILE" 2>&1

echo "open-gpx in avvio in background (PID $DETACHED_PID)."
echo "Log: $LOG_FILE"

# Se start.py muore subito (prerequisiti mancanti, ecc.) lascia la finestra aperta.
sleep 3
if ! kill -0 "$DETACHED_PID" 2>/dev/null; then
    echo
    echo "start.py si è fermato. Ultime righe del log:"
    tail -n 20 "$LOG_FILE"
    echo
    read -r -p "Premi Invio per chiudere..."
    exit 1
fi

# Chiude la finestra solo dopo l'uscita di questo script e della shell di login:
# a tab non più occupato Terminal non mostra il prompt "terminare i processi?".
TTY_NAME="$(tty 2>/dev/null)"
if [ -n "$TTY_NAME" ] && [ "$TTY_NAME" != "not a tty" ]; then
    detach osascript \
        -e 'on run argv' \
        -e '  set ttyName to item 1 of argv' \
        -e '  repeat 50 times' \
        -e '    delay 0.2' \
        -e '    tell application "Terminal"' \
        -e '      set found to false' \
        -e '      repeat with w in windows' \
        -e '        repeat with t in tabs of w' \
        -e '          if tty of t is ttyName then' \
        -e '            set found to true' \
        -e '            if not busy of t then' \
        -e '              close w' \
        -e '              return' \
        -e '            end if' \
        -e '          end if' \
        -e '        end repeat' \
        -e '      end repeat' \
        -e '      if not found then return' \
        -e '    end tell' \
        -e '  end repeat' \
        -e 'end run' \
        "$TTY_NAME" >/dev/null 2>&1
fi

exit 0
