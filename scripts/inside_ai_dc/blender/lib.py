"""Shared helpers for the inside-ai-data-center Blender models.

Spec: docs/specs/inside-ai-data-center-blender-models.md (sections 5, 6). Runs inside Blender 4.5 (bpy).

Frames
  * Blender space, metres, Z up. The front of every model faces -Y (Blender's front view). The glTF exporter's +Y-up
    conversion maps Blender (x, y, z) to three.js (x, z, -y), so the front faces +Z in the page, toward its camera.
  * Vector extras (explode offsets, slot positions, box sizes) are written already converted to glTF space (gl()).

Node contract (spec 6.2)
  * A part is an object named with its part id; custom properties become glTF extras: tier, manifest, explode,
    explodeStep, down, flow, slots, next, kind, box, visibleSteps.
  * Each part has a child empty named 'anchor:<id>' (callout pin position).
  * Objects whose name starts with 'i.' are anonymous linked duplicates; post.mjs turns siblings that share a mesh into
    one EXT_mesh_gpu_instancing node under the same parent.
"""
import json
import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
REF = json.load(open(os.path.join(HERE, '..', 'reference_build.json'), encoding='utf-8'))
BUILD = os.path.join(ROOT, 'build', 'inside_ai_dc')
os.makedirs(BUILD, exist_ok=True)


def count(key):
    return REF['counts'][key]['value']


def dim(key):
    return REF['dims'][key]['value']


# Spec 5.2. sRGB hex, roughness, metalness. The page's runtime PALETTE swaps these by name; check_inside_ai_dc.py
# asserts the two lists match.
PALETTE = {
    'steel-painted': ('#3b4450', 0.55, 0.35),
    'steel-bare': ('#9aa3ab', 0.38, 0.85),
    'aluminium': ('#b9c0c7', 0.34, 0.8),
    'sheet-dark': ('#252b33', 0.6, 0.45),
    'copper': ('#c27b47', 0.32, 0.9),
    'pcb': ('#1e4a3b', 0.7, 0.05),
    'substrate': ('#2d5a4c', 0.65, 0.05),
    'silicon': ('#1d2c3d', 0.25, 0.4),
    'dram': ('#2a3e4f', 0.35, 0.3),
    'mold': ('#2b2d31', 0.8, 0.0),
    'concrete': ('#8a8f94', 0.95, 0.0),
    'asphalt': ('#3b3f44', 0.95, 0.0),
    'roof': ('#59626d', 0.8, 0.1),
    'glass': ('#9cc2d6', 0.15, 0.1),
    'hose': ('#1c1f23', 0.75, 0.0),
    'pipe-facility': ('#6d7f8f', 0.4, 0.7),
    'pipe-secondary': ('#a9b4bd', 0.3, 0.9),
    'cable': ('#262a30', 0.7, 0.0),
    'section': ('#d9d2c3', 0.9, 0.0),
    'referent': ('#9fb0bf', 0.75, 0.05),
    'flow-power': ('#F2A93B', 0.5, 0.0),
    'flow-cool': ('#3E9BE0', 0.5, 0.0),
    'flow-hot': ('#E0574A', 0.5, 0.0),
    'flow-data': ('#4CC38A', 0.5, 0.0),
}
FLOW_MAT = {'power': 'flow-power', 'cool': 'flow-cool', 'hot': 'flow-hot', 'data': 'flow-data'}


def srgb_to_linear(hexcode):
    h = hexcode.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


def gl(v):
    """Blender vector -> glTF/three.js vector (Y up)."""
    return [round(v[0], 5), round(v[2], 5), round(-v[1], 5)]


# ============================================================================ scene

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    scn.unit_settings.system = 'METRIC'
    scn.unit_settings.scale_length = 1.0
    scn['metresPerUnit'] = 1.0
    return scn


