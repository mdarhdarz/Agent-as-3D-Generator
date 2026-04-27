# Windows + Blender 5 Compatibility Status

Status snapshot as of April 27, 2026. System smoke-test results from April 20 remain the current known-good scene-pipeline references unless noted otherwise. A native OpenCV smoke test was added on April 27 after reinstalling `cv2`.

This document records the current local environment, the exact commands used to exercise the system-level pipelines, and the current validation status for:

- `infinigen_examples.generate_indoors`
- `infinigen_examples.generate_nature`

It is intended as a working handoff note for continued compatibility work on Blender 5 / Python 3.13.

## Local Environment

- OS: Windows x86_64
- Repo root: `D:\MyFiles\General_Agent_Workspace\scene_generation\infinigen`
- Python: `D:\Python313\python.exe`
- Python version: 3.13
- NumPy version: 2.4.4
- Blender Python (`bpy`) version: 5.1.1
- `cv2`: native OpenCV wheel available and tested in the current Python / NumPy environment

Notes:

- The current repo metadata still targets `python==3.11.*`, `numpy<2`, and `bpy==4.2.0`, but the validation below was performed against the local environment above.
- System-level commands run under `D:\Python313\python.exe`, while Blender MCP executes inside the currently open Blender process using Blender's bundled Python. These are not automatically the same import environment.
- For live MCP edits that directly call Infinigen factories in the current `.blend`, configure the Blender process `sys.path` before import:
  - first: `D:\MyFiles\General_Agent_Workspace\scene_generation\infinigen`
  - second: `D:\Python313\Lib\site-packages`
- Blender 5.1 emits several non-fatal warnings in this environment:
  - extension cache / lock permission errors under `%APPDATA%\Blender Foundation\Blender\5.1`
  - optional addon install warnings for `real_snow`
  - `scene.blend@` backup-file warnings when saving large scenes

## Command Patterns

### Blender MCP Direct Factory Calls

For reference-scene reconstruction, single-asset `.blend` generation is useful for isolated validation, but it is not required for inserting assets into the active reconstruction scene. The preferred live workflow is:

1. Use Blender MCP `execute_blender_code` inside the current `.blend`.
2. Configure import paths in the Blender process as described above.
3. Import or reload the target Infinigen factory.
4. Spawn/create the asset directly in the active scene.
5. Move it into the target collection, archive the old blockout, place it relationally, run bbox/visibility audits, restore the photo-match camera, and save.

If temporary fake modules such as fake `gin` or `tqdm` were injected during debugging, remove them from `sys.modules` before retrying with the real dependency environment. If Infinigen was imported while those fake modules were present, also purge `infinigen` and `infinigen.*` from `sys.modules` before a clean import.

Minimal MCP-side setup snippet:

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

### Native `cv2` / Individual Asset Smoke

Native `cv2` import check:

```powershell
python -c "import numpy, cv2; print(numpy.__version__); print(cv2.__version__); print(cv2.__file__)"
```

April 27, 2026 result:

- NumPy: `2.4.4`
- OpenCV: `4.13.0`
- `cv2.__file__`: `D:\Python313\Lib\site-packages\cv2\__init__.py`

Single-asset generation smoke:

```powershell
python -m infinigen_examples.generate_individual_assets -o outputs/system_smoke/individual_assets/cv2_native_plate_20260427 -f infinigen.assets.objects.tableware.PlateFactory -n 1 -D 0 -r none -s
```

Result: passed.

Important outputs:

- `outputs/system_smoke/individual_assets/cv2_native_plate_20260427/infinigen.assets.objects.tableware.PlateFactory_000/scene.blend`
- `outputs/system_smoke/individual_assets/cv2_native_plate_20260427/infinigen.assets.objects.tableware.PlateFactory_000/polycounts.txt`
- `outputs/system_smoke/individual_assets/cv2_native_plate_20260427/infinigen.assets.objects.tableware.PlateFactory_000/MaskTag.json`

