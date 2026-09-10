# 古风学者 · v2 动画与语音口型原型

v1 全部保留。v2 新增自然垂手、12 组可编辑动作，以及真正改变顶点的 A/E/I/O/U Shape Keys。

## 交付文件

- `output/scholar_voice_rig_v2.blend`：25 根骨骼、12 个骨骼 Action、嘴部与胡须各 12 个配套 Action；36 秒展示时间线，24 fps。
- `output/scholar_voice_rig_v2.glb`：12 个独立动画片段；骨骼、材质、5 个具名口型目标均已导出。每片段 3 秒。
- `output/voice_interaction_preview_v2.mp4`：36 秒动作预览，640 × 640、12 fps，无音频。说话段切换为面部特写。
- `output/preview_v2.html`：可逐项循环播放的本地预览和闭嘴/A/E/I/O/U 对照。
- `src/live_visemes.mjs`：独立于网络服务的口型平滑控制器，可接入 Three.js 风格场景。
- `qa/v2/`：口型截图、变形检查、GLB 重新导入验证与视频验证记录。

## 在 Blender 使用

打开 v2 `.blend`，空格播放；时间线 1–864 帧，每 72 帧切换一个动作。手臂默认姿势已下垂，举手只出现在相应手势内。

| 动作 | 时间 | 意图 |
|---|---|---|
| idle | 0–3 秒 | 自然待机 |
| listen | 3–6 秒 | 倾听、轻侧头 |
| think | 6–9 秒 | 思考、转头 |
| speak | 9–12 秒 | 说话手势和示范口型 |
| acknowledge | 12–15 秒 | 点头确认 |
| greet | 15–18 秒 | 轻举手致意 |
| walk | 18–21 秒 | 原地走路循环 |
| run | 21–24 秒 | 原地跑步循环 |
| wave | 24–27 秒 | 挥手 |
| shrug | 27–30 秒 | 耸肩、轻摊手 |
| bow | 30–33 秒 | 礼貌鞠躬 |
| look_around | 33–36 秒 | 左右观察 |

编辑单个骨骼动作前，在 NLA 编辑器禁用 `Showcase v2` 轨道，再在 Action Editor 选择同名动作。行走/跑步保持原地，只有周期性高度修正；应用中的前进距离与方向应由角色控制器负责。

### 手动测试口型

1. 选择 `Mouth_Visemes`，打开 Object Data Properties → Shape Keys。
2. 先禁用该 Shape Keys 数据块的 `Showcase v2` NLA 轨道，避免演示关键帧覆盖手调数值。
3. 调整 `viseme_A`、`viseme_E`、`viseme_I`、`viseme_O`、`viseme_U`，范围 0–1。
4. `Scholar_Mesh` 上有同名胡须配套 Shape Keys，也应禁用其演示轨道并同步数值。
5. 五个值全部归零即闭嘴。混合时建议总和不超过 1。

嘴部为新增独立几何，含唇缘、暗色口腔、简化上齿与舌面，随头骨运动；胡须配套形变为开口让位。这是风格化口型原型，尚非精修的完整脸部拓扑。

## 接入 Live LLM / TTS

让口型跟随实际播放的语音时间，避免直接按 LLM 输出文本 token 切嘴。推荐：LLM → TTS 音频与音素时间戳 → 用播放器当前时间选取口型 → 平滑更新两个网格。

```js
import { createLiveVisemeDriver, bodyOnlyClip } from './live_visemes.mjs';
const mouth = createLiveVisemeDriver(gltf.scene, { smoothingMs: 55 });
// 在 AnimationMixer 中使用 bodyOnlyClip(clip)，移除演示口型动画。
// 以下仅示例；音素映射和时间戳来自你的 TTS 服务。
mouth.set({ A: 0.8, O: 0.2 });
// 每个渲染帧：先 mixer.update(dt)，再调用口型驱动。
mouth.update(dt);
// 音频结束：柔和闭嘴；用户打断：立即复位。
mouth.stop();
mouth.stop({ immediate: true });
```

此控制器包含归一化、约 55ms 指数平滑、两网格同步、结束闭嘴和打断复位。单元测试：`node src/test_live_visemes.mjs`。没有写入 API key，没有麦克风采集或网络请求。

重要边界：A/E/I/O/U 是五个便于驱动的视觉元音姿势，不等于完整中文或英文音素集。当前未做 M/B/P 闭唇、F/V 咬唇、舌齿音、独立眨眼与眼球；视频口型为合成节奏，未连接任何真实 TTS 或 Live LLM。

## 质量与来源

沿用 v1 的同一次 Hyper3D 生成，本轮没有重新付费生成。原始多视图模型、提取版本、v1 场景均保留。贴图与几何仍低于用户原始设定图，后帽带缺失；宽袍动作是蒙皮近似，没有布料物理。大幅度动作存在服装挤压，适合验证交互流程，后续精修角色仍需要重拓扑与面部整合。

导出 GLB 将每顶点影响规范到最多 4 根骨骼；重新导入后验证全部 12 个动画实际形变，两个网格均保留 5 个具名 morph targets，`speak` 中有非零口型曲线。

## 可复现步骤

用 Blender `-b --python-exit-code 1 --python` 依次运行 `src/build_v2.py`、`src/qa_export_v2.py`、`src/verify_glb_v2.py`、`src/render_v2.py`；然后 `node src/encode_v2.mjs`。检查 JSON 中的 `passed` 字段，不以“成功保存”代替形变和播放验证。

仅查看文件无需重启 Blender；先保存当前打开的工作再打开 v2。不要覆盖正在编辑的其他角色工程。
