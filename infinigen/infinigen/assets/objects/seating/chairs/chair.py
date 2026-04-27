# Copyright (C) 2024, Princeton University.
# This source code is licensed under the BSD 3-Clause license found in the LICENSE file in the root directory of this source tree.

# Authors: Lingjie Mei
import bpy
import numpy as np
from mathutils import Vector
from numpy.random import uniform

from infinigen.assets.composition import material_assignments
from infinigen.assets.utils.decorate import (
    read_co,
    read_edge_center,
    read_edge_direction,
    remove_edges,
    remove_vertices,
    select_edges,
    solidify,
    subsurf,
    write_attribute,
    write_co,
)
from infinigen.assets.utils.draw import align_bezier, bezier_curve
from infinigen.assets.utils.nodegroup import geo_radius
from infinigen.assets.utils.object import join_objects, new_bbox
from infinigen.assets.objects.seating.chairs.dining_slat_sdf import (
    create_sdf_dining_slat_asset,
)
from infinigen.core import surface
from infinigen.core.placement.factory import AssetFactory
from infinigen.core.surface import NoApply
from infinigen.core.util import blender as butil
from infinigen.core.util.blender import deep_clone_obj
from infinigen.core.util.math import FixedSeed
from infinigen.core.util.random import log_uniform, weighted_sample
from infinigen.core.util.random import random_general as rg


