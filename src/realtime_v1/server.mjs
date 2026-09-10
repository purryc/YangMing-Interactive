import http from 'node:http';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { randomUUID } from 'node:crypto';
import WebSocket, { WebSocketServer } from 'ws';
import { loadConfig, sessionConfig } from './config.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const config = await loadConfig();
const mime = { '.html':'text/html', '.mjs':'text/javascript', '.js':'text/javascript', '.css':'text/css', '.glb':'model/gltf-binary' };
const files = new Map(['index.html','client.mjs','audio.mjs','mic_worklet.js','style.css'].map(n=>['/'+n,path.join(here,n)]));
files.set('/model.glb',path.resolve(here,'../../output/scholar_voice_rig_v3.glb'));
files.set('/live_face_v3.mjs',path.resolve(here,'../live_face_v3.mjs'));
files.set('/live_visemes.mjs',path.resolve(here,'../live_visemes.mjs'));
const server = http.createServer(async (req,res) => {
  if (req.headers.host !== `127.0.0.1:${server.address().port}` && req.headers.host !== `localhost:${server.address().port}`) { res.writeHead(403).end(); return; }
  try {
    const url = new URL(req.url,'http://localhost');
    if(url.pathname === '/favicon.ico') { res.writeHead(204).end(); return; }
    if(url.pathname === '/api/status') { res.setHeader('Cache-Control','no-store'); res.setHeader('Content-Type','application/json'); res.end(JSON.stringify({configured:!!config.key,source:config.source,model:config.model,voice:config.voice,region:config.region})); return; }
    let filename = files.get(url.pathname === '/' ? '/index.html' : url.pathname);
    if (url.pathname.startsWith('/vendor/')) {
      const relative = url.pathname.slice('/vendor/'.length);
      if (/^(build\/three\.(module|core)\.js|examples\/jsm\/[\w/.-]+\.js)$/.test(relative) && !relative.includes('..')) filename=path.join(here,'node_modules/three',relative);
    }
    if(!filename) { res.writeHead(404).end('Not found'); return; }
    const data = await readFile(filename);
    res.setHeader('Content-Type',mime[path.extname(filename)] || 'application/octet-stream');
    res.setHeader('X-Content-Type-Options','nosniff');
    res.setHeader('Cache-Control','no-cache');
    res.setHeader('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; connect-src 'self' blob: ws://127.0.0.1:* ws://localhost:*; worker-src 'self' blob:; media-src 'self' blob:");
    res.end(data);
  } catch { res.writeHead(404).end('Not found'); }
});
const wss = new WebSocketServer({noServer:true,maxPayload:1024*1024});
server.on('upgrade',(req,socket,head)=>{
  const port = server.address().port;
  if(req.url !== '/realtime' || ![`http://127.0.0.1:${port}`,`http://localhost:${port}`].includes(req.headers.origin) || wss.clients.size >= 3) { socket.destroy(); return; }
  wss.handleUpgrade(req,socket,head,ws=>wss.emit('connection',ws));
});
wss.on('connection',client=>{
  let upstream, ready=false, generating=false, timer, activeId=null;
  const blocked = new Set();
  const send = data => {if(client.readyState===WebSocket.OPEN)client.send(JSON.stringify(data));};
  const emit = data => {if(upstream?.readyState===WebSocket.OPEN)upstream.send(JSON.stringify({event_id:randomUUID(),...data}));};
  const stop = () => { ready=false; clearTimeout(timer); upstream?.close(); };
  const interrupt = () => {
    if(activeId)blocked.add(activeId);
    if(generating)emit({type:'response.cancel'});
    generating=false; send({type:'interrupted'});
  };
  client.on('message',(data,isBinary)=>{
    if(isBinary) { if(ready && data.length <= 32000 && data.length%2===0)emit({type:'input_audio_buffer.append',audio:data.toString('base64')}); return; }
    let event; try {event=JSON.parse(data);}catch{return;}
    if(event.type==='connect' && !upstream) {
      const key = config.key || (typeof event.key==='string' ? event.key.trim() : '');
      if(!key) {send({type:'error',message:'未找到 Qwen 密钥。请展开连接设置，输入 DashScope API Key。'});return;}
      let endpoint=config.endpoint;
      if(!config.key && event.region === 'cn-beijing')endpoint='wss://dashscope.aliyuncs.com/api-ws/v1/realtime';
      upstream=new WebSocket(`${endpoint}?model=${encodeURIComponent(config.model)}`,{headers:{Authorization:`Bearer ${key}`},handshakeTimeout:15000,maxPayload:8*1024*1024});
      timer=setTimeout(()=>{send({type:'error',message:'Qwen 连接超时，请检查网络、密钥地区与服务权限后重试。'});stop();client.close();},20000);
      upstream.on('open',()=>emit({type:'session.update',session:sessionConfig(config.voice)}));
      upstream.on('message',data=>{
        let e;try{e=JSON.parse(data);}catch{return;}
        if(e.type==='session.updated'){clearTimeout(timer);ready=true;send({type:'ready'});}
        if(e.type==='response.created'){activeId=e.response?.id;generating=true;send({type:'response_start'});}
        if(e.type==='input_audio_buffer.speech_started') {interrupt();send({type:'listening'});}
        if(e.type==='input_audio_buffer.speech_stopped')send({type:'thinking'});
        if(e.type==='conversation.item.input_audio_transcription.completed')send({type:'user_text',text:e.transcript || ''});
        if(blocked.has(e.response_id))return;
        if(e.type==='response.audio.delta')send({type:'audio',pcm:e.delta});
        if(e.type==='response.audio_transcript.delta')send({type:'text_delta',text:e.delta || ''});
        if(e.type==='response.audio_transcript.done')send({type:'text_done',text:e.transcript || ''});
        if(e.type==='response.done') {generating=false;send({type:'response_done'});}
        if(e.type==='error') {
          const raw=String(e.error?.message || 'Qwen 请求失败');
          if(/no active response|no response.*cancel/i.test(raw))return;
          send({type:'error',message:raw.replaceAll(key,'[redacted]').replace(/sk-[\w-]+/g,'[redacted]').slice(0,350)});
        }
      });
      upstream.on('error',()=>send({type:'error',message:'Qwen 连接失败，请检查密钥地区、模型权限或网络。'}));
      upstream.on('close',()=>{clearTimeout(timer);ready=false;send({type:'closed'});client.close();});
    }
    if(event.type==='text' && ready && typeof event.text==='string' && event.text.trim()) {
      interrupt();
      emit({type:'conversation.item.create',item:{type:'message',role:'user',content:[{type:'input_text',text:event.text.slice(0,2000)}]}});
      emit({type:'response.create',response:{modalities:['text','audio']}});
    }
    if(event.type==='interrupt' && ready)interrupt();
  });
  client.on('close',stop);client.on('error',stop);
});
server.listen(Number(process.env.PORT || 8766),'127.0.0.1',()=>console.log(JSON.stringify({url:`http://127.0.0.1:${server.address().port}`,configured:!!config.key,source:config.source,model:config.model,voice:config.voice})));
