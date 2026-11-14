# Data sources

All map data is real NASA / USGS data, downloaded once and stored in this repository. The app makes **no network requests at runtime**.

## Challenge resources (NASA Space Apps 2026)

| # | Resource | Used for |
|---|---|---|
| 1 | [JPL Mars Trek](https://trek.nasa.gov/mars/) | All orbital imagery, elevation and thermal layers (WMTS tiles and ArcGIS ImageServer `exportImage` for raw DEM values). |
| 2 | [USGS-NASA Planetary Geologic Mapping Program](https://astrogeology-usgs.hub.arcgis.com/pages/interactive-maps-mars) | Geology layer from the *Geologic Map of Mars*, USGS SIM 3292 (Tanaka et al. 2014), via its ArcGIS FeatureServer (1,311 polygons, 44 units, official renderer colors). |
| 3 | [Curiosity's proposed path up Mount Sharp](https://science.nasa.gov/resource/curiositys-proposed-path-up-mount-sharp/) | Image in the Curiosity panel (NASA/JPL-Caltech/ESA/UArizona/JHUAPL/MSSS/USGS, PIA23179). |
| 4 | [NASA Worldview](https://worldview.earthdata.nasa.gov/) | The interface model: layer switching, legends, sources, opacity. |
| 5 | [Mars Perseverance Raw Images](https://mars.nasa.gov/mars2020/multimedia/raw-images/) | Raw images from the sol of each Perseverance event (Hazcam, Navcam, Mastcam-Z), selected through the gallery's JSON feed. |

## Map layers

| Layer | Area | Dataset (Mars Trek layer) | Resolution |
|---|---|---|---|
| Image | whole planet, overview | Viking MDIM 2.1 color mosaic | ~ 1 km/px (global), regional crop |
| Image | Gale | MRO HiRISE (Curiosity roving-site mosaic) | ~ 7 m/px in the app |
| Image | Gusev | MRO HiRISE Spirit roving-site mosaic | ~ 2.5 m/px |
| Image | Jezero | MRO HiRISE Jezero controlled ortho-mosaic over CTX | ~ 5 m/px |
| Elevation | whole planet | MGS MOLA 128/64 ppd merge (`mola128_mola64_merge_90Nto90S_SimpleC_clon0`) | ~ 460 m |
| Elevation | overview, Jezero | MOLA + HRSC blended DEM 200 m (`Mars_MOLA_blend200ppx_HRSC_DEM_clon0dd_200mpp_lzw`) | 200 m |
| Elevation | Gale | MRO HiRISE Gale DEM (`Gale_DEM_SMG_1m`), resampled | 1 m → 30 m grid |
| Elevation | Gusev | CTX/HiRISE Columbia Hills DEM, calibrated to MOLA/HRSC (r = 0.88) | ~ 10 m grid |
| Thermal | whole planet, sites | Mars Odyssey THEMIS day and night IR global mosaics | 100 m (65°S–65°N) |
| Geology | whole planet | USGS SIM 3292 (Tanaka et al. 2014), 1:20,000,000 | rasterised 4096×2048 (global), 36 px/° (overview) |

Elevation values are meters relative to the Mars areoid/datum. Thermal brightness is relative, not calibrated temperature.

## Rover paths and events

| Mission | Source | Coverage |
|---|---|---|
| Curiosity (MSL) | NASA/JPL MMGIS: `MSL_waypoints.json`, `MSL_traverse.json` | sols 0–5073 (official odometry 38.64 km) |
| Perseverance (M2020) | NASA/JPL MMGIS: `M20_waypoints.json`, `M20_traverse.json` | sols 0–2022 (official odometry 45.25 km) |
| Ingenuity | NASA/JPL MMGIS: `m20_heli_waypoints.json` | all 72 flights, sols 43–1036 |
| Spirit (MER-A) | PDS Geosciences Node, MER Analyst's Notebook: `MERA_traverse.csv` (corrected positions) | sols 1–2209 |

Every event and resource marker uses the rover's official position on the sol of that event.

## Sulfur & concrete layer

| Site | Finding | Source |
|---|---|---|
| Gediz Vallis (Gale) | Elemental sulfur crystals, sol 4200 (30 May 2024) | NASA/JPL news release, July 2024 |
| Sulfate-bearing unit (Gale) | Mg-sulfate, Ca-sulfate (gypsum), NaCl; drill "Canaima", sol 3612 | NASA/JPL news release, Oct 2022 |
| Bagnold dunes, Gobabeb (Gale) | Scooped, sieved active dune sand, Jan 2016 | NASA/JPL news release, Jan 2016 |
| Rocknest (Gale) | First scooped sand, Oct–Nov 2012 | Blake et al. 2013, *Science* 341 |
| Paso Robles, Arad, Tyrone (Gusev) | Ferric/Mg/Ca-sulfate soils, > 30 wt % SO₃ | Ming et al. 2006 *JGR*; Johnson et al. 2007 *GRL*; Lane et al. 2008 *Am. Mineral.*; Wang et al. 2008 *JGR* |
| Gusev plains, "Big Hole" | Basaltic soil trench, sols 113–115 | Wang et al. 2008 *JGR* |
| Hogwallow Flats, Yori Pass (Jezero) | Sulfate-cemented siltstone; Fe-Mg sulfates | Williams et al. LPSC 2023; Stack Morgan et al. GSA 2022; Hurowitz et al. Goldschmidt 2023 |
| Observation Mountain (Jezero) | Regolith samples Atmo Mountain and Crosswind Lake, sols 634/639 | NASA sample table; Simon et al. 2025 *PNAS* |
| Sulfur concrete | 50 % S + 50 % regolith, ≤ 1 mm, > 50 MPa | Wan, Wendner & Cusatis 2016, *Construction and Building Materials* |

## Rover images

- Curiosity: 14 Mastcam/Navcam raw images from the NASA MSL raw-image archive, at their MMGIS positions.
- Perseverance: 8 raw images (one per event sol) from the Mars 2020 raw-image feed.

## Credits

NASA/JPL-Caltech · University of Arizona (HiRISE) · Arizona State University (THEMIS) · Malin Space Science Systems (CTX, Mastcam, MAHLI) · USGS Astrogeology Science Center · ESA/DLR/FU Berlin (HRSC) · Cornell University (MER Pancam) · PDS Geosciences Node, Washington University in St. Louis.
