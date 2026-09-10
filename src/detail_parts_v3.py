import bpy,math
from mathutils import Vector
TAU=math.tau
def material(name,col,rough=.5,metal=0,noise=False):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if noise:
  n=m.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=75;n.inputs['Detail'].default_value=3
  bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.008;m.node_tree.links.new(n.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 return m
class Mesh:
 def __init__(self):self.v=[];self.f=[];self.mat=[];self.weights=[]
 def surface(self,rings,mat,bone,closed=True):
  start=len(self.v);n=len(rings[0]);self.v.extend(p for ring in rings for p in ring);self.weights.extend([bone]*(len(rings)*n))
  for j in range(len(rings)-1):
   for i in range(n if closed else n-1):self.f.append((start+j*n+i,start+j*n+(i+1)%n,start+(j+1)*n+(i+1)%n,start+(j+1)*n+i));self.mat.append(mat)
 def ellipsoid(self,center,scale,mat,bone,n=20,k=12):
  c=Vector(center);self.surface([[tuple(c+Vector((scale[0]*math.sin(math.pi*j/k)*math.cos(TAU*i/n),scale[1]*math.sin(math.pi*j/k)*math.sin(TAU*i/n),scale[2]*math.cos(math.pi*j/k)))) for i in range(n)] for j in range(k+1)],mat,bone)
 def tube(self,points,radii,mat,bone,n=12):
  pts=list(map(Vector,points));rings=[]
  for j,p in enumerate(pts):
   d=(pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)]).normalized();u=d.cross(Vector((0,0,1)))
   if u.length<.01:u=d.cross(Vector((0,1,0)))
   u.normalize();v=d.cross(u).normalized();rings.append([tuple(p+radii[j]*(math.cos(TAU*i/n)*u+math.sin(TAU*i/n)*v)) for i in range(n)])
  self.surface(rings,mat,bone)
 def object(self,name,materials,rig):
  me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(self.v,[],self.f);me.update();ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob)
  for m in materials:me.materials.append(m)
  for p,m in zip(me.polygons,self.mat):p.material_index=m;p.use_smooth=True
  for bone in set(self.weights):
   g=ob.vertex_groups.new(name=bone);g.add([i for i,b in enumerate(self.weights) if b==bone],1,'REPLACE')
  mod=ob.modifiers.new('Character skin','ARMATURE');mod.object=rig;ob.parent=rig
  return ob
def make_boots(rig):
 mats=[material('Boot charcoal woven cloth',(.020,.021,.024),.82,noise=True),material('Boot warm welt',(.28,.25,.20),.75),material('Boot sole rubber',(.012,.013,.015),.86),material('Boot stitching',(.065,.059,.049),.8)]
 b=Mesh()
 for sign,side in [(1,'L'),(-1,'R')]:
  x=sign*.19;bone='foot.'+side
  b.surface([[(x+.12*r*math.cos(TAU*i/40),-.07+.20*r*math.sin(TAU*i/40),z) for i in range(40)] for z,r in [(.028,.97),(.042,1),(.085,.97),(.122,.82),(.155,.45),(.162,0)]],0,bone)
  # Layered flattened sole and welt with distinct thickness.
  for z,mat,w,l in [(.014,2,.121,.201),(.033,1,.122,.201)]:
   b.surface([[(x+w*math.cos(TAU*i/40),-.07+l*math.sin(TAU*i/40),z+dz) for i in range(40)] for dz in [-.009,.009]],mat,bone)
  b.surface([[(x+(.079+.003*math.sin(j*2))*math.cos(TAU*i/32),.015+(.088+.004*math.cos(j*2))*math.sin(TAU*i/32),z) for i in range(32)] for j,z in enumerate([.11,.14,.18,.22,.27,.28])],0,bone)
  b.tube([(x+.082*math.cos(TAU*i/48),.015+.092*math.sin(TAU*i/48),.28) for i in range(49)],[.004]*49,3,bone)
  b.tube([(x,-.25,.065),(x,-.235,.11),(x,-.17,.15),(x,-.078,.19),(x,-.075,.28)],[.0025]*5,3,bone)
  b.tube([(x,.106,z) for z in [.06,.11,.18,.28]],[.0025]*4,3,bone)
  # Fine sole tread, visible in lifted-foot and bottom views.
  for y in [-.21,-.16,-.11,-.06,-.01,.04]:b.tube([(x-.075,y,.004),(x+.075,y,.004)],[.003,.003],2,bone,n=6)
 return b.object('Boots_Detailed',mats,rig)
