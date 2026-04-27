# Copyright (C) 2024, Princeton University.
# This source code is licensed under the BSD 3-Clause license found in the LICENSE file in the root directory of this source tree.

# Authors: Beining Han

import bpy
import numpy as np
from numpy.random import normal, randint, uniform

from infinigen.assets.objects.shelves.doors import CabinetDoorBaseFactory
from infinigen.assets.objects.shelves.large_shelf import LargeShelfBaseFactory
from infinigen.assets.utils.object import new_bbox
from infinigen.core import surface, tagging
from infinigen.core.nodes.node_wrangler import Nodes, NodeWrangler
from infinigen.core.placement.factory import AssetFactory
from infinigen.core.util import blender as butil
from infinigen.core.util.math import FixedSeed


def shader_wardrobe_wood(nw: NodeWrangler):
    principled_bsdf = nw.new_node(
        Nodes.PrincipledBSDF,
        input_kwargs={
            "Base Color": (0.6650, 0.4480, 0.2100, 1.0000),
            "Roughness": 0.5200,
            "Specular IOR Level": 0.3000,
        },
    )

    material_output = nw.new_node(
        Nodes.MaterialOutput,
        input_kwargs={"Surface": principled_bsdf},
        attrs={"is_active_output": True},
    )


def shader_handle_dark(nw: NodeWrangler):
    principled_bsdf = nw.new_node(
        Nodes.PrincipledBSDF,
        input_kwargs={
            "Base Color": (0.1400, 0.1200, 0.1050, 1.0000),
            "Metallic": 0.9000,
            "Roughness": 0.2800,
        },
    )

    material_output = nw.new_node(
        Nodes.MaterialOutput,
        input_kwargs={"Surface": principled_bsdf},
        attrs={"is_active_output": True},
    )


def shader_wardrobe_shadow(nw: NodeWrangler):
    principled_bsdf = nw.new_node(
        Nodes.PrincipledBSDF,
        input_kwargs={
            "Base Color": (0.0900, 0.0600, 0.0350, 1.0000),
            "Roughness": 0.6800,
            "Specular IOR Level": 0.1200,
        },
    )

    material_output = nw.new_node(
        Nodes.MaterialOutput,
        input_kwargs={"Surface": principled_bsdf},
        attrs={"is_active_output": True},
    )


def shader_wardrobe_grain(nw: NodeWrangler):
    principled_bsdf = nw.new_node(
        Nodes.PrincipledBSDF,
        input_kwargs={
            "Base Color": (0.5200, 0.3300, 0.1500, 1.0000),
            "Roughness": 0.6100,
            "Specular IOR Level": 0.1800,
        },
    )

    material_output = nw.new_node(
        Nodes.MaterialOutput,
        input_kwargs={"Surface": principled_bsdf},
        attrs={"is_active_output": True},
    )


def geometry_cabinet_nodes(nw: NodeWrangler, **kwargs):
    # Code generated using version 2.6.4 of the node_transpiler
    right_door_info = nw.new_node(
        Nodes.ObjectInfo, input_kwargs={"Object": kwargs["door"][0]}
    )
    left_door_info = nw.new_node(
        Nodes.ObjectInfo, input_kwargs={"Object": kwargs["door"][1]}
    )
    shelf_info = nw.new_node(Nodes.ObjectInfo, input_kwargs={"Object": kwargs["shelf"]})

    doors = []
    transform_r = nw.new_node(
        Nodes.Transform,
        input_kwargs={
            "Geometry": right_door_info.outputs["Geometry"],
            "Translation": kwargs["door_hinge_pos"][0],
            "Rotation": (0, 0, kwargs["door_open_angle"]),
        },
    )
    doors.append(transform_r)
    if len(kwargs["door_hinge_pos"]) > 1:
        transform_l = nw.new_node(
            Nodes.Transform,
            input_kwargs={
                "Geometry": left_door_info.outputs["Geometry"],
                "Translation": kwargs["door_hinge_pos"][1],
                "Rotation": (0, 0, kwargs["door_open_angle"]),
            },
        )
        doors.append(transform_l)

    attaches = []
    for pos in kwargs["attach_pos"]:
        cube = nw.new_node(
            Nodes.MeshCube, input_kwargs={"Size": (0.0006, 0.0200, 0.04500)}
        )

        combine_xyz = nw.new_node(Nodes.CombineXYZ, input_kwargs={"Y": -0.0100})

        transform = nw.new_node(
            Nodes.Transform, input_kwargs={"Geometry": cube, "Translation": combine_xyz}
        )

        cube_1 = nw.new_node(
            Nodes.MeshCube, input_kwargs={"Size": (0.0005, 0.0340, 0.0200)}
        )

        join_geometry = nw.new_node(
            Nodes.JoinGeometry, input_kwargs={"Geometry": [transform, cube_1]}
        )

        transform_1 = nw.new_node(
            Nodes.Transform,
            input_kwargs={
                "Geometry": join_geometry,
                "Translation": (0.0000, -0.0170, 0.0000),
            },
        )

        transform_2 = nw.new_node(
            Nodes.Transform,
            input_kwargs={
                "Geometry": transform_1,
                "Rotation": (0.0000, 0.0000, -1.5708),
            },
        )

        transform_3 = nw.new_node(
            Nodes.Transform, input_kwargs={"Geometry": transform_2, "Translation": pos}
        )

        attaches.append(transform_3)

    join_geometry_a = nw.new_node(
        Nodes.JoinGeometry, input_kwargs={"Geometry": attaches}
    )

    join_geometry = nw.new_node(
        Nodes.JoinGeometry, input_kwargs={"Geometry": doors + [join_geometry_a]}
    )

    group_output = nw.new_node(
        Nodes.GroupOutput,
        input_kwargs={"Geometry": join_geometry},
        attrs={"is_active_output": True},
    )


