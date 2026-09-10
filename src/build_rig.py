import bpy, math, json
from mathutils import Vector, Quaternion
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'qa'/'extracted_studio.blend'))
s=bpy.context.scene; obj=bpy.data.objects['Scholar_Mesh']
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def bone(name,head,tail,parent=None,deform=True):
 b=rig.data.edit_bones.new(name);b.head=head;b.tail=tail;b.use_deform=deform
 if parent:b.parent=rig.data.edit_bones[parent]
 return b
bpy.ops.object.select_all(action='DESELECT');bpy.ops.object.armature_add();rig=bpy.context.object;rig.name='Scholar_Rig';rig.data.name='Scholar_Skeleton';rig.show_in_front=True
bpy.ops.object.mode_set(mode='EDIT');rig.data.edit_bones.remove(rig.data.edit_bones[0])
bone('root',(0,0,0),(0,0,.18),deform=False)
bone('pelvis',(0,0,.24),(0,0,.52),'root')
bone('spine',(0,0,.52),(0,0,.88),'pelvis')
bone('chest',(0,0,.88),(0,0,1.03),'spine')
bone('neck',(0,0,1.03),(0,0,1.20),'chest')
bone('head',(0,0,1.20),(0,0,1.67),'neck')
bone('hat',(0,.08,1.55),(0,.08,1.95),'head')
bone('jaw',(0,-.20,1.13),(0,-.30,1.02),'head')
bone('beard',(0,-.29,1.08),(0,-.35,.76),'jaw')
for sign,side in [(1,'L'),(-1,'R')]:
 bone('clavicle.'+side,(0,0,1.00),(sign*.29,0,1.00),'chest')
 bone('upper_arm.'+side,(sign*.29,0,1.00),(sign*.57,0,1.00),'clavicle.'+side)
 bone('forearm.'+side,(sign*.57,0,1.00),(sign*.77,0,1.00),'upper_arm.'+side)
 bone('hand.'+side,(sign*.77,0,1.00),(sign*.93,0,1.00),'forearm.'+side)
 bone('sleeve.'+side,(sign*.58,0,.96),(sign*.62,0,.55),'upper_arm.'+side)
 bone('thigh.'+side,(sign*.19,0,.36),(sign*.19,0,.21),'pelvis')
 bone('shin.'+side,(sign*.19,0,.21),(sign*.19,0,.08),'thigh.'+side)
 bone('foot.'+side,(sign*.19,0,.08),(sign*.19,-.20,.05),'shin.'+side)
bpy.ops.object.mode_set(mode='OBJECT')
for b in rig.pose.bones:
 b.rotation_mode='QUATERNION'
 if b.name.startswith(('head','neck','jaw','beard','upper_arm','forearm','hand')):
  b.bone.color.palette='THEME04'
 else:b.bone.color.palette='THEME03'
groups={b.name:obj.vertex_groups.new(name=b.name) for b in rig.data.bones if b.use_deform}
for v in obj.data.vertices:
 x,y,z=v.co;ax=abs(x);side='L' if x>=0 else 'R';w={}
 def add(n,a):
  if a>0:w[n]=w.get(n,0)+a
 head=smooth(.98,1.17,z)
 beard=smooth(.20,.31,-y)*(1-smooth(1.00,1.16,z))*(1-smooth(.16,.28,ax))*smooth(.67,.79,z)
 head=max(head,beard)
 hat=smooth(1.57,1.72,z)
 add('hat',head*hat);add('head',head*(1-hat)*(1-.6*beard));add('beard',head*(1-hat)*.6*beard)
 remain=1-head
 arm_inner=.28+.13*(1-smooth(.45,.90,z))
 arm=smooth(arm_inner,arm_inner+.13,ax)*smooth(.20,.35,z)
 fore=smooth(.53,.72,ax);hand=smooth(.75,.83,ax)
 sleeve=(1-smooth(.78,.99,z))*.5
 add('upper_arm.'+side,remain*arm*(1-fore)*(1-sleeve))
 add('sleeve.'+side,remain*arm*(1-hand)*sleeve)
 add('forearm.'+side,remain*arm*fore*(1-hand)*(1-sleeve))
 add('hand.'+side,remain*arm*hand)
 body=remain*(1-arm)
 foot=1-smooth(.12,.21,z)
 spine=smooth(.42,.80,z)
 add('foot.'+side,body*foot)
 add('pelvis',body*(1-foot)*(1-spine))
 add('spine',body*(1-foot)*spine*(1-smooth(.88,1.04,z)))
 add('chest',body*(1-foot)*spine*smooth(.88,1.04,z))
 total=sum(w.values())
 for n,a in w.items():groups[n].add([v.index],a/total,'REPLACE')
