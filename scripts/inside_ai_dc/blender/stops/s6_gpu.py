"""Stop 6: Blackwell GPU package, true scale in metres.

Lesson: "one GPU" is two logic dies and eight memory stacks on an interposer; the package is a layered sandwich.
States: step 0 the whole package with its cold plate lifted clear; step 1 "Slice package" removes the front half
(every package part is split at y = 0 into a rear part and a front child with visibleSteps [0]) and shows the
layer section beside it, drawn with the named vertical exaggeration `packageSliceHeight`.
The HBM stacks are the stop 7 stack's low-detail export (hbm.proxy).
"""
import bpy

import lib
from lib import Mesh, part, instance, exag, count
from parts import gpu_package as G, hbm, referents

VE = exag('packageSliceHeight')
LIFT = 0.03
BOARD = (0.10, 0.10, 0.0024)
PLATE_BACK = 0.055        # the lifted plate also moves back so the dies and stacks stay in view
REQUIRED = ['substrate', 'interposer', 'compute-die-a', 'compute-die-b', 'hbm-array', 'die-link', 'gpu-power',
            'stiffener', 'cold-plate-lifted', 'section', 'gpu-heat', 'fingertip']


def split_part(pid, build_fn, tier, manifest, anchor, ao_dist=0.004, **extras):
    """Build rear/front halves with build_fn(rear, front); the part is the rear half, the front half its child."""
    rear, front = Mesh(), Mesh()
    build_fn(rear, front)
    o = rear.finish(pid, ao_dist=ao_dist)
    f = front.finish(pid + '-front', ao_dist=ao_dist)
    f.parent = o
    f['visibleSteps'] = [0]
    part(o, pid, tier, manifest=manifest, anchor=anchor, **extras)
    return o, f


