import { Circle } from 'react-leaflet'
import { useRouteStore } from '../../store/useRouteStore'

export function ExtremeCircles() {
  const waypoints = useRouteStore((s) => s.waypoints)
  const segmentOptions = useRouteStore((s) => s.segmentOptions)

  return (
    <>
      {waypoints.slice(0, -1).map((wp) => {
        const opts = segmentOptions[wp.id]
        if (!opts?.extreme) return null
        return (
          <Circle
            key={wp.id}
            center={[wp.lat, wp.lng]}
            radius={opts.extreme_radius_km * 1000}
            pathOptions={{ color: '#f97316', fillOpacity: 0.05, dashArray: '6 4' }}
          />
        )
      })}
    </>
  )
}
