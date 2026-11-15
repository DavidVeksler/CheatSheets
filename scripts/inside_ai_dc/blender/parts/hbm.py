"""HBM3E stack (spec section 4, stop 7) and its low-detail proxy (placed eight times in the GPU package, stop 6).

Local frame: metres, origin at the centre of the stack footprint on the underside of the base die, front at -Y, Z up.
Footprint and the per-layer split are illustrative (manifest rows `hbm stack footprint`, `hbm via and bump scale`);
the total stack height is the JEDEC HBM3E maximum (`hbm stack height`) and the die count is vendor-stated.

The hero is drawn with two named exaggerations from reference_build.json: every height x hs (`hbmHeight`) and the
via and microbump diameters x vs (`hbmVia`). The proxy is true scale.
"""
import bmesh
from mathutils import Matrix, Vector

import lib
from lib import Mesh, count

FW, FD = lib.dim('hbmFootprint')
H = lib.dim('hbmStackHeight')
N = count('dramDiesPerStack')

# Illustrative layer split, summing to H: base die, one microbump gap under every DRAM die, thin core dies, thicker top die.
BASE_T = 0.00006
GAP_T = 0.000025
CORE_T = 0.000035
TOP_T = H - BASE_T - N * GAP_T - (N - 1) * CORE_T
BUMP_T = 0.00004            # base-die bumps to the interposer (below z = 0 of the stack proper)
BUMP_D = 0.000025           # microbump diameter, illustrative
MOLD_W = 0.0003             # mould compound wall between the core dies and the stack edge, illustrative


def layers():
    """(name, z0, thickness) for the base die and the N DRAM dies, true scale, z from the base die underside."""
    out = [('base', 0.0, BASE_T)]
    z = BASE_T
    for i in range(N):
        z += GAP_T
        t = TOP_T if i == N - 1 else CORE_T
        out.append(('dram%d' % i, z, t))
        z += t
    assert abs(z - H) < 1e-9, z
    return out


def proxy(m, origin=(0, 0, 0)):
    """True-scale low-detail stack: moulded block with the top DRAM die showing. Two boxes."""
    ox, oy, oz = origin
    m.box((FW, FD, H * 0.96), (ox, oy, oz + H * 0.48), 'mold')
    m.box((FW - 2 * MOLD_W, FD - 2 * MOLD_W, H * 0.04), (ox, oy, oz + H * 0.98), 'dram')   # top DRAM die, ground flush


# ============================================================================ hero (stop 7)

def lbox(m, x0, x1, y0, y1, z0, h, mat):
    """Box over [x0,x1] x [y0,y1] minus the front-right quarter (x > 0, y < 0): the quarter cut. Section plates on the
    two cut faces so a cut reads as a cut (spec 3.3)."""
    t = 0.00001
    m.box((x1 - x0, y1, h), ((x0 + x1) / 2, y1 / 2, z0 + h / 2), mat)          # rear half, full width
    m.box((-x0, -y0, h), (x0 / 2, y0 / 2, z0 + h / 2), mat)                   # front-left quarter
    m.box((x1, t, h), (x1 / 2, -t / 2, z0 + h / 2), 'section')               # cut face y = 0, x > 0
    m.box((t, -y0, h), (t / 2, y0 / 2, z0 + h / 2), 'section')                # cut face x = 0, y < 0


def scale_z(m, verts, hs, z_origin=0.0):
    bmesh.ops.scale(m.bm, vec=Vector((1, 1, hs)), space=Matrix.Translation(Vector((0, 0, -z_origin))), verts=list(verts))


