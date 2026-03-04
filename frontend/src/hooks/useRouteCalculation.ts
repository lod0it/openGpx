import { useEffect, useRef } from 'react'
import { useRouteStore } from '../store/useRouteStore'
import { fetchRoute } from '../api/routing'

export function useRouteCalculation() {
  const waypoints = useRouteStore((s) => s.waypoints)
  const profile = useRouteStore((s) => s.profile)
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
        const result = await fetchRoute(waypoints, profile)
        if (result) {
          setRoute(result.geometry as [number, number][], result.distance_m, result.duration_s)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Routing failed')
      }
    }, 400)

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [waypoints, profile, setRoute, setLoading, setError])
}
