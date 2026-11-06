# 架构说明

## 运行时数据流

```text
浏览器麦克风
  → getUserMedia
  → AudioWorklet（重采样为 16 kHz PCM16）
  → 本机 WebSocket /realtime
  → server.mjs（Key 仅在服务端内存）
  → Qwen Omni Realtime

Qwen response.audio.delta（24 kHz PCM16）
  → 浏览器 AudioContext 顺序播放队列
  ├→ 扬声器
  └→ 同一播放时钟 MouthTimeline
       → A/E/O + MBP 几何基线
       → createFaceDriver
       → v3 GLB Morph Targets
```

服务端还转发用户转写、回复字幕、说话状态和错误。用户插话或点击“打断”时，服务端发送 `response.cancel`，浏览器停止全部 AudioBufferSource、清空嘴部时间轴，并屏蔽已取消 response 的迟到数据。

## 边界与信任模型

- HTTP 与 WebSocket 只监听 `127.0.0.1`。
- Host 与 Origin 均限制为当前 loopback 端口。
- 浏览器可以临时提交 Key，但输入框提交后清空；服务端不持久化。
- WebSocket 二进制输入限制为不超过 32 KB 且必须是完整 PCM16 sample。
- 连接最多 3 个本地客户端。
- 返回错误会清除 Key 字符串和 `sk-*` 形态的敏感值。
- 当前适合本机原型，不是公网多租户服务；若部署公网，必须重新设计认证、会话隔离、限流和密钥管理。

## 模块职责

| 文件 | 职责 |
|---|---|
| `src/realtime_v1/server.mjs` | 静态资源、本机 WebSocket、Qwen 代理、取消与安全边界 |
| `src/realtime_v1/config.mjs` | 环境变量、可选 AIRI 配置读取、角色系统提示词 |
| `src/realtime_v1/client.mjs` | Three.js、GLB、动作混合、UI、录放音、实时脸部驱动 |
| `src/realtime_v1/audio.mjs` | PCM16 解码、25 ms 声学帧、播放时间轴、打断清理 |
| `src/realtime_v1/mic_worklet.js` | 设备采样率到 16 kHz 的连续重采样与 100 ms 分包 |
| `src/live_face_v3.mjs` | 11 口型、表情、眼神、眨眼绑定和指数平滑 |
| `src/live_visemes.mjs` | 五元音兼容驱动与移除动画 Morph 轨道 |
| `output/scholar_voice_rig_v3.glb` | 浏览器运行时角色、蒙皮、Morph 与动作 |

## 状态到动画

| 会话状态 | 身体 Action | 面部来源 |
|---|---|---|
| 未连接 | `idle` | 自然眨眼 |
| 正在听 | `listen` | 自然眨眼 |
| 正在生成 | `think` | 自然眨眼 |
| 音频正在播放 | `speak` | 实际播放时钟驱动口型 + 自然眨眼 |

身体动画通过 `bodyOnlyClip()` 去掉 Morph 轨道后播放；每帧顺序是 `mixer.update(dt)` → 写入实时脸部权重 → `face.update(dt)` → render。

## 模型资产层次

- v1：25 骨骼、6 个主要状态 Action，面部以贴图和示意下颌为主。
- v2：独立 A/E/I/O/U 嘴型、自然下垂手臂、走路和跑步。
- v3：55 骨骼，新增分指、靴子、独立口腔、11 组口型、8 情绪、眼神/眼睑、宽袖和手势。

v1/v2 是历史交付；浏览器默认只加载 v3。
