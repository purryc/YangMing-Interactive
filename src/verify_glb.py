import bpy,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'output'/'scholar_voice_rig_v1.glb'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
obj=max((o for o in bpy.data.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
tracks=rig.animation_data.nla_tracks
rig.animation_data.action=None
out={'imported':True,'bone_count':len(rig.data.bones),'animations':[]}
for track in tracks:
 for t in tracks:t.mute=True
 track.mute=False
 frames=[]
 for f in [1,19,37,55,73]:
  bpy.context.scene.frame_set(f);bpy.context.view_layer.update()
  ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
  coords=[ev.matrix_world@v.co for v in mesh.vertices]
  frames.append(coords);ev.to_mesh_clear()
 delta=max((a-b).length for frame in frames[1:] for a,b in zip(frames[0],frame))
 out['animations'].append({'track':track.name,'deformed_vertex_displacement':delta,'finite':all(math.isfinite(x) for frame in frames for v in frame for x in v)})
out['passed']=len(out['animations'])==6 and all(a['finite'] and a['deformed_vertex_displacement']>.005 for a in out['animations'])
(ROOT/'qa'/'glb_validation.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
