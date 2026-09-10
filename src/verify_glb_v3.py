import bpy,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(ROOT/'output/scholar_voice_rig_v3.glb'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');meshes=[o for o in bpy.data.objects if o.type=='MESH' and o.find_armature()==rig];owners=[rig]+[o.data.shape_keys for o in meshes if o.data.shape_keys]
for data in owners:data.animation_data.action=None
names=[t.name for t in rig.animation_data.nla_tracks];r={'bones':len(rig.data.bones),'clips':[],'morphs':{},'technical_passed':False}
for name in names:
 for data in owners:
  for tr in data.animation_data.nla_tracks:tr.mute=tr.name!=name
 frames=[];weights=[]
 for f in [1,19,37,55,73]:
  bpy.context.scene.frame_set(f);bpy.context.view_layer.update();co=[]
  for ob in meshes:
   ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();co.extend(ev.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
  frames.append(co);weights.append(max([k.value for data in owners[1:] for k in list(data.key_blocks)[1:]]))
 r['clips'].append({'name':name,'movement':max((a-b).length for f in frames[1:] for a,b in zip(frames[0],f)),'endpoint_delta':max((a-b).length for a,b in zip(frames[0],frames[-1])),'morph_max':max(weights),'finite':all(math.isfinite(x) for f in frames for v in f for x in v)})
for ob in meshes:
 if ob.data.shape_keys:
  r['morphs'][ob.name]=[k.name for k in list(ob.data.shape_keys.key_blocks)[1:]]
r['technical_passed']=r['bones']==55 and len(names)==35 and len(r['morphs'])==3 and all(c['finite'] for c in r['clips']) and all(c['endpoint_delta']<.005 for c in r['clips'] if c['name'] in ['walk','run'])
r['visual_status']='revise: eyelid/brow seams and sleeve/contact fidelity remain below the supplied reference; technical pass is not visual signoff'
(ROOT/'qa/v3/glb_validation.json').write_text(json.dumps(r,indent=2));print(json.dumps({'technical_passed':r['technical_passed'],'bones':r['bones'],'clips':len(names),'morph_meshes':len(r['morphs'])}),flush=True);assert r['technical_passed']
