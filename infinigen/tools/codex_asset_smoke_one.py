import argparse
import json
import sys
import traceback
from pathlib import Path

import bpy
import gin

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from infinigen.core import init, surface, tagging
from infinigen.core.init import configure_blender
from infinigen.core.placement import density
from infinigen.core.rendering.render import set_displacement_mode
from infinigen.core.util import blender as butil
from infinigen.core.util.logging import save_polycounts
from infinigen.core.util.math import FixedSeed
from infinigen.core.util.test_utils import import_item


def setup_runtime(config_profile):
    gin.clear_config()
    if config_profile == "nature":
        config_folders = ["infinigen_examples/configs_nature"]
        configs = ["base_nature.gin"]
    else:
        config_folders = [
            "infinigen_examples/configs_indoor",
            "infinigen_examples/configs_nature",
        ]
        configs = ["base_indoors.gin"]
    init.apply_gin_configs(
        config_folders=config_folders,
        configs=configs,
        overrides=["configure_cycles_devices.use_gpu=False"],
        skip_unknown=True,
        finalize_config=False,
    )
    gin.unlock_config()
    configure_blender()


def validate_object_tree(asset):
    if not isinstance(asset, bpy.types.Object):
        raise ValueError(f"Expected bpy.types.Object, got {type(asset)}")
    if tuple(asset.location) != (0, 0, 0):
        raise ValueError(f"{asset.name} has nonzero location {tuple(asset.location)}")
    if tuple(asset.rotation_euler) != (0, 0, 0):
        raise ValueError(f"{asset.name} has nonzero rotation {tuple(asset.rotation_euler)}")
    if tuple(asset.scale) != (1, 1, 1):
        raise ValueError(f"{asset.name} has non-unit scale {tuple(asset.scale)}")

    for obj in butil.iter_object_tree(asset):
        for slot in obj.material_slots:
            if slot.material is None:
                raise ValueError(f"{asset.name}: {obj.name} has empty material slot")

        for mod in obj.modifiers:
            if mod.type in {"NODES", "SUBSURF"}:
                raise ValueError(
                    f"{asset.name}: {obj.name} has unapplied {mod.type} modifier {mod.name}"
                )

        if obj.type != "MESH":
            continue
        if obj.data is None:
            raise ValueError(f"{asset.name}: {obj.name} has no mesh data")
        if len(obj.data.vertices) <= 2:
            raise ValueError(
                f"{asset.name}: {obj.name} has only {len(obj.data.vertices)} vertices"
            )
        if tagging.COMBINED_ATTR_NAME in obj.data.attributes:
            attr = obj.data.attributes[tagging.COMBINED_ATTR_NAME]
            if attr.domain != "FACE":
                raise ValueError(
                    f"{asset.name}: {attr.name} has domain {attr.domain}, expected FACE"
                )
        for attr in obj.data.attributes:
            if attr.name.startswith(tagging.PREFIX):
                raise ValueError(
                    f"{asset.name}: {obj.name} has unmerged tag attribute {attr.name}"
                )


def save_scene(out_dir, asset_name, autopack):
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "polycounts.txt").open("w") as handle:
        save_polycounts(handle)
    set_displacement_mode()
    butil.save_blend(out_dir / "scene.blend", autopack=autopack, purge_orphans=True)
    (out_dir / "asset.json").write_text(
        json.dumps({"asset": asset_name}, indent=2), encoding="utf-8"
    )


def save_partial_scene(out_dir, asset_name, autopack):
    out_dir.mkdir(parents=True, exist_ok=True)
    if (out_dir / "scene.blend").exists():
        return
    try:
        butil.save_blend(out_dir / "partial_scene.blend", autopack=autopack, purge_orphans=True)
        (out_dir / "asset.json").write_text(
            json.dumps({"asset": asset_name, "partial": True}, indent=2),
            encoding="utf-8",
        )
    except Exception:
        traceback.print_exc()


def run_mesh(pathspec, out_dir, seed, distance, autopack):
    cls = import_item(pathspec)
    with FixedSeed(seed):
        butil.clear_scene()
        fac = cls(seed)
        asset = fac.spawn_asset(seed, distance=distance)
        fac.finalize_assets(asset)
    save_scene(out_dir, pathspec, autopack)
    validate_object_tree(asset)


def make_material_target():
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.8, subdivisions=5)
    return bpy.context.active_object


def assign_or_apply_material(generator, target):
    if hasattr(generator, "apply"):
        generator.apply(target)
        return
    material = generator()
    if not isinstance(material, bpy.types.Material):
        raise ValueError(f"Expected bpy.types.Material, got {type(material)}")
    target.data.materials.append(material)


def run_material(pathspec, out_dir, seed, autopack, deprecated=False):
    cls = import_item(pathspec)
    with FixedSeed(seed):
        butil.clear_scene()
        target = make_material_target()
        generator = cls() if type(cls) is type else cls
        assign_or_apply_material(generator, target)
        if deprecated and hasattr(generator, "apply"):
            target2 = make_material_target()
            target2.location.x = 2.0
            generator.apply([target, target2])
    save_scene(out_dir, pathspec, autopack)


def run_scatter(pathspec, out_dir, seed, autopack, scatter_subdivisions, scatter_density):
    cls = import_item(pathspec)
    with FixedSeed(seed):
        butil.clear_scene()
        bpy.ops.mesh.primitive_grid_add(
            size=10,
            x_subdivisions=scatter_subdivisions,
            y_subdivisions=scatter_subdivisions,
        )
        plane = bpy.context.active_object
        scatter = cls()
        scatter.apply(plane, selection=density.placement_mask(scatter_density, 0.45))
    save_scene(out_dir, pathspec, autopack)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", required=True, choices=["mesh", "material", "material_deprecated", "scatter"])
    parser.add_argument("--profile", required=True, choices=["indoor", "nature"])
    parser.add_argument("--pathspec", required=True)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--seed", default=0, type=int)
    parser.add_argument("--distance", default=50, type=float)
    parser.add_argument("--scatter-subdivisions", default=160, type=int)
    parser.add_argument("--scatter-density", default=0.15, type=float)
    parser.add_argument("--autopack", action="store_true")
    args = parser.parse_args()

    setup_runtime(args.profile)
    try:
        if args.kind == "mesh":
            run_mesh(args.pathspec, args.out_dir, args.seed, args.distance, args.autopack)
        elif args.kind == "scatter":
            run_scatter(
                args.pathspec,
                args.out_dir,
                args.seed,
                args.autopack,
                args.scatter_subdivisions,
                args.scatter_density,
            )
        else:
            run_material(
                args.pathspec,
                args.out_dir,
                args.seed,
                args.autopack,
                deprecated=args.kind == "material_deprecated",
            )
    except Exception:
        save_partial_scene(args.out_dir, args.pathspec, args.autopack)
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
