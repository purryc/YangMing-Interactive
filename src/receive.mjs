import fs from 'node:fs';
import path from 'node:path';
import {Hyper3D} from './hyper3d.mjs';
const root=path.resolve(import.meta.dirname,'..');
const generation=JSON.parse(fs.readFileSync(path.join(root,'qa','generation.json')));
function unwrap(r){const d=r.result??r;if(d.isError)throw new Error(JSON.stringify(d));if(d.structuredContent)return d.structuredContent;for(const b of d.content||[])if(b.type==='text'){try{return JSON.parse(b.text);}catch{}}throw new Error('Unexpected response');}
const api=new Hyper3D();
try{
 await api.init();
 const status=unwrap(await api.call('rodin_wait',{generation_id:generation.generation_id,timeout_seconds:35}));
 fs.writeFileSync(path.join(root,'qa','generation_status.json'),JSON.stringify(status,null,2));
 console.log(JSON.stringify(status));
 if(status.status==='completed'){
   const r=unwrap(await api.call('rodin_get_result',{generation_id:generation.generation_id}));
   const manifest={display_url:r.display_url,files:[]};
   for(const file of r.files){
     const name=path.basename(file.name);
     const dest=path.join(root,'output',name);
     if(!fs.existsSync(dest)){
       const response=await fetch(file.url);
       if(!response.ok)throw new Error('Download failed '+response.status);
       fs.writeFileSync(dest,Buffer.from(await response.arrayBuffer()));
     }
     manifest.files.push({name,role:file.role,mime_type:file.mime_type,bytes:fs.statSync(dest).size});
   }
   fs.writeFileSync(path.join(root,'qa','source_manifest.json'),JSON.stringify(manifest,null,2));
   console.log(JSON.stringify(manifest,null,2));
 }
}finally{api.close();}
