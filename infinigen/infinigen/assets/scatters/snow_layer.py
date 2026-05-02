# Copyright (C) 2023, Princeton University.
# This source code is licensed under the BSD 3-Clause license found in the LICENSE file in the root directory of this source tree.

# Authors: Zeyu Ma


import bpy

from infinigen.core import surface
from infinigen.core.init import require_blender_addon
from infinigen.core.tagging import tag_object
from infinigen.core.util import blender as butil
from infinigen.infinigen_gpl.surfaces.snow import shader_snow

require_blender_addon("real_snow", fail="warn")


class Snowlayer:
    def __init__(self):
        try:
            require_blender_addon("real_snow", fail="fatal")
            self.use_addon = True
        except ValueError:
            self.use_addon = False

    def apply(self, obj, **kwargs):
        if not self.use_addon:
            snow = obj.copy()
            snow.data = obj.data.copy()
            snow.name = "snow"
            bpy.context.scene.collection.objects.link(snow)
            snow.location.z += 0.015
            surface.add_material(snow, shader_snow)
            tag_object(snow, "snow")
            return snow

        bpy.context.scene.snow.height = 0.1
        with butil.SelectObjects(obj):
            bpy.ops.snow.create()
            snow = bpy.context.active_object
        tag_object(snow, "snow")
        return snow


def apply(obj, selection=None):
    snowlayer = Snowlayer()
    snowlayer.apply(obj)
    # snowlayer(obj)
    return snowlayer
