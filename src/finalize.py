import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output'/'scholar_voice_rig_v1.blend'))
text=bpy.data.texts.get('README - Voice character') or bpy.data.texts.new('README - Voice character')
text.clear();text.write((ROOT/'README.md').read_text())
bpy.context.scene.frame_set(1)
bpy.context.scene.render.resolution_x=768;bpy.context.scene.render.resolution_y=768
bpy.context.scene.cycles.samples=24
bpy.context.scene.render.filepath=str(ROOT/'output'/'scholar_voice_beauty.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'output'/'scholar_voice_rig_v1.blend'),compress=True)
