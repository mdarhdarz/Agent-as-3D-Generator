# Native Asset Rewrite Guidelines

Use this reference when an Infinigen asset family is close to a reference object but parameter tuning or higher resolution does not solve the visual problem.

## Decision Ladder

1. Study the native factory and nearby asset families.
2. Try parameter-only steering if the construction topology already matches.
3. Add a constrained `style_preset` if the family is close but needs reference-specific defaults.
4. Rewrite the preset construction path only when the issue is structural.
5. Create a new asset family only when no native family offers the right modeling primitives, material hooks, or placement semantics.

## What Counts As Structural

A problem is structural when it comes from how the object is built, not from how many segments it has.

Examples:

- chair legs are independent cylinders instead of continuous rear posts
- back rails do not connect into the post logic
- a seat is a slab when the reference needs a shaped support surface
- material regions are separate patches instead of part of the asset's physical construction
- the asset loses tags, material hooks, support surfaces, or bbox normalization after patching

## Rewrite Principles

- Preserve default behavior for existing styles.
- Keep the new behavior behind a specific `style_preset`.
- Reuse native primitives and helpers such as factory methods, curve alignment, sweep/solidify paths, support-surface tagging, material assignment, bbox normalization, and face attributes.
- Generate coherent modules, not a pile of unrelated primitives.
- Express details from parent dimensions and local axes rather than hardcoded world coordinates.
- Keep resolution as a result of the construction method, not the core fix.

## Validation

- Run a syntax or import check outside Blender when possible.
- Smoke-test the factory in Blender or the repo-native asset pipeline.
- Inspect bbox, polycount, tags, materials, support surfaces, and normalized scale.
- Compare the generated asset at close range and through the reconstruction camera before replacing all repeated instances.

## Anti-Patterns

- Raising segment counts while keeping bad construction logic.
- Adding many small parts to hide wrong proportions.
- Replacing native hooks with scene-only manual transforms.
- Declaring a preset reusable before it has been generated cleanly in the live Blender runtime.
