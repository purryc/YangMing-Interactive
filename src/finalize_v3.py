import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/scholar_voice_rig_v3.blend'))
doc=bpy.data.texts.get('README_v3') or bpy.data.texts.new('README_v3');doc.clear();doc.write((ROOT/'README_v3.md').read_text())
rig=bpy.data.objects['Scholar_Rig'];rig['quality_status']='REVISION REQUIRED: functional detail/control prototype, not production visual signoff';rig['visual_review']='qa/v3/visual_review.json';rig['source']='Original Hyper3D generation + local Blender edits informed by five user reference sheets. No new provider generation in v3.'
rig['controls']='55 bones, 30 finger bones; 11 visemes; 8 eye/gaze and 8 emotion morphs; 35 action/control-demo clips. See packed README_v3.'
s=bpy.context.scene;s.frame_set(1);bpy.ops.object.select_all(action='DESELECT');ob=bpy.data.objects['Mouth_Visemes'];ob.select_set(True);bpy.context.view_layer.objects.active=ob
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='PROPERTIES':area.spaces.active.context='DATA'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'output/scholar_voice_rig_v3.blend'),compress=True)
