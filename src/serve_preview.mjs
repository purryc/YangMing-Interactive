import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
const mime={'.html':'text/html; charset=utf-8','.mp4':'video/mp4','.png':'image/png','.md':'text/plain; charset=utf-8','.glb':'model/gltf-binary'};
http.createServer((req,res)=>{
 const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
 const file=path.resolve(root,'.'+(pathname==='/'?'/output/preview.html':pathname));
 if(!file.startsWith(root+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404);return res.end();}
 const size=fs.statSync(file).size;const headers={'Content-Type':mime[path.extname(file)]||'application/octet-stream','Accept-Ranges':'bytes'};
 const m=/^bytes=(\d+)-(\d*)$/.exec(req.headers.range||'');
 if(m){const start=Number(m[1]),end=Math.min(m[2]?Number(m[2]):size-1,size-1);if(start>=size){res.writeHead(416);return res.end();}res.writeHead(206,{...headers,'Content-Length':end-start+1,'Content-Range':`bytes ${start}-${end}/${size}`});fs.createReadStream(file,{start,end}).pipe(res);}
 else {res.writeHead(200,{...headers,'Content-Length':size});fs.createReadStream(file).pipe(res);}
}).listen(0,'127.0.0.1',function(){console.log('PREVIEW_URL=http://127.0.0.1:'+this.address().port+'/output/preview.html');});
