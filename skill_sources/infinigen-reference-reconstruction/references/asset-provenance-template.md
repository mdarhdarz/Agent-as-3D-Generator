# Asset Provenance Template

Use this reference when a reconstruction scene mixes native Infinigen assets, modified presets, direct Blender modeling, and archived blockouts.

## Purpose

Keep provenance notes close to the artifact they describe so future sessions know which assets are reusable source code, which are scene-specific, and which are temporary or superseded.

Recommended locations:

```text
<scene-or-project-folder>/ASSET_PROVENANCE.md
infinigen/docs/<asset-catalog>.md
```

Use a scene/project provenance note for object placement, screenshots, reference images, and current `.blend` status. Use an Infinigen repo doc for code-level asset catalogs such as native factories, locally added `style_preset` values, and reusable factory entry points.

## Template

```markdown
# Asset Provenance

Scene file: `<blend filename>`
Reference image(s): `<input image names>`
Last reviewed: `<date or session note>`

## Native Infinigen Assets

| Scene object or subsystem | Source factory | Status | Notes |
| --- | --- | --- | --- |
| `<object prefix>` | `<module.Factory>` | `native` | `<parameter notes>` |

## Modified Native Presets

| Scene object or subsystem | Source factory/preset | Status | Notes |
| --- | --- | --- | --- |
| `<object prefix>` | `<module.Factory(style_preset="...")>` | `modified preset` | `<what changed and validation state>` |

## Scene-Specific Procedural Assets

| Scene object or subsystem | Authoring path | Status | Notes |
| --- | --- | --- | --- |
| `<object prefix>` | `Blender MCP / direct mesh script` | `scene-specific` | `<why native asset was not used>` |

## Archived Or Superseded Objects

| Object prefix | Location | Reason |
| --- | --- | --- |
| `<old prefix>` | `<collection>` | `<why hidden or archived>` |

## Pending Provenance Questions

- `<asset or subsystem needing validation>`
```

## Maintenance Rules

- Update the note when replacing a subsystem or changing the factory source.
- Mark unvalidated generated assets as pending instead of presenting them as accepted.
- Keep exact object names or prefixes, not vague labels like "the good chair".
- Do not duplicate the full modeling log; record source, status, and the reason future sessions should care.
- Do not store scene-specific object state in a generic skill reference. Keep it in the local project note or the relevant repository doc.
