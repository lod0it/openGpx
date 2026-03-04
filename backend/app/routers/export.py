from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.gpx_builder import build_gpx_track, build_gpx_route
import io

router = APIRouter()


class WaypointExport(BaseModel):
    lat: float
    lng: float
    name: str = ""


class ExportRequest(BaseModel):
    type: str  # "track" or "route"
    waypoints: list[WaypointExport]
    geometry: list[list[float]] = []
    route_name: str = "My Route"


@router.post("/export/gpx")
async def export_gpx(body: ExportRequest):
    if body.type not in ("track", "route"):
        raise HTTPException(status_code=400, detail="type must be 'track' or 'route'")

    if body.type == "track":
        if not body.geometry:
            raise HTTPException(status_code=400, detail="geometry required for track export")
        gpx_xml = build_gpx_track(body.geometry, body.route_name)
        filename = "route_track.gpx"
    else:
        if not body.waypoints:
            raise HTTPException(status_code=400, detail="waypoints required for route export")
        gpx_xml = build_gpx_route(
            [wp.model_dump() for wp in body.waypoints],
            body.route_name,
        )
        filename = "route_waypoints.gpx"

    return StreamingResponse(
        content=io.BytesIO(gpx_xml.encode("utf-8")),
        media_type="application/gpx+xml",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
