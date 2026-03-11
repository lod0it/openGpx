import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.routers import routing, geocoding, export, system
from app.routers.system import heartbeat_monitor, SHUTDOWN_FLAG

# Logger dedicato (visibile anche con uvicorn --reload su Windows)
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s"))
_log = logging.getLogger("opengpx")
_log.addHandler(_handler)
_log.setLevel(logging.INFO)
_log.propagate = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Rimuovi flag residuo da sessioni precedenti
    SHUTDOWN_FLAG.unlink(missing_ok=True)
    asyncio.create_task(heartbeat_monitor())
    yield


app = FastAPI(title="open-gpx", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routing.router, prefix="/api")
app.include_router(geocoding.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(system.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Serve built frontend in production (optional, used with `npm run build`)
frontend_dist = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
