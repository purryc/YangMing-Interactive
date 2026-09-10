import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'output'/'base_basic_pbr.glb'))
obj=next(o for o in bpy.context.scene.objects if o.type=='MESH')
for v in obj.data.vertices:v.co=obj.matrix_world@v.co
obj.matrix_world.identity()
bm=bmesh.new();bm.from_mesh(obj.data)
remove=[v for v in bm.verts if v.co.x>-.32 or v.co.z<-.12]
bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(obj.data);bm.free()
pts=[v.co for v in obj.data.vertices];lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)])
shift=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z));scale=2/(hi.z-lo.z)
for v in obj.data.vertices:v.co=(v.co-shift)*scale
obj.name='Scholar_Mesh'
for p in obj.data.polygons:p.use_smooth=True
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'qa'/'extracted_character.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'output'/'scholar_source_extracted.glb'),export_format='GLB')
report={'extraction':'Top-left complete character from multi-view reconstruction','raw_region':{'x_max':-.32,'z_min':-.12},'vertices':len(obj.data.vertices),'faces':len(obj.data.polygons),'height':2.0,'bounds':[list(lo),list(hi)]}
(ROOT/'qa'/'extraction.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
