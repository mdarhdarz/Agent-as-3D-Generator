---
name: infinigen-reference-reconstruction
description: Reference-image-driven 3D scene reconstruction in Blender using Blender MCP plus Infinigen asset authoring. Use when Codex needs to rebuild a room or small scene from one or more images, judge whether native Infinigen assets can be steered by parameters, patch existing asset factories with new style presets, add multi-view review cameras, or solve object placement from relative spatial relationships such as chairs around a table, lights above a table, or cabinets against a wall.
---

# Infinigen Reference Reconstruction

## Overview

Rebuild a reference-image scene by combining fast Blender MCP iteration with targeted Infinigen asset study. Prefer steering or patching native assets before creating brand-new assets.

Keep this skill generic. Do not store project-specific dates, file paths, progress logs, or one-off scene status here.

## References

- For screenshot and render-preview hygiene, read `references/review-artifact-policy.md`.
- For material and surface realism checks, read `references/lookdev-authenticity-checklist.md`.
- For deciding whether to rewrite an Infinigen preset, read `references/native-asset-rewrite-guidelines.md`.
- For live Blender MCP factory import cleanup, read `references/blender-mcp-infinigen-runtime-reset.md`.
- For project-local source tracking, read `references/asset-provenance-template.md`.
- For unfamiliar object construction, professional modeling technique, or version-sensitive Blender/Geometry Nodes/SDF/Infinigen behavior, search or open current technical references before committing to an implementation route.

## Workflow

1. Capture the reference constraints.

- Identify camera feel, room shell, dominant objects, critical proportions, and which objects are generic versus hero assets.
- If only one view exists, treat hidden regions as plausible reconstruction rather than exact ground truth.

2. Inspect the current Blender scene before editing.

- Use Blender MCP to read scene state, collection structure, object transforms, materials, cameras, and viewport screenshots.
- Preserve or add a photo-match camera plus review cameras for side and top checks.

3. Build an anchor hierarchy before changing placement.

- Identify what each object is positioned relative to: wall, floor, table, cabinet, window, or another prop.
- Prefer local relationships over world coordinates. Example: a dining chair is usually solved relative to one edge of the table, not by freehand XYZ.
- For furniture groups, define the main support object first. Example: for a dining setup, use the table as the anchor and express chairs, pendant, and centerpiece relative to the table frame.
- For room-shell edits, define the subsystem first: wall plane, opening, trim, ceiling/floor contact, and adjacent decorative bands. Do not tune one object such as a door or window without checking the shell pieces it touches.

4. Decide the asset route object by object.

- Follow `Infinigen Asset Route Protocol` before hand-modeling a hero object.
- Try parameter-only study on native Infinigen factories first, then patch a nearby factory with a constrained `style_preset`, then create a brand-new parameterized asset only after native families clearly fail.
- If the object type, construction method, or professional modeling route is uncertain, research examples, technique notes, and current docs before coding. Do this for modeling strategy as well as API details.
- If the intended route depends on specialized or recently changed APIs, such as Geometry Nodes SDF/volume nodes, node socket names, Blender Python node types, exporters, or Infinigen factory hooks, search or inspect current technical documentation before coding.

5. Solve placement relationally.

- For rectangular tables, classify chairs by table side first: `left`, `right`, `near`, `far`.
- After side classification, solve:
  - along-edge offset
  - setback distance from the edge
  - yaw relative to the table center
  - crop and occlusion in the camera view
- For wall-mounted or wall-adjacent objects, solve against the wall plane first, then refine width/height offsets.
- For hanging objects such as pendants, solve against the anchor object below them. Example: pendant centered or intentionally biased over the table, then refine cable length and cluster rotation.

6. Run the validation gate after every replacement.

- Replace scene objects incrementally, then apply the checks in `Validation Gate` before moving to another subsystem.
- Validate relationships, not only absolute transforms. Example: verify that a chair still belongs to the intended table side after every move.
- After a replacement or rejected iteration, run the `Scene Organization And Cleanup Pattern` before saving. A visually correct scene with mixed collections, duplicate live objects, or stale review variants is not finished.

7. Save the scene and summarize only reusable findings.

- Save the working `.blend` after any milestone that materially changes proportions or replaces assets.
- Promote reusable methods into this `SKILL.md` only when they generalize across scenes.
- Keep project-specific state outside the skill unless the user explicitly asks for a separate project note.
- If the scene mixes native assets, modified presets, and hand-authored pieces, maintain a project-local provenance note using `references/asset-provenance-template.md`.

