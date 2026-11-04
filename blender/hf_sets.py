# hf_sets.py — 3D sets for What-If EP.1 (เตรียมอุดมศึกษาพัฒนาการปทุมธานี)
# School colors: pink + navy. Emblem: พระเกี้ยว (royal crown) simplified.
import math
import bpy
from hf_common import (new_material, add_primitive, wave, reset_scene)

M = math

M = math


def _mats_common():
    mc = {}
    mc["asphalt"] = new_material("Asphalt", (0.10, 0.10, 0.115, 1.0), rough=0.9)
    mc["concrete"] = new_material("Concrete", (0.45, 0.44, 0.43, 1.0), rough=0.85)
    mc["pink"] = new_material("FacadePink", (0.40, 0.12, 0.23, 1.0), rough=0.75)
    mc["pink_dim"] = new_material("FacadePinkDim", (0.24, 0.07, 0.14, 1.0), rough=0.8)
    mc["cream"] = new_material("Cream", (0.32, 0.29, 0.27, 1.0), rough=0.85)
    mc["navy"] = new_material("NavyWall", (0.03, 0.05, 0.11, 1.0), rough=0.8)
    mc["glass"] = new_material("Glass", (0.04, 0.05, 0.09, 1.0), rough=0.15)
    mc["glass_lit"] = new_material("GlassLit", (0.35, 0.22, 0.10, 1.0), rough=0.2,
                                   emission=(1.0, 0.62, 0.25, 1.0), emission_strength=1.1)
    mc["door"] = new_material("Door", (0.12, 0.09, 0.10, 1.0), rough=0.55)
    mc["wood"] = new_material("Wood", (0.35, 0.22, 0.13, 1.0), rough=0.7)
    mc["trunk"] = new_material("Trunk", (0.28, 0.19, 0.14, 1.0), rough=0.9)
    mc["blossom"] = new_material("Blossom", (0.62, 0.28, 0.44, 1.0), rough=0.85,
                                 emission=(0.55, 0.15, 0.32, 1.0), emission_strength=0.12)
    mc["moon"] = new_material("Moon", (1.0, 0.98, 0.85, 1.0), rough=1.0,
                              emission=(1.0, 0.95, 0.8, 1.0), emission_strength=6.0)
    mc["gold"] = new_material("Gold", (0.75, 0.6, 0.25, 1.0), rough=0.35, metallic=0.8)
    return mc


def build_ground(size=60):
    g = add_primitive("plane", "Ground", _mats_common()["asphalt"],
                      loc=(0, 0, 0), scale=(size, size, 1))
    return g


