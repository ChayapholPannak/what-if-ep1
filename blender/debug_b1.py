# debug_b1.py — inspect moon vs camera
import sys, os, math
import bpy

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import hf_common as C
import hf_character as CH
import hf_sets as S

C.reset_scene()
CH.MAT_CACHE.clear()
mc = S._mats_common()
S.build_ground(60)
S.build_school(mc)
S.build_moon_and_lights(mc, bpy.context.scene)
cam = bpy.data.objects.get("CamB1")
if cam is None:
    cam_data = bpy.data.cameras.new("CamB1")
    cam = bpy.data.objects.new("CamB1", cam_data)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
cam.location = (1.2, -12.5, 1.8)
cam.data.lens = 22.0
tgt = bpy.data.objects.new("tgt", None)
tgt.location = (0, 6, 4.4)
bpy.context.collection.objects.link(tgt)
cam.constraints.new("TRACK_TO").target = tgt

moon = bpy.data.objects["Moon"]
print("### moon loc:", moon.location[:], "visible:", moon.visible_get())
print("### cam matrix:", [tuple(round(v, 2) for v in row) for row in cam.matrix_world])
print("### clip:", cam.data.clip_start, cam.data.clip_end, "sensor_fit", cam.data.sensor_fit)
mw = moon.matrix_world.translation
from bpy_extras import object_utils

bpy.context.view_layer.update()
fo = cam.matrix_world.to_translation()
dir_cam = (cam.matrix_world.to_quaternion() @ bpy.mathutils_vector.Zero3() if False else None)
# camera forward = -Z of matrix
fwd = (cam.matrix_world.to_3x3() @ bpy_extras.mathutils_vector.Zero3() if False else None)
import mathutils
fwd = cam.matrix_world.to_3x3() @ mathutils.Vector((0, 0, -1))
v = (mw - fo).normalized()
ang = fwd.angle(v)
print("### angle fwd<->moon deg:", math.degrees(ang))
print("### camera data lens:", cam.data.lens, "sensor fit:", cam.data.sensor_fit, "clip_end:", cam.data.clip_end)
hit, loc, nrm, idx, obj, matx = bpy.context.scene.ray_cast(bpy.context.depsgraph, fo, v)
print("### ray_cast hit:", hit, "obj:", obj.name if obj else None, "at:", tuple(round(x, 1) for x in loc) if hit else None)
ndc = object_utils.world_to_camera_view(bpy.context.scene, cam, mw)
print("### moon camview:", tuple(round(x, 3) for x in ndc))
