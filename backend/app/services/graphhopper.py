import math
import logging
from collections import defaultdict
import httpx
from app.config import settings
from app.services.overpass import fetch_passes_around

logger = logging.getLogger("opengpx")


def _haversine_m(a: list, b: list) -> float:
    """Distanza in metri tra due punti [lng, lat, ...]."""
    lat1, lon1 = math.radians(a[1]), math.radians(a[0])
    lat2, lon2 = math.radians(b[1]), math.radians(b[0])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * 6_371_000 * math.asin(math.sqrt(h))


def _nudge_toward(start: dict, end: dict, meters: float = 300.0) -> dict:
    """Punto a `meters` m da start in direzione end."""
    R = 6_371_000.0
    lat1 = math.radians(start["lat"])
    lng1 = math.radians(start["lng"])
    lat2 = math.radians(end["lat"])
    lng2 = math.radians(end["lng"])

    dlon = lng2 - lng1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.atan2(x, y)

    d = meters / R
    lat_out = math.asin(
        math.sin(lat1) * math.cos(d) + math.cos(lat1) * math.sin(d) * math.cos(bearing)
    )
    lng_out = lng1 + math.atan2(
        math.sin(bearing) * math.sin(d) * math.cos(lat1),
        math.cos(d) - math.sin(lat1) * math.sin(lat_out),
    )
    return {"lat": math.degrees(lat_out), "lng": math.degrees(lng_out)}


def _nudge_past_pass(seg_start: dict, pass_wp: dict, meters: float = 2000.0) -> dict:
    """
    Punto a `meters` m oltre pass_wp nella direzione seg_start→pass_wp.
    Usato per il loop: forza GH ad andare 2km oltre il passo prima di tornare.
    """
    dist_to_pass = _haversine_m(
        [seg_start["lng"], seg_start["lat"]],
        [pass_wp["lng"], pass_wp["lat"]],
    )
    return _nudge_toward(seg_start, pass_wp, meters=dist_to_pass + meters)


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

    if filters.get("extreme"):
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
    if filters.get("extreme"):
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
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
    except httpx.ConnectError:
        raise RuntimeError(
            "GraphHopper non raggiungibile — potrebbe essere ancora in avvio. "
            "Attendi qualche secondo e riprova."
        )
    except httpx.TimeoutException:
        raise RuntimeError("GraphHopper timeout — il server è sovraccarico o ancora in avvio.")
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Errore di connessione a GraphHopper: {exc}")

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
    extreme_log: list[dict] = []

    for i in range(len(waypoints) - 1):
        seg_opts = segment_options[i] if i < len(segment_options) else {}
        seg_adventure = (
            seg_opts.get("adventure")
            if seg_opts.get("adventure") is not None
            else adventure
        )
        filters = {k: v for k, v in seg_opts.items() if k != "adventure"}

        custom_model = build_custom_model(seg_adventure, filters)

        seg_start, seg_end = waypoints[i], waypoints[i + 1]
        data = None

        if filters.get("extreme"):
            radius = filters.get("extreme_radius_km", 50.0)
            direction = filters.get("extreme_direction")
            pass_index = int(filters.get("extreme_pass_index", 0))
            extreme_loop = filters.get("extreme_loop", False)

            logger.info(f"[Extreme] seg={i} start={seg_start} radius={radius}km dir={direction} idx={pass_index} loop={extreme_loop}")
            passes = await fetch_passes_around(seg_start, radius, direction)
            passes_found = len(passes)
            names = [p['name'] or f"{p['lat']:.4f},{p['lng']:.4f}" for p in passes]
            logger.info(f"[Extreme] seg={i} trovati {passes_found} passi: {names}")

            if not passes:
                extreme_log.append({
                    "segment": i,
                    "name": "—",
                    "lat": seg_start["lat"],
                    "lng": seg_start["lng"],
                    "ele": 0,
                    "ctd_m": 0,
                    "status": "no_passes",
                    "mode": "",
                    "passes_found": 0,
                })
            else:
                # Riordina in base all'indice scelto dall'utente (con fallback circolare)
                preferred_idx = pass_index % passes_found
                ordered = passes[preferred_idx:] + passes[:preferred_idx]

                for p in ordered:
                    pass_wp = {"lat": p["lat"], "lng": p["lng"]}
                    try:
                        if extreme_loop:
                            # Loop: start → pass → (2km oltre il passo) → start → end
                            # Crea un lollipop visibile sulla mappa
                            nudge = _nudge_past_pass(seg_start, pass_wp, meters=2000.0)
                            points = [seg_start, pass_wp, nudge, seg_start, seg_end]
                        else:
                            points = [seg_start, pass_wp, seg_end]

                        data = await _call_graphhopper(points, custom_model)
                        mode = "loop" if extreme_loop else "route"
                        extreme_log.append({
                            "segment": i,
                            "name": p["name"],
                            "lat": p["lat"],
                            "lng": p["lng"],
                            "ele": p["ele"],
                            "ctd_m": round(p["dist"]),
                            "status": "used",
                            "mode": mode,
                            "passes_found": passes_found,
                        })
                        logger.info(f"[Extreme] Pass usato ({mode}): {p['name']} lat={p['lat']} lng={p['lng']} ele={p['ele']}m idx={preferred_idx}/{passes_found}")
                        break
                    except RuntimeError as exc:
                        if "PointNotFoundException" in str(exc):
                            extreme_log.append({
                                "segment": i,
                                "name": p["name"],
                                "lat": p["lat"],
                                "lng": p["lng"],
                                "ele": p["ele"],
                                "ctd_m": round(p["dist"]),
                                "status": "unreachable",
                                "mode": "",
                                "passes_found": passes_found,
                            })
                            logger.info(f"[Extreme] Pass non raggiungibile ({p['name']}), provo prossimo")
                            continue
                        raise

        if data is None:
            data = await _call_graphhopper([seg_start, seg_end], custom_model)

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

    # Considera validi solo valori > 0 (ele=0 indica assenza di dati SRTM)
    valid_elevations = [p["ele"] for p in elevation_profile if p["ele"] > 0]
    total_road = sum(agg_road_class.values()) or 1
    total_surf = sum(agg_surface.values()) or 1

    return {
        "distance_m": total_distance,
        "duration_s": total_duration,
        "geometry": all_geometry,
        "elevation": elevation_profile,
        "max_elevation": max(valid_elevations) if valid_elevations else None,
        "min_elevation": min(valid_elevations) if valid_elevations else None,
        "road_stats": {
            "road_class": {k: round(v / total_road * 100, 1) for k, v in agg_road_class.items()},
            "surface": {k: round(v / total_surf * 100, 1) for k, v in agg_surface.items()},
        },
        "extreme_log": extreme_log,
    }
