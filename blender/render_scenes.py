# render_scenes.py — master builder+renderer for What-If EP.1 Blender beats.
# Usage:  blender -b -P render_scenes.py -- --scene b1 --out <dir> [--quick]
#         --quick : 25% res, every Nth frame (for review previews)
import sys, os, math
import bpy

_here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.path.dirname(sys.argv[-1])
sys.path.insert(0, _here)

import hf_common as C
import hf_character as CH
import hf_sets as S

M = math
FPS = 30
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(name, default=None):
    if name in ARGS:
        return ARGS[ARGS.index(name) + 1]
    return default


def flag(name):
    return name in ARGS


QUICK = flag("--quick")
OUT = arg("--out", os.path.join(os.path.dirname(__file__), "out"))


# ---------------------------------------------------------------- helpers
def fresh():
    C.reset_scene()
    CH.MAT_CACHE.clear()
    scene = bpy.context.scene
    scene.render.fps = FPS
    return scene


def camera(name, loc, aim=None):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = 28.0
    cam = bpy.data.objects.new(name, cam_data)
    cam.location = loc
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    if aim:
        tgt = bpy.data.objects.new(name + "_tgt", None)
        tgt.location = aim
        bpy.context.collection.objects.link(tgt)
        c = cam.constraints.new("TRACK_TO")
        c.target = tgt
    return cam


def cam_key(cam, frame, loc, lens=None):
    cam.location = loc
    cam.keyframe_insert("location", frame=frame)
    if lens is not None:
        cam.data.lens = lens
        cam.data.keyframe_insert("lens", frame=frame)


def cam_path(cam, f0, f1, p0, p1, shake=0.02, seed=7):
    """Push-in with tiny deterministic handheld shake keyed every frame."""
    n = f1 - f0
    for f in range(f0, f1 + 1):
        t = (f - f0) / max(1, n)
        e = t * t * (3 - 2 * t)  # smoothstep ease
        dx = M.sin(f * 0.9 + seed) * shake
        dy = M.cos(f * 0.7 + seed * 2) * shake * 0.6
        dz = M.sin(f * 1.3 + seed * 3) * shake * 0.4
        cam_key(cam, f,
                tuple(p0[k] + (p1[k] - p0[k]) * e + (dx, dy, dz)[k] for k in range(3)))


def static_cam(cam, f0, f1, loc, shake=0.015, seed=3):
    for f in range(f0, f1 + 1):
        dx = M.sin(f * 0.9 + seed) * shake
        dy = M.cos(f * 0.7 + seed * 2) * shake * 0.6
        dz = M.sin(f * 1.4 + seed * 3) * shake * 0.35
        cam_key(cam, f, (loc[0] + dx, loc[1] + dy, loc[2] + dz))


def fog_card(name, y, size_x=30.0, height=11.0, alpha=0.14, col=(0.35, 0.45, 0.75)):
    m = C.new_material(name, (col[0], col[1], col[2], 1.0), rough=1.0)
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Alpha"].default_value = alpha
    try:
        m.surface_render_method = "BLENDED"
    except Exception:
        try:
            m.blend_method = "BLEND"
        except Exception:
            pass
    card = C.add_primitive("plane", name, m, loc=(0, y, height / 2),
                           rot=(M.pi / 2, 0, 0), scale=(size_x / 2, height / 2, 1))
    return card


def res_and_range(g_frames, g_res_pct=100):
    r = bpy.context.scene.render
    r.resolution_x, r.resolution_y = 1080, 1920
    r.resolution_percentage = 25 if QUICK else g_res_pct
    r.film_transparent = False
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = g_frames
    if QUICK:
        # render every 5th frame for preview speed
        bpy.context.scene.frame_step = 5
    else:
        bpy.context.scene.frame_step = 1


