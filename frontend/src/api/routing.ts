import type { RouteProfile, RouteResult, Waypoint } from '../types'

export async function fetchRoute(
  waypoints: Waypoint[],
  profile: RouteProfile,
): Promise<RouteResult | null> {
  const resp = await fetch('/api/route', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      waypoints: waypoints.map((w) => ({ lat: w.lat, lng: w.lng })),
      profile,
    }),
  })

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail ?? `HTTP ${resp.status}`)
  }

  return resp.json()
}
