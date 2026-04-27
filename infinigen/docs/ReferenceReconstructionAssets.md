# Reference Reconstruction Assets

This document tracks Infinigen repo-level assets and locally added presets used for reference-image reconstruction work. It should not record per-scene placement, camera status, screenshot paths, or `.blend` progress; keep those in the scene/project provenance note.

## Native Families Used For Reconstruction

| Factory | Module | Native role | Local reconstruction use |
| --- | --- | --- | --- |
| `ChairFactory` | `infinigen.assets.objects.seating.chairs.chair` | Generic procedural chair family with seat, leg, back, decor, material, and bbox-normalization hooks. | Base family for the slatted dining chair preset. |
| `TableDiningFactory` | `infinigen.assets.objects.tables.dining_table` | Procedural dining/side/coffee table family. | Base family for plain dining table experiments and reconstruction table studies. |
| `SingleCabinetFactory` | `infinigen.assets.objects.shelves.single_cabinet` | Cabinet and wardrobe-style storage asset family. | Base family for flat wardrobe/cabinet reconstruction. |
| `CeilingClassicLampFactory` | `infinigen.assets.objects.lamp.ceiling_classic_lamp` | Procedural hanging ceiling lamp family. | Base family for compact dining pendant reconstruction. |

## Local Added Or Modified Presets

| Factory entry point | Source file | Status | Notes |
| --- | --- | --- | --- |
| `ChairFactory(style_preset="dining_slat")` / `DiningSlatChairFactory` | `infinigen/assets/objects/seating/chairs/chair.py`, `infinigen/assets/objects/seating/chairs/dining_slat_sdf.py` | modified native preset / local reconstruction asset | Painted slat-back dining chair route created for the dining reference reconstruction. The current version stores the successful control-tube `MeshToSDFGrid -> SDFGridMean -> GridToMesh` frame workflow in source code, then combines it with a high-resolution bullnose seat and a reference-tuned aged deep red-brown painted wood material. `DiningSlatChairFactory` is exported and listed in `tests/assets/list_indoor_meshes.txt`, but should remain marked as local reconstruction work until reviewed for upstream-native generality. |
| `TableDiningFactory(style_preset="simple_dining")` | `infinigen/assets/objects/tables/dining_table.py` | available local preset | Plain four-leg dining table route with explicit preset parameters and a dedicated creation path. Verify in the current checkout before reuse. |
| `SingleCabinetFactory(style_preset="wardrobe_flat")` | `infinigen/assets/objects/shelves/single_cabinet.py` | available local preset | Flat wardrobe/cabinet route with dedicated placeholder and asset creation path. Verify dimensions and door rhythm against the target reference before reuse. |
| `WardrobeFlatCabinetFactory(...)` | `infinigen/assets/objects/shelves/single_cabinet.py` | available local wrapper | Convenience wrapper that defaults to `style_preset="wardrobe_flat"`. |
| `CeilingClassicLampFactory(style_preset="dining_cluster")` | `infinigen/assets/objects/lamp/ceiling_classic_lamp.py` | available local preset | Compact clustered pendant route with dedicated placeholder and asset creation path. Verify scale, cable length, and shade count for each scene. |

## Scene-Only Assets Not Yet In Infinigen

These object groups may exist in reconstruction `.blend` files, but they are not reusable Infinigen factories unless promoted later:

| Scene object prefix | Current source | Notes |
| --- | --- | --- |
| `ProcDiningTable_InfinigenRefined_*` | Blender MCP direct procedural mesh | Informed by Infinigen table construction patterns, but not registered as a reusable factory. |
| `ProcDiningTable_InfinigenRefined_Placemat*` | Blender MCP direct procedural mesh and packed material | Scene-specific cloth placemat; not an Infinigen asset. |
| `ProcCenterpieceHD_*`, `ProcPendantHD_*`, `ProcLeftWindowHD_*`, `ProcRightRecessHD_*`, `ProcWallpaperBandVine*` | Blender MCP direct scene reconstruction | Reference-specific reconstruction objects; promote only after a real reusable factory design exists. |

## Maintenance Rules

- Update this document when adding, renaming, or validating a local `style_preset` or wrapper factory.
- Mark unvalidated presets as `in progress` or `pending`; do not present them as stable just because they instantiate.
- Keep exact module paths and factory signatures here.
- Keep per-scene transforms, object visibility, archived blockout names, and screenshot organization in the scene/project provenance note.