Observed non-fatal Blender warnings remain consistent with the previous environment notes:

- extension cache permission warning under `%APPDATA%\Blender Foundation\Blender\5.1`
- HIP initialization warning on this machine
- `scene.blend@` backup-file warning while saving

### Indoors

Validated coarse command:

```bash
python -m infinigen_examples.generate_indoors --seed 0 --task coarse --output_folder outputs/system_smoke/indoors/coarse_live11 -g fast_solve.gin singleroom.gin -p compose_indoors.terrain_enabled=False -p compose_indoors.restrict_single_supported_roomtype=True
```

This uses:

- `fast_solve.gin` to shorten solver runtime
- `singleroom.gin` to keep the case small and deterministic
- `compose_indoors.terrain_enabled=False` to avoid background terrain
- `compose_indoors.restrict_single_supported_roomtype=True` to constrain room selection

### Nature

Full terrain command attempted:

```bash
python -m infinigen_examples.generate_nature --seed 0 --task coarse -g desert.gin simple.gin --output_folder outputs/system_smoke/nature/coarse_live2
```

Nature smoke command without terrain:

```bash
python -m infinigen_examples.generate_nature --seed 0 --task coarse -g desert.gin simple.gin --output_folder outputs/system_smoke/nature/coarse_no_terrain4 -p compose_nature.terrain_enabled=False
```

The no-terrain command exercises most of the Python / asset / camera / lighting path while bypassing the terrain shared-library dependency.

Follow-on populate smoke from the successful no-terrain coarse output:

```bash
python -m infinigen_examples.generate_nature --seed 0 --task populate --input_folder outputs/system_smoke/nature/coarse_no_terrain4 --output_folder outputs/system_smoke/nature/populate_no_terrain3 -g desert.gin simple.gin -p compose_nature.terrain_enabled=False populate_scene.populate_bushes_enabled=False
```

No-terrain fine-terrain handoff check:

```bash
python -m infinigen_examples.generate_nature --seed 0 --task fine_terrain --input_folder outputs/system_smoke/nature/populate_no_terrain3 --output_folder outputs/system_smoke/nature/fine_terrain_no_terrain1 -g desert.gin simple.gin -p compose_nature.terrain_enabled=False populate_scene.populate_bushes_enabled=False
```

No-terrain mesh export smoke after populate:

```bash
python -m infinigen_examples.generate_nature --seed 0 --task mesh_save --input_folder outputs/system_smoke/nature/populate_no_terrain3 --output_folder outputs/system_smoke/nature/mesh_save_no_terrain1 -g desert.gin simple.gin -p compose_nature.terrain_enabled=False populate_scene.populate_bushes_enabled=False
```

## Test Progress

### Native `cv2` single-asset smoke

Result: passed on April 27, 2026.

Confirmed:

- `cv2` imports from `D:\Python313\Lib\site-packages\cv2\__init__.py`
- OpenCV version is `4.13.0`
- `infinigen_examples.generate_individual_assets` can create and save a `PlateFactory` `.blend`

### `generate_indoors`

Result: passed.

Output folder:

- `outputs/system_smoke/indoors/coarse_live11`

Important outputs:

- `outputs/system_smoke/indoors/coarse_live11/scene.blend`
- `outputs/system_smoke/indoors/coarse_live11/solve_state.json`
- `outputs/system_smoke/indoors/coarse_live11/optim_records.csv`

Observed successful stage flow:

- `solve_rooms`
- `solve_large`
- `solve_medium`
- `solve_small`
- `populate_assets`
- `room_doors`
- `room_windows`
- `room_stairs`
- `skirting_floor`
- `room_walls`
- `room_floors`
- `room_ceilings`
- blend save

### `generate_nature` with full terrain

Result: blocked on native terrain libraries.

Observed failure:

- `FileNotFoundError` for `infinigen/terrain/lib/cpu/elements/waterbody.so`

Current conclusion:

- This is not primarily a Blender 5 API issue.
- It is a platform / build-artifact issue in the current native Windows environment.

