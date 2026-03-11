import { useEffect, useRef } from 'react'
import { useRouteStore } from '../store/useRouteStore'
import { fetchRoute } from '../api/routing'

export function useRouteCalculation() {
  const waypoints = useRouteStore((s) => s.waypoints)
  const adventure = useRouteStore((s) => s.adventure)
  const segmentOptions = useRouteStore((s) => s.segmentOptions)
  const globalFilters = useRouteStore((s) => s.globalFilters)
  const setRoute = useRouteStore((s) => s.setRoute)
  const setLoading = useRouteStore((s) => s.setLoading)
  const setError = useRouteStore((s) => s.setError)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (waypoints.length < 2) return

    if (debounceRef.current) clearTimeout(debounceRef.current)

    debounceRef.current = setTimeout(async () => {
      setLoading(true)
      try {
        const result = await fetchRoute(waypoints, adventure, segmentOptions, globalFilters)
        if (result) {
          setRoute({
            geometry: result.geometry as [number, number][],
            distanceM: result.distance_m,
            durationS: result.duration_s,
            elevation: result.elevation,
            maxElevation: result.max_elevation,
            minElevation: result.min_elevation,
            roadStats: result.road_stats,
            extremeLog: result.extreme_log ?? [],
          })
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Routing failed')
      }
    }, 400)

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [waypoints, adventure, segmentOptions, globalFilters, setRoute, setLoading, setError])
}
