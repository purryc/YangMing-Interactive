import { ClassicLevel } from 'classic-level';
import { cp, mkdtemp, rm } from 'node:fs/promises';
import { tmpdir, homedir } from 'node:os';
import path from 'node:path';

// Read only the explicit Qwen settings from a disposable copy; never open AIRI's live DB.
export async function loadConfig() {
  let saved = {};
  for (const relative of ['@proj-airi/stage-tamagotchi', 'ai.moeru.airi']) {
    const temp = await mkdtemp(path.join(tmpdir(), 'scholar-qwen-'));
    let db;
    try {
      await cp(path.join(homedir(), 'Library/Application Support', relative, 'Local Storage/leveldb'), path.join(temp, 'db'), { recursive: true });
      db = new ClassicLevel(path.join(temp, 'db'), { keyEncoding: 'buffer', valueEncoding: 'buffer', createIfMissing: false });
      await db.open();
      const values = {};
      for await (const [key, value] of db.iterator()) {
        const match = key.toString().match(/settings\/qwen-omni\/(api-key|region|realtime-model|voice)$/);
        if (!match) continue;
        const text = value.subarray(1).toString(value[0] === 0 ? 'utf16le' : 'utf8');
        try { values[match[1]] = JSON.parse(text); } catch { values[match[1]] = text; }
      }
      if (typeof values['api-key'] === 'string' && values['api-key'].trim()) { saved = values; break; }
    } catch { /* Missing/locked copy: use environment configuration or explicit UI entry. */ }
    finally { if (db) await db.close().catch(() => {}); await rm(temp, { recursive: true, force: true }); }
  }
  const region = process.env.QWEN_REGION || saved.region || 'intl-singapore';
  return {
    key: process.env.DASHSCOPE_API_KEY || saved['api-key'] || '',
    source: process.env.DASHSCOPE_API_KEY ? 'environment' : saved['api-key'] ? 'airi' : 'none',
    endpoint: process.env.QWEN_REALTIME_URL || (region === 'cn-beijing' ? 'wss://dashscope.aliyuncs.com/api-ws/v1/realtime' : 'wss://dashscope-intl.aliyuncs.com/api-ws/v1/realtime'),
    region,
    model: process.env.QWEN_REALTIME_MODEL || saved['realtime-model'] || 'qwen3.5-omni-plus-realtime',
    // Male preset for the scholar; AIRI's Tina remains unchanged in the original app.
    voice: process.env.QWEN_REALTIME_VOICE || 'Ethan',
  };
}

export function sessionConfig(voice) {
  return {
    modalities: ['text', 'audio'], voice,
    instructions: '你是以王阳明为灵感的虚构书生数字角色。用中文与用户自然交流，温和、沉稳、简洁，每次通常两三句话。谈心学时用通俗例子，不编造古籍原文；不确定就说明。声音以成熟男性、从容清晰为目标，不夸张表演。不要声称自己是历史人物本人。',
    input_audio_format: 'pcm', output_audio_format: 'pcm',
    input_audio_transcription: { model: 'gummy-realtime-v1' },
    turn_detection: { type: 'server_vad', threshold: 0.5, prefix_padding_ms: 500, silence_duration_ms: 700 },
  };
}
