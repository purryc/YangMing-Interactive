import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from face_v3 import VISEMES,EXPRESSIONS
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'qa/v3/details.blend'))
s=bpy.context.scene;rig=bpy.data.objects['Scholar_Rig'];body=bpy.data.objects['Scholar_Mesh'];mouth=bpy.data.objects['Mouth_Visemes'];eyes=bpy.data.objects['Face_Controls'];boots=bpy.data.objects['Boots_Detailed']
owners=[body.data.shape_keys,mouth.data.shape_keys,eyes.data.shape_keys]
for ob in [rig,*owners]:ob.animation_data_clear();ob.animation_data_create()
old=['idle','listen','think','speak','acknowledge','greet','walk','run','wave','shrug','bow','look_around']
sources={n:bpy.data.actions[n] for n in old}
for n,a in sources.items():a.name='v2_source_'+n
names=old+['shake_head','stroke_beard','salute','hands_on_hips','point','peace','pinch','clap']+['hand_'+n for n in ['open','fist','point','peace','pinch']]+['express_'+n.lower() for n in EXPRESSIONS]+['viseme_demo','eye_demo']
def rotate(name,xyz):
 b=rig.pose.bones[name];q=b.bone.matrix_local.to_quaternion();r=Quaternion((1,0,0),math.radians(xyz[0]))@Quaternion((0,1,0),math.radians(xyz[1]))@Quaternion((0,0,1),math.radians(xyz[2]));b.rotation_quaternion=q.inverted()@r@q
def fingers(side,kind,amount=1):
 sign=1 if side=='L' else -1
 for f in ['thumb','index','middle','ring','pinky']:
  curl=0 if kind=='open' else 1
  if kind=='point' and f=='index':curl=0
  if kind=='peace' and f in ['index','middle']:curl=0
  if kind=='pinch':curl=.80 if f=='index' else .55 if f=='thumb' else .12
  for j,angle in enumerate([65,85,55],1):rotate(f'{f}_{j}.{side}',(0,sign*angle*curl*amount,sign*(15 if f=='thumb' and j==1 else 0)*curl*amount))
  if kind=='peace' and f in ['index','middle']:rotate(f'{f}_1.{side}',(0,0,sign*(-9 if f=='index' else 9)*amount))
  if kind=='pinch' and f=='thumb':rotate('thumb_1.'+side,(0,sign*35*amount,sign*35*amount))
def reach(side,target):
 # Analytic two-bone arm positioning, baked back to standard FK channels.
 sign=1 if side=='L' else -1;bpy.context.view_layer.update();a=rig.pose.bones['upper_arm.'+side];f=rig.pose.bones['forearm.'+side];h=rig.pose.bones['hand.'+side]
 origin=a.head.copy();dest=Vector(target);d=dest-origin;distance=min(.476,max(.086,d.length));direction=d.normalized();l1=a.bone.length;l2=f.bone.length
 along=(l1*l1-l2*l2+distance*distance)/(2*distance);height=math.sqrt(max(0,l1*l1-along*along));pole=Vector((sign,.15,-.8));perp=(pole-direction*pole.dot(direction)).normalized();elbow=origin+direction*along+perp*height;dest=origin+direction*distance
 def place(b,p,q):
  rest=b.bone.tail_local-b.bone.head_local;rotation=rest.rotation_difference((q-p).normalized())@b.bone.matrix_local.to_quaternion();b.matrix=Matrix.Translation(p)@rotation.to_matrix().to_4x4()
 place(a,origin,elbow);bpy.context.view_layer.update();place(f,elbow,dest);bpy.context.view_layer.update();place(h,dest,dest+Vector((0,-.1,.03)))
 # Sleeve keeps a downward long axis while following the arm attachment.
 sleeve=rig.pose.bones['sleeve.'+side];p=sleeve.head.copy();sleeve.matrix=Matrix.Translation(p)@sleeve.bone.matrix_local.to_quaternion().to_matrix().to_4x4()
def envelope(t):
 if t<.25:return .5-.5*math.cos(math.pi*t/.25)
 if t>.78:return .5-.5*math.cos(math.pi*(1-t)/.22)
 return 1
