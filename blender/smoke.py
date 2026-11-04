# smoke.py — verify bpy works headless + probe engine IDs available
import bpy, sys

print("### Blender:", bpy.app.version_string)
scene = bpy.context.scene
r = scene.render
for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES", "BLENDER_WORKBENCH"):
    try:
        old = r.engine
        r.engine = e
        print("### ENGINE OK:", e)
        r.engine = old
    except Exception as ex:
        print("### ENGINE FAIL:", e, "(", ex, ")")

# tiny scene render test
r.resolution_x = 480
r.resolution_y = 480
r.resolution_percentage = 50
try:
    r.engine = "BLENDER_EEVEE_NEXT"
except Exception:
    try:
        r.engine = "BLENDER_EEVEE"
    except Exception:
        r.engine = "CYCLES"
bpy.ops.mesh.primitive_monkey_add()
m = bpy.data.materials.new("m"); m.use_nodes = True
bpy.context.active_object.data.materials.append(m)
bpy.ops.object.light_add(location=(3, -2, 4))
print("### rendering...")
r.filepath = sys.argv[-1]
bpy.ops.render.render(write_still=True)
print("### smoke done ->", r.filepath)