def build_school(mc=None):
    """ตอพปท real look (from school photos): LONG 3-storey pink building,
    blue roof + blue window frames, OPEN corridors with pink railings on
    every floor, grass field + football goal in front, pink/navy sign."""
    mc = mc or _mats_common()
    objs = []
    CX, W, D = 0.0, 22.0, 8.0     # center x, width, depth
    FLOOR_H = 3.2
    y = 11.0                      # facade front plane at y - D/2 = 7.0
    front = y - D / 2

    pink_f = new_material("FacPink", (0.62, 0.20, 0.35, 1.0), rough=0.8)
    blue_r = new_material("RoofBlue", (0.10, 0.15, 0.38, 1.0), rough=0.7)
    blue_f = new_material("FrameBlue", (0.08, 0.13, 0.32, 1.0), rough=0.6)
    grass_m = new_material("FieldGrass", (0.055, 0.10, 0.045, 1.0), rough=0.95)
    white_m = new_material("GoalWhite", (0.70, 0.69, 0.65, 1.0), rough=0.5)

    # ---- field in front: grass + white football goal ----
    objs.append(add_primitive("plane", "FieldGrass", grass_m,
                              loc=(CX, front - 13, 0.005), scale=(28, 15, 1)))
    gy = front - 8.5
    for sx in (-1, 1):
        add_primitive("cylinder", "GoalPost%d" % sx, white_m,
                      loc=(sx * 3.2, gy, 1.0), radius=0.06, depth=2.0)
    add_primitive("cylinder", "GoalBar", white_m,
                  loc=(0, gy, 2.0), rot=(0, M.pi / 2, 0), radius=0.06, depth=6.4)

    # ---- 3 storeys: recessed glass wall + pink piers + open corridor ----
    for f in (1, 2, 3):
        z = f * FLOOR_H
        # corridor slab (cream, juts out front)
        add_primitive("cube", "CorrSlab%d" % f, mc["cream"],
                      loc=(CX, front + 0.45, z - 0.10),
                      scale=(W / 2, 0.7, 0.10))
        # pink railing: solid low wall + cream top rail
        add_primitive("cube", "RailWall%d" % f, pink_f,
                      loc=(CX, front + 1.0, z + 0.40),
                      scale=(W / 2, 0.07, 0.40))
        add_primitive("cube", "RailTop%d" % f, mc["cream"],
                      loc=(CX, front + 1.0, z + 0.63),
                      scale=(W / 2 + 0.05, 0.13, 0.06))
        # windows behind corridor
        wi = 0
        for k in range(12):
            wx = -10.0 + k * (20.0 / 11.0)
            if abs(wx) < 1.9 and f == 1:
                continue  # entrance clearance
            lit = wave(f * 13 + wi, 0.31) > 0.7
            mat = mc["glass_lit"] if lit else mc["glass"]
            add_primitive("cube", "SchoolWin%d_%d" % (f, wi), mat,
                          loc=(wx, front + 0.18, z + 0.85),
                          scale=(0.60, 0.04, 0.60))
            add_primitive("cube", "WinF%d_%d" % (f, wi), blue_f,
                          loc=(wx, front + 0.19, z + 0.85),
                          scale=(0.68, 0.035, 0.68))
            if lit:
                wl = bpy.data.objects.new(
                    "WinLight%d_%d" % (f, wi),
                    bpy.data.lights.new("wll%d_%d" % (f, wi), "POINT"))
                wl.data.energy = 26.0
                wl.data.color = (1.0, 0.65, 0.3)
                wl.location = (wx, front - 0.4, z + 0.85)
                bpy.context.collection.objects.link(wl)
            wi += 1
        # pink piers between windows
        for pi, px in enumerate((-10.8, -7.2, -3.6, 0.0, 3.6, 7.2, 10.8)):
            add_primitive("cube", "Pier%d_%d" % (f, pi), pink_f,
                          loc=(px, front + 0.22, z + 0.85),
                          scale=(0.30, 0.16, 1.05))

    # ground floor: wall + pink columns
    add_primitive("cube", "GroundWall", pink_f,
                  loc=(CX, front + 0.6, FLOOR_H / 2),
                  scale=(W / 2, 0.25, FLOOR_H / 2))
    for i, cx in enumerate((-10.4, -6.8, -3.4, 3.4, 6.8, 10.4)):
        add_primitive("cube", "GroundCol%d" % i, pink_f,
                      loc=(cx, front - 0.2, FLOOR_H / 2),
                      scale=(0.4, 0.4, FLOOR_H / 2))

    # ---- blue roof ----
    add_primitive("cube", "RoofSlab", blue_r,
                  loc=(CX, front + 0.2, FLOOR_H * 3 + 0.34),
                  scale=(W / 2 + 0.4, D / 2 + 0.3, 0.16))
    add_primitive("cube", "RoofTrim", pink_f,
                  loc=(CX, front + 0.02, FLOOR_H * 3 + 0.14),
                  scale=(W / 2 + 0.35, 0.10, 0.22))

    # facade moonlight wash (keeps the pink readable at night)
    wash = bpy.data.lights.new("FacWash", "AREA")
    wash.energy = 900.0
    wash.color = (0.55, 0.65, 1.0)
    wash.size = 26.0
    wo = bpy.data.objects.new("FacWash", wash)
    wo.location = (0, front - 7.5, 7.0)
    wo.rotation_euler = (M.radians(105), 0, 0)
    bpy.context.collection.objects.link(wo)

    # entrance: steps + door + blue awning
    for s in range(3):
        add_primitive("cube", "SchoolStep%d" % s, mc["concrete"],
                      loc=(0, front - 0.4 - s * 0.28, s * 0.155 + 0.02),
                      scale=(2.2, 0.45, 0.16))
    add_primitive("cube", "SchoolDoor", mc["door"],
                  loc=(0.9, front + 0.1, 1.35), scale=(0.55, 0.08, 1.4))
    add_primitive("cylinder", "DoorHandle", mc["gold"],
                  loc=(1.35, front - 0.08, 1.15),
                  rot=(0, M.pi / 2, 0.1), radius=0.035, depth=0.35)
    add_primitive("cube", "DoorAwning", blue_r,
                  loc=(0, front - 0.5, 2.85), scale=(1.9, 0.8, 0.07))
    gl = bpy.data.lights.new("doorlight", "AREA")
    gl.energy = 40.0
    gl.color = (1.0, 0.7, 0.45)
    gl.size = 1.2
    glo = bpy.data.objects.new("DoorLight", gl)
    glo.location = (0.9, front - 1.6, 2.6)
    glo.rotation_euler = (M.pi * 0.52, 0, 0)
    bpy.context.collection.objects.link(glo)

    # school sign: pink over navy bar + gold emblem (พระเกี้ยว simplified)
    add_primitive("cube", "SignPink", pink_f,
                  loc=(4.6, front - 0.15, 2.65), scale=(1.7, 0.06, 0.16))
    add_primitive("cube", "SignNavy", mc["navy"],
                  loc=(4.6, front - 0.15, 2.28), scale=(1.7, 0.06, 0.16))
    add_primitive("cylinder", "EmblemRing", mc["gold"],
                  loc=(-1.6, front - 0.2, 2.55),
                  rot=(M.pi / 2, 0, 0), radius=0.42, depth=0.08)
    add_primitive("cone", "EmblemCrown", mc["gold"],
                  loc=(-1.6, front - 0.26, 2.60),
                  rot=(-M.pi / 2, 0, 0), radius1=0.25, radius2=0.05,
                  depth=0.28)

    # flagpole with pink flag
    add_primitive("cylinder", "FlagPole", white_m,
                  loc=(5.5, front - 5.0, 3.0), radius=0.045, depth=6.0)
    add_primitive("cube", "FlagPink", pink_f,
                  loc=(5.95, front - 5.0, 5.6), scale=(0.45, 0.015, 0.28))

    # gate posts with pink caps
    for sx in (-1, 1):
        add_primitive("cube", "GatePost%d" % sx, mc["pink_dim"],
                      loc=(sx * 6.2, front - 6.6, 1.4),
                      scale=(0.35, 0.35, 1.4))
        add_primitive("cube", "GateCap%d" % sx, mc["pink"],
                      loc=(sx * 6.2, front - 6.6, 2.95),
                      scale=(0.45, 0.45, 0.22))

    return objs, front  # facade front y


