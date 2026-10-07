#!/usr/bin/env python3
"""
open-gpx - Pannello di controllo sviluppo
Avvia GraphHopper, Backend e Frontend in un unico terminale.

Uso:
    python start.py              # avvia tutto
    python start.py --no-gh      # salta GraphHopper (già avviato)
    python start.py --debug      # stream Rich con prefissi (default: silenzioso, log in logs/)
"""

import atexit
import json
import os
import sys
import subprocess
import threading
import signal
import time
import argparse
import webbrowser
import urllib.request
from pathlib import Path
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box
except ImportError:
    if sys.stdout is not None:
        print("Dipendenza mancante: pip install rich")
    sys.exit(1)

# ── Configurazione ──────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
SHUTDOWN_FLAG = ROOT / ".shutdown_requested"
LOCK_FILE = ROOT / ".opengpx.lock"
FE_URL = "http://localhost:5173"
LOGS_DIR = ROOT / "logs"

# Windows: nessuna finestra console per i processi figli
_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0

SERVICES = [
    {
        "key":   "GH",
        "label": "GraphHopper",
        "color": "yellow",
        "port":  8989,
        "url":   "http://localhost:8989/health",
    },
    {
        "key":   "BE",
        "label": "Backend",
        "color": "green",
        "port":  8000,
        "url":   "http://localhost:8000/api/health",
    },
    {
        "key":   "FE",
        "label": "Frontend",
        "color": "cyan",
        "port":  5173,
        "url":   "http://localhost:5173",
    },
]

# Lunghezza del prefisso "[GH ] " per allineamento
PREFIX_W = 5

# ── Stato globale ───────────────────────────────────────────────────────────

console = Console()
_lock   = threading.Lock()
_stop   = threading.Event()
_debug  = False
_log_files: dict[str, object] = {}

_status: dict[str, str] = {s["key"]: "starting" for s in SERVICES}
_pids:   dict[str, int]  = {}
_procs:  dict[str, subprocess.Popen] = {}

# ── Helper output ───────────────────────────────────────────────────────────

def _print(*args, **kwargs) -> None:
    """console.print solo in --debug e se esiste uno stdout (pythonw: None)."""
    if _debug and sys.stdout is not None:
        console.print(*args, **kwargs)


def _run(*args, **kwargs) -> subprocess.CompletedProcess:
    """subprocess.run senza finestra e senza stdin ereditato (pythonw)."""
    kwargs.setdefault("stdin", subprocess.DEVNULL)
    if _NO_WINDOW:
        kwargs.setdefault("creationflags", _NO_WINDOW)
    return subprocess.run(*args, **kwargs)


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def log(key: str, line: str, level: str = "info") -> None:
    svc   = next(s for s in SERVICES if s["key"] == key)
    color = svc["color"]
    label = key.ljust(PREFIX_W)

    ts_markup   = f"[dim]{_ts()}[/dim]"
    pfx_markup  = f"[bold {color}][{label}][/bold {color}]"
    line_clean  = line.rstrip()

    if level == "warn":
        body = f"[yellow]{line_clean}[/yellow]"
    elif level == "error":
        body = f"[red]{line_clean}[/red]"
    else:
        body = line_clean

    with _lock:
        _print(f"{ts_markup} {pfx_markup} {body}", highlight=False)


def info(msg: str) -> None:
    with _lock:
        _print(f"[dim]{_ts()}[/dim] [bold white][DASH ][/bold white] {msg}")


def warn(msg: str) -> None:
    with _lock:
        _print(f"[dim]{_ts()}[/dim] [bold yellow][DASH ][/bold yellow] [yellow]{msg}[/yellow]")


def err(msg: str) -> None:
    with _lock:
        _print(f"[dim]{_ts()}[/dim] [bold red][DASH ][/bold red] [red]{msg}[/red]")


# ── Banner iniziale ─────────────────────────────────────────────────────────

def print_banner(services_to_start: list[dict]) -> None:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("Servizio", style="bold")
    table.add_column("Porta")
    table.add_column("URL")

    for s in services_to_start:
        table.add_row(
            f"[{s['color']}]{s['label']}[/{s['color']}]",
            str(s["port"]),
            s["url"],
        )

    panel = Panel(
        table,
        title="[bold]open-gpx dev[/bold]",
        subtitle="Ctrl+C per fermare tutto",
        border_style="bright_blue",
    )
    _print(panel)
    _print()


