# hf_character.py — builds a Thai student character from primitives.
# Boy: white shirt, navy trousers, navy tie, black shoes.
# Girl: white shirt, navy skirt. Zombie variant: pale-green skin, glowing red eyes.
import math
import bpy
from hf_common import (new_material, add_primitive, wave, reset_scene)  # shorthand

M = math

MAT_CACHE = {}


def mats(zombie=False):
    key = "zombie" if zombie else "alive"
    if key in MAT_CACHE:
        return MAT_CACHE[key]
    if zombie:
        skin = new_material("SkinZ", (0.55, 0.62, 0.52, 1.0), rough=0.7)
        eyes = new_material("EyesZ", (0.05, 0.0, 0.0, 1.0), rough=0.3,
                            emission=(0.8, 0.02, 0.02, 1.0), emission_strength=8.0)
        shirt = new_material("ShirtZ", (0.66, 0.66, 0.64, 1.0), rough=0.85)
        navy = new_material("NavyZ", (0.05, 0.07, 0.14, 1.0), rough=0.8)
        hair = new_material("HairZ", (0.02, 0.02, 0.02, 1.0), rough=0.6)
        shoes = new_material("ShoeZ", (0.03, 0.03, 0.03, 1.0), rough=0.5)
    else:
        skin = new_material("SkinA", (0.85, 0.65, 0.5, 1.0), rough=0.6)
        eyes = new_material("EyesA", (0.02, 0.02, 0.02, 1.0), rough=0.2)
        shirt = new_material("ShirtA", (0.9, 0.9, 0.88, 1.0), rough=0.85)
        navy = new_material("NavyA", (0.07, 0.1, 0.22, 1.0), rough=0.8)
        hair = new_material("HairA", (0.03, 0.02, 0.02, 1.0), rough=0.55)
        shoes = new_material("ShoeA", (0.05, 0.05, 0.05, 1.0), rough=0.5)
    pink = new_material("PinkBand", (0.55, 0.05, 0.22, 1.0), rough=0.6)
    MAT_CACHE[key] = dict(skin=skin, eyes=eyes, shirt=shirt, navy=navy,
                          hair=hair, shoes=shoes, pink=pink)
    return MAT_CACHE[key]


def _limb(name, mat, radius, length, parent, pivot_below=True):
    """Capsule hanging DOWN (-Z) from parent empty. Rotate parent to swing it."""
    mesh = add_primitive("capsule", name, mat,
                         loc=(0, 0, -length / 2.0),
                         scale=(radius, radius, length / 2.0 + radius),
                         parent=parent, smooth=True)
    return mesh


