import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output'/'scholar_voice_rig_v1.blend'))
s=bpy.context.scene
for f in range(1,433):
 dest=ROOT/'qa'/'frames_final'/f'frame_{f:04d}.png'
 dest.parent.mkdir(exist_ok=True)
 if dest.exists():continue
 s.frame_set(f);s.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
print('ANIMATION_RENDER_COMPLETE')
