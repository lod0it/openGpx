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
  extreme: boolean
  extreme_radius_km: number
  extreme_direction?: 'N' | 'S' | 'E' | 'O'
  extreme_loop: boolean
  extreme_pass_index: number
}

export const defaultSegmentOptions: SegmentOptions = {
  adventure: undefined,
  avoid_motorways: false,
  avoid_highways: false,
  avoid_primary: false,
  prefer_unpaved: false,
  prefer_secondary: false,
  extreme: false,
  extreme_radius_km: 20,
  extreme_direction: undefined,
  extreme_loop: false,
  extreme_pass_index: 0,
}

export interface GlobalFilters {
  avoid_motorways: boolean
  avoid_highways: boolean
  avoid_primary: boolean
  prefer_unpaved: boolean
  prefer_secondary: boolean
}

export const defaultGlobalFilters: GlobalFilters = {
  avoid_motorways: false,
  avoid_highways: false,
  avoid_primary: false,
  prefer_unpaved: false,
  prefer_secondary: false,
}

export interface ElevationPoint {
  d: number
  ele: number
}

export interface RoadStats {
  road_class: Record<string, number>
  surface: Record<string, number>
}

export interface ExtremeLogEntry {
  segment: number
  name: string
  lat: number
  lng: number
  ele: number
  ctd_m: number
  status: 'used' | 'unreachable' | 'no_passes'
  mode: string
  passes_found: number
}

export interface RouteResult {
  distance_m: number
  duration_s: number
  geometry: [number, number][]
  elevation: ElevationPoint[]
  max_elevation: number | null
  min_elevation: number | null
  road_stats: RoadStats
  extreme_log: ExtremeLogEntry[]
}

export interface GeocodeResult {
  display_name: string
  lat: number
  lng: number
}
