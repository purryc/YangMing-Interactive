import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector,Quaternion
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mouth_v2 import make_mouth,add_beard_morphs,VISEMES
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output'/'scholar_voice_rig_v1.blend'))
s=bpy.context.scene;rig=bpy.data.objects['Scholar_Rig'];obj=bpy.data.objects['Scholar_Mesh']
rig.animation_data_clear()
for b in rig.pose.bones:b.location=(0,0,0);b.rotation_quaternion=(1,0,0,0);b.scale=(1,1,1)
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
s.timeline_markers.clear()
def smooth(a,b,x):t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def rot(name,xyz):
 b=rig.pose.bones[name];rest=b.bone.matrix_local.to_quaternion()
 q=Quaternion((1,0,0),math.radians(xyz[0]))@Quaternion((0,1,0),math.radians(xyz[1]))@Quaternion((0,0,1),math.radians(xyz[2]))
 b.rotation_quaternion=rest.inverted()@q@rest
def loc_world(name,delta):
 b=rig.pose.bones[name];b.location=b.bone.matrix_local.to_quaternion().inverted()@Vector(delta)
# Repaint lower sleeves so their own bones preserve the downward fabric drape.
obj.vertex_groups.clear();groups={b.name:obj.vertex_groups.new(name=b.name) for b in rig.data.bones if b.use_deform}
for v in obj.data.vertices:
 x,y,z=v.co;ax=abs(x);side='L' if x>=0 else 'R';w={}
 def add(n,a):
  if a>0:w[n]=w.get(n,0)+a
 head=smooth(.98,1.17,z);beard=smooth(.20,.31,-y)*(1-smooth(1.00,1.16,z))*(1-smooth(.16,.28,ax))*smooth(.67,.79,z);head=max(head,beard);hat=smooth(1.57,1.72,z)
 add('hat',head*hat);add('head',head*(1-hat)*(1-.60*beard));add('beard',head*(1-hat)*.60*beard)
 remain=1-head;inner=.28+.13*(1-smooth(.45,.90,z));arm=smooth(inner,inner+.13,ax)*smooth(.20,.35,z)
 fore=smooth(.53,.72,ax);hand=smooth(.75,.83,ax);sleeve=(1-smooth(.83,1.015,z))*.98
 add('sleeve.'+side,remain*arm*(1-hand)*sleeve)
 add('upper_arm.'+side,remain*arm*(1-fore)*(1-sleeve));add('forearm.'+side,remain*arm*fore*(1-hand)*(1-sleeve));add('hand.'+side,remain*arm*hand)
 body=remain*(1-arm);foot=1-smooth(.12,.22,z);leg=(1-smooth(.20,.36,z))*(1-foot);spine=smooth(.42,.80,z)
 add('foot.'+side,body*foot);add('shin.'+side,body*leg*.4);add('thigh.'+side,body*leg*.6)
 add('pelvis',body*(1-foot-leg)*(1-spine));add('spine',body*(1-foot-leg)*spine*(1-smooth(.88,1.04,z)));add('chest',body*(1-foot-leg)*spine*smooth(.88,1.04,z))
 total=sum(w.values())
 for n,a in w.items():groups[n].add([v.index],a/total,'REPLACE')
mouth=make_mouth(rig);add_beard_morphs(obj)
names=['idle','listen','think','speak','acknowledge','greet','walk','run','wave','shrug','bow','look_around']
def arms(left=72,right=72,forward_l=0,forward_r=0):
 for side,sign,angle,forward in [('L',1,left,forward_l),('R',-1,right,forward_r)]:
  rot('upper_arm.'+side,(forward,sign*angle,0));rot('forearm.'+side,(0,0,sign*-3))
  rot('sleeve.'+side,(-forward*.55,-sign*angle*.95,0))
