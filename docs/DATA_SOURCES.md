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
| Elevation | Gusev | MRO HiRISE Columbia Hills DEM (`DEM_1m_ColumbiaHills`, Float32 ImageServer) | 1 m → ~10 m grid |
| Thermal | whole planet, sites | Mars Odyssey THEMIS day and night IR global mosaics | 100 m (65°S–65°N) |
| Geology | whole planet | USGS SIM 3292 (Tanaka et al. 2014), 1:20,000,000 | rasterised 4096×2048 (global), 36 px/° (overview) |

Elevation values are meters relative to the Mars areoid/datum. Thermal brightness is relative, not calibrated temperature.

## Layer details

| Detail | Dataset | Notes |
|---|---|---|
| Contour lines and spot heights | Same DEMs as the Elevation layer | Steps: 2 km (planet), 1 km (overview), 100 m (Gale), 10 m (Gusev), 50 m (Jezero) |
| Real ground and air temperatures, Gale | Curiosity REMS daily min/max (NASA/JPL, CAB INTA-CSIC outreach feed) | 4,694 sols, sol 10–4995; values outside −110…+40 °C dropped |
| Air temperatures, Jezero | Perseverance MEDA daily min/max (same feed) | Sols 1130–1133 (Apr 2024) |
| Night ground temperature, Jezero | MEDA, sols 128–188 | ≈ 200 K, EMIRS–rover comparison (arXiv 2204.12850) |
| Gusev surface temperatures, thermal inertia | Mini-TES | Spanovich et al. 2006, Icarus 180; Fergason et al. 2006, JGR 111 |
| Thermal inertia (global) | MGS TES (Mars Trek `TES_Thermal_Inertia`) | Values read back from the 25–600 color scale |
| Ground layer (walking conditions) | Derived from the MGS TES thermal inertia above (`tools/v12.py`) | Interpretation in 4 classes: < 100 soft dust, 100–250 sand, 250–400 coarse sand / duricrust, > 400 rock |
| Aqueous minerals | Ehlmann & Edwards 2014 (Mars Trek feature service) | 4,572 points: phyllosilicate, sulfate, chloride, silica, carbonate |
| Hydrous minerals | Carter et al. 2013, JGR 118 (Mars Trek feature service) | 1,648 CRISM/OMEGA detections |
| Rover mineralogy | Bish et al. 2013 (Science 341); Christensen et al. 2004 (Science 305); Morris et al. 2006 (JGR 111); Liu et al. 2022 (Science 377); Udry et al. 2022; Beyssac et al. 2023; Hurowitz et al. 2023 | Shown in the Geology legend |

## Rover paths and events

| Mission | Source | Coverage |
|---|---|---|
| Curiosity (MSL) | NASA/JPL MMGIS: `MSL_waypoints.json`, `MSL_traverse.json` | sols 0–5073 (official odometry 38.64 km) |
| Perseverance (M2020) | NASA/JPL MMGIS: `M20_waypoints.json`, `M20_traverse.json` | sols 0–2022 (official odometry 45.25 km) |
| Ingenuity | NASA/JPL MMGIS: `m20_heli_waypoints.json` | all 72 flights, sols 43–1036 |
| Spirit (MER-A) | PDS Geosciences Node, MER Analyst's Notebook: `MERA_traverse.csv` (corrected positions) | sols 1–2209 |

Every event and resource marker uses the rover's official position on the sol of that event.

## Resources layer (sulfur & concrete)

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

## Radiation

| Value | Used for | Source |
|---|---|---|
| **0.64 ± 0.12 mSv/day** mean dose equivalent rate (galactic cosmic rays) on the surface of Gale crater, ~300 sols, Aug 2012 – Jun 2013; absorbed dose 0.21 ± 0.04 mGy/day | Dose per walk on every route (route card and route panel) | Hassler, D. M. et al. 2014, "Mars' surface radiation environment measured with the Mars Science Laboratory's Curiosity rover", *Science* 343, 1244797, [doi:10.1126/science.1244797](https://doi.org/10.1126/science.1244797) (Curiosity RAD) |
| 600 mSv career effective-dose limit | Scale only | NASA-STD-3001 Vol. 1, [OCHMO technical brief OCHMO-TB-020](https://www.nasa.gov/wp-content/uploads/2023/03/radiation-protection-technical-brief-ochmo.pdf) |

## EVA limit

| Value | Used for | Source |
|---|---|---|
| EVAs of up to 8 h (6 ± 2 h) | EVA budget limit on every route | NASA EVA-EXP-0075, Exploration EVA concept of operations ([NTRS 20200001071](https://ntrs.nasa.gov/api/citations/20200001071/downloads/20200001071.pdf)); NASA EVA technology roadmaps, ICES-2025-61 (Mars EVA suit: "8-hour EVA", [NTRS 20250006297](https://ntrs.nasa.gov/api/citations/20250006297/downloads/ICES-2025-61%20Roadmaps%20Presentation.pdf)) |

## Rover images

- Curiosity: 14 Mastcam/Navcam raw images from the NASA MSL raw-image archive, at their MMGIS positions.
- Perseverance: 8 raw images (one per event sol) from the Mars 2020 raw-image feed.

## Credits

NASA/JPL-Caltech · University of Arizona (HiRISE) · Arizona State University (THEMIS) · Malin Space Science Systems (CTX, Mastcam, MAHLI) · USGS Astrogeology Science Center · ESA/DLR/FU Berlin (HRSC) · Cornell University (MER Pancam) · PDS Geosciences Node, Washington University in St. Louis.
