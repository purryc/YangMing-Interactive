class PcmCapture extends AudioWorkletProcessor {
  constructor() { super(); this.buffer = []; this.phase = 0; this.sum = 0; this.count = 0; }
  process(inputs) {
    const input = inputs[0]?.[0]; if (!input) return true;
    // Accumulating phase survives render quanta and handles 44.1/48 kHz devices.
    for (const sample of input) {
      this.sum += sample; this.count++; this.phase += 16000;
      if (this.phase >= sampleRate) {
        this.phase -= sampleRate;
        const v = Math.max(-1, Math.min(1, this.sum / this.count));
        this.buffer.push(Math.round(v * (v < 0 ? 32768 : 32767))); this.sum = 0; this.count = 0;
        if (this.buffer.length === 1600) {
          const pcm = new ArrayBuffer(3200), view = new DataView(pcm);
          this.buffer.forEach((v, i) => view.setInt16(i * 2, v, true));
          this.port.postMessage(pcm, [pcm]); this.buffer = [];
        }
      }
    }
    return true;
  }
}
registerProcessor('pcm_capture', PcmCapture);
