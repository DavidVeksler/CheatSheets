"""1RU compute tray and NVLink switch tray (spec section 4, stops 3 and 4).

Local frame: metres, origin at the centre of the tray footprint on its floor plane, front at -Y, Z up.
The proxy (in the rack) and the hero (stop 4) share chassis(), front() and rear(), so the tray the reader clicks in
the rack is the same object as the tray they arrive at. Everything except counts is illustrative
(manifest row `compute tray envelope`): no vendor drawing is used, and no bezel styling, logo or text is copied.
"""
import math

import lib
from lib import Mesh, count, dim

TW, TH, TD = lib.dim('trayEnvelope')
FRONT = -TD / 2
REAR = TD / 2
MATE = 0.022          # rear connector reach behind the chassis; the rack spines' front faces sit at REAR + MATE
WALL = 0.0015         # sheet thickness (drawn)

# Rear connector positions (x), shared with the rack spines in rack.py.
NVL_X = (-0.24, -0.16, -0.08, 0.0)
QD_SUPPLY_X, QD_RETURN_X = 0.09, 0.15
QD_Z = 0.022
BUS_X = 0.242


def chassis(m, lid=False):
    """Sheet-metal pan: floor, side walls, slide rails (outermost, so the rails define the 0.56 m width), rear wall.
    The lid is a separate part (hero) or omitted."""
    inner = TW - 0.008
    m.box((inner, TD, WALL), (0, 0, WALL / 2), 'sheet-dark', bevel=0.0006)
    for s in (-1, 1):
        m.box((WALL, TD, TH - 0.002), (s * (inner / 2 - WALL / 2), 0, (TH - 0.002) / 2), 'sheet-dark')
        m.box((0.004, TD - 0.02, 0.006), (s * (TW / 2 - 0.002), 0.0, TH * 0.5), 'steel-bare')  # slide rail
    m.box((inner, WALL, TH - 0.004), (0, REAR - WALL / 2, (TH - 0.004) / 2), 'sheet-dark')
    if lid:
        m.box((inner, TD, WALL), (0, 0, TH - WALL / 2), 'sheet-dark', bevel=0.0006)


def front(m, kind='compute'):
    """Front service face. Compute: ejector handles, four E1.S bays, two DPU brackets, four OSFP NIC cages.
    Switch: plain perforated face with management ports. Positions are illustrative."""
    y = FRONT + WALL / 2
    m.box((TW - 0.008, WALL, TH - 0.002), (0, y, (TH - 0.002) / 2), 'sheet-dark', bevel=0.0005)
    for s in (-1, 1):  # ejector handles: lever plus pivot block
        x = s * (TW / 2 - 0.016)
        m.box((0.010, 0.012, 0.032), (x, FRONT - 0.006, TH / 2), 'steel-bare', bevel=0.0015)
        m.box((0.016, 0.004, 0.008), (x - s * 0.006, FRONT - 0.002, TH * 0.82), 'steel-bare')
    if kind == 'compute':
        for i in range(count('e1sDrivesPerTray')):  # E1.S drive carriers stand vertically in 1RU
            m.box((0.0095, 0.006, 0.034), (-0.228 + i * 0.0115, FRONT - 0.003, TH / 2), 'aluminium', bevel=0.0008)
        for i in range(count('dpusPerTray')):  # DPU brackets, two cages each
            x = -0.155 + i * 0.05
            m.box((0.042, 0.003, 0.034), (x, FRONT - 0.0015, TH / 2), 'steel-bare')
            for k in (-1, 1):
                m.box((0.016, 0.004, 0.011), (x + k * 0.01, FRONT - 0.004, TH / 2), 'sheet-dark')
        for i in range(count('nicsPerTray')):  # OSFP cages
            x = 0.035 + i * 0.034
            m.box((0.0235, 0.008, 0.0145), (x, FRONT - 0.004, TH * 0.55), 'steel-bare', bevel=0.0008)
            m.box((0.018, 0.002, 0.010), (x, FRONT - 0.0085, TH * 0.55), 'sheet-dark')
    else:
        for i in range(10):  # perforation bands read as vents
            m.box((0.018, 0.002, 0.026), (-0.2 + i * 0.026, FRONT - 0.001, TH / 2), 'steel-bare')
        for i in range(2):
            m.box((0.016, 0.006, 0.012), (0.12 + i * 0.022, FRONT - 0.003, TH / 2), 'sheet-dark')


def rear(m, kind='compute', which=('power', 'liquid', 'nvlink')):
    """Rear blind-mate field: busbar clip, two liquid quick disconnects, NVLink connector blocks."""
    y0 = REAR
    if 'power' in which:
        m.box((0.022, MATE, 0.030), (BUS_X, y0 + MATE / 2, TH / 2), 'copper', bevel=0.001)
        m.box((0.030, 0.012, 0.036), (BUS_X, y0 - 0.006, TH / 2), 'sheet-dark')
    if 'liquid' in which:
        for x in (QD_SUPPLY_X, QD_RETURN_X):
            m.cyl(0.009, MATE, (x, y0 + MATE / 2, QD_Z), 'pipe-secondary', axis='Y', seg=10)
            m.cyl(0.0115, 0.008, (x, y0 - 0.004, QD_Z), 'steel-bare', axis='Y', seg=10)
    if 'nvlink' in which:
        w = 0.062 if kind == 'compute' else 0.074
        for x in NVL_X:
            m.box((w, MATE, 0.032), (x, y0 + MATE / 2, TH / 2), 'sheet-dark', bevel=0.0008)
            m.box((w - 0.01, 0.001, 0.020), (x, y0 + MATE + 0.0005, TH / 2), 'copper')


