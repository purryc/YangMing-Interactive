import bpy,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from detail_parts_v3 import Mesh,material,TAU
VISEMES={'A':(.093,.067,0),'E':(.105,.043,0),'I':(.107,.023,0),'O':(.049,.053,-.013),'U':(.029,.025,-.024),'MBP':(.064,.001,-.005),'FV':(.078,.016,0),'TH':(.073,.031,0),'TDNL':(.074,.041,0),'CHSHZH':(.043,.025,-.013),'KGNG':(.081,.049,0)}
EXPRESSIONS=['Happy','Angry','Sad','Laughing','Surprised','Thinking','Proud','Helpless']
EYE_KEYS=['blink_L','blink_R','squint','wide','gaze_L','gaze_R','gaze_U','gaze_D']
def mouth_mesh(kind):
 if kind.startswith('viseme_'):w,h,push=VISEMES[kind[7:]]
 elif kind.startswith('expr_'):
  w,h,push={'Happy':(.098,.027,0),'Angry':(.086,.026,0),'Sad':(.065,.009,0),'Laughing':(.102,.060,0),'Surprised':(.055,.066,0),'Thinking':(.057,.002,0),'Proud':(.073,.007,0),'Helpless':(.068,.003,0)}[kind[5:]]
 else:w,h,push=.042,.0005,.080
 m=Mesh();zc=1.105-h*.77;front=-.522+push
 smile=.012 if kind in ['expr_Happy','expr_Laughing','expr_Proud','viseme_E','viseme_I'] else -.006 if kind in ['expr_Sad','expr_Helpless'] else 0
 def ring(radius,depth):return [(w*radius*math.cos(TAU*i/64),front+depth+.012*math.cos(TAU*i/64)**2,zc+h*radius*math.sin(TAU*i/64)+smile*math.cos(TAU*i/64)**2) for i in range(64)]
 m.surface([ring(1.09,0),ring(1,.001)],0,'head');m.surface([ring(1,.001),ring(.92,.018),[(0,front+.021,zc)]*64],1,'head')
 # Individual teeth follow an arched dental row rather than a single flat rectangle.
 for lower in [False,True]:
  for i in range(8):
   x=(i-3.5)*w*.18;y=front+.009+.014*(x/w)**2
   z=zc+(-h*.66 if lower else h*.69)+smile*(x/w)**2
   if kind=='viseme_FV' and lower:z+=h*.50
   ht=min(h*.20,.010);m.ellipsoid((x,y,z),(w*.088,.007,max(.0001,ht)),2,'head',12,8)
 tz=zc-h*.63;ty=front+.008
 if kind=='viseme_TH':tz=zc-h*.15;ty=front-.010
 if kind=='viseme_TDNL':tz=zc+h*.40
 m.ellipsoid((0,ty,tz),(w*.43,.007,max(.0001,min(.012,h*.23))),3,'head',24,10)
 # Moustache locks arch around the opening and follow each mouth target.
 for sign in [-1,1]:
  for j in range(5):
   pts=[(sign*x,front-.003+j*.001,z) for x,z in [(w*.12,zc+h+.024+j*.002),(w*.45,zc+h+.018-j*.001),(w*.85,zc+h*.75+.010-j*.001),(w*1.22,zc+h*.17-j*.003)]]
   m.tube(pts,[.004,.005,.004,.0002],4,'head',8)
 return m
def make_mouth(rig):
 mats=[material('V3 subtle lip',(.53,.28,.19),.6),material('V3 oral cavity',(.022,.004,.006),.8),material('V3 ivory enamel',(.83,.79,.67),.3),material('V3 tongue',(.42,.095,.095),.52),material('V3 moustache locks',(.80,.78,.69),.75)]
 base=mouth_mesh('Basis');ob=base.object('Mouth_Visemes',mats,rig);ob.shape_key_add(name='Basis',from_mix=False).value=0
 for key in ['viseme_'+k for k in VISEMES]+['expr_'+k for k in EXPRESSIONS]:
  vs=mouth_mesh(key).v;k=ob.shape_key_add(name=key,from_mix=False);k.value=0
  for d,p in zip(k.data,vs):d.co=p
 return ob