# ── Setup state ───────────────────────────────────────────────────────────────

def load_state() -> dict:
    state_file = ROOT / "backend" / ".setup-state"
    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ── Prerequisiti ─────────────────────────────────────────────────────────────

def check_prerequisites(skip_gh: bool) -> bool:
    ok = True
    state = load_state()

    if not state:
        warn("Setup non completato — esegui setup.command prima di avviare")

    if not skip_gh:
        java_ok = _run(
            ["java", "-version"], capture_output=True
        ).returncode == 0
        if not java_ok:
            warn("Java non trovato — GraphHopper non potrà avviarsi")
            return False

        gh_dir = ROOT / "graphhopper"

        # JAR: usa il nome dallo state, oppure cerca il primo disponibile
        jar_name = state.get("jar_filename", "")
        if jar_name:
            if not (gh_dir / jar_name).exists():
                warn(f"JAR non trovato: graphhopper/{jar_name}")
                ok = False
        else:
            jars = list(gh_dir.glob("graphhopper-web-*.jar"))
            if not jars:
                warn("Nessun GraphHopper JAR trovato in graphhopper/")
                ok = False

        # OSM: usa il nome dallo state, oppure cerca il primo .pbf disponibile
        osm_name = state.get("osm_filename", "")
        if osm_name:
            if not (gh_dir / osm_name).exists():
                warn(f"File OSM non trovato: graphhopper/{osm_name}")
                ok = False
        else:
            pbfs = list(gh_dir.glob("*.pbf"))
            if not pbfs:
                warn("Nessun file OSM .pbf trovato in graphhopper/")
                ok = False

    is_win = sys.platform == "win32"
    venv_py = ROOT / "backend" / ".venv" / ("Scripts" if is_win else "bin") / ("python.exe" if is_win else "python")
    if not venv_py.exists():
        warn("Virtualenv backend non trovato — esegui setup.command")
        ok = False

    nm = ROOT / "frontend" / "node_modules"
    if not nm.exists():
        warn("node_modules non trovato — esegui: cd frontend && npm install")
        ok = False

    return ok


# ── Istanza singola ───────────────────────────────────────────────────────────

def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform == "win32":
        import ctypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        h = k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return ctypes.get_last_error() == 5  # ERROR_ACCESS_DENIED: esiste
        try:
            code = ctypes.c_ulong()
            return bool(k32.GetExitCodeProcess(h, ctypes.byref(code))) and code.value == 259  # STILL_ACTIVE
        finally:
            k32.CloseHandle(h)
    try:
        os.kill(pid, 0)
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _read_lock_pid() -> int:
    # Riprova brevemente: un'istanza concorrente può aver creato il file senza averlo ancora scritto
    for _ in range(5):
        try:
            return int(LOCK_FILE.read_text(encoding="utf-8").strip())
        except FileNotFoundError:
            return 0
        except (OSError, ValueError):
            time.sleep(0.2)
    return 0


def release_lock() -> None:
    if _read_lock_pid() == os.getpid():
        LOCK_FILE.unlink(missing_ok=True)


def acquire_lock() -> int:
    """Crea il lock file. Ritorna 0 se acquisito, altrimenti il PID dell'istanza attiva."""
    for _ in range(3):
        try:
            fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            pid = _read_lock_pid()
            if _pid_alive(pid):
                return pid
            LOCK_FILE.unlink(missing_ok=True)  # lock stale: PID morto
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
        atexit.register(release_lock)
        return 0
    return 0


# ── Pulizia porte ─────────────────────────────────────────────────────────────

def kill_port(port: int) -> None:
    """Termina tutti i processi in ascolto sulla porta specificata."""
    is_win = sys.platform == "win32"
    try:
        if is_win:
            r = _run(
                f'netstat -ano | findstr ":{port} "',
                shell=True, capture_output=True, text=True,
            )
            pids: set[str] = set()
            for line in r.stdout.splitlines():
                parts = line.split()
                if "LISTENING" in line and len(parts) >= 5:
                    pids.add(parts[-1])
            for pid in pids:
                _run(
                    ["taskkill", "/PID", pid, "/F", "/T"],
                    capture_output=True,
                )
                info(f"Processo PID {pid} sulla porta {port} terminato")
        else:
            r = _run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True, text=True,
            )
            for pid in r.stdout.split():
                _run(["kill", "-9", pid], capture_output=True)
                info(f"Processo PID {pid} sulla porta {port} terminato")
    except Exception:
        pass


