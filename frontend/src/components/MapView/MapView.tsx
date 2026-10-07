import { MapContainer, TileLayer } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { MapClickHandler } from './MapClickHandler'
import { WaypointMarkers } from './WaypointMarkers'
import { RoutePolyline } from './RoutePolyline'
import { ExtremeCircles } from './ExtremeCircles'
import { MapAutoFit } from './MapAutoFit'
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
  esriTopo: {
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, USGS, and the GIS User Community',
    maxZoom: 19,
  },
}

const HILLSHADE_OVERLAY = {
  url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}',
  attribution: 'Hillshade &copy; Esri, USGS, NOAA',
  maxZoom: 16,
  opacity: 0.5,
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
  const hillshadeOverlay = useMapStore((s) => s.hillshadeOverlay)
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
      {hillshadeOverlay && (
        <TileLayer
          attribution={HILLSHADE_OVERLAY.attribution}
          url={HILLSHADE_OVERLAY.url}
          maxZoom={HILLSHADE_OVERLAY.maxZoom}
          opacity={HILLSHADE_OVERLAY.opacity}
        />
      )}
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
      <ExtremeCircles />
      <MapAutoFit />
    </MapContainer>
  )
}
