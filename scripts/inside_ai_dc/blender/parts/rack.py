"""Rack frame, power shelves, management switches and the three rear spines (spec section 4, stop 3).

Local frame: metres, origin at the centre of the rack footprint on the floor, front at -Y, Z up.
Envelope is the ORv3 proxy from the manifest (`rack outer drawing envelope`, illustrative). Shelf faces, spine
mechanics and positions are illustrative (`rack rear spines`, `rack frame layout`).
"""
import lib
from lib import Mesh, count, dim
from parts import tray as T

RW, RH, RD = dim('rackEnvelope')
RU = dim('rackUnit')
BASE = dim('rackBase')
ORDER = lib.REF['rackOrder']['fromTop']
TOP_SLOT = BASE + len(ORDER) * RU          # top of the equipment stack
POST = 0.04
FRONT = -RD / 2
TRAY_Y = FRONT + 0.07 + T.TD / 2           # tray centre: front face 70 mm behind the frame front
SPINE_Y = TRAY_Y + T.REAR + T.MATE         # front face of every rear spine (where tray connectors mate)


def slot_z(i):
    """Floor of slot i (0 = top of stack)."""
    return TOP_SLOT - (i + 1) * RU


def frame(lod='hero'):
    """Posts, top and base frames, casters with levelling feet, far (-X) side panel, top panel.
    Near (+X) side panel and rear door removed (cutaway). Bounds equal the envelope exactly."""
    m = Mesh()
    b = 0.003 if lod == 'hero' else 0.0
    caster_h = 0.05
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (RW / 2 - POST / 2), sy * (RD / 2 - POST / 2)
            m.box((POST, POST, RH - caster_h), (x, y, caster_h + (RH - caster_h) / 2), 'steel-painted', bevel=b)
            cx, cy = sx * (RW / 2 - 0.06), sy * (RD / 2 - 0.08)
            m.cyl(0.024, 0.03, (cx, cy, 0.024), 'sheet-dark', axis='X', seg=12)            # caster wheel
            m.box((0.03, 0.05, 0.022), (cx, cy, caster_h - 0.011), 'steel-bare')            # caster fork
            m.cyl(0.016, 0.006, (cx + sx * -0.05, cy, 0.003), 'sheet-dark', seg=10)         # levelling foot pad
            m.cyl(0.005, caster_h - 0.006, (cx + sx * -0.05, cy, 0.006 + (caster_h - 0.006) / 2), 'steel-bare', seg=6)
    # base frame and top frame rails
    for z, hgt in ((caster_h, BASE - caster_h), (RH - 0.04, 0.04)):
        for sy in (-1, 1):
            m.box((RW - 2 * POST, POST, hgt), (0, sy * (RD / 2 - POST / 2), z + hgt / 2), 'steel-painted', bevel=b)
        for sx in (-1, 1):
            m.box((POST, RD - 2 * POST, hgt), (sx * (RW / 2 - POST / 2), 0, z + hgt / 2), 'steel-painted', bevel=b)
    m.box((RW - 2 * POST, RD - 2 * POST, 0.004), (0, 0, RH - 0.002), 'sheet-dark')            # top panel
    m.box((0.003, RD - 2 * POST, RH - caster_h - 0.08), (-RW / 2 + 0.0015, 0, caster_h + (RH - caster_h) / 2), 'sheet-dark')
    # front and rear mounting rails (equipment hangs from these)
    for y in (FRONT + 0.06, TRAY_Y + T.REAR - 0.02):
        for sx in (-1, 1):
            m.box((0.018, 0.012, TOP_SLOT - BASE + 0.02), (sx * (T.TW / 2 + 0.013), y, BASE + (TOP_SLOT - BASE) / 2), 'steel-bare')
    # rear spine mounting crossbar under the manifolds and bus bar
    m.box((RW - 2 * POST, 0.05, 0.02), (0, SPINE_Y + 0.04, BASE + 0.01), 'steel-painted', bevel=b)
    # cable management tray across the top (illustrative)
    m.box((RW - 2 * POST - 0.02, 0.30, 0.004), (0, 0.2, TOP_SLOT + 0.14), 'steel-bare')
    return m


