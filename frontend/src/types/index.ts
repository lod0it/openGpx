export interface Waypoint {
  id: string
  lat: number
  lng: number
  name?: string
}

export type RouteProfile = 'standard' | 'avoid_tolls' | 'scenic'

export interface RouteResult {
  distance_m: number
  duration_s: number
  geometry: [number, number][]
}

export interface GeocodeResult {
  display_name: string
  lat: number
  lng: number
}
