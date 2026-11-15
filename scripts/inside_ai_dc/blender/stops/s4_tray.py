"""Stop 4: 1RU compute tray, true scale in metres.

Lesson: a 1RU tray is mostly cold plate and power delivery, and coolant reaches four GPUs through a sealed loop that
starts and ends at two rear quick disconnects.
States: explodeStep 1 lifts the lid; explodeStep 2 removes it and lifts the cold plates (hoses follow).
"""
import bpy

import lib
from lib import Mesh, gl, part, count
from parts import referents, tray as T

BOARD_X = (-0.135, 0.135)
BOARD_Z = 0.005           # standoff height under the superchip boards
LIFT = 0.06               # cold plate lift at step 2
LID_LIFT = 0.12

REQUIRED = ['tray', 'tray-lid', 'superchip-a', 'superchip-b', 'cold-plate', 'cold-plate-b', 'nic', 'dpu', 'ssd-bank',
            'tray-fans', 'power-contact', 'quick-disconnect', 'nvlink-connector', 'tray-supply', 'tray-return',
            'tray-power', 'tray-data', 'id-card']

BLOCK = (0.12, 0.30, 0.016)   # small distribution block between the rear quick disconnects and the plates
BLOCK_SIZE = (0.07, 0.03, 0.02)


def flow(name, routes, mat, radius, flowkind, carrier, **extras):
    m = Mesh()
    ends = []
    for pts in routes:
        swept = m.tube(pts, radius, mat, seg=8, bend=0.012)
        ends += list(swept[0]) + list(swept[-1])
    o = m.finish(name, ao=False)
    mid = routes[0][len(routes[0]) // 2]
    part(o, name, 'illustrative', manifest='compute tray envelope', anchor=tuple(mid))
    o['flow'] = flowkind
    o['carrier'] = carrier
    o['ends'] = ends
    for k, v in extras.items():
        o[k] = v
    return o


def build():
    lib.reset()
    m = Mesh()
    T.chassis(m, lid=False)
    T.front(m, 'compute')
    tray = m.finish('tray')
    part(tray, 'tray', 'illustrative', manifest='compute tray envelope', anchor=(-T.TW / 2, -0.2, T.TH))

    m = Mesh()
    m.box((T.TW - 0.012, T.TD - 0.004, T.WALL), (0, 0, T.TH - T.WALL / 2), 'sheet-dark', bevel=0.0006)
    lid = m.finish('tray-lid')
    part(lid, 'tray-lid', 'illustrative', manifest='compute tray envelope', anchor=(0, 0, T.TH),
         explode=gl((0, 0, LID_LIFT)), explodeStep=1, visibleSteps=[0, 1])

    # rear blind-mate field as three parts
    for pid, which in (('power-contact', 'power'), ('quick-disconnect', 'liquid'), ('nvlink-connector', 'nvlink')):
        mm = Mesh()
        T.rear(mm, 'compute', (which,))
        if pid == 'power-contact':  # power distribution board behind the clip
            mm.box((0.12, 0.12, 0.0024), (0.21, 0.34, 0.006), 'pcb')
            for k in range(6):
                mm.box((0.012, 0.012, 0.009), (0.165 + (k % 3) * 0.03, 0.31 + (k // 3) * 0.05, 0.0117), 'sheet-dark')
            mm.box((0.022, 0.04, 0.02), (T.BUS_X, 0.395, 0.017), 'copper')
        o = mm.finish(pid)
        x = {'power-contact': T.BUS_X, 'quick-disconnect': T.QD_SUPPLY_X, 'nvlink-connector': T.NVL_X[1]}[pid]
        part(o, pid, 'illustrative', manifest='compute tray envelope', anchor=(x, T.REAR + T.MATE, T.TH))

    # distribution block (context part, joined)
    mm = Mesh()
    mm.box(BLOCK_SIZE, BLOCK, 'steel-bare', bevel=0.002)
    mm.box((0.02, 0.02, BLOCK[2] - BLOCK_SIZE[2] / 2), (BLOCK[0], BLOCK[1], (BLOCK[2] - BLOCK_SIZE[2] / 2) / 2), 'steel-bare')
    blk = mm.finish('tray-distribution')
    blk['tier'] = 'illustrative'

    # superchips and their plate assemblies
    sc = T.superchip()
    board = sc.finish('superchip-a')
    plate_ports = {}
    for i, x in enumerate(BOARD_X):
        pid = 'superchip-' + 'ab'[i]
        if i == 0:
            o = board
        else:
            o = bpy.data.objects.new(pid, board.data)
            bpy.context.scene.collection.objects.link(o)
        o.location = (x, 0, BOARD_Z)
        extras = {'next': True} if i == 0 else {}
        o['kind'] = 'superchip'
        part(o, pid, 'vendor', manifest='superchip', anchor=(0.06, -0.13, 0.008), **extras)
        cp, ports = T.cold_plate(cut=(i == 0))
        c = cp.finish('cold-plate' if i == 0 else 'cold-plate-b')
        c.location = (x, 0, BOARD_Z)
        part(c, 'cold-plate' if i == 0 else 'cold-plate-b', 'illustrative', manifest='compute tray envelope',
             anchor=(-0.062, 0.085, T.PLATE_Z + T.PLATE_T), explode=gl((0, 0, LIFT)), explodeStep=2)
        plate_ports[i] = {k: (x + v[0], v[1], BOARD_Z + v[2]) for k, v in ports.items()}
    # a standoff under every board corner so the boards visibly sit on the pan
    mm = Mesh()
    for x in BOARD_X:
        for sx in (-1, 1):
            for sy in (-1, 1):
                mm.cyl(0.004, BOARD_Z - T.WALL, (x + sx * 0.115, sy * 0.21, T.WALL + (BOARD_Z - T.WALL) / 2), 'steel-bare', seg=6)
    mm.finish('tray-standoffs', ao=False)['tier'] = 'illustrative'

    # NICs, DPUs, drives and fans behind the front face
    mm = Mesh()
    for k in range(count('nicsPerTray')):
        x = 0.035 + k * 0.034
        mm.box((0.026, 0.11, 0.0016), (x, T.FRONT + 0.065, 0.012), 'pcb')
        mm.box((0.022, 0.05, 0.012), (x, T.FRONT + 0.07, 0.019), 'aluminium', bevel=0.001)
        mm.box((0.0235, 0.04, 0.0145), (x, T.FRONT + 0.02, T.TH * 0.55), 'steel-bare')
    nic = mm.finish('nic')
    part(nic, 'nic', 'vendor', manifest='tray', anchor=(0.086, T.FRONT - 0.012, T.TH * 0.75), count=count('nicsPerTray'))
    mm = Mesh()
    for k in range(count('dpusPerTray')):
        x = -0.155 + k * 0.05
        mm.box((0.044, 0.15, 0.0016), (x, T.FRONT + 0.08, 0.008), 'pcb')
        mm.box((0.036, 0.06, 0.014), (x, T.FRONT + 0.09, 0.016), 'aluminium', bevel=0.001)
    dpu = mm.finish('dpu')
    part(dpu, 'dpu', 'vendor', manifest='tray storage and DPUs', anchor=(-0.13, T.FRONT, T.TH), count=count('dpusPerTray'))
    mm = Mesh()
    for k in range(count('e1sDrivesPerTray')):
        mm.box((0.0095, 0.11, 0.0315), (-0.228 + k * 0.0115, T.FRONT + 0.06, 0.0175), 'aluminium', bevel=0.0006)
    mm.box((0.06, 0.008, 0.036), (-0.21, T.FRONT + 0.12, 0.019), 'pcb')  # backplane
    ssd = mm.finish('ssd-bank')
    part(ssd, 'ssd-bank', 'vendor', manifest='tray storage and DPUs', anchor=(-0.21, T.FRONT, T.TH),
         count=count('e1sDrivesPerTray'))
    mm = Mesh()
    nf = 6
    for k in range(nf):  # 40 mm fans for the air-cooled share (count and size illustrative)
        x = -0.24 + k * 0.096
        mm.box((0.04, 0.028, 0.038), (x, -0.27, 0.0205), 'sheet-dark', bevel=0.002)
        mm.cyl(0.0185, 0.03, (x, -0.27, 0.0205), 'hose', axis='Y', seg=14)
        mm.cyl(0.008, 0.032, (x, -0.27, 0.0205), 'steel-painted', axis='Y', seg=10)
    fans = mm.finish('tray-fans')
    part(fans, 'tray-fans', 'illustrative', manifest='compute tray envelope', anchor=(0, -0.27, 0.04), count=nf)

    # coolant: rear quick disconnects -> distribution block -> plate barbs and back (physical routes, no mid-air ends)
    bx, by, bz = BLOCK
    front_y = by - BLOCK_SIZE[1] / 2
    qd_in = T.REAR - 0.008
    flow('tray-supply', [[(T.QD_SUPPLY_X, qd_in, T.QD_Z), (T.QD_SUPPLY_X, 0.36, T.QD_Z), (bx - 0.02, 0.36, bz), (bx - 0.02, by + BLOCK_SIZE[1] / 2, bz)]],
         'hose', 0.0045, 'cool', 'hose')
    flow('tray-return', [[(bx + 0.02, by + BLOCK_SIZE[1] / 2, bz), (bx + 0.02, 0.36, bz), (T.QD_RETURN_X, 0.36, T.QD_Z), (T.QD_RETURN_X, qd_in, T.QD_Z)]],
         'hose', 0.0045, 'hot', 'hose')
    for variant, lift, steps in (('down', 0.0, [0, 1]), ('up', LIFT, [2])):
        sup, ret = [], []
        for i in (0, 1):
            pin = plate_ports[i]['in']
            pout = plate_ports[i]['out']
            for (p, route_x, lst, off) in ((pin, bx - 0.025, sup, -0.012), (pout, bx + 0.025, ret, 0.012)):
                end = (p[0], p[1], p[2] + lift)
                start = (route_x + off * i, front_y, bz)
                lst.append([start, (start[0], 0.22, bz + 0.012 + lift * 0.5), (end[0], 0.2, end[2] + 0.006), (end[0], end[1] + 0.012, end[2]), end])
        flow('hoses-supply-' + variant, sup, 'hose', 0.0035, 'cool', 'hose', visibleSteps=steps)
        flow('hoses-return-' + variant, ret, 'hose', 0.0035, 'hot', 'hose', visibleSteps=steps)
    # power: distribution board to each superchip input connector
    flow('tray-power', [[(0.17, 0.30, 0.012), (0.17, 0.25, 0.014), (BOARD_X[i] + 0.08, 0.24, 0.014), (BOARD_X[i] + 0.08, 0.206, BOARD_Z + 0.0064)]
                        for i in (0, 1)], 'cable', 0.003, 'power', 'cable')
    # data: GPU side of each board to the rear NVLink connector blocks
    routes = []
    for i, x in enumerate(BOARD_X):
        for k, cx in enumerate(T.NVL_X[i * 2:i * 2 + 2]):
            start = (x + (-0.06 + 0.12 * k), 0.22, BOARD_Z + 0.004)
            routes.append([start, (start[0], 0.27, 0.012 + 0.004 * k), (cx, 0.36, 0.012 + 0.004 * k), (cx, T.REAR - 0.002, 0.012 + 0.004 * k)])
    flow('tray-data', routes, 'cable', 0.0028, 'data', 'cable')

    card = referents.id_card().finish('id-card', ao=False)
    card.location = (T.TW / 2 + 0.07, T.FRONT + 0.04, 0)
    part(card, 'id-card', 'derived', manifest='ID-1 card referent', anchor=(0, 0, 0.002))

    scn = bpy.context.scene
    scn['metresPerUnit'] = 1.0
    scn['stop'] = 4
    scn['scaleBar'] = {'length': 0.1, 'part': 'tray', 'axis': 'x'}
    spec = dict(stop=4, required=REQUIRED, counts={'superchip': count('superchipsPerTray')},
                bounds={'id-card': ('id1Card', 'xzy'), 'tray': ('trayEnvelope', 'x')},
                budget={'uniqueTriangles': 80000, 'drawCalls': 150})
    return spec
