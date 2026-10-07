import asyncio
import logging
import sys
import time
from pathlib import Path

import httpx
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.config import settings

router = APIRouter()
log = logging.getLogger("opengpx")

# backend/app/routers -> backend/app -> backend -> project root
ROOT = Path(__file__).parent.parent.parent.parent

_HEARTBEAT_TIMEOUT = 30   # secondi senza heartbeat → shutdown
_HEARTBEAT_CHECK   = 10   # ogni quanti secondi controlla
_FIRST_HEARTBEAT_TIMEOUT = 300   # secondi di attesa del primo heartbeat → shutdown
SHUTDOWN_FLAG      = ROOT / ".shutdown_requested"

_last_heartbeat: float | None = None   # None = nessun browser mai connesso


async def _graphhopper_state() -> str:
    """Probe di GraphHopper: "ready" oppure "starting"."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get(f"{settings.graphhopper_url}/health")
        if r.status_code == 200:
            return "ready"
    except httpx.HTTPError as e:
        log.debug("GraphHopper non raggiungibile: %s", e)
    return "starting"


@router.get("/system/status")
async def status():
    """Riporta lo stato del backend e la readiness di GraphHopper."""
    return {"backend": "ok", "graphhopper": await _graphhopper_state()}


@router.post("/system/heartbeat")
async def heartbeat():
    global _last_heartbeat
    _last_heartbeat = time.monotonic()
    return {"ok": True}


async def heartbeat_monitor() -> None:
    """Task asyncio avviato al boot: scrive il flag di shutdown se il browser si disconnette."""
    started = time.monotonic()
    while True:
        await asyncio.sleep(_HEARTBEAT_CHECK)
        if _last_heartbeat is None:
            waited = time.monotonic() - started
            if waited <= _FIRST_HEARTBEAT_TIMEOUT:
                continue  # aspetta la prima connessione
            log.info("Nessun browser connesso dopo %.0fs → shutdown", waited)
        else:
            elapsed = time.monotonic() - _last_heartbeat
            if elapsed <= _HEARTBEAT_TIMEOUT:
                continue
            if await _graphhopper_state() == "starting":
                continue  # build del grafo in corso: non interromperlo
            log.info("Browser disconnesso (heartbeat timeout %.0fs) → shutdown", elapsed)
        try:
            SHUTDOWN_FLAG.write_text("1")
        except Exception as e:
            log.error("Impossibile scrivere shutdown flag: %s", e)
        break


@router.get("/system/update")
async def run_update() -> StreamingResponse:
    """Esegue update.py come subprocess e streama l'output via SSE."""

    async def generate():
        env = {"COLUMNS": "100", "PYTHONUNBUFFERED": "1"}
        import os
        full_env = {**os.environ, **env}

        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            str(ROOT / "update.py"),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=ROOT,
            env=full_env,
        )

        assert proc.stdout is not None
        async for raw in proc.stdout:
            line = raw.decode("utf-8", errors="replace").rstrip()
            if line:
                yield f"data: {line}\n\n"

        await proc.wait()
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
