# Copyright (C) 2024, Princeton University.
# This source code is licensed under the BSD 3-Clause license found in the LICENSE file in the root directory of this source tree.

import math

import bpy
import numpy as np
from mathutils import Vector

from infinigen.core import surface
from infinigen.core.util import blender as butil


def _red_lacquer_material():
    mat = bpy.data.materials.get("shader_red_lacquered_wood_dining_slat_sdf")
    if mat is None:
        mat = bpy.data.materials.new("shader_red_lacquered_wood_dining_slat_sdf")
    mat.diffuse_color = (0.46, 0.020, 0.012, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 16
    noise.inputs["Detail"].default_value = 9
    noise.inputs["Roughness"].default_value = 0.64
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.16
    ramp.color_ramp.elements[0].color = (0.24, 0.007, 0.004, 1)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (0.62, 0.026, 0.014, 1)
    mid = ramp.color_ramp.elements.new(0.58)
    mid.color = (0.40, 0.014, 0.008, 1)
    grain = nodes.new("ShaderNodeTexWave")
    grain.inputs["Scale"].default_value = 31
    grain.inputs["Distortion"].default_value = 14
    grain_ramp = nodes.new("ShaderNodeValToRGB")
    grain_ramp.color_ramp.elements[0].position = 0.35
    grain_ramp.color_ramp.elements[0].color = (0.58, 0.48, 0.42, 1)
    grain_ramp.color_ramp.elements[1].position = 1.0
    grain_ramp.color_ramp.elements[1].color = (0.98, 0.88, 0.76, 1)
    grain_mix = nodes.new("ShaderNodeMixRGB")
    grain_mix.blend_type = "MULTIPLY"
    grain_mix.inputs[0].default_value = 0.22
    bump_noise = nodes.new("ShaderNodeTexNoise")
    bump_noise.inputs["Scale"].default_value = 96
    bump_noise.inputs["Detail"].default_value = 8
    bump_noise.inputs["Roughness"].default_value = 0.58
    bump_mix = nodes.new("ShaderNodeMath")
    bump_mix.operation = "MULTIPLY"
    bump_mix.inputs[1].default_value = 0.38
    bump_add = nodes.new("ShaderNodeMath")
    bump_add.operation = "ADD"
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.0012
    bump.inputs["Distance"].default_value = 0.0011

    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], grain_mix.inputs[1])
    links.new(grain.outputs["Fac"], grain_ramp.inputs["Fac"])
    links.new(grain_ramp.outputs["Color"], grain_mix.inputs[2])
    links.new(grain_mix.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(grain.outputs["Fac"], bump_mix.inputs[0])
    links.new(bump_mix.outputs[0], bump_add.inputs[0])
    links.new(bump_noise.outputs["Fac"], bump_add.inputs[1])
    links.new(bump_add.outputs[0], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.62
    if "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = 1.0
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.14
    if "Coat Roughness" in bsdf.inputs:
        bsdf.inputs["Coat Roughness"].default_value = 0.58
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.34
    mat["reference_material"] = "aged deep red painted wood chair from rgb1.png"
    mat["lookdev_note"] = "dark red-brown lacquer, satin roughness, subtle multiplied grain, reduced plastic clearcoat"
    return mat


def _add_tube(verts, faces, centers, radius=0.01, sides=16):
    pts = [Vector(p) for p in centers]
    clean = []
    for p in pts:
        if not clean or (p - clean[-1]).length > 1e-5:
            clean.append(p)
    pts = clean
    if len(pts) < 2:
        return

    rings = []
    prev_n = None
    for i, center in enumerate(pts):
        if i == 0:
            tangent = (pts[1] - pts[0]).normalized()
        elif i == len(pts) - 1:
            tangent = (pts[-1] - pts[-2]).normalized()
        else:
            tangent = (pts[i + 1] - pts[i - 1]).normalized()

        normal = None
        if prev_n is not None:
            normal = prev_n - tangent * prev_n.dot(tangent)
            if normal.length < 1e-5:
                normal = None
        if normal is None:
            ref = Vector((0, 0, 1))
            if abs(tangent.dot(ref)) > 0.88:
                ref = Vector((1, 0, 0))
            normal = ref.cross(tangent)
            if normal.length < 1e-5:
                normal = Vector((0, 1, 0)).cross(tangent)
        normal.normalize()
        if prev_n is not None and normal.dot(prev_n) < 0:
            normal = -normal
        binormal = tangent.cross(normal).normalized()
        prev_n = normal.copy()

        ring = []
        for j in range(sides):
            angle = 2 * math.pi * j / sides
            p = (
                center
                + normal * (math.cos(angle) * radius)
                + binormal * (math.sin(angle) * radius)
            )
            ring.append(len(verts))
            verts.append((p.x, p.y, p.z))
        rings.append(ring)

    for i in range(len(rings) - 1):
        r0, r1 = rings[i], rings[i + 1]
        for j in range(sides):
            faces.append((r0[j], r0[(j + 1) % sides], r1[(j + 1) % sides], r1[j]))

    c0 = len(verts)
    verts.append(tuple(pts[0]))
    for j in range(sides):
        faces.append((c0, rings[0][j], rings[0][(j + 1) % sides]))
    c1 = len(verts)
    verts.append(tuple(pts[-1]))
    for j in range(sides):
        faces.append((c1, rings[-1][(j + 1) % sides], rings[-1][j]))


def _bezier(points, t):
    pts = [Vector(p) for p in points]
    while len(pts) > 1:
        pts = [pts[i].lerp(pts[i + 1], t) for i in range(len(pts) - 1)]
    return pts[0]


def _crest_point(t):
    return (0.205 * t, -0.218 - 0.020 * (1 - t * t), 0.974 + 0.072 * (1 - t * t))


def _lower_rail_point(t):
    return (0.214 * t, -0.181 - 0.010 * (1 - t * t), 0.612 + 0.014 * (1 - t * t))


def _build_frame_control_mesh(spindle_count=6, spindle_path_samples=22):
    crest = [_crest_point(-1 + 2 * i / 40) for i in range(41)]
    u_back = [
        (-0.213, -0.171, 0.046),
        (-0.208, -0.166, 0.405),
        (-0.203, -0.184, 0.640),
        crest[0],
        *crest[1:-1],
        crest[-1],
        (0.203, -0.184, 0.640),
        (0.208, -0.166, 0.405),
        (0.213, -0.171, 0.046),
    ]

    specs = [(u_back, 0.0154, 22)]
    for sx in (-1, 1):
        specs.append(
            (
                [
                    (0.207 * sx, 0.196, 0.046),
                    (0.195 * sx, 0.177, 0.260),
                    (0.186 * sx, 0.160, 0.414),
                ],
                0.0132,
                20,
            )
        )
    specs += [
        ([(-0.211, 0.160, 0.405), (0.211, 0.160, 0.405)], 0.0110, 18),
        ([(-0.222, -0.166, 0.405), (0.222, -0.166, 0.405)], 0.0110, 18),
        ([(-0.188, 0.160, 0.405), (-0.214, -0.166, 0.405)], 0.0105, 18),
        ([(0.188, 0.160, 0.405), (0.214, -0.166, 0.405)], 0.0105, 18),
        ([(-0.220, 0.188, 0.252), (0.220, 0.188, 0.252)], 0.0094, 16),
        ([(-0.224, -0.172, 0.263), (0.224, -0.172, 0.263)], 0.0094, 16),
        ([(-0.214, 0.187, 0.256), (-0.218, -0.173, 0.266)], 0.0090, 16),
        ([(0.214, 0.187, 0.256), (0.218, -0.173, 0.266)], 0.0090, 16),
        ([_lower_rail_point(-1 + 2 * i / 34) for i in range(35)], 0.0124, 20),
    ]

    for x in np.linspace(-0.132, 0.132, spindle_count):
        tl = max(-1, min(1, x / 0.214))
        tt = max(-1, min(1, (x * 0.92) / 0.205))
        _, ly, lz = _lower_rail_point(tl)
        _, ty, tz = _crest_point(tt)
        bottom = Vector((x, ly, lz - 0.010))
        top = Vector((x * 0.920, ty, tz + 0.006))
        mid_low = bottom.lerp(top, 0.34) + Vector((0, -0.0015, 0.004))
        mid_high = bottom.lerp(top, 0.70) + Vector((0, -0.0025, 0.006))
        path = [
            _bezier([bottom, mid_low, mid_high, top], i / spindle_path_samples)
            for i in range(spindle_path_samples + 1)
        ]
        specs.append((path, 0.0077, 18))

    verts, faces = [], []
    for centers, radius, sides in specs:
        _add_tube(verts, faces, centers, radius, sides)

    mesh = bpy.data.meshes.new("DiningSlatSDFControlFrameMesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)
    mesh.validate(clean_customdata=False)
    return mesh


def _build_frame_mesh(
    material,
    voxel_size=0.0042,
    band_width=4,
    spindle_count=6,
    spindle_path_samples=22,
):
    control_mesh = _build_frame_control_mesh(spindle_count, spindle_path_samples)
    carrier = bpy.data.objects.new("DiningSlatSDFControlFrameCarrier", control_mesh)
    bpy.context.collection.objects.link(carrier)
    # Keep visible until the evaluated mesh is baked; hidden inputs can be skipped
    # by Blender's depsgraph in some MCP/headless sessions.
    carrier.hide_viewport = False
    carrier.hide_render = True

    ng = bpy.data.node_groups.new("GN_DiningSlatChair_MeshToSDFGrid_Rebuild", "GeometryNodeTree")
    try:
        ng.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        ng.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    except Exception:
        pass
    nodes = ng.nodes
    links = ng.links
    group_in = nodes.new("NodeGroupInput")
    group_out = nodes.new("NodeGroupOutput")
    mesh_to_sdf = nodes.new("GeometryNodeMeshToSDFGrid")
    mesh_to_sdf.inputs[1].default_value = voxel_size
    mesh_to_sdf.inputs[2].default_value = band_width
    mean = nodes.new("GeometryNodeSDFGridMean")
    mean.inputs[1].default_value = 1
    mean.inputs[2].default_value = 1
    grid_to_mesh = nodes.new("GeometryNodeGridToMesh")
    grid_to_mesh.inputs[1].default_value = 0.0
    grid_to_mesh.inputs[2].default_value = 0.0
    set_material = nodes.new("GeometryNodeSetMaterial")
    set_material.inputs[2].default_value = material

    links.new(group_in.outputs[0], mesh_to_sdf.inputs[0])
    links.new(mesh_to_sdf.outputs[0], mean.inputs[0])
    links.new(mean.outputs[0], grid_to_mesh.inputs[0])
    links.new(grid_to_mesh.outputs[0], set_material.inputs[0])
    links.new(set_material.outputs[0], group_out.inputs[0])

    mod = carrier.modifiers.new("GN MeshToSDF chair frame rebuild", "NODES")
    mod.node_group = ng
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    frame_mesh = bpy.data.meshes.new_from_object(carrier.evaluated_get(depsgraph), depsgraph=depsgraph)
    frame_mesh.name = "DiningSlatChairSDFFrameMesh"
    frame_mesh.materials.append(material)
    for poly in frame_mesh.polygons:
        poly.use_smooth = True
        poly.material_index = 0

    bpy.data.objects.remove(carrier, do_unlink=True)
    if control_mesh.users == 0:
        bpy.data.meshes.remove(control_mesh)
    if ng.users == 0:
        bpy.data.node_groups.remove(ng)
    return frame_mesh


def _rounded_rect_loop(width, depth, radius, count_per_corner=10):
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
            loop.append(center + Vector((math.cos(a) * radius, math.sin(a) * radius, 0)))
    return loop


def _build_seat_mesh(material):
    width = 0.497
    depth = 0.446
    center_y = 0.0
    bottom_z = 0.404
    edge_top_z = 0.454
    crown_z = 0.463
    perimeter_count = 64
    ring_count = 9

    outer_loop = _rounded_rect_loop(
        width, depth, min(width, depth) * 0.105, perimeter_count // 4
    )
    verts = [(0, center_y, crown_z)]
    faces = []
    top_rings = []

    for r_i in range(1, ring_count + 1):
        r = r_i / ring_count
        ring = []
        for p in outer_loop:
            x = p.x * r
            y = p.y * r + center_y
            crown = (crown_z - edge_top_z) * (1 - r**2.4)
            slight_scoop = -0.0015 * (y / (depth / 2)) ** 2 * (1 - r * 0.35)
            ring.append(len(verts))
            verts.append((x, y, edge_top_z + crown + slight_scoop))
        top_rings.append(ring)

    n = len(outer_loop)
    first = top_rings[0]
    for i in range(n):
        faces.append((0, first[i], first[(i + 1) % n]))
    for a, b in zip(top_rings[:-1], top_rings[1:]):
        for i in range(n):
            faces.append((a[i], b[i], b[(i + 1) % n], a[(i + 1) % n]))

    # Multi-level bullnose side wall: the top edge rolls under instead of
    # reading as a hard extruded slab.
    side_rings = [top_rings[-1]]
    side_profiles = [
        (0.996, edge_top_z - 0.010),
        (0.986, edge_top_z - 0.024),
        (0.968, bottom_z + 0.010),
        (0.944, bottom_z),
    ]
    for scale, z in side_profiles:
        ring = []
        for p in outer_loop:
            ring.append(len(verts))
            verts.append((p.x * scale, p.y * scale + center_y, z))
        side_rings.append(ring)
    for a, b in zip(side_rings[:-1], side_rings[1:]):
        for i in range(n):
            faces.append((a[i], b[i], b[(i + 1) % n], a[(i + 1) % n]))

    bottom_center = len(verts)
    verts.append((0, center_y, bottom_z))
    bottom = side_rings[-1]
    for i in range(n):
        faces.append((bottom_center, bottom[(i + 1) % n], bottom[i]))

    mesh = bpy.data.meshes.new("DiningSlatChairThinSeatMesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)
    mesh.validate(clean_customdata=False)
    mesh.materials.append(material)
    for poly in mesh.polygons:
        poly.use_smooth = True
        poly.material_index = 0
    return mesh


def _combine_meshes(name, meshes, material):
    verts = []
    faces = []
    for mesh in meshes:
        offset = len(verts)
        verts.extend([tuple(v.co) for v in mesh.vertices])
        faces.extend([tuple(offset + i for i in poly.vertices) for poly in mesh.polygons])
    combined = bpy.data.meshes.new(name)
    combined.from_pydata(verts, [], faces)
    combined.update(calc_edges=True)
    combined.validate(clean_customdata=False)
    combined.materials.append(material)
    for poly in combined.polygons:
        poly.use_smooth = True
        poly.material_index = 0
    return combined


def create_sdf_dining_slat_asset(factory) -> bpy.types.Object:
    """Create the reference dining chair using the SDF/GN frame workflow."""

    material = _red_lacquer_material()
    frame_mesh = _build_frame_mesh(
        material,
        spindle_count=getattr(factory, "dining_slat_spindle_count", 6),
        spindle_path_samples=getattr(factory, "dining_slat_spindle_samples", 22),
    )
    seat_mesh = _build_seat_mesh(material)
    mesh = _combine_meshes("DiningSlatChairSDFAssetMesh", [frame_mesh, seat_mesh], material)

    for temp_mesh in (frame_mesh, seat_mesh):
        if temp_mesh.users == 0:
            bpy.data.meshes.remove(temp_mesh)

    obj = bpy.data.objects.new("DiningSlat_SDFGeometryNodesChair", mesh)
    bpy.context.collection.objects.link(obj)
    obj.rotation_euler.z += np.pi / 2
    butil.apply_transform(obj)
    factory.normalize_to_placeholder_bbox(obj)
    surface.assign_material(obj, material)
    butil.modify_mesh(obj, "WEIGHTED_NORMAL", keep_sharp=True)

    obj["infinigen_style_preset"] = "dining_slat"
    obj["generated_detail_level"] = "reference_reconstruction"
    obj["sdf_geometry_nodes_workflow"] = "control_tube_mesh -> MeshToSDFGrid -> SDFGridMean -> GridToMesh"
    obj["asset_status"] = "modified native preset / local reconstruction asset"
    return obj