def make_eyes(rig,body):
 tree=BVHTree.FromPolygons([v.co for v in body.data.shape_keys.key_blocks['Basis'].data],[list(p.vertices) for p in body.data.polygons])
 def surface(x,z):
  p,_,_,_=tree.ray_cast(Vector((x,-2,z)),Vector((0,1,0)))
  return p.y if p else -.35
 def build(key):
  m=Mesh()
  for sign,side in [(1,'L'),(-1,'R')]:
   cx=sign*.159;cz=1.250;w=.086;h=.090
   blink=1 if key=='blink_'+side else .65 if key=='squint' else 1 if key in ['expr_Happy','expr_Laughing'] else .45 if key in ['expr_Helpless','expr_Proud'] else 0
   opened=1-blink;opened=max(.007,opened)*(1.17 if key in ['wide','expr_Surprised'] else 1)
   dx=.027 if key=='gaze_L' else -.027 if key=='gaze_R' else .017 if key=='expr_Thinking' else 0
   dz=.024 if key=='gaze_U' else -.028 if key=='gaze_D' else .012 if key=='expr_Thinking' else 0
   def point(x,z,front=.010):return (x,surface(x,z)-front,z)
   def eye_point(x,z,front=0):return (x,surface(cx,cz)-.029+sign*.42*(x-cx)+.65*((x-cx)**2+(z-cz)**2)-front,z)
   # Skin eyelid annulus covers the baked eye and opens around the new eyeball.
   outer=[];inner=[]
   for i in range(64):
    a=TAU*i/64;x=cx+w*math.cos(a);z=cz+h*math.sin(a)*opened
    if key=='expr_Angry' and math.sin(a)>0:z-=.029*(1-sign*math.cos(a))*.5
    outer.append(point(cx+w*1.32*math.cos(a),cz+h*1.24*math.sin(a),.001))
    inner.append(eye_point(x,z))
   rings=[]
   for t in [0,.25,.5,.75,1]:
    ring=[]
    for p,q in zip(outer,inner):
     x=p[0]*(1-t)+q[0]*t;z=p[2]*(1-t)+q[2]*t
     y=(surface(x,z)-.001)*(1-t)+eye_point(x,z)[1]*t;ring.append((x,y,z))
    rings.append(ring)
   m.surface(rings,0,'head')
   m.surface([inner,[eye_point(cx,cz)]*64],1,'head')
   # Iris/pupil projected and clipped by the eyelids, independent of gaze direction.
   for radius,mat in [(.067,2),(.055,3),(.034,4)]:
    rings=[]
    for rr in [1,.65,.0]:
     ring=[]
     for i in range(48):
      x=cx+dx+radius*rr*math.cos(TAU*i/48);raw=cz+dz+radius*rr*math.sin(TAU*i/48)
      boundary=h*opened*math.sqrt(max(0,1-((x-cx)/w)**2))*.97
      z=max(cz-boundary,min(cz+boundary,raw));ring.append(eye_point(x,z,.004+mat*.001))
     rings.append(ring)
    m.surface(rings,mat,'head')
   if opened>.02:
    m.ellipsoid(eye_point(cx+dx-.023,cz+dz+.032,.012),(.009,.001,.009*opened),5,'head',12,8)
   else:
    m.ellipsoid((cx+dx-.023,surface(cx,cz),cz),(.011,.002,.0001),5,'head',12,8)
   # Upper and lower eyelid edge; same topology for every shape.
   for upper in [True,False]:
    pts=[]
    for i in range(33):
     a=math.pi*i/32+(0 if upper else math.pi);x=cx+w*math.cos(a);z=cz+h*math.sin(a)*opened
     if key=='expr_Angry' and upper:z-=.029*(1-sign*math.cos(a))*.5
     pts.append(eye_point(x,z,.010))
    m.tube(pts,[.0028 if upper else .0014]*33,7 if upper else 0,'head',8)
   # Brow cover and layered white eyebrow wisps.
   bx=cx;bz=1.367
   m.surface([[point(bx+.112*rr*math.cos(TAU*i/48),bz+.043*rr*math.sin(TAU*i/48),.001+.005*(1-rr)) for i in range(48)] for rr in [1,.8,.6,.4,.2,0]],0,'head')
   for j in range(9):
    pts=[]
    for i in range(12):
     u=i/11;x=cx+sign*(-.080+.160*u);z=bz+.013*math.sin(math.pi*u)+j*.0015
     if key=='expr_Angry':z+=.030*(u-.5)
     if key in ['expr_Sad','expr_Helpless']:z+=.035*(.5-u)
     if key in ['expr_Surprised','wide']:z+=.028
     if key=='expr_Thinking':z+=.018*sign
     pts.append(point(x,z,.018+j*.001))
    m.tube(pts,[.001+.004*math.sin(math.pi*i/11) for i in range(12)],6,'head',8)
  return m
 mats=[material('V3 eyelid skin',(.63,.405,.28),.65),material('V3 eye sclera',(.88,.85,.76),.3),material('V3 limbal ring',(.048,.019,.007),.3),material('V3 amber iris',(.20,.073,.017),.3),material('V3 pupil and lid line',(.009,.005,.003),.28),material('V3 eye catchlight',(.98,.98,.93),.16),material('V3 brows white',(.83,.81,.73),.72)]
 mats.append(material('V3 dark eyelid edge',(.02,.012,.006),.6))
 m=build('Basis');ob=m.object('Face_Controls',mats,rig);ob.shape_key_add(name='Basis',from_mix=False).value=0
 for key in EYE_KEYS+['expr_'+k for k in EXPRESSIONS]:
  k=ob.shape_key_add(name=key,from_mix=False);k.value=0;vs=build(key).v;assert len(vs)==len(k.data)
  for d,p in zip(k.data,vs):d.co=p
 # Color-match eyelid boundaries to the existing UV texture, avoiding flat skin badges.
 import numpy as np
 from mathutils.geometry import barycentric_transform
 source=next(n.image for n in body.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image and 'base' in n.image.name.lower()) if any(n.type=='TEX_IMAGE' and n.image and 'base' in n.image.name.lower() for n in body.data.materials[0].node_tree.nodes) else next(n.image for n in body.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image)
 pixels=np.empty(len(source.pixels),dtype=np.float32);source.pixels.foreach_get(pixels);pixels=pixels.reshape(source.size[1],source.size[0],4);uvs=body.data.uv_layers.active.data
 def sample(x,z):
  co,_,idx,_=tree.ray_cast(Vector((x,-2,z)),Vector((0,1,0)))
  if co is None:return (.63,.405,.28,1)
  poly=body.data.polygons[idx];ls=list(poly.loop_indices)[:3];ids=[body.data.loops[i].vertex_index for i in ls];ps=[body.data.shape_keys.key_blocks['Basis'].data[i].co for i in ids];uv=[Vector((*uvs[i].uv,0)) for i in ls];p=barycentric_transform(co,*ps,*uv)
  return pixels[int(max(0,min(1,p.y))*(source.size[1]-1)),int(max(0,min(1,p.x))*(source.size[0]-1))]
 colors=ob.data.color_attributes.new(name='SkinMatch',type='FLOAT_COLOR',domain='POINT')
 for i,v in enumerate(ob.data.vertices):
  x,y,z=v.co;sign=1 if x>=0 else -1;cx=sign*.159
  skin=np.array(sample(sign*.040,1.31));original=np.array(sample(x,z));r=math.sqrt(((x-cx)/.086)**2+((z-1.250)/.09)**2)
  rb=math.sqrt(((x-cx)/.112)**2+((z-1.367)/.043)**2)
  colors.data[i].color=(.55,.37,.26,1)
 vc=mats[0].node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='SkinMatch';mats[0].node_tree.links.new(vc.outputs['Color'],mats[0].node_tree.nodes['Principled BSDF'].inputs['Base Color'])
 # Use the supplied reference's iris appearance on the independently moving iris geometry.
 from pathlib import Path
 ref=bpy.data.images.load(str(Path(__file__).resolve().parents[1]/'reference/visemes_v3.png'),check_existing=True);ref.pack()
 iris=material('Reference amber iris',(.2,.08,.02),.23);tex=iris.node_tree.nodes.new('ShaderNodeTexImage');tex.image=ref;iris.node_tree.links.new(tex.outputs['Color'],iris.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
 for slot in [2,3,4]:ob.data.materials[slot]=iris if slot!=4 else mats[4]
 # One textured iris disk; remove redundant pupil/color disks visually by sharing UV mapping.
 ob.data.materials[4]=iris
 uv=ob.data.uv_layers.new(name='ReferenceIris')
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;cx=.159 if v.x>=0 else -.159
   uv.data[li].uv=((124+(v.x-cx)/.067*29)/2048,1-(227-(v.z-1.250)/.067*29)/1152)
 return ob