def pose(kind,t):
 for b in rig.pose.bones:b.location=(0,0,0);b.rotation_quaternion=(1,0,0,0);b.scale=(1,1,1)
 ease=math.sin(math.pi*t)**2;wave=math.sin(math.tau*t);arms()
 rot('spine',(0,.45*wave,0));rot('chest',(.45*wave,0,0))
 if kind=='idle':rot('head',(.6*wave,0,.5*wave))
 elif kind=='listen':rot('neck',(3*ease,0,0));rot('head',(2*ease,-6*ease,2*ease))
 elif kind=='think':rot('head',(-5*ease,4*ease,12*ease))
 elif kind=='speak':
  rhythm=math.sin(6*math.pi*t)*ease;arms(72-22*ease,72,-12*ease,0);rot('forearm.L',(-12*ease,0,-12*ease));rot('head',(2.5*rhythm,0,3*wave*ease));rot('beard',(1.2*rhythm,0,0))
 elif kind=='acknowledge':
  nod=math.sin(math.pi*min(1,max(0,(t-.15)/.6)))**2;rot('neck',(2*nod,0,0));rot('head',(9*nod,0,0))
 elif kind=='greet':arms(72-26*ease,72,-8*ease,0);rot('head',(5*ease,0,-3*ease))
 elif kind in ['walk','run']:
  running=kind=='run';cycles=3 if running else 2;phase=math.tau*cycles*t
  amp=34 if running else 20;lift=.105 if running else .045
  loc_world('pelvis',(0,0,(.026 if running else .010)*(1-math.cos(2*phase))))
  rot('spine',(5 if running else 1,0,0));rot('chest',(0,0,(3 if running else 1.5)*math.sin(phase)))
  for side,shift in [('L',0),('R',math.pi)]:
   p=phase+shift;rot('thigh.'+side,(amp*math.sin(p),0,0));rot('shin.'+side,(-max(0,math.sin(p))*(42 if running else 22),0,0));rot('foot.'+side,(-amp*math.sin(p)+max(0,math.sin(p))*(42 if running else 22),0,0));loc_world('thigh.'+side,(0,0,lift*max(0,math.sin(p))))
  arms(70,70,(19 if running else 9)*math.sin(phase),-(19 if running else 9)*math.sin(phase));rot('head',(-2 if running else 0,0,0));rot('beard',(2.5*math.sin(phase),0,0))
 elif kind=='wave':
  arms(72-54*ease,72,-16*ease,0);rot('forearm.L',(-25*ease,0,-18*ease));rot('hand.L',(8*math.sin(8*math.pi*t)*ease,0,0));rot('head',(0,-3*ease,0))
 elif kind=='shrug':arms(72-24*ease,72-24*ease);loc_world('clavicle.L',(0,0,.032*ease));loc_world('clavicle.R',(0,0,.032*ease));rot('head',(-3*ease,-6*ease,0))
 elif kind=='bow':rot('spine',(12*ease,0,0));rot('head',(7*ease,0,0));arms(72,72,-8*ease,-8*ease)
 elif kind=='look_around':rot('head',(0,0,18*math.sin(math.tau*t)*ease))
 return ease
def vowels(kind,t):
 values={k:0 for k in VISEMES}
 if kind=='speak':
  seq=['A','E','I','O','U','A'];f=t*6;i=min(5,int(f));envelope=math.sin(math.pi*(f-i))**2;values[seq[i]]=envelope*.85
 return values
