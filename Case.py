# ── SAFE AUTO-INSTALL ────────────────────────────────────────────────────────
import sys, subprocess

for _pkg in ["build123d", "numpy"]:
    try:
        __import__(_pkg.replace("-", "_"))
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", _pkg])

# ── IMPORTS ─────────────────────────────────────────────────────────────────
import os
from build123d import *

# ─────────────────────────────────────────────────────────────────────────────
# PARAMETERS
# ─────────────────────────────────────────────────────────────────────────────
OUTER_W, OUTER_D, OUTER_H = 325.75, 126.00, 22.10
CORNER_R = 7

WALL_L, WALL_R, WALL_F, WALL_B = 3.00, 7.00, 5.00, 5.00
BOT_H, TRAY_H = 15.60, 6.50

TRAY_X1, TRAY_X2 = 20.00, 305.75
TRAY_Y1, TRAY_Y2 = 15.33, 110.56

SCREW_XY = [
    (9.00, 6.50),(9.00,119.50),
    (93.00,6.50),(93.00,119.50),
    (220.75,6.50),(220.75,119.50),
    (310.75,6.50),(310.75,119.50)
]

# 🔴 LARGE RIBS
RIB_POINTS_BIG = [
    (93.00,6.50),(93.00,119.50),
    (220.75,6.50),(220.75,119.50),
]

RIB_BIG_W = 60.0
RIB_BIG_D = 12.7
RIB_BIG_HEIGHT = -22.0
RIB_BIG_FILLET = 6.0

# 🔴 LEFT SIDE RIBS
RIB_POINTS_LEFT = [(9.00, 6.50),(9.00,119.50)]
LEFT_RIGHT_WIDTH = 12.0
LEFT_LEFT_WIDTH  = 8.5
LEFT_RIB_D = 12.7
LEFT_RIB_HEIGHT = -22.0
LEFT_RIB_FILLET = 5

# 🔴 RIGHT SIDE RIBS
RIB_POINTS_RIGHT = [(310.75,6.50),(310.75,119.50)]
RIGHT_RIGHT_WIDTH = 12.0
RIGHT_LEFT_WIDTH  = 12.0
RIGHT_RIB_D = 12.7
RIGHT_RIB_HEIGHT = -22.0
RIGHT_RIB_FILLET = 5.0

# BOSSES
BOSS_R_OUT, BOSS_R_IN, BOSS_H = 2.30, 1.80, 17.00

# OTHER FEATURES
POST_R, POST_H = 1.86, 3.00
POST_XY = [
    (43.79,10.06),(43.79,115.91),
    (162.84,10.06),(162.84,115.91),
    (277.16,10.06),(277.16,115.91)
]

LEDGE_X1, LEDGE_X2 = 3.00, 18.00
LEDGE_Y1, LEDGE_Y2 = 28.00, 113.00
LEDGE_TOP_Z = 21.10

SHELF_X1, SHELF_X2 = 209.50, 249.60
SHELF_Y1, SHELF_Y2 = 15.30, 34.36
SHELF_RISE = 3.50
SHELF_CUT_MARGIN = 3.0

NOTCH_Y_CEN, NOTCH_W = 95.50, 10.55
NOTCH_DEPTH, NOTCH_H, NOTCH_Z_BOT = 5.00, 7.00, 3.96

def C(x, y):
    return (x - OUTER_W/2, y - OUTER_D/2)

# ─────────────────────────────────────────────────────────────────────────────
# BUILD
# ─────────────────────────────────────────────────────────────────────────────
print("\n[build] Constructing case...")

INNER_W = OUTER_W - WALL_L - WALL_R
INNER_D = OUTER_D - WALL_F - WALL_B

INNER_CX = WALL_L + INNER_W/2
INNER_CY = WALL_F + INNER_D/2

TRAY_W = TRAY_X2 - TRAY_X1
TRAY_D = TRAY_Y2 - TRAY_Y1
TRAY_CX = (TRAY_X1 + TRAY_X2)/2
TRAY_CY = (TRAY_Y1 + TRAY_Y2)/2