def make_student(name, gender="boy", zombie=True, scale=1.0):
    m = mats(zombie)
    parts = {}

    root = bpy.data.objects.new(name + "_root", None)
    bpy.context.collection.objects.link(root)

    # ---------- torso (capsule, upright along Z) ----------
    torso = add_primitive("capsule", name + "_torso", m["shirt"],
                          loc=(0, 0, 0), scale=(0.15, 0.19, 0.30),
                          parent=root, smooth=True)
    torso.location = (0, 0, 1.16)
    parts["torso"] = torso

    # shirt hem band
    hem = add_primitive("cylinder", name + "_hem", m["shirt"],
                        scale=(1.02, 1.02, 1), radius=0.155, depth=0.10,
                        loc=(0, 0, 0.86), parent=root, smooth=True)

    # ---------- tie ----------
    tie_knot = add_primitive("cube", name + "_tie_knot", m["navy"],
                             loc=(0, -0.17, 1.42), scale=(0.055, 0.03, 0.05), parent=root)
    tie = add_primitive("cube", name + "_tie", m["navy"],
                        loc=(0, -0.175, 1.30), scale=(0.045, 0.022, 0.16), parent=root)
    parts["tie"] = tie

    # ---------- head group ----------
    neck = bpy.data.objects.new(name + "_neck", None)
    neck.location = (0, 0, 1.46)
    neck.parent = root
    bpy.context.collection.objects.link(neck)
    parts["neck"] = neck

    head = add_primitive("sphere", name + "_head", m["skin"],
                         scale=(0.078, 0.088, 0.098), loc=(0, 0, 0.10),
                         parent=neck, smooth=True)
    parts["head"] = head

    # hair cap
    add_primitive("sphere", name + "_hair", m["hair"],
                  scale=(0.084, 0.094, 0.096), loc=(0, 0.006, 0.108),
                  parent=neck, smooth=True)
    if gender == "girl":
        # longer hair: two side slabs + back slab
        add_primitive("cube", name + "_hair_back", m["hair"],
                      loc=(0, 0.02, -0.06), scale=(0.07, 0.09, 0.16),
                      parent=neck)
        add_primitive("cube", name + "_hair_side_l", m["hair"],
                      loc=(-0.085, -0.0, 0.0), scale=(0.02, 0.09, 0.10),
                      parent=neck)
        add_primitive("cube", name + "_hair_side_r", m["hair"],
                      loc=(0.085, -0.0, 0.0), scale=(0.02, 0.09, 0.10),
                      parent=neck)

    # eyes (zombie glows red; alive dark)
    for side, x in (("l", -0.038), ("r", 0.038)):
        e = add_primitive("sphere", name + "_eye_" + side, m["eyes"],
                          scale=(0.016, 0.012, 0.016),
                          loc=(x, -0.088, 0.115), parent=neck, smooth=True)

    # mouth (dark slit)
    mouth = add_primitive("cube", name + "_mouth", mats(False)["hair"],
                          loc=(0, -0.092, 0.045), scale=(0.035, 0.008, 0.012),
                          parent=neck)

    # ---------- arms ----------
    parts["shoulders"], parts["elbows"], parts["hands"] = [], [], []
    for side, x in (("L", -0.20), ("R", 0.20)):
        sh = bpy.data.objects.new(name + "_sh" + side, None)
        sh.location = (x, 0, 1.34)
        sh.parent = root
        bpy.context.collection.objects.link(sh)
        # sleeve (upper arm, points down from shoulder)
        _limb(name + "_uarm" + side, m["shirt"], 0.052, 0.30, sh, True)
        # elbow at bottom of upper arm
        el = bpy.data.objects.new(name + "_el" + side, None)
        el.location = (0, 0, -0.30)
        el.parent = sh
        bpy.context.collection.objects.link(el)
        _limb(name + "_farm" + side, m["skin"], 0.044, 0.26, el, True)
        hand = add_primitive("sphere", name + "_hand" + side, m["skin"],
                             scale=(0.042, 0.05, 0.055),
                             loc=(0, 0, -0.34), parent=el, smooth=True)
        parts["shoulders"].append(sh)
        parts["elbows"].append(el)
        parts["hands"].append(hand)

    # ---------- hips + legs ----------
    parts["hips"], parts["knees"] = [], []
    hip_y = 1.0 if gender == "boy" else 0.98
    for side, x in (("L", -0.09), ("R", 0.09)):
        hip = bpy.data.objects.new(name + "_hip" + side, None)
        hip.location = (x, 0, hip_y)
        hip.parent = root
        bpy.context.collection.objects.link(hip)
        if gender == "boy":
            _limb(name + "_thigh" + side, m["navy"], 0.085, 0.44, hip, True)
            kn = bpy.data.objects.new(name + "_kn" + side, None)
            kn.location = (0, 0, -0.44)
            kn.parent = hip
            bpy.context.collection.objects.link(kn)
            _limb(name + "_shin" + side, m["navy"], 0.068, 0.42, kn, True)
            add_primitive("cube", name + "_shoe" + side, m["shoes"],
                          loc=(0, -0.045, -0.48), scale=(0.075, 0.14, 0.05),
                          parent=kn)
        else:
            # girl: navy skirt + legs
            _limb(name + "_thigh" + side, m["skin"], 0.070, 0.40, hip, True)
            kn = bpy.data.objects.new(name + "_kn" + side, None)
            kn.location = (0, 0, -0.40)
            kn.parent = hip
            bpy.context.collection.objects.link(kn)
            _limb(name + "_shin" + side, m["skin"], 0.055, 0.40, kn, True)
            add_primitive("cube", name + "_shoe" + side, m["shoes"],
                          loc=(0, -0.04, -0.45), scale=(0.06, 0.12, 0.045),
                          parent=kn)
        parts["hips"].append(hip)
        parts["knees"].append(kn)

    if gender == "girl":
        skirt = add_primitive("cone", name + "_skirt", m["navy"],
                              radius1=0.17, radius2=0.24, depth=0.30,
                              loc=(0, 0, 0.78), parent=root, smooth=True)

    root.scale = (scale, scale, scale)
    parts["root"] = root
    parts["name"] = name
    return parts


