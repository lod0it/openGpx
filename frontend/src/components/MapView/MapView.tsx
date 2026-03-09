import { MapContainer, TileLayer } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { MapClickHandler } from './MapClickHandler'
import { WaypointMarkers } from './WaypointMarkers'
import { RoutePolyline } from './RoutePolyline'
import { useMapStore } from '../../store/useMapStore'

const TILE_LAYERS = {
  osm: {
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  },
  topo: {
    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attribution: '&copy; <a href="https://opentopomap.org">OpenTopoMap</a> contributors',
    maxZoom: 17,
  },
  cyclosm: {
    url: 'https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png',
    attribution: '&copy; <a href="https://www.cyclosm.org">CyclOSM</a> | OpenStreetMap contributors',
    maxZoom: 20,
  },
}

const TRAILS_OVERLAY = {
  url: 'https://tile.waymarkedtrails.org/hiking/{z}/{x}/{y}.png',
  attribution: '&copy; <a href="https://waymarkedtrails.org">Waymarked Trails</a>',
  maxZoom: 19,
  opacity: 0.7,
}

export function MapView() {
  const baseLayer = useMapStore((s) => s.baseLayer)
  const trailsOverlay = useMapStore((s) => s.trailsOverlay)
  const tile = TILE_LAYERS[baseLayer]

  return (
    <MapContainer
      center={[45.46, 9.19]}
      zoom={7}
      style={{ flex: 1, height: '100%' }}
    >
      <TileLayer
        key={baseLayer}
        attribution={tile.attribution}
        url={tile.url}
        maxZoom={tile.maxZoom}
      />
      {trailsOverlay && (
        <TileLayer
          attribution={TRAILS_OVERLAY.attribution}
          url={TRAILS_OVERLAY.url}
          maxZoom={TRAILS_OVERLAY.maxZoom}
          opacity={TRAILS_OVERLAY.opacity}
        />
      )}
      <MapClickHandler />
      <WaypointMarkers />
      <RoutePolyline />
    </MapContainer>
  )
}
