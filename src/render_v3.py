import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/scholar_voice_rig_v3.blend'))
s=bpy.context.scene;s.render.resolution_x=640;s.render.resolution_y=640;s.cycles.samples=8
cam=bpy.data.objects['Camera_Front'];s.camera=cam
shots=['idle','viseme_demo','eye_demo','express_happy','express_angry','hand_fist','hand_peace','stroke_beard','salute','walk']
segments=json.loads((ROOT/'qa/v3/actions.json').read_text());dest=ROOT/'qa/v3/frames';dest.mkdir(exist_ok=True)
for i,name in enumerate(shots):
 start=next(seg['start'] for seg in segments if seg['name']==name)
 for j in range(36):
  path=dest/f'frame_{i*36+j+1:04d}.png'
  if path.exists():continue
  s.frame_set(start+j*2)
  if name.startswith('hand_'):loc=(.88,-1,2);target=(.88,0,1);scale=.34
  elif name in ['viseme_demo','eye_demo','express_happy','express_angry']:loc=(0,-5,1.38);target=(0,-.2,1.30);scale=.92
  else:loc=(.20 if name!='walk' else 2.3,-5,1.5);target=(0,0,1);scale=2.5
  cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
(ROOT/'qa/v3/preview_shots.json').write_text(json.dumps(shots,indent=2));print('V3_RENDER_COMPLETE',flush=True)
