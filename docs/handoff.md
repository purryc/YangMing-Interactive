# YangMing Interactive 完整交接

交接日期：2026-11-06（America/Toronto）

## 1. 唯一可信来源

- GitHub：[purryc/YangMing-Interactive](https://github.com/purryc/YangMing-Interactive)
- 最终交接版本：[v1.1.0](https://github.com/purryc/YangMing-Interactive/releases/tag/v1.1.0)
- 默认分支：`main`
- 本地目录在完成本交接后删除。此后不要把任何本机旧副本视作最新版本；恢复时重新 clone GitHub。

## 2. 项目是什么

YangMing Interactive 是一个古风书生 3D 互动角色原型，由四层组成：

1. Blender 可编辑角色：v1-v3 源文件、骨骼、蒙皮、材质、相机和灯光。
2. 可交换运行时资产：GLB、35 段动作、Morph Targets、预览视频和 QA 静帧。
3. 浏览器互动：Three.js 场景、镜头控制、状态动作、字幕和交互界面。
4. 实时语音：Qwen Omni Realtime、麦克风 PCM、流式播放、声音驱动口型和打断。

这是技术验证版。结构和交互已验证，外观仍有明确的 revise 项，不能标记为高保真最终角色。

## 3. 当前交付状态

| 领域 | 当前状态 | 证据 |
|---|---|---|
| Blender 主文件 | v3 可编辑，55 根骨骼 | `output/scholar_voice_rig_v3.blend` |
| GLB | 蒙皮、Morph、35 段动画 | `output/scholar_voice_rig_v3.glb`、`qa/v3/glb_validation.json` |
| 手部 | 左右五指，每指三节，共 30 根指骨 | `README_v3.md`、`qa/v3/hand_*.png` |
| 面部 | 11 组口型、8 种情绪、眼神、左右眨眼 | `README_v3.md`、`qa/v3/control_*.png` |
| 浏览器模型 | Three.js 正常加载，14 个 Morph 绑定 | `qa/realtime_v1/browser_validation.json` |
| Qwen 文本到语音 | 真实服务往返通过 | `qa/realtime_v1/provider_validation.json` |
| 麦克风代码链路 | 录音注入经过 MediaStream → AudioWorklet → Qwen | `qa/realtime_v1/browser_validation.json` |
| 打断 | 停止音频、清空嘴部时间轴，迟到块被屏蔽 | `qa/realtime_v1/interrupted.png` |
| 自动测试 | 6 项通过 | `src/realtime_v1/test_*.mjs` |
| 真人现场麦克风 | 尚未完成听辨与回声验收 | 明确未通过，不要扩大结论 |
| 中文逐音素口型 | 未实现 | 当前仅 A/E/O 声学近似 |

## 4. 最快恢复与运行

### 环境

- Git
- Node.js 20.6 或更高版本
- npm
- Chrome / Edge 等支持 Web Audio、AudioWorklet 和麦克风的浏览器
- 可用的 DashScope API Key
- 需要编辑模型时安装 Blender 5.2 LTS；仅运行网页无需 Blender

### 下载

```sh
git clone https://github.com/purryc/YangMing-Interactive.git
cd YangMing-Interactive
```

### 验证仓库

```sh
node src/verify_repository.mjs
cd src/realtime_v1
npm ci
npm test
```

### 启动网页

macOS：双击根目录的 `open_yangming.command`，或执行：

```sh
./open_yangming.command
```

跨平台：

```sh
cd src/realtime_v1
npm ci
npm start
```

打开 `http://127.0.0.1:8766`。页面只监听 loopback，不是公网服务。

### 配置 Qwen

最简单的方式是在页面“连接与口型设置”中输入 DashScope API Key。输入值仅用于当前会话，不写入仓库或浏览器存储。

也可以在启动前提供：

```sh
export DASHSCOPE_API_KEY='your-key'
export QWEN_REGION='intl-singapore'
npm start
```

可覆盖的变量：

| 变量 | 用途 | 默认值 |
|---|---|---|
| `DASHSCOPE_API_KEY` | Qwen 服务认证 | 无 |
| `QWEN_REGION` | `intl-singapore` 或 `cn-beijing` | `intl-singapore` |
| `QWEN_REALTIME_URL` | 工作空间专用 WebSocket 地址 | 按地区选择旧版公共地址 |
| `QWEN_REALTIME_MODEL` | Realtime 模型 | `qwen3.5-omni-plus-realtime` |
| `QWEN_REALTIME_VOICE` | 预置音色 | `Ethan` |
| `PORT` | 本地端口 | `8766` |

不要把 Key 写入源码、README、issue、日志或提交历史。

## 5. Blender 交接

主文件：`output/scholar_voice_rig_v3.blend`。直接打开即可查看完整 1–2520 帧展示时间线。

主要对象和控制：

- `Scholar_Rig`：角色骨架。
- `Scholar_Mesh`：主体蒙皮及口型/表情 Shape Keys。
- `Mouth_Visemes`：口腔、唇缘、牙齿、舌头及同名口型。
- `Face_Controls`：眼神、眨眼和表情。
- `Boots_Detailed`：重建靴子。
- 手指：`thumb/index/middle/ring/pinky_1..3.L/R`。

口型控制：`viseme_A/E/I/O/U/MBP/FV/TH/TDNL/CHSHZH/KGNG`。全零为基础状态。

面部控制：`gaze_L/R/U/D`、`blink_L/R`、`squint`、`wide`、`expr_Happy/Angry/Sad/Laughing/Surprised/Thinking/Proud/Helpless`。

应用实时控制时，动画必须先经 `bodyOnlyClip()` 移除 `morphTargetInfluences` 轨道，避免展示动画覆盖实时脸部。

## 6. 重新构建 v3

已有 `.blend` 和 `.glb` 足够恢复项目，正常使用不需要重新调用 Hyper3D。若确实修改了建模脚本，在 Blender 后台依次执行：

```text
src/build_details_v3.py
src/animate_v3.py
src/export_review_v3.py
src/verify_glb_v3.py
src/render_v3.py
```

每个 Blender 命令使用 `-b --python-exit-code 1 --python <script>`。随后执行：

```sh
node src/encode_v3.mjs
node src/test_live_face_v3.mjs
```

`src/generate.mjs` 会调用外部 Hyper3D 服务、可能计费且结果不确定。基础生成产物已经保留，除非明确要重新生成角色，不要运行它。

## 7. 发布与版本管理

- Commit message 使用英文 Conventional Commits。
- 不提交 `.env`、Key、`node_modules`、`.blend1`、逐帧缓存和临时录音。
- 修改运行时代码后运行 `npm test` 与 `node src/verify_repository.mjs`。
- 修改模型后同时更新 `.blend`、`.glb`、QA JSON、必要截图和对应 README。
- 新版本使用 Git tag 和 GitHub Release；Release notes 必须说明视觉未通过项与现场麦克风是否实测。

## 8. 已知问题与下一步

高优先级：

1. 用真人现场麦克风完成回声消除、插话、权限拒绝和设备切换验收。
2. 评估 AIRI `model-driver-lipsync` 的 A/E/I/O/U 权重，替换当前 A/E/O 简化估计。
3. 修复近景眼睑/眉毛补片边界和旧眉毛穿插。
4. 精修宽袖、拱手和捋胡须的接触、权重与碰撞。
5. 若要作为“王阳明”知识角色上线，加入可追溯史料知识库和引用边界。

不要声称：

- 当前口型是中文逐音素精确同步。
- 当前声音是历史人物声音克隆。
- 35 个片段都是互不相同的全身动作。
- 技术验证通过等于美术验收通过。
- Qwen 输出可直接作为史料引用。

## 9. 本地清理与恢复

本次交接完成后删除的本地范围：

- `/Users/hmi/Documents/AIGC/projects/scholar_voice_character`
- 名称包含 `yangming-clone-qa` 或 `scholar_voice_character` 的项目专用临时副本
- 仅属于该项目的本地 Node 依赖、渲染帧、Blender 自动备份和 QA 临时录音

明确不删除：

- `/Users/hmi/Documents/airi`：独立的 Project AIRI 仓库，被本项目参考但不属于本项目。
- AIRI 的本地设置和 DashScope Key：属于其他项目/账号配置。
- Blender、Node.js、npm、Codex 和共享缓存：是共享工具，不属于本项目。
- GitHub 和 Notion 中的远端交付。

恢复命令：

```sh
git clone https://github.com/purryc/YangMing-Interactive.git
cd YangMing-Interactive/src/realtime_v1
npm ci
npm test
```

## 10. 国漫美术与研究交接

[美术设定与提示词](character_art_direction.md) 记录 13 套年龄或服装状态和 6 种视觉方向。`reference/ink_identity_boards/` 保存六张 1672 × 941 的全龄总设定板。单阶段完整三视图、表情表和配件拆解仍待生成。继续创作时保持相近年龄的面部身份一致，通过衣着、姿态与道具表达人物经历。

[研究来源索引](research/source_manifest.md) 保留书目与原始链接。[国漫开发简报](research/animation_development_brief.md) 和 [生平工作笔记](research/biography_working_notes.md) 用于改编选题。`docs/research/tools/` 保存资料抓取、OCR 和 NotebookLM 上传辅助脚本。

传说、虚岁、事件日期与对白不得只依据工作笔记；正式发布前必须回查原典或可靠研究。索引是研究包快照，外部书刊与原始扫描不复制进仓库，按索引链接重新取得。

## 11. 接手验收顺序

1. 克隆 `main`，运行仓库完整性检查与自动测试。
2. 打开 v3 Blender、GLB 和预览，确认可编辑资产与参考图可读取。
3. 使用接手方自己的 Key，依次验收文字回复、真人麦克风、播放口型和打断。
4. 继续 3D 时优先处理脸部、胡须与宽袖接触；继续国漫时先锁定风格与阶段脸谱，再制作单阶段设定板。
5. Git 保存源码、可编辑交付、关键 QA 和概念资产；依赖目录、逐帧缓存、本机调试状态与临时实验应重新生成。

## 12. 完整文档索引

- `README.md`：项目入口和快速启动
- `README_v1.md`：v1 历史交付
- `README_v2.md`：v2 模型、动作和五元音口型
- `README_v3.md`：v3 骨骼、手、靴子、11 组口型、表情和质量边界
- `README_realtime_v1.md`：Qwen、音频、口型、打断和验证
- `docs/ARCHITECTURE.md`：运行时架构和模块职责
- `docs/OPERATIONS.md`：维护、验证、故障排查和发布
- `docs/ASSET_MANIFEST.md`：关键资产、哈希和追踪范围
- `docs/ARCHIVE_STATUS.md`：远端复验与本机清理的最终状态
- `docs/character_art_direction.md`：13 个阶段与 6 种国漫视觉方向
- `docs/research/`：史料索引、工作笔记、动画开发简报和研究工具
