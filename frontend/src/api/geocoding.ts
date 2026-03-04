import type { GeocodeResult } from '../types'

export async function searchLocation(query: string): Promise<GeocodeResult[]> {
  if (query.length < 2) return []

  const resp = await fetch(`/api/geocode?q=${encodeURIComponent(query)}`)

  if (!resp.ok) return []

  return resp.json()
}
