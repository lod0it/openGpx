import { Polyline } from 'react-leaflet'
import { useRouteStore } from '../../store/useRouteStore'

export function RoutePolyline() {
  const geometry = useRouteStore((s) => s.geometry)

  if (geometry.length === 0) return null

  return (
    <Polyline
      positions={geometry}
      pathOptions={{ color: '#2563eb', weight: 4, opacity: 0.85 }}
    />
  )
}
