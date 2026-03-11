# open-gpx

A self-hosted motorcycle route planner. Plan routes on an interactive map, tune them with road preference filters, discover mountain passes automatically, and export everything as GPX files — with no cloud subscriptions and no data leaving your machine.

## Features

- **Interactive map** — click to add waypoints, drag to reorder, drag markers to adjust position
- **Adventure level** — single slider (0–100) that shifts routing from motorways toward scenic, curvy backroads
- **Per-segment filters** — each leg of the route can have independent settings: avoid motorways/highways/primary roads, prefer unpaved or secondary roads
- **Extreme routing** — automatically finds mountain passes near a waypoint via OpenStreetMap, then routes through them; supports loop mode (lollipop), configurable radius, and cardinal direction filter
- **Pass selector** — cycle through available passes with `<` / `>` or pick one at random; shows pass name, elevation, and distance
- **Elevation profile** — chart of altitude along the route
- **Road type breakdown** — visual summary of road classes and surface types used
- **Address search** — autocomplete via Nominatim (OpenStreetMap geocoding, no API key)
- **GPX export** — compatible with Garmin, TwoNav, Komoot, and most GPS devices
- **Map layer switcher** — toggle base map and trail overlays
- **Dark / light theme** — persisted in localStorage
- **Bilingual UI** — Italian and English, persisted in localStorage
- **Offline capable** — once OSM data is imported, no internet connection required for routing

## Quick Start

> Never used a terminal before? No problem — just follow these steps in order and the app installs itself.
>
> You will need about **3 GB of free disk space**.

---

### Installation on macOS

**Step 1 — Install dependencies**

Open **Terminal** (find it with Spotlight: `Cmd + Space`, type "Terminal") and paste these commands one at a time:

```bash
# 1. Install Homebrew (macOS package manager)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install Python 3.12
brew install python@3.12

# 3. Install Java (OpenJDK)
brew install --cask temurin

# 4. Install Node.js
brew install node
```

> If Homebrew is already installed, skip the first command. If a tool is already installed, Homebrew will just tell you and you can move on.

**Step 2 — Download the project**

Download or clone this repository to your computer and note where you save it.

**Step 3 — Run the setup**

Open the `scripts/macos/` folder in Finder and double-click **`setup.command`**.

- If macOS blocks the file, go to *System Settings → Privacy & Security* and click *Open Anyway*.
- The script automatically downloads the map data, routing engine, and all dependencies.
- **The first run may take 15–30 minutes** depending on your connection.

When it finishes, the app opens automatically in your browser.

**To launch the app next time:** double-click `scripts/macos/start.command`.

---

### Installation on Windows

**Step 1 — Install dependencies**

Open **Command Prompt** or **PowerShell** as administrator (right-click the Start menu → *Terminal (Admin)*) and paste these commands one at a time:

```bat
:: 1. Install Python 3.12
winget install --id Python.Python.3.12 --source winget

:: 2. Install Java (Eclipse Temurin 21 LTS)
winget install --id EclipseAdoptium.Temurin.21.JDK --source winget

:: 3. Install Node.js LTS
winget install --id OpenJS.NodeJS.LTS --source winget
```