segments=[]
for index,name in enumerate(names):
 frames=[]
 for frame in range(1,74,3):
  rig.animation_data.action=sources[name if name in old else 'idle'];s.frame_set(frame);bpy.context.view_layer.update()
  for b in rig.pose.bones:
   if any(b.name.startswith(f+'_') for f in ['thumb','index','middle','ring','pinky']):b.rotation_quaternion=(1,0,0,0);b.location=(0,0,0)
  t=(frame-1)/72;e=envelope(t)
  if name.startswith('hand_'):
   for b in rig.pose.bones:b.rotation_quaternion=(1,0,0,0);b.location=(0,0,0)
   fingers('L',name[5:],e);fingers('R',name[5:],e)
  elif name in ['point','peace','pinch']:
   side='L';p=rig.pose.bones['hand.L'].head.copy();target=Vector((.32,-.27,1.12));reach(side,p.lerp(target,e));fingers(side,name,e)
  elif name=='salute' or name=='clap':
   for side,sign in [('L',1),('R',-1)]:
    p=rig.pose.bones['hand.'+side].head.copy();gap=.042 if name=='salute' else .04+.08*(.5+.5*math.cos(t*math.pi*8));reach(side,p.lerp(Vector((sign*gap,-.25,.96)),e));fingers(side,'fist' if side=='R' and name=='salute' else 'open',e*.65)
  elif name=='stroke_beard':
   p=rig.pose.bones['hand.R'].head.copy();reach('R',p.lerp(Vector((-.065,-.37,.87+.028*math.sin(t*math.pi*4))),e));fingers('R','pinch',e*.6);rotate('head',(0,-5*e,0))
  elif name=='hands_on_hips':
   for side,sign in [('L',1),('R',-1)]:
    p=rig.pose.bones['hand.'+side].head.copy();reach(side,p.lerp(Vector((sign*.26,-.12,.58)),e));fingers(side,'fist',e*.65)
   rotate('head',(-4*e,0,0))
  elif name=='shake_head':rotate('head',(0,0,13*math.sin(t*math.pi*4)*e))
  if name in ['walk','run']:
   bpy.context.view_layer.update();ev=boots.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();floor=min((ev.matrix_world@v.co).z for v in me.vertices);ev.to_mesh_clear();phase=math.tau*(3 if name=='run' else 2)*t
   target=.024*math.sin(phase)**2 if name=='run' else 0;rb=rig.pose.bones['root'];rb.location+=rb.bone.matrix_local.to_quaternion().inverted()@Vector((0,0,target-floor))
  frames.append((frame,{b.name:(tuple(b.location),tuple(b.rotation_quaternion)) for b in rig.pose.bones}))
 action=bpy.data.actions.new(name);action.use_fake_user=True;action.asset_mark();rig.animation_data.action=action
 for frame,pose in frames:
  for b in rig.pose.bones:
   b.location,b.rotation_quaternion=pose[b.name];b.keyframe_insert(data_path='location',frame=frame,group=b.name);b.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=b.name)
 for owner,suffix in zip(owners,['beard','mouth','eyes']):
  a=bpy.data.actions.new(name+'.'+suffix);a.use_fake_user=True;owner.animation_data.action=a
  for frame in range(1,74,3):
   t=(frame-1)/72;e=envelope(t);values={k.name:0 for k in list(owner.key_blocks)[1:]}
   if name in ['speak','viseme_demo']:
    seq=list(VISEMES) if name=='viseme_demo' else ['A','E','I','O','U','A'];f=t*len(seq);i=min(len(seq)-1,int(f));key='viseme_'+seq[i]
    if key in values:values[key]=.85*math.sin(math.pi*(f-i))**2
   if name.startswith('express_'):
    ex=next(n for n in EXPRESSIONS if n.lower()==name[8:]);key='expr_'+ex
    if key in values:values[key]=e
   if suffix=='eyes':
    if name=='eye_demo':
     seq=['gaze_L','gaze_R','gaze_U','gaze_D','blink_L','blink_R'];f=t*6;i=min(5,int(f));values[seq[i]]=math.sin(math.pi*(f-i))**2
    elif not name.startswith('express_'):
     blink=max(0,1-abs(t-.43)/.055);values['blink_L']=blink;values['blink_R']=blink
    if name in ['salute','bow']:values['blink_L']=e*.9;values['blink_R']=e*.9
    if name=='stroke_beard':values['gaze_D']=e*.5
   for key,v in values.items():owner.key_blocks[key].value=v;owner.key_blocks[key].keyframe_insert(data_path='value',frame=frame)
 segments.append({'name':name,'start':index*72+1,'end':(index+1)*72,'duration':3})
for ob,suffix in [(rig,''),*zip(owners,['.beard','.mouth','.eyes'])]:
 ob.animation_data.action=None;track=ob.animation_data.nla_tracks.new();track.name='Showcase v3'
 for seg in segments:
  st=track.strips.new(seg['name'],seg['start'],bpy.data.actions[seg['name']+suffix]);st.action_frame_start=1;st.action_frame_end=73;st.frame_end=seg['start']+72;st.extrapolation='NOTHING'
s.timeline_markers.clear()
for seg in segments:s.timeline_markers.new(seg['name'],frame=seg['start'])
s.frame_start=1;s.frame_end=len(names)*72;s.frame_set(1);s.render.fps=24
(ROOT/'qa/v3/actions.json').write_text(json.dumps(segments,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'output/scholar_voice_rig_v3.blend'),compress=True)
s.cycles.samples=12;s.render.resolution_x=640;s.render.resolution_y=640;cam=s.camera
def shot(name,loc,target,scale):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(ROOT/'qa/v3'/f'{name}.png');bpy.ops.render.render(write_still=True)
for name in ['salute','stroke_beard','point','hands_on_hips','clap']:
 seg=next(x for x in segments if x['name']==name);s.frame_set(seg['start']+36);shot(name,(.15,-5,1.5),(0,0,1),2.5)
for name in ['fist','point','peace','pinch']:
 seg=next(x for x in segments if x['name']=='hand_'+name);s.frame_set(seg['start']+36);shot('hand_'+name,(.88,-1,2),(.88,0,1),.32)
print('V3_ANIMATED',len(names),'actions',flush=True)
