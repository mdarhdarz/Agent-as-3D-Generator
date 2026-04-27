# Copyright (C) 2023, Princeton University.
# This source code is licensed under the BSD 3-Clause license found in the LICENSE file in the root directory of this source tree.

# Authors: Yiming Zuo


import bpy
from numpy.random import choice, normal, uniform

from infinigen.assets.composition import material_assignments
from infinigen.assets.utils.decorate import read_center, read_normal
from infinigen.assets.utils.object import join_objects, new_bbox
from infinigen.assets.objects.tables.legs.single_stand import (
    nodegroup_generate_single_stand,
)
from infinigen.assets.objects.tables.legs.square import nodegroup_generate_leg_square
from infinigen.assets.objects.tables.legs.straight import (
    nodegroup_generate_leg_straight,
)
from infinigen.assets.objects.tables.strechers import nodegroup_strecher
from infinigen.assets.objects.tables.table_top import nodegroup_generate_table_top
from infinigen.assets.objects.tables.table_utils import (
    nodegroup_create_anchors,
    nodegroup_create_legs_and_strechers,
)
from infinigen.core import surface, tagging
from infinigen.core import tags as t
from infinigen.core.nodes import node_utils

# from infinigen.assets.materials import metal, metal_shader_list
# from infinigen.assets.materials.fabrics import fabric
from infinigen.core.nodes.node_wrangler import Nodes, NodeWrangler
from infinigen.core.placement.factory import AssetFactory
from infinigen.core.surface import NoApply
from infinigen.core.util import blender as butil
from infinigen.core.util.math import FixedSeed
from infinigen.core.util.random import weighted_sample


@node_utils.to_nodegroup(
    "geometry_create_legs", singleton=False, type="GeometryNodeTree"
)
def geometry_create_legs(nw: NodeWrangler, **kwargs):
    createanchors = nw.new_node(
        nodegroup_create_anchors().name,
        input_kwargs={
            "Profile N-gon": kwargs["Leg Number"],
            "Profile Width": kwargs["Leg Placement Top Relative Scale"]
            * kwargs["Top Profile Width"],
            "Profile Aspect Ratio": kwargs["Top Profile Aspect Ratio"],
        },
    )

    if kwargs["Leg Style"] == "single_stand":
        leg = nw.new_node(
            nodegroup_generate_single_stand(**kwargs).name,
            input_kwargs={
                "Leg Height": kwargs["Leg Height"],
                "Leg Diameter": kwargs["Leg Diameter"],
                "Resolution": 64,
            },
        )

        leg = nw.new_node(
            nodegroup_create_legs_and_strechers().name,
            input_kwargs={
                "Anchors": createanchors,
                "Keep Legs": True,
                "Leg Instance": leg,
                "Table Height": kwargs["Top Height"],
                "Leg Bottom Relative Scale": kwargs[
                    "Leg Placement Bottom Relative Scale"
                ],
                "Align Leg X rot": True,
            },
        )

    elif kwargs["Leg Style"] == "straight":
        leg = nw.new_node(
            nodegroup_generate_leg_straight(**kwargs).name,
            input_kwargs={
                "Leg Height": kwargs["Leg Height"],
                "Leg Diameter": kwargs["Leg Diameter"],
                "Resolution": 32,
                "N-gon": kwargs["Leg NGon"],
                "Fillet Ratio": 0.1,
            },
        )

        strecher = nw.new_node(
            nodegroup_strecher().name,
            input_kwargs={"Profile Width": kwargs["Leg Diameter"] * 0.5},
        )

        leg = nw.new_node(
            nodegroup_create_legs_and_strechers().name,
            input_kwargs={
                "Anchors": createanchors,
                "Keep Legs": True,
                "Leg Instance": leg,
                "Table Height": kwargs["Top Height"],
                "Strecher Instance": strecher,
                "Strecher Index Increment": kwargs["Strecher Increament"],
                "Strecher Relative Position": kwargs["Strecher Relative Pos"],
                "Leg Bottom Relative Scale": kwargs[
                    "Leg Placement Bottom Relative Scale"
                ],
                "Align Leg X rot": True,
            },
        )

    elif kwargs["Leg Style"] == "square":
        leg = nw.new_node(
            nodegroup_generate_leg_square(**kwargs).name,
            input_kwargs={
                "Height": kwargs["Leg Height"],
                "Width": 0.707
                * kwargs["Leg Placement Top Relative Scale"]
                * kwargs["Top Profile Width"]
                * kwargs["Top Profile Aspect Ratio"],
                "Has Bottom Connector": (kwargs["Strecher Increament"] > 0),
                "Profile Width": kwargs["Leg Diameter"],
            },
        )

        leg = nw.new_node(
            nodegroup_create_legs_and_strechers().name,
            input_kwargs={
                "Anchors": createanchors,
                "Keep Legs": True,
                "Leg Instance": leg,
                "Table Height": kwargs["Top Height"],
                "Leg Bottom Relative Scale": kwargs[
                    "Leg Placement Bottom Relative Scale"
                ],
                "Align Leg X rot": True,
            },
        )

    else:
        raise NotImplementedError

    leg = nw.new_node(
        Nodes.SetMaterial,
        input_kwargs={"Geometry": leg, "Material": kwargs["LegMaterial"]},
    )

    group_output = nw.new_node(
        Nodes.GroupOutput,
        input_kwargs={"Geometry": leg},
        attrs={"is_active_output": True},
    )


