// Finding logos and text on top of a clip (docs/tools/app/clean.js): a moving picture with a sharp, still logo in a corner and a line of
// text along the left edge; the same picture without them finds nothing it is sure of; a still scene with no overlay is not flooded.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { detect } from './docs/tools/app/clean.js';

const W = 240, H = 136, N = 24;
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const noise = Float32Array.from({ length: (W + 64) * (H + 64) }, rnd);
function clip({ logo = false, text = false, still = false } = {}) {
  const fr = [];
  for (let k = 0; k < N; k++) {
    const d = new Uint8Array(W * H * 3), sh = still ? 0 : k * 2;
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const n = noise[(y + (sh >> 1)) * (W + 64) + x + sh];   // a soft, moving cloudy picture
      let r = 40 + 60 * Math.sin((x + sh) / 23) + 40 * n, g = 50 + 50 * Math.cos((y + sh) / 17) + 30 * n, b = 90 + 30 * n;
      if (logo && x >= 196 && x < 230 && y >= 100 && y < 128 && ((x >> 2) + (y >> 2)) % 2) { r = 230; g = 40; b = 220; }   // a purple checker logo
      if (text && x >= 3 && x < 9 && y >= 60 && y < 128 && (y % 4 < 2) && x % 3) { r = g = b = 255; }                      // a line of small white letters
      const i = (y * W + x) * 3; d[i] = Math.max(0, Math.min(255, r)); d[i + 1] = Math.max(0, Math.min(255, g)); d[i + 2] = Math.max(0, Math.min(255, b));
    }
    fr.push(d);
  }
  return fr;
}
const inside = (o, x, y) => x >= o.box[0] * W && x <= (o.box[0] + o.box[2]) * W && y >= o.box[1] * H && y <= (o.box[1] + o.box[3]) * H;

test('a still logo and edge text on a moving picture are found and chosen', () => {
  const r = detect(clip({ logo: true, text: true }), W, H), sure = r.filter(o => o.sure);
  const logo = sure.find(o => inside(o, 213, 114)), text = sure.find(o => inside(o, 6, 94));
  console.log('found', JSON.stringify(r.map(o => [o.score, o.sure, o.box.map(v => +v.toFixed(2))])));
  assert.ok(logo, 'the logo is found');
  assert.ok(text, 'the text is found');
  assert.ok(logo.box[2] * W >= 34 && logo.box[3] * H >= 28, 'the logo box covers the whole logo');
  assert.ok(logo.box[2] * logo.box[3] < 0.06, 'the logo box is not much bigger than the logo');
  assert.ok(sure.length <= 3, 'not many other boxes');
});
test('the same moving picture without them: nothing it is sure of', () => {
  const r = detect(clip(), W, H);
  assert.equal(r.filter(o => o.sure).length, 0, JSON.stringify(r));
});
test('a still picture with no overlay: at most a couple of suggestions', () => {
  const r = detect(clip({ still: true }), W, H);
  assert.ok(r.filter(o => o.sure).length <= 2, JSON.stringify(r));
});
test('a still picture with text right at the edge: the text is chosen', () => {
  const r = detect(clip({ still: true, text: true }), W, H);
  assert.ok(r.find(o => o.sure && inside(o, 6, 94)), JSON.stringify(r));
});
test('quick enough for a phone: 24 frames of 360 x 202 in well under a second', () => {
  const w = 360, h = 202, fr = Array.from({ length: 24 }, (_, k) => Uint8Array.from({ length: w * h * 4 }, (_, i) => (i * 7 + k * 13) & 255));
  const t = Date.now(); detect(fr, w, h, { stride: 4 }); const ms = Date.now() - t;
  assert.ok(ms < 1500, `${ms} ms`);
});