def finger_layout(sign):
 out={}
 for i,(name,length) in enumerate([('index',.100),('middle',.112),('ring',.101),('pinky',.080)]):
  y=-.0525+i*.035;start=Vector((sign*.86,y,1.0));end=Vector((sign*(.86+length),y*1.18,1.0));out[name]=[start.lerp(end,t) for t in [0,.38,.72,1]]
 out['thumb']=[Vector((sign*x,y,z)) for x,y,z in [(.807,-.046,1.0),(.834,-.075,.996),(.859,-.093,.991),(.880,-.102,.991)]]
 return out
def add_finger_bones(rig):
 bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 for sign,side in [(1,'L'),(-1,'R')]:
  for finger,pts in finger_layout(sign).items():
   for j in range(3):
    name=f'{finger}_{j+1}.{side}';b=rig.data.edit_bones.new(name);b.head=pts[j];b.tail=pts[j+1];b.parent=rig.data.edit_bones['hand.'+side if j==0 else f'{finger}_{j}.{side}'];b.use_connect=j>0
 bpy.ops.object.mode_set(mode='OBJECT')
 for b in rig.pose.bones:b.rotation_mode='QUATERNION'
def make_hands(rig):
 mats=[material('Hand warm skin',(.64,.39,.25),.52),material('Soft fingernails',(.73,.48,.36),.4),material('Palm creases',(.43,.24,.15),.7)]
 m=Mesh();details=Mesh()
 for sign,side in [(1,'L'),(-1,'R')]:
  m.ellipsoid((sign*.827,0,1),(.057,.060,.027),0,'hand.'+side,24,16)
  m.ellipsoid((sign*.777,0,1),(.040,.042,.023),0,'hand.'+side)
  for finger,pts in finger_layout(sign).items():
   r=.0125 if finger=='pinky' else .0148
   for j in range(3):
    bone=f'{finger}_{j+1}.{side}';p=pts[j];q=pts[j+1]
    m.tube([p,p.lerp(q,.5),q],[r*(1-.1*j),r*(1-.08*j),r*(.97-.1*j)],0,bone)
    m.ellipsoid(p,(r*.95,r*.95,r*.95),0,bone,12,8)
   m.ellipsoid(pts[-1],(r*.70,r*.70,r*.75),0,f'{finger}_3.{side}',16,10)
   tip=pts[2].lerp(pts[3],.55);tip.z+=r*.85;details.ellipsoid(tip,(.009,.009,.0015),1,f'{finger}_3.{side}',16,8)
  for dy in [-.020,.006]:details.tube([(sign*x,dy+.008*math.sin(t*math.pi),.974) for t,x in [(0,.803),(.5,.826),(1,.845)]],[.0006]*3,2,'hand.'+side,n=6)
 ob=m.object('Hands_Articulated',mats,rig)
 from mathutils.kdtree import KDTree
 tree=KDTree(len(m.v))
 for i,p in enumerate(m.v):tree.insert(p,i)
 tree.balance();bpy.context.view_layer.objects.active=ob
 # Unite intersecting construction surfaces into a smooth continuous hand skin.
 mod=ob.modifiers.new('Unified organic hand surface','REMESH');mod.mode='VOXEL';mod.voxel_size=.0028;mod.use_smooth_shade=True
 bpy.ops.object.modifier_apply(modifier=mod.name)
 smooth=ob.modifiers.new('Hand surface relaxation','SMOOTH');smooth.factor=.65;smooth.iterations=3;bpy.ops.object.modifier_apply(modifier=smooth.name)
 ob.vertex_groups.clear();groups={n:ob.vertex_groups.new(name=n) for n in set(m.weights)}
 def smooth(a,b,x):t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
 for v in ob.data.vertices:
  side='L' if v.co.x>=0 else 'R';sign=1 if side=='L' else -1;candidates=[]
  for name,pts in finger_layout(sign).items():
   axis=pts[-1]-pts[0];u=(v.co-pts[0]).dot(axis)/axis.length_squared;q=pts[0]+axis*max(0,min(1,u));candidates.append(((v.co-q).length,name,u))
  _,name,u=min(candidates);finger=smooth(-.12,.14,u);second=smooth(.25,.51,u);third=smooth(.59,.84,u)
  ws={'hand.'+side:1-finger,f'{name}_1.{side}':finger*(1-second),f'{name}_2.{side}':finger*second*(1-third),f'{name}_3.{side}':finger*third}
  for n,w in ws.items():
   if w>0:groups[n].add([v.index],w,'REPLACE')
 details.object('Hand_Nails_Creases',mats,rig)
 return ob