with BuildPart() as case:

    with BuildSketch(Plane.XY):
        RectangleRounded(OUTER_W, OUTER_D, CORNER_R)
    extrude(amount=OUTER_H)

    with BuildSketch(Plane.XY):
        with Locations(C(INNER_CX, INNER_CY)):
            Rectangle(INNER_W, INNER_D)
    extrude(amount=OUTER_H, mode=Mode.SUBTRACT)

    with BuildSketch(Plane.XY.offset(BOT_H)):
        with Locations(C(INNER_CX, INNER_CY)):
            Rectangle(INNER_W, INNER_D)
    extrude(amount=TRAY_H, mode=Mode.ADD)

    with BuildSketch(Plane.XY.offset(OUTER_H)):
        with Locations(C(TRAY_CX, TRAY_CY)):
            Rectangle(TRAY_W, TRAY_D)
    extrude(amount=-TRAY_H, mode=Mode.SUBTRACT)

    with BuildSketch(Plane.XY.offset(BOT_H)):
        with Locations(C((LEDGE_X1+LEDGE_X2)/2, (LEDGE_Y1+LEDGE_Y2)/2)):
            Rectangle(LEDGE_X2-LEDGE_X1, LEDGE_Y2-LEDGE_Y1)
    extrude(amount=LEDGE_TOP_Z - BOT_H, mode=Mode.ADD)

    # Shelf
    shelf_w = SHELF_X2 - SHELF_X1
    shelf_d = SHELF_Y2 - SHELF_Y1
    shelf_cx = (SHELF_X1 + SHELF_X2)/2
    shelf_cy = (SHELF_Y1 + SHELF_Y2)/2

    with BuildSketch(Plane.XY.offset(OUTER_H)):
        with Locations(C(shelf_cx, shelf_cy)):
            Rectangle(shelf_w, shelf_d)
    extrude(amount=-SHELF_RISE, mode=Mode.ADD)

    with BuildSketch(Plane.XY.offset(OUTER_H)):
        with Locations(C(shelf_cx, shelf_cy)):
            Rectangle(shelf_w - 2*SHELF_CUT_MARGIN, shelf_d - 2*SHELF_CUT_MARGIN)
    extrude(amount=-SHELF_RISE, mode=Mode.SUBTRACT)

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

    # Ribs
    RIB_Z = BOT_H + TRAY_H

    for rx, ry in RIB_POINTS_BIG:
        with BuildSketch(Plane.XY.offset(RIB_Z)):
            with Locations(C(rx, ry)):
                RectangleRounded(RIB_BIG_W, RIB_BIG_D, RIB_BIG_FILLET)
        extrude(amount=RIB_BIG_HEIGHT, mode=Mode.ADD)

    for rx, ry in RIB_POINTS_LEFT:
        total_w = LEFT_LEFT_WIDTH + LEFT_RIGHT_WIDTH
        shift_x = (LEFT_RIGHT_WIDTH - LEFT_LEFT_WIDTH) / 2
        with BuildSketch(Plane.XY.offset(RIB_Z)):
            with Locations(C(rx + shift_x, ry)):
                RectangleRounded(total_w, LEFT_RIB_D, LEFT_RIB_FILLET)
        extrude(amount=LEFT_RIB_HEIGHT, mode=Mode.ADD)

    for rx, ry in RIB_POINTS_RIGHT:
        total_w = RIGHT_LEFT_WIDTH + RIGHT_RIGHT_WIDTH
        shift_x = (RIGHT_RIGHT_WIDTH - RIGHT_LEFT_WIDTH) / 2
        with BuildSketch(Plane.XY.offset(RIB_Z)):
            with Locations(C(rx + shift_x, ry)):
                RectangleRounded(total_w, RIGHT_RIB_D, RIGHT_RIB_FILLET)
        extrude(amount=RIGHT_RIB_HEIGHT, mode=Mode.ADD)

    # Existing half cuts
    HOLE_DEPTH = abs(RIB_BIG_HEIGHT) / 2

    for bx, by in SCREW_XY:
        with BuildSketch(Plane.XY):
            with Locations(C(bx, by)):
                Circle(BOSS_R_IN)
        extrude(amount=HOLE_DEPTH, mode=Mode.SUBTRACT)

    # 🔥 MID CIRCLES (BOTTOM)
    bottom_x = [9.00, 93.00, 220.75, 310.75]

    mid_x = [
        (bottom_x[0] + bottom_x[1]) / 2,
        (bottom_x[1] + bottom_x[2]) / 2,
        (bottom_x[2] + bottom_x[3]) / 2,
    ]

    MID_Z = BOT_H / 2

    for i, mx in enumerate(mid_x):
        y_pos = 6.50 + 3.0
        if i == 0:
            mx -= 8.0

        with BuildSketch(Plane.XY.offset(MID_Z)):
            with Locations(C(mx, y_pos)):
                Circle(BOSS_R_IN)
        extrude(amount=HOLE_DEPTH, mode=Mode.SUBTRACT)

    # 🔥 MIRRORED MID CIRCLES (TOP) ✅ ADDED ONLY
    for i, mx in enumerate(mid_x):
        y_pos = 119.50 - 3.0
        if i == 0:
            mx -= 8.0

        with BuildSketch(Plane.XY.offset(MID_Z)):
            with Locations(C(mx, y_pos)):
                Circle(BOSS_R_IN)
        extrude(amount=HOLE_DEPTH, mode=Mode.SUBTRACT)

    # Notch
    notch_z = NOTCH_Z_BOT + NOTCH_H/2
    with BuildSketch(Plane.YZ.offset(-OUTER_W/2)):
        with Locations((NOTCH_Y_CEN - OUTER_D/2, notch_z)):
            SlotOverall(NOTCH_W, NOTCH_H)
    extrude(amount=NOTCH_DEPTH, mode=Mode.SUBTRACT)

print("[build] Done.")

# EXPORT
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
GEN_STL = os.path.join(desktop, "generated_case.stl")

export_stl(case.part, GEN_STL)
print(f"\n✅ Generated STL → {GEN_STL}")

# VIEWER
try:
    from ocp_vscode import show
    show(case.part, reset_camera=True)
except:
    print("Install viewer: pip install ocp-vscode")
