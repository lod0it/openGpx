from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from app.services.nominatim import geocode

router = APIRouter()


class GeocodeResult(BaseModel):
    display_name: str
    lat: float
    lng: float


@router.get("/geocode", response_model=list[GeocodeResult])
async def search_location(q: str = Query(..., min_length=2)):
    try:
        results = await geocode(q)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Geocoding failed: {exc}")
    return results
