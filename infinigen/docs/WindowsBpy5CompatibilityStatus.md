# Windows + Blender 5 Compatibility Status

Status snapshot: May 1, 2026.

This document is a practical handoff for running Infinigen locally on native Windows with Python 3.13, Blender Python (`bpy`) 5.1, NumPy 2.x, and native OpenCV. It records what currently works, what is still blocked, and where the latest smoke-test outputs live.

## Current Summary

- Native `cv2` imports successfully.
- `bpy` imports successfully from the local Python environment.
- Indoor scene generation has a known-good coarse reference.
- Nature generation works on the no-terrain path through coarse, populate, fine-terrain no-op handoff, and mesh-save.
- Full terrain generation is still blocked on native terrain shared libraries on Windows.
- Rendering the populated no-terrain nature scene is still blocked by memory pressure in Cycles / OPTIX.
- The May 1 all-asset smoke baseline covered 301 curated assets and saved `.blend` files without rendering.
- After follow-up fixes, the 4 original indoor mesh failures now pass isolated rechecks.

## Local Environment

- OS: Windows x86_64
- Repo root: `D:\MyFiles\General_Agent_Workspace\scene_generation\infinigen`
- Python: `D:\Python313\python.exe`
- Python version: 3.13
- NumPy version: 2.4.4
- Blender Python (`bpy`) version: 5.1.1
- OpenCV (`cv2`) version: 4.13.0

The repo metadata still targets older package versions such as `python==3.11.*`, `numpy<2`, and `bpy==4.2.0`. The results below are for the local environment listed above, not the original upstream target environment.

Quick environment check:

```powershell
python -c "import bpy, numpy, cv2; print('bpy', bpy.app.version_string); print('numpy', numpy.__version__); print('cv2', cv2.__version__)"
```

Expected current output:

```text
bpy 5.1.1
numpy 2.4.4
cv2 4.13.0
```

## Non-Fatal Local Warnings

These warnings are expected in this local setup and do not by themselves mean a smoke test failed:

- Blender extension cache permission warnings under `%APPDATA%\Blender Foundation\Blender\5.1`
- optional addon warnings for `real_snow`
- HIP / GPU backend initialization warnings on this machine
- `scene.blend@` save warnings from Blender 5.1
- `Unable to remove directory` after short `bpy` runs

## Blender MCP Notes

Blender MCP runs inside the currently open Blender process. That process is not guaranteed to have the same import paths as `D:\Python313\python.exe`.

For live MCP edits that directly call Infinigen factories, set the Blender process import path before importing Infinigen:

```python
import sys

repo_root = r"D:\MyFiles\General_Agent_Workspace\scene_generation\infinigen"
py313_site = r"D:\Python313\Lib\site-packages"

for path in [py313_site, repo_root]:
    while path in sys.path:
        sys.path.remove(path)
sys.path.insert(0, repo_root)
sys.path.insert(1, py313_site)
```

If temporary fake modules were injected during debugging, remove them from `sys.modules` before retrying. If Infinigen was imported while those fake modules were present, also purge `infinigen` and `infinigen.*` from `sys.modules` before a clean import.

## Scene Pipeline Smoke Status

### Indoors

Known-good coarse command:

```powershell
python -m infinigen_examples.generate_indoors --seed 0 --task coarse --output_folder outputs/system_smoke/indoors/coarse_live11 -g fast_solve.gin singleroom.gin -p compose_indoors.terrain_enabled=False -p compose_indoors.restrict_single_supported_roomtype=True
```

Result: passed.

Reference output:

- `outputs/system_smoke/indoors/coarse_live11/scene.blend`
- `outputs/system_smoke/indoors/coarse_live11/solve_state.json`
- `outputs/system_smoke/indoors/coarse_live11/optim_records.csv`

### Nature With Full Terrain

Attempted command:

```powershell
python -m infinigen_examples.generate_nature --seed 0 --task coarse -g desert.gin simple.gin --output_folder outputs/system_smoke/nature/coarse_live2
```

Result: blocked.

Observed blocker:

- `FileNotFoundError` for `infinigen/terrain/lib/cpu/elements/waterbody.so`

Current conclusion:

