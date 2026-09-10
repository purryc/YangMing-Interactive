import WebSocket from 'ws';
import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { decodePcm,mouthFrames } from './audio.mjs';
const output=fileURLToPath(new URL('../../qa/realtime_v1/',import.meta.url));await mkdir(output,{recursive:true});
const started=Date.now(),chunks=[],events={},report={started:new Date().toISOString(),prompt:'只说一句：知是行之始，行是知之成。',success:false};
const ws=new WebSocket('ws://127.0.0.1:8766/realtime',{origin:'http://127.0.0.1:8766'});
const timeout=setTimeout(()=>{report.error='timeout';ws.close();},55000);
ws.on('open',()=>ws.send(JSON.stringify({type:'connect'})));
ws.on('message',data=>{const e=JSON.parse(data);events[e.type]=(events[e.type]||0)+1;
  if(e.type==='ready'){report.ready_ms=Date.now()-started;ws.send(JSON.stringify({type:'text',text:report.prompt}));}
  if(e.type==='audio'){report.first_audio_ms??=Date.now()-started;chunks.push(Buffer.from(e.pcm,'base64'));}
  if(e.type==='text_done')report.transcript=e.text;
  if(e.type==='error'){report.error=e.message;ws.close();}
  if(e.type==='response_done'){report.success=chunks.length>0;ws.close();}
});
ws.on('error',()=>{report.error='local websocket error';});
ws.on('close',async()=>{clearTimeout(timeout);const pcm=Buffer.concat(chunks);report.audio_seconds=pcm.length/48000;report.events=events;
  if(pcm.length){const frames=mouthFrames(decodePcm(pcm));report.nonzero_mouth_frames=frames.filter(f=>f.weights.A>0).length;const header=Buffer.alloc(44);header.write('RIFF');header.writeUInt32LE(36+pcm.length,4);header.write('WAVEfmt ',8);header.writeUInt32LE(16,16);header.writeUInt16LE(1,20);header.writeUInt16LE(1,22);header.writeUInt32LE(24000,24);header.writeUInt32LE(48000,28);header.writeUInt16LE(2,32);header.writeUInt16LE(16,34);header.write('data',36);header.writeUInt32LE(pcm.length,40);await writeFile(output+'qwen_reply.wav',Buffer.concat([header,pcm]));}
  await writeFile(output+'provider_validation.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));process.exitCode=report.success?0:1;
});
