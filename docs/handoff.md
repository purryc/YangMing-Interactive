# YangMing Interactive 交接手册

归档日期为 2026-11-06。项目包含一个可恢复的 3D 实时语音原型，以及一组独立的王阳明水墨国漫角色概念。GitHub 的 `main` 是恢复入口，`v1.0.0` 是此前的发布快照。

## 1. 恢复与运行

```sh
git clone https://github.com/purryc/YangMing-Interactive.git
cd YangMing-Interactive/src/realtime_v1
npm ci
npm test
node ../verify_repository.mjs
node --test ../test_live_face_v3.mjs ../test_live_visemes.mjs
npm start
```

仓库原定 Node.js 20.6 以上，本次检查使用 Node.js 24.11.1。macOS 可双击根目录的 `open_yangming.command`。在浏览器打开 `http://127.0.0.1:8766`，先看模型、切换近景和全身。端口被占用时可用 `PORT=8767 npm start`。在连接设置填写自己的 DashScope Key，或在启动进程的环境配置 `DASHSCOPE_API_KEY`。密钥只供本机服务使用。停止服务可在终端按 Ctrl+C。离线检查模型可直接打开 Blender 主文件。

## 2. 文件与版本

| 路径 | 接手用途 |
| --- | --- |
| `output/scholar_voice_rig_v3.blend` | Blender 5.2 的可编辑主文件，含材质、骨骼、Shape Keys 与展示时间线 |
| `output/scholar_voice_rig_v3.glb` | Web 集成用 GLB，带骨骼、蒙皮、具名 morph 和动画 |
| `output/preview_v3.html`、`output/detail_preview_v3.mp4` | 模型、动作及面部控制预览。用 `node src/serve_preview.mjs` 启动本地预览，打开日志地址同目录下的 `preview_v3.html` |
| `output/` 的 v1/v2 文件 | 保留历代 Blender、GLB 与预览。v2 增加五元音、走跑和自然垂臂 |
| `src/`、`src/realtime_v1/` | Blender 生产脚本与 Web 前后端、锁文件和测试 |
| `reference/`、`qa/` | 建模输入、关键渲染、可视化与结构验收证据 |
| `reference/ink_identity_boards/` | 六张独立的国漫角色总设定板，原始 PNG 为 1672 × 941 |
| `docs/research/` | 国漫开发简报、生平工作笔记、原典索引和研究脚本 |

现有 GLB 和基础模型都在仓库。直接使用这些文件无需 Hyper3D。重新生成底模需要单独配置 Hyper3D MCP，可能计费，生成结果也会变化。AIRI 的相关实现来源与 MIT 许可副本见 `src/realtime_v1/airi_license.txt`。

## 3. 维护模型与重新导出

用 Blender 5.2 打开 v3，另存迭代文件后编辑。独立动作在 Action Editor 中选择。手动调嘴、眼睛和表情前，先禁用相关 NLA 展示轨。角色自身左右用 `L/R` 表示。v3 有 55 根骨骼、35 个动作或控制展示片段、11 组口型、8 种情绪。嘴部、胡须与脸部的同名形态要保持同步。

从仓库根目录操作，每个脚本的调用形式为 `blender -b --python-exit-code 1 --python src/<script>.py`。v3 顺序是 `build_details_v3.py` → `animate_v3.py` → `export_review_v3.py` → `verify_glb_v3.py` → `render_v3.py`。需要重新编码预览时运行 `node src/encode_v3.mjs`，并按脚本配置准备视频编码环境。完整形态命名、控制示例和版本依赖见 [v3 说明](../README_v3.md)。

修改后检查 GLB 能重新导入，正背侧材质显示正常，表情可独立调节，四肢和宽袖在大幅动作中形变可接受。重点看近景眼睑与眉毛、拇指对掌、宽袖与手或胡须的接触。历史记录中的技术检查通过，v3 的美术状态仍为 `revise`。以 [视觉验收](../qa/v3/visual_review.json) 为准。

## 4. 语音交互架构与排查

浏览器用 AudioWorklet 将麦克风重采样为 16 kHz PCM，经本地 WebSocket 代理送入 Qwen。返回的 24 kHz PCM 进入 Web Audio 播放队列。同一个播放时钟驱动 A/E/O 权重、静音归零与取消。骨骼轨道与面部控制分开，避免待机动画覆盖口型。

- `server.mjs` 管理本机代理与 Qwen 会话，`config.mjs` 解析模型、区域、音色与凭据。
- `client.mjs` 负责 Three.js、会话 UI 与播放，`audio.mjs` 管理音频分析，`mic_worklet.js` 负责采集端重采样。
- `src/live_face_v3.mjs` 管理口型、情绪、视线和眨眼；`src/live_visemes.mjs` 提供骨骼轨道分离与口型辅助。
- 默认模型为 `qwen3.5-omni-plus-realtime`，预置音色为 `Ethan`。可通过 `QWEN_REALTIME_MODEL`、`QWEN_REALTIME_VOICE`、`QWEN_REGION` 或 `QWEN_REALTIME_URL` 覆盖。新机无需安装 AIRI，可直接使用自己的 Key。

页面开不了先查终端地址和端口。能看模型但没有回复，先用文字验证 Key、地区及模型可用性，再检查麦克风权限与设备。回归打断时确认旧音频停止、待播队列清空、嘴形归零且迟到音频未恢复。更多证据与限制见 [实时语音说明](../README_realtime_v1.md)。

历史固定句通过真实 Qwen 往返，覆盖浏览器播放、口型、手动打断及软件注入麦克风。交接时复跑本地自动测试和仓库完整性检查。仍需用新设备上的真人麦克风验收收音、回声和插话。当前口型是声学估计，史料检索尚未接入对话。

## 5. 国漫美术与研究交接

[美术设定与提示词](character_art_direction.md) 记录 13 套年龄或服装状态和 6 种视觉方向。这批图是全龄总览。单阶段完整三视图、表情表和配件拆解仍待生成。保持相近年龄面部一致，通过衣着、姿态与道具表达遭遇。

[研究来源索引](research/source_manifest.md) 保留书目与原始链接。[国漫开发简报](research/animation_development_brief.md) 和 [生平工作笔记](research/biography_working_notes.md) 用于改编选题。传说、虚岁以及事件日期须在写对白与字幕前回查原典。索引反映研究包早期快照，云端另有后续 OCR 上传记录。外部书刊与原始扫描请从索引来源获取。

## 6. 接手验收顺序

1. 克隆 `main`，执行仓库校验和自动测试。
2. 打开 v3 Blender、GLB 与预览，确认资产和参考图能读取。
3. 配置自己的 Key，依次验收文字回复、真人麦克风、播放时口型与打断。
4. 继续 3D 时优先处理脸部、胡须和宽袖的接触表现。继续漫剧时先锁定风格与阶段脸谱，再出独立角色设定板。

Git 保留源码、可编辑交付件、关键 QA 与角色概念。可重建逐帧输出、依赖目录、本机浏览器调试状态和临时实验不作为恢复依赖。
