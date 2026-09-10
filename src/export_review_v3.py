import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from face_v3 import VISEMES,EXPRESSIONS,EYE_KEYS
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/scholar_voice_rig_v3.blend'))
s=bpy.context.scene;rig=bpy.data.objects['Scholar_Rig'];meshes=[o for o in bpy.data.objects if o.type=='MESH' and o.parent==rig];owners=[(rig,'')]+[(bpy.data.objects[n].data.shape_keys,suf) for n,suf in [('Scholar_Mesh','.beard'),('Mouth_Visemes','.mouth'),('Face_Controls','.eyes')]]
segments=json.loads((ROOT/'qa/v3/actions.json').read_text());r={'bones':len(rig.data.bones),'meshes':{},'actions':[]}
for ob in meshes:
 errors=sum(abs(sum(g.weight for g in v.groups)-1)>1e-4 for v in ob.data.vertices);r['meshes'][ob.name]={'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons),'weight_errors':errors,'shape_keys':[k.name for k in list(ob.data.shape_keys.key_blocks)[1:]] if ob.data.shape_keys else []}
for seg in segments:
 frames=[];floors=[]
 for f in [seg['start'],seg['start']+18,seg['start']+36,seg['start']+54]:
  s.frame_set(f);bpy.context.view_layer.update();coords=[]
  for ob in meshes:
   ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();coords.extend(ev.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
  frames.append(coords);floors.append(min(p.z for p in coords))
 r['actions'].append({'name':seg['name'],'movement':max((a-b).length for f in frames[1:] for a,b in zip(frames[0],f)),'floor_min':min(floors),'finite':all(math.isfinite(x) for f in frames for v in f for x in v)})
r['packed_images']=all(im.packed_file for im in bpy.data.images if im.source=='FILE');r['passed']=all(m['weight_errors']==0 and m['vertices']>0 for m in r['meshes'].values()) and r['packed_images'] and all(a['finite'] and a['floor_min']>-.035 for a in r['actions'])
(ROOT/'qa/v3/rig_validation.json').write_text(json.dumps(r,indent=2));print(json.dumps({'passed':r['passed'],'bones':r['bones'],'bad_actions':[a for a in r['actions'] if not a['finite'] or a['floor_min']<-.035],'bad_meshes':{n:m for n,m in r['meshes'].items() if m['weight_errors']}}),flush=True)
s.frame_set(1)
for data,suffix in owners:
 data.animation_data.action=None
 for tr in list(data.animation_data.nla_tracks):data.animation_data.nla_tracks.remove(tr)
 for seg in segments:
  tr=data.animation_data.nla_tracks.new();tr.name=seg['name'];st=tr.strips.new(seg['name'],1,bpy.data.actions[seg['name']+suffix]);st.action_frame_start=1;st.action_frame_end=73;st.extrapolation='NOTHING'
bpy.ops.object.select_all(action='DESELECT')
for ob in [rig,*meshes]:ob.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(ROOT/'output/scholar_voice_rig_v3.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_skins=True,export_force_sampling=True,export_morph=True)
# Gallery is intentionally separate from the saved animation state.
for data,_ in owners:
 for tr in data.animation_data.nla_tracks:tr.mute=True
rig.animation_data.action=bpy.data.actions['idle'];s.frame_set(1);s.cycles.samples=12;s.render.resolution_x=640;s.render.resolution_y=640;cam=bpy.data.objects['Camera_Front'];s.camera=cam
def shot(name,loc,target,scale):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(ROOT/'qa/v3'/(name+'.png'));bpy.ops.render.render(write_still=True)
for name in ['closed',*VISEMES,*EYE_KEYS,*['expr_'+e for e in EXPRESSIONS]]:
 for owner,_ in owners[1:]:
  for k in list(owner.key_blocks)[1:]:k.value=1 if k.name in [name,'viseme_'+name] else 0
 if name=='closed':
  shot('beauty',(0,-5,1.4),(0,0,1),2.5)
 shot('control_'+name,(0,-5,1.38),(0,-.2,1.30),.92)
for owner,_ in owners[1:]:
 for k in list(owner.key_blocks)[1:]:k.value=0
shot('back',(0,5,1.4),(0,0,1),2.5);shot('side',(5,0,1.4),(0,0,1),2.5)
for ob in meshes:ob.hide_render=ob.name!='Boots_Detailed'
shot('boot_detail',(.6,-1,.6),(0,-.04,.14),.82)
print('V3_EXPORT_GALLERY_READY',flush=True)
assert r['passed']
