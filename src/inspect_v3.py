import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/scholar_voice_rig_v2.blend'))
ob=bpy.data.objects['Scholar_Mesh'];vs=[v.co for v in ob.data.vertices];tree=BVHTree.FromPolygons(vs,[p.vertices for p in ob.data.polygons])
out=[]
for z in [1.20,1.27,1.33,1.38,1.43,1.48,1.53]:
 for x in [.08,.16,.23]:
  co,n,idx,d=tree.ray_cast(Vector((x,-2,z)),Vector((0,1,0)))
  out.append({'x':x,'z':z,'y':co.y if co else None})
print(json.dumps(out))
