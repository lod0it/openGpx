#!/usr/bin/env python3
"""
Scarica le tile SRTM (CGIAR v4.1) per l'Italia e le posiziona
nella cartella elevation-cache di GraphHopper.

Uso:
    python scripts/download_elevation.py
    python scripts/download_elevation.py --check   # verifica solo, non scarica

Dopo il download:
    1. Cancella la cartella  graphhopper/italy-gh/
    2. Riavvia GraphHopper  (java -jar graphhopper-web-10.0.jar server config.yml)
    3. Attendi il re-import (~15-30 min) — questa volta con quota 3D
"""

import argparse
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# ── Configurazione ───────────────────────────────────────────────────────────

ROOT       = Path(__file__).parent.parent
CACHE_DIR  = ROOT / "graphhopper" / "elevation-cache"

# CGIAR SRTM V4.1 — stesso URL usato da GraphHopper internamente
CGIAR_BASE = "https://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF"

# Mirror di backup (OpenTopography CDN)
MIRROR_BASE = "https://opentopography.s3.sdsc.edu/raster/SRTM_GL3/SRTM_GL3_srtm"

# Tile CGIAR che coprono l'Italia (5°x5° ciascuna):
#   Colonne 38-40 → longitudine  5-20°E
#   Righe    3- 5 → latitudine  35-50°N
ITALY_TILES = [
    (38, 3), (38, 4), (38, 5),
    (39, 3), (39, 4), (39, 5),
    (40, 3), (40, 4), (40, 5),
]

# ── Helper ────────────────────────────────────────────────────────────────────

def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def log(msg: str, level: str = "INFO") -> None:
    print(f"{ts()} [{level:5s}] {msg}", flush=True)


def format_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"


def download_file(url: str, dest: Path) -> bool:
    """Scarica url → dest con progress a console. Ritorna True se ok."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "open-gpx/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            chunk = 65536
            with open(dest, "wb") as f:
                while True:
                    data = resp.read(chunk)
                    if not data:
                        break
                    f.write(data)
                    downloaded += len(data)
                    if total:
                        pct = downloaded / total * 100
                        print(f"\r    {format_bytes(downloaded)} / {format_bytes(total)}  ({pct:.0f}%)", end="", flush=True)
            print()  # newline dopo progress
        return True
    except urllib.error.HTTPError as e:
        print()
        log(f"HTTP {e.code} per {url}", "WARN")
        return False
    except Exception as e:
        print()
        log(f"Errore: {e}", "WARN")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Download tile SRTM per l'Italia")
    parser.add_argument("--check", action="store_true", help="Mostra lo stato senza scaricare")
    args = parser.parse_args()

    print()
    print("=" * 60)
    print("  open-gpx — Download tile elevazione SRTM per l'Italia")
    print("=" * 60)
    print(f"  Cartella di destinazione: {CACHE_DIR}")
    print(f"  Tile da scaricare: {len(ITALY_TILES)}")
    print()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    missing = []
    present = []
    for col, row in ITALY_TILES:
        name = f"srtm_{col:02d}_{row:02d}.zip"
        dest = CACHE_DIR / name
        if dest.exists() and dest.stat().st_size > 100_000:
            present.append((name, dest.stat().st_size))
        else:
            missing.append((col, row, name, dest))

    # Stato attuale
    if present:
        log(f"Tile già presenti ({len(present)}/{len(ITALY_TILES)}):")
        for name, size in present:
            print(f"    [ok] {name}  ({format_bytes(size)})")
    if missing:
        log(f"Tile mancanti: {len(missing)}")
        for col, row, name, _ in missing:
            print(f"    [ ] {name}")
    print()

    if not missing:
        log("Tutte le tile sono già presenti.")
        print()
        _print_next_steps()
        return

    if args.check:
        log("Modalità --check: nessun download eseguito.")
        return

    # Download
    ok = 0
    fail = 0
    for col, row, name, dest in missing:
        cgiar_url  = f"{CGIAR_BASE}/{name}"
        log(f"Download {name} ...")
        print(f"    URL: {cgiar_url}")

        # Tenta CGIAR prima
        success = download_file(cgiar_url, dest)

        if not success:
            # Rimuovi file parziale
            if dest.exists():
                dest.unlink()
            log(f"{name} non scaricato da CGIAR.", "WARN")
            log("Il server CGIAR potrebbe essere offline. Vedi sezione ALTERNATIVA.", "WARN")
            fail += 1
            continue

        size = dest.stat().st_size
        log(f"OK  {name}  ({format_bytes(size)})", "OK")
        ok += 1

    print()
    print("=" * 60)
    print(f"  Completato: {ok} scaricati, {fail} falliti")
    print("=" * 60)
    print()

    if fail > 0:
        _print_alternative()
    else:
        _print_next_steps()


def _print_next_steps() -> None:
    gh_dir = ROOT / "graphhopper"
    graph_dir = gh_dir / "italy-gh"
    print("PROSSIMI PASSI")
    print("-" * 40)
    print("1. Cancella il grafo esistente (necessario per re-import con quota):")
    print()
    print(f"     rmdir /s /q \"{graph_dir}\"")
    print()
    print("2. Riavvia GraphHopper (import ~15-30 minuti):")
    print()
    print(f"     cd \"{gh_dir}\"")
    print(f"     java -jar graphhopper-web-10.0.jar server config.yml")
    print()
    print("3. Quando GH è pronto (log: 'Started server'), riavvia il Backend")
    print("   e ricalcola un percorso: il profilo altimetrico sarà disponibile.")
    print()


def _print_alternative() -> None:
    cache = CACHE_DIR
    print("ALTERNATIVA — Download manuale")
    print("-" * 40)
    print("Il server CGIAR è offline. Scarica le tile manualmente da:")
    print()
    print("  https://www.dropbox.com/sh/r7jt24tkb5vxke4/AAAiI2gOI2w4_fORgp1N1LqNa")
    print("  oppure cerca 'CGIAR SRTM V4.1' su Google per mirror aggiornati.")
    print()
    print(f"Posiziona i file .zip in: {cache}")
    print()
    tile_names = [f"srtm_{col:02d}_{row:02d}.zip" for col, row, _, _ in
                  [(c, r, '', Path()) for c, r in ITALY_TILES]]
    print("File necessari:")
    for t in tile_names:
        print(f"  - {t}")
    print()
    print("Poi esegui di nuovo questo script per verificare:")
    print("  python scripts/download_elevation.py --check")
    print()


if __name__ == "__main__":
    main()
