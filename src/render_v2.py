import bpy,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/scholar_voice_rig_v2.blend'))
s=bpy.context.scene;s.render.resolution_x=640;s.render.resolution_y=640;s.cycles.samples=8
cam=bpy.data.objects['Camera_Front'];s.camera=cam
original=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.ortho_scale)
dest=ROOT/'qa/v2/frames_final';dest.mkdir(exist_ok=True)
# Sample the unchanged 24fps animation at 12fps, preserving its exact 36s duration.
for i,f in enumerate(range(1,865,2),1):
 path=dest/f'frame_{i:04d}.png'
 if path.exists():continue
 s.frame_set(f)
 if 217<=f<289:
  cam.location=(0,-5,1.38);cam.rotation_euler=(Vector((0,-.2,1.29))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.04
 elif 433<=f<577:
  cam.location=(2.7,-5,1.7);cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.5
 else:cam.location=original[0];cam.rotation_euler=original[1];cam.data.ortho_scale=original[2]
 s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
print('V2_RENDER_COMPLETE',flush=True)
