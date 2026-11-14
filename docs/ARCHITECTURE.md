# Architecture

A single static page (`index.html`) with two parts:

```
┌──────────────────────────── index.html ─────────────────────────────┐
│  #intro  (ES module, three.js)        #app  (Leaflet, classic JS)   │
│  ─ 3D globe, textures img/global_*    ─ header: views, Globe, Data   │
│  ─ zoom-to-cursor, drag, labels       ─ left: layers, overlays, key  │
│  ─ enter(lat,lon,alt) ───────────────▶ window.APP.enterAt / go()      │
│                                       ─ map: image overlays + layers │
│                                       ─ right: mission panel         │
└───────────────────────────────────────────────────────────────────────┘
```

## Libraries

- `lib/leaflet.js` 1.9.4: the 2D map.
- `lib/three.module.min.js` 0.160: the globe, loaded through an import map.

Both are vendored, so the page needs no CDN and makes no external requests.

## Coordinate system

- Planetocentric latitude and **east longitude 0–360°** (as in Mars Trek and USGS).
- Leaflet uses `L.CRS.EPSG4326`; at zoom `z` there are `1.422 × 2^z` pixels per degree.
- The global textures cover −180…180°, so they are drawn **twice** (at −180…180° and 180…540°). Map bounds are 0…360°, so the map never ends at the antimeridian, even east of Spirit (175.5°E).
- Distances use a sphere of radius 3,389.5 km.

## Views

`VIEWS` / `key4` map each view to a data area:

| View | Area key | Image overlays shown |
|---|---|---|
| overview | overview | global + overview + gale + spirit + jezero |
| curiosity | gale | global + overview + gale (+ boxwork HiRISE) |
| spirit | spirit | global + overview + spirit |
| perseverance | jezero | global + overview + jezero |

`OV[area][layer]` holds a Leaflet `imageOverlay` for `vis`, `elev`, `tday`, `tnight` (and `geol` for global and overview).

## Data files

| File | Format |
|---|---|
| `data/meta.json` | per area: `bbox [lonW, latS, lonE, latN]`, grid `w × h`, `cell` size (m), elevation range `lo`/`hi`, legend range, color ramps |
| `data/*_grid.png` | hover grid: **R·256 + G** = elevation as 16-bit between `lo` and `hi`; **B** = slope × 4 (degrees) |
| `data/missions.json` | per mission: `traverse` `[[lat,lon],…]`, `events`, `lander`, `sites` (with `route.pts`), `heli` (Perseverance), `sulfur` (resources) |
| `data/geology.json` | USGS units: `code`, `name`, `group`, `char`, `interp`, `c` (color) |
| `data/geol_idx.png`, `geol_idx_ov.png` | 8-bit unit index (0 = none, n = `units[n-1]`), global and overview |
| `data/pov.json`, `pov_m20.json` | rover image file, sol, lat/lon, instrument, link to the original |

The PNG grids are read with `createImageBitmap(..., {colorSpaceConversion:'none', premultiplyAlpha:'none'})`, so the values are exact.

## Globe ↔ map hand-off

- `window.APP` exposes `map`, `go(view)`, `setBase(layer)` and `enterAt(lat, lon, altKm)`.
- When the globe camera goes below ~1.09 R, `enterAt` picks the nearest rover if it is within `max(350 km, 0.6 × altitude)`. Otherwise it opens the overview at the zoom that matches the altitude.
- The globe's chosen layer is passed to the map.

## Deployment

The site is static, so any web server works. GitHub Pages serves it from the repository root (`.nojekyll` turns off Jekyll processing).
