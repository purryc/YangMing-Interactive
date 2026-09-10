import bpy,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from detail_parts_v3 import material
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/scholar_voice_rig_v3.blend'))
body=bpy.data.objects['Scholar_Mesh'];s=bpy.context.scene;s.frame_set(1)
skin=material('Unified facial skin v3',(.55,.37,.26),.65);body.data.materials.append(skin);slot=len(body.data.materials)-1
base=body.data.shape_keys.key_blocks['Basis'].data
for p in body.data.polygons:
 co=sum((base[i].co for i in p.vertices),Vector())/len(p.vertices);x,y,z=co
 if y<-.17 and ((1.19<z<1.545 and abs(x)<.30) or (1.37<z<1.545 and abs(x)<.345)):
  p.material_index=slot
cam=bpy.data.objects['Camera_Front'];s.camera=cam;cam.location=(0,-5,1.38);cam.rotation_euler=(Vector((0,-.2,1.30))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.92;s.cycles.samples=16;s.render.resolution_x=768;s.render.resolution_y=768;s.render.filepath=str(ROOT/'qa/v3/face_surface_unified.png');bpy.ops.render.render(write_still=True)
cam.location=(.20,-5,1.4);cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.5
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'qa/v3/unified_surface.blend'),compress=True)
