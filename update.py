#!/usr/bin/env python3
"""
open-gpx - Aggiornamento dopo git pull
Rileva dipendenze cambiate e le reinstalla automaticamente.

Uso:
    python update.py
"""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
STATE_FILE = ROOT / "backend" / ".setup-state"

# ── Rich opzionale ───────────────────────────────────────────────────────────

try:
    from rich.console import Console
    from rich.panel import Panel
    _rich = True
    console = Console()
except ImportError:
    _rich = False
    console = None  # type: ignore[assignment]


def _print(msg: str) -> None:
    if _rich:
        console.print(msg)  # type: ignore[union-attr]
    else:
        clean = re.sub(r"\[/?[^\]]*\]", "", msg)
        print(clean)


def _print_panel(title: str, body: str, style: str = "bright_blue") -> None:
    if _rich:
        console.print(Panel(body, title=f"[bold]{title}[/bold]", border_style=style))  # type: ignore[union-attr]
    else:
        print(f"\n{'='*50}\n  {title}\n{'='*50}\n{body}\n")


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


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


# ── Step 1: verifica git ──────────────────────────────────────────────────────

def check_git() -> bool:
    _print("\n[bold]Step 1 — Verifica repository git[/bold]")
    if not (ROOT / ".git").exists():
        _fail("Questa directory non è un repository git")
        return False

    r = _run(["git", "status", "--porcelain"], cwd=ROOT)
    if r.stdout.strip():
        _warn("Working tree non pulito — alcune modifiche locali potrebbero andare perse:")
        for line in r.stdout.strip().splitlines()[:5]:
            _print(f"    {line}")

    _ok("Repository git rilevato")
    return True


# ── Step 2: git pull ──────────────────────────────────────────────────────────

def git_pull() -> None:
    _print("\n[bold]Step 2 — git pull[/bold]")

    # Commit corrente prima del pull
    r = _run(["git", "rev-parse", "HEAD"], cwd=ROOT)
    old_commit = r.stdout.strip()

    _info("Eseguo git pull...")
    r = subprocess.run(["git", "pull"], cwd=ROOT)
    if r.returncode != 0:
        _warn("git pull terminato con errori — continuo comunque")
        return

    r = _run(["git", "rev-parse", "HEAD"], cwd=ROOT)
    new_commit = r.stdout.strip()

    if old_commit == new_commit:
        _skip("Nessuna modifica dal repository remoto")
        return

    _ok("Repository aggiornato")
    # Mostra i commit scaricati
    r = _run(["git", "log", "--oneline", f"{old_commit}..HEAD"], cwd=ROOT)
    if r.stdout.strip():
        _print("  Nuovi commit:")
        for line in r.stdout.strip().splitlines():
            _print(f"    [dim]{line}[/dim]")


# ── Step 3: requirements.txt ──────────────────────────────────────────────────

def update_backend(state: dict) -> dict:
    _print("\n[bold]Step 3 — Backend: dipendenze Python[/bold]")

    is_win = sys.platform == "win32"
    venv_dir = ROOT / "backend" / ".venv"
    pip_path = venv_dir / ("Scripts" if is_win else "bin") / ("pip" if not is_win else "pip.exe")
    req_file = ROOT / "backend" / "requirements.txt"

    if not venv_dir.exists():
        _warn("Virtualenv non trovato — esegui prima setup.py")
        return state

    req_hash = sha256_file(req_file)
    if req_hash == state.get("requirements_txt_hash"):
        _skip("requirements.txt invariato")
        return state

    _info("requirements.txt modificato — reinstallo dipendenze...")
    subprocess.run(
        [str(pip_path), "install", "-r", str(req_file), "--quiet"],
        check=True,
    )
    _ok("Dipendenze Python aggiornate")
    state["requirements_txt_hash"] = req_hash
    return state


# ── Step 4: package.json ──────────────────────────────────────────────────────

def update_frontend(state: dict) -> dict:
    _print("\n[bold]Step 4 — Frontend: dipendenze Node.js[/bold]")

    pkg_file = ROOT / "frontend" / "package.json"
    pkg_hash = sha256_file(pkg_file)

    if pkg_hash == state.get("package_json_hash"):
        _skip("package.json invariato")
        return state

    _info("package.json modificato — eseguo npm install...")
    subprocess.run(
        "npm install",
        cwd=ROOT / "frontend",
        shell=True,
        check=True,
    )
    _ok("Dipendenze Node.js aggiornate")
    state["package_json_hash"] = pkg_hash
    return state


# ── Step 5: graphhopper/config.yml ───────────────────────────────────────────

def check_graphhopper(state: dict) -> dict:
    _print("\n[bold]Step 5 — GraphHopper config[/bold]")

    cfg_file = ROOT / "graphhopper" / "config.yml"
    if not cfg_file.exists():
        _skip("config.yml non trovato")
        return state

    cfg_hash = sha256_file(cfg_file)
    if cfg_hash != state.get("graphhopper_config_hash"):
        _warn(
            "graphhopper/config.yml è stato modificato.\n"
            "  Il grafo di routing potrebbe richiedere una ricostruzione.\n"
            "  Per forzarla: cancella la cartella graphhopper/*-gh/ e riavvia."
        )
        state["graphhopper_config_hash"] = cfg_hash
    else:
        _skip("config.yml invariato")

    # Controlla se il JAR richiesto è cambiato
    start_py = ROOT / "start.py"
    if start_py.exists():
        m = re.search(r'"graphhopper-web-([\d.]+)\.jar"', start_py.read_text())
        if m:
            expected_jar = f"graphhopper-web-{m.group(1)}.jar"
            current_jar = state.get("jar_filename", "")
            if expected_jar != current_jar:
                jar_path = ROOT / "graphhopper" / expected_jar
                if not jar_path.exists():
                    _warn(
                        f"Il JAR richiesto è cambiato: {expected_jar}\n"
                        f"  JAR attuale: {current_jar or 'non registrato'}\n"
                        f"  Esegui setup.py per scaricarlo automaticamente."
                    )

    return state


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    _print_panel(
        "open-gpx — Update",
        "Aggiorna il repository e reinstalla le dipendenze modificate.",
    )

    if not check_git():
        sys.exit(1)

    state = load_state()
    if not state.get("setup_completed"):
        _warn("Setup non completato — esegui prima setup.py")

    git_pull()
    state = update_backend(state)
    state = update_frontend(state)
    state = check_graphhopper(state)

    save_state(state)

    _print("\n[bold green]Update completato.[/bold green]\n")


if __name__ == "__main__":
    main()
