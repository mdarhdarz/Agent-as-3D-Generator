# Reference Reconstruction Assets

This is the repo-level catalog for reusable Infinigen assets, presets, and wrappers that were added or modified during reference-image reconstruction work.

This file only lists changed local entries. It intentionally omits placement notes, screenshots, and `.blend` progress.

## Status Labels

| Status | Meaning |
| --- | --- |
| `added factory` | New reusable factory/source entry added locally. |
| `added wrapper` | New convenience factory class that exposes a local preset or route. |
| `modified preset` | Existing factory gained a local `style_preset` or constrained reconstruction branch. |

## Changed Assets And Presets

| Entry Point | Status | Source | Registration | Validation | Notes |
| --- | --- | --- | --- | --- | --- |
| `infinigen.assets.objects.seating.chairs.DiningSlatChairFactory` | `added wrapper` for `modified preset` | `infinigen/assets/objects/seating/chairs/chair.py`; `infinigen/assets/objects/seating/chairs/dining_slat_sdf.py` | exported from `infinigen/assets/objects/seating/chairs/__init__.py`; listed in `tests/assets/list_indoor_meshes.txt` | May 1 all-asset smoke: pass; about 1.72 MB, 84,252 tris | New curated-list entry. Wraps `ChairFactory(style_preset="dining_slat")`; uses a control-tube `MeshToSDFGrid -> SDFGridMean -> GridToMesh` frame workflow plus tuned red painted wood material. |
| `ChairFactory(style_preset="dining_slat")` | `modified preset` | `infinigen/assets/objects/seating/chairs/chair.py`; `infinigen/assets/objects/seating/chairs/dining_slat_sdf.py` | exposed through `DiningSlatChairFactory` | May 1 smoke through wrapper: pass | Backing preset for the dining slat chair wrapper. |
| `infinigen.assets.objects.organizer.napkin_holder.NapkinHolderFactory` | `added factory` | `infinigen/assets/objects/organizer/napkin_holder.py` | exported from `infinigen/assets/objects/organizer/__init__.py`; listed in `tests/assets/list_indoor_meshes.txt` | May 1 all-asset smoke: pass; about 0.17 MB, 3,604 tris | New reusable tabletop napkin holder with base, side panels, optional press bar, and individual napkin sheets. |
| `TableDiningFactory(style_preset="simple_dining")` | `modified preset` | `infinigen/assets/objects/tables/dining_table.py` | not a standalone curated-list entry | pending current full-list validation | Plain four-leg dining table route with explicit preset parameters. |
| `SingleCabinetFactory(style_preset="wardrobe_flat")` | `modified preset` | `infinigen/assets/objects/shelves/single_cabinet.py` | not a standalone curated-list entry | pending current full-list validation | Flat wardrobe/cabinet route with dedicated placeholder and asset creation path. |
| `WardrobeFlatCabinetFactory(...)` | `added wrapper` for `modified preset` | `infinigen/assets/objects/shelves/single_cabinet.py` | not a standalone curated-list entry | pending current full-list validation | Convenience wrapper around `SingleCabinetFactory(style_preset="wardrobe_flat")`. |
| `CeilingClassicLampFactory(style_preset="dining_cluster")` | `modified preset` | `infinigen/assets/objects/lamp/ceiling_classic_lamp.py` | uses existing `CeilingClassicLampFactory` curated-list entry | May 1 all-asset smoke for factory entry: pass | Compact clustered pendant route. Verify scale, cable length, and shade count per scene. |

## Maintenance Rules

- Add a row when a reusable reconstruction asset, preset, or wrapper is added or renamed.
- Use `added factory` for genuinely new reusable factories.
- Use `added wrapper` for new convenience classes that expose local presets.
- Use `modified preset` for local branches inside existing factories.
- Keep validation short and concrete: date, smoke family, pass/fail, output name if useful.
- Keep compatibility-only bug fixes in `docs/WindowsBpy5CompatibilityStatus.md`, not in this catalog.
- Keep scene transforms, object visibility, archived blockout names, screenshots, and `.blend` state out of this repo-level catalog.
