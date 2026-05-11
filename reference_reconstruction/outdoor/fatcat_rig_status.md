# Fatcat Rig Status

Updated: 2026-05-11 Asia/Shanghai
Blend file: `fatcat.blend`

## Final Kept Version

- Mesh: `node_0.001`
- Armature: `node_0_deform_rig_v01`
- Final action: `node_0_fat_cat_jump_down_test_v08_relaxed_leaves_ear_sway`
- Current active action before cleanup: `node_0_fat_cat_jump_down_test_v08_relaxed_leaves_ear_sway`
- Final timeline range: `1-88`
- Review frames: `1`, `12`, `22`, `38`, `50`, `58`, `72`, `88`

## Weight Baseline

The accepted weight version is the global topology distance-field rebuild. It was created from the existing influence masks rather than old weight values, giving smoother transitions from support boundaries inward.

- Weighted vertices: `749769 / 749769`
- Zero-weight vertices: `0`
- Deform vertex groups: `28`
- Empty deform groups: `0`
- Max groups per vertex: `6`
- Average groups per weighted vertex: `2.9809`
- Weight sum range: `0.9999997872509994` to `1.000000208732672`

Approved internal backup before cleanup:

- `node_0.001_distance_field_weights_approved_v01`
- `node_0_deform_rig_v01_distance_field_weights_approved_v01`

These backup objects were used only as an internal safety point. After this Markdown export, the blend is cleaned to keep the final working version only.

## Final Animation

Final action: `node_0_fat_cat_jump_down_test_v08_relaxed_leaves_ear_sway`

The final test animation is a high forward jump into a belly landing. It includes:

- Calibrated root-axis mapping: root local `Y` controls world height, root local `Z` controls forward travel toward negative world `Y`.
- Higher starting point and forward travel matched to the model scale.
- Belly-down contact and belly-rest ending.
- Larger leg motion for crouch, push-off, air pose, contact, and settle.
- Larger back-leaf swing in the air.
- Corrected leaf gravity direction at landing.
- Relaxed final leaf pose so the leaves do not curl too tightly.
- Subtle ear follow-through/sway.

Key poses:

| Frame | Marker | Purpose |
|---:|---|---|
| 1 | `jump_high_back_start` | High starting point |
| 12 | `jump_deep_leg_crouch` | Leg-loaded crouch |
| 22 | `jump_big_leg_push_ears_trail` | Push-off with ear follow-through |
| 38 | `jump_wide_leaf_air_swing` | Airborne swing, leaves open |
| 50 | `jump_belly_approach_relaxed_leaves` | Approach belly landing |
| 58 | `jump_belly_contact_soft_leaf_drag` | Belly contact, leaves dragged down |
| 72 | `jump_small_rebound_ear_follow` | Small rebound and ear follow |
| 88 | `jump_belly_rest_relaxed_leaves` | Final belly rest, relaxed leaves |

## Iteration History

Weight and rigging milestones:

- Automatic weights were generated after scaling workaround.
- Body/back coverage was repaired so torso weights affected both front and back.
- Non-main weight islands were removed strictly when requested.
- Boundary ramp and internal smoothing were attempted.
- Final accepted weights came from the topology distance-field rebuild.
- Approved weight version was preserved before animation work.

Jump action iterations:

- `v01`: first extreme jump-down pressure test.
- `v02`: gentler version without bone scaling.
- `v03`: aligned start/end test, later found root-axis mismatch.
- `v04`: calibrated root axes; local `Y` became height, local `Z` became horizontal travel.
- `v05`: forward high jump with belly landing.
- `v06`: larger leg motion and larger back-leaf motion.
- `v07`: corrected back-leaf gravity direction.
- `v08`: relaxed final leaf curl and added subtle ear sway.

## Cleanup Plan Applied

After writing this document, the blend is cleaned to keep only the final version:

Kept:

- `node_0.001`
- `node_0_deform_rig_v01`
- `node_0_fat_cat_jump_down_test_v08_relaxed_leaves_ear_sway`
- Materials used by `node_0.001`

Removed from the blend:

- Intermediate jump actions `v01-v07`
- Diagnostic action `node_0_auto_weights_test_pose_v01`
- Internal `RIG_STATUS_*` Text data-blocks
- Internal backup/approved objects
- Original unrigged mesh `node_0`
- Jump reference marker objects and their marker materials
- Empty helper collections created during the workflow

## Notes For Future Work

- If exporting to a game/runtime target, decide separately whether to run influence limiting or format-specific cleanup.
- The current blend after cleanup is meant to be the clean final rig/animation version, not a full edit-history archive.
- This Markdown file is the external record replacing the internal Blender Text status blocks.


## Control Rig v01

Added after the clean final rig pass.

- Control action: `node_0_fat_cat_jump_down_CTRL_v01`
- Previous direct deformation action preserved in blend: `node_0_fat_cat_jump_down_test_v08_relaxed_leaves_ear_sway`
- Added control bones: `29` `CTRL-*` bones.
- Driven bones: original `root` plus all `DEF-*` deform bones.
- Constraint type: `COPY_TRANSFORMS` from each driven bone to its matching control bone in local space.
- Source `root`/`DEF-*` bones are hidden in the viewport for cleaner animation; they still deform the mesh.
- Control bones are non-deforming and visible.
- Verification against the previous direct action:
  - Max bbox center delta across key frames: `2.980232238769531e-07`
  - Max bbox size delta across key frames: `3.5762786865234375e-07`

Recommended next step: add IK targets/pole controls for hands and feet if FK limb posing feels too slow.


## Limb IK v01

Added four-limb IK controls after `Control Rig v01`.

- IK action: `node_0_fat_cat_jump_down_CTRL_IK_v01`
- FK action preserved: `node_0_fat_cat_jump_down_CTRL_v01`
- IK target bones: `IK-hand.L`, `IK-hand.R`, `IK-foot.L`, `IK-foot.R`
- Pole target bones: `POLE-elbow.L`, `POLE-elbow.R`, `POLE-knee.L`, `POLE-knee.R`
- IK constraints are on: `CTRL-forearm.L`, `CTRL-forearm.R`, `CTRL-shin.L`, `CTRL-shin.R`
- Chain length: `2`
- The original FK action has IK influence keyed to `0`; the new IK action has IK influence keyed to `1`.
- Upper/lower solver controls are hidden for cleaner animation; hand/foot FK controls remain visible for local orientation.
- Verification against `node_0_fat_cat_jump_down_CTRL_v01`:
  - Max bbox center delta across key frames: `0.006361722946166992`
  - Max bbox size delta across key frames: `0.03180134296417236`

Use the IK target bones for placing hands/feet, pole bones for elbow/knee direction, and `CTRL-hand.*` / `CTRL-foot.*` for local hand/foot rotation.
