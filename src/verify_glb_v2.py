import bpy,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'output/scholar_voice_rig_v2.glb'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');obj=max((o for o in bpy.data.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
meshes=[o for o in bpy.data.objects if o.type=='MESH' and o.data.shape_keys];owners=[rig]+[o.data.shape_keys for o in meshes]
for data in owners:data.animation_data.action=None
names=[t.name for t in rig.animation_data.nla_tracks];out={'animations':[],'morph_meshes':[o.name for o in meshes],'bones':len(rig.data.bones)}
for name in names:
 for data in owners:
  for t in data.animation_data.nla_tracks:t.mute=t.name!=name
 frames=[];values=[]
 for frame in range(1,74,3):
  bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();frames.append([ev.matrix_world@v.co for v in me.vertices]);ev.to_mesh_clear()
  values.append([k.value for k in meshes[0].data.shape_keys.key_blocks][1:])
 out['animations'].append({'name':name,'movement':max((a-b).length for f in frames[1:] for a,b in zip(frames[0],f)),'loop_endpoint_delta':max((a-b).length for a,b in zip(frames[0],frames[-1])),'max_mouth_weight':max(v for vals in values for v in vals),'finite':all(math.isfinite(x) for f in frames for v in f for x in v)})
out['mouth_key_tests']=[]
for data in owners:
 for t in data.animation_data.nla_tracks:t.mute=True
for ob in meshes:
 keys=ob.data.shape_keys.key_blocks
 for k in list(keys)[1:]:k.value=0
 def coords():
  bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();co=[v.co.copy() for v in me.vertices];ev.to_mesh_clear();return co
 neutral=coords()
 for k in list(keys)[1:]:
  k.value=1;full=coords();k.value=0;zero=coords()
  out['mouth_key_tests'].append({'mesh':ob.name,'key':k.name,'delta':max((a-b).length for a,b in zip(neutral,full)),'reset_error':max((a-b).length for a,b in zip(neutral,zero))})
out['passed']=len(names)==12 and len(meshes)==2 and all(a['finite'] and a['movement']>.002 for a in out['animations']) and next(a for a in out['animations'] if a['name']=='speak')['max_mouth_weight']>.5 and all(t['delta']>.001 and t['reset_error']<1e-5 for t in out['mouth_key_tests']) and all(a['loop_endpoint_delta']<.002 for a in out['animations'] if a['name'] in ['walk','run'])
(ROOT/'qa/v2/glb_validation.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
