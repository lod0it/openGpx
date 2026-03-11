#!/usr/bin/env python3
"""
open-gpx - Setup iniziale
Esegui dopo il clone per installare tutte le dipendenze e scaricare i file necessari.

Uso:
    python setup.py
"""

import hashlib
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
STATE_FILE = ROOT / "backend" / ".setup-state"

# ── Rich opzionale ───────────────────────────────────────────────────────────

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import (
        BarColumn,
        DownloadColumn,
        Progress,
        TextColumn,
        TimeRemainingColumn,
        TransferSpeedColumn,
    )
    _rich = True
    console = Console()
except ImportError:
    _rich = False
    console = None  # type: ignore[assignment]


def _print(msg: str) -> None:
    if _rich:
        console.print(msg)  # type: ignore[union-attr]
    else:
        # strip rich markup
        clean = re.sub(r"\[/?[^\]]*\]", "", msg)
        print(clean)


def _print_panel(title: str, body: str, style: str = "bright_blue") -> None:
    if _rich:
        console.print(Panel(body, title=f"[bold]{title}[/bold]", border_style=style))  # type: ignore[union-attr]
    else:
        print(f"\n{'='*50}")
        print(f"  {title}")
        print(f"{'='*50}")
        print(body)
        print()


def _ok(msg: str) -> None:
    _print(f"[green]  OK[/green]  {msg}")


def _skip(msg: str) -> None:
    _print(f"[dim]  --[/dim]  [dim]{msg}[/dim]")


def _info(msg: str) -> None:
    _print(f"[cyan]  ..[/cyan]  {msg}")


def _warn(msg: str) -> None:
    _print(f"[yellow]  !![/yellow]  [yellow]{msg}[/yellow]")


def _fail(msg: str) -> None:
    _print(f"[red]  XX[/red]  [red]{msg}[/red]")


# ── Stato ────────────────────────────────────────────────────────────────────

def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return f"sha256:{h.hexdigest()}"


# ── Download ─────────────────────────────────────────────────────────────────

def _make_ssl_context() -> ssl.SSLContext:
    """Crea un SSL context cercando i certificati in ordine di preferenza."""
    # 1. certifi (se installato)
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        pass
    # 2. Certificati di sistema macOS via /etc/ssl o bundle Homebrew/Python.org
    for ca_path in (
        "/etc/ssl/cert.pem",
        "/usr/local/etc/openssl@3/cert.pem",
        "/opt/homebrew/etc/openssl@3/cert.pem",
    ):
        if os.path.exists(ca_path):
            return ssl.create_default_context(cafile=ca_path)
    # 3. Fallback: contesto di default (funziona su Linux e Windows)
    return ssl.create_default_context()


def _urlretrieve(url: str, dest: Path, reporthook=None) -> None:
    """Wrapper di urlretrieve che installa un opener con SSL corretto."""
    ctx = _make_ssl_context()
    https_handler = urllib.request.HTTPSHandler(context=ctx)
    opener = urllib.request.build_opener(https_handler)
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, dest, reporthook)


