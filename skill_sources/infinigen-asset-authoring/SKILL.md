---
name: infinigen-asset-authoring
description: Use when working in Infinigen or a similar procedural Blender repository and the task is to create, port, refactor, debug, or invoke a procedural asset, material, scatter, or sim-ready object implemented with Python, bpy, Geometry Nodes, AssetFactory, NodeWrangler, or the node transpiler.
---

# Infinigen Asset Authoring

## Use When

- The user wants a new procedural asset in the style of Infinigen.
- The task involves `AssetFactory`, `bpy`, Geometry Nodes, materials, scatters, or sim-ready articulated assets.
- The task is to call an existing asset from the CLI, Blender Python Console, or Blender MCP.
- The task starts from a Blender node graph and needs to be converted into maintainable Python.
- The task is to decide whether an asset should be pure mesh code, transpiled node code, or a hybrid.

For exact repo paths, import patterns, and validation commands, read `references/infinigen-patterns.md`.

## Core Model

- `AssetFactory` owns seeding, placeholder spawning, and final asset creation. `create_asset()` must return a `bpy.types.Object`.
- `surface.add_geomod()` is the normal bridge from Python functions to real Geometry Nodes modifiers.
- `NodeWrangler` and `node_utils.to_nodegroup()` are the standard way to express reusable node graphs in Python.
- `surface.add_material()` and named attributes are the standard way to connect geometry outputs to shaders.
- `generate_individual_assets.unified_asset_import()` can load exact full import paths directly, even before a new asset is exported from a package `__init__.py`.
- `butil.spawn_vert()` is the usual starting point for node-driven assets. Direct mesh or curve creation is appropriate when topology control matters more than node reuse.

## Workflow

1. Decide whether the task is invoking an existing asset or authoring a new one.
2. Locate the canonical asset path before coding.
   - Check `tests/assets/*.txt` curated lists first.
   - Check the family `__init__.py` next.
   - Fall back to the exact module path when the asset is new or not exported yet.
3. Read one or two nearby assets before writing code.
   - Prefer neighbors from the same family over broad repo searches.
4. Choose the modeling strategy before coding.
   - Transpiled nodes: best when the shape is easiest to build visually in Blender.
   - Pure Python geometry: best for sampled curves, array math, custom topology, or tight control of mesh layout.
   - Hybrid: best default for many indoor assets. Build subparts procedurally, then assemble them with Geometry Nodes or light `bpy` code.
   - When the asset category, modeling method, or route is unfamiliar, research professional modeling approaches and real object construction before coding.
   - When the route depends on version-sensitive Blender, Geometry Nodes, SDF/volume, exporter, or Infinigen APIs, check current technical documentation or live API introspection before coding.
5. Implement the minimum deterministic factory first.
   - Add seed-dependent parameters in `__init__()` or a `sample_params()` helper.
   - Keep `create_asset()` short and push heavy node logic into helper functions.
6. Integrate with repo entry points after the first working version exists.
   - Export from the family `__init__.py` when appropriate.
   - Add the asset to curated `tests/assets/*.txt` lists if the repo uses them.
   - For assets created from reference reconstruction work, document provenance before treating the asset as reusable.
7. Validate in the right environment.
   - Prefer repo-native Blender or `generate_individual_assets` first.
   - Use Blender MCP for scene insertion and live inspection.
   - If a plain Python interpreter lacks `bpy`, or a generic Blender session lacks Infinigen dependencies, treat that as an environment issue before changing asset code.

## Existing Asset Invocation

- For first smoke tests, prefer the exact full import path over a short alias.
- Use `generate_individual_assets` when you want a repo-native single-asset validation.
- Use Blender Python Console or Blender MCP when you want tight edit-reload-spawn loops.
- After file edits inside Blender, use `importlib.reload()` before respawning the factory.

## Strategy Guide

### Start From Blender Nodes

Use this when the asset is shape-driven and easy to iterate on visually.

- Build the geometry or shader graph in Blender.
- Run the transpiler.
- Move the generated functions into the repo.
- Clean the output before calling the task done:
  - Rename generic functions.
  - Pull repeated constants into explicit parameters.
  - Split reusable nodegroups out with `to_nodegroup()`.
  - Keep generated code behind a thin factory interface.

### Start From Pure Python Geometry

Use this when the asset is easier to describe as curves, sampled points, or mesh operations than as a node graph.

- Use NumPy or helper geometry classes for sampling.
- Create the base object with repo helpers or direct mesh creation.
- Convert to mesh only when needed.
- Add materials after the geometry is stable.

### Use A Hybrid

This is often the best default for new furniture or appliance assets.

- Build small sub-assets independently.
- Reuse existing materials and helper nodegroups.
- Assemble and place parts in a top-level geometry node function or a small amount of direct `bpy` code.

### Build Continuous Geometry

Use this when the asset should read as one manufactured body rather than separate primitives.

