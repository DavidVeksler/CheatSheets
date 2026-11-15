"""Stop 5: GB200 superchip board, true scale in metres.

Lesson: one CPU and two GPU packages share a board, and most of the board area around them is power conversion.
No explode states. The GPU packages are the stop 6 package's low-detail export (gpu_package.proxy).
"""
import bpy

import lib
from lib import Mesh, part
from parts import gpu_package as G, referents, superchip as S

REQUIRED = ['superchip', 'grace-cpu', 'gpu-left', 'gpu-right', 'power-delivery', 'c2c-link', 'c2c-link-two',
            'superchip-cool', 'superchip-power', 'id-card']


def flow(name, routes, radius, flowkind, carrier, mat, anchor, ends=True, **extras):
    m = Mesh()
    pts = []
    for r in routes:
        swept = m.tube(r, radius, mat, seg=8, bend=0.004)
        pts += list(swept[0]) + list(swept[-1])
    o = m.finish(name, ao=False)
    part(o, name, 'illustrative', manifest='superchip board', anchor=anchor, flow=flowkind, carrier=carrier,
         shadow=False, **({'ends': pts} if ends else {}), **extras)
    return o


def build():
    lib.reset()
    bt, top = S.BT, S.BT + S.TOP

    m = Mesh()
    S.board(m)
    S.posts(m)
    board = m.finish('superchip', ao_dist=0.01)
    part(board, 'superchip', 'vendor', manifest='superchip', anchor=(-0.09, -0.19, bt))

    m = Mesh()
    S.cpu(m)
    S.cpu_memory(m)
    cpu = m.finish('grace-cpu', ao_dist=0.008)
    part(cpu, 'grace-cpu', 'vendor', manifest='superchip', anchor=(S.CPU[0], S.CPU[1], top))

    for i, (x, y) in enumerate(S.GPU):
        pid = ('gpu-left', 'gpu-right')[i]
        m = Mesh()
        G.proxy(m, (0, 0, 0))
        if i == 0:
            gpu = m.finish(pid, ao_dist=0.006)
            gpu_mesh = gpu.data
        else:
            m.bm.free()
            gpu = bpy.data.objects.new(pid, gpu_mesh)
            bpy.context.scene.collection.objects.link(gpu)
        gpu.location = (x, y, bt)
        gpu['kind'] = 'gpu-package'
        part(gpu, pid, 'vendor', manifest='superchip', anchor=(0, -0.012, G.TOP), **({'next': True} if i == 0 else {}))

    m = Mesh()
    S.vrm(m)
    vrm = m.finish('power-delivery', ao_dist=0.006)
    part(vrm, 'power-delivery', 'illustrative', manifest='superchip board', anchor=(S.VRM_X[3], 0.083, bt + 0.005))

    # NVLink-C2C: trace bundles on the board surface from the CPU substrate edge to each GPU substrate edge
    cy_edge = S.CPU[1] + S.CPU_SUB / 2
    gy_edge = S.GPU[0][1] - G.SW / 2
    zt = bt + 0.0003
    for pid, s in (('c2c-link', -1), ('c2c-link-two', 1)):
        routes = []
        for k in range(6):
            o = (k - 2.5) * 0.0012
            x0 = s * 0.008 + o
            x1 = S.GPU[1][0] * s + o
            routes.append([(x0, cy_edge - 0.001, zt), (x0, cy_edge + 0.02, zt), (x1, gy_edge - 0.02, zt), (x1, gy_edge + 0.001, zt)])
        mid = routes[3][1:3]
        flow(pid, routes, 0.0003, 'data', 'copper', 'copper',
             anchor=tuple((a + b) / 2 for a, b in zip(*mid)))

    # power: input connector to the VRM rows (copper pour drawn as a strap)
    (cx, cy), (w, d, h) = S.CONNECTOR
    zp = bt + 0.0006
    routes = [[(cx, cy - d / 2 + 0.001, zp), (cx, 0.172, zp), (0.118, 0.172, zp), (0.118, 0.152, zp)],
              [(cx - 0.02, cy - d / 2 + 0.001, zp), (cx - 0.02, 0.178, zp), (-0.118, 0.178, zp), (-0.118, 0.152, zp)]]
    flow('superchip-power', routes, 0.0006, 'power', 'copper', 'copper', anchor=(0.0, 0.178, zp))

    # coolant: cold plate footprints over the packages and the coolant direction (supply in at the left GPU plate,
    # through the CPU plate, out at the right GPU plate; tray.cold_plate)
    m = Mesh()
    zc = top + 0.0015
    for (x, y, pw, pd) in [(S.CPU[0], S.CPU[1], 0.06, 0.06)] + [(gx, gy, 0.078, 0.082) for gx, gy in S.GPU]:
        a, b = pw / 2, pd / 2
        m.tube([(x - a, y - b, zc), (x + a, y - b, zc), (x + a, y + b, zc), (x - a, y + b, zc), (x - a, y - b + 0.0008, zc)],
               0.0008, 'hose', seg=6)
    for path in ([(-0.062, 0.14, zc), (-0.062, 0.05, zc), (-0.02, -0.06, zc)],
                 [(0.02, -0.06, zc), (0.062, 0.05, zc), (0.062, 0.135, zc)]):
        m.tube(path, 0.0012, 'hose', seg=8, bend=0.02)
        tip, prev = path[-1], path[-2]
        d = [t - p for t, p in zip(tip, prev)]
        n = sum(c * c for c in d) ** 0.5
        u = [c / n for c in d]
        from mathutils import Vector
        axis = 'Y' if abs(u[1]) > abs(u[0]) else 'X'
        faces = m.cyl(0.003, 0.008, tuple(t + 0.004 * c for t, c in zip(tip, u)), 'hose', axis=axis, seg=10, radius2=0.0)
        if (axis == 'Y' and u[1] > 0) or (axis == 'X' and u[0] < 0):  # cone tips point -Y (axis Y) or +X (axis X)
            import bmesh
            from mathutils import Matrix
            vs = list({v for f in faces for v in f.verts})
            c = Vector(tuple(t + 0.004 * cc for t, cc in zip(tip, u)))
            bmesh.ops.rotate(m.bm, cent=c, matrix=Matrix.Rotation(3.14159265, 3, 'Z'), verts=vs)
    cool = m.finish('superchip-cool', ao=False)
    part(cool, 'superchip-cool', 'illustrative', manifest='superchip board', anchor=(-0.062, 0.14, zc),
         flow='cool', carrier='hose', shadow=False)

    card = referents.id_card().finish('id-card', ao=False)
    w, t, d = lib.dim('id1Card')
    card.location = (S.BW / 2 + 0.012 + w / 2, -S.BD / 2 + d / 2 + 0.02, 0)
    part(card, 'id-card', 'derived', manifest='ID-1 card referent', anchor=(0, 0, t))

    scn = bpy.context.scene
    scn['metresPerUnit'] = 1.0
    scn['stop'] = 5
    scn['scaleBar'] = {'length': 0.1, 'part': 'superchip', 'axis': 'x'}
    scn['referents'] = ['id-card']
    scn['camera'] = [8.0, 5.5, 2.4]   # long axis across the screen, so the board is larger at 375 px
    spec = dict(stop=5, required=REQUIRED, counts={'gpu-package': lib.REF['page']['superchip']['gpus']},
                bounds={'id-card': ('id1Card', 'xzy'), 'superchip': ('superchipBoard', 'x')},
                budget={'uniqueTriangles': 80000, 'drawCalls': 150}, flowTolerance=0.0015)
    return spec