def shelf_proxy(kind):
    """1RU power shelf (six PSU modules) or management switch, front and rear features only."""
    m = Mesh(lod='proxy')
    T.chassis(m, lid=True)
    y = T.FRONT
    if kind == 'power':
        n = count('psusPerShelf')
        w = (T.TW - 0.02) / n
        for i in range(n):
            x = -T.TW / 2 + 0.01 + w * (i + 0.5)
            m.box((w - 0.003, 0.006, T.TH - 0.004), (x, y - 0.003, T.TH / 2), 'aluminium', bevel=0.001)
            m.box((w * 0.55, 0.003, T.TH * 0.5), (x - w * 0.12, y - 0.0075, T.TH / 2), 'sheet-dark')   # fan grille
            m.box((0.006, 0.012, 0.024), (x + w * 0.36, y - 0.010, T.TH / 2), 'steel-bare')           # handle
        m.box((0.10, T.MATE, 0.034), (T.BUS_X - 0.04, T.REAR + T.MATE / 2, T.TH / 2), 'copper', bevel=0.001)
    else:
        m.box((T.TW - 0.02, 0.004, T.TH - 0.006), (0, y - 0.002, T.TH / 2), 'steel-painted')
        for row in (0, 1):
            m.box((0.30, 0.003, 0.012), (-0.05, y - 0.004, T.TH * (0.3 + 0.4 * row)), 'sheet-dark')
        for i in range(12):
            m.box((0.002, 0.004, 0.032), (-0.2 + i * 0.025, y - 0.005, T.TH / 2), 'steel-bare')
    return m


def busbar():
    """Vertical copper bar pair in a moulded shroud, full equipment height."""
    m = Mesh()
    z0, z1 = BASE, TOP_SLOT + 0.02
    h = z1 - z0
    y = SPINE_Y + 0.012
    for dx in (-0.006, 0.006):
        m.box((0.006, 0.024, h), (T.BUS_X + dx, y, z0 + h / 2), 'copper', bevel=0.0008)
    m.box((0.040, 0.004, h + 0.02), (T.BUS_X, y + 0.016, z0 + h / 2), 'sheet-dark')               # shroud back
    for s in (-1, 1):
        m.box((0.004, 0.032, h + 0.02), (T.BUS_X + s * 0.018, y + 0.002, z0 + h / 2), 'sheet-dark')
    return m


def manifold(x, slots):
    """Vertical liquid manifold with one quick-disconnect port per liquid-cooled tray position."""
    m = Mesh()
    r = 0.022
    yc = SPINE_Y + 0.016 + r
    z0, z1 = BASE + 0.02, RH - 0.004
    m.cyl(r, z1 - z0, (x, yc, z0 + (z1 - z0) / 2), 'pipe-secondary', seg=16)
    m.cyl(r + 0.004, 0.02, (x, yc, z0 + 0.01), 'steel-bare', seg=16)
    for i in slots:
        z = slot_z(i) + T.QD_Z
        stub = yc - r * 0.6 - SPINE_Y
        m.cyl(0.008, stub, (x, SPINE_Y + stub / 2, z), 'pipe-secondary', axis='Y', seg=8)
        m.cyl(0.012, 0.010, (x, SPINE_Y + 0.005, z), 'steel-bare', axis='Y', seg=10)          # female coupling collar
    ends = [x, yc, z0, x, yc, z1]
    return m, ends


def nvlink_spine(compute_slots, switch_slots):
    """Four passive copper cable cartridges: open frame, a receptacle at every tray position, and cable bundles
    running from switch-tray positions to compute-tray positions. Cartridge count and routing are illustrative."""
    m = Mesh()
    z0 = slot_z(max(compute_slots)) - 0.01
    z1 = slot_z(min(compute_slots)) + RU + 0.01
    h = z1 - z0
    depth = 0.18
    for ci, x in enumerate(T.NVL_X):
        w = 0.07
        yc = SPINE_Y + depth / 2
        m.box((0.002, depth, h), (x - w / 2, yc, z0 + h / 2), 'aluminium')
        m.box((0.002, depth, h), (x + w / 2, yc, z0 + h / 2), 'aluminium')
        m.box((w, 0.003, h), (x, SPINE_Y + depth, z0 + h / 2), 'steel-painted')
        for i in compute_slots + switch_slots:
            m.box((w - 0.008, 0.012, 0.03), (x, SPINE_Y + 0.006, slot_z(i) + RU / 2), 'sheet-dark', bevel=0.0008)
        # bundles: each switch position fans out to compute positions above and below
        for k, si in enumerate(switch_slots[::2]):
            zs = slot_z(si) + RU / 2
            for target in (compute_slots[(k * 2 + ci) % 10], compute_slots[10 + (k * 2 + ci) % 8]):
                zt = slot_z(target) + RU / 2
                dx = -0.018 + 0.012 * ((k + ci) % 4)
                yb = SPINE_Y + 0.05 + 0.025 * (k % 4)
                m.tube([(x + dx, SPINE_Y + 0.012, zs), (x + dx, yb, zs), (x + dx, yb, zt), (x + dx, SPINE_Y + 0.012, zt)],
                       0.0045, 'cable', seg=6, bend=0.03)
    return m