def free_ports(services: list[dict]) -> None:
    for svc in services:
        kill_port(svc["port"])


# ── Reader thread ─────────────────────────────────────────────────────────────

def _reader(key: str, proc: subprocess.Popen) -> None:
    """Legge stdout+stderr del processo e stampa le righe con prefisso colorato."""
    try:
        for raw in proc.stdout:  # type: ignore[union-attr]
            if _stop.is_set():
                break
            line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
            if not line:
                continue

            lower = line.lower()
            if any(w in lower for w in ("error", "exception", "critical", "failed")):
                lvl = "error"
            elif any(w in lower for w in ("warn", "warning")):
                lvl = "warn"
            else:
                lvl = "info"

            log(key, line, lvl)
    except Exception:
        pass
    finally:
        with _lock:
            _status[key] = "stopped"
        if not _stop.is_set():
            warn(f"{key} si è fermato inaspettatamente")


# ── JVM heap size ─────────────────────────────────────────────────────────────

def _jvm_xmx() -> str:
    """Ritorna un flag -Xmx appropriato basato sulla RAM disponibile."""
    try:
        total = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        mb = max(2048, min(int(total * 0.60 / 1024 / 1024), 8192))
        return f"{mb}m"
    except Exception:
        return "4g"


def _popen_io(key: str) -> dict:
    """Debug: pipe letta dal reader. Headless: output diretto su logs/<key>.log."""
    kw: dict = {"stdin": subprocess.DEVNULL, "stderr": subprocess.STDOUT}
    if _NO_WINDOW:
        kw["creationflags"] = _NO_WINDOW
    if sys.platform != "win32":
        kw["start_new_session"] = True  # process group proprio → killpg sull'albero
    if _debug:
        kw["stdout"] = subprocess.PIPE
    else:
        LOGS_DIR.mkdir(exist_ok=True)
        f = open(LOGS_DIR / f"{key}.log", "wb")  # troncato ad ogni avvio
        _log_files[key] = f
        kw["stdout"] = f
    return kw


# ── Avvio processi ────────────────────────────────────────────────────────────

def start_graphhopper() -> subprocess.Popen | None:
    gh_dir = ROOT / "graphhopper"

    # Leggi il nome del JAR dallo state; fallback: primo JAR trovato
    state = load_state()
    jar_name = state.get("jar_filename", "")
    if not jar_name or not (gh_dir / jar_name).exists():
        jars = list(gh_dir.glob("graphhopper-web-*.jar"))
        if not jars:
            err("Nessun GraphHopper JAR trovato in graphhopper/")
            return None
        jar_name = jars[0].name

    graph_location = state.get("graph_location", "")
    if graph_location:
        graph_dir = gh_dir / graph_location
        if graph_dir.exists() and any(graph_dir.iterdir()):
            info(f"GH: caricamento grafo dalla cache ({graph_location}/)")
        else:
            info("GH: prima build — costruzione grafo in corso (potrebbe richiedere minuti)...")

    xmx = _jvm_xmx()
    cmd = ["java", f"-Xmx{xmx}", "-jar", str(gh_dir / jar_name), "server", "config.yml"]
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=gh_dir,
            **_popen_io("GH"),
        )
        return proc
    except FileNotFoundError:
        err("Java non trovato nel PATH")
        return None


def start_backend() -> subprocess.Popen | None:
    is_win = sys.platform == "win32"
    venv_py = ROOT / "backend" / ".venv" / ("Scripts" if is_win else "bin") / ("python.exe" if is_win else "python")
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    cmd = [
        str(venv_py), "-m", "uvicorn",
        "app.main:app", "--reload", "--port", "8000",
    ]
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=ROOT / "backend",
            **_popen_io("BE"),
            env=env,
        )
        return proc
    except Exception as e:
        err(f"Impossibile avviare Backend: {e}")
        return None


