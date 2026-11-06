# 运行与维护手册

## 初次安装

```sh
git clone https://github.com/purryc/YangMing-Interactive.git
cd YangMing-Interactive/src/realtime_v1
npm ci
npm test
node ../verify_repository.mjs
```

## 本地启动

```sh
npm start
```

成功后终端输出 JSON，其中 `url` 默认为 `http://127.0.0.1:8766`。如果端口占用：

```sh
PORT=8767 npm start
```

## 最小验收

1. 页面显示“书生已就绪”，模型贴图正常。
2. “近看口型”和“全身”都能正确取景，拖动/滚轮可用。
3. 输入文字后 Qwen 返回字幕与声音，嘴在听到声音时张合。
4. 回复中点击“打断”，声音立即停止，嘴闭合，旧音频不恢复。
5. 点击“开始语音对话”后才出现麦克风权限请求。
6. 拒绝麦克风权限时页面仍可继续文字对话。
7. 点击“结束”后麦克风轨道和 WebSocket 关闭。

## 自动验证

```sh
node src/verify_repository.mjs
cd src/realtime_v1
npm ci
npm test
node --check client.mjs
node --check server.mjs
```

`probe_live.mjs` 会产生一次真实 Qwen 请求，可能计费；仅在有意验证服务时运行：

```sh
node probe_live.mjs
```

## 常见问题

### 页面提示没有 Key

在页面设置中输入 Key，或启动前设置 `DASHSCOPE_API_KEY`。不要把 Key 加进 `.env` 后提交。

### Qwen 连接失败

检查 Key 所属地区、模型权限、额度和 `QWEN_REALTIME_URL`。新工作空间可能要求控制台提供的专用 WebSocket 地址。

### 模型空白或贴图丢失

必须从本地 HTTP 服务打开，不能直接双击 `index.html`。确认 `output/scholar_voice_rig_v3.glb` 存在并通过 `node src/verify_repository.mjs`。

### 有声音但嘴不动

确认浏览器没有挂起 AudioContext；检查 `window.scholarDiagnostics.audioChunks`、`mouth` 和 `peakMouth`。不要把原始 `speak` Action 的 Morph 轨道直接混入，必须使用 `bodyOnlyClip()`。

### 口型幅度太小或埋在胡须后

页面可调“口型幅度”。运行时以 MBP 作为可见闭唇基线再混合元音；不要把 MBP 解释为实时识别到 m/b/p。

### 麦克风不工作

确认浏览器权限、系统输入设备和 HTTPS/loopback 安全上下文。当前页面使用 loopback，符合 `getUserMedia` 本地开发要求。现场回声与设备切换尚未完成正式验收。

## 修改模型后的交付检查

1. 新版本使用新文件名，保留旧版本。
2. 骨骼、Morph 名称保持兼容，或同步修改 `live_face_v3.mjs`。
3. 重新导出 GLB，运行 `verify_glb_v3.py`。
4. 检查正面、侧面、背面、闭嘴、A/O、眨眼、手型和地面接触。
5. 浏览器检查 `idle/listen/think/speak` 切换和打断。
6. 更新 README、QA JSON、关键截图和资产清单。

## 发布

```sh
git status
git add <明确文件>
git commit -m 'feat: describe the change'
git push origin main
gh release create vX.Y.Z --target main --generate-notes
```

发布前确认没有 API Key、签名 URL、本机绝对路径、`node_modules`、`.blend1`、逐帧缓存或临时录音。