def make_sleeves(rig):
 from pathlib import Path
 cloth=material('V3 blue patterned sleeve cloth',(.15,.21,.26),.8,noise=True)
 im=bpy.data.images.load(str(Path(__file__).resolve().parents[1]/'reference/hands_boots_v3.png'),check_existing=True);im.pack();tex=cloth.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;cloth.node_tree.links.new(tex.outputs['Color'],cloth.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
 lining=material('V3 sleeve inner lining',(.065,.09,.11),.85);trim=material('V3 ivory cuff piping',(.47,.44,.35),.85)
 m=Mesh()
 for sign,side in [(1,'L'),(-1,'R')]:
  rings=[]
  for j in range(15):
   t=j/14;x=sign*(.29+.49*t);r=.10+.14*t
   rings.append([(x,(.085+.048*t)*math.sin(TAU*i/48),1.035-r*(1-math.cos(TAU*i/48))) for i in range(48)])
  m.surface(rings,0,'upper_arm.'+side)
  m.surface([[(sign*.78,(.133-d)*math.sin(TAU*i/48),1.035-(.24-d)*(1-math.cos(TAU*i/48))) for i in range(48)] for d in [0,.008]],2,'forearm.'+side)
  m.surface([[ (sign*x,.125*math.sin(TAU*i/48),1.027-.23*(1-math.cos(TAU*i/48))) for i in range(48)] for x in [.72,.78]],1,'forearm.'+side)
 ob=m.object('Sleeves_Retopo', [cloth,lining,trim],rig)
 ob.vertex_groups.clear();groups={n:ob.vertex_groups.new(name=n) for n in ['upper_arm.L','upper_arm.R','forearm.L','forearm.R','sleeve.L','sleeve.R']}
 for v in ob.data.vertices:
  side='L' if v.co.x>=0 else 'R';t=max(0,min(1,(abs(v.co.x)-.47)/.20));t=t*t*(3-2*t)
  gravity=max(0,min(1,(.96-v.co.z)/.15))*.92
  groups['upper_arm.'+side].add([v.index],(1-t)*(1-gravity),'REPLACE');groups['forearm.'+side].add([v.index],t*(1-gravity),'REPLACE');groups['sleeve.'+side].add([v.index],gravity,'REPLACE')
 uv=ob.data.uv_layers.new(name='SleeveReference')
 for p in ob.data.polygons:
  for li in p.loop_indices:
   co=ob.data.vertices[ob.data.loops[li].vertex_index].co;t=(abs(co.x)-.29)/.49
   uv.data[li].uv=((70+70*t)/2048,1-(477+32*((co.z-.53)/.51))/1152)
 return ob