# ------------------------------------------------------------------
# Animation: zombie walk — deterministic, keyframe-per-frame insertion.
# ------------------------------------------------------------------
def pose_rest(parts):
    """Neutral standing pose values (radians) we always start from."""
    for sh in parts["shoulders"]:
        sh.rotation_euler = (0, 0, 0)
    for el in parts["elbows"]:
        el.rotation_euler = (0, 0, 0)
    for hp in parts["hips"]:
        hp.rotation_euler = (0, 0, 0)
    for kn in parts["knees"]:
        kn.rotation_euler = (0, 0, 0)


def pose_zombie_idle(parts, t=0.0):
    """Hunched, arms forward, ~shuffling sway. Call once per frame then key."""
    pose_rest(parts)
    sway = M.sin(t * 1.3) * 0.06
    # hunch
    parts["neck"].rotation_euler = (0.32 + sway * 0.4, 0, sway * 0.5)
    # arms out front, drooping, slight asymmetric sway
    for i, sh in enumerate(parts["shoulders"]):
        base = -1.25 + (0.12 if i else -0.12)
        sh.rotation_euler = (base + M.sin(t * 1.7 + i * 2.1) * 0.10, 0,
                             (0.15 if i else -0.15) + M.sin(t * 1.1 + i) * 0.05)
    for i, el in enumerate(parts["elbows"]):
        el.rotation_euler = (-0.25 - M.sin(t * 2.3 + i * 1.7) * 0.15, 0, 0)
    # legs shuffle
    for i, hp in enumerate(parts["hips"]):
        hp.rotation_euler = (M.sin(t * 2.0 + i * M.pi) * 0.10, 0,
                             (0.06 if i else -0.06))
    for i, kn in enumerate(parts["knees"]):
        kn.rotation_euler = (0.14 + M.sin(t * 2.0 + i * M.pi) * 0.06, 0, 0)


def animate_zombie_walk(parts, f0, f1, fps=30, speed=0.45, key_every=2):
    """Walk forward along -Y (towards camera at scene setup) between frames."""
    root = parts["root"]
    y0 = root.location.y
    t0 = f0 / fps
    for f in range(f0, f1 + 1, key_every):
        t = f / fps
        root.location.y = y0 - speed * (t - t0)
        root.location.z = M.sin(t * 4.0) * 0.018  # bob
        root.location.x += 0.0  # keep lane
        pose_zombie_idle(parts, t)
        root.keyframe_insert("location", frame=f)
        for grp in ("shoulders", "elbows", "hips", "knees"):
            for p in parts[grp]:
                p.keyframe_insert("rotation_euler", frame=f)
        parts["neck"].keyframe_insert("rotation_euler", frame=f)


def pose_hidden_idle(parts, t=0.0):
    """Living students hiding: still + tiny breathing sway, arms low."""
    pose_rest(parts)
    parts["neck"].rotation_euler = (M.sin(t * 1.1) * 0.05, 0, M.sin(t * 0.7) * 0.06)
    for sh in parts["shoulders"]:
        sh.rotation_euler = (0.10 + M.sin(t * 0.9) * 0.025, 0, 0)


def animate_still_group(parts_list, f0, f1, fps=30, key_every=3, jitter=0.4,
                        pose_fn=None):
    """ '~Frozen still' students: tiny sway only, no forward motion."""
    pose_fn = pose_fn or pose_zombie_idle
    for parts in parts_list:
        for f in range(f0, f1 + 1, key_every):
            t = f / fps
            pose_fn(parts, t * jitter)
            for grp in ("shoulders", "elbows", "hips", "knees"):
                for p in parts[grp]:
                    p.keyframe_insert("rotation_euler", frame=f)
            parts["neck"].keyframe_insert("rotation_euler", frame=f)


def wave_id(parts):
    return abs(parts["name"].__hash__()) % 1000
