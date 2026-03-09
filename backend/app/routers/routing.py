from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.graphhopper import get_route

router = APIRouter()


class Waypoint(BaseModel):
    lat: float
    lng: float


class SegmentOptions(BaseModel):
    adventure: Optional[int] = Field(default=None, ge=0, le=100)
    avoid_motorways: bool = False
    avoid_highways: bool = False
    avoid_primary: bool = False
    prefer_unpaved: bool = False
    prefer_secondary: bool = False
    prefer_mountain_passes: bool = False


class RouteRequest(BaseModel):
    waypoints: list[Waypoint]
    adventure: int = Field(default=0, ge=0, le=100)
    segment_options: list[SegmentOptions] = []


class ElevationPoint(BaseModel):
    d: float
    ele: float


class RoadStats(BaseModel):
    road_class: dict[str, float]
    surface: dict[str, float]


class RouteResponse(BaseModel):
    distance_m: float
    duration_s: float
    geometry: list[list[float]]
    elevation: list[ElevationPoint]
    max_elevation: Optional[float]
    min_elevation: Optional[float]
    road_stats: RoadStats


@router.post("/route", response_model=RouteResponse)
async def calculate_route(body: RouteRequest):
    if len(body.waypoints) < 2:
        raise HTTPException(status_code=400, detail="At least 2 waypoints required")

    try:
        result = await get_route(
            [wp.model_dump() for wp in body.waypoints],
            body.adventure,
            [seg.model_dump() for seg in body.segment_options],
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return result
