import bpy,math
from mathutils import Vector
VISEMES={'A':(.095,.070,.000),'E':(.110,.030,.000),'I':(.100,.018,-.001),'O':(.057,.058,-.018),'U':(.044,.039,-.028)}
def material(name,color,roughness=.65):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=roughness
 return m
def make_mouth(rig):
 n=48
 def coordinates(w,h,push=0):
  # Fixed upper lip and downward jaw opening under the white moustache.
  zc=1.113-h*.85;front=-.520+push;verts=[]
  for radius,depth in [(1.17,.004),(1.035,-.002),(1,.003),(.92,.020)]:
   for i in range(n):
    a=2*math.pi*i/n;x=w*radius*math.cos(a);z=zc+h*radius*math.sin(a)
    if radius>1:z+=(.008 if math.sin(a)>=0 else -.008)*abs(math.sin(a))
    verts.append((x,front+depth+.012*(x/max(w,.001))**2,z))
  verts.append((0,front+.027,zc))
  # Upper teeth and lower tongue are part of the same morphable mesh.
  th=min(.013,h*.45);tw=w*.70
  verts.extend([(-tw,front+.012,zc+h*.73),(tw,front+.012,zc+h*.73),(tw,front+.012,zc+h*.73-th),(-tw,front+.012,zc+h*.73-th)])
  verts.extend([(w*.50*math.cos(i*2*math.pi/16),front+.013,zc-h*.60+min(h*.20,.012)*math.sin(i*2*math.pi/16)) for i in range(16)])
  return verts
 # Tuck the neutral mesh into the original moustache; avoid a floating closed lip in profile.
 verts=coordinates(.040,.0005,.035)
 faces=[];mats=[]
 for r in range(3):
  for i in range(n):faces.append((r*n+i,r*n+(i+1)%n,(r+1)*n+(i+1)%n,(r+1)*n+i));mats.append([0,1,2][r])
 for i in range(n):faces.append((3*n+i,3*n+(i+1)%n,4*n));mats.append(2)
 faces.append((4*n+1,4*n+2,4*n+3,4*n+4));mats.append(3)
 faces.append(tuple(range(4*n+5,4*n+21)));mats.append(4)
 mesh=bpy.data.meshes.new('Viseme_Mouth_Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 mouth=bpy.data.objects.new('Mouth_Visemes',mesh);bpy.context.scene.collection.objects.link(mouth)
 for m in [material('Mouth skin transition',(.55,.34,.21)),material('Soft natural lip',(.40,.18,.12)),material('Oral cavity',(.025,.007,.010),.9),material('Upper teeth',(.80,.74,.59)),material('Tongue',(.37,.08,.10))]:mesh.materials.append(m)
 for p,idx in zip(mesh.polygons,mats):p.material_index=idx;p.use_smooth=True
 mouth.shape_key_add(name='Basis')
 for name,settings in VISEMES.items():
  key=mouth.shape_key_add(name='viseme_'+name)
  for v,co in zip(key.data,coordinates(*settings)):v.co=co
 mouth['neutral']='All viseme values = 0';mouth['mixing']='Normalize A E I O U weights so total is at most 1.0. Blend toward zero when audio ends.'
 g=mouth.vertex_groups.new(name='head');g.add(list(range(len(mesh.vertices))),1,'REPLACE')
 mod=mouth.modifiers.new('Follow head','ARMATURE');mod.object=rig;mouth.parent=rig
 return mouth
def add_beard_morphs(obj):
 def smooth(a,b,x):t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
 base=[v.co.copy() for v in obj.data.vertices]
 obj.shape_key_add(name='Basis',from_mix=False)
 for name,(_,h,push) in VISEMES.items():
  k=obj.shape_key_add(name='viseme_'+name,from_mix=False)
  for co,d in zip(base,k.data):
   d.co=co
   x,y,z=co
   mask=(1-smooth(.13,.27,abs(x)))*smooth(.27,.43,-y)*(1-smooth(1.05,1.15,z))*smooth(.62,.78,z)
   d.co.z-=h*.80*mask;d.co.y-=h*.14*mask
