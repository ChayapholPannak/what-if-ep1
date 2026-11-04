# debug_moon.py — minimal moon visibility test
import bpy, sys, os

here = os.path.dirname(os.path.abspath(__file__))
r = bpy.context.scene.render
r.resolution_x, r.resolution_y, r.resolution_percentage = 480, 480, 50
r.engine = "BLENDER_EEVEE"

mat = bpy.data.materials.new("M"); mat.use_nodes = True
b = mat.node_tree.nodes["Principled BSDF"]
b.inputs["Emission Color"].default_value = (1.0, 0.95, 0.8, 1.0)
b.inputs["Emission Strength"].default_value = 6.0

bpy.ops.mesh.primitive_uv_sphere_add(radius=2.4, location=(0, 30, 12))
obj = bpy.context.active_object
obj.data.materials.append(mat)

camd = bpy.data.cameras.new("C")
camd.lens = 22
cam = bpy.data.objects.new("C", camd)
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam
cam.location = (1.2, -12.5, 1.8)
tgt = bpy.data.objects.new("t", None)
tgt.location = (0, 6, 4.4)
bpy.context.collection.objects.link(tgt)
cam.constraints.new("TRACK_TO").target = tgt

r.filepath = os.path.join(here, "out", "debug_moon.png")
bpy.ops.render.render(write_still=True)
print("### done ->", r.filepath)