def build_piyaraj(mc=None):
    """ห้องปิยราชรังสรรค์ (หอประชุมของเตรียมอุดมฯ ปทุมธานี): tall gabled hall,
    thick cream columns, pink walls + cream trim, gold sign, warm entrance light."""
    mc = mc or _mats_common()
    objs = []
    W, D = 14.0, 9.0
    y = 10.0
    front = y - D / 2          # 5.5
    H = 4.4                    # wall height
    pink_f = new_material("HallPink", (0.50, 0.16, 0.30, 1.0), rough=0.8)
    cream2 = new_material("HallCream", (0.60, 0.53, 0.45, 1.0), rough=0.85)
    trim = new_material("HallTrim", (0.70, 0.62, 0.50, 1.0), rough=0.7)
    roof_m = new_material("HallRoof", (0.10, 0.15, 0.38, 1.0), rough=0.7)

    # ---- main hall block ----
    add_primitive("cube", "HallBody", pink_f,
                  loc=(0, y, H / 2), scale=(W / 2, D / 2, H / 2))
    add_primitive("cube", "HallBase", cream2,
                  loc=(0, front + 0.15, 0.35), scale=(W / 2 + 0.1, 0.35, 0.35))
    add_primitive("cube", "HallCornice", trim,
                  loc=(0, y, H + 0.12), scale=(W / 2 + 0.35, D / 2 + 0.2, 0.12))

    # ---- gabled roof (ridge along X) ----
    rise = 2.0
    slope = M.atan2(rise, D / 2)
    slab_len = M.sqrt((D / 2) ** 2 + rise ** 2)
    for s, sy in ((1, -1), (2, 1)):
        add_primitive("cube", "HallRoof%d" % s, roof_m,
                      loc=(0, y + sy * D / 4, H + rise / 2),
                      rot=(-sy * slope, 0, 0),
                      scale=(W / 2 + 0.5, slab_len / 2, 0.10))
    add_primitive("cylinder", "HallRidge", mc["gold"],
                  loc=(0, y, H + rise + 0.05), rot=(0, M.pi / 2, 0),
                  radius=0.09, depth=W + 1.0)

    # ---- front porch: 6 thick cream columns + overhang ----
    for i in range(6):
        cx = -6.0 + i * 2.4
        add_primitive("cube", "HallCol%d" % i, cream2,
                      loc=(cx, front - 1.1, H / 2), scale=(0.28, 0.28, H / 2))
        add_primitive("cube", "HallColCap%d" % i, trim,
                      loc=(cx, front - 1.1, H + 0.28), scale=(0.42, 0.42, 0.14))
    add_primitive("cube", "HallPorchRoof", roof_m,
                  loc=(0, front - 0.6, H + 0.42), scale=(W / 2 + 0.4, 1.3, 0.08))

    # ---- entrance: steps + double doors ----
    for s in range(3):
        add_primitive("cube", "HallStep%d" % s, mc["concrete"],
                      loc=(0, front - 0.55 - s * 0.3, s * 0.16 + 0.02),
                      scale=(3.0, 0.5, 0.16))
    for sx in (-1, 1):
        add_primitive("cube", "HallDoor%d" % sx, mc["door"],
                      loc=(sx * 0.55, front + 0.1, 1.45), scale=(0.5, 0.08, 1.4))

    # ---- gold sign + emblem (พระเกี้ยว simplified) ----
    add_primitive("cube", "HallSign", mc["gold"],
                  loc=(0, front - 0.12, 3.4), scale=(2.6, 0.06, 0.35))
    add_primitive("cylinder", "HallEmblem", mc["gold"],
                  loc=(-4.2, front - 0.2, 3.2), rot=(M.pi / 2, 0, 0),
                  radius=0.45, depth=0.08)
    add_primitive("cone", "HallCrown", mc["gold"],
                  loc=(-4.2, front - 0.26, 3.25), rot=(-M.pi / 2, 0, 0),
                  radius1=0.27, radius2=0.06, depth=0.3)

    # ---- tall lit windows on the front wall ----
    for k in range(8):
        wx = -5.6 + k * 1.6
        if abs(wx) < 1.7:
            continue
        add_primitive("cube", "HallWin%d" % k, mc["glass_lit"],
                      loc=(wx, front - 0.05, 2.3), scale=(0.5, 0.04, 0.85))
        add_primitive("cube", "HallWinF%d" % k, trim,
                      loc=(wx, front - 0.06, 2.3), scale=(0.58, 0.035, 0.93))

    # ---- warm lights: porch points + door glow + moonlight wash ----
    for k, lx in enumerate((-3.4, 3.4)):
        pl = bpy.data.lights.new("HallWarm%d" % k, "POINT")
        pl.energy = 60.0
        pl.color = (1.0, 0.62, 0.3)
        pl.shadow_soft_size = 0.6
        po = bpy.data.objects.new("HallWarm%d" % k, pl)
        po.location = (lx, front - 1.4, 3.0)
        bpy.context.collection.objects.link(po)
    dl = bpy.data.lights.new("HallDoorGlow", "AREA")
    dl.energy = 80.0
    dl.color = (1.0, 0.68, 0.38)
    dl.size = 2.0
    do_ = bpy.data.objects.new("HallDoorGlow", dl)
    do_.location = (0, front - 2.2, 2.8)
    do_.rotation_euler = (M.pi * 0.55, 0, 0)
    bpy.context.collection.objects.link(do_)
    wash = bpy.data.lights.new("HallWash", "AREA")
    wash.energy = 700.0
    wash.color = (0.55, 0.65, 1.0)
    wash.size = 18.0
    wo = bpy.data.objects.new("HallWash", wash)
    wo.location = (0, front - 8.0, 6.5)
    wo.rotation_euler = (M.radians(105), 0, 0)
    bpy.context.collection.objects.link(wo)

    return objs, front  # facade front y


