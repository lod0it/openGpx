import type { Waypoint } from '../types'

export async function downloadGpx(
  type: 'track' | 'route',
  waypoints: Waypoint[],
  geometry: [number, number][],
  routeName = 'My Route',
) {
  const resp = await fetch('/api/export/gpx', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type, waypoints, geometry, route_name: routeName }),
  })

  if (!resp.ok) {
    throw new Error(`Export failed: HTTP ${resp.status}`)
  }

  const blob = await resp.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = type === 'track' ? 'route_track.gpx' : 'route_waypoints.gpx'
  a.click()
  URL.revokeObjectURL(url)
}
