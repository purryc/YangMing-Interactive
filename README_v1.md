# 古风学者语音交互角色 · v1（归档说明）

## 文件与使用

- `output/scholar_voice_rig_v1.blend`：可编辑角色、25 根骨骼、6 个 Action、灯光和相机、18 秒 NLA 展示时间线。
- `output/scholar_voice_rig_v1.glb`：带骨骼及六个独立动作的交换文件。
- `output/voice_interaction_preview.mp4`：连续动作预览，24 fps，每个状态 3 秒。
- `output/scholar_voice_beauty.png`：默认姿态渲染。
- `output/base_basic_pbr.glb`、`output/base_basic_shaded.glb`：Hyper3D 原始输出，保留全部部件。
- `output/scholar_source_extracted.glb`：从生成结果中提取的单个完整角色。
- `reference/character_sheet.png`：用户原始设定图。
- `src/`：可复现的生成、提取、绑定、动作、导出与检查脚本。
- `qa/`：三面检查、动作关键帧、生成记录、权重和形变验证。

在 Blender 打开 `.blend` 后按空格播放。时间线标记按顺序为 `idle`、`listen`、`think`、`speak`、`acknowledge`、`greet`。动作编辑器中的同名 Action 可独立编辑。修改单个 Action 时先禁用 NLA 展示轨道，避免叠加。

`Scholar_Rig` 为骨架，`Scholar_Mesh` 为蒙皮角色。进入 Pose Mode 可操作 `head`、`neck`、`upper_arm.L/R`、`forearm.L/R`、`hand.L/R`、`jaw`、`beard`、`sleeve.L/R`。`root` 移动整个角色。此版采用 FK；手指、眼球尚无独立控制。部分腿部骨骼作为后续扩展层级保留，当前动作以固定脚底为设计目标。

## 动作含义

| Action | 时间段 | 意图 |
|---|---|---|
| idle | 0–3 秒 | 小幅呼吸和自然重心变化 |
| listen | 3–6 秒 | 轻微前倾、侧头关注 |
| think | 6–9 秒 | 稍转头、停顿和回正 |
| speak | 9–12 秒 | 单手节拍、头部强调、胡须轻动 |
| acknowledge | 12–15 秒 | 一次清楚的点头 |
| greet | 15–18 秒 | 小幅举手和礼貌致意 |

## 生成来源与质量边界

Hyper3D Rodin Gen-2.5 Medium，一次生成，参考图为用户提供的多视图角色设定。请求目标为 30,000 四边形面，服务返回的 GLB 实际由三角面组成；提取角色为 6,431 顶点、10,912 面。原始多角色结果未删除。

模型来源：https://hyper3d.ai/workspace/rodin/b89607c5-f8a8-44d8-8bef-331d5c8eda35

首次生成将设定图里的多个视图分别重建，因此在 Blender 中提取了左上完整角色继续绑定。帽子、服装、白胡须和比例基本保留，但贴图和几何精度低于参考图，背部帽带缺失。适合作为可编辑的交互动作原型；不能称为高保真成品角色。

眼睛、嘴唇主要属于烘焙贴图，当前没有独立眼球、眼睑、口腔及面部 Shape Keys。`speak` 是示意动作和下颌/胡须微动，未接入音频，不能用于逐音素口型同步。宽袖与胡须使用骨骼形变，没有布料或毛发物理模拟。

后续提升应优先拆出单个干净正面与侧背参考，重新生成高保真角色，或对当前角色重拓扑、重做面部及补帽带。实时语音应用可按 ASR/TTS 状态切换这六个动作；当前交付不包含麦克风、语音识别或合成服务。

## 复现

本机 Blender：`/Applications/Blender.app/Contents/MacOS/Blender`。

依次运行 `extract_character.py`、`render_extracted.py`、`build_rig.py`、`validate_rig.py`、`render_animation.py`。Blender 使用 `-b --python-exit-code 1 --python <script>`。生成脚本有重复提交防护；不要删除生成记录后直接重跑，以免重复扣费。


## 实时对话入口

已新增 [Qwen 实时对话与口型试验](README_realtime_v1.md)。启动 `src/realtime_v1/open_realtime.command`，使用现有 v3 GLB 对话；原模型文件保持不变。