Supporting repo evidence:

- `docs/Installation.md` marks `Terrain (CPU)` as `no` for `Windows x86_64`.
- `scripts/install/compile_terrain.sh` is a Unix shell build script that outputs `.so` terrain libraries.
- The local workspace does not currently contain `infinigen/terrain/lib/cpu/...` artifacts.

### `generate_nature` without terrain

Result: `coarse` passed, `populate` partially passed with a targeted stage disable, `fine_terrain` safely no-op'ed, `mesh_save` passed, `render` blocked by memory / Cycles backend limits.

Output folder:

- `outputs/system_smoke/nature/coarse_no_terrain4`
- `outputs/system_smoke/nature/populate_no_terrain3`
- `outputs/system_smoke/nature/fine_terrain_no_terrain1`
- `outputs/system_smoke/nature/mesh_save_no_terrain1`

Important outputs:

- `outputs/system_smoke/nature/coarse_no_terrain4/scene.blend`
- `outputs/system_smoke/nature/coarse_no_terrain4/pipeline_coarse.csv`
- `outputs/system_smoke/nature/populate_no_terrain3/scene.blend`
- `outputs/system_smoke/nature/populate_no_terrain3/pipeline_fine.csv`
- `outputs/system_smoke/nature/mesh_save_no_terrain1/frame_0001/mesh/saved_mesh_0001.npz`

Observed successful progress:

- terrain stage skipped through `compose_nature.terrain_enabled=False`
- fallback `noise_plane` path used
- bushes
- cactus
- camera preprocessing
- camera pose search
- lighting
- coarse terrain frustum split on fallback mesh
- rocks
- ground twigs
- leaf particles
- blend save

Populate follow-up observations:

- `populate_no_terrain1`: failed in `populate_bushes` with allocator null / out-of-memory during bush asset realization
- `populate_no_terrain2`: lowering `placement.populate_all.dist_cull=20` reduced bush count but still failed in a second `BushFactory`
- `populate_no_terrain3`: succeeded with `populate_scene.populate_bushes_enabled=False`
- successful populated stages in `populate_no_terrain3` included `populate_cactus`, `populate_clouds`, `populate_glowing_rocks`, all cached-fire populate no-ops, creature populate no-ops, and final blend save

Fine-terrain follow-up observations:

- `fine_terrain_no_terrain1` completed successfully
- because the no-terrain scene does not contain terrain atmosphere objects, `fine_terrain` was effectively skipped and the input scene was re-saved without touching native terrain code

Mesh-save follow-up observations:

- `mesh_save_no_terrain1` completed successfully
- produced static mesh plus per-frame mesh packs under `frame_0001` and `frame_0002`
- exporter handled very large tree assets by chunking into multiple `saved_mesh_XXXX.npz` files

Render follow-up observations:

- GPU render attempt from `populate_no_terrain3` failed on April 20, 2026 with `OPTIX_ERROR_INTERNAL_COMPILER_ERROR` followed by GPU out-of-memory
- CPU-only render attempt also failed on April 20, 2026 with Cycles out-of-memory, even after reducing samples and disabling saved passes
- current render blocker is scene memory pressure in Cycles rather than a Python exception in the Infinigen render driver

This confirms that, aside from the terrain native-library path and the current memory-heavy render path, a large portion of the nature system chain now runs under Blender 5.1 in the local environment.

## Compatibility Fixes Applied During Earlier Validation

The following compatibility fixes were added while bringing the pipelines forward before the April 27 native `cv2` reinstall:

- Convert NumPy boolean scalars to plain Python `bool` before writing Blender RNA selection properties.
- Make UV read/write resilient when `uv_layers.active is None`.
- Add fallback handling for edge-loop selection operators across Blender versions.
- Force Geometry Nodes `Mesh Boolean` to use `EXACT` solver when legacy inputs such as `Self Intersection` / `Hole Tolerant` are requested.
- Make node input lookup tolerant of disabled-but-present sockets.
- Replace legacy shader HSV node usage with `Separate Color` / `Combine Color` in HSV mode where Blender 5 removed old node ids.
- Allow no-terrain camera preprocessing to accept a single Blender object as `scene_objs`.
- Add a targeted fallback in `NatureShelfTrinketsFactory` so that a creature-only memory failure can degrade to a non-creature trinket during indoors population.

