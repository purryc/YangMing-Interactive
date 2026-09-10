import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
const dest=path.join(root,'output','voice_interaction_preview.mp4');
for(let i=1;i<=432;i++){if(!fs.existsSync(path.join(root,'qa','frames_final',`frame_${String(i).padStart(4,'0')}.png`)))throw new Error('Missing frame '+i);}
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8'});if(r.status!==0)throw new Error(r.stderr);return r.stdout;}
run('ffmpeg',['-hide_banner','-loglevel','error','-y','-framerate','24','-i',path.join(root,'qa','frames_final','frame_%04d.png'),'-i',path.join(root,'src','preview_labels.srt'),'-map','0:v:0','-map','1:0','-c:v','libx264','-crf','20','-preset','medium','-pix_fmt','yuv420p','-c:s','mov_text','-metadata:s:s:0','language=zho','-movflags','+faststart',dest]);
const probe=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',dest]));
run('ffmpeg',['-hide_banner','-v','error','-i',dest,'-f','null','-']);
const stream=probe.streams.find(s=>s.codec_type==='video');
const report={decoded:true,duration:Number(probe.format.duration),frames:stream.nb_frames,fps:stream.r_frame_rate,width:stream.width,height:stream.height,bytes:Number(probe.format.size),audio:'none; illustrative voice-interaction movement',subtitle_track:probe.streams.some(s=>s.codec_type==='subtitle')};
fs.writeFileSync(path.join(root,'qa','video_validation.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
