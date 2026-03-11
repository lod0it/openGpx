import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.graphhopper import get_route

logger = logging.getLogger("opengpx")

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
    extreme: bool = False
    extreme_radius_km: float = Field(default=20.0, ge=1.0, le=300.0)
    extreme_direction: Optional[str] = None  # "N" | "S" | "E" | "O"
    extreme_loop: bool = False
    extreme_pass_index: int = Field(default=0, ge=0, le=9)


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


class ExtremeLogEntry(BaseModel):
    segment: int
    name: str
    lat: float
    lng: float
    ele: float
    ctd_m: int
    status: str
    mode: str = ""
    passes_found: int = 0


class RouteResponse(BaseModel):
    distance_m: float
    duration_s: float
    geometry: list[list[float]]
    elevation: list[ElevationPoint]
    max_elevation: Optional[float]
    min_elevation: Optional[float]
    road_stats: RoadStats
    extreme_log: list[ExtremeLogEntry] = []


@router.post("/route", response_model=RouteResponse)
async def calculate_route(body: RouteRequest):
    if len(body.waypoints) < 2:
        raise HTTPException(status_code=400, detail="At least 2 waypoints required")

    try:
        seg_dicts = [seg.model_dump() for seg in body.segment_options]
        for i, s in enumerate(seg_dicts):
            if s.get("extreme"):
                logger.info(f"[API] seg={i} EXTREME radius={s.get('extreme_radius_km')}km dir={s.get('extreme_direction')} loop={s.get('extreme_loop')}")
        result = await get_route(
            [wp.model_dump() for wp in body.waypoints],
            body.adventure,
            seg_dicts,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return result
