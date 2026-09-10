// Acoustic approximation adapted from AIRI pcm-playback.ts. No phoneme timestamps inferred.
export function decodePcm(bytes) {
  if (bytes.byteLength % 2) throw new Error('PCM16 requires complete samples');
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const samples = new Float32Array(bytes.byteLength / 2);
  for (let i = 0; i < samples.length; i++) samples[i] = view.getInt16(i * 2, true) / 32768;
  return samples;
}
export function mouthFrames(samples, sampleRate = 24000) {
  const frames = [], step = Math.round(sampleRate * .025);
  for (let start = 0; start < samples.length; start += step) {
    const end = Math.min(start + step, samples.length); let sum = 0, crossings = 0;
    for (let i = start; i < end; i++) { sum += samples[i] ** 2; if (i > start && (samples[i] < 0) !== (samples[i-1] < 0)) crossings++; }
    const rms = Math.sqrt(sum / (end - start));
    const open = rms <= .012 ? 0 : Math.min(.82, (Math.min(1, (rms - .012) * 6)) ** .72);
    const wide = Math.min(1, crossings / Math.max(1, end - start - 1) * 12);
    frames.push({ start: start / sampleRate, end: end / sampleRate, weights: { A: open * .62, E: open * wide * .38, O: open * (1 - wide) * .38 } });
  }
  return frames;
}
export class MouthTimeline {
  frames = []; until = 0;
  append(samples, currentTime, sampleRate = 24000) {
    const start = Math.max(currentTime + .025, this.until);
    this.until = start + samples.length / sampleRate;
    this.frames.push(...mouthFrames(samples, sampleRate).map(f => ({...f, start:f.start + start, end:f.end + start})));
    return start;
  }
  at(time) {
    while (this.frames.length && this.frames[0].end <= time) this.frames.shift();
    return this.frames[0]?.start <= time ? this.frames[0].weights : {};
  }
  clear(time = 0) { this.frames = []; this.until = time; }
}
export class AudioOutput {
  constructor(context) { this.context = context; this.timeline = new MouthTimeline(); this.sources = new Set(); this.chunks = 0; }
  push(bytes) {
    const samples = decodePcm(bytes); if (!samples.length) return;
    const buffer = this.context.createBuffer(1, samples.length, 24000); buffer.copyToChannel(samples, 0);
    const source = this.context.createBufferSource(); source.buffer = buffer; source.connect(this.context.destination);
    const start = this.timeline.append(samples, this.context.currentTime);
    this.sources.add(source); source.onended = () => { this.sources.delete(source); source.disconnect(); };
    source.start(start); this.chunks++;
  }
  stop() { for (const source of this.sources) { source.stop(); source.disconnect(); } this.sources.clear(); this.timeline.clear(this.context.currentTime); }
  weights() {
    // Output timestamp follows samples heard at the device, including hardware latency.
    const timestamp = this.context.getOutputTimestamp?.();
    const time = timestamp?.contextTime > 0 ? timestamp.contextTime : Math.max(0, this.context.currentTime - (this.context.outputLatency || 0));
    return this.timeline.at(time);
  }
}
