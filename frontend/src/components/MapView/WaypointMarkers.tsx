import { Marker, Tooltip } from 'react-leaflet'
import L from 'leaflet'
import { useRouteStore } from '../../store/useRouteStore'

function createNumberedIcon(index: number) {
  return L.divIcon({
    className: '',
    html: `<div style="
      background: #2563eb;
      color: white;
      border: 2px solid white;
      border-radius: 50%;
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 13px;
      font-weight: bold;
      box-shadow: 0 2px 6px rgba(0,0,0,0.35);
      cursor: grab;
    ">${index + 1}</div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  })
}

export function WaypointMarkers() {
  const waypoints = useRouteStore((s) => s.waypoints)
  const updateWaypointPosition = useRouteStore((s) => s.updateWaypointPosition)

  return (
    <>
      {waypoints.map((wp, index) => (
        <Marker
          key={wp.id}
          position={[wp.lat, wp.lng]}
          icon={createNumberedIcon(index)}
          draggable
          eventHandlers={{
            dragend(e) {
              const { lat, lng } = e.target.getLatLng()
              updateWaypointPosition(wp.id, lat, lng)
            },
          }}
        >
          {wp.name && <Tooltip permanent={false}>{wp.name}</Tooltip>}
        </Marker>
      ))}
    </>
  )
}
