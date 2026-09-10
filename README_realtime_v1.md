# 王阳明书生 · Qwen 实时对话与口型试验

已接通本地 v3 模型与 AIRI 使用的 Qwen Omni Realtime。可以文字提问、麦克风对话、接收流式声音、按实际音频播放时间驱动口型、手动打断和结束会话。此版本不改写 Blender/GLB 源模型，原 v1/v2/v3 都保留。

## 打开

双击 `src/realtime_v1/open_realtime.command`，或打开已启动的 <http://127.0.0.1:8766>。

点击“开始语音对话”后浏览器才申请麦克风权限。也可先点示例问题或输入文字试听。点击“近看口型”放大脸部，“全身”查看角色；拖动转向，滚轮缩放。“打断”立即停播，“结束”关闭麦克风和 Qwen 会话。

开发启动：

```sh
cd src/realtime_v1
npm ci
npm start
```

服务只监听本机，未部署到公网。

## 接入方式与复用来源

```text
麦克风 → AudioWorklet → 16 kHz PCM → 本地 WebSocket 代理 → Qwen
Qwen → 24 kHz PCM 流 → Web Audio 队列 → 扬声器
                                  └→ 同一播放时钟 → 口型权重 → v3 GLB
```

- 参考 AIRI `packages/stage-shared/src/qwen-omni.ts` 的地区、模型与会话事件约定，以及 `apps/stage-tamagotchi/src/renderer/libs/qwen-omni/pcm-playback.ts` 的声学估计思路。没有修改 AIRI 项目。
- 使用 `qwen3.5-omni-plus-realtime`，男性预置音色 `Ethan`。这是预置声音，不是王阳明声线克隆。
- 优先使用环境变量 `DASHSCOPE_API_KEY`。否则从 AIRI 的 Qwen 设置中只读加载密钥与地区；读取临时数据库副本后立即删除。密钥仅保留在服务端内存，不写入代码、日志或浏览器存储。
- 没有已有密钥时，可在页面“连接与口型设置”中填写。仅发送给本机代理用于当前会话，提交后清空输入框。
- 可用 `QWEN_REALTIME_URL`、`QWEN_REGION`、`QWEN_REALTIME_MODEL`、`QWEN_REALTIME_VOICE` 覆盖配置。当前 AIRI 旧版地区地址已经过真实请求验证；如账号使用工作空间专用地址，可通过 `QWEN_REALTIME_URL` 设置官方控制台提供的完整 `wss://.../api-ws/v1/realtime` 地址。
- 浏览器只接收音频、转写与状态。音频/对话默认不落盘；`qa/realtime_v1/qwen_reply.wav` 是主动执行的固定测试句录音。

官方协议参考：[Qwen Omni Realtime](https://www.alibabacloud.com/help/en/model-studio/realtime)。以本次真实往返结果确认当前账号可用性，不假设每个地区/账号都有相同权限。

## 口型与身体

- 复用 `src/live_face_v3.mjs`，连接 GLB 中 14 个带 Morph 的材质子网格。
- 音频每 25 ms 分析响度与过零率，混合 A/E/O；口型跟随 `AudioContext.getOutputTimestamp()`，不用文字 token 到达时间猜测。
- v3 Basis 嘴部原本埋在胡须后，小权重容易不可见；发声时以 MBP 闭唇形态作几何基线再混合元音，静音全部归零。这里的 MBP 不表示识别出了 m/b/p。
- `idle/listen/think/speak` 只播放身体骨骼轨道，移除展示动画的面部轨道，避免覆盖实时嘴部。自然眨眼单独叠加。
- 手动打断和服务端检测到新语音都会清空待播声音、口型时间轴，并屏蔽已取消回复的迟到音频块。

## 实际验证与边界

证据位于 `qa/realtime_v1/`：

- 真实 Qwen 文本到语音：固定测试句“知是行之始，行是知之成”，返回 2.96 秒音频、10 个音频块；会话就绪 1.82 秒，首音频 2.90 秒（均从开始连接计时，单次样本，不是延迟承诺）。
- 浏览器真实音频播放：模型成功加载，声音期间 Morph 非零；截图 `speaking_closeup.png` 可见嘴唇、牙齿与张合。
- 打断验证：打断前约 526 ms 待播音频，打断后队列和口型为零，700 ms 后没有旧声音重新进入。
- 录音注入验证：测试录音通过浏览器 MediaStream → AudioWorklet → Qwen，正确转写原句并返回语音。这个验证覆盖真实云服务和音频采集后的代码；没有用人的现场声音做听辨与回声验收。
- Chrome 文件模拟麦克风曾只输出静音，因此改用软件 MediaStream 注入验证。该隔离测试没有改变交付页面的真实 `getUserMedia`。
- 6 项自动测试通过：PCM 字节序、静音归零、权重范围、播放时间轴/取消、24/44.1/48 kHz 连续重采样。

仍有明确限制：

1. 这是声学口型近似，没有逐字音素时间戳；不能称为完整中文音素级对齐。不同元音和辅音的识别精度还未测量。
2. 实体麦克风、扬声器回声消除与真人插话体验待实际试聊；录音注入不等同于现场验证。
3. 打断会停止本地播放和服务端生成，但未截断服务器对话历史中的未播完文字。
4. 沿用 v3 外观及其未通过项：眼睑/眉毛贴合、胡须与衣袖接触、帽子/衣服纹理仍需精修。
5. 当前角色提示词是试验配置，没有接入史料知识库；回答不能作为史料引用。

## 下一步怎样提高精度

优先评估 AIRI 已有 `packages/model-driver-lipsync` 的 `getVowelWeights()`，把它输出的 A/E/I/O/U 权重直接映射到本模型，并针对 Ethan 的中文语音重新标定。先用同一组录音比较闭口、圆唇、展唇表现，再决定是否引入更重的音素识别或带时间戳的对齐服务。当前播放时钟、取消机制和模型控制接口都可以保留。

验证命令：`npm test`；`node probe_live.mjs` 会执行一次真实 Qwen 请求并覆盖固定测试句的验证文件。
