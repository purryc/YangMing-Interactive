import bpy, json, math, os
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
source=next((ROOT/'output').glob('*.glb'))
bpy.ops.import_scene.gltf(filepath=str(source))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
lo=Vector(tuple(min(p[i] for p in points) for i in range(3)))
hi=Vector(tuple(max(p[i] for p in points) for i in range(3)))
print('BOUNDS',list(lo),list(hi))
report={'source':source.name,'bounds':[list(lo),list(hi)],'objects':[{'name':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'materials':[m.name if m else None for m in o.data.materials]} for o in meshes]}
(ROOT/'qa'/'mesh_inspection.json').write_text(json.dumps(report,indent=2))
center=(lo+hi)/2
for o in meshes:
 for v in o.data.vertices: v.co=o.matrix_world@v.co
 o.matrix_world.identity()
 for v in o.data.vertices: v.co=(v.co-Vector((center.x,center.y,lo.z)))*(2/(hi.z-lo.z))
 for p in o.data.polygons:p.use_smooth=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12
scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.world.color=(0.45,0.45,0.45)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size in [('Key',(3,-4,5),650,4),('Fill',(-3,-1,3),400,3),('Rim',(0,3,4),650,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,(0,0,1))
bpy.ops.object.camera_add(location=(0,-5,1.1));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=2.65;scene.camera=cam
scene.view_settings.view_transform='Standard'
for name,loc in [('front',(0,-5,1.05)),('back',(0,5,1.05)),('side',(5,0,1.05))]:
 cam.location=loc;aim(cam,(0,0,1));scene.render.filepath=str(ROOT/'qa'/f'source_{name}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'qa'/'source_inspected.blend'))
