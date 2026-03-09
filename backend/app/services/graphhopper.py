import math
from collections import defaultdict
import httpx
from app.config import settings


def _haversine_m(a: list, b: list) -> float:
    """Distanza in metri tra due punti [lng, lat, ...]."""
    lat1, lon1 = math.radians(a[1]), math.radians(a[0])
    lat2, lon2 = math.radians(b[1]), math.radians(b[0])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * 6_371_000 * math.asin(math.sqrt(h))


def build_custom_model(adventure: int, filters: dict) -> dict:
    priority: list[dict] = []

    avoid_motorways = filters.get("avoid_motorways", False) or adventure >= 80
    avoid_highways = filters.get("avoid_highways", False)
    avoid_primary = filters.get("avoid_primary", False)

    # MOTORWAY: penalità lineare, evitato da adventure >= 80
    if avoid_motorways:
        priority.append({"if": "road_class == MOTORWAY", "multiply_by": "0"})
    elif adventure > 0:
        p = round(max(0.0, 1.0 - adventure / 100), 2)
        priority.append({"if": "road_class == MOTORWAY", "multiply_by": str(p)})

    # TRUNK: penalità quadratica-esponenziale
    if avoid_highways:
        priority.append({"if": "road_class == TRUNK", "multiply_by": "0"})
    elif adventure > 0:
        p = round(max(0.0, 1.0 - (adventure / 100) ** 1.5 * 1.2), 2)
        priority.append({"if": "road_class == TRUNK", "multiply_by": str(p)})

    # PRIMARY: penalizzata da adventure > 30
    if avoid_primary:
        priority.append({"if": "road_class == PRIMARY", "multiply_by": "0"})
    elif adventure > 30:
        p = round(max(0.05, 1.0 - (adventure - 30) / 70 * 0.95), 2)
        priority.append({"if": "road_class == PRIMARY", "multiply_by": str(p)})

    if adventure > 0:
        # Bonus strade secondarie e curve
        secondary_bonus = str(round(1.0 + adventure / 100 * 0.8, 2))
        tertiary_bonus = str(round(1.0 + adventure / 100 * 1.5, 2))
        curvy_bonus = str(round(1.0 + adventure / 100 * 3.0, 2))
        very_curvy_bonus = str(round(1.0 + adventure / 100 * 5.0, 2))
        priority.append({"if": "road_class == SECONDARY", "multiply_by": secondary_bonus})
        priority.append({"if": "road_class == TERTIARY", "multiply_by": tertiary_bonus})
        priority.append({"if": "curvature > 0.5", "multiply_by": curvy_bonus})
        priority.append({"if": "curvature > 0.75", "multiply_by": very_curvy_bonus})

    if filters.get("prefer_unpaved"):
        for surface in ["UNPAVED", "GRAVEL", "DIRT", "GROUND", "GRASS"]:
            priority.append({"if": f"surface == {surface}", "multiply_by": "2.0"})

    if filters.get("prefer_secondary") and adventure == 0:
        priority.append({"if": "road_class == SECONDARY", "multiply_by": "1.5"})
        priority.append({"if": "road_class == TERTIARY", "multiply_by": "1.5"})

    if filters.get("prefer_mountain_passes"):
        priority.append({"if": "road_class == MOTORWAY", "multiply_by": "0.01"})
        priority.append({"if": "road_class == TRUNK", "multiply_by": "0.05"})
        priority.append({"if": "road_class == PRIMARY", "multiply_by": "0.3"})
        priority.append({"if": "road_class == SECONDARY", "multiply_by": "2.5"})
        priority.append({"if": "road_class == TERTIARY", "multiply_by": "2.0"})
        priority.append({"if": "curvature > 0.6", "multiply_by": "2.0"})
        priority.append({"if": "curvature > 0.8", "multiply_by": "3.5"})

    model: dict = {"priority": priority} if priority else {}
    if adventure > 0:
        model["distance_influence"] = round(adventure * 1.5)
    if filters.get("prefer_mountain_passes"):
        model["distance_influence"] = 250
    return model


async def _call_graphhopper(points: list[dict], custom_model: dict) -> dict:
    payload: dict = {
        "profile": "motorcycle",
        "points": [[p["lng"], p["lat"]] for p in points],
        "points_encoded": False,
        "elevation": True,
        "details": ["road_class", "surface"],
    }
    payload["ch.disable"] = True
    if custom_model:
        payload["custom_model"] = custom_model

    url = f"{settings.graphhopper_url}/route"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=payload)

    if resp.status_code != 200:
        raise RuntimeError(f"GraphHopper error {resp.status_code}: {resp.text}")

    return resp.json()


async def get_route(
    waypoints: list[dict],
    adventure: int,
    segment_options: list[dict],
) -> dict:
    total_distance = 0.0
    total_duration = 0.0
    all_geometry: list[list[float]] = []
    all_coords_3d: list[list[float]] = []
    agg_road_class: dict[str, float] = defaultdict(float)
    agg_surface: dict[str, float] = defaultdict(float)

    for i in range(len(waypoints) - 1):
        seg_opts = segment_options[i] if i < len(segment_options) else {}
        seg_adventure = (
            seg_opts.get("adventure")
            if seg_opts.get("adventure") is not None
            else adventure
        )
        filters = {k: v for k, v in seg_opts.items() if k != "adventure"}

        custom_model = build_custom_model(seg_adventure, filters)
        data = await _call_graphhopper([waypoints[i], waypoints[i + 1]], custom_model)

        path = data["paths"][0]
        coords = path["points"]["coordinates"]  # [lng, lat, ele]

        skip = 1 if i > 0 else 0
        all_geometry.extend([[c[1], c[0]] for c in coords[skip:]])
        all_coords_3d.extend(coords[skip:])

        details = path.get("details", {})
        for from_i, to_i, value in details.get("road_class", []):
            for k in range(from_i, to_i):
                if k + 1 < len(coords):
                    agg_road_class[value] += _haversine_m(coords[k], coords[k + 1])
        for from_i, to_i, value in details.get("surface", []):
            for k in range(from_i, to_i):
                if k + 1 < len(coords):
                    agg_surface[value] += _haversine_m(coords[k], coords[k + 1])

        total_distance += path["distance"]
        total_duration += path["time"] / 1000

    elevation_profile: list[dict] = []
    d = 0.0
    for j, c in enumerate(all_coords_3d):
        if j > 0:
            d += _haversine_m(all_coords_3d[j - 1], c)
        ele = round(c[2], 1) if len(c) >= 3 else 0.0
        elevation_profile.append({"d": round(d / 1000, 3), "ele": ele})

    elevations = [p["ele"] for p in elevation_profile]
    total_road = sum(agg_road_class.values()) or 1
    total_surf = sum(agg_surface.values()) or 1

    return {
        "distance_m": total_distance,
        "duration_s": total_duration,
        "geometry": all_geometry,
        "elevation": elevation_profile,
        "max_elevation": max(elevations) if elevations else None,
        "min_elevation": min(elevations) if elevations else None,
        "road_stats": {
            "road_class": {k: round(v / total_road * 100, 1) for k, v in agg_road_class.items()},
            "surface": {k: round(v / total_surf * 100, 1) for k, v in agg_surface.items()},
        },
    }
