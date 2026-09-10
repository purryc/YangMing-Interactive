import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/scholar_voice_rig_v2.blend'))
s=bpy.context.scene;s.frame_set(1)
name='README_v2 — 使用与语音接入'
doc=bpy.data.texts.get(name) or bpy.data.texts.new(name);doc.clear();doc.write((ROOT/'README_v2.md').read_text())
bpy.ops.object.select_all(action='DESELECT');mouth=bpy.data.objects['Mouth_Visemes'];mouth.select_set(True);bpy.context.view_layer.objects.active=mouth;mouth.active_shape_key_index=1
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='PROPERTIES':area.spaces.active.context='DATA'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'output/scholar_voice_rig_v2.blend'),compress=True)
print('V2_FINALIZED_README_PACKED')