## Infinigen Asset Route Protocol

- Treat each hero object as an asset-routing decision before hand-modeling it in Blender.
- Survey native Infinigen assets first: inspect `tests/assets/*.txt`, the relevant asset-family `__init__.py`, and one or two nearby factory modules. Prefer exact import paths when aliases or exports are unclear.
- Compare candidate families in a study area: default output, seeded variants, and explicit parameter sweeps against the reference silhouette, dimensions, construction logic, material hooks, support surfaces, and tags.
- Prefer parameter steering when the candidate topology already matches the reference. Keep useful parameter names and ranges explicit so the result can be reused.
- If the family is close but needs a reference-specific variant, patch the native factory with a constrained `style_preset`. Preserve default behavior, existing materials, tagging, support surfaces, and downstream placement hooks.
- If the visual problem is bad construction logic rather than low resolution, follow `references/native-asset-rewrite-guidelines.md`; do not treat higher segment counts as a quality fix.
- Use the `infinigen-asset-authoring` skill for code-level factory work: patching an existing factory, adding a `style_preset`, creating a new `AssetFactory`, choosing pure Python geometry versus Geometry Nodes versus hybrid modeling, or validating through repo-native individual-asset entry points.
- Create a brand-new parameterized asset only after the native survey, parameter sweep, and preset-patching routes fail to match the reference.
- Insert approved assets into the active reconstruction `.blend` through `Current-Blend Factory Invocation Pattern`; treat manual Blender geometry as blockout or last-resort reconstruction, not the default for hero assets.

## Native Asset Study Pattern

- Create a dedicated study area such as `ASSET_STUDY` plus a `StudyCam`.
- Compare default and reference-tuned candidates before editing code.
- Prefer adding `style_preset` branches over rewriting default behavior.
- If generated geometry drifts from intended size, normalize against the placeholder bbox instead of silently scaling scene instances by hand.
- Preserve materials, tagging, and support-surface hooks so downstream systems still behave correctly.
- Use single-asset generation for isolated validation, not as the default insertion path for an already-open reconstruction scene.
- For normal Blender scene review, prefer asset output that preserves live modifiers or instances when the evaluated result remains usable. Use isolated saved `.blend` outputs for batch smoke tests, regression handoff, or cases where the active Blender process cannot import the factory cleanly.

## Object Quality Standards

- Prioritize silhouette and construction logic before small decoration. A refined object should first read correctly in the reference camera: main proportions, support points, connection logic, and orientation.
- Model the object's physical construction, not a pile of visible parts. If two pieces are meant to be one continuous casting, bent frame, molded shell, welded tube, carved support, or laminated body, solve continuity in the geometry instead of hiding intersections with decorative caps or spheres.
- Build details in levels:
  - primary details define the object's visible silhouette and structure, such as chair back curves, seat thickness, table legs, window apertures, cabinet door rhythm, and door frames.
  - secondary details add believable construction without changing the silhouette, such as bevels, rails, panels, aprons, mullions, casing, thresholds, support braces, and inset grooves.
  - tertiary details are near-view only, such as screw heads, dowels, plugs, wear marks, thin grain lines, and tiny decorative caps.
- Do not add tertiary details until primary and secondary details are accepted in the reference camera and a close review camera.
- Control visual weight. Tiny details should add depth when close up, but should not become dark dots, oversized bumps, graphic stripes, or noisy clutter in the reference camera.
- Size details against their parent part, not by eye alone. For example, a foot pad, peg, screw head, or decorative collar should stay small relative to the leg, post, rail, or panel it belongs to.
- Derive detail placement from the object's bbox, local axes, support plane, and parent parts. Avoid hardcoded world coordinates except for scene-level anchors.
- Accept detail changes only after they pass the reference view and a close construction review in `Validation Gate`.
- If a color region reads like a pasted panel or sticker, fix the construction first. Rebuild it as an attached functional part such as a lid, rim, inset panel, hinge, handle, trim piece, or reveal before tuning its material.
- For material realism repairs, apply `references/lookdev-authenticity-checklist.md` before accepting the result.
- For uncertain refinements, create a removable detail layer using a clear prefix such as `ProcObjectDetailHD_*`. Preserve the base object until the detail direction is approved.
- Before propagating rich details across a repeated set, test on one representative object, inspect close-up and through `PhotoMatchCamera`, then copy the pattern to the group.
- A high object count is not a quality signal. Prefer fewer details with correct scale and construction purpose over many small objects that do not improve the reference match.

