import { useMapEvents } from 'react-leaflet'
import { useRouteStore } from '../../store/useRouteStore'

export function MapClickHandler() {
  const addWaypoint = useRouteStore((s) => s.addWaypoint)

  useMapEvents({
    click(e) {
      addWaypoint({ lat: e.latlng.lat, lng: e.latlng.lng })
    },
  })

  return null
}
