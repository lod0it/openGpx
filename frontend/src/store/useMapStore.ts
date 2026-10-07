import { create } from 'zustand'

export type BaseLayer = 'osm' | 'topo' | 'cyclosm' | 'esriTopo'

interface MapStore {
  baseLayer: BaseLayer
  trailsOverlay: boolean
  hillshadeOverlay: boolean
  setBaseLayer: (l: BaseLayer) => void
  setTrailsOverlay: (v: boolean) => void
  setHillshadeOverlay: (v: boolean) => void
}

export const useMapStore = create<MapStore>((set) => ({
  baseLayer: 'osm',
  trailsOverlay: false,
  hillshadeOverlay: false,
  setBaseLayer: (baseLayer) => set({ baseLayer }),
  setTrailsOverlay: (trailsOverlay) => set({ trailsOverlay }),
  setHillshadeOverlay: (hillshadeOverlay) => set({ hillshadeOverlay }),
}))