class SingleCabinetBaseFactory(AssetFactory):
    def __init__(self, factory_seed, params={}, coarse=False):
        super(SingleCabinetBaseFactory, self).__init__(factory_seed, coarse=coarse)
        self.shelf_params = {}
        self.door_params = {}
        self.mat_params = {}
        self.shelf_fac = LargeShelfBaseFactory(factory_seed)
        self.door_fac = CabinetDoorBaseFactory(factory_seed)
        with FixedSeed(factory_seed):
            self.params = self.sample_params()

    def sample_params(self):
        # Update fac params
        pass

    def get_material_params(self):
        with FixedSeed(self.factory_seed):
            params = self.mat_params.copy()
            if params.get("frame_material", None) is None:
                params["frame_material"] = np.random.choice(
                    ["white", "black_wood", "wood"], p=[0.5, 0.2, 0.3]
                )
            return params

    def get_shelf_params(self, i=0):
        params = self.shelf_params.copy()
        if params.get("shelf_cell_width", None) is None:
            params["shelf_cell_width"] = [
                np.random.choice([0.76, 0.36], p=[0.5, 0.5])
                * np.clip(normal(1.0, 0.1), 0.75, 1.25)
            ]
        if params.get("shelf_cell_height", None) is None:
            num_v_cells = randint(3, 7)
            shelf_cell_height = []
            for i in range(num_v_cells):
                shelf_cell_height.append(0.3 * np.clip(normal(1.0, 0.06), 0.75, 1.25))
            params["shelf_cell_height"] = shelf_cell_height
        if params.get("frame_material", None) is None:
            params["frame_material"] = self.mat_params["frame_material"]

        return params

    def get_door_params(self, i=0):
        params = self.door_params.copy()

        # get door params
        shelf_width = (
            self.shelf_params["shelf_width"]
            + self.shelf_params["side_board_thickness"] * 2
        )
        if params.get("door_width", None) is None:
            if shelf_width < 0.55:
                params["door_width"] = shelf_width
                params["num_door"] = 1
            else:
                params["door_width"] = shelf_width / 2.0 - 0.0005
                params["num_door"] = 2
        if params.get("door_height", None) is None:
            params["door_height"] = (
                self.shelf_params["division_board_z_translation"][-1]
                - self.shelf_params["division_board_z_translation"][0]
                + self.shelf_params["division_board_thickness"]
            )
            if len(
                self.shelf_params["division_board_z_translation"]
            ) > 5 and np.random.choice([True, False], p=[0.5, 0.5]):
                params["door_height"] = (
                    self.shelf_params["division_board_z_translation"][3]
                    - self.shelf_params["division_board_z_translation"][0]
                    + self.shelf_params["division_board_thickness"]
                )
        if params.get("frame_material", None) is None:
            params["frame_material"] = self.mat_params["frame_material"]

        return params

    def get_cabinet_params(self, i=0):
        params = dict()

        shelf_width = (
            self.shelf_params["shelf_width"]
            + self.shelf_params["side_board_thickness"] * 2
        )
        if self.door_params["num_door"] == 1:
            params["door_hinge_pos"] = [
                (
                    self.shelf_params["shelf_depth"] / 2.0 + 0.0025,
                    -shelf_width / 2.0,
                    self.shelf_params["bottom_board_height"],
                )
            ]
            params["door_open_angle"] = 0
            params["attach_pos"] = [
                (
                    self.shelf_params["shelf_depth"] / 2.0,
                    -self.shelf_params["shelf_width"] / 2.0,
                    self.shelf_params["bottom_board_height"] + z,
                )
                for z in self.door_params["attach_height"]
            ]
        elif self.door_params["num_door"] == 2:
            params["door_hinge_pos"] = [
                (
                    self.shelf_params["shelf_depth"] / 2.0 + 0.008,
                    -shelf_width / 2.0,
                    self.shelf_params["bottom_board_height"],
                ),
                (
                    self.shelf_params["shelf_depth"] / 2.0 + 0.008,
                    shelf_width / 2.0,
                    self.shelf_params["bottom_board_height"],
                ),
            ]
            params["door_open_angle"] = 0
            params["attach_pos"] = [
                (
                    self.shelf_params["shelf_depth"] / 2.0,
                    -self.shelf_params["shelf_width"] / 2.0,
                    self.shelf_params["bottom_board_height"] + z,
                )
                for z in self.door_params["attach_height"]
            ] + [
                (
                    self.shelf_params["shelf_depth"] / 2.0,
                    self.shelf_params["shelf_width"] / 2.0,
                    self.shelf_params["bottom_board_height"] + z,
                )
                for z in self.door_params["attach_height"]
            ]
        else:
            raise NotImplementedError

        return params

    def get_cabinet_components(self, i):
        # update material params
        self.mat_params = self.get_material_params()

        # create shelf
        shelf_params = self.get_shelf_params(i=i)
        self.shelf_fac.params = shelf_params
        shelf, shelf_params = self.shelf_fac.create_asset(i=i, ret_params=True)
        shelf.name = "cabinet_frame"
        self.shelf_params = shelf_params

        # create doors
        door_params = self.get_door_params(i=i)
        self.door_fac.params = door_params
        self.door_fac.params["door_left_hinge"] = False
        right_door, door_obj_params = self.door_fac.create_asset(i=i, ret_params=True)
        right_door.name = "cabinet_right_door"
        self.door_fac.params = door_obj_params
        self.door_fac.params["door_left_hinge"] = True
        left_door, _ = self.door_fac.create_asset(i=i, ret_params=True)
        left_door.name = "cabinet_left_door"
        self.door_params = door_obj_params

        return shelf, right_door, left_door

    def create_asset(self, i=0, **params):
        bpy.ops.mesh.primitive_plane_add(
            size=1,
            enter_editmode=False,
            align="WORLD",
            location=(0, 0, 0),
            scale=(1, 1, 1),
        )
        obj = bpy.context.active_object

        shelf, right_door, left_door = self.get_cabinet_components(i=i)

        # create cabinet
        cabinet_params = self.get_cabinet_params(i=i)
        surface.add_geomod(
            obj,
            geometry_cabinet_nodes,
            attributes=[],
            apply=True,
            input_kwargs={
                "door": [right_door, left_door],
                "shelf": shelf,
                "door_hinge_pos": cabinet_params["door_hinge_pos"],
                "door_open_angle": cabinet_params["door_open_angle"],
                "attach_pos": cabinet_params["attach_pos"],
            },
        )
        butil.delete([left_door, right_door])
        obj = butil.join_objects([shelf, obj])

        tagging.tag_system.relabel_obj(obj)
        return obj