def build_sakura(mc, x=-7.0, y=6.0, h=4.6):
    """ชมพูพันธุ์ทิพย์ (cherry) tree: curved trunk + blossom clusters."""
    refs = []
    m = mc
    prev = None
    n_seg = 5
    for i in range(n_seg):
        t = i / (n_seg - 1)
        z0 = h * 0.42 * (i / n_seg)
        loc = (x + 0.5 * t * t, y - 0.3 * t, h * 0.06 + z0)
        seg = add_primitive("cylinder", "Trunk%d" % i, m["trunk"],
                            loc=loc, rot=(0.5 * t, 0.35 * t, 0.2 * i),
                            radius=0.22 - 0.16 * t * (t), depth=h * 0.42 / n_seg * 1.5,
                            smooth=True)
        prev = seg
        # side branches near top
        if i >= 2:
            br = add_primitive("cylinder", "Branch%d" % i, m["trunk"],
                               loc=(x + 0.85 * t, y - 0.5 * t, h * 0.55 + i * 0.12),
                               rot=(0.9 + 0.15 * t, 0.4, 0.7 * i),
                               radius=0.09 - 0.05 * t, depth=1.3 / n_seg * 2.2,
                               smooth=True)
    # blossom clusters (icospheres, tweaked by wave for variety)
    n_cl = 34
    for i in range(n_cl):
        a = wave(i, 0.77) * M.pi * 2
        r = 0.9 + wave(i + 31, 0.13) * 1.1
        t = 0.6 + wave(i + 7, 0.41) * 0.4
        cz = h * 0.8 + t * h * 0.22
        cl = add_primitive("ico", "Blossom%d" % i, m["blossom"],
                           loc=(x + M.cos(a) * r * 0.9, y + M.sin(a) * r * 0.55 - 0.2,
                                cz),
                           scale=(0.16 + wave(i + 3, 0.0) * 0.16,
                                  0.15 + wave(i + 9, 0.28) * 0.14,
                                  0.13 + wave(i + 5, 0.55) * 0.12),
                           smooth=True)
        # subdivide only the first few for perf balance
        if i < 6:
            mod = cl.modifiers.new("sub", "SUBSURF")
            mod.levels = mod.render_levels = 1
    return refs


