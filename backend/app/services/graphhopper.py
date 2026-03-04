import httpx
from app.config import settings

CUSTOM_MODELS: dict[str, dict] = {
    "standard": {},
    "avoid_tolls": {
        "priority": [
            {"if": "toll == ALL || toll == HGV", "multiply_by": "0"}
        ]
    },
    "scenic": {
        "priority": [
            {"if": "road_class == MOTORWAY || road_class == TRUNK", "multiply_by": "0.05"},
            {"if": "road_class == SECONDARY || road_class == TERTIARY", "multiply_by": "1.5"},
        ]
    },
}


async def get_route(
    waypoints: list[dict],
    profile: str,
) -> dict:
    """Call self-hosted GraphHopper and return geometry + stats."""
    custom_model = CUSTOM_MODELS.get(profile, {})

    payload: dict = {
        "profile": "car",
        "points": [[wp["lng"], wp["lat"]] for wp in waypoints],
        "points_encoded": False,
    }

    # Custom models require ch.disable (only works with self-hosted GH)
    if custom_model:
        payload["custom_model"] = custom_model
        payload["ch.disable"] = True
    else:
        # Standard profile: CH is fine (fastest query)
        payload["ch.disable"] = False

    url = f"{settings.graphhopper_url}/route"

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=payload)

    if resp.status_code != 200:
        detail = resp.text
        raise RuntimeError(f"GraphHopper error {resp.status_code}: {detail}")

    data = resp.json()
    path = data["paths"][0]

    # GH returns [lng, lat] — flip to [lat, lng] for frontend/Leaflet
    coordinates = path["points"]["coordinates"]
    geometry = [[c[1], c[0]] for c in coordinates]

    return {
        "distance_m": path["distance"],
        "duration_s": path["time"] / 1000,  # ms → s
        "geometry": geometry,
    }
