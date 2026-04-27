# Review Artifact Policy

Use this reference when a reconstruction task produces viewport screenshots, render previews, or other temporary visual checks.

## Default

- Prefer session-only Blender MCP viewport screenshots for ordinary iteration.
- Do not save a PNG just to prove that an edit was inspected.
- Save the `.blend` after meaningful modeling or placement milestones, not after every screenshot.

## When to Save Images

Save review images only when they serve one of these purposes:

- before/after comparison for a user-facing milestone
- final delivery evidence for a difficult visual fix
- regression reference before replacing a complex subsystem
- documentation artifact that another session must inspect without reopening Blender

## Directory Layout

When saving screenshots, keep them out of the project root.

Recommended layout:

```text
<scene-or-project-folder>/
  review_shots/
    YYYY-MM-DD_topic/
      photomatch_main.png
      subsystem_close.png
      top_or_side_audit.png
```

Use descriptive names that encode the view and purpose. Avoid sequential scratch names such as `test1.png` or `preview_new.png`.

## Cleanup

- Move earlier loose screenshots into an appropriate `review_shots/` subfolder before final handoff.
- Keep scene/project root folders limited to core inputs, `.blend` files, and project notes.
- If a saved screenshot was only a debugging artifact and no longer informs review, archive or remove it before declaring the project tidy.