def build_moon_and_lights(mc, scene, sun_target=(0, 0, 1)):
    objs = []
    # moon disc — high enough to clear the 13m building (elev > 31 deg)
    moon = add_primitive("sphere", "Moon", mc["moon"],
                         loc=(-5.5, 92, 72), scale=(3.0, 3.0, 3.0), smooth=True)
    sun = bpy.data.lights.new("MoonSun", "SUN")
    sun.energy = 2.2
    sun.color = (0.55, 0.65, 1.0)
    sun.angle = M.radians(8)
    so = bpy.data.objects.new("MoonSun", sun)
    so.location = (-10, 18, 22)
    # aim at origin nicely
    target = bpy.data.objects.new("SunTarget", None)
    target.location = (0, 0, 0)
    bpy.context.collection.objects.link(target)
    lc = so.constraints.new("TRACK_TO")
    lc.target = target
    bpy.context.collection.objects.link(so)
    objs.append(so)

    fill = bpy.data.lights.new("FillBlue", "AREA")
    fill.energy = 260.0
    fill.color = (0.5, 0.62, 1.0)
    fill.size = 10.0
    fo = bpy.data.objects.new("FillBlue", fill)
    fo.location = (6, -6, 7)
    fo.rotation_euler = (1.15, 0, -0.5)
    bpy.context.collection.objects.link(fo)
    objs.append(fo)
    return objs


