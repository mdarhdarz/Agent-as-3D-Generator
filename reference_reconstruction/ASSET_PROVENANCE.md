# Asset Provenance

Scene file: `indoor_final.blend`
Reference image(s): `rgb1.png`
Last reviewed: `2026-04-27`

## Modified Native Presets

| Scene object or subsystem | Source factory / preset | Status | Notes |
| --- | --- | --- | --- |
| `InfinigenDiningSlatChair_*_SDFGeometryNodesFactory` | `infinigen.assets.objects.seating.chairs.DiningSlatChairFactory` / `ChairFactory(style_preset="dining_slat")` | modified native preset / local reconstruction asset | Replaces the hand-authored topology/SDF blockout chairs. The rewritten factory stores the successful control-tube `MeshToSDFGrid -> SDFGridMean -> GridToMesh` frame workflow in source code and bakes a high-resolution bullnose seat into the generated object. Current placement uses the archived topology/SDF chair groups for bbox and points each chair back away from the table center. Chair material is a reference-tuned aged deep red-brown painted wood shader with subtle multiplied grain, restrained bump, and reduced plastic clearcoat, not a default native Infinigen material. |

## Archived Or Superseded Objects

| Object prefix | Location | Reason |
| --- | --- | --- |
| `ProcDiningChair_TopologyInst_*` | `ARCHIVE_PreInfinigenAssetChairReplacement` | Superseded by registered Infinigen factory assets. |
| `ARCHIVE_LegacyWrapper_InfinigenDiningSlatChair_*` | `ARCHIVE_PreSDFChairFactoryRewrite` | Superseded because it used the previous direct `ChairFactory` dining-slat wrapper rather than the SDF/GN rewrite. |
| `ARCHIVE_WrongDirectionSeat_InfinigenDiningSlatChair_*` | `ARCHIVE_PreChairDirectionSeatFix` | Superseded because chair orientation and seat quality were corrected after the first SDF/GN rewrite insertion. |

## Code-Level Catalog

Reusable local asset status is tracked in `infinigen/docs/ReferenceReconstructionAssets.md`.

## Current Blend Collection Layout

- Current visible reconstruction modules live under `REFERENCE_RECONSTRUCTION_CURRENT`.
- Chair development history is grouped under `ARCHIVE_ChairDevelopment`.
- Chair study/control objects are grouped under `STUDY_ChairDevelopment`.
- The rejected bow-back / curved-spindle chair pass was removed from the blend; the visible chairs are restored to the SDF/GN high-resolution bullnose-seat version.
