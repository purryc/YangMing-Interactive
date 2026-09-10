import bpy,json
bpy.ops.wm.open_mainfile(filepath='/Users/hmi/Documents/AIGC/projects/scholar_voice_character/qa/v3/details.blend')
for o in bpy.data.objects:
 if o.type=='MESH' and o.name!='Studio_Ground':
  print(o.name,len(o.data.vertices),list(o.dimensions),list(o.scale),[(k.name,k.value) for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else '')
for n in bpy.data.objects['Scholar_Mesh'].data.materials[0].node_tree.nodes:
 if n.type=='TEX_IMAGE':print('TEXTURE',n.image.name,[(l.to_node.name,l.to_socket.name) for l in n.outputs['Color'].links])
