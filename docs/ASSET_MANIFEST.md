# 关键资产清单

## v3 主交付

| 文件 | 字节数 | SHA-256 |
|---|---:|---|
| `output/scholar_voice_rig_v3.blend` | 43,414,345 | `cb597408956b8b2647ec94800d0c19e4e08ca90bfc4af9f319229d5454ecaa82` |
| `output/scholar_voice_rig_v3.glb` | 25,082,504 | `251cb80038774c043be2c1acf586e22a63c3db2b4bf12a89b8be07d8af4e4302` |
| `output/detail_preview_v3.mp4` | 1,246,684 | `da3a029ac2a86b3b5867ab32e731eaea7b5afe7a16c5050ec86c4a410371b20b` |

## 原始参考

| 文件 | 字节数 | 内容 |
|---|---:|---|
| `reference/character_sheet.png` | 4,189,801 | 角色多视图设定 |
| `reference/visemes_v3.png` | 3,829,651 | 11 组口型 |
| `reference/eyes_v3.png` | 3,828,330 | 眼神与眼睑 |
| `reference/emotions_v3.png` | 3,555,547 | 8 种情绪 |
| `reference/hands_boots_v3.png` | 3,085,460 | 手型与靴子 |
| `reference/gestures_v3.png` | 3,015,075 | 身体手势 |

## 国漫美术与研究包

- `reference/ink_identity_boards/01_baseline.png` 至 `06_woodblock.png`：六套 1672 × 941 的全龄角色身份板。
- `docs/character_art_direction.md`：13 个年龄/服装阶段、统一人物提示词与视觉方向。
- `docs/research/source_manifest.md`：原典、传记、地方志与研究来源索引。
- `docs/research/animation_development_brief.md`：国漫开发主题、分集方向和史料边界。
- `docs/research/biography_working_notes.md`：生平工作笔记，不可替代原典核验。
- `docs/research/tools/`：资料抓取、PDF OCR 文本层和 NotebookLM 上传辅助脚本。

外部书刊、网页与扫描件按来源索引重新获取，不将第三方原文副本误当作仓库自有资产。

## 历史版本

- `output/scholar_voice_rig_v1.blend/.glb`
- `output/scholar_voice_rig_v2.blend/.glb`
- `output/voice_interaction_preview.mp4`
- `output/voice_interaction_preview_v2.mp4`
- `README_v1.md`、`README_v2.md`

## 源码范围

- Blender：`src/*.py`
- 导出、预览与验证：`src/*.mjs`
- 实时互动：`src/realtime_v1/`
- 自动测试：`src/test_live_*.mjs`、`src/realtime_v1/test_*.mjs`
- 依赖锁：`src/realtime_v1/package-lock.json`

## QA 范围

- v1：`qa/*.json`、三视图与状态姿势
- v2：`qa/v2/` 的结构、动作、五元音与视频验证
- v3：`qa/v3/` 的 35 动作、11 口型、8 情绪、眼神、手型、靴子和视觉评审
- Realtime：`qa/realtime_v1/` 的 provider、浏览器、口型和打断证据

## Git 有意排除

以下文件不会影响恢复，且可由源文件重建，因此不进 Git：

- `node_modules/`
- `.env` 和任何 Key
- `.blend1` 自动备份
- `qa/**/frames/` 与 `frames_final/` 逐帧缓存
- 中间 Blender staging 文件
- 本机 Playwright 会话、日志、测试 WAV 和临时浏览器配置
- 共享工具与 npm 缓存

排除这些缓存不改变模型、动画、交互源码、最终输出或关键 QA 的可恢复性。
