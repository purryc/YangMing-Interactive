import bpy,sys,json,math,bmesh
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from detail_parts_v3 import add_finger_bones,make_hands,make_boots,make_sleeves,Mesh,material
from face_v3 import make_mouth,make_eyes,VISEMES,EXPRESSIONS
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/scholar_voice_rig_v2.blend'))
s=bpy.context.scene;rig=bpy.data.objects['Scholar_Rig'];body=bpy.data.objects['Scholar_Mesh'];qa=ROOT/'qa/v3';qa.mkdir(exist_ok=True)
s.frame_set(1)
for tr in rig.animation_data.nla_tracks:tr.mute=True
for tr in body.data.shape_keys.animation_data.nla_tracks:tr.mute=True
for k in body.data.shape_keys.key_blocks:k.value=0
for b in rig.pose.bones:b.location=(0,0,0);b.rotation_quaternion=(1,0,0,0)
bpy.data.objects.remove(bpy.data.objects['Mouth_Visemes'],do_unlink=True)
# Remove only source hands/shoes; Blender edit operations preserve UVs and existing morph topology.
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body;body.active_shape_key_index=0
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='DESELECT');bm=bmesh.from_edit_mesh(body.data)
remove=[v for v in bm.verts if (abs(v.co.x)>.37 and .25<v.co.z<1.07) or (abs(v.co.x)>.786 and v.co.z>.90) or v.co.z<.153]
bmesh.ops.delete(bm,geom=remove,context='VERTS');bmesh.update_edit_mesh(body.data);bpy.ops.object.mode_set(mode='OBJECT')
assert len(body.data.vertices)>3000
add_finger_bones(rig);hands=make_hands(rig);boots=make_boots(rig);sleeves=make_sleeves(rig);mouth=make_mouth(rig);eyes=make_eyes(rig,body)
# Matching beard response for new consonants; never accumulate previous morph deltas.
base=[v.co.copy() for v in body.data.shape_keys.key_blocks['Basis'].data]
def smooth(a,b,x):t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
for key,h in [('viseme_'+n,p[1]) for n,p in VISEMES.items() if n not in ['A','E','I','O','U']]+[('expr_'+n,.05 if n in ['Laughing','Surprised'] else .015) for n in EXPRESSIONS]:
 k=body.shape_key_add(name=key,from_mix=False);k.value=0
 for d,co in zip(k.data,base):
  d.co=co;x,y,z=co;mask=(1-smooth(.13,.27,abs(x)))*smooth(.27,.43,-y)*(1-smooth(1.05,1.15,z))*smooth(.62,.78,z);d.co.z-=h*.8*mask
# Restore rear hat tie strips as real cloth ribbons, retaining source hat mesh.
m=Mesh()
for sign in [-1,1]:
 rings=[]
 for i in range(16):
  t=i/15;x=sign*(.055+.025*math.sin(t*math.pi));y=.27+.045*math.sin(t*math.pi);z=1.53-.46*t
  rings.append([(x+dx,y,z+.008*math.sin(t*7+dx*30)) for dx in [-.024,.024]])
 m.surface(rings,0,'hat',closed=False)
m.ellipsoid((0,.28,1.51),(.064,.025,.032),0,'hat')
ribbons=m.object('Hat_Ribbons', [material('Hat ribbon charcoal',(.025,.026,.028),.85,noise=True)],rig)
# Reinstate the v2 idle pose without altering its saved source.
for tr in rig.animation_data.nla_tracks:tr.mute=False
s.frame_set(1);bpy.context.view_layer.update()
s.render.resolution_x=768;s.render.resolution_y=768;s.cycles.samples=16
cam=bpy.data.objects['Camera_Front'];s.camera=cam
def shot(name,loc,target,scale):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(qa/(name+'.png'));bpy.ops.render.render(write_still=True)
shot('neutral',(0,-5,1.4),(0,0,1),2.5)
shot('face_neutral',(0,-5,1.38),(0,-.2,1.30),.92)
eyes.data.shape_keys.key_blocks['blink_L'].value=1;eyes.data.shape_keys.key_blocks['blink_R'].value=1
shot('face_blink',(0,-5,1.38),(0,-.2,1.30),.92)
eyes.data.shape_keys.key_blocks['blink_L'].value=0;eyes.data.shape_keys.key_blocks['blink_R'].value=0
mouth.data.shape_keys.key_blocks['viseme_A'].value=1;body.data.shape_keys.key_blocks['viseme_A'].value=1
shot('mouth_a',(0,-5,1.38),(0,-.2,1.30),.92)
mouth.data.shape_keys.key_blocks['viseme_A'].value=0;body.data.shape_keys.key_blocks['viseme_A'].value=0
shot('boots',(.6,-2,.5),(0,-.04,.14),.82)
for tr in rig.animation_data.nla_tracks:tr.mute=True
for b in rig.pose.bones:b.location=(0,0,0);b.rotation_quaternion=(1,0,0,0)
bpy.context.view_layer.update();shot('hand_open',(.87,-1,2),(.87,0,1),.32)
for tr in rig.animation_data.nla_tracks:tr.mute=False
s.frame_set(1);cam.location=(.2,-5,1.4);cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.5
for p in (ROOT/'reference').glob('*_v3.png'):
 im=bpy.data.images.load(str(p));im.pack();im.use_fake_user=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(qa/'details.blend'),compress=True)
print('DETAILS_V3_READY',len(rig.data.bones),flush=True)