class ChairFactory(AssetFactory):
    back_types = (
        "weighted_choice",
        (1, "whole"),
        (1, "partial"),
        (1, "horizontal-bar"),
        (1, "vertical-bar"),
    )

    def __init__(self, factory_seed, coarse=False, style_preset=None):
        super().__init__(factory_seed, coarse)
        self.style_preset = style_preset or "random"
        with FixedSeed(self.factory_seed):
            self.width = uniform(0.4, 0.5)
            self.size = uniform(0.38, 0.45)
            self.thickness = uniform(0.04, 0.08)
            self.bevel_width = self.thickness * (0.1 if uniform() < 0.4 else 0.5)
            self.seat_back = uniform(0.7, 1.0) if uniform() < 0.75 else 1.0
            self.seat_mid = uniform(0.7, 0.8)
            self.seat_mid_x = uniform(
                self.seat_back + self.seat_mid * (1 - self.seat_back), 1
            )
            self.seat_mid_z = uniform(0, 0.5)
            self.seat_front = uniform(1.0, 1.2)
            self.is_seat_round = uniform() < 0.6
            self.is_seat_subsurf = uniform() < 0.5

            self.leg_thickness = uniform(0.04, 0.06)
            self.limb_profile = uniform(1.5, 2.5)
            self.limb_segments = 32
            self.leg_height = uniform(0.45, 0.5)
            self.back_height = uniform(0.4, 0.5)
            self.is_leg_round = uniform() < 0.5
            self.leg_type = np.random.choice(
                ["vertical", "straight", "up-curved", "down-curved"]
            )

            self.leg_x_offset = 0
            self.leg_y_offset = 0, 0
            self.back_x_offset = 0
            self.back_y_offset = 0

            self.has_leg_x_bar = uniform() < 0.6
            self.has_leg_y_bar = uniform() < 0.6
            self.leg_offset_bar = uniform(0.2, 0.4), uniform(0.6, 0.8)

            self.has_arm = uniform() < 0.7
            self.arm_thickness = uniform(0.04, 0.06)
            self.arm_height = self.arm_thickness * uniform(0.6, 1)
            self.arm_y = uniform(0.8, 1) * self.size
            self.arm_z = uniform(0.3, 0.6) * self.back_height
            self.arm_mid = np.array(
                [uniform(-0.03, 0.03), uniform(-0.03, 0.09), uniform(-0.09, 0.03)]
            )
            self.arm_profile = log_uniform(0.1, 3, 2)

            self.back_thickness = uniform(0.04, 0.05)
            self.back_type = rg(self.back_types)
            self.back_profile = [(0, 1)]
            self.back_bridge_cuts = 64
            self.back_vertical_cuts = np.random.randint(1, 4)
            self.back_partial_scale = uniform(1, 1.4)

            limb_surface_gen_class = weighted_sample(material_assignments.furniture_leg)
            self.limb_surface_material_gen = limb_surface_gen_class()
            self.limb_surface = self.limb_surface_material_gen()

            surface_gen_class = weighted_sample(
                material_assignments.furniture_hard_surface
            )
            self.surface_material_gen = surface_gen_class()
            self.surface = self.surface_material_gen()

            if uniform() < 0.3:
                self.panel_surface = self.surface
            else:
                self.panel_surface = weighted_sample(
                    material_assignments.furniture_hard_surface
                )()()

            scratch_prob, edge_wear_prob = material_assignments.wear_tear_prob
            scratch, edge_wear = material_assignments.wear_tear
            self.scratch = None if uniform() > scratch_prob else scratch()
            self.edge_wear = None if uniform() > edge_wear_prob else edge_wear()

            # from infinigen.assets.clothes import blanket
            # from infinigen.assets.scatters.clothes import ClothesCover
            # self.clothes_scatter = ClothesCover(factory_fn=blanket.BlanketFactory, width=log_uniform(.8, 1.2),
            #                                    size=uniform(.8, 1.2)) if uniform() < .3 else NoApply()
            self.clothes_scatter = NoApply()
            self.post_init()
            self.apply_style_preset()

    def apply_style_preset(self):
        if self.style_preset == "random":
            return

        if self.style_preset != "dining_slat":
            raise ValueError(f"Unknown ChairFactory style preset: {self.style_preset}")

        # A narrow dining-chair family closer to simple painted wooden slat backs.
        with FixedSeed(self.factory_seed):
            self.width = uniform(0.42, 0.46)
            self.size = uniform(0.40, 0.44)
            self.thickness = uniform(0.034, 0.044)
            self.bevel_width = self.thickness * 0.16

            self.seat_back = uniform(0.82, 0.9)
            self.seat_mid = uniform(0.76, 0.82)
            self.seat_mid_x = uniform(0.88, 0.96)
            self.seat_mid_z = uniform(0.04, 0.09)
            self.seat_front = uniform(1.0, 1.08)
            self.is_seat_round = True
            self.is_seat_subsurf = True

            self.leg_thickness = uniform(0.026, 0.033)
            self.limb_profile = uniform(1.2, 1.55)
            self.limb_segments = 24
            self.dining_slat_spindle_count = 6
            self.dining_slat_spindle_samples = 22
            self.leg_height = uniform(0.44, 0.47)
            self.back_height = uniform(0.44, 0.50)
            self.is_leg_round = False
            self.leg_type = "straight"

            self.leg_x_offset = uniform(0.006, 0.014)
            self.leg_y_offset = (uniform(0.008, 0.018), uniform(0.01, 0.026))
            self.back_x_offset = uniform(-0.006, 0.006)
            self.back_y_offset = uniform(0.012, 0.03)

            self.has_leg_x_bar = True
            self.has_leg_y_bar = True
            self.leg_offset_bar = (0.26, 0.42)

            self.has_arm = False
            self.arm_thickness = 0.0
            self.arm_height = 0.0

            self.back_thickness = uniform(0.018, 0.023)
            self.back_type = "vertical-bar"
            self.back_profile = ((uniform(0.70, 0.78), 1),)
            self.back_bridge_cuts = 28
            self.back_vertical_cuts = np.random.randint(4, 6)
            self.back_partial_scale = 1.0

            # Keep the chair visually coherent so it can be painted/recolored as one piece.
            self.panel_surface = self.surface
            self.limb_surface = self.surface
            self.scratch = None
            self.edge_wear = None

    def post_init(self):
        with FixedSeed(self.factory_seed):
            if self.leg_type == "vertical":
                self.leg_x_offset = 0
                self.leg_y_offset = 0, 0
                self.back_x_offset = 0
                self.back_y_offset = 0
            else:
                self.leg_x_offset = self.width * uniform(0.05, 0.2)
                self.leg_y_offset = self.size * uniform(0.05, 0.2, 2)
                self.back_x_offset = self.width * uniform(-0.1, 0.15)
                self.back_y_offset = self.size * uniform(0.1, 0.25)

            match self.back_type:
                case "partial":
                    self.back_profile = ((uniform(0.4, 0.8), 1),)
                case "horizontal-bar":
                    n_cuts = np.random.randint(2, 4)
                    locs = uniform(1, 2, n_cuts).cumsum()
                    locs = locs / locs[-1]
                    ratio = uniform(0.5, 0.75)
                    locs = np.array(
                        [
                            (p + ratio * (l - p), l)
                            for p, l in zip([0, *locs[:-1]], locs)
                        ]
                    )
                    lowest = uniform(0, 0.4)
                    self.back_profile = locs * (1 - lowest) + lowest
                case "vertical-bar":
                    self.back_profile = ((uniform(0.8, 0.9), 1),)
                case _:
                    self.back_profile = [(0, 1)]

    def create_placeholder(self, **kwargs) -> bpy.types.Object:
        obj = new_bbox(
            -self.width / 2 - max(self.leg_x_offset, self.back_x_offset),
            self.width / 2 + max(self.leg_x_offset, self.back_x_offset),
            -self.size - self.leg_y_offset[1] - self.leg_thickness * 0.5,
            max(self.leg_y_offset[0], self.back_y_offset),
            -self.leg_height,
            self.back_height * 1.2,
        )
        obj.rotation_euler.z += np.pi / 2
        butil.apply_transform(obj)
        return obj

    def create_asset(self, **params) -> bpy.types.Object:
        if self.style_preset == "dining_slat":
            return self.create_dining_slat_asset()

        obj = self.make_seat()
        legs = self.make_legs()
        backs = self.make_backs()

        parts = [obj] + legs + backs
        parts.extend(self.make_leg_decors(legs))
        if self.has_arm:
            parts.extend(self.make_arms(obj, backs))
        parts.extend(self.make_back_decors(backs))

        for obj in legs:
            self.solidify(obj, 2)
        for obj in backs:
            self.solidify(obj, 2, self.back_thickness)

        obj = join_objects(parts)
        obj.rotation_euler.z += np.pi / 2
        butil.apply_transform(obj)
        self.normalize_to_placeholder_bbox(obj)

        with FixedSeed(self.factory_seed):
            # TODO: wasteful to create unique materials for each individual asset
            # self.surface.apply(obj)

            # self.panel_surface.apply(obj, selection="panel")
            # self.limb_surface.apply(obj, selection="limb")
            surface.assign_material(obj, self.surface)
            surface.assign_material(obj, self.panel_surface, selection="panel")
            surface.assign_material(obj, self.limb_surface, selection="limb")

        return obj

    def create_dining_slat_asset(self) -> bpy.types.Object:
        return create_sdf_dining_slat_asset(self)

    def create_legacy_dining_slat_asset(self) -> bpy.types.Object:
        verts = []
        faces = []
        face_kinds = []
        ring_segments = max(18, int(self.limb_segments))

        def add_face(indices, kind):
            faces.append(tuple(indices))
            face_kinds.append(kind)

        def add_vertex(v):
            verts.append(Vector(v))
            return len(verts) - 1

        def bezier_point(points, t):
            pts = [Vector(p) for p in points]
            while len(pts) > 1:
                pts = [pts[i].lerp(pts[i + 1], t) for i in range(len(pts) - 1)]
            return pts[0]

        def bezier_tangent(points, t):
            eps = 1e-3
            a = bezier_point(points, max(0, t - eps))
            b = bezier_point(points, min(1, t + eps))
            tangent = b - a
            if tangent.length < 1e-6:
                tangent = Vector((0, 0, 1))
            return tangent.normalized()

        def stable_frame(tangent, normal_hint=None):
            if normal_hint is not None:
                normal = Vector(normal_hint)
                normal -= tangent * normal.dot(tangent)
                if normal.length > 1e-6:
                    normal.normalize()
                    binormal = tangent.cross(normal).normalized()
                    return normal, binormal
            ref = Vector((0, 0, 1))
            if abs(tangent.dot(ref)) > 0.90:
                ref = Vector((0, 1, 0))
            normal = ref.cross(tangent).normalized()
            binormal = tangent.cross(normal).normalized()
            return normal, binormal

        def radius_at(radii, t):
            if np.isscalar(radii):
                return float(radii)
            return float(radii[0] * (1 - t) + radii[-1] * t)

        def add_tube(points, radii, kind="limb", samples=8, normal_hint=None):
            first_ring = len(verts)
            for s in range(samples + 1):
                t = s / samples
                center = bezier_point(points, t)
                tangent = bezier_tangent(points, t)
                normal, binormal = stable_frame(tangent, normal_hint)
                radius = radius_at(radii, t)
                for k in range(ring_segments):
                    angle = 2 * np.pi * k / ring_segments
                    add_vertex(
                        center
                        + normal * np.cos(angle) * radius
                        + binormal * np.sin(angle) * radius
                    )
            for s in range(samples):
                base = first_ring + s * ring_segments
                next_base = first_ring + (s + 1) * ring_segments
                for k in range(ring_segments):
                    add_face(
                        [
                            base + k,
                            base + (k + 1) % ring_segments,
                            next_base + (k + 1) % ring_segments,
                            next_base + k,
                        ],
                        kind,
                    )
            start_center = add_vertex(bezier_point(points, 0))
            end_center = add_vertex(bezier_point(points, 1))
            end_base = first_ring + samples * ring_segments
            for k in range(ring_segments):
                add_face([start_center, first_ring + (k + 1) % ring_segments, first_ring + k], kind)
                add_face([end_center, end_base + k, end_base + (k + 1) % ring_segments], kind)

        def rounded_rect_loop(width, depth, radius, count_per_corner=8):
            hx = width / 2 - radius
            hy = depth / 2 - radius
            centers = [
                Vector((hx, -hy, 0)),
                Vector((hx, hy, 0)),
                Vector((-hx, hy, 0)),
                Vector((-hx, -hy, 0)),
            ]
            angles = [
                (-np.pi / 2, 0),
                (0, np.pi / 2),
                (np.pi / 2, np.pi),
                (np.pi, 3 * np.pi / 2),
            ]
            loop = []
            for center, (a0, a1) in zip(centers, angles):
                for i in range(count_per_corner):
                    a = a0 + (a1 - a0) * i / count_per_corner
                    loop.append(center + Vector((np.cos(a) * radius, np.sin(a) * radius, 0)))
            return loop

        def add_seat_plate(width, depth, thickness, center_y):
            loop = rounded_rect_loop(width, depth, min(width, depth) * 0.075)
            top_center = add_vertex((0, center_y - depth * 0.02, 0.0015))
            bottom_center = add_vertex((0, center_y, -thickness))
            top = []
            bottom = []
            for p in loop:
                x = p.x
                y = p.y + center_y
                edge_crown = 0.0006 * (x / (width / 2)) ** 2
                top.append(add_vertex((x, y, edge_crown)))
                bottom.append(add_vertex((x, y, -thickness)))
            n = len(loop)
            for i in range(n):
                add_face([top_center, top[i], top[(i + 1) % n]], "seat")
                add_face([bottom_center, bottom[(i + 1) % n], bottom[i]], "seat")
                add_face([top[i], bottom[i], bottom[(i + 1) % n], top[(i + 1) % n]], "seat")

        def add_knob(center, radius):
            top = add_vertex(Vector(center) + Vector((0, 0, radius)))
            rings = []
            for j in range(1, 7):
                theta = np.pi * j / 7
                z = np.cos(theta) * radius
                r = np.sin(theta) * radius
                ring = []
                for k in range(ring_segments):
                    a = 2 * np.pi * k / ring_segments
                    ring.append(add_vertex(Vector(center) + Vector((np.cos(a) * r, np.sin(a) * r, z))))
                rings.append(ring)
            bottom = add_vertex(Vector(center) - Vector((0, 0, radius * 0.82)))
            for k in range(ring_segments):
                add_face([top, rings[0][k], rings[0][(k + 1) % ring_segments]], "limb")
            for a, b in zip(rings[:-1], rings[1:]):
                for k in range(ring_segments):
                    add_face([a[k], a[(k + 1) % ring_segments], b[(k + 1) % ring_segments], b[k]], "limb")
            for k in range(ring_segments):
                add_face([bottom, rings[-1][(k + 1) % ring_segments], rings[-1][k]], "limb")

        seat_width = self.width * 1.05
        seat_depth = self.size * 1.05
        seat_center_y = -self.size * 0.48
        seat_front_y = seat_center_y - seat_depth / 2
        seat_back_y = seat_center_y + seat_depth / 2
        foot_z = -self.leg_height
        seat_bottom_z = -self.thickness
        post_top_z = self.back_height
        back_lean = self.size * 0.15

        def back_plane_y(z):
            return seat_back_y - self.size * 0.03 + back_lean * (z / max(post_top_z, 1e-6))

        half_front = seat_width * 0.43
        half_rear = seat_width * 0.37
        leg_splay_x = self.width * 0.06
        leg_splay_y = self.size * 0.07
        leg_r = self.leg_thickness * 0.46
        post_r = self.leg_thickness * 0.48
        apron_r = self.leg_thickness * 0.34
        stretcher_r = self.leg_thickness * 0.29
        lower_rail_r = self.back_thickness * 0.58
        crest_r = self.back_thickness * 0.92
        spindle_r = self.back_thickness * 0.36

        add_seat_plate(seat_width, seat_depth, self.thickness, seat_center_y)

        front_top = {
            -1: Vector((-half_front, seat_front_y + self.size * 0.07, seat_bottom_z * 0.65)),
            1: Vector((half_front, seat_front_y + self.size * 0.07, seat_bottom_z * 0.65)),
        }
        front_foot = {
            -1: Vector((-half_front - leg_splay_x, seat_front_y - leg_splay_y, foot_z)),
            1: Vector((half_front + leg_splay_x, seat_front_y - leg_splay_y, foot_z)),
        }
        rear_post = {}
        rear_post_paths = {}
        for side in (-1, 1):
            x = side * half_rear
            rear_post[side] = {
                "foot": Vector((x + side * leg_splay_x * 0.55, back_plane_y(0) + self.size * 0.04, foot_z)),
                "seat": Vector((x, back_plane_y(0), seat_bottom_z * 0.54)),
                "mid": Vector((x * 0.98, back_plane_y(post_top_z * 0.52), post_top_z * 0.52)),
                "top": Vector((x * 0.92, back_plane_y(post_top_z), post_top_z)),
            }
            rear_post_paths[side] = [
                rear_post[side]["foot"],
                rear_post[side]["seat"],
                rear_post[side]["mid"],
                rear_post[side]["top"],
            ]

        def rear_post_at(side, z):
            samples = [bezier_point(rear_post_paths[side], i / 64) for i in range(65)]
            samples = sorted(samples, key=lambda p: p.z)
            for a, b in zip(samples[:-1], samples[1:]):
                if a.z <= z <= b.z:
                    denom = max(b.z - a.z, 1e-6)
                    return a.lerp(b, (z - a.z) / denom)
            return samples[0] if z < samples[0].z else samples[-1]

        for side in (-1, 1):
            add_tube(
                [front_foot[side], front_foot[side].lerp(front_top[side], 0.58), front_top[side]],
                (leg_r * 0.82, leg_r * 1.04),
                samples=8,
                normal_hint=(0, 1, 0),
            )
            add_tube(
                rear_post_paths[side],
                (post_r * 0.88, post_r * 1.02),
                samples=13,
                normal_hint=(0, 1, 0),
            )

        rail_pairs = [
            (front_top[-1], front_top[1], apron_r, 6),
            (rear_post[-1]["seat"], rear_post[1]["seat"], apron_r, 6),
            (front_top[-1], rear_post[-1]["seat"], apron_r * 0.92, 7),
            (front_top[1], rear_post[1]["seat"], apron_r * 0.92, 7),
            (
                Vector((front_foot[-1].x, front_foot[-1].y + self.size * 0.025, foot_z * 0.55)),
                Vector((front_foot[1].x, front_foot[1].y + self.size * 0.025, foot_z * 0.55)),
                stretcher_r,
                6,
            ),
            (
                Vector((rear_post[-1]["foot"].x, rear_post[-1]["foot"].y, foot_z * 0.48)),
                Vector((rear_post[1]["foot"].x, rear_post[1]["foot"].y, foot_z * 0.48)),
                stretcher_r,
                6,
            ),
            (
                Vector((front_foot[-1].x, front_foot[-1].y, foot_z * 0.55)),
                Vector((rear_post[-1]["foot"].x, rear_post[-1]["foot"].y, foot_z * 0.45)),
                stretcher_r * 0.9,
                8,
            ),
            (
                Vector((front_foot[1].x, front_foot[1].y, foot_z * 0.55)),
                Vector((rear_post[1]["foot"].x, rear_post[1]["foot"].y, foot_z * 0.45)),
                stretcher_r * 0.9,
                8,
            ),
        ]
        for a, b, radius, samples in rail_pairs:
            add_tube([a, b], radius, samples=samples, normal_hint=(0, 0, 1))

        lower_z = post_top_z * 0.34
        crest_side_z = post_top_z * 0.74
        crest_center_z = post_top_z * 0.88
        lower_l = rear_post_at(-1, lower_z)
        lower_r = rear_post_at(1, lower_z)
        add_tube([lower_l, lower_r], lower_rail_r, "panel", samples=7, normal_hint=(0, 0, 1))
        crest_left = rear_post_at(-1, crest_side_z)
        crest_mid = Vector((0, back_plane_y(crest_center_z) + self.size * 0.018, crest_center_z))
        crest_right = rear_post_at(1, crest_side_z)
        add_tube([crest_left, crest_mid, crest_right], crest_r, "panel", samples=14, normal_hint=(0, 1, 0))

        spindle_count = getattr(self, "dining_slat_spindle_count", 5)
        spindle_samples = getattr(self, "dining_slat_spindle_samples", 10)
        for i, x in enumerate(np.linspace(lower_l.x * 0.62, lower_r.x * 0.62, spindle_count)):
            rel = abs((i - (spindle_count - 1) / 2) / ((spindle_count - 1) / 2))
            top_z = crest_side_z + (1 - rel * 0.78) * (crest_center_z - crest_side_z) - crest_r * 0.72
            bottom = Vector((x, back_plane_y(lower_z) + self.size * 0.004, lower_z + lower_rail_r * 0.92))
            top = Vector((x * 0.96, back_plane_y(top_z) + self.size * 0.006, top_z))
            mid_low = bottom.lerp(top, 0.36) + Vector((0, self.size * 0.0025, 0))
            mid_high = bottom.lerp(top, 0.70) + Vector((0, self.size * 0.0035, 0))
            add_tube(
                [bottom, mid_low, mid_high, top],
                spindle_r,
                "limb",
                samples=spindle_samples,
                normal_hint=(1, 0, 0),
            )

        for side in (-1, 1):
            add_knob(
                rear_post[side]["top"] + Vector((0, self.size * 0.006, self.back_thickness * 0.52)),
                self.back_thickness * 0.66,
            )

        mesh = bpy.data.meshes.new("DiningSlatIntegratedChairMesh")
        mesh.from_pydata([tuple(v) for v in verts], [], faces)
        mesh.update()
        obj = bpy.data.objects.new("DiningSlat_IntegratedChair", mesh)
        bpy.context.collection.objects.link(obj)
        try:
            panel_attr = obj.data.attributes.new("panel", "BOOLEAN", "FACE")
            limb_attr = obj.data.attributes.new("limb", "BOOLEAN", "FACE")
            for i, kind in enumerate(face_kinds):
                panel_attr.data[i].value = kind in {"panel", "seat"}
                limb_attr.data[i].value = kind == "limb"
        except Exception:
            write_attribute(obj, 1, "limb", "FACE")
        obj.rotation_euler.z += np.pi / 2
        butil.apply_transform(obj)
        self.normalize_to_placeholder_bbox(obj)
        for i, poly in enumerate(obj.data.polygons):
            poly.use_smooth = face_kinds[i] != "seat"
        butil.modify_mesh(obj, "WEIGHTED_NORMAL", keep_sharp=True)

        mat = bpy.data.materials.get("shader_red_lacquered_wood_dining_slat")
        if mat is None:
            mat = bpy.data.materials.new("shader_red_lacquered_wood_dining_slat")
        mat.diffuse_color = (0.64, 0.035, 0.025, 1.0)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        output = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 4
        noise.inputs["Detail"].default_value = 5
        noise.inputs["Roughness"].default_value = 0.42
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.12
        ramp.color_ramp.elements[0].color = (0.58, 0.030, 0.020, 1)
        ramp.color_ramp.elements[1].position = 1.0
        ramp.color_ramp.elements[1].color = (0.74, 0.066, 0.040, 1)
        bump_noise = nodes.new("ShaderNodeTexNoise")
        bump_noise.inputs["Scale"].default_value = 38
        bump_noise.inputs["Detail"].default_value = 5
        bump_noise.inputs["Roughness"].default_value = 0.48
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.0035
        bump.inputs["Distance"].default_value = 0.0025
        links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(bump_noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
        bsdf.inputs["Metallic"].default_value = 0.0
        bsdf.inputs["Roughness"].default_value = 0.32
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = 1.0
        if "Coat Weight" in bsdf.inputs:
            bsdf.inputs["Coat Weight"].default_value = 0.48
        if "Coat Roughness" in bsdf.inputs:
            bsdf.inputs["Coat Roughness"].default_value = 0.22
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.58
        surface.assign_material(obj, mat)
        obj["infinigen_style_preset"] = "dining_slat"
        obj["generated_detail_level"] = "reference_reconstruction"

        return obj

    def normalize_to_placeholder_bbox(self, obj):
        placeholder = self.create_placeholder()
        target_co = np.array(placeholder.bound_box, dtype=np.float32)
        target_min = target_co.min(axis=0)
        target_max = target_co.max(axis=0)
        target_dims = target_max - target_min
        butil.delete(placeholder)

        co = read_co(obj)
        curr_min = co.min(axis=0)
        curr_max = co.max(axis=0)
        curr_dims = curr_max - curr_min
        curr_dims = np.where(curr_dims < 1e-6, 1.0, curr_dims)

        co = (co - curr_min) * (target_dims / curr_dims) + target_min
        write_co(obj, co)
        butil.apply_transform(obj)

    def finalize_assets(self, assets):
        pass
        # if self.scratch:
        #     self.scratch.apply(assets)
        # if self.edge_wear:
        #     self.edge_wear.apply(assets)

    def make_seat(self):
        x_anchors = (
            np.array(
                [
                    0,
                    0.1,
                    1,
                    self.seat_mid_x,
                    self.seat_back,
                    0,
                ]
            )
            * self.width
            / 2
        )
        y_anchors = (
            np.array([-self.seat_front, -self.seat_front, -1, -self.seat_mid, 0, 0])
            * self.size
        )
        z_anchors = np.array([0, 0, 0, self.seat_mid_z, 0, 0]) * self.thickness
        vector_locations = [4] if self.is_seat_round else [2, 4]
        obj = bezier_curve((x_anchors, y_anchors, z_anchors), vector_locations)
        butil.modify_mesh(obj, "MIRROR")
        with butil.ViewportMode(obj, "EDIT"):
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.mesh.fill_grid(use_interp_simple=True)
        butil.modify_mesh(obj, "SOLIDIFY", thickness=self.thickness, offset=0)
        subsurf(obj, 1, not self.is_seat_subsurf)
        butil.modify_mesh(obj, "BEVEL", width=self.bevel_width, segments=8)
        return obj

    def make_legs(self):
        leg_starts = np.array(
            [[-self.seat_back, 0, 0], [-1, -1, 0], [1, -1, 0], [self.seat_back, 0, 0]]
        ) * np.array([[self.width / 2, self.size, 0]])
        leg_ends = leg_starts.copy()
        leg_ends[[0, 1], 0] -= self.leg_x_offset
        leg_ends[[2, 3], 0] += self.leg_x_offset
        leg_ends[[0, 3], 1] += self.leg_y_offset[0]
        leg_ends[[1, 2], 1] -= self.leg_y_offset[1]
        leg_ends[:, -1] = -self.leg_height
        return self.make_limb(leg_ends, leg_starts)

    def make_limb(self, leg_ends, leg_starts):
        limbs = []
        for leg_start, leg_end in zip(leg_starts, leg_ends):
            match self.leg_type:
                case "up-curved":
                    axes = [(0, 0, 1), None]
                    scale = [self.limb_profile, 1]
                case "down-curved":
                    axes = [None, (0, 0, 1)]
                    scale = [1, self.limb_profile]
                case _:
                    axes = None
                    scale = None
            limb = align_bezier(np.stack([leg_start, leg_end], -1), axes, scale)
            limb.location = (
                np.array(
                    [
                        1 if leg_start[0] < 0 else -1,
                        1 if leg_start[1] < -self.size / 2 else -1,
                        0,
                    ]
                )
                * self.leg_thickness
                / 2
            )
            butil.apply_transform(limb, True)
            limbs.append(limb)
        return limbs

    def make_backs(self):
        back_starts = (
            np.array([[-self.seat_back, 0, 0], [self.seat_back, 0, 0]]) * self.width / 2
        )
        back_ends = back_starts.copy()
        back_ends[:, 0] += np.array([self.back_x_offset, -self.back_x_offset])
        back_ends[:, 1] = self.back_y_offset
        back_ends[:, 2] = self.back_height
        return self.make_limb(back_starts, back_ends)

    def make_leg_decors(self, legs):
        decors = []
        if self.has_leg_x_bar:
            z_height = -self.leg_height * uniform(*self.leg_offset_bar)
            locs = []
            for leg in legs:
                co = read_co(leg)
                locs.append(co[np.argmin(np.abs(co[:, -1] - z_height))])
            decors.append(
                self.solidify(bezier_curve(np.stack([locs[0], locs[3]], -1)), 0)
            )
            decors.append(
                self.solidify(bezier_curve(np.stack([locs[1], locs[2]], -1)), 0)
            )
        if self.has_leg_y_bar:
            z_height = -self.leg_height * uniform(*self.leg_offset_bar)
            locs = []
            for leg in legs:
                co = read_co(leg)
                locs.append(co[np.argmin(np.abs(co[:, -1] - z_height))])
            decors.append(
                self.solidify(bezier_curve(np.stack([locs[0], locs[1]], -1)), 1)
            )
            decors.append(
                self.solidify(bezier_curve(np.stack([locs[2], locs[3]], -1)), 1)
            )
        for d in decors:
            write_attribute(d, 1, "limb", "FACE")
        return decors

    def make_back_decors(self, backs, finalize=True):
        obj = join_objects([deep_clone_obj(b) for b in backs])
        x, y, z = read_co(obj).T
        x += np.where(x > 0, self.back_thickness / 2, -self.back_thickness / 2)
        write_co(obj, np.stack([x, y, z], -1))
        smoothness = uniform(0, 1)
        profile_shape_factor = uniform(0, 0.4)
        with butil.ViewportMode(obj, "EDIT"):
            bpy.ops.mesh.select_mode(type="EDGE")
            center = read_edge_center(obj)
            for z_min, z_max in self.back_profile:
                select_edges(
                    obj,
                    (z_min * self.back_height <= center[:, -1])
                    & (center[:, -1] <= z_max * self.back_height),
                )
                bpy.ops.mesh.bridge_edge_loops(
                    number_cuts=self.back_bridge_cuts,
                    interpolation="LINEAR",
                    smoothness=smoothness,
                    profile_shape_factor=profile_shape_factor,
                )
            bpy.ops.mesh.select_loose()
            bpy.ops.mesh.delete()
        butil.modify_mesh(
            obj,
            "SOLIDIFY",
            thickness=np.minimum(self.thickness, self.back_thickness),
            offset=0,
        )
        if finalize:
            butil.modify_mesh(obj, "BEVEL", width=self.bevel_width, segments=8)
        parts = [obj]
        if self.back_type == "vertical-bar":
            other = join_objects([deep_clone_obj(b) for b in backs])
            with butil.ViewportMode(other, "EDIT"):
                bpy.ops.mesh.select_mode(type="EDGE")
                bpy.ops.mesh.select_all(action="SELECT")
                bpy.ops.mesh.bridge_edge_loops(
                    number_cuts=self.back_vertical_cuts,
                    interpolation="LINEAR",
                    smoothness=smoothness,
                    profile_shape_factor=profile_shape_factor,
                )
                bpy.ops.mesh.select_all(action="INVERT")
                bpy.ops.mesh.delete()
                bpy.ops.mesh.select_all(action="SELECT")
                bpy.ops.mesh.delete(type="ONLY_FACE")
            remove_edges(other, np.abs(read_edge_direction(other)[:, -1]) < 0.5)
            remove_vertices(other, lambda x, y, z: z < -self.thickness / 2)
            remove_vertices(
                other,
                lambda x, y, z: z
                > (self.back_profile[0][0] + self.back_profile[0][1])
                * self.back_height
                / 2,
            )
            parts.append(self.solidify(other, 2, self.back_thickness))
        elif self.back_type == "partial":
            co = read_co(obj)
            co[:, 1] *= self.back_partial_scale
            write_co(obj, co)
        for p in parts:
            write_attribute(p, 1, "panel", "FACE")
        return parts

    def make_arms(self, base, backs):
        co = read_co(base)
        end = co[np.argmin(co[:, 0] - (np.abs(co[:, 1] + self.arm_y) < 0.02))]
        end[0] += self.arm_thickness / 4
        end_ = end.copy()
        end_[0] = -end[0]
        arms = []
        co = read_co(backs[0])
        start = co[np.argmin(co[:, 0] - (np.abs(co[:, -1] - self.arm_z) < 0.02))]
        start[0] -= self.arm_thickness / 4
        start_ = start.copy()
        start_[0] = -start[0]
        for start, end in zip([start, start_], [end, end_]):
            mid = np.array(
                [
                    end[0] + self.arm_mid[0] * (-1 if end[0] > 0 else 1),
                    end[1] + self.arm_mid[1],
                    start[2] + self.arm_mid[2],
                ]
            )
            arm = align_bezier(
                np.stack([start, mid, end], -1),
                np.array(
                    [
                        [end[0] - start[0], end[1] - start[1], 0],
                        [0, 1 / np.sqrt(2), 1 / np.sqrt(2)],
                        [0, 0, 1],
                    ]
                ),
                [1, *self.arm_profile, 1],
            )
            if self.is_leg_round:
                surface.add_geomod(
                    arm,
                    geo_radius,
                    apply=True,
                    input_args=[self.arm_thickness / 2, 32],
                    input_kwargs={"to_align_tilt": False},
                )
            else:
                with butil.ViewportMode(arm, "EDIT"):
                    bpy.ops.mesh.select_all(action="SELECT")
                    bpy.ops.mesh.extrude_edges_move(
                        TRANSFORM_OT_translate={
                            "value": (
                                self.arm_thickness
                                if end[0] < 0
                                else -self.arm_thickness,
                                0,
                                0,
                            )
                        }
                    )
                butil.modify_mesh(arm, "SOLIDIFY", thickness=self.arm_height, offset=0)
            write_attribute(arm, 1, "limb", "FACE")
            arms.append(arm)
        return arms

    def solidify(self, obj, axis, thickness=None):
        if thickness is None:
            thickness = self.leg_thickness
        if self.is_leg_round:
            solidify(obj, axis, thickness)
            butil.modify_mesh(obj, "BEVEL", width=self.bevel_width, segments=8)
        else:
            surface.add_geomod(
                obj,
                geo_radius,
                apply=True,
                input_args=[thickness / 2, self.limb_segments],
            )
        write_attribute(obj, 1, "limb", "FACE")
        return obj


class DiningSlatChairFactory(ChairFactory):
    """Reference-reconstruction dining chair with a red slatted back."""

    def __init__(self, factory_seed, coarse=False):
        super().__init__(factory_seed, coarse=coarse, style_preset="dining_slat")
