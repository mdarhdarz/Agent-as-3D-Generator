# Lookdev Authenticity Checklist

Use this reference when a scene object looks "procedural", pasted on, too clean, or physically implausible even though the geometry roughly matches the reference.

## Construction First

- Fix the object construction before tuning color.
- Do not simulate missing construction with floating planes, fake highlight strips, oversized dark grooves, or sticker-like material islands.
- If a colored region reads as pasted on, rebuild it as a real part: inset panel, cloth with thickness, trim, lip, reveal, stitched edge, handle, hinge, cap, or support frame.

## Contact And Thickness

- Check that cloth, pads, trims, and mats have visible thickness or a deliberate near-zero clearance for z-fighting avoidance.
- Audit small gaps numerically when the view is ambiguous.
- Prefer slight intentional overlaps at hidden construction contacts over coplanar surfaces.

## Material Read

- Compare the material in both the photo-match camera and a close review camera.
- Tune base color, roughness, clearcoat/specular response, and bump together; a correct color with incorrect reflectance still reads wrong.
- Use UVs or generated coordinates consistently. Avoid procedural noise that creates graphic stripes or high-contrast blotches at reference-camera distance.
- Keep micro-detail subtle. Wood grain, woven fabric, painted lacquer, tile glaze, and wall paint should add variation without becoming the main pattern unless the reference demands it.

## Common Failure Signs

- The surface looks like a flat color plus a noise layer rather than a material.
- A detail is visible only because it is too dark, too thick, or too glossy.
- A mat, tabletop insert, label, or trim appears to hover above its support.
- Rounded corners become soft blobs instead of bevelled manufactured edges.
- A material changes abruptly where one physical object should remain continuous.

## Acceptance

Accept a lookdev repair only after:

- the object reads correctly in `PhotoMatchCamera`
- the close camera shows plausible thickness, attachment, and bevel behavior
- normals and smoothing do not erase construction edges
- the material still belongs to the same object under viewport/render lighting