def download_file(url: str, dest: Path) -> bool:
    """Scarica url in dest. Usa file .part durante il download."""
    part = dest.with_suffix(dest.suffix + ".part")
    try:
        if _rich:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
                console=console,  # type: ignore[arg-type]
                transient=True,
            ) as progress:
                task = progress.add_task(f"Download {dest.name}", total=None)

                def _reporthook(count: int, block_size: int, total_size: int) -> None:
                    if total_size > 0:
                        progress.update(task, total=total_size, completed=count * block_size)
                    else:
                        progress.update(task, advance=block_size)

                _urlretrieve(url, part, _reporthook)
        else:
            def _reporthook(count: int, block_size: int, total_size: int) -> None:
                downloaded = count * block_size
                if total_size > 0:
                    pct = min(100, downloaded * 100 // total_size)
                    mb_down = downloaded / 1_048_576
                    mb_tot = total_size / 1_048_576
                    print(f"\r  {mb_down:.1f} MB / {mb_tot:.1f} MB ({pct}%)   ", end="", flush=True)

            _urlretrieve(url, part, _reporthook)
            print()

        part.rename(dest)
        return True
    except Exception as e:
        _fail(f"Download fallito: {e}")
        if part.exists():
            part.unlink()
        return False


# ── Prerequisiti ─────────────────────────────────────────────────────────────

def _run_version(cmd: list[str]) -> str | None:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
        return (r.stdout + r.stderr).strip()
    except FileNotFoundError:
        return None


def check_prerequisites() -> bool:
    _print("\n[bold]Step 1 — Verifica prerequisiti[/bold]")
    ok = True

    # Python
    vi = sys.version_info
    if vi < (3, 12):
        _fail(f"Python 3.12+ richiesto, trovato {vi.major}.{vi.minor}")
        ok = False
    else:
        _ok(f"Python {vi.major}.{vi.minor}.{vi.micro}")

    # Java
    java_out = _run_version(["java", "-version"])
    if java_out is None:
        _fail("Java non trovato — installa Java 11+: https://adoptium.net")
        ok = False
    else:
        m = re.search(r'version "(\d+)', java_out)
        ver = int(m.group(1)) if m else 0
        if ver < 11:
            _fail(f"Java 11+ richiesto, trovato versione {ver}")
            ok = False
        else:
            _ok(f"Java ({java_out.splitlines()[0]})")

    # Node.js
    node_out = _run_version(["node", "--version"])
    if node_out is None:
        _fail("Node.js non trovato — installa Node.js 18+: https://nodejs.org")
        ok = False
    else:
        m = re.match(r"v(\d+)", node_out)
        ver = int(m.group(1)) if m else 0
        if ver < 18:
            _fail(f"Node.js 18+ richiesto, trovato {node_out}")
            ok = False
        else:
            _ok(f"Node.js {node_out}")

    return ok


# ── Backend venv ──────────────────────────────────────────────────────────────

def setup_backend(state: dict) -> dict:
    _print("\n[bold]Step 2 — Backend: venv e dipendenze[/bold]")

    is_win = sys.platform == "win32"
    venv_dir = ROOT / "backend" / ".venv"
    pip_path = venv_dir / ("Scripts" if is_win else "bin") / ("pip" if not is_win else "pip.exe")
    req_file = ROOT / "backend" / "requirements.txt"

    venv_created = False
    if not venv_dir.exists():
        _info("Creo virtualenv backend...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        venv_created = True
        _ok("Virtualenv creato")
    else:
        _skip("Virtualenv già presente")

    req_hash = sha256_file(req_file)
    if venv_created or req_hash != state.get("requirements_txt_hash"):
        _info("Installo dipendenze Python...")
        subprocess.run(
            [str(pip_path), "install", "-r", str(req_file), "--quiet"],
            check=True,
        )
        _ok("Dipendenze Python installate")
        state["requirements_txt_hash"] = req_hash
    else:
        _skip("Dipendenze Python aggiornate (nessuna modifica a requirements.txt)")

    return state


# ── Frontend npm ──────────────────────────────────────────────────────────────

def setup_frontend(state: dict) -> dict:
    _print("\n[bold]Step 3 — Frontend: npm install[/bold]")

    pkg_file = ROOT / "frontend" / "package.json"
    nm = ROOT / "frontend" / "node_modules"
    pkg_hash = sha256_file(pkg_file)

    if not nm.exists() or pkg_hash != state.get("package_json_hash"):
        _info("Eseguo npm install...")
        subprocess.run(
            "npm install",
            cwd=ROOT / "frontend",
            shell=True,
            check=True,
        )
        _ok("Dipendenze Node.js installate")
        state["package_json_hash"] = pkg_hash
    else:
        _skip("node_modules aggiornato (nessuna modifica a package.json)")

    return state


# ── .env ──────────────────────────────────────────────────────────────────────

def setup_env() -> None:
    _print("\n[bold]Step 4 — File .env[/bold]")
    env_file = ROOT / "backend" / ".env"
    example = ROOT / "backend" / ".env.example"

    if env_file.exists():
        _skip(".env già presente")
        return

    if example.exists():
        shutil.copy(example, env_file)
        _ok(".env creato da .env.example")
    else:
        env_file.write_text("# open-gpx backend environment\n", encoding="utf-8")
        _ok(".env vuoto creato")


# ── Selezione regione OSM ────────────────────────────────────────────────────

REGIONS = [
    ("Italy (default)", "italy-latest.osm.pbf", "~2.0 GB"),
    ("France", "france-latest.osm.pbf", "~4.1 GB"),
    ("Spain", "spain-latest.osm.pbf", "~1.3 GB"),
    ("Germany", "germany-latest.osm.pbf", "~3.8 GB"),
    ("Switzerland", "switzerland-latest.osm.pbf", "~470 MB"),
    ("Austria", "austria-latest.osm.pbf", "~690 MB"),
]
GEOFABRIK_BASE = "https://download.geofabrik.de/europe/"


def select_osm_region() -> tuple[str, str] | None:
    """Ritorna (filename, url) oppure None se si vuole saltare."""
    gh_dir = ROOT / "graphhopper"
    existing_pbf = list(gh_dir.glob("*.pbf"))
    if existing_pbf:
        _skip(f"File OSM già presente: {existing_pbf[0].name}")
        return existing_pbf[0].name, ""  # url vuoto = skip download

    _print("\n  Scegli la regione da scaricare:")
    for i, (name, _, size) in enumerate(REGIONS, 1):
        _print(f"    {i}. {name:<25} {size}")
    _print(f"    {len(REGIONS)+1}. URL personalizzato")

    try:
        raw = input(f"\n  Scelta [1]: ").strip() or "1"
        choice = int(raw)
    except (ValueError, EOFError):
        choice = 1

    if 1 <= choice <= len(REGIONS):
        _, filename, _ = REGIONS[choice - 1]
        url = GEOFABRIK_BASE + filename
        return filename, url
    elif choice == len(REGIONS) + 1:
        try:
            url = input("  URL: ").strip()
        except EOFError:
            url = ""
        if not url:
            return None
        filename = url.split("/")[-1]
        return filename, url
    else:
        return None


def _update_config_yml(filename: str) -> None:
    cfg = ROOT / "graphhopper" / "config.yml"
    if not cfg.exists():
        return
    text = cfg.read_text(encoding="utf-8")
    new_text = re.sub(r"datareader\.file:.*", f"datareader.file: {filename}", text)
    if new_text != text:
        cfg.write_text(new_text, encoding="utf-8")
        _ok(f"config.yml aggiornato: datareader.file = {filename}")


def download_osm(state: dict) -> dict:
    _print("\n[bold]Step 5 — File OSM .pbf[/bold]")

    result = select_osm_region()
    if result is None:
        _warn("Nessun file OSM selezionato — GraphHopper non funzionerà senza di esso")
        return state

    filename, url = result
    dest = ROOT / "graphhopper" / filename

    if dest.exists() and dest.stat().st_size > 100 * 1024 * 1024:
        _skip(f"{filename} già presente e completo")
        state["osm_filename"] = filename
        _update_config_yml(filename)
        return state

    if not url:
        return state

    _info(f"Download {filename} da Geofabrik...")
    ok = download_file(url, dest)
    if ok:
        _ok(f"{filename} scaricato")
        state["osm_filename"] = filename
        _update_config_yml(filename)
    return state


# ── GraphHopper JAR ──────────────────────────────────────────────────────────

def _get_gh_version() -> str:
    m = re.search(r'"graphhopper-web-([\d.]+)\.jar"', (ROOT / "start.py").read_text())
    return m.group(1) if m else "10.0"


def download_jar(state: dict) -> dict:
    _print("\n[bold]Step 6 — GraphHopper JAR[/bold]")
    ver = _get_gh_version()
    jar_name = f"graphhopper-web-{ver}.jar"
    dest = ROOT / "graphhopper" / jar_name

    if dest.exists() and dest.stat().st_size > 10 * 1024 * 1024:
        _skip(f"{jar_name} già presente")
        state["jar_filename"] = jar_name
        return state

    url = f"https://github.com/graphhopper/graphhopper/releases/download/{ver}/{jar_name}"
    _info(f"Download {jar_name}...")
    ok = download_file(url, dest)
    if ok:
        _ok(f"{jar_name} scaricato")
        state["jar_filename"] = jar_name
    return state


# ── Elevation tiles ──────────────────────────────────────────────────────────

def download_elevation(state: dict) -> dict:
    _print("\n[bold]Step 7 — SRTM Elevation tiles (opzionale)[/bold]")
    script = ROOT / "scripts" / "download_elevation.py"
    if not script.exists():
        _skip("Script download_elevation.py non trovato — skip")
        return state

    try:
        answer = input("  Download SRTM elevation tiles? [y/N]: ").strip().lower()
    except EOFError:
        answer = "n"

    if answer == "y":
        _info("Avvio download elevation tiles...")
        subprocess.run([sys.executable, str(script)], check=False)
    else:
        _skip("Elevation tiles saltate")

    return state


# ── Prebuild grafo GraphHopper ───────────────────────────────────────────────

def build_gh_graph(state: dict) -> dict:
    _print("\n[bold]Step 8 — Prebuild grafo GraphHopper[/bold]")
    gh_dir = ROOT / "graphhopper"

    # Leggi graph.location da config.yml
    cfg = gh_dir / "config.yml"
    graph_location = "italy-gh"
    if cfg.exists():
        m = re.search(r"graph\.location:\s*(\S+)", cfg.read_text(encoding="utf-8"))
        if m:
            graph_location = m.group(1)

    graph_dir = gh_dir / graph_location

    # Controlla se già costruito
    if graph_dir.exists() and any(graph_dir.iterdir()):
        _skip(f"Grafo già presente: {graph_location}/ — skip")
        state["graph_built"] = True
        state["graph_location"] = graph_location
        return state

    jar_name = state.get("jar_filename", "")
    if not jar_name or not (gh_dir / jar_name).exists():
        _warn("JAR non trovato nello state — prebuild saltato")
        return state

    osm_name = state.get("osm_filename", "")
    _warn(f"Prima esecuzione: costruzione grafo da [bold]{osm_name}[/bold]")
    _warn("Questa operazione richiede 10–30 minuti per regioni grandi (es. Italy)")
    _print("")

    PHASES = [
        ("start creating graph",      "Importazione OSM",          5),
        ("pass1 finished",            "Lettura waypoint",          20),
        ("pass2 finished",            "Costruzione archi",         45),
        ("Finished graph:",           "Grafo base completato",     60),
        ("LandmarkStorage",           "Preparazione landmarks",    72),
        ("PrepareRoutingSubnetworks", "Ottimizzazione rete",       85),
        ("Started @",                 "GraphHopper pronto!",       100),
    ]

    current_pct = [0]
    current_desc = ["Avvio GraphHopper..."]
    last_log_line = [""]
    done_event = threading.Event()

    cmd = ["java", "-jar", str(gh_dir / jar_name), "server", "config.yml"]
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=gh_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except FileNotFoundError:
        _fail("Java non trovato — installa Java 11+ e riesegui setup")
        return state

    def _read_gh_output() -> None:
        for raw in proc.stdout:  # type: ignore[union-attr]
            line = raw.decode("utf-8", errors="replace").rstrip()
            if not line:
                continue
            last_log_line[0] = line
            for keyword, desc, pct in PHASES:
                if keyword in line:
                    if pct > current_pct[0]:
                        current_pct[0] = pct
                        current_desc[0] = desc
                    if pct == 100:
                        done_event.set()
                    break
        done_event.set()  # EOF = processo terminato

    def _poll_health() -> None:
        while not done_event.is_set():
            try:
                urllib.request.urlopen("http://localhost:8989/health", timeout=2)
                current_pct[0] = 100
                current_desc[0] = "GraphHopper pronto!"
                done_event.set()
                return
            except Exception:
                pass
            time.sleep(3)

    threading.Thread(target=_read_gh_output, daemon=True).start()
    threading.Thread(target=_poll_health, daemon=True).start()

    start_ts = time.time()
    try:
        if _rich:
            from rich.live import Live
            from rich.text import Text

            with Live(console=console, refresh_per_second=2) as live:  # type: ignore[arg-type]
                while not done_event.is_set():
                    elapsed = int(time.time() - start_ts)
                    mins, secs = divmod(elapsed, 60)
                    pct = current_pct[0]
                    bar_len = 40
                    filled = int(bar_len * pct / 100)
                    bar = "█" * filled + "░" * (bar_len - filled)
                    log_tail = last_log_line[0][-90:] if last_log_line[0] else ""
                    txt = Text()
                    txt.append(f"  [{bar}] {pct:3d}%  {mins}m {secs:02d}s\n", style="cyan")
                    txt.append(f"  {current_desc[0]}\n", style="bold white")
                    if log_tail:
                        txt.append(f"  {log_tail}", style="dim")
                    live.update(txt)
                    if proc.poll() is not None:
                        break
                    time.sleep(0.5)
        else:
            while not done_event.is_set():
                elapsed = int(time.time() - start_ts)
                mins, secs = divmod(elapsed, 60)
                print(
                    f"\r  [{current_pct[0]:3d}%] {current_desc[0]} ({mins}m {secs:02d}s)   ",
                    end="", flush=True,
                )
                if proc.poll() is not None:
                    break
                time.sleep(2)
            print()
    except KeyboardInterrupt:
        _warn("\nInterrotto — rimozione grafo parziale...")
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(graph_dir, ignore_errors=True)
        _fail("Prebuild annullato. Riesegui setup per completare.")
        sys.exit(1)

    # Termina GH (al prossimo avvio caricherà il grafo dalla cache, molto più veloce)
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()

    elapsed_total = int(time.time() - start_ts)
    mins, secs = divmod(elapsed_total, 60)
    if current_pct[0] >= 100:
        _ok(f"Grafo costruito in {mins}m {secs:02d}s → {graph_location}/")
        state["graph_built"] = True
        state["graph_location"] = graph_location
    else:
        _fail("Costruzione grafo non completata — controlla che Java sia installato correttamente.")
        shutil.rmtree(graph_dir, ignore_errors=True)

    return state


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    _print_panel(
        "open-gpx — Setup",
        "Questo script prepara l'ambiente per la prima esecuzione.\n"
        "Ogni step è idempotente: può essere rieseguito senza problemi.",
    )

    state = load_state()

    # Step 1
    if not check_prerequisites():
        _fail("\nPrerequisiti mancanti. Correggi gli errori sopra e riesegui setup.py")
        sys.exit(1)

    # Step 2
    state = setup_backend(state)

    # Step 3
    state = setup_frontend(state)

    # Step 4
    setup_env()

    # Step 5
    state = download_osm(state)

    # Step 6
    state = download_jar(state)

    # Step 7 (elevation)
    state = download_elevation(state)

    # Step 8 — Prebuild grafo GH (solo se OSM e JAR presenti)
    if state.get("osm_filename") and state.get("jar_filename"):
        state = build_gh_graph(state)
    else:
        _warn("OSM o JAR mancanti — il grafo verrà costruito al primo avvio (lento)")

    # Salva stato
    state["schema_version"] = 1
    state["setup_completed"] = True
    cfg_file = ROOT / "graphhopper" / "config.yml"
    if cfg_file.exists():
        state["graphhopper_config_hash"] = sha256_file(cfg_file)
    save_state(state)

    # Imposta bit eseguibile sui .command macOS (non Windows)
    if sys.platform != "win32":
        for cmd_file in (ROOT / "scripts" / "macos").glob("*.command"):
            cmd_file.chmod(cmd_file.stat().st_mode | 0o111)

    _print("\n[bold green]Setup completato![/bold green] Avvio applicazione...\n")
    try:
        for i in range(3, 0, -1):
            print(f"  Avvio in {i}... (Ctrl+C per annullare)", end="\r", flush=True)
            time.sleep(1)
        print()
        subprocess.run([sys.executable, str(ROOT / "start.py")])
    except KeyboardInterrupt:
        _print("\n[dim]Avvio annullato. Esegui start.bat per avviare manualmente.[/dim]")


if __name__ == "__main__":
    main()