def build_classroom(mc=None):
    """Interior: desks, chairs, board, fluorescent lights, a doorway to hide."""
    mc = mc or _mats_common()
    # room shell (dim, moody)
    floor = add_primitive("plane", "ClassFloor",
                          new_material("ClassFloorM", (0.16, 0.15, 0.15, 1.0), rough=0.9),
                          loc=(0, 0, 0), scale=(8, 12, 1))
    wall = add_primitive("cube", "ClassWallBack",
                         new_material("ClassWallM", (0.22, 0.20, 0.19, 1.0), rough=0.9),
                         loc=(0, 6, 1.8), scale=(8, 0.15, 1.8))
    wall2 = add_primitive("cube", "ClassWallSide",
                          new_material("ClassWallM2", (0.18, 0.16, 0.16, 1.0), rough=0.9),
                          loc=(-8, 0, 1.8), scale=(0.15, 12, 1.8))
    ceiling = add_primitive("cube", "ClassCeiling",
                            new_material("ClassCeilM", (0.12, 0.12, 0.14, 1.0), rough=0.9),
                            loc=(0, 0, 3.5), scale=(8, 12, 0.1))
    # blackboard
    board = add_primitive("cube", "Board",
                          new_material("BoardM", (0.02, 0.03, 0.02, 1.0), rough=0.7),
                          loc=(0, 5.85, 1.7), scale=(3.4, 0.08, 1.1))
    # desks (2 rows)
    desk_mat = new_material("DeskM", (0.30, 0.20, 0.13, 1.0), rough=0.8)
    navy_mat = new_material("ChairNavyM", (0.05, 0.07, 0.16, 1.0), rough=0.8)
    for r in range(2):
        for c in range(3):
            dx, dy = (c - 1) * 2.2, 1.6 + r * 1.8
            desk = add_primitive("cube", "Desk%d%d" % (r, c), desk_mat,
                                 loc=(dx, dy, 0.38), scale=(0.55, 0.4, 0.035))
            add_primitive("cube", "DeskLeg%d%d" % (r, c), desk_mat,
                          loc=(dx, dy, 0.19), scale=(0.05, 0.05, 0.19))
            chair = add_primitive("cube", "Chair%d%d" % (r, c), navy_mat,
                                  loc=(dx, dy - 0.75, 0.26),
                                  scale=(0.18, 0.16, 0.03))
            add_primitive("cube", "ChairBack%d%d" % (r, c), navy_mat,
                          loc=(dx, dy - 0.88, 0.52), scale=(0.18, 0.03, 0.13))
            add_primitive("cube", "ChairLeg%d%d" % (r, c), navy_mat,
                          loc=(dx, dy - 0.75, 0.13), scale=(0.16, 0.14, 0.13))
    # fluorescent tubes (dim, moody)
    for i, ty in enumerate((-2.0, 1.0, 4.0)):
        tube = add_primitive("cube", "Tube%d" % i,
                             new_material("TubeM", (0.9, 0.9, 0.9, 1),
                                          emission=(1.0, 0.9, 0.75, 1.0),
                                          emission_strength=1.1),
                             loc=(0, ty, 3.32), scale=(2.2, 0.14, 0.04))
        light = bpy.data.lights.new("RoomLight%d" % i, "AREA")
        light.energy = 55.0
        light.color = (1.0, 0.85, 0.65)
        light.size = 3.0
        lo = bpy.data.objects.new("RoomLight%d" % i, light)
        lo.location = (0, ty, 3.1)
        bpy.context.collection.objects.link(lo)
    # doorway (right wall, no door yet)
    add_primitive("cube", "DoorFrameSide",
                  new_material("FrameM", (0.6, 0.58, 0.52, 1.0), rough=0.8),
                  loc=(0.95, 6, 1.1), scale=(0.5, 0.05, 0.55))
    return {}


