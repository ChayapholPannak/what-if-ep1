# test_c_scenes.py — render ONE preview frame per new scene (small res)
# Usage: blender -b -P test_c_scenes.py
import sys, os, importlib, bpy

BASE = r"C:\Users\USER\OneDrive\Documents\Default Project\whatif-ep1\blender"
OUTD = os.path.join(BASE, "out_test")
sys.path.insert(0, BASE)


def run(scene_name, frame):
    sys.argv = ["blender", "--", "--scene", scene_name, "--out", OUTD]
    import render_scenes
    importlib.reload(render_scenes)
    R = render_scenes
    import hf_common as C

    def single_go(out_name, frames, prefix="t", _f=frame):
        out_dir = os.path.join(OUTD, out_name)
        os.makedirs(out_dir, exist_ok=True)
        scene = bpy.context.scene
        C.setup_render(scene, out_dir, prefix="t", fps=R.FPS)
        scene.render.resolution_x, scene.render.resolution_y = 540, 960
        scene.render.resolution_percentage = 100
        scene.frame_start = scene.frame_end = _f
        bpy.ops.render.render(write_still=True)
        print("### TEST DONE", out_name)

    R.go = single_go
    R.SCENES[scene_name]()


run("c3", 75)
run("c4", 80)
print("### ALL TESTS DONE")
