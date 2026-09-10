import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const root = path.resolve(import.meta.dirname, '..');
export class Hyper3D {
  constructor() {
    this.proc = spawn('codex', ['app-server', '--stdio'], {stdio:['pipe','pipe','pipe']});
    this.pending = new Map(); this.seq = 0; let buffer = '';
    this.proc.stderr.on('data',()=>{});
    this.proc.stdout.on('data', chunk=>{
      buffer+=chunk; let pos;
      while((pos=buffer.indexOf('\n'))>=0) {
        const line=buffer.slice(0,pos); buffer=buffer.slice(pos+1);
        let m; try {m=JSON.parse(line);} catch {continue;}
        const p=this.pending.get(m.id);
        if(p){this.pending.delete(m.id); clearTimeout(p.timer); m.error?p.reject(new Error(JSON.stringify(m.error))):p.resolve(m.result);}
      }
    });
  }
  request(method,params,timeout=90000) {
    return new Promise((resolve,reject)=>{
      const id=++this.seq;
      const timer=setTimeout(()=>{this.pending.delete(id);reject(new Error('Timeout: '+method));},timeout);
      this.pending.set(id,{resolve,reject,timer});
      this.proc.stdin.write(JSON.stringify({id,method,params})+'\n');
    });
  }
  async init() {
    await this.request('initialize',{clientInfo:{name:'hyper3d-character-workflow',version:'1.0.0'},capabilities:{experimentalApi:true}});
    this.proc.stdin.write(JSON.stringify({method:'initialized',params:{}})+'\n');
  }
  async inventory() {
    const r=await this.request('mcpServerStatus/list',{detail:'toolsAndAuthOnly',limit:100});
    return r.data.find(x=>x.name==='hyper3d');
  }
  async call(tool,args) {
    if(!this.thread) {
      const r=await this.request('thread/start',{cwd:root,ephemeral:true});
      this.thread=r.thread.id;
    }
    const r=await this.request('mcpServer/tool/call',{threadId:this.thread,server:'hyper3d',tool,arguments:args});
    return r;
  }
  close(){this.proc.kill();}
}
if (process.argv[1] === import.meta.filename) {
  const api=new Hyper3D();
  try {
    await api.init();
    if(process.argv[2]==='inventory') {
      const r=await api.inventory();
      fs.mkdirSync(path.join(root,'qa'),{recursive:true});
      fs.writeFileSync(path.join(root,'qa','hyper3d_inventory.json'),JSON.stringify(r,null,2));
      console.log(JSON.stringify(r,null,2));
    } else {
      const result=await api.call(process.argv[2],JSON.parse(process.argv[3]||'{}'));
      console.log(JSON.stringify(result,null,2));
    }
  } finally {api.close();}
}
