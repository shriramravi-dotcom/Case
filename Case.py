# ── SAFE AUTO-INSTALL (ONLY AT TOP) ──────────────────────────────────────────
import sys, subprocess

for _pkg in ["build123d", "numpy"]:
    try:
        __import__(_pkg.replace("-", "_"))
    except ImportError:
        print(f"[setup] installing {_pkg}…")
        subprocess.check_call([sys.executable, "-m", "pip", "install", _pkg])

# ── IMPORTS ─────────────────────────────────────────────────────────────────
import os, struct
import numpy as np

from build123d import *

# ─────────────────────────────────────────────────────────────────────────────
# PARAMETERS
# ─────────────────────────────────────────────────────────────────────────────

OUTER_W = 325.75
OUTER_D = 126.00
OUTER_H = 22.10
CORNER_R = 3.07

WALL_L = 3.00
WALL_R = 7.00
WALL_F = 5.00
WALL_B = 5.00

BOT_H  = 15.60
TRAY_H = 6.50

TRAY_X1 = 20.00
TRAY_X2 = 305.75
TRAY_Y1 = 15.33
TRAY_Y2 = 110.56

# ✅ FIXED (no garbage inside list)
SCREW_XY = [
    (9.00, 6.50),
    (9.00, 119.50),
    (93.00, 6.50),
    (93.00, 119.50),
    (220.75, 6.50),
    (220.75, 119.50),
    (310.75, 6.50),
    (310.75, 119.50),
]

BOSS_R_OUT = 4.30
BOSS_R_IN  = 1.80
BOSS_H     = 5.00

POST_R = 1.86
POST_H = 3.00

POST_XY = [
    (43.79, 10.06),
    (43.79, 115.91),
    (162.84, 10.06),
    (162.84, 115.91),
    (277.16, 10.06),
    (277.16, 115.91),
]

LEDGE_X1, LEDGE_X2 = 3.00, 18.00
LEDGE_Y1, LEDGE_Y2 = 28.00, 113.00
LEDGE_TOP_Z = 21.10

SHELF_X1, SHELF_X2 = 209.50, 249.60
SHELF_Y1, SHELF_Y2 = 15.30, 34.36
SHELF_RISE = 3.50

NOTCH_Y_CEN = 95.50
NOTCH_W = 10.55
NOTCH_DEPTH = 2.00
NOTCH_H = 7.00
NOTCH_Z_BOT = 3.96

# ─────────────────────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────────────────────
def C(x, y):
    return (x - OUTER_W / 2, y - OUTER_D / 2)

# ─────────────────────────────────────────────────────────────────────────────
# BUILD
# ─────────────────────────────────────────────────────────────────────────────
print("\n[build] Constructing case...")

INNER_W = OUTER_W - WALL_L - WALL_R
INNER_D = OUTER_D - WALL_F - WALL_B

INNER_CX = WALL_L + INNER_W / 2
INNER_CY = WALL_F + INNER_D / 2

TRAY_W = TRAY_X2 - TRAY_X1
TRAY_D = TRAY_Y2 - TRAY_Y1
TRAY_CX = (TRAY_X1 + TRAY_X2) / 2
TRAY_CY = (TRAY_Y1 + TRAY_Y2) / 2

with BuildPart() as case:

    # Outer body
    with BuildSketch(Plane.XY):
        RectangleRounded(OUTER_W, OUTER_D, CORNER_R)
    extrude(amount=OUTER_H)

    # Hollow inner
    with BuildSketch(Plane.XY):
        with Locations(C(INNER_CX, INNER_CY)):
            Rectangle(INNER_W, INNER_D)
    extrude(amount=OUTER_H, mode=Mode.SUBTRACT)

    # Top tray fill
    with BuildSketch(Plane.XY.offset(BOT_H)):
        with Locations(C(INNER_CX, INNER_CY)):
            Rectangle(INNER_W, INNER_D)
    extrude(amount=TRAY_H, mode=Mode.ADD)

    # Tray cut
    with BuildSketch(Plane.XY.offset(OUTER_H)):
        with Locations(C(TRAY_CX, TRAY_CY)):
            Rectangle(TRAY_W, TRAY_D)
    extrude(amount=-TRAY_H, mode=Mode.SUBTRACT)

    # Ledge
    with BuildSketch(Plane.XY.offset(BOT_H)):
        with Locations(C((LEDGE_X1+LEDGE_X2)/2, (LEDGE_Y1+LEDGE_Y2)/2)):
            Rectangle(LEDGE_X2-LEDGE_X1, LEDGE_Y2-LEDGE_Y1)
    extrude(amount=LEDGE_TOP_Z - BOT_H, mode=Mode.ADD)

    # Shelf
    with BuildSketch(Plane.XY.offset(BOT_H)):
        with Locations(C((SHELF_X1+SHELF_X2)/2, (SHELF_Y1+SHELF_Y2)/2)):
            Rectangle(SHELF_X2-SHELF_X1, SHELF_Y2-SHELF_Y1)
    extrude(amount=SHELF_RISE, mode=Mode.ADD)

    # Posts
    for px, py in POST_XY:
        with BuildSketch(Plane.XY.offset(BOT_H)):
            with Locations(C(px, py)):
                Circle(POST_R)
        extrude(amount=POST_H, mode=Mode.ADD)

    # Screw bosses
    for bx, by in SCREW_XY:
        with BuildSketch(Plane.XY):
            with Locations(C(bx, by)):
                Circle(BOSS_R_OUT)
                Circle(BOSS_R_IN)
        extrude(amount=BOSS_H, mode=Mode.ADD)

    # Notch
    notch_z = NOTCH_Z_BOT + NOTCH_H / 2
    with BuildSketch(Plane.YZ.offset(-OUTER_W / 2)):
        with Locations((NOTCH_Y_CEN - OUTER_D / 2, notch_z)):
            Rectangle(NOTCH_W, NOTCH_H)
    extrude(amount=NOTCH_DEPTH, mode=Mode.SUBTRACT)

print("[build] Done.")

# ─────────────────────────────────────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────────────────────────────────────
GEN_STL = os.path.join(os.path.expanduser("~"), "Desktop", "pheromone_case_generated.stl")
export_stl(case.part, GEN_STL)

print(f"\n✅ STL saved → {GEN_STL}")

# ─────────────────────────────────────────────────────────────────────────────
# VIEWER
# ─────────────────────────────────────────────────────────────────────────────
try:
    from ocp_vscode import show
    show(case.part)
except:
    print("Install viewer: pip install ocp-vscode")
