# YangMing Interactive

一个可下载、可编辑、可运行的 3D 古风书生互动角色项目。仓库包含 Blender 源模型、骨骼与 35 段动画、GLB 交付文件、表情和 11 组口型、参考图、完整构建脚本，以及接入 Qwen Omni Realtime 的浏览器互动界面。

![实时对话界面](qa/realtime_v1/speaking_closeup.png)

## 下载后直接运行

需要 Node.js 20.6 或更高版本，以及一个可用的 DashScope API Key。

macOS 可双击仓库根目录的：

```text
open_yangming.command
```

其他平台：

```sh
cd src/realtime_v1
npm ci
npm start
```

浏览器打开 <http://127.0.0.1:8766>，展开“连接与口型设置”填写 Key；Key 只进入当前本地服务进程，不写入仓库或浏览器存储。页面支持文字提问、麦克风实时对话、流式语音、声音驱动口型、打断、近景和全身查看。

## Blender 与模型

直接打开 [v3 Blender 主文件](output/scholar_voice_rig_v3.blend)，或在其他 3D/网页工具中载入 [v3 GLB](output/scholar_voice_rig_v3.glb)。

- v3：55 根骨骼、30 根分指骨、35 段动画/控制展示、11 组口型、8 种情绪、眼神与眨眼、独立口腔和靴子细节。
- v1/v2 的 `.blend`、`.glb`、预览视频也全部保留，可比较演进过程。
- `reference/` 保留全部原始角色和控制参考图。
- `src/` 包含生成、提取、绑定、材质、面部、动作、导出、渲染与验证脚本。
- `qa/` 保留关键三视图、姿势、口型、结构和实时交互验证证据。逐帧渲染缓存可由源文件重新生成，因此不进入 Git。

在 Blender 5.2 打开 v3 文件即可编辑。时间线为完整展示，Animation/Action Editor 中可独立编辑 `idle`、`listen`、`think`、`speak`、`greet`、`wave`、`stroke_beard` 等动作。详细控制名称与外观限制见 [v3 说明](README_v3.md)。

## 仓库结构

```text
reference/                   原始角色、口型、眼睛、情绪、手势参考
output/                      v1-v3 Blender/GLB、预览视频和静帧
src/                         可复现的 Blender 建模、绑定、动画与验证脚本
src/realtime_v1/             Qwen 服务端代理、Three.js 界面、音频与口型代码
qa/                          结构、形变、视觉和实时链路的关键验证证据
README_v1.md                 v1 归档说明
README_v2.md                 v2 说明
README_v3.md                 v3 控制与质量边界
README_realtime_v1.md        实时对话架构、验证与限制
```

## 验证

```sh
cd src/realtime_v1
npm ci
npm test
node ../verify_repository.mjs
```

`npm test` 检查 PCM、静音闭嘴、播放时钟/打断和麦克风重采样。`verify_repository.mjs` 检查可运行页面、v1-v3 模型、Blender 主文件、参考图与关键 QA 是否齐全。

真实 Qwen 验证已完成：固定句返回 2.96 秒语音；浏览器播放期间模型口型非零；打断后待播队列和口型归零。真实人的现场麦克风和回声体验仍需在下载设备上验收。当前口型是声音分析驱动的 A/E/O 近似，不能称为逐音素精确对齐。详情见 [实时对话说明](README_realtime_v1.md)。

## 复现边界

下载仓库即可完整复现现有模型、动画和交互效果，不需要再次调用 Hyper3D。若要从最初参考图重新生成基础模型，`src/generate.mjs` 依赖 Codex 中已配置的 Hyper3D MCP，会产生外部服务费用和非确定性结果；仓库已保留原始生成产物，常规使用不应重新生成。

角色是参考驱动的互动原型。眼睑边缘、宽袖、胡须接触以及原始服装纹理还未达到高保真成品标准。史料知识库尚未接入，Qwen 回答不能作为史料引用。

## 第三方说明

实时音频分析思路参考 Project AIRI 的 MIT 授权实现；许可证副本位于 `src/realtime_v1/airi_license.txt`。Three.js、ws 和 classic-level 通过 npm 安装，具体版本锁定在 `package-lock.json`。