def go(out_name, frames, prefix="frame"):
    out_dir = os.path.join(OUT, out_name)
    os.makedirs(out_dir, exist_ok=True)
    scene = bpy.context.scene
    engine = C.setup_render(scene, out_dir, prefix=prefix, fps=FPS)
    print("### ENGINE:", engine)
    res_and_range(frames)
    res = scene.render
    print("### RENDER", out_name, res.resolution_x * res.resolution_percentage // 100,
          "x", res.resolution_y * res.resolution_percentage // 100, "frames", frames)
    bpy.ops.render.render(animation=True)
    print("### DONE", out_name)


# =================================================================== B1
# โรงเรียนตอนกลางคืน + จ้อบซอมบี้เดินเข้ามา (กล้อง push-in)
def scene_b1():
    fresh()
    mc = S._mats_common()
    S.build_ground(60)
    objs, facade_y = S.build_school(mc)
    if not flag("--no-tree"):
        S.build_sakura(mc, x=-7.0, y=facade_y - 0.6)
    S.build_moon_and_lights(mc, bpy.context.scene)
    fog_card("FogA", facade_y - 2.6, 34, 12, 0.10)
    fog_card("FogB", facade_y - 6.5, 26, 9, 0.06)

    job = CH.make_student("Job", gender="boy", zombie=True, scale=1.0)
    job["root"].location = (-0.6, 4.4, 0)
    job["root"].rotation_euler = (0, 0, 0.1)
    CH.animate_zombie_walk(job, 1, 135, speed=0.72)
    # red glow around จ้อบ so he reads in the dark
    zl = bpy.data.lights.new("JobGlow", "POINT")
    zl.energy = 16.0
    zl.color = (1.0, 0.12, 0.08)
    zl.shadow_soft_size = 0.5
    zo = bpy.data.objects.new("JobGlow", zl)
    zo.location = (-0.6, 3.2, 1.5)
    bpy.context.collection.objects.link(zo)
    zc = zo.constraints.new("TRACK_TO")
    zc.target = bpy.data.objects.get("Job_root")
    # soft key light on จ้อบ from camera side
    kl = bpy.data.lights.new("JobKey", "SPOT")
    kl.energy = 110.0
    kl.color = (0.7, 0.78, 1.0)
    kl.spot_size = M.radians(40)
    kl.shadow_soft_size = 0.4
    ko = bpy.data.objects.new("JobKey", kl)
    ko.location = (-0.4, -5.5, 2.6)
    bpy.context.collection.objects.link(ko)
    kc = ko.constraints.new("TRACK_TO")
    kc.target = bpy.data.objects.get("Job_root")

    C.setup_world(bpy.context.scene, horizon=(0.015, 0.022, 0.05, 1.0), strength=1.0)
    cam = camera("CamB1", (1.2, -12.5, 1.8), aim=(0, 6, 5.2))
    cam.data.lens = 22.0
    cam_path(cam, 1, 135, (1.2, -12.5, 1.75), (0.6, -9.6, 2.1), shake=0.03, seed=11)
    go("b1", 135)


# =================================================================== B3
# นักเรียน 3 คนยืนนิ่ง ไม่ขยับ (กล้อง dolly ช้าๆ)
def scene_b3():
    fresh()
    mc = S._mats_common()
    S.build_ground(40)
    S.build_moon_and_lights(mc, bpy.context.scene)
    # blue sidelight strongly behind figures (rim silhouette)
    rim = bpy.data.lights.new("Rim", "AREA")
    rim.energy = 400
    rim.color = (0.35, 0.5, 0.95)
    rim.size = 6
    ro = bpy.data.objects.new("Rim", rim)
    ro.location = (0, 6, 4.5)
    ro.rotation_euler = (M.pi * 0.65, 0, 0)
    bpy.context.collection.objects.link(ro)

    parts = []
    for i, x in enumerate((-2.6, 0.1, 2.7)):
        p = CH.make_student("Still%d" % i, gender=("girl" if i == 1 else "boy"),
                            zombie=True, scale=1.0)
        p["root"].location = (x, 2.0 + 0.4 * ((i % 2) - 1), 0)
        p["root"].rotation_euler = (0, 0, 0.35 - 0.5 * i - 0.18)
        parts.append(p)
    CH.animate_still_group(parts, 1, 150, key_every=3, jitter=0.5)

    fog_card("FogC", -1.5, 24, 9, 0.09)
    cam = camera("CamB3", (-3.0, -5.0, 1.45), aim=(0.2, 2.0, 1.05))
    for f in range(1, 151):
        t = (f - 1) / 149
        e = t * t * (3 - 2 * t)
        loc = (-3.0 + 5.6 * e, -5.0, 1.45 + 0.1 * e)
        dx = M.sin(f * 1.1) * 0.02
        dz = M.cos(f * 0.8) * 0.012
        cam_key(cam, f, (loc[0] + dx, loc[1], loc[2] + dz))
    go("b3", 150)


# =================================================================== B4
# ภาพกว้างบรรยากาศโรงเรียน (พื้นหลัง TIP) — กล้องนิ่ง หมอก
def scene_b4():
    fresh()
    mc = S._mats_common()
    S.build_ground(60)
    S.build_school(mc)
    S.build_sakura(mc, x=6.4, y=5.6)
    S.build_sakura(mc, x=-9.0, y=5.0)
    S.build_moon_and_lights(mc, bpy.context.scene)
    fog_card("FogD", 9.0, 40, 14, 0.16)
    fog_card("FogE", 2.0, 30, 11, 0.10)
    cam = camera("CamB4", (0, -14, 1.7), aim=(0, 8, 5.0))
    cam_path(cam, 1, 300, (0, -14.0, 1.65), (0, -12.4, 1.95), shake=0.03, seed=21)
    go("b4", 300)


# =================================================================== B5
# ห้องเรียน นักเรียนซ่อนหลังโต๊ะ (crouch) + ประตูที่จะถูกปิด/ล็อค
def scene_b5():
    fresh()
    S.build_classroom()
    mc = S._mats_common()
    # hide students: sink root below floor so only head+shoulders stay above
    # desk level (0.38m) — reads as crouched hiding, no distorted geometry.
    hide_rows = [(-2.2, 2.1, "girl", 0.15), (2.2, 2.1, "boy", -0.1),
                 (0.0, 3.9, "girl", 0.12)]
    for i, (x, yy, g, tilt) in enumerate(hide_rows):
        p = CH.make_student("Hide%d" % i, gender=g, zombie=False, scale=1.0)
        p["root"].location = (x, yy, -0.5)   # sunk: head top ≈ 1.16m, torso hidden by desk
        p["root"].rotation_euler = (0, 0, M.pi * (0.92 + tilt))
        # tense pose handled by pose_hidden_idle inside the animation loop
        CH.animate_still_group([p], 1, 300, key_every=4, jitter=0.22,
                               pose_fn=CH.pose_hidden_idle)

    cam = camera("CamB5", (0.9, -4.6, 1.75), aim=(0.2, 4.5, 1.05))
    cam.data.lens = 24.0
    cam_path(cam, 1, 300, (0.9, -4.6, 1.7), (0.35, -1.6, 1.5), shake=0.03, seed=31)
    # breathing dim of room lights for tension
    lamps = [o for o in bpy.data.objects if o.name.startswith("RoomLight")]
    for f in range(1, 301):
        v = 1.0 - 0.18 * (0.5 + 0.5 * M.sin(f * 0.35)) - (0.1 if C.wave(f, 0.5) > 0.93 else 0)
        for lo in lamps:
            lo.data.energy = 55.0 * v
            lo.data.keyframe_insert("energy", frame=f)
    go("b5", 300)


# =================================================================== B6
# ประตูสนิท + รอยข่วนเรืองแดง (กล้อง push เข้าหารอยข่วน)
def scene_b6():
    fresh()
    refs = S.build_door_closeup()
    cam = camera("CamB6", (0, -2.6, 1.35), aim=(0.05, 0, 1.35))
    cam_path(cam, 1, 315, (-0.1, -2.6, 1.3), (0.05, -1.55, 1.42), shake=0.02, seed=41)
    # red flicker on scratches
    red = bpy.data.objects.get("ScratchRed")
    for f in range(1, 316):
        e = 14 + 12 * (0.5 + 0.5 * M.sin(f * 0.9)) + (16 if C.wave(f, 0.21) > 0.9 else 0)
        red.data.energy = e
        red.data.keyframe_insert("energy", frame=f)
    go("b6", 315)


# =================================================================== C3
# ห้องปิยราชรังสรรค์ กลางคืน — นักเรียนเดินเข้าหอ (ผอ.ประกาศ)
def pose_walk_normal(parts, t=0.0):
    """Alive student walking: upright, natural arm/leg swing."""
    CH.pose_rest(parts)
    parts["neck"].rotation_euler = (0.05 + M.sin(t * 2.1) * 0.03, 0,
                                    M.sin(t * 1.1) * 0.05)
    for i, sh in enumerate(parts["shoulders"]):
        sh.rotation_euler = (M.sin(t * 2.3 + i * M.pi) * 0.30, 0, 0)
    for i, el in enumerate(parts["elbows"]):
        el.rotation_euler = (-0.30 - max(0.0, M.sin(t * 2.3 + i * M.pi)) * 0.35, 0, 0)
    for i, hp in enumerate(parts["hips"]):
        hp.rotation_euler = (-M.sin(t * 2.3 + i * M.pi) * 0.32, 0, 0)
    for i, kn in enumerate(parts["knees"]):
        kn.rotation_euler = (0.15 + max(0.0, M.sin(t * 2.3 + i * M.pi)) * 0.30, 0, 0)


def animate_walk(parts, f0, f1, fps=30, speed=0.5, key_every=2, pose_fn=None,
                 dir_y=-1.0):
    """Walk along Y (dir_y=-1 towards default camera, +1 away)."""
    root = parts["root"]
    y0 = root.location.y
    t0 = f0 / fps
    pose_fn = pose_fn or CH.pose_zombie_idle
    for f in range(f0, f1 + 1, key_every):
        t = f / fps
        root.location.y = y0 + dir_y * speed * (t - t0)
        root.location.z = abs(M.sin(t * 4.6)) * 0.022
        pose_fn(parts, t)
        root.keyframe_insert("location", frame=f)
        for grp in ("shoulders", "elbows", "hips", "knees"):
            for p in parts[grp]:
                p.keyframe_insert("rotation_euler", frame=f)
        parts["neck"].keyframe_insert("rotation_euler", frame=f)


def scene_c3():
    fresh()
    mc = S._mats_common()
    S.build_ground(50)
    S.build_piyaraj(mc)
    S.build_sakura(mc, x=-9.5, y=3.2)
    S.build_sakura(mc, x=9.5, y=3.6)
    S.build_moon_and_lights(mc, bpy.context.scene)
    fog_card("FogC3a", 2.0, 30, 10, 0.10)
    fog_card("FogC3b", -3.0, 24, 8, 0.06)

    # students walking to the hall (towards +Y)
    lanes = [(-3.4, 0.9, "girl", 0.10), (-2.0, 0.0, "boy", -0.06),
             (-0.7, 1.1, "boy", 0.05), (0.6, 0.2, "girl", -0.08),
             (1.9, 0.9, "boy", 0.07), (3.2, 0.0, "boy", -0.05),
             (-4.6, 0.4, "boy", 0.12)]
    for i, (x, y0, g, rz) in enumerate(lanes):
        p = CH.make_student("Stu%d" % i, gender=g, zombie=False, scale=1.0)
        p["root"].location = (x, y0, 0)
        p["root"].rotation_euler = (0, 0, M.pi + rz)   # face +Y (hall)
        animate_walk(p, 1, 150, speed=0.55, pose_fn=pose_walk_normal, dir_y=1.0)

    C.setup_world(bpy.context.scene, horizon=(0.015, 0.022, 0.05, 1.0), strength=1.0)
    # soft key on the walking group so shirts read against the lit wall
    kl = bpy.data.lights.new("C3Key", "SPOT")
    kl.energy = 160.0
    kl.color = (0.75, 0.8, 1.0)
    kl.spot_size = M.radians(55)
    kl.shadow_soft_size = 0.6
    ko = bpy.data.objects.new("C3Key", kl)
    ko.location = (-3.0, -6.5, 3.2)
    bpy.context.collection.objects.link(ko)
    kc = ko.constraints.new("TRACK_TO")
    kc.target = bpy.data.objects.get("Stu3_root")
    cam = camera("CamC3", (-5.0, -7.5, 1.9), aim=(0.5, 5.5, 2.2))
    cam.data.lens = 26.0
    cam_path(cam, 1, 150, (-5.0, -7.5, 1.9), (-2.4, -5.8, 2.1), shake=0.03, seed=51)
    go("c3", 150)


# =================================================================== C4
# ห้องเรียน — จ้อบ×บอลคุยเสียงดัง + ครูเกริกเตือน
def pose_talk(parts, t=0.0):
    """Two kids chatting: head turns + small hand gestures."""
    CH.pose_rest(parts)
    parts["neck"].rotation_euler = (0.04 + M.sin(t * 2.3) * 0.04, 0,
                                    M.sin(t * 0.9) * 0.14)
    for i, sh in enumerate(parts["shoulders"]):
        sh.rotation_euler = (0.12 + M.sin(t * 1.9 + i * 2.2) * 0.10, 0,
                             (0.18 if i else -0.18) + M.sin(t * 1.2 + i) * 0.05)
    for i, el in enumerate(parts["elbows"]):
        el.rotation_euler = (-0.45 + M.sin(t * 2.5 + i * 1.6) * 0.12, 0, 0)


def pose_teacher(parts, t=0.0):
    """ครูเกริก: stern, right arm raised pointing, slow head scan."""
    CH.pose_rest(parts)
    parts["neck"].rotation_euler = (0.10, 0, M.sin(t * 0.6) * 0.06)
    parts["shoulders"][1].rotation_euler = (-1.35 + M.sin(t * 1.1) * 0.06, 0, -0.25)
    parts["elbows"][1].rotation_euler = (-0.5, 0, 0)
    parts["shoulders"][0].rotation_euler = (0.12, 0, 0.15)


def scene_c4():
    fresh()
    S.build_classroom()
    mc = S._mats_common()

    # จ้อบ & บอล standing between desk rows, facing each other, talking
    job = CH.make_student("Job", gender="boy", zombie=False, scale=1.0)
    job["root"].location = (-1.15, 2.6, 0)
    job["root"].rotation_euler = (0, 0, M.pi / 2)      # faces +X
    ball = CH.make_student("Ball", gender="boy", zombie=False, scale=1.0)
    ball["root"].location = (1.15, 2.45, 0)
    ball["root"].rotation_euler = (0, 0, -M.pi / 2)    # faces -X
    CH.animate_still_group([job, ball], 1, 165, key_every=2, jitter=1.0,
                           pose_fn=pose_talk)

    # ครูเกริก: taller, steel-blue shirt, standing behind them
    teacher = CH.make_student("KruK", gender="boy", zombie=False, scale=1.12)
    tmat = C.new_material("TeacherShirt", (0.16, 0.20, 0.30, 1.0), rough=0.8)
    for o in bpy.data.objects:
        if o.name.startswith("KruK_") and o.type == "MESH":
            for sl in o.material_slots:
                if sl.material and sl.material.name == "ShirtA":
                    sl.material = tmat
    teacher["root"].location = (0.1, 5.3, 0)
    teacher["root"].rotation_euler = (0, 0, 0.06)
    CH.animate_still_group([teacher], 1, 165, key_every=3, jitter=0.8,
                           pose_fn=pose_teacher)

    # brighter room + camera-side fill so faces read (talking scene)
    lamps = [o for o in bpy.data.objects if o.name.startswith("RoomLight")]
    for f in range(1, 166):
        v = 1.0 - 0.10 * (0.5 + 0.5 * M.sin(f * 0.4))
        for lo in lamps:
            lo.data.energy = 85.0 * v
            lo.data.keyframe_insert("energy", frame=f)
    fill = bpy.data.lights.new("C4Fill", "AREA")
    fill.energy = 45.0
    fill.color = (1.0, 0.85, 0.7)
    fill.size = 3.0
    fo = bpy.data.objects.new("C4Fill", fill)
    fo.location = (3.2, -0.8, 2.2)
    fo.rotation_euler = (M.radians(115), 0, M.radians(-35))
    bpy.context.collection.objects.link(fo)

    cam = camera("CamC4", (3.4, -2.2, 1.7), aim=(-0.2, 3.4, 1.25))
    cam.data.lens = 30.0
    cam_path(cam, 1, 165, (3.4, -2.2, 1.7), (2.6, -1.2, 1.55), shake=0.025, seed=61)
    go("c4", 165)


SCENES = {"b1": scene_b1, "b3": scene_b3, "b4": scene_b4,
          "b5": scene_b5, "b6": scene_b6,
          "c3": scene_c3, "c4": scene_c4}

if __name__ == "__main__":
    name = arg("--scene", "b1")
    SCENES[name]()