## Continuous Construction Pattern

- Before rebuilding a hero object, classify which regions are continuous bodies and which are separate attached parts. Examples generalize beyond chairs: tubular frames, handles, rails, faucet arms, lamp stems, cabinet pulls, appliance shells, molded brackets, and carved legs may need seamless continuity; panels, cushions, glass, doors, lids, and tabletop slabs often need dedicated topology.
- For continuous tube/frame/shell systems, start from a clean control skeleton or guide surface. Use Blender's native Geometry Nodes SDF/volume grid workflow when field fusion is the chosen route; use bevelled curves, booleans, subdivision, or controlled retopology when those better match the shape. Do not rely on intersecting cylinders, stacked primitives, or add-on balls at joints as final construction.
- Prefer the native Blender Geometry Nodes SDF chain over hand-written SDF or custom remeshing approximations when it is available in the active Blender version. A typical route is clean control mesh or points -> `Mesh to SDF Grid` or `Points to SDF Grid` -> optional `SDF Grid Boolean` / `SDF Grid Mean` / `SDF Grid Median` / `SDF Grid Fillet` / `SDF Grid Offset` -> `Grid to Mesh` -> normals/cleanup. Bake the evaluated result only after the node output has passed close visual inspection.
- Treat SDF and voxel fusion as a construction tool, not an automatic quality switch. Tune voxel size, active band width, threshold, adaptivity, filtering width/iterations, and field offsets deliberately. Keep inputs simple, radii consistent, sampling dense enough for the target scale, and smoothing restrained. Inspect for blobby corners, dents, pits, over-rounded joints, triangulation artifacts, and loss of design intent.
- Build non-tubular key surfaces with their own geometry. Thin boards, panels, shelves, cushions, lids, and molded seats often need controlled bevels, inset/support edges, thickness variation, or subdivided surfaces rather than being absorbed into the fused field.
- Validate the result at three levels: the reference camera for silhouette, a close construction view for joints and surface quality, and a numeric audit for bbox, orientation, polycount, contact, and intended continuity.

## Technical And Modeling Research Checkpoints

- Research is appropriate for modeling judgment, not only API uncertainty. Before improvising a hero asset or unfamiliar object category, look up professional construction references, modeling breakdowns, topology/SDF/subdivision techniques, and real-world object structure so the first implementation is not just personal guesswork.
- Search or open current official docs when using APIs whose node names, socket order, availability, or behavior may depend on Blender/Infinigen versions. This includes Geometry Nodes SDF/volume grids, node RNA types, exporter settings, simulation hooks, and generated node wrappers.
- For Blender SDF/volume workflows, verify the active version supports the intended native nodes and settings before falling back to custom code. Prioritize the built-in nodes because they usually produce cleaner surfaces than ad hoc Python SDF conversion.
- Prefer primary sources for version-sensitive details: Blender Manual/API/release notes for Blender nodes and Python types, Infinigen source/docs for factory hooks, and live Blender introspection for the active session's actual node sockets. For modeling strategy, combine current docs with high-quality professional references and inspect the real object category before finalizing the route.
- Use research to answer concrete implementation questions before coding, such as "how is this object manufactured?", "which parts should be continuous?", "what topology or SDF workflow fits this form?", "does this node exist in this Blender version?", or "which repo entry point is canonical?". Do not brute-force a fragile model alone when the technique is discoverable.

## Geometry And Normal Hygiene

- After creating, replacing, or procedurally generating mesh objects, apply the scene's normal policy before visual approval: set mesh polygons smooth, add or update `Weighted Normal` with sharp edges preserved, and use Blender's `Smooth by Angle` / auto-smooth path when available.
- In Blender 4/5, `bpy.ops.object.shade_auto_smooth` only works on selectable objects in the active ViewLayer. If it fails because archived or hidden objects are not selectable, retry on visible ViewLayer meshes, then still apply polygon smoothing and `Weighted Normal` to all mesh datablocks.
- Re-run the normal policy on newly added objects even if a global smoothing pass already happened earlier in the session.
- Validate smoothing in both the reference camera and a close camera. Look for rounded cuboid corners becoming blobby, hard construction edges disappearing, or new meshes looking faceted compared with existing assets.

