import { create } from 'zustand'
import { nanoid } from 'nanoid'
import { arrayMove } from '@dnd-kit/sortable'
import type { Waypoint, RouteProfile } from '../types'

interface RouteStore {
  waypoints: Waypoint[]
  geometry: [number, number][]
  distanceM: number | null
  durationS: number | null
  profile: RouteProfile
  isLoading: boolean
  error: string | null

  addWaypoint: (wp: Omit<Waypoint, 'id'>) => void
  removeWaypoint: (id: string) => void
  reorderWaypoints: (oldIndex: number, newIndex: number) => void
  updateWaypointPosition: (id: string, lat: number, lng: number) => void
  setProfile: (profile: RouteProfile) => void
  setRoute: (geometry: [number, number][], distanceM: number, durationS: number) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearAll: () => void
}

export const useRouteStore = create<RouteStore>((set) => ({
  waypoints: [],
  geometry: [],
  distanceM: null,
  durationS: null,
  profile: 'standard',
  isLoading: false,
  error: null,

  addWaypoint: (wp) =>
    set((state) => ({
      waypoints: [...state.waypoints, { ...wp, id: nanoid() }],
      error: null,
    })),

  removeWaypoint: (id) =>
    set((state) => ({
      waypoints: state.waypoints.filter((w) => w.id !== id),
      geometry: state.waypoints.filter((w) => w.id !== id).length < 2 ? [] : state.geometry,
      distanceM: state.waypoints.filter((w) => w.id !== id).length < 2 ? null : state.distanceM,
      durationS: state.waypoints.filter((w) => w.id !== id).length < 2 ? null : state.durationS,
    })),

  reorderWaypoints: (oldIndex, newIndex) =>
    set((state) => ({
      waypoints: arrayMove(state.waypoints, oldIndex, newIndex),
    })),

  updateWaypointPosition: (id, lat, lng) =>
    set((state) => ({
      waypoints: state.waypoints.map((w) => (w.id === id ? { ...w, lat, lng } : w)),
    })),

  setProfile: (profile) => set({ profile }),

  setRoute: (geometry, distanceM, durationS) =>
    set({ geometry, distanceM, durationS, isLoading: false, error: null }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error, isLoading: false }),

  clearAll: () =>
    set({
      waypoints: [],
      geometry: [],
      distanceM: null,
      durationS: null,
      error: null,
    }),
}))
