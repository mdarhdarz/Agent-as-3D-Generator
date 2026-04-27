# Copyright (C) 2026, Princeton University.
# This source code is licensed under the BSD 3-Clause license found in the LICENSE file in the root directory
# of this source tree.

# Authors: OpenAI

import bpy
import numpy as np
from numpy.random import uniform

from infinigen.assets.materials.fabric.fine_knit_fabric import (
    shader_material as shader_fabric_material,
)
from infinigen.assets.materials.metal.brushed_metal import shader_brushed_metal
from infinigen.assets.materials.plastic.plastic_rough import shader_rough_plastic
from infinigen.assets.materials.wood.wood import shader_wood
from infinigen.core import surface, tagging
from infinigen.core.placement.factory import AssetFactory
from infinigen.core.util import blender as butil
from infinigen.core.util.math import FixedSeed


class NapkinHolderFactory(AssetFactory):
    def __init__(self, factory_seed, coarse=False):
        super().__init__(factory_seed, coarse=coarse)

        with FixedSeed(factory_seed):
            self.wall_thickness = uniform(0.004, 0.007)
            self.base_thickness = uniform(0.006, 0.012)
            self.sheet_thickness = uniform(0.0009, 0.0016)
            self.sheet_pitch = self.sheet_thickness * uniform(1.15, 1.65)
            self.napkin_count = int(np.random.randint(18, 34))

            self.stack_length = self.sheet_thickness + (self.napkin_count - 1) * (
                self.sheet_pitch
            )
            self.inner_margin = uniform(0.007, 0.014)
            self.holder_length = self.stack_length + 2 * (
                self.inner_margin + self.wall_thickness * 0.5
            )

            self.napkin_width = uniform(0.09, 0.125)
            self.holder_width = self.napkin_width + uniform(0.012, 0.024)
            self.napkin_height = uniform(0.065, 0.095)
            self.wall_height = self.napkin_height + uniform(0.012, 0.03)
            self.panel_depth = self.holder_width * uniform(0.92, 0.98)

            self.use_press_bar = uniform() < 0.82
            self.bar_radius = uniform(0.0025, 0.0045)
            self.bar_height = self.base_thickness + self.napkin_height * uniform(
                0.60, 0.74
            )

            self.edge_radius = min(self.wall_thickness, self.base_thickness) * uniform(
                0.18, 0.35
            )
            self.body_material = "wood" if uniform() < 0.55 else "plastic"
            neutral = uniform(0.18, 0.55)
            self.body_plastic_color = (
                neutral * uniform(0.9, 1.1),
                neutral * uniform(0.9, 1.1),
                neutral * uniform(0.9, 1.1),
                1.0,
            )
            paper_tone = uniform(0.88, 0.98)
            warm_shift = uniform(-0.03, 0.02)
            self.napkin_color = np.clip(
                np.array(
                    [paper_tone + warm_shift, paper_tone, paper_tone - warm_shift]
                ),
                0.0,
                1.0,
            )
            self.sheet_tilt = uniform(0.015, 0.05)

    def _bevel(self, obj: bpy.types.Object, width: float, segments: int = 3):
        if width <= 0:
            return
        butil.modify_mesh(obj, "BEVEL", apply=True, width=width, segments=segments)

    def _make_base(self):
        base = butil.spawn_cube(
            size=2,
            location=(0, 0, self.base_thickness * 0.5),
            scale=(
                self.holder_length * 0.5,
                self.holder_width * 0.5,
                self.base_thickness * 0.5,
            ),
            name="napkin_holder_base",
        )
        self._bevel(base, self.edge_radius)
        return base

    def _make_panel(self, sign: float):
        panel = butil.spawn_cube(
            size=2,
            location=(
                sign * (self.holder_length * 0.5 - self.wall_thickness * 0.5),
                0,
                self.base_thickness + self.wall_height * 0.5,
            ),
            scale=(
                self.wall_thickness * 0.5,
                self.panel_depth * 0.5,
                self.wall_height * 0.5,
            ),
            name=f"napkin_holder_panel_{'r' if sign > 0 else 'l'}",
        )
        self._bevel(panel, self.edge_radius)
        return panel

    def _make_press_bar(self):
        bar = butil.spawn_cylinder(
            radius=self.bar_radius,
            depth=self.panel_depth * 0.9,
            location=(0, 0, self.bar_height),
            name="napkin_holder_press_bar",
        )
        bar.rotation_euler[0] = np.pi * 0.5
        butil.apply_transform(bar)
        return bar

    def _make_napkin_sheet(self, index: int):
        x = -0.5 * (self.napkin_count - 1) * self.sheet_pitch + index * self.sheet_pitch
        height = self.napkin_height * uniform(0.94, 1.02)
        width = self.napkin_width * uniform(0.96, 1.01)
        thickness = self.sheet_thickness * uniform(0.9, 1.1)
        y = uniform(-self.holder_width * 0.01, self.holder_width * 0.01)

        sheet = butil.spawn_cube(
            size=2,
            location=(x, y, self.base_thickness + height * 0.5),
            scale=(thickness * 0.5, width * 0.5, height * 0.5),
            name=f"napkin_sheet_{index:02d}",
        )
        sheet.rotation_euler[1] = uniform(-self.sheet_tilt, self.sheet_tilt)
        sheet.rotation_euler[2] = uniform(-0.03, 0.03)
        butil.apply_transform(sheet)
        self._bevel(sheet, min(thickness * 0.2, 0.00025), segments=2)
        return sheet

    def create_asset(self, **params) -> bpy.types.Object:
        body_parts = [self._make_base(), self._make_panel(-1.0), self._make_panel(1.0)]

        body_shader = shader_wood
        body_kwargs = {}
        if self.body_material == "plastic":
            body_shader = shader_rough_plastic
            body_kwargs = {"base_color": self.body_plastic_color, "roughness": 0.65}
        surface.add_material(body_parts, body_shader, input_kwargs=body_kwargs)

        detail_parts = []
        if self.use_press_bar:
            press_bar = self._make_press_bar()
            surface.add_material([press_bar], shader_brushed_metal)
            detail_parts.append(press_bar)

        napkins = [self._make_napkin_sheet(i) for i in range(self.napkin_count)]
        surface.add_material(
            napkins,
            shader_fabric_material,
            input_kwargs={
                "_color": self.napkin_color,
                "_roughness": uniform(0.6, 0.9),
                "_thread_density_x": uniform(130, 220),
                "_relative_density_y": uniform(0.85, 1.15),
                "_displacement_scale": uniform(0.0004, 0.0014),
                "_map": "Object",
            },
        )

        obj = butil.join_objects(body_parts + detail_parts + napkins)
        tagging.tag_object(obj, "napkin_holder")
        tagging.tag_system.relabel_obj(obj)
        return obj
