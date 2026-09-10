import test from 'node:test';
import assert from 'node:assert/strict';
import { MouthTimeline, decodePcm, mouthFrames } from './audio.mjs';
test('PCM16 decoding respects little endian and typed array offset',()=>{
  assert.deepEqual([...decodePcm(new Uint8Array([99,0,128,255,127,99]).subarray(1,5))],[-1,32767/32768]);
  assert.throws(()=>decodePcm(new Uint8Array(3)));
});
test('silence closes mouth; speech weights stay bounded',()=>{
  const silent=mouthFrames(new Float32Array(2400));
  assert(silent.every(f=>Object.values(f.weights).every(v=>v===0)));
  const voice=Float32Array.from({length:2400},(_,i)=>Math.sin(i*.12)*.4);
  const frames=mouthFrames(voice);
  assert(frames.some(f=>f.weights.A>.1));
  assert(frames.every(f=>Object.values(f.weights).reduce((a,b)=>a+b,0)<=.821));
});
test('queue uses playback time, stays closed before start and in underrun; cancel drops future mouth',()=>{
  const t=new MouthTimeline(),samples=new Float32Array(2400).fill(.1);
  const a=t.append(samples,2),b=t.append(samples,2.01);
  assert.equal(a,2.025);assert(Math.abs(b-2.125)<1e-8);
  assert.deepEqual(t.at(2),{});assert(t.at(2.04).A>0);
  t.clear(2.06);assert.deepEqual(t.at(2.15),{});
  const c=t.append(samples,3);assert.equal(c,3.025);assert.deepEqual(t.at(3),{});
  assert.deepEqual(t.at(3.2),{});
});