> `winget` is built into Windows 10 (2020 update) and Windows 11. If the command is not recognised, update Windows or install [App Installer](https://apps.microsoft.com/detail/9NBLGGH4NNS1) from the Microsoft Store.
>
> **After installation, close and reopen the terminal** so the new commands are available in your PATH.

**Step 2 — Download the project**

Download or clone this repository to your computer and note where you save it.

**Step 3 — Run the setup**

Open the `scripts\win\` folder in File Explorer and double-click **`setup.bat`**.

- If Windows shows a "PC protected" warning, click *More info → Run anyway*.
- The script automatically downloads the map data, routing engine, and all dependencies.
- **The first run may take 15–30 minutes** depending on your connection.

When it finishes, the app opens automatically in your browser.

**To launch the app next time:** double-click `scripts\win\start.bat`.

---

### Updating the app

Double-click `scripts/macos/update.command` (macOS) or `scripts\win\update.bat` (Windows).

---

## Screenshots

> Coming soon.

## Architecture

```
Browser (localhost:5173)
  └─ React + TypeScript + Leaflet
       └─ FastAPI (localhost:8000)
            ├─ GraphHopper (localhost:8989)       ← self-hosted routing engine
            ├─ Overpass API (overpass-api.de)     ← mountain pass lookup
            └─ Nominatim (openstreetmap.org)      ← address geocoding
```

All routing is computed locally by GraphHopper. Only geocoding and mountain pass queries hit external OpenStreetMap services.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 + TypeScript + Vite + Leaflet |
| Backend | Python 3.12 + FastAPI + uvicorn |
| Routing engine | GraphHopper 10.x (self-hosted JAR) |
| Elevation data | CGIAR SRTM tiles (auto-downloaded) |
| Geocoding | Nominatim (OpenStreetMap) |
| Mountain passes | Overpass API |
| State management | Zustand |
| Drag & drop | @dnd-kit |
| GPX generation | gpxpy |
| Dashboard launcher | Python `rich` |

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Java | 11 or newer | Required to run GraphHopper |
| Python | 3.12 | 3.13+ not yet supported by pydantic-core |
| Node.js | 18 or newer | Frontend build tooling |
| Disk space | ~3 GB | OSM data + routing graph for Italy |

## Setup (advanced / manual)

> The `setup.command` / `setup.bat` scripts handle everything below automatically. Follow this section only if you prefer a manual setup or need to troubleshoot.

### 1. Get the OSM data and GraphHopper JAR

Download an OSM extract for your region from [Geofabrik](https://download.geofabrik.de/) and place it inside the `graphhopper/` folder:

```bash
cd graphhopper

# Italy (~2 GB)
curl -LO https://download.geofabrik.de/europe/italy-latest.osm.pbf

# GraphHopper routing engine
curl -LO https://github.com/graphhopper/graphhopper/releases/download/10.0/graphhopper-web-10.0.jar
```

For a different region, update `datareader.file` in `graphhopper/config.yml` to match your `.osm.pbf` filename.

### 2. Set up the Python backend

```bash
cd backend
python3.12 -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Install frontend dependencies

```bash
cd frontend
npm install
```

## Running

### Windows

```bat
scripts\win\start.bat
```

If GraphHopper is already running, skip it with:

```bat
scripts\win\start.bat --no-gh
```

### macOS

```bash
scripts/macos/start.command
```

This launches GraphHopper, the FastAPI backend, and the Vite dev server in a single terminal with color-coded unified log output. Press `Ctrl+C` to stop all services.

### Manual start (any OS)

Open three separate terminals:

```bash
# Terminal 1 — GraphHopper
cd graphhopper
java -jar graphhopper-web-10.0.jar server config.yml
# First run: ~15 min to build the routing graph
# Subsequent runs: ~30 sec

# Terminal 2 — Backend
cd backend
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8000

# Terminal 3 — Frontend
cd frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

## How It Works

### Routing and adventure level

The adventure slider (0–100) controls GraphHopper's custom model in real time:

| Level | Behaviour |
|---|---|
| 0–30 | Fastest route; motorways and primary roads fully allowed |
| 30–60 | Motorways softly penalized; secondary roads preferred |
| 60–80 | Strong preference for secondary, tertiary, and curvy roads |
| 80–100 | Extreme scenic mode: motorways avoided entirely; gravel/dirt paths preferred; maximum curvature bonus |

Per-segment filter checkboxes override the adventure level for individual legs of the route.

### Extreme routing

Enable the **Extreme** toggle on any waypoint to force the route through a mountain pass near that leg:

1. The backend queries Overpass API for mountain passes and natural saddles above 800 m within the configured radius.
2. Passes are filtered by cardinal direction (N / S / E / O) if selected.
3. The route is recalculated through the best available pass.
4. Use `<` and `>` in the sidebar to cycle through alternative passes, or `?` for a random one.
5. Enable **Loop** to generate a lollipop route: the path goes up to the pass, continues 2 km beyond it, loops back to the departure point, then proceeds to the destination.

The **Extreme Log** panel shows the result for each segment: pass name, elevation, distance, and whether the pass was used or was unreachable.

### GPX export

Click **Export GPX** in the sidebar to download the current route as a standard GPX file. The file includes waypoints and the full track and is compatible with Garmin devices, TwoNav, Komoot import, and most navigation apps.

## API Reference

All endpoints are exposed by the FastAPI backend at `http://localhost:8000`.

### `POST /api/route`

Calculate a multi-segment route.

**Request body**

```json
{
  "waypoints": [
    { "lat": 45.4654, "lng": 9.1859 },
    { "lat": 46.0664, "lng": 11.1218 }
  ],
  "adventure": 70,
  "segment_options": [
    {
      "adventure": 70,
      "avoid_motorways": true,
      "avoid_highways": false,
      "avoid_primary": false,
      "prefer_unpaved": false,
      "prefer_secondary": true,
      "extreme": false,
      "extreme_radius_km": 30,
      "extreme_direction": null,
      "extreme_loop": false,
      "extreme_pass_index": 0
    }
  ]
}
```

**Response**

```json
{
  "distance_m": 185400,
  "duration_s": 9120,
  "geometry": [[45.4654, 9.1859], ...],
  "elevation": [{ "d": 0.0, "ele": 122 }, ...],
  "max_elevation": 2108,
  "min_elevation": 122,
  "road_stats": {
    "road_class": { "secondary": 0.45, "tertiary": 0.30, "primary": 0.25 },
    "surface": { "asphalt": 0.80, "gravel": 0.20 }
  },
  "extreme_log": [
    {
      "segment": 0,
      "name": "Passo Tonale",
      "lat": 46.2567,
      "lng": 10.5789,
      "ele": 1883,
      "ctd_m": 24500,
      "status": "used",
      "mode": "route",
      "passes_found": 3
    }
  ]
}
```

### `GET /api/geocode?q=<query>`

Search for an address using Nominatim. Returns a list of candidates with `lat`, `lng`, and `display_name`.

### `POST /api/export/gpx`

Export the current route as a GPX file. Accepts the same geometry array returned by `/api/route`.

### `GET /api/health`

Returns `{ "status": "ok" }`. Useful for readiness checks.

## Project Structure

```
open-gpx/
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py                 # FastAPI entry point, CORS, routers
│       ├── config.py               # Settings (GraphHopper URL via env)
│       ├── routers/
│       │   ├── routing.py          # POST /api/route — Pydantic models + handler
│       │   ├── geocoding.py        # GET /api/geocode
│       │   └── export.py           # POST /api/export/gpx
│       └── services/
│           ├── graphhopper.py      # Custom model builder + routing logic
│           ├── overpass.py         # Mountain pass lookup via Overpass API
│           ├── nominatim.py        # Geocoding proxy
│           └── gpx_builder.py      # GPX file generation
├── frontend/
│   └── src/
│       ├── types/index.ts          # Shared TypeScript types
│       ├── api/                    # Fetch wrappers
│       ├── store/                  # Zustand stores (route, theme, i18n, map)
│       ├── hooks/                  # useRouteCalculation, useGeocoding
│       ├── i18n/                   # IT/EN translations
│       └── components/
│           ├── Sidebar/            # Waypoint list, filters, stats, export
│           └── MapView/            # Leaflet map, markers, polyline, extreme circles
├── graphhopper/
│   ├── config.yml                  # GraphHopper configuration
│   ├── graphhopper-web-10.0.jar    # Routing engine (download separately)
│   └── italy-latest.osm.pbf        # OSM data (download separately)
└── scripts/
    ├── setup.py                    # First-time setup (installs all dependencies)
    ├── start.py                    # Unified launcher (GraphHopper + backend + frontend)
    ├── update.py                   # Updater (git pull + dependency sync)
    ├── download_elevation.py       # SRTM elevation tile downloader
    ├── macos/
    │   ├── setup.command           # Double-click to install (macOS)
    │   ├── start.command           # Double-click to launch (macOS)
    │   ├── update.command          # Double-click to update (macOS)
    │   ├── stop.command            # Stop all services (macOS)
    │   └── download_elevation.command
    └── win/
        ├── setup.bat               # Double-click to install (Windows)
        ├── start.bat               # Double-click to launch (Windows)
        ├── update.bat              # Double-click to update (Windows)
        ├── stop.bat                # Stop all services (Windows)
        ├── download_elevation.bat
        └── test.bat                # API smoke tests (developer tool)
```

## Configuration

### GraphHopper (`graphhopper/config.yml`)

The key settings are:

```yaml
graphhopper:
  datareader.file: italy-latest.osm.pbf   # path to your OSM extract
  graph.location: italy-gh                 # routing graph cache directory
  profiles:
    - name: motorcycle
      custom_model_files: [car.json]
  graph.encoded_values: car_access, car_average_speed, toll, road_class,
                        road_environment, curvature, surface, max_speed
  graph.elevation.provider: cgiar
  graph.elevation.cache_dir: elevation-cache
  import.osm.ignored_highways: footway, cycleway, path, pedestrian, steps
```

`profiles_ch: []` disables Contraction Hierarchies so that the custom model (adventure level) can be applied dynamically per request.

### Backend environment (`.env`)

Copy `backend/.env.example` to `backend/.env` and adjust if GraphHopper runs on a non-default port:

```
GRAPHHOPPER_URL=http://localhost:8989
```

## Using a Different Region

1. Download the `.osm.pbf` file for your region from [Geofabrik](https://download.geofabrik.de/).
2. Place it in `graphhopper/`.
3. Update `datareader.file` in `graphhopper/config.yml`.
4. Delete the old `graphhopper/italy-gh/` cache directory if it exists.
5. Start GraphHopper — the graph will be rebuilt on first run.

## Troubleshooting

**GraphHopper does not start**
- Verify Java is installed: `java -version`
- Check that the `.osm.pbf` file exists and is not corrupted

**No route is calculated**
- Open the browser console and look for network errors on `/api/route`
- Confirm GraphHopper is running: `curl http://localhost:8989/health`
- Confirm the backend is running: `curl http://localhost:8000/api/health`

**Extreme routing finds no passes**
- Increase the search radius slider
- Remove the direction filter
- The area may not have tagged mountain passes in OpenStreetMap

**Elevation profile is empty**
- GraphHopper requires elevation data to be pre-cached; run `scripts/download_elevation.py` for your bounding box or let GraphHopper download tiles automatically on first routing request

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

- [GraphHopper](https://github.com/graphhopper/graphhopper) — open-source routing engine
- [OpenStreetMap](https://www.openstreetmap.org/) — map data and geocoding
- [Nominatim](https://nominatim.org/) — address search
- [Overpass API](https://overpass-api.de/) — OpenStreetMap data queries
- [react-leaflet](https://react-leaflet.js.org/) — map rendering for React
- [gpxpy](https://github.com/tkrajina/gpxpy) — GPX file handling
