import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "open-gpx/1.0 (local development)"


async def geocode(query: str) -> list[dict]:
    """Search OSM Nominatim and return up to 5 results."""
    params = {
        "q": query,
        "format": "json",
        "limit": 5,
        "addressdetails": 0,
    }
    headers = {"User-Agent": USER_AGENT}

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(NOMINATIM_URL, params=params, headers=headers)

    if resp.status_code != 200:
        return []

    results = resp.json()
    return [
        {
            "display_name": r["display_name"],
            "lat": float(r["lat"]),
            "lng": float(r["lon"]),
        }
        for r in results
    ]