mod=obj.modifiers.new('Weighted deformation','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True;obj.parent=rig
rig['usage']='Actions: idle, listen, think, speak, acknowledge, greet. Root moves whole character. Head/neck/arms/beard are FK controls.'
rig['speech_mode']='Illustrative rhythm, not audio-driven lip sync. Eyes and mouth remain baked in source texture.'

def rot_world(name,xyz):
 b=rig.pose.bones[name];rest=b.bone.matrix_local.to_quaternion()
 q=Quaternion((1,0,0),math.radians(xyz[0]))@Quaternion((0,1,0),math.radians(xyz[1]))@Quaternion((0,0,1),math.radians(xyz[2]))
 b.rotation_quaternion=rest.inverted()@q@rest
def pose(kind,t):
 for b in rig.pose.bones:b.location=(0,0,0);b.rotation_quaternion=(1,0,0,0);b.scale=(1,1,1)
 ease=math.sin(math.pi*t)**2;wave=math.sin(2*math.pi*t)
 # Relax the arms while keeping enough lateral room for the large sleeves.
 rot_world('upper_arm.L',(0,25,0));rot_world('upper_arm.R',(0,-25,0))
 rot_world('spine',(0,.65*wave,0));rot_world('chest',(.7*wave,0,0))
 if kind=='idle':rot_world('head',(.7*wave,0,.65*wave))
 elif kind=='listen':
  rot_world('neck',(3*ease,0,0));rot_world('head',(2*ease,-6*ease,2*ease))
 elif kind=='think':
  rot_world('head',(-5*ease,4*ease,10*ease));rot_world('forearm.R',(0,0,-6*ease))
 elif kind=='speak':
  rhythm=math.sin(6*math.pi*t)*ease
  rot_world('head',(2.5*rhythm,0,3*wave*ease));rot_world('upper_arm.L',(-5*ease,25-13*ease,0));rot_world('forearm.L',(-7*ease,0,-8*ease));rot_world('hand.L',(0,0,4*rhythm));rot_world('jaw',(1.8*abs(rhythm),0,0));rot_world('beard',(1.3*rhythm,0,.5*wave))
 elif kind=='acknowledge':
  nod=math.sin(math.pi*min(1,max(0,(t-.15)/.6)))**2
  rot_world('neck',(2*nod,0,0));rot_world('head',(9*nod,0,0));rot_world('beard',(-1.8*wave*ease,0,0))
 elif kind=='greet':
  rot_world('spine',(3*ease,0,0));rot_world('upper_arm.L',(-4*ease,25-23*ease,0));rot_world('forearm.L',(0,-8*ease,-8*ease));rot_world('hand.L',(0,6*math.sin(6*math.pi*t)*ease,0));rot_world('head',(4*ease,0,-3*ease))
 for side in ['L','R']:rot_world('sleeve.'+side,(1.0*math.sin(2*math.pi*t-.5)*ease,0,0))

rig.animation_data_create()
names=['idle','listen','think','speak','acknowledge','greet'];segments=[]
for idx,name in enumerate(names):
 action=bpy.data.actions.new(name);action.use_fake_user=True;rig.animation_data.action=action
 for frame in range(1,74,3):
  pose(name,(frame-1)/72)
  for b in rig.pose.bones:
   b.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=b.name)
   b.keyframe_insert(data_path='location',frame=frame,group=b.name)
 action.asset_mark();action.asset_data.description='Voice interaction: '+name
 segments.append({'name':name,'start':1+idx*72,'end':(idx+1)*72,'seconds':3})
rig.animation_data.action=None
track=rig.animation_data.nla_tracks.new();track.name='Voice interaction showcase'
for seg in segments:
 strip=track.strips.new(seg['name'],seg['start'],bpy.data.actions[seg['name']]);strip.action_frame_start=1;strip.action_frame_end=73;strip.frame_end=seg['start']+72;strip.blend_type='REPLACE';strip.extrapolation='NOTHING'
 s.timeline_markers.new(seg['name'],frame=seg['start'])
s.frame_start=1;s.frame_end=432;s.render.fps=24;s.frame_set(1)
# Soft neutral stage, editable lighting and three proof cameras.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.012));ground=bpy.context.object;ground.name='Studio_Ground'
mat=bpy.data.materials.new('Warm gray studio');mat.diffuse_color=(.17,.185,.20,1);ground.data.materials.append(mat)
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.30,1)
s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
cam=s.camera;cam.name='Camera_Front';cam.location=(.20,-5,1.4);aim(cam,(0,0,1));cam.data.ortho_scale=2.50
for name,loc in [('Camera_Back',(0,5,1.25)),('Camera_Side',(5,0,1.25))]:
 c=cam.copy();c.data=cam.data.copy();s.collection.objects.link(c);c.name=name;c.location=loc;aim(c,(0,0,1))
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
s.render.resolution_x=768;s.render.resolution_y=768;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
ref=bpy.data.images.load(str(ROOT/'reference'/'character_sheet.png'));ref.name='Reference character sheet';ref.pack();ref.use_fake_user=True
for im in bpy.data.images:
 if im.source=='FILE':
  try:im.pack()
  except:pass
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
s.render.filepath=str(ROOT/'output'/'scholar_voice_beauty.png');bpy.ops.render.render(write_still=True)
for name,frame in [('listen',109),('think',181),('speak',253),('acknowledge',325),('greet',397)]:
 s.frame_set(frame);s.render.filepath=str(ROOT/'qa'/('pose_'+name+'.png'));bpy.ops.render.render(write_still=True)
s.frame_set(1)
for name in ['Back','Side']:
 s.camera=bpy.data.objects['Camera_'+name];s.render.filepath=str(ROOT/'qa'/('rigged_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
s.camera=cam;s.render.filepath=str(ROOT/'qa'/'frames'/'frame_');s.cycles.samples=8;s.render.resolution_x=640;s.render.resolution_y=640
(ROOT/'qa'/'frames').mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'output'/'scholar_voice_rig_v1.blend'),compress=True)
(ROOT/'qa'/'actions.json').write_text(json.dumps(segments,indent=2))
print('RIG_SAVED',len(rig.data.bones),'bones',len(names),'actions')
