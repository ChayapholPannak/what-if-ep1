# hf_common.py — shared helpers for What-If EP.1 Blender pipeline
# Deterministic, no random. Plain bpy, Blender 4.x/5.x compatible.
import math
import bpy


# ---------- scene reset ----------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


# ---------- materials ----------
def new_material(name, base=(0.8, 0.8, 0.8, 1.0), rough=0.5, metallic=0.0,
                 emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = _bsdf(mat)
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None and emission_strength > 0:
        _set_in(mat, "Emission Color", emission)
        _set_in(mat, "Emission Strength", emission_strength)
    return mat


def _bsdf(mat):
    return mat.node_tree.nodes.get("Principled BSDF")


def _set_in(mat, names, value):
    """Set a Principled input trying several known names across versions."""
    bsdf = _bsdf(mat)
    if isinstance(names, str):
        names = [names]
    for n in names:
        if n in bsdf.inputs:
            bsdf.inputs[n].default_value = value
            return True
    return False


# ---------- primitives ----------
def add_primitive(kind, name, mat=None, loc=(0, 0, 0), rot=(0, 0, 0),
                  scale=(1, 1, 1), smooth=False, parent=None, **geo):
    """kind in {cube, sphere, capsule, cylinder, cone, plane, ico}; extra kwargs
    like radius/depth/radius1/radius2 pass straight to the primitive operator."""
    ops_map = {
        "cube": bpy.ops.mesh.primitive_cube_add,
        "sphere": bpy.ops.mesh.primitive_uv_sphere_add,
        "capsule": bpy.ops.mesh.primitive_capsule_add,
        "cylinder": bpy.ops.mesh.primitive_cylinder_add,
        "cone": bpy.ops.mesh.primitive_cone_add,
        "plane": bpy.ops.mesh.primitive_plane_add,
        "ico": bpy.ops.mesh.primitive_ico_sphere_add,
    }
    fn = ops_map[kind]
    try:
        fn(location=loc, **geo)
    except Exception:
        # Blender 5.x removed capsule op — use cylinder (ends hidden by joint spheres)
        if kind == "capsule":
            ops_map["cylinder"](location=loc, **geo)
        else:
            raise
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = rot
    obj.scale = scale
    if smooth:
        bpy.ops.object.shade_smooth()
    if mat is not None:
        obj.data.materials.append(mat)
    if parent is not None:
        obj.parent = parent
    return obj


def unwrap_auto(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66))
    bpy.ops.object.mode_set(mode="OBJECT")


# ---------- deterministic wave (instead of random) ----------
def wave(i, t=0.0, f=1.0):
    """Stable pseudo-chaotic value in [0,1] from integers + time (no random module)."""
    n = (i * 9301 + 49297) % 233280
    return ((n / 233280.0) + t * f) % 1.0


# ---------- frame helpers ----------
def key_objs(objs, frame, offset=0.0, axis_only=None):
    """Insert keyframe at given frame for loc/rot/scale of objects."""
    for obj in objs:
        if offset:
            obj.location = tuple(c + offset for c in obj.location)
        obj.keyframe_insert(data_path="location", frame=frame)
        if axis_only is None:
            obj.keyframe_insert(data_path="rotation_euler", frame=frame)
            obj.keyframe_insert(data_path="scale", frame=frame)


# ---------- render setup ----------
def setup_render(scene, out_dir, prefix="frame", fps=30, res=(1080, 1920),
                 engine=None, samples=64):
    r = scene.render
    r.fps = fps
    r.resolution_x, r.resolution_y = res
    r.resolution_percentage = 100
    r.filepath = out_dir + "/" + prefix + "_"
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGBA"
    # film look
    vs = scene.view_settings
    try:
        vs.view_transform = "AgX"
        vs.look = "AgX - Punchy"
    except Exception:
        pass
    # engine choice: EEVEE Next (4.2+) -> EEVEE -> Cycles fallback chain
    engines = []
    if engine:
        engines = [engine]
    else:
        for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
            engines.append(e)
    chosen = None
    for e in engines:
        try:
            scene.render.engine = e
            chosen = e
            break
        except Exception:
            continue
    if chosen and "EEVEE" in chosen and hasattr(scene, "eevee"):
        ee = scene.eevee
        try:
            # speed: no raytracing (EEVEE Next), few TAA samples, simple shadows
            ee.use_raytracing = False
            ee.taa_render_samples = 8
            ee.use_soft_shadows = False
        except Exception:
            pass
    return chosen


def setup_world(scene, horizon=(0.02, 0.03, 0.06, 1.0), strength=1.0):
    world = bpy.data.worlds.new("Night")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = horizon
    bg.inputs["Strength"].default_value = strength
    return world
