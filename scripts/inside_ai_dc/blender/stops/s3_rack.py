"""Stop 3: GB200 NVL72 contents in an ORv3 proxy envelope, true scale in metres.

Lesson: the rack is one 72-GPU computer because every tray blind-mates into three shared spines at the rear.
States: explodeStep 1 slides one compute tray forward on its rails; explodeStep 2 moves the spines rearward.
"""
import bpy
from mathutils import Vector

import lib
from lib import gl, part, count
from parts import rack as R, referents, tray as T

ORDER = lib.REF['rackOrder']['fromTop']
HERO = lib.REF['rackOrder']['heroComputeIndex']
SLIDE = 0.45      # step 1: hero tray forward on its rails (m)
SPINE_BACK = 0.25 # step 2: spines rearward (m)
GPU_XS = (-0.197, -0.073, 0.073, 0.197)   # GPU package centres across the tray (tray stop layout)
GPU_Y, GPU_Z = 0.085, 0.017
SLOT_SIZE = [0.078, 0.012, 0.082]         # runtime GPU-and-plate block, glTF axes (x, up, depth)

REQUIRED = ['rack', 'compute-tray', 'switch-tray', 'manifold', 'return', 'busbar', 'nvlink-spine', 'domain',
            'person', 'rack-gpus']


def build():
    lib.reset()
    rack = R.frame('hero').finish('rack')
    part(rack, 'rack', 'illustrative', manifest='rack', anchor=(0, R.FRONT, R.RH))

    templates = {'compute': T.proxy('compute').finish('proxy-compute'),
                 'switch': T.proxy('switch').finish('proxy-switch'),
                 'power': R.shelf_proxy('power').finish('proxy-power'),
                 'tor': R.shelf_proxy('tor').finish('proxy-tor')}
    kinds = {'compute': 'compute-tray', 'switch': 'switch-tray', 'power': 'power-shelf', 'tor': 'tor-switch'}
    used = {k: False for k in templates}
    n = {k: 0 for k in templates}
    compute_slots, switch_slots, slots = [], [], []
    for i, kind in enumerate(ORDER):
        z = R.slot_z(i)
        loc = (0, R.TRAY_Y, z)
        idx = n[kind]
        n[kind] += 1
        hero_id = {'compute': 'compute-tray', 'switch': 'switch-tray'}.get(kind) if idx == HERO else None
        if hero_id:
            o = bpy.data.objects.new(hero_id, templates[kind].data.copy())
            bpy.context.scene.collection.objects.link(o)
            o.location = loc
            o['kind'] = kinds[kind]
            extras = {'shadow': kind == 'compute'}
            if kind == 'compute':
                extras = dict(explode=gl((0, -SLIDE, 0)), explodeStep=1, next=True)
            part(o, hero_id, 'illustrative', manifest='compute tray envelope',
                 anchor=(0, T.FRONT - 0.012, T.TH / 2), **extras)
        elif not used[kind]:
            o = templates[kind]
            o.name = 'i.%s.%02d' % (kind, idx)
            o.location = loc
            o['kind'] = kinds[kind]
            o['tier'] = 'illustrative'
            o['shadow'] = False
            used[kind] = True
        else:
            o = lib.instance(templates[kind], 'i.%s.%02d' % (kind, idx), loc)
        if kind == 'compute':
            compute_slots.append(i)
            for x in GPU_XS:
                slots += gl((x, R.TRAY_Y + GPU_Y, z + GPU_Z))
        elif kind == 'switch':
            switch_slots.append(i)

    # runtime-instanced GPU slots (per-tray fault state); the hero tray's four follow its slide
    g = lib.empty('rack-gpus', (0, 0, 0))
    part(g, 'rack-gpus', 'vendor', manifest='tray', anchor=(0, R.TRAY_Y, R.slot_z(6 + HERO) + 0.03),
         slots=slots, slotSize=SLOT_SIZE, followPart='compute-tray', followFrom=HERO * 4,
         followTo=HERO * 4 + count('gpuSlotsPerTray'), kind='gpu-slots')

    liquid = compute_slots + switch_slots
    spine = dict(explode=gl((0, SPINE_BACK, 0)), explodeStep=2, shadow=False)
    bus = R.busbar().finish('busbar')
    part(bus, 'busbar', 'illustrative', manifest='rack rear spines', anchor=(T.BUS_X, R.SPINE_Y + 0.03, R.TOP_SLOT - 0.05),
         flow='power', carrier='copper', **spine)
    sup, sup_ends = R.manifold(T.QD_SUPPLY_X, liquid)
    sup = sup.finish('manifold')
    part(sup, 'manifold', 'illustrative', manifest='rack rear spines',
         anchor=(T.QD_SUPPLY_X, R.SPINE_Y + 0.04, 1.0), flow='cool', carrier='pipe-secondary', ends=sup_ends, **spine)
    ret, ret_ends = R.manifold(T.QD_RETURN_X, liquid)
    ret = ret.finish('return')
    part(ret, 'return', 'illustrative', manifest='rack rear spines',
         anchor=(T.QD_RETURN_X, R.SPINE_Y + 0.04, 0.8), flow='hot', carrier='pipe-secondary', ends=ret_ends, **spine)
    nvl = R.nvlink_spine(compute_slots, switch_slots).finish('nvlink-spine')
    part(nvl, 'nvlink-spine', 'illustrative', manifest='rack rear spines',
         anchor=(T.NVL_X[1], R.SPINE_Y + 0.09, 1.0), flow='data', carrier='cable', **spine)

    # NVLink domain: dashed outline drawn at runtime around the 18 compute trays, 9 switch trays and the spines
    z_lo = R.slot_z(max(compute_slots))
    z_hi = R.slot_z(min(compute_slots)) + R.RU
    y_lo, y_hi = R.TRAY_Y + T.FRONT - 0.01, R.SPINE_Y + 0.19
    w = T.TW + 0.04
    dom = lib.empty('domain', (0, (y_lo + y_hi) / 2, (z_lo + z_hi) / 2))
    part(dom, 'domain', 'vendor', manifest='rack', anchor=(0, (y_lo - y_hi) / 2, 0),
         box=[round(w, 4), round(z_hi - z_lo, 4), round(y_hi - y_lo, 4)])

    person = referents.person().finish('person', ao_dist=0.08)
    person.location = (-R.RW / 2 - 0.42, -0.25, 0)
    part(person, 'person', 'illustrative', manifest='person', anchor=(0, 0, lib.dim('person') + 0.02))

    scn = bpy.context.scene
    scn['metresPerUnit'] = 1.0
    scn['stop'] = 3
    scn['scaleBar'] = {'length': 2.054, 'part': 'rack', 'axis': 'y'}

    spec = dict(stop=3, required=REQUIRED,
                counts={'compute-tray': count('computeTrays'), 'switch-tray': count('switchTrays'),
                        'power-shelf': count('powerShelves'), 'tor-switch': count('torSwitches')},
                slots={'rack-gpus': count('computeTrays') * count('gpuSlotsPerTray')},
                bounds={'rack': ('rackEnvelope', 'xzy'), 'person': ('person', 'z')},
                budget={'uniqueTriangles': 80000, 'drawCalls': 150})
    return spec
