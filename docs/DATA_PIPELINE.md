# Data pipeline

The raw NASA downloads (several hundred MB) are **not** in this repository. The processed, map-ready outputs are in `img/`, `data/` and `pov/`. The scripts in `tools/` are kept as they were used, for transparency. All paths go through `tools/paths.py`: outputs are written into the repository, and raw downloads are read from the folder in the `MAREK_RAW` environment variable (default `raw/` in the repository). Run them from the repository root, for example `MAREK_RAW=/path/to/downloads python3 tools/v13.py`. Only `v13.py` needs nothing beyond the repository itself.

## 1. Download

The data was fetched from the official services, using a browser session where a service required one:

| Data | Service |
|---|---|
| Imagery and THEMIS | Mars Trek WMTS tiles, `https://trek.nasa.gov/tiles/Mars/EQ/{layer}/1.0.0/default/default028mm/{z}/{row}/{col}.{png,jpg}`, stitched into one image per area |
| DEMs (raw values) | Mars Trek ArcGIS ImageServer, `…/trekarcgis/rest/services/{layer}/ImageServer/exportImage` (Float32 / Int16 TIFF) |
| Geology | USGS ArcGIS FeatureServer `Tanaka_et_al_2014_Mars_Global_Map_Features/FeatureServer/3`, queried in lat/lon (`outSR=104905`, `maxAllowableOffset=0.03`) |
| Rover paths | NASA MMGIS JSON (`mars.nasa.gov/mmgis-maps/{MSL,M20}/Layers/json/…`); PDS MER Analyst's Notebook `MERA_traverse.csv` |
| Raw images | `mars.nasa.gov/rss/api/?feed=raw_images&category=mars2020&feedtype=json&sol=N` (Perseverance), MSL raw-image archive (Curiosity) |

Large binary data was moved out of the browser as gzip + base64 chunks and reassembled by `tools/assemble.py`. Int16 DEMs were delta-encoded per row before compression.

## 2. Processing scripts

| Script | What it does |
|---|---|
| `assemble.py` | Reassembles chunked downloads and decodes base64 and gzip. |
| `v2.py` | Color ramps (elevation, thermal), hillshade, `save_layers()` (writes `*_elev.png`, `*_tday/tnight.jpg`, `*_grid.png`) and `meta.json`. |
| `v2b.py` | `Grid` class: roughness from HiRISE, lander scoring, Dijkstra/Tobler routes. Builds the Curiosity and Spirit missions. |
| `v3.py` | Jezero and overview layers. |
| `v3b.py` | Perseverance mission and Ingenuity flights. |
| `v4.py` | Whole-planet layers and `global_grid.png`. |
| `geol.py`, `geol2.py` | Rasterise the USGS SIM 3292 polygons (even-odd fill for holes, nearest-neighbour gap fill) into colored layers and unit-index rasters. |
| `v8.py`, `v9.py` | Current routing: slope-limited (15°) least-time routes, hazard outlines (`hazards.json`). |
| `v13.py` | Return time for every route (`back_h`: the same path walked from target to lander, same speed model) and the Gale boxwork science stop with its route. Run from the repo root. |
| `v14.py` | Removes the separate "resources (water)" marker type: the Gediz Vallis site becomes pure sulfur (S), the Gusev soils sulfate (SO₄) and the Jezero delta a science stop (★). |
| `v15.py` | Removes three plan markers: the Jezero delta science stop, the Husband Hill lookout (Spirit) and the Gale boxwork science stop with its route. Run it after `v13.py`, which adds the boxwork stop. |
| `v16.py` | Jezero: removes the Ingenuity site and adds safest routes to the two sulfate deposits, Hogwallow Flats (2.73 km) and Yori Pass / Hidden Harbor (2.19 km), with the same rules as the other routes. |

## 3. Processing notes

- **Spirit coordinates:** `CORRECTED_X/Y` in the MER notebook are meters in an equirectangular projection centred on 175.5°E, so `lon = 175.5 + X / 59275.06` and `lat = Y / 59275.06`.
- **Spirit DEM:** rebuilt from the raw Float32 values of the Mars Trek `DEM_1m_ColumbiaHills` ImageServer (exported at ~5 m, block-averaged to the ~10 m grid). The earlier version used an 8-bit gray DEM that saturated on Husband and McCool Hills (a flat plateau at −1,871 m); the summit now correctly reaches about −1,859 m on Spirit's path.
- **Slopes and no-go zones:** terrain slope is the gradient magnitude of each DEM grid (Gale ~30 m, Gusev ~10 m, Jezero ~19 m cells; Jezero is upsampled from the 200 m MOLA/HRSC blend, so its slopes are smoothed and likely underestimated). Cells steeper than 15° are drawn as red no-go hatching, and the safest routes (`tools/v8.py`) never enter them; they also stay 50 m outside every hazard zone.
- **THEMIS global IR (globe and overview):** the night mosaic's overview tiles (zoom 2–3) are empty over 45°W–0°, 0–65°S, so that block was rebuilt from the same mosaic's zoom-4 to zoom-6 tiles and brightness-matched. Nothing is interpolated: real orbit gaps and the poles beyond 65° (outside THEMIS coverage) stay dark as no-data (`tools/v11.py`).
- **Elevation colors:** the overview and global layers share one range (−8,000 to +12,000 m), so colors match where they meet.
- **No-data:** HiRISE no-data is masked, so lander zones never fall into image gaps.
- **Resampling** uses PIL bicubic. Earlier scipy zoom output left a zero last column and was replaced.

## 4. Updating the rover paths

Curiosity and Perseverance are still driving. To update them:
1. Download the latest `MSL_waypoints.json` / `MSL_traverse.json` and `M20_waypoints.json` / `M20_traverse.json` from MMGIS.
2. Rebuild `traverse` and the "Today: latest position" event in `data/missions.json` (format: `[[lat, lon], …]`).
3. Update the odometry on the mission cards in `index.html`.