## Validation Gate

- Check ground contact, support surfaces, bbox dimensions, orientation, scale, polycount, collection membership, and support-surface or tagging behavior when relevant.
- Review each local repair at two distances: `PhotoMatchCamera` for composition and a close subsystem camera for construction seams, bevels, support/contact, material transitions, and whether a color region reads as part of the object.
- Check adjacent systems after every local fix. Example: after grounding a door, inspect frame-to-wall, frame-to-ceiling, threshold-to-floor, visible side gaps, and upper gaps around the whole doorway.
- Use numeric audits when visual inspection is ambiguous: bbox min/max, intended small overlaps, exact gaps, and support-plane contact.
- Restore temporary visibility, selection, active camera, render flags, and collection memberships before saving. Treat hidden ceilings, selected debug objects, mixed archive/live collections, and active inspection cameras as unfinished state.

## Current-Blend Factory Invocation Pattern

- Prefer direct Blender MCP factory calls when replacing assets in the active `.blend`: configure the Blender process import path, reload the target factory module, create the asset in-place, move it into the target collection, then archive the old blockout.
- Remember that the active Blender process may use a different Python executable than the repo's system-level validation command. Before importing Infinigen inside MCP, put the repo root before the validated third-party `site-packages` path.
- Do not paper over missing dependencies by injecting no-op modules such as fake `gin` or `tqdm`. If that happened during debugging, remove those modules from `sys.modules`; if Infinigen was imported while they were present, also purge `infinigen` and `infinigen.*` before a clean import.
- When the live Blender import state is suspect, use `references/blender-mcp-infinigen-runtime-reset.md` before retrying factory creation.
- When the object is staying in the active Blender `.blend`, keep live modifier stacks and Geometry Nodes instances where safe instead of realizing everything into mesh data. Bake only when the reconstruction workflow needs mesh editing, export, simulation, stable-pose analysis, or joined geometry.
- If retained Geometry Nodes instances depend on hidden source collections or prototype objects, keep those dependencies hidden and non-rendering but present. Do not delete source collections that a live modifier still references.
- After direct factory creation, validate the generated object just like an appended asset: bbox, polycount, ground/support contact, collection membership, old-object archive state, neighboring subsystem gaps, active camera, and viewport screenshot.

## Environment Compatibility Pattern

- If the project has a compatibility handoff such as `infinigen/docs/WindowsBpy5CompatibilityStatus.md`, read it before running or debugging Infinigen system pipelines, direct Blender MCP factory imports, or Blender/Python dependency work.
- Treat that document as the project-local reference for exact commands, runtime versions, known-good smoke outputs, and current blockers. Do not duplicate those details inside this skill.
- Treat system-level Infinigen commands, Blender MCP execution, and standalone Python probes as separate runtimes until verified. Record which Python executable, `bpy` version, NumPy version, and dependency paths each one is using.
- Put the Infinigen repo root before the validated third-party `site-packages` in the active process import path.
- Prefer real installed dependencies such as `gin`, `tqdm`, and `trimesh`. Temporary fake modules can make imports appear successful while corrupting later factory behavior.
- If an import path was wrong, clean the live process before retrying: remove the affected dependency modules from `sys.modules`; if Infinigen was already imported, also remove `infinigen` and `infinigen.*`.
- Use this skill for reusable workflow and the compatibility handoff for exact local commands and environment status.

## Blender MCP Review Pattern

- Use `get_scene_info`, `get_object_info`, `get_viewport_screenshot`, and `execute_blender_code` to inspect and iterate.
- Prefer session-only viewport screenshots for routine iteration. Save PNG review artifacts only when they have lasting comparison or handoff value; see `references/review-artifact-policy.md`.
- Keep `PhotoMatchCamera` for the reference view and maintain side/top review cameras such as `ReviewCamFront`, `ReviewCamRight`, `ReviewCamTop`, and `ReviewTarget`.
- For every local asset or material repair, create or reuse a close review camera named for the subsystem, such as `ReviewCamLeftBin_Close` or `ReviewCamDiningLookdev_Close`.
- Temporarily hide blocking shell pieces like the ceiling or side wall for side and top checks instead of moving the review logic.
- When no environment texture is set, use Blender's built-in world for viewport preview so material-preview checks stay readable.

## Subsystem Replacement Pattern

