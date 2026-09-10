import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'qa'/'extracted_character.blend'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24
s.render.resolution_x=768;s.render.resolution_y=768;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.20,.20,.20,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.3
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size in [('Key',(3,-4,5),220,4),('Fill',(-3,-1,3),120,3),('Rim',(0,3,4),250,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.size=size;aim(o,(0,0,1))
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=2.4;s.camera=cam
s.view_settings.view_transform='AgX'
for name,loc in [('front',(0,-5,1.15)),('back',(0,5,1.15)),('side',(5,0,1.15))]:
 cam.location=loc;aim(cam,(0,0,1));s.render.filepath=str(ROOT/'qa'/f'extracted_{name}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'qa'/'extracted_studio.blend'))
