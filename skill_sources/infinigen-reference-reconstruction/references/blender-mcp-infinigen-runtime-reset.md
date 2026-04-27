# Blender MCP Infinigen Runtime Reset

Use this reference when importing or reloading Infinigen factories inside an already-open Blender MCP session.

## Runtime Separation

Treat these as separate runtimes until verified:

- terminal Python used for syntax checks
- Blender's embedded Python used by MCP
- repo-level generation scripts

Record which runtime produced each result when debugging import or compatibility problems.

## Import Path Order

Before importing Infinigen inside Blender MCP, put paths in this order:

1. Infinigen repo root
2. validated third-party `site-packages`

If available, read the project compatibility handoff for exact local paths instead of reconstructing them from memory.

## Clean Reload Pattern

When a factory import or reload behaved incorrectly:

- remove temporary fake modules from `sys.modules`
- remove the target factory module and related package entries
- if Infinigen was imported under a bad environment, remove `infinigen` and all `infinigen.*` entries
- call `gin.enter_interactive_mode()` when repeated configurable registration causes conflicts
- reinsert paths in the intended order before importing again

## Do Not Fake Dependencies

Do not inject no-op replacements for dependencies such as `gin`, `tqdm`, or `trimesh`. Fake modules can let imports appear successful while corrupting asset behavior later.

## Minimal Verification

After a clean import:

- instantiate the target factory with the intended `style_preset`
- call `create_asset()` in the active Blender scene
- verify the object exists, has plausible bbox dimensions, and has nonzero mesh data
- delete or archive the test object if it was only a smoke test
