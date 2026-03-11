# open-gpx — Technical Documentation

## Overview

open-gpx is a fully self-hosted motorcycle route planner. It consists of three services that run locally on the user's machine:

| Service | Default port | Technology |
|---|---|---|
| GraphHopper | 8989 | Routing engine (Java JAR) |
| FastAPI backend | 8000 | API layer (Python) |
| Vite dev server | 5173 | React frontend (Node.js) |

All three services are managed by `start.py`, a single Python launcher that streams their log output to a unified, color-coded terminal dashboard.

---

## Data Flow

```
User interaction (click / drag / filter change)
  → useRouteCalculation hook (300 ms debounce)
    → fetchRoute() in api/routing.ts
      → POST /api/route (FastAPI)
        → get_route() in services/graphhopper.py
          → for each segment:
              build_custom_model(options) → custom_model JSON
              [if extreme] fetch_passes_around() → Overpass API
              _call_graphhopper(waypoints, custom_model) → GraphHopper /route
          → concatenate segments
          → aggregate road_stats, elevation profile
        → RouteResponse
      → update useRouteStore (Zustand)
        → MapView re-renders polyline + circles
        → Sidebar re-renders stats + charts
```

---

## Backend

### `app/main.py`

Entry point for FastAPI. Sets up:
- A custom logger `opengpx` writing to `sys.stdout` (visible with `uvicorn --reload`)
- CORS for `localhost:5173` and `127.0.0.1:5173`
- Router includes for `/api/route`, `/api/geocode`, `/api/export/gpx`
- Health check at `GET /api/health`
- Optional static file serving of `frontend/dist` for production builds

### `app/routers/routing.py`

Defines Pydantic models and the main `POST /api/route` endpoint.

**Models:**

```
Waypoint          lat, lng
SegmentOptions    adventure, avoid_motorways, avoid_highways, avoid_primary,
                  prefer_unpaved, prefer_secondary,
                  extreme, extreme_radius_km, extreme_direction,
                  extreme_loop, extreme_pass_index
RouteRequest      waypoints[], adventure, segment_options[]
ElevationPoint    d (km), ele (m)
RoadStats         road_class{}, surface{}
ExtremeLogEntry   segment, name, lat, lng, ele, ctd_m, status, mode, passes_found
RouteResponse     distance_m, duration_s, geometry, elevation[],
                  max_elevation, min_elevation, road_stats, extreme_log[]
```

### `app/services/graphhopper.py`

Core routing logic. The two main responsibilities are:

#### 1. Custom model building (`build_custom_model`)

GraphHopper supports per-request custom models that re-weight roads at query time (CH must be disabled). The function maps user options to a JSON custom model:

| Input | Effect on custom model |
|---|---|
| `adventure` 0–100 | Linear/quadratic penalty on MOTORWAY and TRUNK; bonus on SECONDARY/TERTIARY |
| `adventure >= 30` | Penalty on PRIMARY |
| `adventure >= 60` | Curvature bonus (curved > straight) |
| `adventure >= 80` | Severe motorway/trunk avoidance; `distance_influence=250` |
| `avoid_motorways=True` | Hard-avoid MOTORWAY |
| `avoid_highways=True` | Hard-avoid TRUNK |
| `avoid_primary=True` | Hard-avoid PRIMARY |
| `prefer_unpaved=True` | 2× priority multiplier on GRAVEL, DIRT, GROUND, GRASS |
| `prefer_secondary=True` | Extra bonus on SECONDARY |
| `extreme=True` | All of the above maximized; forces maximum curvature weighting |

#### 2. Route assembly (`get_route`)

For each consecutive pair of waypoints (a "segment"):
1. Select the `SegmentOptions` for that segment (falls back to global adventure if none set)
2. Build the custom model
3. If `extreme=True`:
   a. Call `fetch_passes_around(seg_start, radius_km, direction)` → list of passes
   b. Rotate the list by `extreme_pass_index` (circular)
   c. For each pass candidate:
      - If `extreme_loop=True`: route `[seg_start → pass → nudge_2km_past_pass → seg_start → seg_end]`
      - Else: route `[seg_start → pass → seg_end]`
      - If GraphHopper raises `PointNotFoundException`, mark as `unreachable` and try next
   d. Append `ExtremeLogEntry` to the log
4. Else: route `[seg_start → seg_end]` directly
5. Concatenate geometry (skip first point of each subsequent segment to avoid duplicates)
6. Aggregate `road_class%` and `surface%` across all segments
7. Sum `distance_m` and `duration_s`
8. Build elevation profile from GraphHopper 3D coordinates

**Helper functions:**

```python
_haversine_m(a, b)            # great-circle distance in metres
_nudge_toward(start, end, m)  # point `m` metres along start→end bearing
_nudge_past_pass(start, pass, m)  # point `m` metres beyond pass (away from start)
_call_graphhopper(points, model)  # POST to GraphHopper /route, returns raw response
```

### `app/services/overpass.py`

Queries the Overpass API for mountain passes near a given point.

- Tags searched: `mountain_pass=yes` or `natural=saddle` with an `ele` tag
- Elevation threshold: **800 m** (lower passes are discarded)
- Timeout: 8 s
- Max candidates returned: 3 (sorted by distance from `center`)
- Direction filter: bearing from `center` to pass must fall within ±45° of the requested cardinal direction

Direction bearings:
- N: 315–45° (wraps around 0°)
- E: 45–135°
- S: 135–225°
- O (West): 225–315°

---

## Frontend

