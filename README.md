# open-gpx

A self-hosted motorcycle GPX route planner — a local alternative to web paid services 

Plan routes on an interactive map, export them as GPX files, and run everything locally with no external paid APIs.

## Features

- Interactive map with clickable waypoints (add, drag, reorder, remove)
- Automatic route calculation between waypoints via self-hosted GraphHopper
- Motorcycle-optimized routing (avoids motorways, prefers scenic roads)
- GPX export for GPS devices and navigation apps (Garmin, TwoNav, etc.)
- Address search via Nominatim (OpenStreetMap geocoding)
- Fully offline-capable once OSM data is imported

## Screenshots


## Architecture

```
Browser (localhost:5173)
  └─ React + Leaflet UI
       └─ FastAPI (localhost:8000)   ← /api/route, /api/geocode, /api/export/gpx
            ├─ GraphHopper (localhost:8989)  ← local routing engine
            └─ Nominatim (nominatim.openstreetmap.org)  ← geocoding
```

## Tech Stack

| Layer      | Technology                             |
|------------|----------------------------------------|
| Frontend   | React 18 + TypeScript + Vite + Leaflet |
| Backend    | Python 3.12 + FastAPI + uvicorn        |
| Routing    | GraphHopper 10.x (local JAR)           |
| Map tiles  | OpenStreetMap                          |
| Geocoding  | Nominatim                              |
| State      | Zustand                                |
| Drag & drop| @dnd-kit                               |
| GPX export | gpxpy                                  |

## Prerequisites

- **Java 11+** (for GraphHopper)
- **Python 3.12** (not 3.13+, pydantic-core wheels not yet available)
- **Node.js 18+** and npm
- ~3 GB free disk space (OSM data + routing graph)

## Setup

### 1. Download GraphHopper and OSM data

```bash
mkdir -p ~/graphhopper-data
cd ~/graphhopper-data

# Download GraphHopper JAR
curl -LO https://github.com/graphhopper/graphhopper/releases/download/10.0/graphhopper-web-10.0.jar

# Download OSM data for Italy (adjust region as needed)
curl -LO https://download.geofabrik.de/europe/italy-latest.osm.pbf
# ~2 GB — check progress: watch -n3 "stat -f%z italy-latest.osm.pbf | awk '{printf \"%dMB\n\", \$1/1024/1024}'"
```

### 2. Create GraphHopper config

Create `~/graphhopper-data/config.yml`:

```yaml
graphhopper:
  datareader.file: italy-latest.osm.pbf
  graph.location: italy-gh

  profiles:
    - name: motorcycle
      custom_model_files: [car.json]

  profiles_ch: []

  graph.encoded_values: car_access, car_average_speed, toll, road_class, road_environment

  import.osm.ignored_highways: footway, cycleway, path, pedestrian, steps

server:
  application_connectors:
    - type: http
      port: 8989
  admin_connectors:
    - type: http
      port: 8990
```

### 3. Start GraphHopper

```bash
cd ~/graphhopper-data
java -jar graphhopper-web-10.0.jar server config.yml
# First run: ~15 min to import OSM data → builds italy-gh/ cache
# Subsequent runs: ~30 sec
```

Verify it's ready:
```bash
curl http://localhost:8989/health
```

### 4. Install backend dependencies

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 5. Install frontend dependencies

```bash
cd frontend
npm install
```

## Running

### macOS — one-click start

Double-click `start.command` to launch all three services and open the browser automatically.
Double-click `stop.command` to shut everything down.

### Manual start

```bash
# Terminal 1 — GraphHopper
cd ~/graphhopper-data && java -jar graphhopper-web-10.0.jar server config.yml

# Terminal 2 — Backend
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Terminal 3 — Frontend
cd frontend && npm run dev
```

Open **http://localhost:5173** in your browser.

## API Endpoints

| Method | Endpoint           | Description                        |
|--------|--------------------|------------------------------------|
| POST   | `/api/route`       | Calculate route between waypoints  |
| GET    | `/api/geocode`     | Search address via Nominatim       |
| POST   | `/api/export/gpx`  | Export current route as GPX file   |

## Project Structure

```
open-gpx/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI entry point
│   │   ├── config.py             # Settings
│   │   ├── routers/
│   │   │   ├── routing.py        # POST /api/route
│   │   │   ├── geocoding.py      # GET /api/geocode
│   │   │   └── export.py         # POST /api/export/gpx
│   │   └── services/
│   │       ├── graphhopper.py    # GraphHopper client + custom models
│   │       ├── gpx_builder.py    # GPX file generation
│   │       └── nominatim.py      # Geocoding proxy
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Sidebar/          # Waypoint list, search, controls
│       │   └── MapView/          # Leaflet map, markers, route polyline
│       ├── hooks/
│       │   ├── useRouteCalculation.ts  # Debounced auto-routing
│       │   └── useGeocoding.ts         # Debounced address search
│       ├── store/
│       │   └── useRouteStore.ts  # Zustand global state
│       └── types/
├── start.command                 # macOS: start all services
├── stop.command                  # macOS: stop all services
└── README.md
```

## OSM Data for Other Regions

Download any region from [Geofabrik](https://download.geofabrik.de/) and update `datareader.file` in `config.yml` accordingly.

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

- [GraphHopper](https://github.com/graphhopper/graphhopper) — open source routing engine
- [OpenStreetMap](https://www.openstreetmap.org/) — map data
- [Nominatim](https://nominatim.org/) — geocoding
- [react-leaflet](https://react-leaflet.js.org/) — map rendering