## Files Touched

Key files updated during the earlier Blender 5 compatibility round include:

- `infinigen/__init__.py`
- `infinigen/assets/utils/decorate.py`
- `infinigen/core/constraints/example_solver/geometry/planes.py`
- `infinigen/core/placement/split_in_view.py`
- `infinigen/core/nodes/compatibility.py`
- `infinigen/core/nodes/utils.py`
- `infinigen/core/placement/camera.py`
- `infinigen/assets/materials/plant/bark_random.py`
- `infinigen/assets/objects/tableware/pan.py`
- `infinigen/assets/objects/tableware/plant_container.py`
- `infinigen/assets/objects/bathroom/bathroom_sink.py`
- `infinigen/assets/objects/bathroom/toilet.py`
- `infinigen/assets/objects/leaves/leaf_ginko.py`
- `infinigen/assets/objects/trees/utils/materials.py`
- `infinigen/assets/objects/elements/nature_shelf_trinkets/generate.py`

There were also several small Blender RNA boolean compatibility edits in object / utility modules touched during indoors validation.

## Output Cleanup

On April 20, 2026, old exploratory outputs under:

- `outputs/system_smoke/indoors`
- `outputs/system_smoke/nature`

were pruned to keep only the current reference results:

- `outputs/system_smoke/indoors/coarse_live11`
- `outputs/system_smoke/nature/coarse_no_terrain4`
- `outputs/system_smoke/nature/populate_no_terrain3`
- `outputs/system_smoke/nature/fine_terrain_no_terrain1`

## Recommended Next Steps

### For Indoors

- Use `outputs/system_smoke/indoors/coarse_live11` as the current known-good coarse reference on this machine.
- The current requested stopping point is the final `scene.blend`, so no further `render`, `mesh_save`, or export tasks are required for the indoor line unless explicitly requested.

### For Nature

Three practical paths are available:

1. Continue local Blender 5 compatibility work using the no-terrain smoke chain that is now known to work:

```bash
python -m infinigen_examples.generate_nature --seed 0 --task coarse -g desert.gin simple.gin --output_folder outputs/system_smoke/nature/coarse_no_terrain_next -p compose_nature.terrain_enabled=False
```

Then optionally follow with:

```bash
python -m infinigen_examples.generate_nature --seed 0 --task populate --input_folder outputs/system_smoke/nature/coarse_no_terrain_next --output_folder outputs/system_smoke/nature/populate_no_terrain_next -g desert.gin simple.gin -p compose_nature.terrain_enabled=False populate_scene.populate_bushes_enabled=False
```

2. For render validation on this machine, reduce scene complexity before rendering.

- Current populated no-terrain scene is too large for both OPTIX and CPU smoke renders in the present environment.
- The first candidate for further reduction is bush population, which is already the dominant populate-memory hotspot.

3. To validate the full terrain path, move the run to an environment that supports terrain compilation and loading:

- Linux
- macOS
- possibly WSL2, which the docs label as experimental

For native Windows x86_64, the current repo documentation does not describe a supported terrain CPU build path.

## Quick Sanity Checks

Verify the local Python / Blender environment:

```bash
python -c "import bpy, numpy; print(bpy.app.version_string); print(numpy.__version__)"
```

Verify that native `cv2` is active:

```powershell
python -c "import cv2; print(cv2.__version__); print(cv2.__file__)"
```

Expected behavior in this environment:

- `bpy.app.version_string` reports `5.1.1`
- `numpy.__version__` reports `2.4.4`
- `cv2.__version__` reports `4.13.0`
- `cv2.__file__` points to `D:\Python313\Lib\site-packages\cv2\__init__.py`