- This is a native Windows terrain-build artifact issue, not the main Blender 5 API blocker.
- `docs/Installation.md` marks `Terrain (CPU)` as unsupported for native `Windows x86_64`.
- `scripts/install/compile_terrain.sh` is a Unix shell build path that produces `.so` artifacts.

### Nature Without Terrain

Coarse no-terrain command:

```powershell
python -m infinigen_examples.generate_nature --seed 0 --task coarse -g desert.gin simple.gin --output_folder outputs/system_smoke/nature/coarse_no_terrain4 -p compose_nature.terrain_enabled=False
```

Populate no-terrain command:

```powershell
python -m infinigen_examples.generate_nature --seed 0 --task populate --input_folder outputs/system_smoke/nature/coarse_no_terrain4 --output_folder outputs/system_smoke/nature/populate_no_terrain3 -g desert.gin simple.gin -p compose_nature.terrain_enabled=False populate_scene.populate_bushes_enabled=False
```

Fine-terrain no-terrain handoff command:

```powershell
python -m infinigen_examples.generate_nature --seed 0 --task fine_terrain --input_folder outputs/system_smoke/nature/populate_no_terrain3 --output_folder outputs/system_smoke/nature/fine_terrain_no_terrain1 -g desert.gin simple.gin -p compose_nature.terrain_enabled=False populate_scene.populate_bushes_enabled=False
```

Mesh-save command:

```powershell
python -m infinigen_examples.generate_nature --seed 0 --task mesh_save --input_folder outputs/system_smoke/nature/populate_no_terrain3 --output_folder outputs/system_smoke/nature/mesh_save_no_terrain1 -g desert.gin simple.gin -p compose_nature.terrain_enabled=False populate_scene.populate_bushes_enabled=False
```

Result: passed through coarse, targeted populate, fine-terrain no-op handoff, and mesh-save.

Reference outputs:

- `outputs/system_smoke/nature/coarse_no_terrain4/scene.blend`
- `outputs/system_smoke/nature/populate_no_terrain3/scene.blend`
- `outputs/system_smoke/nature/fine_terrain_no_terrain1/scene.blend`
- `outputs/system_smoke/nature/mesh_save_no_terrain1/frame_0001/mesh/saved_mesh_0001.npz`

Render follow-up:

- GPU render from `populate_no_terrain3` failed on April 20, 2026 with `OPTIX_ERROR_INTERNAL_COMPILER_ERROR` followed by GPU out-of-memory.
- CPU-only render also failed on April 20, 2026 with Cycles out-of-memory after reducing samples and saved passes.
- Current render blocker is scene memory pressure, not a Python import or driver exception.

## All-Asset Smoke Test

Run date: May 1, 2026.

Output root:

- `outputs/system_smoke/all_assets_20260501/full_blends_realtime`

This run exercised the curated asset lists, saved `.blend` files, and did not render.

Baseline result from `final_status_from_status_json.csv`:

| Group | Total | Pass | Fail |
| --- | ---: | ---: | ---: |
| indoor_meshes | 91 | 87 | 4 |
| nature_meshes | 82 | 67 | 15 |
| materials | 51 | 51 | 0 |
| materials_deprecated | 55 | 54 | 1 |
| scatters | 22 | 18 | 4 |
| total | 301 | 277 | 24 |

Baseline failure list:

- indoor: `OvenFactory`, `AquariumTankFactory`, `SinkFactory`, `WallShelfFactory`
- nature meshes: `StarCoralFactory`, `TubeCoralFactory`, `BeetleFactory`, `CarnivoreFactory`, `FishFactory`, `FruitFactoryCoconutgreen`, `LeafFactoryBroadleaf`, `LeafFactoryMaple`, `LeafFactoryPine`, `DustMoteFactory`, `SnowflakeFactory`, `FernFactory`, `BushFactory`, `LeafBananaTreeFactory`, `PlantBananaTreeFactory`
- deprecated materials: `BarkBirch`
- scatters: `Fern`, `GroundTwigs`, `Ivy`, `Snowlayer`

Failure categories observed in the baseline:

- Blender 5 API drift, such as enum spelling changes and removed shader nodes
- empty material slots caught by the smoke validator
- unapplied Geometry Nodes modifiers caught by the smoke validator
- missing optional addon dependency for `Snowlayer`
- high-memory failures in very large procedural assets or scatters

