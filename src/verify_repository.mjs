import { access, stat } from 'node:fs/promises';

const required = [
  'reference/character_sheet.png',
  'reference/visemes_v3.png',
  'reference/eyes_v3.png',
  'reference/emotions_v3.png',
  'reference/hands_boots_v3.png',
  'reference/gestures_v3.png',
  'output/scholar_voice_rig_v1.blend',
  'output/scholar_voice_rig_v1.glb',
  'output/scholar_voice_rig_v2.blend',
  'output/scholar_voice_rig_v2.glb',
  'output/scholar_voice_rig_v3.blend',
  'output/scholar_voice_rig_v3.glb',
  'output/detail_preview_v3.mp4',
  'src/animate_v3.py',
  'src/build_details_v3.py',
  'src/face_v3.py',
  'src/realtime_v1/server.mjs',
  'src/realtime_v1/client.mjs',
  'src/realtime_v1/package-lock.json',
  'qa/v3/glb_validation.json',
  'qa/v3/rig_validation.json',
  'qa/realtime_v1/browser_validation.json',
];

const missing = [];
let bytes = 0;
for (const file of required) {
  try {
    await access(new URL(`../${file}`, import.meta.url));
    bytes += (await stat(new URL(`../${file}`, import.meta.url))).size;
  } catch {
    missing.push(file);
  }
}

if (missing.length) {
  console.error(JSON.stringify({ passed: false, missing }, null, 2));
  process.exitCode = 1;
} else {
  console.log(JSON.stringify({ passed: true, required_files: required.length, checked_bytes: bytes }, null, 2));
}
