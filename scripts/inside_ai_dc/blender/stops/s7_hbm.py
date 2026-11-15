"""Stop 7: HBM3E stack, quarter cut.

Lesson: the memory is eight thinned DRAM dies and a base die joined vertically by through-silicon vias, and the whole
stack is about as thick as a bank card.
Drawn with two named exaggerations (reference_build.json `exaggeration`): every height on the stage x `hbmHeight`
(stack, interposer, card edge and hair alike, so the thickness comparison stays true), and the via and microbump
diameters x `hbmVia`. Footprints are true scale. No explode states.
"""
import bpy

import lib
from lib import Mesh, part, exag, count
from parts import hbm, referents

HS = exag('hbmHeight')
VS = exag('hbmVia')
INTERPOSER = (0.016, 0.014, 0.0001)      # context: the interposer under the stack (thickness as gpu_package.INT_T)
REQUIRED = ['base-die', 'dram-layers', 'tsv', 'die-edge', 'mold', 'hair', 'card-edge', 'hbm-interposer']


def build():
    lib.reset()
    m = Mesh()
    w, d, t = INTERPOSER
    m.box((w, d, t * HS), (0, 0, t * HS / 2), 'silicon')
    ip = m.finish('hbm-interposer', ao=False)
    part(ip, 'hbm-interposer', 'illustrative', manifest='gpu package geometry', anchor=(-w / 2 + 0.001, -d / 2, t * HS))

    zb = t * HS + hbm.BUMP_T * HS
    parts = hbm.hero(zb, HS, VS)
    top = zb + hbm.H * HS
    assert abs(top - zb - lib.dim('hbmStackHeight') * HS) < 1e-9

    cw, cd = 0.006, 0.005
    card = referents.card_edge(cw, cd, HS).finish('card-edge', ao=False)
    card.location = (-0.0125, 0.006, 0)
    part(card, 'card-edge', 'derived', manifest='ID-1 card referent', anchor=(cw / 2, -cd / 2, lib.dim('id1Card')[1] * HS))

    hair = referents.hair(0.004, HS).finish('hair', ao=False)
    hair.location = (0.004, -0.0115, 0)
    part(hair, 'hair', 'illustrative', manifest='hair referent', anchor=(0, 0, lib.dim('hair') * HS), shadow=False)

    scn = bpy.context.scene
    scn['metresPerUnit'] = 1.0
    scn['stop'] = 7
    scn['scaleBar'] = {'length': 0.001, 'part': 'base-die', 'axis': 'x'}
    scn['exaggeration'] = {'hbmHeight': HS, 'hbmVia': VS}
    scn['referents'] = ['card-edge', 'hair']
    spec = dict(stop=7, required=REQUIRED, counts={'dram': count('dramDiesPerStack')},
                bounds={'base-die': ('hbmFootprint', 'xy'), 'hair': ('hair', 'x')},
                budget={'uniqueTriangles': 80000, 'drawCalls': 150}, flowTolerance=0.0001)
    return spec