def geometry_assemble_table(nw: NodeWrangler, **kwargs):
    # Code generated using version 2.6.4 of the node_transpiler

    generatetabletop = nw.new_node(
        nodegroup_generate_table_top().name,
        input_kwargs={
            "Thickness": kwargs["Top Thickness"],
            "N-gon": kwargs["Top Profile N-gon"],
            "Profile Width": kwargs["Top Profile Width"],
            "Aspect Ratio": kwargs["Top Profile Aspect Ratio"],
            "Fillet Ratio": kwargs["Top Profile Fillet Ratio"],
            "Fillet Radius Vertical": kwargs["Top Vertical Fillet Ratio"],
        },
    )

    tabletop_instance = nw.new_node(
        Nodes.Transform,
        input_kwargs={
            "Geometry": generatetabletop,
            "Translation": (0.0000, 0.0000, kwargs["Top Height"]),
        },
    )

    tabletop_instance = nw.new_node(
        Nodes.SetMaterial,
        input_kwargs={"Geometry": tabletop_instance, "Material": kwargs["TopMaterial"]},
    )

    legs = nw.new_node(geometry_create_legs(**kwargs).name)

    join_geometry = nw.new_node(
        Nodes.JoinGeometry, input_kwargs={"Geometry": [tabletop_instance, legs]}
    )

    group_output = nw.new_node(
        Nodes.GroupOutput,
        input_kwargs={"Geometry": join_geometry},
        attrs={"is_active_output": True},
    )


