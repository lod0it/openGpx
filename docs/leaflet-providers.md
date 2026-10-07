# Leaflet Providers — Reference for openGpx

A curated list of tile providers and overlay layers selected for use in openGpx.
Use this document as reference when adding new layers to `MapPanel.tsx` and `useMapStore.ts`.

---

## Summary

| Name | Type | API Key | Free Tier | Best for |
|---|---|---|---|---|
| OpenStreetMap.HOT | base layer | No | Unlimited | High-readability general map |
| Stadia.AlidadeSmoothDark | base layer | Yes | 200k tiles/month | Dark theme |
| Stadia.Outdoors | base layer | Yes | 200k tiles/month | Mountain / off-road riding |
| Jawg.Streets | base layer | Yes | 75k tiles/month | High-quality street map |
| Esri.WorldShadedRelief | base layer / overlay | No | Unlimited | Terrain relief visualization |

---

## Layers

### OpenStreetMap.HOT

**Type:** base layer

**Visual style:** Bright, high-contrast colors with emphasis on roads, buildings, and public infrastructure. Designed by the Humanitarian OpenStreetMap Team for maximum readability in crisis-mapping contexts. Labels are clear and legible at all zoom levels.

**Use case in openGpx:** Good default alternative to the standard OSM layer when readability is the priority. Works well on both light and dark UI themes.

**API key:** Not required.

**Leaflet string:**
```js
L.tileLayer.provider('OpenStreetMap.HOT')
```

**Tile URL pattern:**
```
https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png
```

---

### Stadia.AlidadeSmoothDark

**Type:** base layer

**Visual style:** Dark background with muted, smooth colors and clean typography. Minimal visual noise — roads are clearly distinguishable without being harsh on the eyes. Ideal companion for the app's dark theme.

**Use case in openGpx:** Primary dark-mode base layer. Pairs well with `[data-theme="dark"]` in the app.

**API key:** Required (free tier available).
- Register at: https://stadia.com/
- Free tier: 200,000 tiles/month

**Leaflet string:**
```js
L.tileLayer.provider('Stadia.AlidadeSmoothDark', { apikey: 'YOUR_API_KEY' })
```

---

### Stadia.Outdoors

**Type:** base layer

**Visual style:** Outdoor-focused map with contour lines, elevation shading, trail networks, and mountain pass labels. Colors are earthy and terrain-aware. Shows unpaved roads, hiking paths, and natural landmarks clearly.

**Use case in openGpx:** Best choice for motorcycle trips in mountainous or rural areas. Complements the Extreme routing feature by making passes and terrain clearly visible.

**API key:** Required (free tier available).
- Register at: https://stadia.com/
- Free tier: 200,000 tiles/month

**Leaflet string:**
```js
L.tileLayer.provider('Stadia.Outdoors', { apikey: 'YOUR_API_KEY' })
```

---

### Jawg.Streets

**Type:** base layer

**Visual style:** Clean, high-quality vector-based street map with well-balanced typography and color scheme. Roads are clearly categorized by type. Supports custom style configuration via the Jawg Maps dashboard (colors, language, POI visibility).

**Use case in openGpx:** High-quality street-level alternative to OpenStreetMap. Good for urban and mixed routes where road hierarchy needs to be clearly visible.

**API key:** Required (free tier available).
- Register at: https://www.jawg.io/
- Free tier: 75,000 tiles/month

**Leaflet string:**
```js
L.tileLayer.provider('Jawg.Streets', { accessToken: 'YOUR_ACCESS_TOKEN' })
```

---

### Esri.WorldShadedRelief

**Type:** base layer (can also be used as overlay on label-only layers)

**Visual style:** Grayscale terrain relief shading derived from SRTM elevation data. Shows mountain ranges, valleys, and landforms through hillshading. Contains no road labels or POIs — pure terrain visualization.

**Use case in openGpx:** Useful for visually understanding the orography along a route. Can be layered underneath a transparent label-only tile set for a hybrid effect, or used standalone when terrain context matters more than street detail.

**API key:** Not required.

**Leaflet string:**
```js
L.tileLayer.provider('Esri.WorldShadedRelief')
```

**Tile URL pattern:**
```
https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}
```
