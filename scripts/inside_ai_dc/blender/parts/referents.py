"""True-size scale referents (spec 3.6): a 1.75 m person, an ID-1 card, a fingertip, a hair and a card-edge fragment.
Neutral `referent` material."""
import lib
from lib import Mesh

import bmesh
from mathutils import Matrix, Vector


def person():
    """Standing adult, feet at z = 0, crown at exactly dims.person. Simplified, no face or clothing detail."""
    h = lib.dim('person')
    m = Mesh()
    head_r = 0.105
    for s in (-1, 1):
        m.cyl(0.072, 0.80, (s * 0.09, 0, 0.06 + 0.40), 'referent', seg=10, radius2=0.058)  # leg (thigh at top)
        m.box((0.10, 0.26, 0.06), (s * 0.09, -0.05, 0.03), 'referent', bevel=0.02)          # shoe
        m.cyl(0.046, 0.60, (s * 0.235, 0, 1.13), 'referent', seg=8, radius2=0.04)             # arm
    m.cyl(0.155, 0.62, (0, 0, 1.17), 'referent', seg=12, radius2=0.19)                        # torso
    m.box((0.40, 0.20, 0.08), (0, 0, 1.46), 'referent', bevel=0.035)                          # shoulders
    m.cyl(0.05, 0.10, (0, 0, 1.53), 'referent', seg=8)                                        # neck
    tmp = bmesh.new()
    bmesh.ops.create_uvsphere(tmp, u_segments=14, v_segments=9, radius=head_r)
    bmesh.ops.transform(tmp, matrix=Matrix.Translation(Vector((0, 0, h - head_r))), verts=tmp.verts)
    for f in tmp.faces:
        f.material_index = m._slot('referent')
        f.smooth = True
    m._merge(tmp)
    return m


def id_card():
    """ISO/IEC 7810 ID-1 card lying flat: 85.60 x 53.98 x 0.76 mm, corner radius drawn as a small bevel."""
    w, t, d = lib.dim('id1Card')
    m = Mesh()
    m.box((w, d, t), (0, 0, t / 2), 'referent', bevel=0.003)
    return m


def fingertip():
    """Fingertip lying on its pad, pointing at -Y: a 16 mm wide rounded cylinder, 30 mm long. Width from
    dims.fingertipWidth (illustrative adult index finger); no nail or print detail."""
    r = lib.dim('fingertipWidth') / 2
    m = Mesh()
    length = 0.03 - r
    m.cyl(r, length, (0, length / 2, r), 'referent', axis='Y', seg=20, caps=False)
    tmp = bmesh.new()
    bmesh.ops.create_uvsphere(tmp, u_segments=20, v_segments=12, radius=r)
    bmesh.ops.transform(tmp, matrix=Matrix.Translation(Vector((0, 0, r))), verts=tmp.verts)
    for f in tmp.faces:
        f.material_index = m._slot('referent')
        f.smooth = True
    m._merge(tmp)
    return m


def hair(length, hs):
    """Hair segment along Y with its cut end at y = 0 facing -Y, lying on z = 0. Diameter dims.hair; height x hs
    (the stage's vertical exaggeration, so the section is drawn as an ellipse)."""
    r = lib.dim('hair') / 2
    m = Mesh()
    faces = m.cyl(r, length, (0, length / 2, r), 'referent', axis='Y', seg=16)
    verts = list({v for f in faces for v in f.verts})
    bmesh.ops.scale(m.bm, vec=Vector((1, 1, hs)), verts=verts)
    return m


def card_edge(w, d, hs):
    """Fragment of an ID-1 card (0.76 mm thick) lying flat, w x d, with section faces on its two cut edges (-Y, +X);
    thickness x hs."""
    t = lib.dim('id1Card')[1] * hs
    m = Mesh()
    m.box((w, d, t), (0, 0, t / 2), 'referent')
    m.box((w, 0.00002, t), (0, -d / 2 - 0.00001, t / 2), 'section')
    m.box((0.00002, d, t), (w / 2 + 0.00001, 0, t / 2), 'section')
    return m
