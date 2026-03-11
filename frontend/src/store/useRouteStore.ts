import { create } from 'zustand'
import { nanoid } from 'nanoid'
import { arrayMove } from '@dnd-kit/sortable'
import type { Waypoint, SegmentOptions, ElevationPoint, RoadStats, GlobalFilters, ExtremeLogEntry } from '../types'
import { defaultGlobalFilters } from '../types'

interface RouteStore {
  waypoints: Waypoint[]
  geometry: [number, number][]
  distanceM: number | null
  durationS: number | null
  adventure: number
  segmentOptions: Record<string, SegmentOptions>
  globalFilters: GlobalFilters
  elevation: ElevationPoint[]
  maxElevation: number | null
  minElevation: number | null
  roadStats: RoadStats | null
  extremeLog: ExtremeLogEntry[]
  isLoading: boolean
  error: string | null

  addWaypoint: (wp: Omit<Waypoint, 'id'>) => void
  removeWaypoint: (id: string) => void
  reorderWaypoints: (oldIndex: number, newIndex: number) => void
  updateWaypointPosition: (id: string, lat: number, lng: number) => void
  setAdventure: (adventure: number) => void
  setSegmentOption: (waypointId: string, opts: SegmentOptions) => void
  setGlobalFilter: (patch: Partial<GlobalFilters>) => void
  setRoute: (result: {
    geometry: [number, number][]
    distanceM: number
    durationS: number
    elevation: ElevationPoint[]
    maxElevation: number | null
    minElevation: number | null
    roadStats: RoadStats
    extremeLog: ExtremeLogEntry[]
  }) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearAll: () => void
}

export const useRouteStore = create<RouteStore>((set) => ({
  waypoints: [],
  geometry: [],
  distanceM: null,
  durationS: null,
  adventure: 0,
  segmentOptions: {},
  globalFilters: defaultGlobalFilters,
  elevation: [],
  maxElevation: null,
  minElevation: null,
  roadStats: null,
  extremeLog: [],
  isLoading: false,
  error: null,

  addWaypoint: (wp) =>
    set((state) => ({
      waypoints: [...state.waypoints, { ...wp, id: nanoid() }],
      error: null,
    })),

  removeWaypoint: (id) =>
    set((state) => {
      const filtered = state.waypoints.filter((w) => w.id !== id)
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { [id]: _removed, ...restOpts } = state.segmentOptions
      return {
        waypoints: filtered,
        segmentOptions: restOpts,
        geometry: filtered.length < 2 ? [] : state.geometry,
        distanceM: filtered.length < 2 ? null : state.distanceM,
        durationS: filtered.length < 2 ? null : state.durationS,
        elevation: filtered.length < 2 ? [] : state.elevation,
        roadStats: filtered.length < 2 ? null : state.roadStats,
        extremeLog: filtered.length < 2 ? [] : state.extremeLog,
      }
    }),

  reorderWaypoints: (oldIndex, newIndex) =>
    set((state) => ({
      waypoints: arrayMove(state.waypoints, oldIndex, newIndex),
    })),

  updateWaypointPosition: (id, lat, lng) =>
    set((state) => ({
      waypoints: state.waypoints.map((w) => (w.id === id ? { ...w, lat, lng } : w)),
    })),

  setAdventure: (adventure) => set({ adventure }),

  setSegmentOption: (waypointId, opts) =>
    set((state) => ({
      segmentOptions: { ...state.segmentOptions, [waypointId]: opts },
    })),

  setGlobalFilter: (patch) =>
    set((state) => ({
      globalFilters: { ...state.globalFilters, ...patch },
    })),

  setRoute: ({ geometry, distanceM, durationS, elevation, maxElevation, minElevation, roadStats, extremeLog }) =>
    set({ geometry, distanceM, durationS, elevation, maxElevation, minElevation, roadStats, extremeLog, isLoading: false, error: null }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error, isLoading: false }),

  clearAll: () =>
    set({
      waypoints: [],
      geometry: [],
      distanceM: null,
      durationS: null,
      segmentOptions: {},
      elevation: [],
      maxElevation: null,
      minElevation: null,
      roadStats: null,
      extremeLog: [],
      error: null,
    }),
}))