- Define continuous regions before coding: welded or bent frames, molded shells, carved supports, handles, rails, stems, brackets, and flowing housings should not be left as intersecting cylinders or boxes.
- Start from clean control geometry such as sampled curves, tubes, guide surfaces, or low-poly cages. Fuse or refine that control shape with the appropriate tool: native Blender Geometry Nodes SDF/volume grids, bevelled curves, booleans, subdivision with support edges, or explicit retopology.
- Prefer Blender's native Geometry Nodes SDF/volume workflow over hand-written SDF or custom remeshing when available. A maintainable factory can create control geometry, run nodes such as `Mesh to SDF Grid` or `Points to SDF Grid`, optionally process the field with `SDF Grid Boolean`, `SDF Grid Mean`, `SDF Grid Median`, `SDF Grid Fillet`, or `SDF Grid Offset`, then use `Grid to Mesh` and bake the evaluated result after validation.
- Use SDF/volume fusion for seamless joints where field blending is physically plausible. Keep radii consistent, voxel size appropriate to the smallest visible feature, band width sufficient for the intended operations, threshold normally at the SDF surface, adaptivity low when uniform surface quality matters, smoothing restrained, and inputs clean. Watch for pits, blobby intersections, lumpy silhouettes, and triangulation artifacts.
- Model precision parts separately when needed. Thin slabs, boards, panels, lids, cushions, glass, and broad support surfaces often need controlled topology, bevels, insets, or subdivision instead of being absorbed into a fused volume.
- Do not use decorative spheres, caps, collars, or overlapping parts to fake a structural connection unless the reference shows them as real hardware.

## Technical And Modeling Research Checkpoints

- For stable local repo patterns, read nearby source first. For unfamiliar object categories or modeling strategies, search professional references and real construction examples before implementation. For version-sensitive or unfamiliar APIs, consult current technical docs before implementation.
- Prefer primary sources for API behavior: Blender Manual/API/release notes for Geometry Nodes, SDF/volume grids, RNA node types, and socket behavior; Infinigen docs/source for factory hooks, registration, asset lists, and generation entry points.
- In the active Blender process, verify docs against live introspection when sockets or node availability matter. A documented node can still differ from the installed runtime.
- For Blender SDF/volume assets, make the native Geometry Nodes route the default baseline when supported by the runtime. Fall back to hand-written SDF or custom mesh conversion only when the native nodes are unavailable, cannot express the required operation, or have been tested and rejected for the specific shape.
- Use research to resolve concrete risks in modeling and implementation: how the object is built, which parts are continuous, which topology or field workflow fits the form, which node sockets exist, and how the asset should be registered. Do not brute-force a low-quality asset alone when the technique can be learned or verified.

## Default Coding Rules

- Prefer `AssetFactory` over ad hoc top-level scripts.
- Prefer `butil` and data-block APIs over raw `bpy.ops` when both are practical.
- Use `bpy.ops` only where the repo already leans on it or where Blender's data API is much clumsier.
- Keep seeding explicit with `FixedSeed` or repo hashing helpers whenever randomness affects geometry or materials.
- Prefer exposed GN inputs and named attributes over hidden magic constants.
- If transpiled code becomes very large, refactor repeated nodegroups instead of adding more generated bulk.
- When validating a brand-new asset, prove it works by exact import path before relying on convenience exports.
- Do not leave temporary carrier objects, control meshes, node groups, materials, or review helpers in the scene unless they are deliberate debug outputs. Remove unused data-blocks when safe, and give retained helpers explicit `STUDY_` or `DEBUG_` naming.

## Provenance For Local Or Reference Assets

- Distinguish upstream-native assets from local reconstruction work. Use explicit status language such as `native`, `modified native preset`, `local reconstruction asset`, or `scene-specific blockout`.
- When a reference-driven asset is exported or added to a curated asset list, add or update the canonical repo-local catalog `infinigen/docs/ReferenceReconstructionAssets.md` describing the factory path, status, modeling route, registration point, and validation state. Do not create parallel repo-level catalogs such as `LocalReconstructionAssets.md` unless the user explicitly asks for a new taxonomy.
- For active `.blend` replacements, keep scene provenance near the scene file, conventionally as `ASSET_PROVENANCE.md`. Record object prefixes, source factory or preset, archived blockouts, collection layout, and why the replacement should be trusted.
- Preserve useful custom properties on generated objects, such as `infinigen_factory`, `asset_status`, and any workflow marker that explains a nonstandard construction path.
- Do not present a locally added factory as a native Infinigen asset unless it has actually been generalized and promoted.

## Minimal Factory Skeleton

```python
import bpy
import numpy as np

from infinigen.core.placement.factory import AssetFactory
from infinigen.core import surface
from infinigen.core.util import blender as butil
from infinigen.core.util.math import FixedSeed


class MyAssetFactory(AssetFactory):
    def __init__(self, factory_seed, coarse=False):
        super().__init__(factory_seed, coarse=coarse)
        with FixedSeed(factory_seed):
            self.height = np.random.uniform(0.8, 1.2)

    def create_asset(self, i=0, **params) -> bpy.types.Object:
        obj = butil.spawn_vert()
        surface.add_geomod(
            obj,
            geometry_nodes,
            apply=False,
            attributes=[],
            input_kwargs={"Height": self.height},
        )
        return obj
```

## Validation Checklist

- Can one asset be generated with the normal individual-asset entry point?
- Does the asset return a real object and not leave stray helpers in scene data?
- Is the output deterministic for a fixed seed?
- Are modifier inputs, named attributes, and materials wired intentionally?
- Are generated objects placed in the intended collection, with temporary helpers removed or clearly isolated?
- Is polycount reasonable for the asset category?
- If the asset is local or reference-driven, is its non-native status documented in the repo and, when inserted into a scene, in scene provenance?
- If the asset is sim-ready, does export still work?
- If validation fails, is the failure actually in the asset code rather than in the Python or Blender environment?

## Response Style For This Skill

- Work like a paired procedural TD.
- Read nearby examples first, then implement the smallest coherent version.
- Prefer exact import paths for first-pass validation and mention when an alias depends on `__init__.py` exports or curated test lists.
- Prefer concrete repo paths, factory names, and validation commands in the final answer.