def proxy(kind):
    """Low-detail tray for the rack: chassis, front and rear only (no interior, no lid)."""
    m = Mesh(lod='proxy')
    chassis(m, lid=False)  # open top: the runtime GPU slots sit on the floor pan
    front(m, kind)
    rear(m, kind)
    return m


# ============================================================================ hero (stop 4)

def superchip(lod='proxy'):
    """Simple superchip proxy (stop 5 builds the detailed board later): PCB, Grace package with memory, two GPU
    packages, VRM rows. Local origin = board centre on its underside. Board 0.25 x 0.44 m, illustrative."""
    m = Mesh()
    bw, bd, bt = 0.25, 0.44, 0.0024
    m.box((bw, bd, bt), (0, 0, bt / 2), 'pcb', bevel=0.0004)
    # Grace CPU package with LPDDR5X alongside (illustrative placement)
    m.box((0.045, 0.045, 0.0025), (0, -0.11, bt + 0.00125), 'substrate')
    m.box((0.034, 0.034, 0.002), (0, -0.11, bt + 0.0035), 'steel-bare', bevel=0.0005)
    for s in (-1, 1):
        for k in range(4):
            m.box((0.008, 0.014, 0.0012), (s * 0.034, -0.135 + k * 0.016, bt + 0.0006), 'dram')
    # two GPU packages: substrate, stiffener ring, die area (low detail)
    for x in (-0.062, 0.062):
        m.box((0.07, 0.075, 0.0025), (x, 0.085, bt + 0.00125), 'substrate')
        m.box((0.05, 0.055, 0.0015), (x, 0.085, bt + 0.0033), 'silicon')
        for s in (-1, 1):
            m.box((0.07, 0.004, 0.002), (x, 0.085 + s * 0.0355, bt + 0.0035), 'steel-bare')
    # VRM rows: inductors either side of each package and along the CPU
    for x in (-0.115, -0.009, 0.009, 0.115):
        for k in range(5):
            m.box((0.007, 0.007, 0.005), (x, 0.055 + k * 0.014, bt + 0.0025), 'sheet-dark')
    for k in range(6):
        m.box((0.007, 0.007, 0.005), (-0.05 + k * 0.02, -0.165, bt + 0.0025), 'sheet-dark')
    m.box((0.05, 0.012, 0.008), (0.08, 0.2, bt + 0.004), 'sheet-dark')  # input power connector
    return m


PLATE_Z = 0.0024 + 0.0055   # board top + package height: plate underside
PLATE_T = 0.009             # plate thickness (base + cover), illustrative


def cold_plate(cut=False):
    """Per-superchip plate assembly: one plate over the CPU, one over each GPU package, bridged by short hoses,
    with inlet and outlet barbs at the rear. cut=True removes the cover of one GPU plate to show the fins."""
    m = Mesh()
    ports = {}
    plates = [(0.0, -0.11, 0.06, 0.06), (-0.062, 0.085, 0.078, 0.082), (0.062, 0.085, 0.078, 0.082)]
    for i, (x, y, w, d) in enumerate(plates):
        base = 0.003
        m.box((w, d, base), (x, y, PLATE_Z + base / 2), 'copper', bevel=0.0006)
        if cut and i == 1:
            # cover removed: section faces on the cut walls, microchannel fins exposed
            for s in (-1, 1):
                m.box((w, 0.003, PLATE_T - base), (x, y + s * (d / 2 - 0.0015), PLATE_Z + base + (PLATE_T - base) / 2), 'section')
                m.box((0.003, d - 0.006, PLATE_T - base), (x + s * (w / 2 - 0.0015), y, PLATE_Z + base + (PLATE_T - base) / 2), 'section')
            n = 18
            for k in range(n):
                fx = x - w / 2 + 0.006 + k * (w - 0.012) / (n - 1)
                m.box((0.0008, d - 0.012, PLATE_T - base - 0.001), (fx, y, PLATE_Z + base + (PLATE_T - base - 0.001) / 2), 'copper')
        else:
            m.box((w, d, PLATE_T - base), (x, y, PLATE_Z + base + (PLATE_T - base) / 2), 'aluminium', bevel=0.001)
        for s in (-1, 1):  # captive screws
            for t in (-1, 1):
                m.cyl(0.003, 0.003, (x + s * (w / 2 - 0.006), y + t * (d / 2 - 0.006), PLATE_Z + PLATE_T + 0.0015), 'steel-bare', seg=8)
    top = PLATE_Z + PLATE_T
    # bridge hoses CPU plate -> GPU plates
    m.tube([(0.0, -0.08, top + 0.004), (-0.03, -0.02, top + 0.006), (-0.062, 0.044, top + 0.004)], 0.0045, 'hose', seg=8, bend=0.02)
    m.tube([(0.0, -0.08, top + 0.004), (0.03, -0.02, top + 0.006), (0.062, 0.044, top + 0.004)], 0.0045, 'hose', seg=8, bend=0.02)
    # barbs at the rear edge of each GPU plate: inlet (left), outlet (right)
    for name, x in (('in', -0.062), ('out', 0.062)):
        m.cyl(0.0045, 0.012, (x, 0.126 + 0.006, PLATE_Z + 0.006), 'steel-bare', axis='Y', seg=10)
        ports[name] = (x, 0.126 + 0.012, PLATE_Z + 0.006)
    return m, ports