def build():
    lib.reset()
    S = G.split_box

    def board(r, f):
        S(r, f, BOARD, (0, 0, -BOARD[2] / 2), 'pcb')
    split_part('gpu-board', board, 'illustrative', 'gpu package geometry', None, ao_dist=0.003)

    def substrate(r, f):
        S(r, f, (G.SW, G.SD, G.SUB_T), (0, 0, G.Z_SUB + G.SUB_T / 2), 'substrate')
        # decoupling capacitors between the interposer edge and the stiffener ring
        for k in range(11):
            t = -0.025 + k * 0.005
            for s in (-1, 1):
                S(r, f, (0.001, 0.0005, 0.0005), (s * 0.0315, t, G.Z_SUB_TOP + 0.00025), 'steel-bare')
                S(r, f, (0.0005, 0.001, 0.0005), (t, s * 0.0315, G.Z_SUB_TOP + 0.00025), 'steel-bare')
    sub, sub_front = split_part('substrate', substrate, 'illustrative', 'gpu package geometry',
                                (-G.SW / 2 + 0.004, -G.SD / 2 + 0.004, G.Z_SUB_TOP))
    # ball grid on the underside: instanced, rear set under the substrate, front set under its front half
    m = Mesh()
    m.cyl(0.00032, G.BALL_T, (0, 0, G.BALL_T / 2), 'copper', seg=8)
    ball = m.finish('i.ball.0', ao=False)
    ball['kind'] = 'ball'
    ball['shadow'] = False
    n = 0
    pitch = 0.0018
    k = int((G.SW - 0.004) / pitch)
    mid = min(range(k), key=lambda j: abs(-(k - 1) * pitch / 2 + j * pitch))
    for i in range(k):
        for j in range(k):
            # only the balls that can be seen: three outer rings and the rows either side of the cut plane
            if min(i, j, k - 1 - i, k - 1 - j) >= 3 and abs(j - mid) > 1:
                continue
            x = -(k - 1) * pitch / 2 + i * pitch
            y = -(k - 1) * pitch / 2 + j * pitch
            o = ball if n == 0 else instance(ball, 'i.ball.%d' % n, (x, y, 0))
            o.location = (x, y, 0)
            o.parent = sub if y > 0 else sub_front
            n += 1

    def ring(r, f):
        for size, c in G.ring_boxes():
            S(r, f, size, c, 'steel-bare')
    split_part('stiffener', ring, 'illustrative', 'gpu package geometry', (G.SW / 2 - 0.0015, -0.02, G.Z_SUB_TOP + G.RING_H))

    def interposer(r, f):
        S(r, f, (G.IW - 0.001, G.ID - 0.001, G.C4_T), (0, 0, G.Z_SUB_TOP + G.C4_T / 2), 'copper')
        S(r, f, (G.IW, G.ID, G.INT_T), (0, 0, G.Z_INT + G.INT_T / 2), 'silicon')
    split_part('interposer', interposer, 'illustrative', 'gpu package geometry', (-G.IW / 2 + 0.001, -G.ID / 2 + 0.001, G.Z_INT_TOP))

    for i, x in enumerate(G.DIE_X):
        pid = ('compute-die-a', 'compute-die-b')[i]

        def die(r, f, x=x):
            S(r, f, (G.DW - 0.0004, G.DD - 0.0004, G.UB_T), (x, 0, G.Z_INT_TOP + G.UB_T / 2), 'copper')
            S(r, f, (G.DW, G.DD, G.DIE_T), (x, 0, G.Z_DIE + G.DIE_T / 2), 'silicon')
        # pins at the four screen corners of the package (default camera) so they stay apart at 375 px
        anchor = (x - G.DW / 2 + 0.003, 0.0155, G.Z_DIE_TOP) if i == 0 else (x + 0.011, -0.0155, G.Z_DIE_TOP)
        o, f = split_part(pid, die, 'vendor', 'gpu', anchor)
        o['kind'] = 'compute-die'
        if i == 0:   # fault tag on the lifted plate's rear edge, clear of the four pins
            lib.fail_anchor(o, pid, (-0.03, PLATE_BACK + 0.041, G.TOP + LIFT + 0.009))

    # eight HBM stacks: rear four under hbm-array, front four under its child hbm-front (hidden in the slice)
    m = Mesh()
    hbm.proxy(m)
    stack = m.finish('i.hbm.0', ao=False)
    stack['kind'] = 'hbm'
    stack['tier'] = 'vendor'
    pos = G.hbm_positions()
    p0 = (pos[0][0], pos[0][1], G.Z_DIE)
    arr = lib.empty('hbm-array', p0)
    fr = lib.empty('hbm-front', (0, 0, 0), parent=arr)
    fr['visibleSteps'] = [0]
    for i, (x, y) in enumerate(pos):
        o = stack if i == 0 else instance(stack, 'i.hbm.%d' % i, (0, 0, 0))
        o.parent = arr if y > 0 else fr
        o.location = (x - p0[0], y - p0[1], 0)
    part(arr, 'hbm-array', 'vendor', manifest='hbm', anchor=(pos[3][0] - p0[0] + 0.004, 0.004, hbm.H), next=True)

    # die-to-die link: short bridges arching over the die gap (region drawn, not the buried bridge's real routing)
    m = Mesh()
    ends = []
    for k in range(6):
        y = 0.002 + k * 0.0024
        swept = m.tube([(-0.0012, y, G.Z_DIE_TOP), (-0.0006, y, G.Z_DIE_TOP + 0.0004), (0.0006, y, G.Z_DIE_TOP + 0.0004),
                        (0.0012, y, G.Z_DIE_TOP)], 0.00012, 'copper', seg=6, bend=0.0003)
        ends += list(swept[0]) + list(swept[-1])
    o = m.finish('die-link', ao=False)
    part(o, 'die-link', 'illustrative', manifest='gpu package geometry', anchor=(0, 0.008, G.Z_DIE_TOP + 0.0004),
         flow='data', carrier='copper', ends=ends, shadow=False)

    # power path: via columns from the ball grid up through the substrate to the capacitor field (on the cut plane)
    m = Mesh()
    ends = []
    for x in (-0.033, -0.031, 0.031, 0.033):
        z0, z1 = 0.0001, G.Z_SUB_TOP + 0.0002
        m.cyl(0.0004, z1 - z0, (x, 0, (z0 + z1) / 2), 'copper', seg=8)
        ends += [x, 0, z0, x, 0, z1]
    o = m.finish('gpu-power', ao=False)
    part(o, 'gpu-power', 'illustrative', manifest='gpu package geometry', anchor=(0.032, 0, G.Z_SUB_TOP),
         flow='power', carrier='copper', ends=ends, shadow=False)

    # cold plate lifted clear of the dies (heat path shown by the arrows)
    m = Mesh()
    z = G.TOP + LIFT
    yb = PLATE_BACK
    m.box((0.078, 0.082, 0.003), (0, yb, z + 0.0015), 'copper', bevel=0.0004)
    m.box((0.078, 0.082, 0.006), (0, yb, z + 0.006), 'aluminium', bevel=0.0008)
    for s in (-1, 1):
        m.cyl(0.0045, 0.012, (s * 0.025, yb + 0.041 + 0.006, z + 0.006), 'steel-bare', axis='Y', seg=10)
    plate = m.finish('cold-plate-lifted', ao_dist=0.004)
    part(plate, 'cold-plate-lifted', 'illustrative', manifest='gpu package geometry', anchor=(0.03, PLATE_BACK - 0.035, z + 0.009))

    m = Mesh()
    for x in G.DIE_X:
        z0, z1 = G.Z_DIE_TOP + 0.002, G.TOP + 0.016
        m.cyl(0.0012, z1 - z0, (x, -0.004, (z0 + z1) / 2), 'flow-hot', seg=10)
        m.cyl(0.0028, 0.004, (x, -0.004, z1 + 0.002), 'flow-hot', seg=12, radius2=0.0)
    heat = m.finish('gpu-heat', ao=False)
    part(heat, 'gpu-heat', 'illustrative', manifest='gpu package geometry', anchor=(G.DIE_X[0], -0.004, G.TOP + 0.01),
         flow='cool', shadow=False)

    # Slice section (step 1): y = 0 cut from inside die B to the package edge, every height x VE
    m = Mesh()
    G.section(m, 0.012, G.SW / 2, 0.003, VE)
    sec = m.finish('section', ao=False)
    sec.location = (0.0, -0.03, -BOARD[2])   # at its true x, standing in the removed front half
    part(sec, 'section', 'illustrative', manifest='exaggeration constants', anchor=(0.025, 0, 0.012 * VE),
         visibleSteps=[1], shadow=False)

    tip = referents.fingertip().finish('fingertip', ao=False)
    tip.location = (-0.03, -0.072, -BOARD[2])
    part(tip, 'fingertip', 'illustrative', manifest='fingertip referent', anchor=(0, 0.01, lib.dim('fingertipWidth')))

    scn = bpy.context.scene
    scn['metresPerUnit'] = 1.0
    scn['stop'] = 6
    scn['scaleBar'] = {'length': 0.01, 'part': 'substrate', 'axis': 'x'}
    scn['exaggeration'] = {'packageSliceHeight': VE}
    scn['referents'] = ['fingertip']
    scn['defaultStep'] = 0
    spec = dict(stop=6, required=REQUIRED,
                counts={'compute-die': count('computeDiesPerPackage'), 'hbm': count('hbmStacksPerPackage')},
                bounds={'compute-die-a': ('reticleField', 'xy'), 'substrate': ('gpuSubstrate', 'xy'),
                        'fingertip': ('fingertipWidth', 'x')},
                budget={'uniqueTriangles': 80000, 'drawCalls': 150}, flowTolerance=0.0006)
    return spec