class TableDiningFactory(AssetFactory):
    def __init__(
        self, factory_seed, coarse=False, dimensions=None, style_preset=None
    ):
        super(TableDiningFactory, self).__init__(factory_seed, coarse=coarse)

        self.dimensions = dimensions
        self.style_preset = style_preset or "random"

        with FixedSeed(factory_seed):
            self.params = self.sample_parameters(dimensions)

            # self.clothes_scatter = ClothesCover(factory_fn=blanket.BlanketFactory, width=log_uniform(.8, 1.2),
            #                                     size=uniform(.8, 1.2)) if uniform() < .3 else NoApply()
            self.clothes_scatter = NoApply()
            self.material_params, self.scratch, self.edge_wear = (
                self.get_material_params()
            )

        self.params.update(self.material_params)
        self.apply_style_preset()

    def apply_style_preset(self):
        if self.style_preset == "random":
            return

        if self.style_preset != "simple_dining":
            raise ValueError(
                f"Unknown TableDiningFactory style preset: {self.style_preset}"
            )

        x, y, z = self.get_dimensions()
        top_thickness = 0.04
        self.params.update(
            {
                "Top Profile N-gon": 4,
                "Top Profile Width": 1.414 * x,
                "Top Profile Aspect Ratio": y / x,
                "Top Profile Fillet Ratio": 0.0,
                "Top Thickness": top_thickness,
                "Top Vertical Fillet Ratio": 0.06,
                "Height": z,
                "Top Height": z - top_thickness,
                "Leg Number": 4,
                "Leg Style": "straight",
                "Leg NGon": 4,
                "Leg Placement Top Relative Scale": 0.88,
                "Leg Placement Bottom Relative Scale": 1.0,
                "Leg Height": 1.0,
                "Leg Diameter": 0.045,
                "Leg Curve Control Points": None,
                "Strecher Relative Pos": 0.32,
                "Strecher Increament": 0,
            }
        )

    def get_dimensions(self):
        if self.dimensions is not None:
            return self.dimensions

        x = self.params["Top Profile Width"] / 1.414
        y = x * self.params["Top Profile Aspect Ratio"]
        z = self.params["Height"]
        return x, y, z

    def get_material_params(self):
        params = {
            "TopMaterial": weighted_sample(material_assignments.table_top)(),
            "LegMaterial": weighted_sample(material_assignments.tableware)(),
        }
        wrapped_params = {k: v() for k, v in params.items()}

        scratch_prob, edge_wear_prob = material_assignments.wear_tear_prob
        scratch, edge_wear = material_assignments.wear_tear
        scratch = None if uniform() > scratch_prob else scratch()
        edge_wear = None if uniform() > edge_wear_prob else edge_wear()

        return wrapped_params, scratch, edge_wear

    @staticmethod
    def sample_parameters(dimensions):
        if dimensions is None:
            width = uniform(0.91, 1.16)

            if uniform() < 0.7:
                # oblong
                length = uniform(1.4, 2.8)
            else:
                # approx square
                length = width * normal(1, 0.1)

            dimensions = (length, width, uniform(0.65, 0.85))

        # all in meters
        x, y, z = dimensions

        NGon = 4

        leg_style = choice(["straight", "single_stand", "square"], p=[0.5, 0.1, 0.4])
        # leg_style = choice(['straight'])

        if leg_style == "single_stand":
            leg_number = 2
            leg_diameter = uniform(0.22 * x, 0.28 * x)

            leg_curve_ctrl_pts = [
                (0.0, uniform(0.1, 0.2)),
                (0.5, uniform(0.1, 0.2)),
                (0.9, uniform(0.2, 0.3)),
                (1.0, 1.0),
            ]

            top_scale = uniform(0.6, 0.7)
            bottom_scale = 1.0

        elif leg_style == "square":
            leg_number = 2
            leg_diameter = uniform(0.07, 0.10)

            leg_curve_ctrl_pts = None

            top_scale = 0.8
            bottom_scale = 1.0

        elif leg_style == "straight":
            leg_diameter = uniform(0.05, 0.07)

            leg_number = 4

            leg_curve_ctrl_pts = [
                (0.0, 1.0),
                (0.4, uniform(0.85, 0.95)),
                (1.0, uniform(0.4, 0.6)),
            ]

            top_scale = 0.8
            bottom_scale = uniform(1.0, 1.2)

        else:
            raise NotImplementedError

        top_thickness = uniform(0.03, 0.06)

        parameters = {
            "Top Profile N-gon": NGon,
            "Top Profile Width": 1.414 * x,
            "Top Profile Aspect Ratio": y / x,
            "Top Profile Fillet Ratio": uniform(0.0, 0.02),
            "Top Thickness": top_thickness,
            "Top Vertical Fillet Ratio": uniform(0.1, 0.3),
            # 'Top Material': choice(['marble', 'tiled_wood', 'metal', 'fabric'], p=[.3, .3, .2, .2]),
            "Height": z,
            "Top Height": z - top_thickness,
            "Leg Number": leg_number,
            "Leg Style": leg_style,
            "Leg NGon": 4,
            "Leg Placement Top Relative Scale": top_scale,
            "Leg Placement Bottom Relative Scale": bottom_scale,
            "Leg Height": 1.0,
            "Leg Diameter": leg_diameter,
            "Leg Curve Control Points": leg_curve_ctrl_pts,
            # 'Leg Material': choice(['metal', 'wood', 'glass', 'plastic']),
            "Strecher Relative Pos": uniform(0.2, 0.6),
            "Strecher Increament": choice([0, 1, 2]),
        }

        return parameters

    def create_asset(self, **params):
        if self.style_preset == "simple_dining":
            return self.create_simple_dining_asset()

        bpy.ops.mesh.primitive_plane_add(
            size=2,
            enter_editmode=False,
            align="WORLD",
            location=(0, 0, 0),
            scale=(1, 1, 1),
        )
        obj = bpy.context.active_object

        # surface.add_geomod(obj, geometry_assemble_table, apply=False, input_kwargs=self.params)
        surface.add_geomod(
            obj, geometry_assemble_table, apply=True, input_kwargs=self.params
        )
        tagging.tag_system.relabel_obj(obj)
        assert tagging.tagged_face_mask(obj, {t.Subpart.SupportSurface}).sum() != 0

        return obj

    def create_simple_dining_asset(self):
        x, y, z = self.get_dimensions()
        top_thickness = self.params["Top Thickness"]
        leg_width = self.params["Leg Diameter"]
        apron_height = min(0.08, max(0.045, top_thickness * 1.4))
        inset_x = max(leg_width * 0.85, x * 0.06)
        inset_y = max(leg_width * 0.85, y * 0.08)

        top = new_bbox(
            -x / 2,
            x / 2,
            -y / 2,
            y / 2,
            z - top_thickness,
            z,
        )
        top.data.materials.append(self.params["TopMaterial"])

        parts = [top]
        leg_xs = [
            -x / 2 + inset_x + leg_width / 2,
            x / 2 - inset_x - leg_width / 2,
        ]
        leg_ys = [
            -y / 2 + inset_y + leg_width / 2,
            y / 2 - inset_y - leg_width / 2,
        ]
        for lx in leg_xs:
            for ly in leg_ys:
                leg = new_bbox(
                    lx - leg_width / 2,
                    lx + leg_width / 2,
                    ly - leg_width / 2,
                    ly + leg_width / 2,
                    0,
                    z - top_thickness,
                )
                leg.data.materials.append(self.params["LegMaterial"])
                parts.append(leg)

        apron_z0 = z - top_thickness - apron_height
        apron_z1 = z - top_thickness
        rail_t = leg_width * 0.78
        apron_specs = [
            (
                -x / 2 + inset_x,
                x / 2 - inset_x,
                -y / 2 + inset_y - rail_t / 2,
                -y / 2 + inset_y + rail_t / 2,
            ),
            (
                -x / 2 + inset_x,
                x / 2 - inset_x,
                y / 2 - inset_y - rail_t / 2,
                y / 2 - inset_y + rail_t / 2,
            ),
            (
                -x / 2 + inset_x - rail_t / 2,
                -x / 2 + inset_x + rail_t / 2,
                -y / 2 + inset_y,
                y / 2 - inset_y,
            ),
            (
                x / 2 - inset_x - rail_t / 2,
                x / 2 - inset_x + rail_t / 2,
                -y / 2 + inset_y,
                y / 2 - inset_y,
            ),
        ]
        for x0, x1, y0, y1 in apron_specs:
            apron = new_bbox(x0, x1, y0, y1, apron_z0, apron_z1)
            apron.data.materials.append(self.params["LegMaterial"])
            parts.append(apron)

        obj = join_objects(parts)
        butil.modify_mesh(
            obj, "BEVEL", width=min(0.006, top_thickness * 0.18), segments=3
        )

        support_mask = (read_normal(obj)[:, -1] > 0.95) & (
            read_center(obj)[:, -1] > z - top_thickness * 0.6
        )
        tagging.tag_object(obj, name=t.Subpart.SupportSurface, mask=support_mask)
        assert tagging.tagged_face_mask(obj, {t.Subpart.SupportSurface}).sum() != 0
        return obj

    def finalize_assets(self, assets):
        pass
        # if self.scratch:
        #     self.scratch.apply(assets)
        # if self.edge_wear:
        #     self.edge_wear.apply(assets)

    # def finalize_assets(self, assets):
    #    self.clothes_scatter.apply(assets)


class SideTableFactory(TableDiningFactory):
    def __init__(self, factory_seed, coarse=False, dimensions=None):
        if dimensions is None:
            w = 0.55 * normal(1, 0.05)
            h = 0.95 * w * normal(1, 0.05)
            dimensions = (w, w, h)
        super().__init__(factory_seed, coarse=coarse, dimensions=dimensions)


class CoffeeTableFactory(TableDiningFactory):
    def __init__(self, factory_seed, coarse=False, dimensions=None):
        if dimensions is None:
            dimensions = (uniform(1, 1.5), uniform(0.6, 0.9), uniform(0.4, 0.5))
        super().__init__(factory_seed, coarse=coarse, dimensions=dimensions)
