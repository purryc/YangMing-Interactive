import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { createFaceDriver } from '/live_face_v3.mjs';
import { bodyOnlyClip } from '/live_visemes.mjs';
import { AudioOutput } from './audio.mjs';

const $=s=>document.querySelector(s), host=$('#canvas');
const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(32,1,.01,100);
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setClearColor(0,0);
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.85;
host.append(renderer.domElement);
const pmrem=new THREE.PMREMGenerator(renderer), room=new RoomEnvironment();
scene.environment=pmrem.fromScene(room,.04).texture;room.dispose();pmrem.dispose();
scene.add(new THREE.HemisphereLight(0xfffaf1,0x86947b,.8));
const key=new THREE.DirectionalLight(0xffecd5,1.5);key.position.set(-3,4,5);scene.add(key);
const fill=new THREE.DirectionalLight(0xdbe8ff,1);fill.position.set(4,2,-2);scene.add(fill);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.minDistance=.35;controls.maxDistance=10;
let face,mixer,currentAction,actions={},bounds,root;
let socket,connecting,context,output,micStream,micSource,micNode,micMute;
let ready=false,generating=false,mode='idle',reply,inputReply,errorMessage='';
const diagnostics={loaded:false,bindings:0,frames:0,peakMouth:0,audioChunks:0,micChunks:0,state:'idle'};
window.scholarDiagnostics=diagnostics;
function status(text){$('#status').textContent=text;}
function setMode(name){mode=name;diagnostics.state=name;const next=actions[name];if(next&&next!==currentAction){next.reset().play();if(currentAction)next.crossFadeFrom(currentAction,.28,true);currentAction=next;}}
function frameView(portrait=false){if(!bounds)return;const center=bounds.getCenter(new THREE.Vector3()),size=bounds.getSize(new THREE.Vector3());const target=center.clone();if(portrait)target.y=bounds.min.y+size.y*.65;controls.target.copy(target);const d=size.y*(portrait?1.5:2.12);camera.position.set(target.x,target.y+size.y*.035,target.z+d);controls.update();}
$('#portrait').onclick=()=>frameView(true);$('#full').onclick=()=>frameView(false);
new GLTFLoader().load('/model.glb',gltf=>{
  root=gltf.scene;scene.add(root);root.updateMatrixWorld(true);
  bounds=new THREE.Box3().setFromObject(root);
  face=createFaceDriver(root,{smoothingMs:35});mixer=new THREE.AnimationMixer(root);
  for(const clip of gltf.animations)actions[clip.name]=mixer.clipAction(bodyOnlyClip(clip));
  setMode('idle');mixer.update(.001);root.updateMatrixWorld(true);bounds=new THREE.Box3().setFromObject(root,true);frameView(true);
  diagnostics.loaded=true;diagnostics.bindings=face.bindings;diagnostics.actions=Object.keys(actions);diagnostics.bounds={min:bounds.min.toArray(),max:bounds.max.toArray()};
  $('#model_status').textContent='书生已就绪';
},undefined,e=>{$('#model_status').textContent='模型加载失败，请刷新重试';console.error(e);});
new ResizeObserver(()=>{const {width,height}=host.getBoundingClientRect();renderer.setSize(width,height,false);camera.aspect=width/height;camera.updateProjectionMatrix();}).observe(host);
let previousTime=performance.now(),nextBlink=2.8,blinkStart=-10,totalTime=0;
function tick(){requestAnimationFrame(tick);const now=performance.now(),dt=Math.min((now-previousTime)/1000,.05);previousTime=now;totalTime+=dt;mixer?.update(dt);controls.update();
  if(face){
    const weights={...(output?.weights() || {})},gain=Number($('#strength').value);
    for(const n in weights)weights[n]*=gain;
    // v3's Basis mouth sits behind the beard. Blend from its visible closed-lip
    // MBP pose while voiced, preserving amplitude without sinking partial vowels.
    // This is a geometric baseline, not recognition of M/B/P phonemes.
    const voicedAmount=Object.values(weights).reduce((a,b)=>a+b,0);
    if(voicedAmount>0)weights.MBP=Math.max(0,1-voicedAmount);
    face.setSpeech(weights);
    if(totalTime>nextBlink){blinkStart=totalTime;nextBlink=totalTime+3+Math.random()*3;}
    const age=totalTime-blinkStart;face.setBlink(age>=0&&age<.18?Math.sin(age/.18*Math.PI):0);
    face.update(dt);
    const amount=voicedAmount;diagnostics.mouth=amount;diagnostics.peakMouth=Math.max(diagnostics.peakMouth,amount);diagnostics.audioChunks=output?.chunks||0;diagnostics.queuedMs=output?Math.max(0,(output.timeline.until-context.currentTime)*1000):0;
    const playing=output && output.sources.size>0;
    if(playing && mode!=='speak'){setMode('speak');status('先生正在说话 · 可以随时打断');}
    if(!playing && mode==='speak'){setMode(generating?'think':ready?'listen':'idle');status(generating?'先生正在思考…':ready?'正在聆听':'对话已结束');}
  }
  diagnostics.camera=camera.position.toArray();diagnostics.target=controls.target.toArray();diagnostics.frames++;renderer.render(scene,camera);
}
tick();
const config=await fetch('/api/status').then(r=>r.json());
$('#config_note').textContent=config.configured?`已${config.source==='airi'?'复用 AIRI':'读取环境变量'}的 Qwen 配置 · ${config.voice}`:'未找到密钥，请在下方填写后开始。';
$('#key').parentElement.hidden=config.configured;$('#region').parentElement.hidden=config.configured;
status(config.configured?'连接已准备好，开始聊聊吧':'请先填写连接设置');if(!config.configured)$('#settings').open=true;
function line(who,text){const hint=$('.hint');hint?.remove();const p=document.createElement('p'),b=document.createElement('b'),span=document.createElement('span');b.textContent=who;span.textContent=text;p.append(b,span);$('#transcript').append(p);$('#transcript').scrollTop=$('#transcript').scrollHeight;return span;}
async function audioReady(){context??=new AudioContext({sampleRate:24000,latencyHint:'interactive'});await context.resume();output??=new AudioOutput(context);}
function stopPlayback(){output?.stop();face?.stopSpeech({immediate:true});diagnostics.mouth=0;}
function send(e){if(socket?.readyState===WebSocket.OPEN)socket.send(JSON.stringify(e));}
async function connect(){
  await audioReady();if(ready)return;if(connecting)return connecting;
  errorMessage='';status('正在连接 Qwen…');
  connecting=new Promise((resolve,reject)=>{
    const ws=new WebSocket(`ws://${location.host}/realtime`);socket=ws;
    ws.onopen=()=>{send({type:'connect',key:$('#key').value,region:$('#region').value});$('#key').value='';};
    ws.onerror=()=>{errorMessage='本地连接失败，请确认服务仍在运行。';status(errorMessage);reject(new Error(errorMessage));};
    ws.onclose=()=>{if(socket!==ws)return;ready=false;generating=false;stopMic();stopPlayback();setMode('idle');status(errorMessage||'对话已结束，点击即可重新连接');reject(new Error(errorMessage||'连接已关闭'));};
    ws.onmessage=({data})=>{
      const e=JSON.parse(data);
      if(e.type==='ready'){ready=true;status('已连接，先生正在聆听');setMode('listen');resolve();}
      if(e.type==='response_start'){generating=true;reply=line('先生','');setMode('think');status('先生正在思考…');}
      if(e.type==='audio'){const bin=atob(e.pcm),bytes=Uint8Array.from(bin,c=>c.charCodeAt(0));output.push(bytes);}
      if(e.type==='text_delta'){reply??=line('先生','');reply.textContent+=e.text;$('#transcript').scrollTop=$('#transcript').scrollHeight;}
      if(e.type==='text_done' && reply)reply.textContent=e.text;
      if(e.type==='user_text'){if(inputReply)inputReply.textContent=e.text;else line('你',e.text);inputReply=null;}
      if(e.type==='response_done'){generating=false;if(!output.sources.size){setMode('listen');status('正在聆听');}}
      if(e.type==='interrupted'){generating=false;stopPlayback();setMode('listen');status('已停下，听你说');}
      if(e.type==='listening'){inputReply=line('你','正在听…');setMode('listen');status('正在听你说…');}
      if(e.type==='thinking'){setMode('think');status('先生正在思考…');}
      if(e.type==='error'){errorMessage=e.message;status(e.message);stopPlayback();stopMic();ws.close();reject(new Error(e.message));}
    };
  });
  try{await connecting;}finally{connecting=null;}
}
async function ask(text){if(!text.trim())return;$('#send').disabled=true;try{await connect();stopPlayback();line('你',text);send({type:'text',text});$('#text').value='';}catch(e){status(e.message);}finally{$('#send').disabled=false;}}
$('#text_form').onsubmit=e=>{e.preventDefault();void ask($('#text').value);};
document.querySelectorAll('[data-prompt]').forEach(b=>b.onclick=()=>ask(b.dataset.prompt));
function stopMic(){micStream?.getTracks().forEach(t=>t.stop());micStream=null;if(micNode)micNode.port.onmessage=null;micSource?.disconnect();micNode?.disconnect();micMute?.disconnect();micSource=micNode=micMute=null;$('#mic').textContent='开始语音对话';}
$('#mic').onclick=async()=>{
  if(micStream){stopMic();status('麦克风已关闭，可以继续文字对话');return;}
  $('#mic').disabled=true;
  try{
    // Permission is requested only after this explicit user action.
    await connect();
    const stream=await navigator.mediaDevices.getUserMedia({audio:{channelCount:1,echoCancellation:true,noiseSuppression:true,autoGainControl:true}});
    if(!ready){stream.getTracks().forEach(t=>t.stop());return;}
    micStream=stream;await context.audioWorklet.addModule('/mic_worklet.js');
    if(!micStream||!ready){stopMic();return;}
    micSource=context.createMediaStreamSource(stream);micNode=new AudioWorkletNode(context,'pcm_capture');micMute=context.createGain();micMute.gain.value=0;
    micSource.connect(micNode).connect(micMute).connect(context.destination);
    micNode.port.onmessage=({data})=>{if(ready && socket.bufferedAmount<320000){socket.send(data);diagnostics.micChunks++;const v=new DataView(data);let sum=0;for(let i=0;i<v.byteLength;i+=2)sum+=(v.getInt16(i,true)/32768)**2;diagnostics.micRms=Math.sqrt(sum/(v.byteLength/2));diagnostics.micPeak=Math.max(diagnostics.micPeak||0,diagnostics.micRms);}};
    $('#mic').textContent='关闭麦克风';status('麦克风已开启，先生正在聆听');
  }catch(e){stopMic();status(e.name==='NotAllowedError'?'麦克风未获许可；可在浏览器设置中开启，或直接文字对话。':e.message);}
  finally{$('#mic').disabled=false;}
};
$('#interrupt').onclick=()=>{stopPlayback();generating=false;send({type:'interrupt'});setMode(ready?'listen':'idle');status('已停下，听你说');};
$('#disconnect').onclick=()=>{stopMic();stopPlayback();socket?.close();};
window.addEventListener('pagehide',()=>{stopMic();stopPlayback();socket?.close();context?.close();});
