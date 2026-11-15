"""GB200 superchip board (spec section 4, stop 5) and its low-detail proxy (placed twice in the compute tray, stop 4).

Local frame: metres, origin at the board centre on its underside, front at -Y, Z up. One Grace CPU and two GPU
packages per board are vendor-stated (`superchip` manifest row). The board outline, the package positions and the
power-delivery layout are illustrative (`superchip board`); no vendor drawing is used.
The package positions match the tray's cold plates (tray.cold_plate): CPU at (0, -0.11), GPUs at (-/+0.062, 0.085).
"""
import lib
from lib import Mesh
from parts import gpu_package as G

BW, BT, BD = lib.dim('superchipBoard')
CPU = (0.0, -0.11)
GPU = ((-0.062, 0.085), (0.062, 0.085))
CPU_SUB, CPU_LID = 0.045, 0.034
TOP = G.TOP                          # package tops (cold plate contact), above the board top
CONNECTOR = ((0.08, 0.2), (0.05, 0.012, 0.008))   # input power connector centre (x, y) and size
VRM_X = (-0.115, -0.009, 0.009, 0.115)


def board(m, edge=True):
    m.box((BW, BD, BT), (0, 0, BT / 2), 'pcb', bevel=0.0004)
    if edge:   # inner copper planes showing on the board edge (layer edge, spec)
        for z in (BT * 0.3, BT * 0.55, BT * 0.8):
            for s in (-1, 1):
                m.box((BW + 0.0002, 0.00012, 0.00012), (0, s * BD / 2, z), 'copper')
                m.box((0.00012, BD + 0.0002, 0.00012), (s * BW / 2, 0, z), 'copper')


def cpu(m):
    x, y = CPU
    m.box((CPU_SUB, CPU_SUB, 0.0025), (x, y, BT + 0.00125), 'substrate')
    m.box((CPU_LID, CPU_LID, TOP - 0.0025), (x, y, BT + 0.0025 + (TOP - 0.0025) / 2), 'steel-bare', bevel=0.0005)


def cpu_memory(m):
    """LPDDR5X packages soldered beside the CPU, four per side (placement illustrative)."""
    x, y = CPU
    for s in (-1, 1):
        for k in range(4):
            m.box((0.008, 0.014, 0.0012), (x + s * 0.034, y - 0.025 + k * 0.016, BT + 0.0006), 'dram', bevel=0.0002)


def vrm(m, detail=True):
    """Power delivery: inductor rows either side of each GPU package and along the CPU, power stages beside each
    inductor (hero), bulk capacitors and the input connector."""
    for x in VRM_X:
        for k in range(5):
            y = 0.055 + k * 0.014
            m.box((0.007, 0.007, 0.005), (x, y, BT + 0.0025), 'sheet-dark', bevel=0.0004)
            if detail:
                d = 0.0065 if x < 0 else -0.0065
                if abs(x) > 0.05:
                    m.box((0.004, 0.005, 0.001), (x + d, y, BT + 0.0005), 'silicon')
    for k in range(6):
        x = -0.05 + k * 0.02
        m.box((0.007, 0.007, 0.005), (x, -0.165, BT + 0.0025), 'sheet-dark', bevel=0.0004)
        if detail:
            m.box((0.005, 0.004, 0.001), (x, -0.1565, BT + 0.0005), 'silicon')
    if detail:
        # the rest of the conversion field (hero only): rows above the GPUs, columns beside the CPU, the band below
        # it and two side columns between CPU and GPUs. Positions and counts illustrative.
        cells = [(-0.11 + i * 0.012, y) for y in (0.135, 0.149) for i in range(19)]
        cells += [(s * x, -0.14 + k * 0.014) for s in (-1, 1) for x in (0.05, 0.064) for k in range(5)]
        cells += [(-0.05 + k * 0.02, y) for y in (-0.18, -0.195) for k in range(6)]
        cells += [(s * 0.105, -0.15 + k * 0.014) for s in (-1, 1) for k in range(12)]
        for x, y in cells:
            m.box((0.007, 0.007, 0.005), (x, y, BT + 0.0025), 'sheet-dark', bevel=0.0004)
            m.box((0.004, 0.004, 0.001), (x, y - 0.0062, BT + 0.0005), 'silicon')
        for k in range(4):   # bulk capacitors near the input
            m.cyl(0.004, 0.009, (0.02 - k * 0.011, 0.2, BT + 0.0045), 'steel-bare', seg=12)
    (cx, cy), (w, d, h) = CONNECTOR
    m.box((w, d, h), (cx, cy, BT + h / 2), 'sheet-dark', bevel=0.0006 if detail else 0.0)


def posts(m):
    """Cold plate mounting posts: four per package, just outside each package outline (positions illustrative)."""
    pk = [(CPU[0], CPU[1], CPU_SUB / 2 + 0.004)] + [(x, y, G.SW / 2 + 0.004) for x, y in GPU]
    for x, y, r in pk:
        for s in (-1, 1):
            for t in (-1, 1):
                m.cyl(0.0022, TOP, (x + s * r, y + t * r, BT + TOP / 2), 'steel-bare', seg=10)


def proxy():
    """Low-detail superchip for the tray: board, CPU with memory, two GPU package proxies, VRM rows, connector."""
    m = Mesh(lod='proxy')
    board(m, edge=False)
    cpu(m)
    cpu_memory(m)
    for x, y in GPU:
        G.proxy(m, (x, y, BT))
    vrm(m, detail=False)
    return m
