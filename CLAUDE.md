# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

open-gpx: a self-hosted motorcycle route planner. Three local services: GraphHopper (Java JAR, :8989) → FastAPI backend (:8000) → React/Vite frontend (:5173, proxies `/api` to :8000 via `frontend/vite.config.ts`). Only geocoding (Nominatim) and mountain-pass lookup (Overpass) call external services. See `README.md` for the user-facing docs and API reference, and `docs/open-gpx.md` for technical detail.

## Conventions

- All project files (code, comments, docs, README) must be in **English only**, even though conversation with the user may be in Italian. Some existing backend log strings/comments are still Italian; don't add more.
- Repo root stays clean: no `.py` or `.bat` files at root. All Python scripts live in `scripts/`; platform launchers in `scripts/macos/*.command` and `scripts/win/*.bat` (same set on both platforms, except `scripts/win/test.bat`, a Windows-only API smoke-test tool).
- Scripts in `scripts/` resolve the repo root with `ROOT = Path(__file__).parent.parent`.

## Commands

There is no automated test suite.

```bash
# Full stack (GraphHopper + backend + frontend, unified log dashboard)
python scripts/start.py            # add --no-gh if GraphHopper is already running
python scripts/setup.py            # first-time install (venv, npm, JAR, OSM data)
python scripts/update.py           # git pull + dependency sync

# Backend only (from backend/, with backend/.venv activated; Python 3.12 — 3.13+ breaks pydantic-core)
uvicorn app.main:app --reload --port 8000

# Frontend only (from frontend/)
npm run dev
npm run build      # tsc -b && vite build
npm run lint       # eslint

# GraphHopper only (from graphhopper/)
java -jar graphhopper-web-10.0.jar server config.yml
```

The GraphHopper JAR and `.osm.pbf` are gitignored and downloaded by `setup.py`. First GraphHopper start builds the routing graph (~15 min). Health checks: `curl localhost:8989/health`, `curl localhost:8000/api/health`.

## Architecture

### Route calculation (backend, `backend/app/services/graphhopper.py`)
`get_route()` is the core. It routes **leg by leg** (waypoint i → i+1), each with its own `SegmentOptions` (adventure level + avoid/prefer filters + extreme settings), and stitches the results:
- `build_custom_model(adventure, filters)` builds a GraphHopper *custom model* per request. This only works because `graphhopper/config.yml` sets `profiles_ch: []` (Contraction Hierarchies disabled). Don't re-enable CH.
- **Extreme mode**: `overpass.fetch_passes_around()` finds mountain passes around the leg's start (filtered by radius and cardinal direction). Passes are tried in circular order starting at `extreme_pass_index`; if GraphHopper returns `PointNotFoundException` the pass is logged `unreachable` and the next is tried. Loop mode routes `start → pass → nudge-past-pass → start → end` (lollipop). If no pass works, it falls back to a plain start→end route.
- Geometry, elevation profile, road-class/surface percentages and the `extreme_log` are aggregated across legs; the first point of every leg after the first is dropped to avoid duplicates.
- Pydantic request/response models live in `routers/routing.py`; the frontend mirrors them in `frontend/src/types/index.ts` — keep both in sync when changing the API shape.

### Frontend
- State is in Zustand stores (`frontend/src/store/`: route, map, theme, i18n). `hooks/useRouteCalculation.ts` triggers `/api/route` from waypoint/option changes; `api/*.ts` are thin fetch wrappers.
- UI text is bilingual (IT/EN) via `i18n/translations.ts` + `useT`; add both languages for any new string.
- Components are split into `Sidebar/` (controls, stats) and `MapView/` (Leaflet layers); styles are CSS modules next to each component.

### Process lifecycle (spans backend + scripts)
The browser POSTs `/api/system/heartbeat` (`hooks/useHeartbeat.ts`). `heartbeat_monitor` in `backend/app/routers/system.py` writes `<repo>/.shutdown_requested` if heartbeats stop for 30 s; `scripts/start.py` watches that flag and tears down all services. `GET /api/system/update` runs the updater as a subprocess and streams output over SSE (used by `UpdateButton`).
### Launchers
`scripts/macos/*.command` and `scripts/win/*.bat` are thin wrappers around the `scripts/*.py` files. On macOS the launchers use a private venv to satisfy PEP 668 and always ensure `rich` is importable before running `start.py`/`setup.py`.
