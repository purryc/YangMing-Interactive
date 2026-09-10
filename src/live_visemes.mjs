// Engine adapter: works with a Three.js-style scene graph; no network or audio capture.
export const VISEME_NAMES = ['viseme_A','viseme_E','viseme_I','viseme_O','viseme_U'];
export function normalizeVisemes(input={}) {
  const values=VISEME_NAMES.map(name=>Math.min(1,Math.max(0,Number(input[name]??input[name.slice(-1)]??0)||0)));
  const divisor=Math.max(1,values.reduce((a,b)=>a+b,0));
  return values.map(v=>v/divisor);
}
export function createLiveVisemeDriver(root,{smoothingMs=55}={}) {
  const bindings=[];
  root.traverse(object=>{
    if(!object.morphTargetDictionary||!object.morphTargetInfluences)return;
    const indices=VISEME_NAMES.map(n=>object.morphTargetDictionary[n]);
    if(indices.every(Number.isInteger))bindings.push({object,indices});
  });
  if(!bindings.length)throw new Error('No A/E/I/O/U morph targets found');
  let current=[0,0,0,0,0],target=[0,0,0,0,0];
  function write(){for(const {object,indices} of bindings)indices.forEach((index,i)=>object.morphTargetInfluences[index]=current[i]);}
  return {
    bindings:bindings.length,
    set(input){target=normalizeVisemes(input);},
    update(deltaSeconds){
      const dt=Math.max(0,Number(deltaSeconds)||0);
      const alpha=smoothingMs>0?1-Math.exp(-dt*1000/smoothingMs):1;
      current=current.map((v,i)=>v+(target[i]-v)*alpha);write();return [...current];
    },
    stop({immediate=false}={}){target=[0,0,0,0,0];if(immediate){current=[...target];write();}},
  };
}
// Remove demonstration mouth curves before using an independent live mouth driver.
export function bodyOnlyClip(clip){const clone=clip.clone();clone.tracks=clone.tracks.filter(t=>!t.name.includes('morphTargetInfluences'));return clone;}
