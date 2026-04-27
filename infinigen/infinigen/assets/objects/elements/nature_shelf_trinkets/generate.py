# Copyright (C) 2023, Princeton University.
# This source code is licensed under the BSD 3-Clause license found in the LICENSE file in the root directory of this source tree.

# Authors: Stamatis Alexandropulos


# Authors: Stamatis Alexandropulos


import logging

import bpy
import mathutils
import numpy as np
import trimesh

from infinigen.assets.objects import corals, creatures, mollusk, monocot, rocks
from infinigen.assets.utils import object as obj
from infinigen.assets.utils.object import join_objects
from infinigen.core.placement.factory import AssetFactory
from infinigen.core.util import blender as butil
from infinigen.core.util.math import FixedSeed, int_hash

logger = logging.getLogger(__name__)


class NatureShelfTrinketsFactory(AssetFactory):
    factories = [
        corals.CoralFactory,
        rocks.BlenderRockFactory,
        rocks.BoulderFactory,
        monocot.PineconeFactory,
        mollusk.MolluskFactory,
        mollusk.AugerFactory,
        mollusk.ClamFactory,
        mollusk.ConchFactory,
        mollusk.MusselFactory,
        mollusk.ScallopFactory,
        mollusk.VoluteFactory,
        creatures.CarnivoreFactory,
        creatures.HerbivoreFactory,
    ]
    probs = np.array([1, 1, 1, 1, 3, 2, 3, 2, 2, 2, 2, 5, 5])
    non_creature_factories = factories[:-2]
    non_creature_probs = probs[:-2]

    def __init__(self, factory_seed, coarse=False):
        super(NatureShelfTrinketsFactory, self).__init__(factory_seed, coarse)
        with FixedSeed(self.factory_seed):
            self.base_factory = self._sample_base_factory()

    def _sample_base_factory(self, allow_creatures=True, key="base"):
        if allow_creatures:
            factories = self.factories
            probs = self.probs
        else:
            factories = self.non_creature_factories
            probs = self.non_creature_probs

        seed = self.factory_seed if allow_creatures and key == "base" else int_hash((self.factory_seed, key))
        with FixedSeed(seed):
            base_factory_fn = np.random.choice(factories, p=probs / probs.sum())

        kwargs = {}
        if base_factory_fn in [
            creatures.HerbivoreFactory,
            creatures.CarnivoreFactory,
        ]:
            kwargs["hair"] = False
        return base_factory_fn(self.factory_seed, **kwargs)

    def create_placeholder(self, **params) -> bpy.types.Object:
        size = np.random.uniform(0.1, 0.15)
        bpy.ops.mesh.primitive_cube_add(size=size, location=(0, 0, size / 2))
        placeholder = bpy.context.active_object
        return placeholder

    def create_asset(self, i, placeholder=None, **params):
        try:
            asset = self.base_factory.spawn_asset(
                np.random.randint(1e7), distance=200, adaptive_resolution=False
            )
        except MemoryError:
            if not isinstance(
                self.base_factory,
                (creatures.HerbivoreFactory, creatures.CarnivoreFactory),
            ):
                raise
            fallback_factory = self._sample_base_factory(
                allow_creatures=False, key=f"fallback_{i}"
            )
            logger.warning(
                "NatureShelfTrinketsFactory(%s) fell back from %s to %s after MemoryError",
                self.factory_seed,
                self.base_factory.__class__.__name__,
                fallback_factory.__class__.__name__,
            )
            self.base_factory = fallback_factory
            asset = self.base_factory.spawn_asset(
                np.random.randint(1e7), distance=200, adaptive_resolution=False
            )

        if list(asset.children):
            asset = join_objects(list(asset.children))

        # butil.modify_mesh(asset, 'DECIMATE')
        butil.apply_transform(asset, loc=True)
        butil.apply_modifiers(asset)
        if isinstance(self.base_factory, creatures.HerbivoreFactory) or isinstance(
            self.base_factory, creatures.CarnivoreFactory
        ):
            pass
        else:
            if not isinstance(asset, trimesh.Trimesh):
                mesh = obj.obj2trimesh(asset)
            stable_poses, probs = trimesh.poses.compute_stable_poses(mesh)
            stable_pose = stable_poses[np.argmax(probs)]
            asset.rotation_euler = mathutils.Matrix(stable_pose[:3, :3]).to_euler()
        butil.apply_transform(asset, rot=True)
        dim = asset.dimensions
        bounding_box = placeholder.dimensions
        scale = min([bounding_box[i] / dim[i] for i in range(3)])
        asset.scale = [scale for i in range(3)]
        # asset.dimensions = placeholder.dimensions
        butil.apply_transform(asset, loc=True)
        bounds = butil.bounds(asset)
        cur_loc = asset.location
        new_location = [
            cur_loc[i] - (bounds[0][i] + bounds[1][i]) / 2 for i in range(3)
        ]
        new_location[2] = cur_loc[2] - (bounds[0][2] + bounding_box[2] / 2)
        asset.location = new_location
        butil.apply_transform(asset, loc=True)
        return asset
