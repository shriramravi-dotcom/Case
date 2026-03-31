from build123d import *
import numpy as np
import os, struct

# ─────────────────────────────────────────────────────────────────────────────
# PARAMETERS
# ─────────────────────────────────────────────────────────────────────────────
OUTER_W, OUTER_D, OUTER_H = 325.75, 126.00, 22.10
CORNER_R = 3.07

# Walls & Floor Logic
WALL_L, WALL_R, WALL_F, WALL_B = 3.00, 7.00, 5.00, 5.00
CAVITY_DEPTH = 6.50
FLOOR_Z = OUTER_H - CAVITY_DEPTH 

# Features
SCREW_HOLE_R, SCREW_HOLE_DEPTH = 1.80, 5.00
SCREW_XY = [
    (9.00, 6.50), (9.00, 119.50), (93.00, 6.50), (93.00, 119.50),
    (220.75, 6.50), (220.75, 119.50), (310.75, 6.50), (310.75, 119.50),
]

POST_R, POST_H = 1.86, 3.00
POST_XY = [
    (43.79, 10.06), (43.79, 115.91), (162.84, 10.06), 
    (162.84, 115.91), (277.16, 10.06), (277.16, 115.91),
]

# Ledge & Shelf
LEDGE_X_DEPTH, LEDGE_Y_START, LEDGE_Y_END = 15.00, 28.00, 113.00
SHELF_X_START, SHELF_X_END, SHELF_Y_START, SHELF_Y_END, SHELF_H = 209.50, 249.60, 15.30, 34.35, 3.50

# Side Notch
NOTCH_W, NOTCH_Y_CENTER, NOTCH_DEPTH = 10.55, 95.24, 2.00
NOTCH_H, NOTCH_Z_BOT = 7.00, 3.96

# ─────────────────────────────────────────────────────────────────────────────
# VOLUME UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def calculate_stl_file_volume(filepath):
    """Calculates volume directly from an STL file on disk."""
    if not os.path.exists(filepath): return 0.0
    with open(filepath, 'rb') as f:
        f.read(80) # Header
        num_tri = struct.unpack('<I', f.read(4))[0]
        vol = 0.0
        for _ in range(num_tri):
            f.read(12) # Normal
            v1 = np.array(struct.unpack('<fff', f.read(12)))
            v2 = np.array(struct.unpack('<fff', f.read(12)))
            v3 = np.array(struct.unpack('<fff', f.read(12)))
            f.read(2) # Attribute byte count
            vol += np.dot(v1, np.cross(v2, v3)) / 6.0
    return abs(vol)

def calculate_part_volume(part_obj):
    """Exports a build123d part to a temp STL and returns volume."""
    temp_path = "temp_gen.stl"
    export_stl(part_obj, temp_path)
    vol = calculate_stl_file_volume(temp_path)
    if os.path.exists(temp_path): os.remove(temp_path)
    return vol

# ─────────────────────────────────────────────────────────────────────────────
# BUILD GEOMETRY
# ─────────────────────────────────────────────────────────────────────────────

with BuildPart() as case:
    # 1. Base Block
    with BuildSketch():
        RectangleRounded(OUTER_W, OUTER_D, CORNER_R)
    extrude(amount=OUTER_H)

    # 2. Interior Cavity (Asymmetric subtraction)
    inner_w = OUTER_W - WALL_L - WALL_R
    inner_d = OUTER_D - WALL_F - WALL_B
    off_x = (WALL_L - WALL_R) / 2
    off_y = (WALL_F - WALL_B) / 2
    
    with BuildSketch(case.faces().sort_by(Axis.Z)[-1]) as cav_sk:
        with Locations((off_x, off_y)):
            Rectangle(inner_w, inner_d)
    extrude(amount=-CAVITY_DEPTH, mode=Mode.SUBTRACT)

    # 3. Features on the Floor (Ledge, Shelf, Posts)
    # We work on the Floor plane (Z = FLOOR_Z)
    floor_plane = Plane.XY.offset(FLOOR_Z)

    # Ledge
    ledge_w = LEDGE_X_DEPTH
    ledge_d = LEDGE_Y_END - LEDGE_Y_START
    ledge_cx = WALL_L + ledge_w/2 - OUTER_W/2
    ledge_cy = (LEDGE_Y_START + LEDGE_Y_END)/2 - OUTER_D/2
    with BuildSketch(floor_plane):
        with Locations((ledge_cx, ledge_cy)):
            Rectangle(ledge_w, ledge_d)
    extrude(amount=1.0, mode=Mode.ADD)

    # Shelf
    shelf_w = SHELF_X_END - SHELF_X_START
    shelf_d = SHELF_Y_END - SHELF_Y_START
    shelf_cx = (SHELF_X_START + SHELF_X_END)/2 - OUTER_W/2
    shelf_cy = (SHELF_Y_START + SHELF_Y_END)/2 - OUTER_D/2
    with BuildSketch(floor_plane):
        with Locations((shelf_cx, shelf_cy)):
            Rectangle(shelf_w, shelf_d)
    extrude(amount=SHELF_H, mode=Mode.ADD)

    # Posts
    with BuildSketch(floor_plane):
        for px, py in POST_XY:
            with Locations((px - OUTER_W/2, py - OUTER_D/2)):
                Circle(POST_R)
    extrude(amount=POST_H, mode=Mode.ADD)

    # 4. Screw Holes (From Bottom)
    with BuildSketch(case.faces().sort_by(Axis.Z)[0]):
        for hx, hy in SCREW_XY:
            with Locations((hx - OUTER_W/2, hy - OUTER_D/2)):
                Circle(SCREW_HOLE_R)
    extrude(amount=SCREW_HOLE_DEPTH, mode=Mode.SUBTRACT)

    # 5. Side Notch (YZ Plane)
    with BuildSketch(Plane.YZ.offset(-OUTER_W/2)):
        with Locations((NOTCH_Y_CENTER - OUTER_D/2, NOTCH_Z_BOT + NOTCH_H/2)):
            Rectangle(NOTCH_W, NOTCH_H)
    extrude(amount=NOTCH_DEPTH, mode=Mode.SUBTRACT)

# ─────────────────────────────────────────────────────────────────────────────
# REPORT & EXPORT
# ─────────────────────────────────────────────────────────────────────────────

REF_STL_PATH = "/Users/softage/Downloads/case.stl"
gen_vol = calculate_part_volume(case.part)

print("\n=== FINAL OPTIMIZED REPORT ===")
print(f"Generated Volume : {gen_vol:.2f} mm³")

if os.path.exists(REF_STL_PATH):
    ref_vol = calculate_stl_file_volume(REF_STL_PATH)
    diff = abs(gen_vol - ref_vol)
    pct = (diff / ref_vol) * 100 if ref_vol > 0 else 0
    print(f"Reference Volume : {ref_vol:.2f} mm³")
    print(f"Difference       : {diff:.2f} ({pct:.4f}%)")
else:
    print(f"⚠️ Reference STL not found at: {REF_STL_PATH}")

FINAL_NAME = "optimized_pheromone_case.stl"
export_stl(case.part, FINAL_NAME)
print(f"✅ Saved to {FINAL_NAME}")

try:
    from ocp_vscode import show
    show(case.part)
except:
    pass