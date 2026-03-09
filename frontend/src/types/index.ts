export interface Waypoint {
  id: string
  lat: number
  lng: number
  name?: string
}

export interface SegmentOptions {
  adventure?: number
  avoid_motorways: boolean
  avoid_highways: boolean
  avoid_primary: boolean
  prefer_unpaved: boolean
  prefer_secondary: boolean
  prefer_mountain_passes: boolean
}

export const defaultSegmentOptions: SegmentOptions = {
  adventure: undefined,
  avoid_motorways: false,
  avoid_highways: false,
  avoid_primary: false,
  prefer_unpaved: false,
  prefer_secondary: false,
  prefer_mountain_passes: false,
}

export interface GlobalFilters {
  avoid_motorways: boolean
  avoid_highways: boolean
  avoid_primary: boolean
  prefer_unpaved: boolean
  prefer_secondary: boolean
  prefer_mountain_passes: boolean
}

export const defaultGlobalFilters: GlobalFilters = {
  avoid_motorways: false,
  avoid_highways: false,
  avoid_primary: false,
  prefer_unpaved: false,
  prefer_secondary: false,
  prefer_mountain_passes: false,
}

export interface ElevationPoint {
  d: number
  ele: number
}

export interface RoadStats {
  road_class: Record<string, number>
  surface: Record<string, number>
}

export interface RouteResult {
  distance_m: number
  duration_s: number
  geometry: [number, number][]
  elevation: ElevationPoint[]
  max_elevation: number | null
  min_elevation: number | null
  road_stats: RoadStats
}

export interface GeocodeResult {
  display_name: string
  lat: number
  lng: number
}
