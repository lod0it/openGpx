from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.graphhopper import get_route

router = APIRouter()


class Waypoint(BaseModel):
    lat: float
    lng: float


class RouteRequest(BaseModel):
    waypoints: list[Waypoint]
    profile: str = "standard"


class RouteResponse(BaseModel):
    distance_m: float
    duration_s: float
    geometry: list[list[float]]


@router.post("/route", response_model=RouteResponse)
async def calculate_route(body: RouteRequest):
    if len(body.waypoints) < 2:
        raise HTTPException(status_code=400, detail="At least 2 waypoints required")

    if body.profile not in ("standard", "avoid_tolls", "scenic"):
        raise HTTPException(status_code=400, detail=f"Unknown profile: {body.profile}")

    try:
        result = await get_route(
            [wp.model_dump() for wp in body.waypoints],
            body.profile,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return result
