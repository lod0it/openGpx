# open-gpx

A self-hosted motorcycle GPX route planner — a local clone of motoplanner.com.

## Objective

Plan motorcycle routes on an interactive map, export them as GPX files, and run everything locally without depending on external paid services.

## Features

- Interactive map with clickable waypoints (add, drag, reorder, remove)
- Automatic route calculation between waypoints via self-hosted GraphHopper
- Motorcycle-optimized routing (avoids motorways, prefers scenic roads)
- GPX file export for use with GPS devices and navigation apps
- Address search via Nominatim (OpenStreetMap geocoding)
- Fully offline-capable once OSM data is imported

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Vite + Leaflet |
| Backend | Python 3.12 + FastAPI |
| Routing | GraphHopper 10.x (local JAR, Italy OSM data) |
| Map tiles | OpenStreetMap |
| Geocoding | Nominatim |
| State | Zustand |

## Architecture

```
Browser (localhost:5173)
  └─ React + Leaflet UI
       └─ FastAPI (localhost:8000)   ← /api/route, /api/geocode, /api/export/gpx
            ├─ GraphHopper (localhost:8989)  ← routing engine
            └─ Nominatim (nominatim.openstreetmap.org)  ← geocoding
```

## Quick Start

1. Start GraphHopper: `cd ~/graphhopper-data && java -jar graphhopper-web-10.0.jar server config.yml`
2. Start backend: `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
3. Start frontend: `cd frontend && npm run dev`
4. Open `http://localhost:5173`

## Data

OSM data for Italy (~2GB) from [Geofabrik](https://download.geofabrik.de/europe/italy-latest.osm.pbf).
GraphHopper builds a routing graph on first run (~15 min), then loads in ~30 sec on subsequent starts.
