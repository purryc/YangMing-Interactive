export const VISEMES=['A','E','I','O','U','MBP','FV','TH','TDNL','CHSHZH','KGNG'];
export const EMOTIONS=['Happy','Angry','Sad','Laughing','Surprised','Thinking','Proud','Helpless'];
const clamp=v=>Math.max(0,Math.min(1,Number(v)||0));
export function createFaceDriver(root,{smoothingMs=60}={}){
 const bindings=[];root.traverse(o=>{if(o.morphTargetDictionary&&o.morphTargetInfluences)bindings.push(o);});
 if(!bindings.length)throw new Error('No facial morph targets');
 let speech={},emotion=null,emotionWeight=0,gaze=[0,0],blink=[0,0];const current=new Map();
 function targets(o){
  const result={};const amount=Object.values(speech).reduce((a,b)=>a+b,0),divisor=Math.max(1,amount);
  const isMouth=o.morphTargetDictionary.viseme_A!==undefined;const em=isMouth?emotionWeight*(1-Math.min(1,amount)*.7):emotionWeight;
  for(const [n,v] of Object.entries(speech))result['viseme_'+n]=v/divisor*(1-em);
  if(emotion)result['expr_'+emotion]=em;
  result.blink_L=blink[0]*(1-em);result.blink_R=blink[1]*(1-em);
  result.gaze_L=Math.max(0,gaze[0])*(1-em);result.gaze_R=Math.max(0,-gaze[0])*(1-em);result.gaze_U=Math.max(0,gaze[1])*(1-em);result.gaze_D=Math.max(0,-gaze[1])*(1-em);
  return result;
 }
 return {
  bindings:bindings.length,
  setSpeech(values={}){speech=Object.fromEntries(VISEMES.map(n=>[n,clamp(values[n]??values['viseme_'+n])]));},
  setEmotion(name=null,weight=1){if(name!==null&&!EMOTIONS.includes(name))throw new Error('Unknown emotion '+name);emotion=name;emotionWeight=name?clamp(weight):0;},
  setGaze(x=0,y=0){gaze=[Math.max(-1,Math.min(1,Number(x)||0)),Math.max(-1,Math.min(1,Number(y)||0))];},
  setBlink(left=0,right=left){blink=[clamp(left),clamp(right)];},
  update(dt){const a=smoothingMs>0?1-Math.exp(-Math.max(0,dt)*1000/smoothingMs):1;for(const o of bindings){const target=targets(o);let state=current.get(o);if(!state){state={};current.set(o,state);}for(const [name,index] of Object.entries(o.morphTargetDictionary)){const value=state[name]??0;state[name]=value+((target[name]??0)-value)*a;o.morphTargetInfluences[index]=state[name];}}},
  stopSpeech({immediate=false}={}){speech={};if(immediate)for(const o of bindings)for(const n of VISEMES){const i=o.morphTargetDictionary['viseme_'+n];if(i!==undefined){o.morphTargetInfluences[i]=0;if(current.has(o))current.get(o)['viseme_'+n]=0;}}},
  reset(){speech={};emotion=null;emotionWeight=0;gaze=[0,0];blink=[0,0];current.clear();for(const o of bindings)o.morphTargetInfluences.fill(0);},
 };
}