# All animation is baked, so no Python handler is needed by the saved file.
rig.animation_data_create();mouth.data.shape_keys.animation_data_create();obj.data.shape_keys.animation_data_create();segments=[]
for idx,name in enumerate(names):
 ra=bpy.data.actions.new(name);ra.use_fake_user=True;rig.animation_data.action=ra
 ma=bpy.data.actions.new(name+'.mouth');ma.use_fake_user=True;mouth.data.shape_keys.animation_data.action=ma
 ba=bpy.data.actions.new(name+'.beard');ba.use_fake_user=True;obj.data.shape_keys.animation_data.action=ba
 for frame in range(1,74,2):
  t=(frame-1)/72;pose(name,t);values=vowels(name,t)
  for b in rig.pose.bones:
   b.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=b.name);b.keyframe_insert(data_path='location',frame=frame,group=b.name)
  for mesh in [mouth,obj]:
   for key,value in values.items():
    k=mesh.data.shape_keys.key_blocks['viseme_'+key];k.value=value;k.keyframe_insert(data_path='value',frame=frame)
 if name in ['walk','run']:
  # Ground the stance foot using the actual deformed shoe vertices.
  for frame in range(1,74,2):
   s.frame_set(frame);bpy.context.view_layer.update()
   ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
   floor=min((ev.matrix_world@v.co).z for v in me.vertices)
   ev.to_mesh_clear()
   phase=math.tau*(3 if name=='run' else 2)*(frame-1)/72
   flight=.024*math.sin(phase)**2 if name=='run' else 0
   loc_world('root',(0,0,flight-floor));rig.pose.bones['root'].keyframe_insert(data_path='location',frame=frame,group='root')
 ra.asset_mark();ra.asset_data.description='Voice companion v2: '+name
 segments.append({'name':name,'start':1+idx*72,'end':(idx+1)*72,'duration':3})
for data,suffix in [(rig,''),(mouth.data.shape_keys,'.mouth'),(obj.data.shape_keys,'.beard')]:
 data.animation_data.action=None;tr=data.animation_data.nla_tracks.new();tr.name='Showcase v2'
 for seg in segments:
  st=tr.strips.new(seg['name'],seg['start'],bpy.data.actions[seg['name']+suffix]);st.action_frame_start=1;st.action_frame_end=73;st.frame_end=seg['start']+72;st.extrapolation='NOTHING'
for seg in segments:s.timeline_markers.new(seg['name'],frame=seg['start'])
s.frame_start=1;s.frame_end=864;s.render.fps=24;s.frame_set(1)
rig['usage']='v2: natural lowered arms. 12 actions. Mouth_Visemes has viseme_A/E/I/O/U shape keys; Scholar_Mesh has matching beard morphs.'
rig['speech_mode']='A E I O U morphable mouth. Demo timing is synthetic; external TTS/phoneme timing is not connected.'
s.render.resolution_x=768;s.render.resolution_y=768;s.cycles.samples=20;s.camera=bpy.data.objects['Camera_Front']
out=ROOT/'qa'/'v2';out.mkdir(exist_ok=True)
s.render.filepath=str(ROOT/'output'/'scholar_voice_beauty_v2.png');bpy.ops.render.render(write_still=True)
for name,frame in [('speak',226),('walk',442),('run',511),('wave',613)]:
 s.frame_set(frame);s.render.filepath=str(out/f'{name}.png');bpy.ops.render.render(write_still=True)
s.frame_set(1)
# Close-up mouth reference images, independent of showcase tracks.
for data in [mouth.data.shape_keys,obj.data.shape_keys]:
 for tr in data.animation_data.nla_tracks:tr.mute=True
cam=s.camera;oldloc=cam.location.copy();oldrot=cam.rotation_euler.copy();oldscale=cam.data.ortho_scale
cam.location=(0,-5,1.38);cam.rotation_euler=(Vector((0,-.2,1.29))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.95
for name in ['closed',*VISEMES]:
 for mesh in [mouth,obj]:
  for k in VISEMES:mesh.data.shape_keys.key_blocks['viseme_'+k].value=1 if k==name else 0
 s.render.filepath=str(out/f'viseme_{name}.png');bpy.ops.render.render(write_still=True)
for mesh in [mouth,obj]:
 for k in VISEMES:mesh.data.shape_keys.key_blocks['viseme_'+k].value=0
 for tr in mesh.data.shape_keys.animation_data.nla_tracks:tr.mute=False
cam.location=oldloc;cam.rotation_euler=oldrot;cam.data.ortho_scale=oldscale
s.frame_set(1);s.render.filepath=str(ROOT/'output'/'scholar_voice_beauty_v2.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'output'/'scholar_voice_rig_v2.blend'),compress=True)
(out/'actions.json').write_text(json.dumps(segments,indent=2))
print('V2_SAVED',len(rig.data.bones),'bones',len(names),'actions',len(VISEMES),'visemes')