def build_door_closeup(mc=None):
    """A metal door with 3 glowing red scratch marks + door handle/lock area.
    NOTE: add_primitive cubes are 2m at scale (1,1,1) — divide dims by 2."""
    mc = mc or _mats_common()
    # dark corridor backdrop
    wall = add_primitive("cube", "CorrWall",
                         new_material("CorrWallM", (0.10, 0.09, 0.13, 1.0), rough=0.9),
                         loc=(0, 2.2, 1.6), scale=(4.5, 0.15, 1.6))
    floor = add_primitive("plane", "CorrFloor",
                          new_material("CorrFloorM", (0.13, 0.11, 0.10, 1.0), rough=0.9),
                          loc=(0, 0, 0), scale=(4.5, 2.0, 1))
    door = add_primitive("cube", "CloseUpDoor", mc["door"],
                         loc=(0, 0, 1.0), scale=(0.8, 0.03, 1.0))   # 1.6 x 2.0 m
    frame = add_primitive("cube", "CloseUpFrame",
                          new_material("FrameM2", (0.28, 0.26, 0.24, 1.0), rough=0.85),
                          loc=(0, 0.10, 1.07), scale=(0.95, 0.05, 1.12))
    handle = add_primitive("cylinder", "CloseUpHandle", mc["gold"],
                           loc=(0.55, -0.09, 1.0), rot=(0, M.pi / 2, 0.02),
                           radius=0.028, depth=0.28)
    plate = add_primitive("cube", "CloseUpPlate",
                          new_material("PlateM", (0.3, 0.27, 0.22, 1.0), rough=0.5),
                          loc=(0.55, -0.11, 1.22), scale=(0.10, 0.012, 0.14))
    # scratches — flat glowing red slashes lying ON the door face (y ~ -0.07)
    scr_mat = new_material("Scratch", (0.25, 0.02, 0.02, 1.0), rough=0.4,
                           emission=(0.85, 0.03, 0.03, 1.0), emission_strength=4.0)
    scratch_objs = []
    for i, (x, rot, ln) in enumerate([(-0.42, 0.13, 0.42),
                                      (-0.12, 0.07, 0.55),
                                      (0.22, 0.20, 0.36)]):
        s = add_primitive("cube", "Scratch%d" % i, scr_mat,
                          loc=(x, -0.075, 1.35), rot=(0, 0, rot),
                          scale=(0.012, 0.006, ln))
        scratch_objs.append(s)
    # red rim light for mood
    rl = bpy.data.lights.new("ScratchRed", "POINT")
    rl.energy = 12.0
    rl.color = (1.0, 0.1, 0.08)
    rl.shadow_soft_size = 0.5
    ro = bpy.data.objects.new("ScratchRed", rl)
    ro.location = (0.1, -1.0, 1.6)
    bpy.context.collection.objects.link(ro)
    cool = bpy.data.lights.new("ScratchCool", "AREA")
    cool.energy = 35.0
    cool.color = (0.5, 0.6, 1.0)
    cool.size = 2.5
    co = bpy.data.objects.new("ScratchCool", cool)
    co.location = (0.4, -3.2, 2.4)
    co.rotation_euler = (1.35, 0, 0)
    bpy.context.collection.objects.link(co)
    return {"door": door, "frame": frame, "scratches": scratch_objs}
