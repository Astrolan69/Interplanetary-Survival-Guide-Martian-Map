# Method

Everything in the **What happened**, **Sulfur & concrete** and data layers comes from NASA, USGS or peer-reviewed data. Everything marked **prediction** (lander zones, routes, site picks and ranking) is this project's own analysis.

## Sulfur concrete resources

**Goal:** find **binder** (elemental sulfur, or sulfates as ore) and **aggregate** (loose regolith ≤ 1 mm) close to each other and to a safe landing zone.

Sulfur concrete is hot-mixed at ~240 °C (sulfur melts at ~115 °C), cast and cooled. It needs no water. Wan et al. (2016) found the best Mars-simulant mix to be **50 % sulfur + 50 % regolith** with grains ≤ 1 mm, giving **> 50 MPa**. Mars' atmospheric pressure is enough to keep the sulfur from sublimating, which would be a problem on the Moon.

| Site | Binder | Aggregate | Distance binder ↔ aggregate | Verdict |
|---|---|---|---|---|
| **Gale** | Pure sulfur (Gediz Vallis) + Mg/Ca sulfates | Bagnold dune sand (sieved by Curiosity), Rocknest sand | ~6.8 km | **Best**: sulfur ready to melt, no chemistry needed |
| **Jezero** | Sulfates (Hogwallow Flats, Yori Pass) | Regolith samples at Observation Mountain | ~20 m (Yori Pass) | Good: sulfur must be extracted from sulfate |
| **Gusev** | Sulfate soils > 30 wt % SO₃ (Paso Robles, Arad, Tyrone) | Basaltic plains soil | ~2 km | Rich ore, but soft soil (Spirit was trapped at Troy) |

Extracting sulfur from sulfates (for example by carbothermal or hydrogen reduction) costs a lot of energy. That is why pure sulfur makes Gale the best site.

## Crew lander zone

The lander zone is computed on each site's DEM grid. For every cell:

```
score = mean_slope_400m / 2
      + 2.0 × roughness_norm      (HiRISE high-pass texture: boulders, craters)
      + 0.6 × elevation_norm      (lower = more atmosphere for braking)
      + distance_to_target / 4000 m
```

Cells are excluded if they are:
- closer than `dmin` or farther than `dmax` from the targets (to keep the plume away from science and heritage sites),
- in image no-data, at the grid edge, or in a no-go mask (for example 400 m around Troy).

| Site | Lander zone | Mean slope | Elevation |
|---|---|---|---|
| Gale | 4.7373°S 137.4023°E | 3.8° | −4,057 m |
| Gusev | 14.5756°S 175.5187°E | 0.9° | −1,938 m |
| Jezero | 18.4202°N 77.3994°E | 1.6° | −2,569 m |

## Walking routes

Routes are least-time paths found with Dijkstra on an 8-connected DEM grid:
- walking speed from **Tobler's hiking function**, `v = exp(−3.5 · |slope + 0.05|)`, scaled to ~3 km/h on flat ground (suited astronaut);
- slowed further by HiRISE roughness, `v / (1 + 2.5 · roughness)`;
- grades steeper than **15°** blocked (12° on the smoothest plains);
- pressurised-rover time assumes 8 km/h.

Each route reports distance, walking time, rover time, total climb and steepest grade.

## Other predicted sites

- **Hazards** are the steepest ~500 m patch near the work area (DEM), plus known soft soil (Troy).
- **Winter power** (Gusev) is a north-facing 8–20° slope near Home Plate. This is how Spirit survived winters.
- **Comms mast** (Gusev) is the Husband Hill summit, the highest point Spirit reached.

## Verification of rover paths

The paths were checked on 14 Nov 2026:

| Check | Curiosity | Perseverance | Spirit |
|---|---|---|---|
| Latest sol in today's official feed | 5073 = ours | 2022 = ours | mission ended 2010 |
| Official odometry vs our polyline | 38.64 km vs 37.95 km | 45.25 km vs 45.65 km | 7.73 km vs 7.07 km (localised positions; odometry also counts slip and back-and-forth) |
| Event markers vs official waypoint on that sol | 0 m | 0 m | on the traverse |
| Fit to orbital imagery | follows the Bagnold dune edge and the Gediz Vallis channel floor | on the controlled HiRISE base map | reaches the Bonneville crater rim and climbs Husband Hill on the USGS-controlled Columbia Hills HiRISE mosaic |
| Ingenuity final position | – | matches flight 72 (sol 1036) | – |

The published Spirit landing coordinates differ from each other by ~300 m (14.5692°S 175.4729°E vs 14.5718°S 175.4785°E). Our traverse start lies between them.