def start_frontend() -> subprocess.Popen | None:
    # su Windows npm è uno script .cmd → serve shell=True
    try:
        proc = subprocess.Popen(
            "npm run dev",
            cwd=ROOT / "frontend",
            **_popen_io("FE"),
            shell=True,
        )
        return proc
    except Exception as e:
        err(f"Impossibile avviare Frontend: {e}")
        return None


# ── Stop pulito ───────────────────────────────────────────────────────────────

def kill_tree(proc: subprocess.Popen) -> None:
    """Termina il processo e tutti i discendenti (node, worker uvicorn, ...)."""
    if sys.platform == "win32":
        _run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
    else:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
        # Il leader può essere uscito lasciando figli nel gruppo
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass


def shutdown(services: list[dict]) -> None:
    _stop.set()
    _print()
    info("[bold]Arresto in corso...[/bold]")

    for key, proc in list(_procs.items()):
        try:
            kill_tree(proc)
            info(f"{key} terminato")
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    # Rete di sicurezza: discendenti orfani ancora in ascolto sulle nostre porte
    free_ports(services)

    _print()
    _print(Panel("[bold green]Tutti i servizi fermati.[/bold green]", border_style="green"))


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="open-gpx dev dashboard")
    parser.add_argument("--no-gh", action="store_true", help="Salta GraphHopper")
    parser.add_argument("--debug", action="store_true", help="Stream Rich con prefissi (default: log su file)")
    args = parser.parse_args()

    global _debug
    _debug = args.debug

    # Istanza già attiva: apri solo il browser, non toccare porte né processi
    if acquire_lock():
        webbrowser.open(FE_URL)
        return

    skip_gh = args.no_gh
    active_services = [s for s in SERVICES if not (skip_gh and s["key"] == "GH")]

    print_banner(active_services)
    check_prerequisites(skip_gh)
    _print()

    # Rimuovi eventuale flag di shutdown residuo
    SHUTDOWN_FLAG.unlink(missing_ok=True)

    # Libera le porte prima di avviare (evita "Address already in use")
    info("Pulizia porte in uso...")
    free_ports(active_services)
    _print()

    # Avvio processi
    starters = {
        "GH": start_graphhopper,
        "BE": start_backend,
        "FE": start_frontend,
    }

    threads: list[threading.Thread] = []

    for svc in active_services:
        key = svc["key"]
        info(f"Avvio {svc['label']} (porta {svc['port']})...")
        proc = starters[key]()
        if proc is None:
            _status[key] = "failed"
            continue

        _procs[key] = proc
        _pids[key]  = proc.pid
        _status[key] = "running"
        info(f"{svc['label']} avviato (PID {proc.pid})")

        if _debug:
            t = threading.Thread(target=_reader, args=(key, proc), daemon=True)
            t.start()
            threads.append(t)

    if not _procs:
        err("Nessun servizio avviato. Controlla i prerequisiti.")
        sys.exit(1)

    _print()
    info("[bold green]Tutti i servizi avviati.[/bold green] Premi [bold]Ctrl+C[/bold] per fermare.")
    _print()

    # Apri il browser quando frontend E GraphHopper sono pronti
    def _open_browser() -> None:
        fe_url = FE_URL

        # Attendi frontend
        for _ in range(60):
            if _stop.is_set():
                return
            try:
                urllib.request.urlopen(fe_url, timeout=1)
                break
            except Exception:
                time.sleep(1)
        else:
            warn("Timeout: frontend non raggiunto, browser non aperto")
            return

        info(f"Browser aperto su [cyan]{fe_url}[/cyan]")
        webbrowser.open(fe_url)

    threading.Thread(target=_open_browser, daemon=True).start()

    # Attesa Ctrl+C o chiusura browser
    try:
        signal.signal(signal.SIGINT, lambda s, f: None)   # gestito da except
        while not _stop.is_set():
            # Controlla se tutti i processi sono morti
            alive = [k for k, p in _procs.items() if p.poll() is None]
            if not alive:
                err("Tutti i servizi si sono fermati.")
                break
            # Controlla flag di shutdown da heartbeat monitor
            if SHUTDOWN_FLAG.exists():
                try:
                    SHUTDOWN_FLAG.unlink()
                except Exception:
                    pass
                info("Browser chiuso — arresto automatico in corso...")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        shutdown(active_services)


if __name__ == "__main__":
    main()
