import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFile } from 'node:fs/promises';
const code=await readFile(new URL('mic_worklet.js',import.meta.url),'utf8');
for(const rate of [24000,44100,48000])test(`worklet resamples ${rate} Hz to continuous 16k PCM`,()=>{
  const packets=[];let Capture;
  const context={sampleRate:rate,AudioWorkletProcessor:class{port={postMessage:b=>packets.push(b)}},registerProcessor:(_,c)=>{Capture=c;}};
  vm.runInNewContext(code,context);const worklet=new Capture();
  for(let i=0;i<rate;i+=128)worklet.process([[new Float32Array(Math.min(128,rate-i)).fill(.25)]]);
  assert.equal(packets.length,10);assert.equal(packets[0].byteLength,3200);assert.equal(new DataView(packets[0]).getInt16(0,true),8192);
});
