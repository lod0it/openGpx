import { MapContainer, TileLayer } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { MapClickHandler } from './MapClickHandler'
import { WaypointMarkers } from './WaypointMarkers'
import { RoutePolyline } from './RoutePolyline'

export function MapView() {
  return (
    <MapContainer
      center={[45.46, 9.19]}
      zoom={7}
      style={{ flex: 1, height: '100%' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapClickHandler />
      <WaypointMarkers />
      <RoutePolyline />
    </MapContainer>
  )
}
