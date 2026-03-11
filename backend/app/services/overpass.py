import math
import httpx

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_FALLBACK_URL = "https://overpass.kumi.systems/api/interpreter"
ELE_THRESHOLD = 800         # metri ASL (abbassato da 1000 → include più passi)
OVERPASS_TIMEOUT_S = 8.0
MAX_CANDIDATES = 20         # limit per bbox grandi

DIRECTION_RANGES = {
    "N": (315, 45),   # wrap-around
    "E": (45, 135),
    "S": (135, 225),
    "O": (225, 315),
}


def _build_bbox_from_center(center: dict, radius_km: float) -> tuple:
    """Restituisce (south, west, north, east) basata su centro e raggio."""
    pad = radius_km / 111.0
    return (
        center["lat"] - pad,
        center["lng"] - pad,
        center["lat"] + pad,
        center["lng"] + pad,
    )


def _parse_ele(ele_str) -> float | None:
    """Converte stringa quota in float. Gestisce '2758', '2758 m', '2758m'."""
    if ele_str is None:
        return None
    try:
        return float(str(ele_str).lower().replace("m", "").strip())
    except ValueError:
        return None


def _haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distanza in metri tra due punti (lat/lng gradi)."""
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _bearing_deg(from_lat: float, from_lng: float, to_lat: float, to_lng: float) -> float:
    """Restituisce bearing 0-360° (0=N, 90=E, 180=S, 270=O)."""
    lat1 = math.radians(from_lat)
    lat2 = math.radians(to_lat)
    dlon = math.radians(to_lng - from_lng)
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


def _in_direction(bearing: float, direction: str) -> bool:
    """Verifica se il bearing rientra nel range della direzione."""
    lo, hi = DIRECTION_RANGES[direction]
    if lo > hi:  # wrap-around (es. N: 315-45)
        return bearing >= lo or bearing <= hi
    return lo <= bearing <= hi


def _extract_coords(el: dict) -> tuple[float, float] | None:
    """
    Estrae (lat, lng) da un elemento Overpass.
    - node: lat/lon diretti
    - way: usa il campo 'center' (disponibile con 'out center;')
    """
    el_type = el.get("type")
    if el_type == "node":
        return el.get("lat"), el.get("lon")
    elif el_type == "way":
        center = el.get("center", {})
        lat = center.get("lat")
        lng = center.get("lon")
        if lat is not None and lng is not None:
            return lat, lng
    return None


async def _query_overpass(url: str, query: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=OVERPASS_TIMEOUT_S) as client:
        resp = await client.post(url, data={"data": query})
        resp.raise_for_status()
        return resp.json().get("elements", [])


async def fetch_passes_around(
    center: dict,
    radius_km: float,
    direction: str | None = None,
) -> list[dict]:
    """
    Trova passi di montagna entro radius_km dal centro.
    - mountain_pass=yes: incluso sempre (tag esplicito di passo, node + way)
    - natural=saddle con ele >= ELE_THRESHOLD: incluso come alternativa
    Se direction fornita, filtra per bearing dal centro.
    Ritorna top-3 ordinati per distanza dal centro.
    In caso di errore/timeout ritorna [].
    """
    s, w, n, e = _build_bbox_from_center(center, radius_km)
    query = (
        f"[out:json][timeout:6];\n"
        f"(\n"
        f'  node["mountain_pass"="yes"]({s},{w},{n},{e});\n'
        f'  node["natural"="saddle"]["ele"]({s},{w},{n},{e});\n'
        f'  way["mountain_pass"="yes"]({s},{w},{n},{e});\n'
        f'  way["natural"="saddle"]["ele"]({s},{w},{n},{e});\n'
        f");\n"
        f"out center;"
    )

    elements: list[dict] = []
    for overpass_url in (OVERPASS_URL, OVERPASS_FALLBACK_URL):
        try:
            elements = await _query_overpass(overpass_url, query)
            break
        except Exception:
            continue

    if not elements:
        return []

    radius_m = radius_km * 1000
    candidates = []
    for el in elements[:MAX_CANDIDATES * 3]:
        tags = el.get("tags", {})
        is_mountain_pass = tags.get("mountain_pass") == "yes"
        is_saddle = tags.get("natural") == "saddle"

        # Saddles senza quota sufficiente: escludi
        if is_saddle and not is_mountain_pass:
            ele = _parse_ele(tags.get("ele"))
            if ele is None or ele < ELE_THRESHOLD:
                continue

        coords = _extract_coords(el)
        if coords is None or coords[0] is None:
            continue
        p_lat, p_lng = coords

        dist = _haversine_m(center["lat"], center["lng"], p_lat, p_lng)
        if dist > radius_m:
            continue

        if direction is not None:
            bearing = _bearing_deg(center["lat"], center["lng"], p_lat, p_lng)
            if not _in_direction(bearing, direction):
                continue

        ele_val = _parse_ele(tags.get("ele")) or 0.0
        candidates.append({
            "lat": p_lat,
            "lng": p_lng,
            "ele": ele_val,
            "name": tags.get("name", ""),
            "dist": dist,
        })

        if len(candidates) >= MAX_CANDIDATES:
            break

    candidates.sort(key=lambda x: x["dist"])
    return candidates[:3]
