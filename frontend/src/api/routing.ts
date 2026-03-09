import type { RouteResult, Waypoint, SegmentOptions, GlobalFilters } from '../types'

export async function fetchRoute(
  waypoints: Waypoint[],
  adventure: number,
  segmentOptions: Record<string, SegmentOptions>,
  globalFilters: GlobalFilters,
): Promise<RouteResult | null> {
  const segOpts = waypoints.slice(0, -1).map((wp) => {
    const opts = segmentOptions[wp.id]
    return {
      adventure: opts?.adventure ?? null,
      avoid_motorways: (opts?.avoid_motorways || globalFilters.avoid_motorways),
      avoid_highways: (opts?.avoid_highways || globalFilters.avoid_highways),
      avoid_primary: (opts?.avoid_primary || globalFilters.avoid_primary),
      prefer_unpaved: (opts?.prefer_unpaved || globalFilters.prefer_unpaved),
      prefer_secondary: (opts?.prefer_secondary || globalFilters.prefer_secondary),
      prefer_mountain_passes: (opts?.prefer_mountain_passes || globalFilters.prefer_mountain_passes),
    }
  })

  const resp = await fetch('/api/route', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      waypoints: waypoints.map((w) => ({ lat: w.lat, lng: w.lng })),
      adventure,
      segment_options: segOpts,
    }),
  })

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail ?? `HTTP ${resp.status}`)
  }

  return resp.json()
}
