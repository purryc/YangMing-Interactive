# 学者角色 v3 · 细节与控制验证版

本轮基于用户提供的五张扩展参考图修改真实 Blender 网格与骨架，未追加 Hyper3D 付费生成。v1/v2 均保留。

**状态：技术验证版，外观验收仍为 revise。** 手指、靴子、扩展口型与独立眼神控制已落地；眼睑/眉毛贴合、宽袖大动作与手—胡须接触仍低于参考质量，不能作为高保真最终角色或直接上线资产。

## 本轮修改

- 新增 30 根手指骨骼，总骨骼数 55；左右手各五指、每指三节。替换原来的静态低模手，增加指甲、掌纹，平滑连接的手部表面与分段蒙皮。
- 重建靴子：靴筒、鞋口、鞋面缝线、沿边、分层鞋底和底纹；重新检查走跑时地面接触。
- 口腔改为独立上/下牙、舌头、唇缘及随口型变化的胡须小束。原有五个元音命名兼容，新增六组辅音姿势。
- 新增独立虹膜视线、左右眼睑和眉毛控制。虹膜外观取自本次用户参考图，通过 UV 用在可动几何上；不是重新生成整个人物。
- 新增宽袖网格与后帽带。袖子采用骨骼近似下垂，无布料物理。
- 保存 35 个骨骼动作片段，包含原有 12 个动作、8 个手势、5 个手型展示、8 个情绪展示及 2 个口型/视线测试片段。展示片段不等于 35 种不同全身运动。

## 文件

- `output/scholar_voice_rig_v3.blend`：可编辑主文件，24 fps、1–2520 帧展示时间线。
- `output/scholar_voice_rig_v3.glb`：骨骼、蒙皮、具名 morph targets 与 35 个动画片段。
- `output/detail_preview_v3.mp4`：30 秒精选预览，640×640、12 fps，无真实音频。
- `output/preview_v3.html`：完整口型、眼神、表情、手脚特写图库及精选动画。
- `src/live_face_v3.mjs`：面向后续应用的口型/表情/视线/眨眼独立控制器。
- `reference/*_v3.png`：用户提供的五张原始参考图。
- `qa/v3/`：实际模型渲染与验证记录，不是参考图替代模型结果。

## 控制与命名

`Mouth_Visemes` 与 `Scholar_Mesh` 具有同名口型/表情 Shape Keys；`Face_Controls` 具有眼神、眨眼和表情 Shape Keys。它们分别有配套的 NLA 动画，手动拖动数值前应禁用对应的 `Showcase v3` 轨道。所有值归零为基础状态。

| 参考含义 | 实际控制名 |
|---|---|
| 静止 / Rest / X | 所有口型权重为 0 |
| A / E / I / O / U | `viseme_A` / `viseme_E` / `viseme_I` / `viseme_O` / `viseme_U` |
| M/B/P、F/V、TH | `viseme_MBP`、`viseme_FV`、`viseme_TH` |
| T/D/N/L、CH/SH/ZH、K/G/NG | `viseme_TDNL`、`viseme_CHSHZH`、`viseme_KGNG` |
| 左/右/上/下看 | `gaze_L` / `gaze_R` / `gaze_U` / `gaze_D`；全零为正视 |
| 左眼/右眼闭合 | `blink_L` / `blink_R`；0.5 为半闭；同时设 1 为全闭 |
| 眯眼 / 瞪眼 | `squint` / `wide` |
| 喜怒哀乐惊思得意无奈 | `expr_Happy` / `expr_Angry` / `expr_Sad` / `expr_Laughing` / `expr_Surprised` / `expr_Thinking` / `expr_Proud` / `expr_Helpless` |

L/R 指角色自身左右。左上视线通过 `gaze_L`、`gaze_U` 组合，不另造重复几何。表情是参考意图的近似，包括眉眼和嘴部配套变化；未做泪珠、脸红、舌齿接触精修或完整 FACS 肌肉系统。

身体姿势使用骨骼 Action。新增 `shake_head`、`stroke_beard`、`salute`、`hands_on_hips`、`point`、`peace`、`pinch`、`clap`。`hand_open/fist/point/peace/pinch` 是单独手型检查片段，身体回到 T 姿势方便编辑，不应作为待机动作播放。

## 后续 Live LLM 使用

使用实际音频播放时钟驱动口型，不能按 LLM 文本 token 到达时间直接驱动嘴。11 组是视觉姿势，不是完整多语言音素模型；本交付未连接麦克风、ASR、TTS 或 LLM 服务。

```js
import { createFaceDriver } from './live_face_v3.mjs';
import { bodyOnlyClip } from './live_visemes.mjs';
const face = createFaceDriver(gltf.scene, { smoothingMs: 60 });
// AnimationMixer 使用 bodyOnlyClip(clip)，避免演示 morph 曲线覆盖实时控制。
face.setSpeech({ A: .7, E: .3 });
face.setEmotion('Happy', .25);
face.setGaze(.2, 0);
face.setBlink(1); // 双眼；第二参数可单独指定右眼
// 每帧：先 mixer.update(dt)，然后：
face.update(dt);
face.stopSpeech({ immediate: true }); // 用户打断
face.reset(); // 全部控制归零
```

控制器限制口型总权重，降低说话期间嘴部情绪幅度；情绪优先时减弱额外眨眼/视线，避免重复相加过量。任意手工叠加多个满值表情仍可能失真。

## 尚未通过外观验收的部分

1. 眼睑/眉毛为独立补片，近景可见边界和少量旧眉毛穿插；需要脸部重拓扑、统一 UV/肤色与面部一体化修形。
2. 宽袖、拱手和捋胡须有接触遮挡；当前为骨骼近似，需进一步校正姿势、袖片权重与碰撞形状。
3. 手型已可动，但拇指对掌和指尖接触仍是近似，未达到参考图的解剖和美术精度。
4. 原始帽子、主服装与胡须仍沿用首次 Hyper3D 的较低精度几何/贴图，局部新增细节不能补回整个角色的高保真信息。

这些问题已在预览和 QA 中明确标记。`technical_passed: true` 仅说明文件结构、有限坐标、动画和 morph 可用，不能替代美术验收。

## 复现与验证

Blender 后台依次执行：`build_details_v3.py` → `animate_v3.py` → `export_review_v3.py` → `verify_glb_v3.py` → `render_v3.py`。命令使用 `--python-exit-code 1`。最后 `node src/encode_v3.mjs`、`node src/test_live_face_v3.mjs`。

打开 v3 无需重启 Blender；先保存正在编辑的文件。没有覆盖 v2，也没有修改全局 Blender 设置。