Follow-up indoor recheck after fixes:

| Asset | Recheck Result | Saved Blend Size | Notes |
| --- | --- | ---: | --- |
| `OvenFactory` | pass | 2.74 MB | isolated smoke recheck |
| `AquariumTankFactory` | pass | 519.10 MB | still very high geometry count |
| `SinkFactory` | pass | 0.26 MB | isolated smoke recheck |
| `WallShelfFactory` | pass | 0.10 MB | isolated smoke recheck |

Follow-up output root:

- `outputs/system_smoke/indoor_fixups_recheck_20260501`

Current interpretation:

- The original indoor baseline failures have been repaired and rechecked individually.
- A full 301-asset rerun has not yet been completed after the follow-up fixes.
- Remaining known failures are concentrated in nature meshes, deprecated material compatibility, and scatters.

## Large Blend Notes

The largest saved `.blend` files in the May 1 baseline were:

| Asset | Group | Size |
| --- | --- | ---: |
| `BushFactory` | nature_meshes | 1043.91 MB |
| `AquariumTankFactory` | indoor_meshes | 1042.93 MB baseline, 519.10 MB after orphan purge recheck |
| `FruitContainerFactory` | indoor_meshes | 643.25 MB |
| `CactusFactory` / `ColumnarCactusFactory` | nature_meshes | 524.37 MB |
| `GlobularCactusFactory` | nature_meshes | 321.18 MB |
| `LargePlantContainerFactory` | indoor_meshes | 189.18 MB |

Size analysis:

- `AquariumTankFactory` had a large orphan mesh in the baseline save. Saving after orphan purge cut the file roughly in half without changing visible geometry.
- `FruitContainerFactory` stayed at about 643 MB after orphan purge. Its size is from baked visible geometry, mainly realized fruit scatter.
- Cactus, bush, and large plant assets are large because of baked remesh/scatter/detail geometry. Meaningful reductions require either preserving instances/Geometry Nodes instead of baking, or adding lower-density/LOD paths.

## Compatibility Fixes Already Applied

The compatibility work so far has focused on Blender 5 / NumPy 2 behavior:

- Convert NumPy boolean scalars to plain Python `bool` before writing Blender RNA selection properties.
- Make UV read/write resilient when `uv_layers.active is None`.
- Add fallback handling for edge-loop selection operators across Blender versions.
- Force Geometry Nodes `Mesh Boolean` to use `EXACT` solver when legacy options are requested.
- Make node input lookup tolerant of disabled-but-present sockets.
- Replace removed legacy HSV shader node usage with Blender 5-compatible color nodes where patched.
- Allow no-terrain camera preprocessing to accept a single Blender object as `scene_objs`.
- Add targeted fallbacks for a few asset-specific smoke failures found during indoor validation.

Representative files touched during compatibility work include:

- `infinigen/core/nodes/node_wrangler.py`
- `infinigen/core/nodes/utils.py`
- `infinigen/core/surface.py`
- `infinigen/assets/utils/nodegroup.py`
- `infinigen/assets/objects/appliances/oven.py`
- `infinigen/assets/objects/decor/aquarium_tank.py`
- `infinigen/assets/objects/lamp/lamp.py`
- `infinigen/assets/objects/lamp/ceiling_classic_lamp.py`
- `infinigen/assets/objects/seating/bedframe.py`
- `infinigen/assets/objects/table_decorations/sink.py`

## Recommended Next Steps

For environment validation:

1. Treat native OpenCV as working.
2. Keep full-terrain validation off native Windows unless terrain libraries are built in a supported environment.
3. Use the no-terrain nature chain for local Blender 5 compatibility work.
4. Use `outputs/system_smoke/indoors/coarse_live11` as the current indoor scene reference.

For asset validation:

1. Rerun the full 301-asset smoke after the latest indoor and node compatibility fixes.
2. Triage remaining nature/material/scatter failures by category: API drift first, missing optional dependency second, memory-heavy generators separately.
3. For very large `.blend` files, separate no-quality-loss cleanup from real geometry reduction. Orphan purge is safe; reducing baked scatter/remesh detail is a modeling or LOD decision.
