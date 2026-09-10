import bpy,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/scholar_voice_rig_v2.blend'))
s=bpy.context.scene;rig=bpy.data.objects['Scholar_Rig'];obj=bpy.data.objects['Scholar_Mesh'];mouth=bpy.data.objects['Mouth_Visemes']
segments=json.loads((ROOT/'qa/v2/actions.json').read_text());report={'bones':len(rig.data.bones),'samples':[],'shape_keys':{},'weight_errors':0}
for ob in [obj,mouth]:
 for v in ob.data.vertices:
  if abs(sum(g.weight for g in v.groups)-1)>1e-5:report['weight_errors']+=1
 keys=ob.data.shape_keys.key_blocks
 report['shape_keys'][ob.name]={k.name:max((v.co-b.co).length for v,b in zip(k.data,keys[0].data)) for k in list(keys)[1:]}
for seg in segments:
 coords=[];floors=[];hands=[]
 for f in range(seg['start'],seg['end']+1,3):
  s.frame_set(f);bpy.context.view_layer.update();ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();co=[ev.matrix_world@v.co for v in m.vertices];coords.append(co);floors.append(min(p.z for p in co));ev.to_mesh_clear()
  hands.append([list(rig.matrix_world@rig.pose.bones['hand.'+side].head) for side in ['L','R']])
 report['samples'].append({'name':seg['name'],'min_z':min(floors),'max_floor_z':max(floors),'movement':max((a-b).length for frame in coords[1:] for a,b in zip(coords[0],frame)),'finite':all(math.isfinite(x) for frame in coords for v in frame for x in v),'hands_first':hands[0]})
print(json.dumps(report,indent=2),flush=True)
s.render.resolution_x=640;s.render.resolution_y=640;s.cycles.samples=12
for name,frame in [('walk_stride',442),('run_stride',511)]:
 s.frame_set(frame)
 for angle in ['Front','Side']:
  s.camera=bpy.data.objects['Camera_'+angle];s.render.filepath=str(ROOT/'qa/v2'/f'{name}_{angle}.png');bpy.ops.render.render(write_still=True)
for data,suffix in [(rig,''),(mouth.data.shape_keys,'.mouth'),(obj.data.shape_keys,'.beard')]:
 data.animation_data.action=None
 for tr in list(data.animation_data.nla_tracks):data.animation_data.nla_tracks.remove(tr)
 for seg in segments:
  tr=data.animation_data.nla_tracks.new();tr.name=seg['name'];st=tr.strips.new(seg['name'],1,bpy.data.actions[seg['name']+suffix]);st.action_frame_start=1;st.action_frame_end=73;st.extrapolation='NOTHING'
s.frame_set(1);bpy.ops.object.select_all(action='DESELECT')
for ob in [rig,obj,mouth]:ob.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(ROOT/'output/scholar_voice_rig_v2.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_skins=True,export_force_sampling=True,export_morph=True)
report['passed']=report['weight_errors']==0 and all(p['finite'] and p['min_z']>-.03 and p['movement']>.002 for p in report['samples']) and all(len(ks)==5 and all(v>0 for v in ks.values()) for ks in report['shape_keys'].values()) and max(report['shape_keys']['Scholar_Mesh'].values())<.07
(ROOT/'qa/v2/rig_validation.json').write_text(json.dumps(report,indent=2));assert report['passed']
