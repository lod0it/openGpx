import { create } from 'zustand'

export type BaseLayer = 'osm' | 'topo' | 'cyclosm'

interface MapStore {
  baseLayer: BaseLayer
  trailsOverlay: boolean
  setBaseLayer: (l: BaseLayer) => void
  setTrailsOverlay: (v: boolean) => void
}

export const useMapStore = create<MapStore>((set) => ({
  baseLayer: 'osm',
  trailsOverlay: false,
  setBaseLayer: (baseLayer) => set({ baseLayer }),
  setTrailsOverlay: (trailsOverlay) => set({ trailsOverlay }),
}))
