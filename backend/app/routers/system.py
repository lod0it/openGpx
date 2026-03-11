import asyncio
import logging
import sys
import time
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()
log = logging.getLogger("opengpx")

# backend/app/routers -> backend/app -> backend -> project root
ROOT = Path(__file__).parent.parent.parent.parent

_HEARTBEAT_TIMEOUT = 30   # secondi senza heartbeat → shutdown
_HEARTBEAT_CHECK   = 10   # ogni quanti secondi controlla
SHUTDOWN_FLAG      = ROOT / ".shutdown_requested"

_last_heartbeat: float | None = None   # None = nessun browser mai connesso


@router.post("/system/heartbeat")
async def heartbeat():
    global _last_heartbeat
    _last_heartbeat = time.monotonic()
    return {"ok": True}


async def heartbeat_monitor() -> None:
    """Task asyncio avviato al boot: scrive il flag di shutdown se il browser si disconnette."""
    global _last_heartbeat
    while True:
        await asyncio.sleep(_HEARTBEAT_CHECK)
        if _last_heartbeat is None:
            continue  # aspetta la prima connessione
        elapsed = time.monotonic() - _last_heartbeat
        if elapsed > _HEARTBEAT_TIMEOUT:
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
