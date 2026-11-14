# Data pipeline

The raw NASA downloads (several hundred MB) are **not** in this repository. The processed, map-ready outputs are in `img/`, `data/` and `pov/`. The scripts in `tools/` are kept as they were used, for transparency. They use absolute paths from the original working machine, so treat them as a record of the processing rather than a turnkey build.

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

## 3. Processing notes

- **Spirit coordinates:** `CORRECTED_X/Y` in the MER notebook are meters in an equirectangular projection centred on 175.5°E, so `lon = 175.5 + X / 59275.06` and `lat = Y / 59275.06`.
- **Spirit DEM:** the CTX/HiRISE DEM saturates at gray 255 in places. It was merged with upsampled MOLA-HRSC heights and calibrated to them (r = 0.88).
- **Elevation colors:** the overview and global layers share one range (−8,000 to +12,000 m), so colors match where they meet.
- **No-data:** HiRISE no-data is masked, so lander zones never fall into image gaps.
- **Resampling** uses PIL bicubic. Earlier scipy zoom output left a zero last column and was replaced.

## 4. Updating the rover paths

Curiosity and Perseverance are still driving. To update them:
1. Download the latest `MSL_waypoints.json` / `MSL_traverse.json` and `M20_waypoints.json` / `M20_traverse.json` from MMGIS.
2. Rebuild `traverse` and the "Today: latest position" event in `data/missions.json` (format: `[[lat, lon], …]`).
3. Update the odometry on the mission cards in `index.html`.
