import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import { useRouteStore } from '../../store/useRouteStore'

export function MapAutoFit() {
  const map = useMap()
  const waypoints = useRouteStore((s) => s.waypoints)
  const geometry = useRouteStore((s) => s.geometry)

  // Fit sulla geometria del percorso calcolato
  useEffect(() => {
    if (geometry.length < 2) return
    const bounds = L.latLngBounds(geometry as [number, number][])
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15, animate: true })
  }, [geometry, map])

  // Fit sui waypoint (ogni aggiunta/rimozione)
  useEffect(() => {
    if (waypoints.length === 0) return
    if (waypoints.length === 1) {
      map.flyTo([waypoints[0].lat, waypoints[0].lng], 13, { duration: 0.8 })
    } else {
      const bounds = L.latLngBounds(waypoints.map((w) => [w.lat, w.lng] as [number, number]))
      map.fitBounds(bounds, { padding: [80, 80], maxZoom: 14, animate: true })
    }
  }, [waypoints, map])

  return null
}
