import fs from 'node:fs';
import path from 'node:path';
import {Hyper3D} from './hyper3d.mjs';
const root=path.resolve(import.meta.dirname,'..');
for(const dir of ['reference','output','qa']) fs.mkdirSync(path.join(root,dir),{recursive:true});
const ref=path.join(root,'reference','character_sheet.png');
if(!fs.existsSync(ref)) fs.copyFileSync('/var/folders/_5/3rw23kp94_3_xfcy1pzzs7v00000gp/T/codex-clipboard-754c81e1-d2a9-45ef-a244-08362a7619ac.png',ref);
const record=path.join(root,'qa','generation.json');
if(fs.existsSync(record)) throw new Error('Generation record exists; do not submit twice.');
function unwrap(r){
  const d=r.result??r;
  if(d.isError) throw new Error(JSON.stringify(d));
  if(d.structuredContent) return d.structuredContent;
  for(const b of d.content||[])if(b.type==='text'){try{return JSON.parse(b.text);}catch{}}
  throw new Error('Unexpected response: '+JSON.stringify(d));
}
const api=new Hyper3D();
try{
  await api.init();
  const result=unwrap(await api.call('rodin_create_uploads',{files:[{filename:'character_sheet.png',mime_type:'image/png',size_bytes:fs.statSync(ref).size}]}));
  const u=result.uploads[0];
  const put=await fetch(u.upload_url,{method:'PUT',headers:u.headers,body:fs.readFileSync(ref)});
  if(!put.ok) throw new Error('Upload failed HTTP '+put.status);
  console.log('Reference uploaded successfully.');
  const args={
    prompt:'Create exactly ONE complete 3D character from this turnaround sheet. All panels depict the SAME character from different angles, NOT separate people. Match the full-body front, side and back views: adorable elderly Chinese scholar, oversized round head and big brown eyes, white eyebrows, white side hair, sculpted flowing white moustache and long pointed white beard, tall soft black traditional scholar hat with rear ribbons, blue gray brocade wide-sleeved open robe, ivory inner robe, brown belt and tassels, short legs and black cloth shoes. Preserve proportions, face identity, costume patterns and muted colors. Symmetric T pose, arms extended horizontally and feet separated slightly. Single isolated character, upright, front facing, neutral expression, animation-friendly quad mesh. No reference board, no other heads or figures, no text, labels, backdrop, floor or pedestal.',
    reference_upload_ids:[u.upload_id],mesh_mode:'Quad',tier:'Gen-2.5-Medium',quality_override:30000,geometry_file_format:'glb'
  };
  fs.writeFileSync(record,JSON.stringify({state:'submission_started',provider:'Hyper3D',estimated_credits:0.5,args,started_at:new Date().toISOString()},null,2));
  const generation=unwrap(await api.call('rodin_generate',args));
  fs.writeFileSync(record,JSON.stringify({provider:'Hyper3D',estimated_credits:0.5,args,...generation},null,2));
  console.log(JSON.stringify({generation_id:generation.generation_id,status:generation.status}));
}finally{api.close();}