def hero(zb, hs, vs, collection=None):
    """Quarter-cut stack for stop 7. zb = drawn z of the base die underside. Returns the part objects by id.
    Heights x hs, via and bump diameters x vs; footprint true scale."""
    from lib import part, instance
    w = MOLD_W
    cx0, cx1, cy0, cy1 = -FW / 2 + w, FW / 2 - w, -FD / 2 + w, FD / 2 - w   # core die footprint
    L = layers()
    z = lambda v: zb + v * hs
    out = {}

    m = Mesh()
    lbox(m, -FW / 2, FW / 2, -FD / 2, FD / 2, z(0), BASE_T * hs, 'silicon')
    rb, hb = BUMP_D / 2 * vs, BUMP_T * hs
    for row in (rb + 0.00002, 3.2 * rb):
        for k in range(int((FW / 2 - 0.0006) / (3 * rb))):
            m.cyl(rb, hb, (0.0005 + k * 3 * rb, -row, zb - hb / 2), 'copper', seg=10)
    base = m.finish('base-die', collection, ao_dist=0.0006)
    out['base-die'] = part(base, 'base-die', 'illustrative', manifest='hbm stack footprint',
                           anchor=(-FW / 2 + 0.0005, -FD / 2, z(BASE_T / 2)))

    layers_parent = lib.empty('dram-layers', (0, 0, 0))
    core = Mesh()
    lbox(core, cx0, cx1, cy0, cy1, 0.0, CORE_T * hs, 'dram')
    core_obj = core.finish('i.dram.0', collection, ao=False)
    core_obj['kind'] = 'dram'
    core_obj['tier'] = 'illustrative'
    core_obj['shadow'] = False
    dies = [n for n in L if n[0] != 'base']
    for i, (name, z0, t) in enumerate(dies[:-1]):
        o = core_obj if i == 0 else instance(core_obj, 'i.dram.%d' % i, (0, 0, z(z0)), collection)
        o.location = (0, 0, z(z0))
        o.parent = layers_parent
    top = Mesh()
    lbox(top, cx0, cx1, cy0, cy1, 0.0, TOP_T * hs, 'dram')
    top_obj = top.finish('dram-top', collection, ao=False)
    top_obj['kind'] = 'dram'
    top_obj.location = (0, 0, z(dies[-1][1]))
    top_obj.parent = layers_parent
    mid = dies[N // 2]
    out['dram-layers'] = part(layers_parent, 'dram-layers', 'vendor', manifest='hbm stack height',
                              anchor=(0.0, cy0 + 0.0012, z(mid[1] + CORE_T)))

    lib.fail_anchor(layers_parent, 'dram-layers', (-FW / 2 - 0.0015, FD / 2, z(H)))   # fault tag rear left, clear of the pins

    m = Mesh()
    rt = lib.dim('tsvDiameter') / 2 * vs
    y = -(rt + 0.00001)
    z_top = z(dies[-1][1])       # TSVs end under the top die
    xs = [0.0007 + k * (cx1 - 0.0011) / 7 for k in range(8)]
    for x in xs:
        m.cyl(rt, z_top - zb, (x, y, (zb + z_top) / 2), 'copper', seg=8)
        for (_, z0, _t) in dies:
            m.cyl(rb * 0.8, GAP_T * hs, (x, y, z(z0 - GAP_T / 2)), 'copper', seg=10)
    tsv = m.finish('tsv', collection, ao=False)
    out['tsv'] = part(tsv, 'tsv', 'illustrative', manifest='hbm via and bump scale', anchor=(xs[7], y, z(dies[0][1])),
                      flow='data', carrier='copper', ends=[xs[0], y, zb, xs[0], y, z_top], shadow=False)

    m = Mesh()
    zm0, hm = z(BASE_T), (H - BASE_T) * hs
    m.box((w, FD, hm), (-FW / 2 + w / 2, 0, zm0 + hm / 2), 'mold')
    m.box((FW - w, w, hm), (w / 2, FD / 2 - w / 2, zm0 + hm / 2), 'mold')
    m.box((FW / 2 - w, w, hm), (-FW / 4 + w / 2, -FD / 2 + w / 2, zm0 + hm / 2), 'mold')
    m.box((w, FD / 2 - w, hm), (FW / 2 - w / 2, FD / 4 - w / 2, zm0 + hm / 2), 'mold')
    mold = m.finish('mold', collection, ao_dist=0.0006)
    out['mold'] = part(mold, 'mold', 'illustrative', manifest='hbm stack footprint', anchor=(-FW / 2, -FD / 4, z(H)))

    m = Mesh()
    ht = 0.00003 * hs
    m.box((cx1 - 0.0002, 0.00003, ht), ((cx1 + 0.0002) / 2, -0.000025, z(H) - ht / 2), 'section')
    edge = m.finish('die-edge', collection, ao=False)
    out['die-edge'] = part(edge, 'die-edge', 'illustrative', manifest='hbm stack footprint', anchor=(cx1 * 0.35, -0.0001, z(H)))
    return out
