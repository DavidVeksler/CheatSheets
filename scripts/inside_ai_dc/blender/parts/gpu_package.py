"""Blackwell GPU package (spec section 4, stop 6) and its low-detail proxy (placed twice on the superchip, stop 5,
and through the superchip proxy in the tray, stop 4).

Local frame: metres, origin at the package centre on the underside of the ball grid (= board top), front at -Y, Z up.
Counts are vendor-stated (two compute dies, eight HBM stacks). The dies are drawn at the 26 x 33 mm reticle field
(manifest `reticle field`, standard figure; the die size itself is not published). Substrate, interposer, layer
heights and component placement are illustrative (`gpu package geometry`). Package heights are true scale; only the
Slice section built by section() is drawn with the `packageSliceHeight` vertical exaggeration.
"""
import lib
from lib import Mesh, count
from parts import hbm

SW, SD = lib.dim('gpuSubstrate')
DW, DD = lib.dim('reticleField')
DIE_GAP = 0.0004
DIE_X = (-(DW + DIE_GAP) / 2, (DW + DIE_GAP) / 2)

# Layer stack, z of each top surface (true scale, illustrative thicknesses)
BALL_T = 0.0005
SUB_T = 0.0035
C4_T = 0.0001
INT_T = 0.0001
UB_T = 0.00004
DIE_T = 0.00075
TIM_T = 0.00051
Z_SUB = BALL_T                      # substrate underside
Z_SUB_TOP = Z_SUB + SUB_T
Z_INT = Z_SUB_TOP + C4_T            # interposer underside
Z_INT_TOP = Z_INT + INT_T
Z_DIE = Z_INT_TOP + UB_T            # die and HBM underside
Z_DIE_TOP = Z_DIE + DIE_T
TOP = Z_DIE_TOP + TIM_T             # cold plate contact plane: 5.5 mm above the board (tray.PLATE_Z - board)

IW, ID = 2 * DW + DIE_GAP + 0.0036, DD + 2 * (hbm.FD + 0.0005) + 0.0035   # interposer
HBM_X = (-0.01875, -0.00625, 0.00625, 0.01875)
HBM_Y = DD / 2 + 0.0005 + hbm.FD / 2
RING_W = 0.003                      # stiffener ring width, illustrative
RING_H = TOP - Z_SUB_TOP


def hbm_positions():
    """Eight stack centres (x, y): four along each long side of the die pair."""
    return [(x, s * HBM_Y) for s in (1, -1) for x in HBM_X]


def ring_boxes():
    """Stiffener ring as four boxes (size, centre) on the substrate perimeter."""
    zc = Z_SUB_TOP + RING_H / 2
    return [((SW, RING_W, RING_H), (0, s * (SD / 2 - RING_W / 2), zc)) for s in (-1, 1)] + \
           [((RING_W, SD - 2 * RING_W, RING_H), (s * (SW / 2 - RING_W / 2), 0, zc)) for s in (-1, 1)]


def proxy(m, origin=(0, 0, 0)):
    """Low-detail package: ball layer, substrate, stiffener ring, interposer, two dies, eight HBM proxies."""
    ox, oy, oz = origin
    m.box((SW - 0.004, SD - 0.004, BALL_T), (ox, oy, oz + BALL_T / 2), 'sheet-dark')
    m.box((SW, SD, SUB_T), (ox, oy, oz + Z_SUB + SUB_T / 2), 'substrate')
    for size, c in ring_boxes():
        m.box(size, (ox + c[0], oy + c[1], oz + c[2]), 'steel-bare')
    m.box((IW, ID, INT_T + C4_T), (ox, oy, oz + Z_SUB_TOP + (INT_T + C4_T) / 2), 'silicon')
    for x in DIE_X:
        m.box((DW, DD, DIE_T + UB_T), (ox + x, oy, oz + Z_INT_TOP + (DIE_T + UB_T) / 2), 'silicon')
    for x, y in hbm_positions():
        hbm.proxy(m, (ox + x, oy + y, oz + Z_INT_TOP + UB_T))


def split_box(rear, front, size, c, mat, bevel=0.0):
    """Box split at y = 0 into a rear piece (rear Mesh) and a front piece (front Mesh) for the Slice state."""
    sx, sy, sz = size
    y0, y1 = c[1] - sy / 2, c[1] + sy / 2
    if y0 >= 0:
        rear.box(size, c, mat, bevel)
    elif y1 <= 0:
        front.box(size, c, mat, bevel)
    else:
        rear.box((sx, y1, sz), (c[0], y1 / 2, c[2]), mat)
        front.box((sx, -y0, sz), (c[0], y0 / 2, c[2]), mat)


SLICE_LAYERS = [  # bottom to top: (name, true thickness, material); the spec's slice order read upward
    ('board', 0.0024, 'pcb'), ('solder balls', BALL_T, 'copper'), ('substrate', SUB_T, 'substrate'),
    ('bumps', C4_T, 'copper'), ('interposer', INT_T, 'silicon'), ('microbumps', UB_T, 'copper'),
    ('die', DIE_T, 'silicon'), ('thermal interface', TIM_T, 'aluminium'), ('cold plate', 0.003, 'copper'),
]


def section(m, x0, x1, depth, ve):
    """Slice section through the package on y = 0 from x0 to x1 (true horizontal scale), every height x ve.
    Bump layers are drawn as rows of bumps; layers that do not reach x1 stop at their true edge. Each layer keeps its
    own material so the sandwich reads by colour."""
    z = 0.0
    for name, t, mat in SLICE_LAYERS:
        h = t * ve
        lo, hi = x0, x1
        if name in ('interposer', 'bumps'):
            hi = min(x1, IW / 2)
        if name in ('die', 'microbumps', 'thermal interface'):
            hi = min(x1, DIE_X[1] + DW / 2)
        if name == 'cold plate':
            hi = x1
        if hi > lo:
            if name in ('solder balls', 'bumps', 'microbumps'):
                pitch = {'solder balls': 0.0018, 'bumps': 0.0009, 'microbumps': 0.0006}[name]
                r = pitch * 0.32
                k = 0
                while lo + pitch / 2 + k * pitch < hi:
                    m.cyl(r, h, (lo + pitch / 2 + k * pitch, 0, z + h / 2), mat, seg=8)
                    k += 1
            else:
                m.box((hi - lo, depth, h), ((lo + hi) / 2, 0, z + h / 2), mat)
        z += h
    return z