class SingleCabinetFactory(SingleCabinetBaseFactory):
    def __init__(
        self, factory_seed, params=None, coarse=False, dimensions=None, style_preset=None
    ):
        self.dimensions_override = dimensions
        self.style_preset = style_preset or "random"
        super().__init__(factory_seed, params={} if params is None else params, coarse=coarse)
        self.apply_style_preset()

    def apply_style_preset(self):
        if self.style_preset == "random":
            return

        if self.style_preset != "wardrobe_flat":
            raise ValueError(
                f"Unknown SingleCabinetFactory style preset: {self.style_preset}"
            )

        width, depth, height = self.dimensions_override or (2.28, 0.62, 2.18)
        panel_count = 4
        side_margin = 0.045
        door_gap = 0.012
        door_width = (width - side_margin * 2 - door_gap * (panel_count - 1)) / panel_count
        bottom_margin = 0.125
        top_margin = 0.120
        door_height = height - bottom_margin - top_margin

        self.dims = (width, depth, height)
        self.params = {
            "Dimensions": self.dims,
            "panel_count": panel_count,
            "door_gap": door_gap,
            "side_margin": side_margin,
            "door_width": door_width,
            "door_height": door_height,
            "door_thickness": 0.040,
            "raised_frame_depth": 0.018,
            "center_panel_depth": 0.010,
            "carcass_thickness": 0.045,
            "door_frame_width": 0.045,
            "door_frame_top_bottom": 0.060,
            "bottom_margin": bottom_margin,
            "top_margin": top_margin,
            "toe_kick_height": 0.095,
            "toe_kick_recess": 0.060,
            "crown_height": 0.045,
            "handle_radius": 0.008,
            "handle_standoff_radius": 0.007,
            "handle_standoff_depth": 0.030,
            "handle_height": 0.390,
            "handle_inset": 0.060,
            "handle_bottom": bottom_margin + door_height * 0.365,
            "grain_line_count": 5,
        }

    def sample_params(self):
        params = dict()
        params["Dimensions"] = (
            uniform(0.25, 0.35),
            uniform(0.3, 0.7),
            uniform(0.9, 1.8),
        )

        params["bottom_board_height"] = 0.083
        params["shelf_depth"] = params["Dimensions"][0] - 0.01
        num_h = int((params["Dimensions"][2] - 0.083) / 0.3)
        params["shelf_cell_height"] = [
            (params["Dimensions"][2] - 0.083) / num_h for _ in range(num_h)
        ]
        params["shelf_cell_width"] = [params["Dimensions"][1]]
        self.shelf_params = params
        self.dims = params["Dimensions"]

    def create_placeholder(self, **kwargs) -> bpy.types.Object:
        if self.style_preset == "wardrobe_flat":
            x, y, z = self.dims
            return new_bbox(-x / 2, x / 2, -y / 2, y / 2, 0, z)

        x, y, z = self.dims
        return new_bbox(
            -x / 2 * 1.2, x / 2 * 1.2, -y / 2 * 1.2, y / 2 * 1.2, 0, (z + 0.083) * 1.02
        )

    def create_asset(self, i=0, **params):
        if self.style_preset == "wardrobe_flat":
            return self.create_wardrobe_flat_asset()

        return super().create_asset(i=i, **params)

    def create_wardrobe_flat_asset(self):
        width, depth, height = self.dims
        door_count = self.params["panel_count"]
        door_gap = self.params["door_gap"]
        side_margin = self.params["side_margin"]
        door_width = self.params["door_width"]
        door_height = self.params["door_height"]
        door_thickness = self.params["door_thickness"]
        raised_frame_depth = self.params["raised_frame_depth"]
        center_panel_depth = self.params["center_panel_depth"]
        carcass_thickness = self.params["carcass_thickness"]
        door_frame_width = self.params["door_frame_width"]
        door_frame_top_bottom = self.params["door_frame_top_bottom"]
        bottom_margin = self.params["bottom_margin"]
        top_margin = self.params["top_margin"]
        toe_kick_height = self.params["toe_kick_height"]
        toe_kick_recess = self.params["toe_kick_recess"]
        crown_height = self.params["crown_height"]

        wood_mat = surface.shaderfunc_to_material(shader_wardrobe_wood)
        handle_mat = surface.shaderfunc_to_material(shader_handle_dark)
        shadow_mat = surface.shaderfunc_to_material(shader_wardrobe_shadow)
        grain_mat = surface.shaderfunc_to_material(shader_wardrobe_grain)
        parts = []

        front_y = -depth / 2
        back_y = depth / 2

        def add_box(name, x0, x1, y0, y1, z0, z1, mat):
            obj = new_bbox(x0, x1, y0, y1, z0, z1)
            obj.name = name
            surface.assign_material(obj, mat)
            parts.append(obj)
            return obj

        def add_handle_cylinder(name, loc, radius, length, mat, axis="Z"):
            rotation = (0, 0, 0)
            if axis == "Y":
                rotation = (1.57079632679, 0, 0)
            elif axis == "X":
                rotation = (0, 1.57079632679, 0)
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=18,
                radius=radius,
                depth=length,
                end_fill_type="NGON",
                location=loc,
                rotation=rotation,
            )
            obj = bpy.context.active_object
            obj.name = name
            surface.assign_material(obj, mat)
            parts.append(obj)
            return obj

        # Carcass pieces stay separate until final join, so seams and reveals read as real joinery.
        add_box(
            "wardrobe_left_side",
            -width / 2,
            -width / 2 + carcass_thickness,
            front_y,
            back_y,
            0,
            height,
            wood_mat,
        )
        add_box(
            "wardrobe_right_side",
            width / 2 - carcass_thickness,
            width / 2,
            front_y,
            back_y,
            0,
            height,
            wood_mat,
        )
        add_box(
            "wardrobe_top_board",
            -width / 2,
            width / 2,
            front_y,
            back_y,
            height - carcass_thickness,
            height,
            wood_mat,
        )
        add_box(
            "wardrobe_bottom_board",
            -width / 2,
            width / 2,
            front_y + toe_kick_recess,
            back_y,
            0,
            toe_kick_height,
            wood_mat,
        )
        add_box(
            "wardrobe_toe_shadow",
            -width / 2 + carcass_thickness,
            width / 2 - carcass_thickness,
            front_y - 0.006,
            front_y + toe_kick_recess,
            0.018,
            toe_kick_height,
            shadow_mat,
        )
        add_box(
            "wardrobe_back_shadow",
            -width / 2 + carcass_thickness,
            width / 2 - carcass_thickness,
            back_y - 0.020,
            back_y,
            toe_kick_height,
            height - carcass_thickness,
            shadow_mat,
        )
        add_box(
            "wardrobe_crown_front_lip",
            -width / 2 - 0.012,
            width / 2 + 0.012,
            front_y - 0.030,
            front_y + 0.018,
            height - crown_height,
            height,
            wood_mat,
        )
        add_box(
            "wardrobe_lower_front_rail",
            -width / 2,
            width / 2,
            front_y - 0.014,
            front_y + 0.020,
            bottom_margin - 0.035,
            bottom_margin + 0.010,
            wood_mat,
        )

        handle_height = self.params["handle_height"]
        handle_radius = self.params["handle_radius"]
        handle_standoff_radius = self.params["handle_standoff_radius"]
        handle_standoff_depth = self.params["handle_standoff_depth"]
        handle_inset = self.params["handle_inset"]
        handle_bottom = self.params["handle_bottom"]
        grain_line_count = self.params["grain_line_count"]

        door_front_y = front_y - door_thickness
        raised_front_y = door_front_y - raised_frame_depth
        center_front_y = door_front_y - center_panel_depth
        door_top = height - top_margin

        for idx in range(door_count):
            x0 = -width / 2 + side_margin + idx * (door_width + door_gap)
            x1 = x0 + door_width

            add_box(
                f"wardrobe_door_backing_{idx}",
                x0,
                x1,
                door_front_y,
                front_y + 0.010,
                bottom_margin,
                door_top,
                wood_mat,
            )
            add_box(
                f"wardrobe_door_left_stile_{idx}",
                x0,
                x0 + door_frame_width,
                raised_front_y,
                door_front_y,
                bottom_margin,
                door_top,
                wood_mat,
            )
            add_box(
                f"wardrobe_door_right_stile_{idx}",
                x1 - door_frame_width,
                x1,
                raised_front_y,
                door_front_y,
                bottom_margin,
                door_top,
                wood_mat,
            )
            add_box(
                f"wardrobe_door_top_rail_{idx}",
                x0,
                x1,
                raised_front_y,
                door_front_y,
                door_top - door_frame_top_bottom,
                door_top,
                wood_mat,
            )
            add_box(
                f"wardrobe_door_bottom_rail_{idx}",
                x0,
                x1,
                raised_front_y,
                door_front_y,
                bottom_margin,
                bottom_margin + door_frame_top_bottom,
                wood_mat,
            )
            add_box(
                f"wardrobe_door_center_panel_{idx}",
                x0 + door_frame_width,
                x1 - door_frame_width,
                center_front_y,
                door_front_y + 0.004,
                bottom_margin + door_frame_top_bottom,
                door_top - door_frame_top_bottom,
                wood_mat,
            )

            groove_y0 = raised_front_y - 0.004
            groove_y1 = raised_front_y - 0.001
            add_box(
                f"wardrobe_panel_left_reveal_{idx}",
                x0 + door_frame_width - 0.004,
                x0 + door_frame_width + 0.004,
                groove_y0,
                groove_y1,
                bottom_margin + door_frame_top_bottom,
                door_top - door_frame_top_bottom,
                shadow_mat,
            )
            add_box(
                f"wardrobe_panel_right_reveal_{idx}",
                x1 - door_frame_width - 0.004,
                x1 - door_frame_width + 0.004,
                groove_y0,
                groove_y1,
                bottom_margin + door_frame_top_bottom,
                door_top - door_frame_top_bottom,
                shadow_mat,
            )
            add_box(
                f"wardrobe_panel_top_reveal_{idx}",
                x0 + door_frame_width,
                x1 - door_frame_width,
                groove_y0,
                groove_y1,
                door_top - door_frame_top_bottom - 0.004,
                door_top - door_frame_top_bottom + 0.004,
                shadow_mat,
            )
            add_box(
                f"wardrobe_panel_bottom_reveal_{idx}",
                x0 + door_frame_width,
                x1 - door_frame_width,
                groove_y0,
                groove_y1,
                bottom_margin + door_frame_top_bottom - 0.004,
                bottom_margin + door_frame_top_bottom + 0.004,
                shadow_mat,
            )

            if idx > 0:
                seam_x = x0 - door_gap / 2
                add_box(
                    f"wardrobe_vertical_door_shadow_{idx}",
                    seam_x - 0.003,
                    seam_x + 0.003,
                    raised_front_y - 0.006,
                    raised_front_y - 0.002,
                    bottom_margin + 0.020,
                    door_top - 0.020,
                    shadow_mat,
                )

            grain_span_x = door_width - door_frame_width * 2
            for g in range(grain_line_count):
                t = (g + 1) / (grain_line_count + 1)
                jitter = ((idx * 37 + g * 17) % 11 - 5) * 0.0015
                gx = x0 + door_frame_width + grain_span_x * t + jitter
                add_box(
                    f"wardrobe_subtle_grain_{idx}_{g}",
                    gx - 0.0010,
                    gx + 0.0010,
                    raised_front_y - 0.003,
                    raised_front_y - 0.001,
                    bottom_margin + door_frame_top_bottom + 0.045,
                    door_top - door_frame_top_bottom - 0.045,
                    grain_mat,
                )

            handle_center_x = x1 - handle_inset
            handle_center_z = handle_bottom + handle_height / 2
            handle_y = raised_front_y - handle_standoff_depth
            add_handle_cylinder(
                f"wardrobe_vertical_pull_{idx}",
                (handle_center_x, handle_y, handle_center_z),
                handle_radius,
                handle_height,
                handle_mat,
                axis="Z",
            )
            for mount_z in (
                handle_bottom + 0.030,
                handle_bottom + handle_height - 0.030,
            ):
                add_handle_cylinder(
                    f"wardrobe_pull_standoff_{idx}_{round(mount_z, 3)}",
                    (
                        handle_center_x,
                        handle_y + handle_standoff_depth / 2,
                        mount_z,
                    ),
                    handle_standoff_radius,
                    handle_standoff_depth,
                    handle_mat,
                    axis="Y",
                )

        obj = butil.join_objects(parts)
        obj.name = "wardrobe_flat_procedural"
        bevel = obj.modifiers.new("small_joinery_bevel", "BEVEL")
        bevel.width = 0.004
        bevel.segments = 2
        bevel.affect = "EDGES"
        normals = obj.modifiers.new("weighted_joinery_normals", "WEIGHTED_NORMAL")
        normals.keep_sharp = True
        obj["infinigen_style_preset"] = "wardrobe_flat"
        obj["panel_count"] = door_count
        obj["door_gap"] = door_gap
        obj["generated_detail_level"] = "high"
        tagging.tag_system.relabel_obj(obj)
        return obj


class WardrobeFlatCabinetFactory(SingleCabinetFactory):
    def __init__(
        self, factory_seed, params=None, coarse=False, dimensions=None, style_preset=None
    ):
        super().__init__(
            factory_seed,
            params=params,
            coarse=coarse,
            dimensions=dimensions or (2.28, 0.675, 2.18),
            style_preset=style_preset or "wardrobe_flat",
        )
