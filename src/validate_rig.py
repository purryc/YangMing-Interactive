import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output'/'scholar_voice_rig_v1.blend'))
s=bpy.context.scene;rig=bpy.data.objects['Scholar_Rig'];obj=bpy.data.objects['Scholar_Mesh']
r={'reopened':True,'bones':len(rig.data.bones),'vertices':len(obj.data.vertices),'faces':len(obj.data.polygons),'actions':sorted(a.name for a in bpy.data.actions if a.name in ['idle','listen','think','speak','acknowledge','greet']),'weight_errors':0,'max_weight_error':0,'pose_samples':[]}
for v in obj.data.vertices:
 err=abs(sum(g.weight for g in v.groups)-1);r['max_weight_error']=max(r['max_weight_error'],err)
 if err>1e-5:r['weight_errors']+=1
r['packed_images']=all(i.packed_file for i in bpy.data.images if i.source=='FILE')
r['armature_modifier']=any(m.type=='ARMATURE' and m.object==rig for m in obj.modifiers)
rest_edges=[(obj.data.vertices[e.vertices[0]].co-obj.data.vertices[e.vertices[1]].co).length for e in obj.data.edges]
ref=None;max_displacement=0;max_stretch=0
for f in [1,19,37,55,73,109,145,181,217,235,253,271,289,325,361,379,397,415,432]:
 s.frame_set(f);bpy.context.view_layer.update();ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();coords=[ev.matrix_world@v.co for v in m.vertices]
 if ref is None:ref=coords
 displacement=max((a-b).length for a,b in zip(ref,coords));max_displacement=max(max_displacement,displacement)
 ratios=[]
 for e,d in zip(m.edges,rest_edges):
  if d>1e-4:ratios.append((coords[e.vertices[0]]-coords[e.vertices[1]]).length/d)
 max_stretch=max(max_stretch,max(ratios))
 r['pose_samples'].append({'frame':f,'finite':all(math.isfinite(c) for p in coords for c in p),'floor_z':min(p.z for p in coords),'max_displacement_from_idle':displacement,'max_edge_stretch':max(ratios)})
 ev.to_mesh_clear()
r['max_displacement']=max_displacement;r['max_edge_stretch']=max_stretch
r['passed']=r['weight_errors']==0 and r['packed_images'] and r['armature_modifier'] and len(r['actions'])==6 and max_displacement>.05 and max_stretch<4 and all(p['finite'] and p['floor_z']>-.05 for p in r['pose_samples'])
s.frame_set(1)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);obj.select_set(True);bpy.context.view_layer.objects.active=rig
for track in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(track)
for name in r['actions']:
 track=rig.animation_data.nla_tracks.new();track.name=name
 strip=track.strips.new(name,1,bpy.data.actions[name]);strip.action_frame_start=1;strip.action_frame_end=73;strip.extrapolation='NOTHING'
bpy.ops.export_scene.gltf(filepath=str(ROOT/'output'/'scholar_voice_rig_v1.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_skins=True,export_force_sampling=True)
(ROOT/'qa'/'rig_validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));assert r['passed'],'Rig validation failed'