def material(name):
    if name not in PALETTE:
        raise ValueError('material outside palette: ' + name)
    m = bpy.data.materials.get(name)
    if m:
        return m
    hexcode, rough, metal = PALETTE[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*srgb_to_linear(hexcode), 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    m.diffuse_color = (*srgb_to_linear(hexcode), 1)
    return m


# ============================================================================ mesh builder

_SCRATCH = None

class Mesh:
    """Accumulates geometry in one bmesh with one material slot per palette name. finish() makes one object, so
    non-selectable detail of a part is already joined per material (one primitive, one draw call per material)."""

    def __init__(self, lod='hero'):
        self.bm = bmesh.new()
        self.mats = []
        self.lod = lod  # 'proxy': no bevels, half the cylinder segments (repeated low-detail exports)

    def _slot(self, mat):
        material(mat)
        if mat not in self.mats:
            self.mats.append(mat)
        return self.mats.index(mat)

    def _tag(self, faces, mat, smooth=False):
        idx = self._slot(mat)
        for f in faces:
            f.material_index = idx
            f.smooth = smooth

    def box(self, size, center, mat, bevel=0.0, rot=None):
        """Axis-aligned box (size x, y, z) centred at center; optional bevel radius on all edges; rot = Matrix (3x3)."""
        sx, sy, sz = size
        if self.lod == 'proxy':
            bevel = 0.0
        if min(sx, sy, sz) <= 0:
            raise ValueError('box with non-positive size %r' % (size,))
        tmp = bmesh.new()
        bmesh.ops.create_cube(tmp, size=1.0)
        bmesh.ops.scale(tmp, vec=Vector((sx, sy, sz)), verts=tmp.verts)
        if bevel > 0:
            b = min(bevel, 0.3 * min(sx, sy, sz))
            bmesh.ops.bevel(tmp, geom=list(tmp.verts) + list(tmp.edges), offset=b, segments=1, affect='EDGES',
                            profile=0.5, clamp_overlap=True)
        m = Matrix.Translation(Vector(center))
        if rot is not None:
            m = m @ rot.to_4x4()
        bmesh.ops.transform(tmp, matrix=m, verts=tmp.verts)
        idx = self._slot(mat)
        for f in tmp.faces:
            f.material_index = idx
            f.smooth = False
        self._merge(tmp)

    def _merge(self, tmp):
        global _SCRATCH
        try:
            ok = _SCRATCH is not None and _SCRATCH.name in bpy.data.meshes
        except ReferenceError:
            ok = False
        if not ok:
            _SCRATCH = bpy.data.meshes.new('_scratch')
        tmp.to_mesh(_SCRATCH)
        tmp.free()
        self.bm.from_mesh(_SCRATCH)

    def cyl(self, radius, length, center, mat, axis='Z', seg=12, radius2=None, caps=True):
        if self.lod == 'proxy':
            seg = max(6, seg // 2)
        res = bmesh.ops.create_cone(self.bm, cap_ends=caps, cap_tris=False, segments=seg, radius1=radius,
                                    radius2=radius if radius2 is None else radius2, depth=length)
        verts = res['verts']
        rot = {'Z': Matrix(), 'X': Matrix.Rotation(math.pi / 2, 4, 'Y'), 'Y': Matrix.Rotation(math.pi / 2, 4, 'X')}[axis]
        bmesh.ops.transform(self.bm, matrix=Matrix.Translation(Vector(center)) @ rot, verts=verts)
        faces = list({f for v in verts for f in v.link_faces})
        idx = self._slot(mat)
        for f in faces:
            f.material_index = idx
            f.smooth = len(f.verts) == 4  # sides smooth, caps flat (the exporter splits the edge)
        return faces

    def tube(self, points, radius, mat, seg=8, bend=0.0):
        """Swept circle along a polyline; corners are rounded by inserting arc points when bend > 0. Returns the
        path actually swept (for endpoint checks)."""
        pts = [Vector(p) for p in points]
        if bend > 0 and len(pts) > 2:
            pts = round_corners(pts, bend)
        rings = []
        n = len(pts)
        prev_side = None
        for i, p in enumerate(pts):
            if i == 0:
                t = (pts[1] - pts[0]).normalized()
            elif i == n - 1:
                t = (pts[-1] - pts[-2]).normalized()
            else:
                t = ((pts[i] - pts[i - 1]).normalized() + (pts[i + 1] - pts[i]).normalized()).normalized()
            if prev_side is None:
                ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
                side = t.cross(ref).normalized()
            else:  # parallel transport keeps the ring from twisting
                side = (prev_side - t * prev_side.dot(t)).normalized()
            up = side.cross(t).normalized()
            prev_side = side
            ring = []
            for k in range(seg):
                a = 2 * math.pi * k / seg
                ring.append(self.bm.verts.new(p + (side * math.cos(a) + up * math.sin(a)) * radius))
            rings.append(ring)
        faces = []
        for r0, r1 in zip(rings, rings[1:]):
            for k in range(seg):
                faces.append(self.bm.faces.new((r0[k], r0[(k + 1) % seg], r1[(k + 1) % seg], r1[k])))
        faces.append(self.bm.faces.new(list(reversed(rings[0]))))
        faces.append(self.bm.faces.new(rings[-1]))
        idx = self._slot(mat)
        for f in faces:
            f.material_index = idx
            f.smooth = len(f.verts) == 4
        return pts

    def finish(self, name, collection=None, ao=True, ao_dist=0.03):
        me = bpy.data.meshes.new(name)
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(material(m))
        obj = bpy.data.objects.new(name, me)
        (collection or bpy.context.scene.collection).objects.link(obj)
        if ao:
            bake_ao(obj, ao_dist)
        return obj


def round_corners(pts, r):
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        d0, d1 = (a - b), (c - b)
        l0, l1 = d0.length, d1.length
        rr = min(r, l0 * 0.45, l1 * 0.45)
        p0 = b + d0.normalized() * rr
        p1 = b + d1.normalized() * rr
        for k in range(5):
            t = k / 4
            out.append((1 - t) ** 2 * p0 + 2 * (1 - t) * t * b + t * t * p1)
    out.append(pts[-1])
    return out


# ============================================================================ ambient occlusion

def _dirs(n=14):
    """Deterministic upper-hemisphere directions (Fibonacci), no random seed needed."""
    out = []
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        z = 1 - (i + 0.5) / n
        r = math.sqrt(1 - z * z)
        out.append(Vector((math.cos(golden * i) * r, math.sin(golden * i) * r, z)))
    return out


DIRS = _dirs()


def bake_ao(obj, dist):
    """Per-vertex self-occlusion by ray cast against the object's own mesh, stored in a byte colour attribute.
    Deterministic. Instances share one mesh, so occlusion between objects is not baked."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bvh = BVHTree.FromBMesh(bm)
    bm.free()
    values = []
    for v in me.vertices:
        n = v.normal
        if n.length < 1e-6:
            values.append(1.0)
            continue
        q = n.to_track_quat('Z', 'Y').to_matrix()
        origin = v.co + n * 1e-4
        hits = 0
        for d in DIRS:
            loc, _, _, _ = bvh.ray_cast(origin, q @ d, dist)
            if loc is not None:
                hits += 1
        values.append(1.0 - 0.55 * hits / len(DIRS))
    ca = me.color_attributes.new('AO', 'BYTE_COLOR', 'CORNER')
    for loop in me.loops:
        a = values[loop.vertex_index]
        ca.data[loop.index].color = (a, a, a, 1.0)
    me.color_attributes.active_color = ca


def instance(src, name, location, collection=None):
    """Linked duplicate (shares mesh data). post.mjs batches 'i.' siblings into one GPU-instanced node."""
    o = bpy.data.objects.new(name, src.data)
    o.location = location
    (collection or bpy.context.scene.collection).objects.link(o)
    for k in ('kind', 'tier', 'shadow'):
        if k in src.keys():
            o[k] = src[k]
    return o


# ============================================================================ naming and extras

def part(obj, pid, tier, manifest=None, anchor=None, **extras):
    """Name an object as a part and attach its contract extras. anchor = local offset (Blender space) of the pin."""
    obj.name = pid
    if obj.data is not None and obj.data.users == 1:
        obj.data.name = pid
    obj['tier'] = tier
    if manifest:
        obj['manifest'] = manifest
    for k, v in extras.items():
        obj[k] = v
    if anchor is not None:
        e = bpy.data.objects.new('anchor:' + pid, None)
        e.empty_display_size = 0.01
        obj.users_collection[0].objects.link(e)
        e.parent = obj
        e.location = anchor
    return obj


def empty(name, location, parent=None):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.02
    bpy.context.scene.collection.objects.link(e)
    e.location = location
    if parent is not None:
        e.parent = parent
    return e


def parent_keep(child, parent):
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_world = mw


# ============================================================================ export

EXPORT_ARGS = dict(export_format='GLB', use_selection=False, export_apply=True, export_extras=True, export_yup=True,
                   export_texcoords=False, export_normals=True, export_cameras=False, export_lights=False,
                   export_animations=False, export_materials='EXPORT', export_vertex_color='ACTIVE',
                   export_all_vertex_colors=False, export_image_format='NONE', export_gpu_instances=True)


def export(path):
    bpy.context.view_layer.update()
    bpy.ops.export_scene.gltf(filepath=path, **EXPORT_ARGS)
    print('exported', path, os.path.getsize(path), 'bytes')


def save_blend(path):
    bpy.ops.wm.save_as_mainfile(filepath=path, check_existing=False, compress=True)


# ============================================================================ validation (spec 6.4)

def _world_bounds(obj, deep=True):
    pts = []
    stack = [obj]
    while stack:
        o = stack.pop()
        if o.type == 'MESH':
            mw = o.matrix_world
            pts += [mw @ Vector(c) for c in o.bound_box]
        if deep:
            stack += list(o.children)
    if not pts:
        return None
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def _mesh_tris(me):
    return sum(len(p.vertices) - 2 for p in me.polygons)


def validate(spec):
    """spec: dict(stop, required ids, counts {kind: n}, bounds {id: (key, tol, axes)}, budgets).
    Raises SystemExit with every failure listed. Returns stats for the manifest."""
    errors = []
    scene = bpy.context.scene
    objs = list(scene.objects)
    by_name = {o.name: o for o in objs}
    parts = [o for o in objs if 'tier' in o.keys() and not o.name.startswith('i.')]

    for pid in spec['required']:
        o = by_name.get(pid)
        if o is None:
            errors.append('missing part ' + pid)
            continue
        if not any(c.name == 'anchor:' + pid for c in o.children):
            errors.append('part %s has no anchor empty' % pid)

    for kind, n in spec.get('counts', {}).items():
        got = sum(1 for o in objs if o.get('kind') == kind)
        if got != n:
            errors.append('count %s: %d != %d' % (kind, got, n))
    for pid, n in spec.get('slots', {}).items():
        o = by_name.get(pid)
        got = len(o['slots']) // 3 if o is not None and 'slots' in o.keys() else -1
        if got != n:
            errors.append('slots %s: %d != %d' % (pid, got, n))

    for pid, (key, axes) in spec.get('bounds', {}).items():
        o = by_name.get(pid)
        b = _world_bounds(o) if o else None
        if not b:
            errors.append('bounds: %s has no geometry' % pid)
            continue
        size = b[1] - b[0]
        want = dim(key)
        want = want if isinstance(want, list) else [want]
        for ax, w in zip(axes, want):
            got = size['xyz'.index(ax)]
            if abs(got - w) > 0.005 * w:
                errors.append('bounds %s.%s = %.4f m, manifest %s = %.4f m' % (pid, ax, got, key, w))

    for o in parts:
        tier = o.get('tier')
        if tier not in ('vendor', 'derived', 'illustrative'):
            errors.append('part %s tier %r' % (o.name, tier))
        if tier == 'vendor' and 'manifest' not in o.keys():
            errors.append('vendor part %s has no manifest key' % o.name)
        if 'manifest' in o.keys() and not _manifest_has(o['manifest']):
            errors.append('part %s manifest key %r not in production notes' % (o.name, o['manifest']))

    for m in bpy.data.materials:
        if m.users and m.name not in PALETTE:
            errors.append('material outside palette: ' + m.name)
    if any(img.users for img in bpy.data.images):
        errors.append('image textures present')
    if any(o.type in ('FONT', 'CURVE', 'SURFACE', 'META') for o in objs):
        errors.append('non-mesh geometry (text or curve) present')

    unique_tris = 0
    seen = set()
    draw_est = 0
    for o in objs:
        if o.type != 'MESH':
            continue
        if o.scale != Vector((1, 1, 1)) and o.name.startswith('i.') is False:
            errors.append('unapplied scale on ' + o.name)
        me = o.data
        if me.name not in seen:
            seen.add(me.name)
            unique_tris += _mesh_tris(me)
            draw_est += max(1, len(me.materials))
            for p in me.polygons:
                if p.area < 1e-12:
                    errors.append('zero-area face in ' + o.name)
                    break
    # instanced groups count once (already done via shared mesh); named parts that reuse a mesh would count twice.
    stats = {'uniqueTriangles': unique_tris, 'drawCallEstimate': draw_est}

    # flow tube ends must touch a mating part, checked in every explode step where the tube is visible
    tol = spec.get('flowTolerance', 0.004)
    meshes = [o for o in objs if o.type == 'MESH']
    steps = sorted({s for o in meshes for s in (o['visibleSteps'] if 'visibleSteps' in o.keys() else [0])})
    for step in steps:
        moved = []
        for o in objs:
            if 'explode' in o.keys() and o.get('explodeStep', 1) <= step:
                g = list(o['explode'])
                d = Vector((g[0], -g[2], g[1]))  # glTF -> Blender
                o.location += d
                moved.append((o, d))
        bpy.context.view_layer.update()
        visible = [o for o in meshes if step in (list(o['visibleSteps']) if 'visibleSteps' in o.keys() else [0, 1, 2])]
        trees = {}
        for o in visible:
            bm = bmesh.new()
            bm.from_mesh(o.data)
            bm.transform(o.matrix_world)
            trees[o.name] = BVHTree.FromBMesh(bm)
            bm.free()
        for o in visible:
            if 'ends' not in o.keys():
                continue
            ends = list(o['ends'])
            for i in range(0, len(ends), 3):
                p = o.matrix_world @ Vector(ends[i:i + 3])
                best = 1e9
                for name, t in trees.items():
                    if name == o.name:
                        continue
                    hit = t.find_nearest(p)
                    if hit[0] is not None:
                        best = min(best, hit[3])
                if best > tol:
                    errors.append('step %d: flow %s end %s is %.1f mm from any mating part'
                                  % (step, o.name, tuple(round(c, 3) for c in p), best * 1000))
        for o, d in moved:
            o.location -= d
        bpy.context.view_layer.update()

    if unique_tris > spec['budget']['uniqueTriangles']:
        errors.append('unique triangles %d > %d' % (unique_tris, spec['budget']['uniqueTriangles']))
    if draw_est > spec['budget']['drawCalls']:
        errors.append('draw call estimate %d > %d' % (draw_est, spec['budget']['drawCalls']))

    if errors:
        for e in errors:
            print('VALIDATE FAIL:', e)
        raise SystemExit('validation failed for stop %s (%d errors)' % (spec['stop'], len(errors)))
    print('validate stop %s: ok, %d unique triangles, ~%d draw calls' % (spec['stop'], unique_tris, draw_est))
    return stats


_MANIFEST_TEXT = None


def _manifest_has(key):
    global _MANIFEST_TEXT
    if _MANIFEST_TEXT is None:
        _MANIFEST_TEXT = open(os.path.join(ROOT, 'docs', 'inside-ai-data-center-production.md'), encoding='utf-8').read()
    return ('`%s`' % key) in _MANIFEST_TEXT


def write_meta(path, stats, extra):
    """Sidecar read by post.mjs: validator stats and the stop's scene extras."""
    data = dict(stats)
    data.update(extra)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1)