### State management

All route state lives in `useRouteStore` (Zustand):

```
waypoints[]          ordered list of Waypoint objects
geometry[]           [[lat, lng], ...] from last successful route
distanceM            total route distance
durationS            total estimated duration
adventure            global adventure level (0–100)
segmentOptions{}     map of waypoint ID → SegmentOptions overrides
globalFilters        fallback filters applied to all segments
elevation[]          ElevationPoint[] for elevation chart
maxElevation         peak elevation on route
minElevation         lowest elevation on route
roadStats            road class and surface percentages
extremeLog[]         ExtremeLogEntry[] for the log panel
isLoading            true while fetch is in progress
error                error message or null
```

Persistent stores:
- `useThemeStore` — dark/light theme, synced to `document.documentElement` attribute
- `useI18nStore` — active language (IT/EN), translated via `useT()` hook
- `useMapStore` — active base layer and trail overlay selection

### Route calculation hook (`useRouteCalculation`)

- Debounces re-routing to 300 ms after any waypoint or filter change
- Skips calculation if fewer than 2 waypoints are set
- Sets `isLoading` before the fetch and clears it on completion or error

### Key components

| Component | Purpose |
|---|---|
| `MapView.tsx` | Leaflet map container; composes all map sub-components |
| `MapClickHandler.tsx` | Adds a new waypoint on map click |
| `WaypointMarkers.tsx` | Draggable numbered markers; drag updates position in store |
| `RoutePolyline.tsx` | Renders the route geometry as a Leaflet polyline |
| `ExtremeCircles.tsx` | Renders orange radius circles for each waypoint with `extreme=true` |
| `MapPanel.tsx` | Collapsible panel (right side) for base map / overlay switcher |
| `Sidebar.tsx` | Left panel; composes search, waypoint list, filters, stats, export |
| `WaypointList.tsx` | Drag-and-drop reorderable list via @dnd-kit |
| `WaypointItem.tsx` | Single waypoint row: `::` drag handle, `opt` settings toggle, `x` delete |
| `GlobalFilters.tsx` | Checkboxes that apply to all segments |
| `SegmentOptions.tsx` | Per-waypoint filter panel; includes Extreme section with pass selector |
| `AdventureSlider.tsx` | 0–100 range input for adventure level |
| `RouteStats.tsx` | Distance and duration summary |
| `RoadTypeBreakdown.tsx` | Pie/bar visualization of road class and surface percentages |
| `ElevationChart.tsx` | SVG line chart of elevation over distance |
| `ExtremeLog.tsx` | Table of pass attempts: name, elevation, distance, status |
| `ExportButtons.tsx` | Calls `/api/export/gpx` and triggers file download |

### Pass selector (inside `SegmentOptions.tsx`)

After a successful extreme route calculation, `ExtremeLogEntry.passes_found` tells the UI how many passes were found. The pass selector displays:

```
< [index of M] > ?
```

- `<` / `>` decrement/increment `extreme_pass_index` with circular wrap
- `?` sets a random index
- Changing the index triggers a new route calculation via the debounced hook

### Internationalization

Translations live in `frontend/src/i18n/translations.ts` as a flat key–value map for each locale (`it`, `en`). The `useT()` hook returns a translation function bound to the active language from `useI18nStore`.

---

## Launcher (`start.py`)

`start.py` at the project root launches all three services as subprocesses and streams their output into a single terminal.

- Uses the `rich` library for formatted log output (auto-installed if missing)
- Prefixes each log line with `[GH]`, `[BE]`, or `[FE]` and the timestamp
- Colors log levels: DEBUG grey, INFO white, WARNING yellow, ERROR/CRITICAL red
- Performs prerequisite checks before starting:
  - Java is available in PATH
  - `backend/.venv` exists
  - `frontend/node_modules` exists
- `--no-gh` flag skips GraphHopper startup (useful if it is already running)
- Ctrl+C sends `SIGTERM` to all child processes and waits for them to exit

---

## GraphHopper configuration

`graphhopper/config.yml` contains the full GraphHopper configuration. Key points:

- `profiles_ch: []` — Contraction Hierarchies disabled. Required for dynamic custom models. Routes take slightly longer to compute (~1–3 s) but custom weighting works per request.
- `graph.encoded_values` — includes `curvature` and `surface`, which are used by the custom model builder for adventure-level tuning.
- `graph.elevation.provider: cgiar` — uses CGIAR SRTM 90 m elevation data. Tiles are downloaded automatically on demand and cached in `elevation-cache/`.
- `import.osm.ignored_highways` — footways, cycleways, and pedestrian paths are excluded from the graph.

---

## Development notes

### Adding a new routing filter

1. Add the field to `SegmentOptions` in `frontend/src/types/index.ts`
2. Add the field to the `SegmentOptions` Pydantic model in `backend/app/routers/routing.py`
3. Use it in `build_custom_model()` in `backend/app/services/graphhopper.py`
4. Add the UI control in `frontend/src/components/Sidebar/SegmentOptions.tsx`
5. Add translation keys in `frontend/src/i18n/translations.ts`

### Adding a new map layer

1. Add the layer URL and name to `useMapStore.ts`
2. Add the toggle button in `MapPanel.tsx`
3. Apply the layer in `MapView.tsx`

### Running in production

Build the frontend:

```bash
cd frontend && npm run build
```

The FastAPI backend will automatically serve `frontend/dist` as static files (configured in `app/main.py`). Point a reverse proxy (nginx, Caddy) at port 8000 for external access.