- Archive old blockout objects in a clearly named collection and hide them before replacing a region. Prefer this over deleting when the model is still exploratory.
- Rebuild coherent modules rather than isolated meshes. Examples: a window module includes wall returns, glass plane, frame rails, sill, baseboard, lighting cue, and nearby small props; a doorway module includes wall opening, jambs, header, threshold, door leaf, reveal, and casing.
- Name new objects by subsystem so later audits can select and inspect the whole group.
- Avoid duplicate overlapping geometry after iterative fixes. If a temporary infill becomes redundant because a structural piece was extended, remove the duplicate before saving.
- Prefer slight, intentional overlaps at closed construction seams over exact coplanar contact when avoiding visible cracks. Keep overlaps small and audit that they do not protrude through adjacent shell pieces.

## Scene Organization And Cleanup Pattern

- Keep live scene modules, archives, and study work in separate collection families. A practical layout is `REFERENCE_RECONSTRUCTION_CURRENT` for visible scene modules, `ARCHIVE_<Subsystem>Development` for hidden history, and `STUDY_<Subsystem>Development` for experiments, control meshes, and Blender construction checks.
- Every visible production object should belong to the intended subsystem collection only, unless the scene has a deliberate cross-cutting collection. Do not leave current objects in archive/study collections, and do not leave archived objects in live subsystem collections.
- When an iteration is rejected, delete or archive that pass immediately. Remove rejected visible objects, temporary review objects, unused helper carriers, empty scratch collections, and intermediate versions that are not useful provenance.
- If an old version is worth keeping, hide it, disable render, move it under a clearly named archive collection, and record the reason in scene provenance. If it is just a failed transient attempt, remove it and purge unused data-blocks when safe.
- After moving collections, audit parentage so scene modules are not linked at multiple hierarchy levels. Avoid mixed collections that contain live objects, archived blockouts, study controls, and review cameras at the same time.
- Before saving, run a small scene hygiene audit: visible target objects, rejected-object name patterns, collection parent map, empty collections, duplicate memberships, object count, and whether the provenance note explains any remaining archive/study collections.

## Relative Placement Heuristics

- Analyze scene composition in object groups, not isolated meshes.
- For each group, identify:
  - anchor object
  - support plane
  - local forward direction
  - symmetry or asymmetry visible in camera
- For dining scenes:
  - table is the anchor
  - chairs belong to the four table edges
  - centerpiece belongs near the table center with small camera-aware bias
  - pendant belongs above the table, then shifts slightly for camera composition only if the reference requires it
- For storage walls:
  - cabinet blocks align to the wall plane first
  - door rhythm, panel width, and handle spacing should be solved as a repeated system rather than one door at a time
- For doors and openings:
  - solve the wall/opening plane first
  - seat the threshold on the floor
  - keep jambs, header, casing, reveal, and leaf as one module
  - check side gaps and upper gaps separately; a fix for one can expose the other
- For windows:
  - solve the wall plane and window aperture first
  - make the glass/frame relationship explicit
  - keep sills low and grounded unless the reference shows cabinet-like mass
  - verify nearby props sit on floor or sill rather than being visually plausible but unsupported
- Use camera framing only after the relative layout is coherent in plan view and side view.

## Asset Catalogs And Provenance

- Do not keep checkout-specific preset lists or scene progress notes in this skill.
- Use `infinigen/docs/ReferenceReconstructionAssets.md` as the canonical repo-level catalog for reference-driven or locally modified Infinigen assets when that file exists. Do not create parallel repo-level catalogs such as `LocalReconstructionAssets.md` unless the user explicitly asks for a new taxonomy.
- Keep scene-specific provenance near the `.blend` or project folder, conventionally as `ASSET_PROVENANCE.md`. Use it for object prefixes, replacement reasons, archive collection names, and current collection layout. Keep code-level provenance with the Infinigen repo in the canonical catalog above.
- Direct Blender factory creation via MCP in the active blend is the preferred reconstruction insertion path once the Blender process import environment is clean; standalone asset `.blend` output remains useful for smoke tests, isolated validation, and durable artifacts.

## Skill Maintenance

- Update this skill only when a method, heuristic, or asset pattern becomes reusable across multiple scenes.
- Do not update the skill for every scene milestone.
- Do not keep one-off project logs inside the skill.
- For local editable skill sources, remember that Codex normally reads installed skills from `CODEX_HOME/skills`. After updating a project-local `skill_sources` copy, sync it to the installed skill directory and validate that the installed copy matches.
