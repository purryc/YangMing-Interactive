import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
for(let i=1;i<=432;i++)if(!fs.existsSync(path.join(root,'qa/v2/frames_final',`frame_${String(i).padStart(4,'0')}.png`)))throw new Error('Missing frame '+i);
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8'});if(r.status!==0)throw new Error(r.stderr);return r.stdout;}
const dest=path.join(root,'output/voice_interaction_preview_v2.mp4');
run('ffmpeg',['-hide_banner','-loglevel','error','-y','-framerate','12','-i',path.join(root,'qa/v2/frames_final/frame_%04d.png'),'-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',dest]);
const probe=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',dest]));
run('ffmpeg',['-hide_banner','-v','error','-i',dest,'-f','null','-']);
const s=probe.streams[0];const report={full_decode:true,duration:Number(probe.format.duration),frames:Number(s.nb_frames),fps:s.r_frame_rate,width:s.width,height:s.height,bytes:Number(probe.format.size),audio:'none; synthetic viseme demonstration',passed:Number(s.nb_frames)===432&&Number(probe.format.duration)===36};
fs.writeFileSync(path.join(root,'qa/v2/video_validation.json'),JSON.stringify(report,null,2));console.log(report);if(!report.passed)throw new Error('Video validation failed');
