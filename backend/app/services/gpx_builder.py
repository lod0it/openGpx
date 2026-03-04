import gpxpy
import gpxpy.gpx


def build_gpx_track(geometry: list[list[float]], route_name: str) -> str:
    """Build a GPX Track from route geometry (full polyline)."""
    gpx = gpxpy.gpx.GPX()
    gpx.name = route_name

    track = gpxpy.gpx.GPXTrack(name=route_name)
    gpx.tracks.append(track)

    segment = gpxpy.gpx.GPXTrackSegment()
    track.segments.append(segment)

    for lat, lng in geometry:
        segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, lng))

    return gpx.to_xml()


def build_gpx_route(waypoints: list[dict], route_name: str) -> str:
    """Build a GPX Route from named waypoints only."""
    gpx = gpxpy.gpx.GPX()
    gpx.name = route_name

    route = gpxpy.gpx.GPXRoute(name=route_name)
    gpx.routes.append(route)

    for wp in waypoints:
        route.points.append(
            gpxpy.gpx.GPXRoutePoint(wp["lat"], wp["lng"], name=wp.get("name") or "")
        )

    return gpx.to_xml()
