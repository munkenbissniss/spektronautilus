// Runs every filter with the computer's own ffmpeg and checks the result. Needs ffmpeg and ffprobe on the PATH.
import test from 'node:test'; import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process'; import { mkdtempSync } from 'node:fs'; import { tmpdir } from 'node:os'; import { join } from 'node:path';
import { FILTERS, filterChain } from './docs/tools/app/filters.js';
import { encodeArgs, defaultProfile, makeName, defaultNaming } from './docs/tools/app/core.js';

const T = mkdtempSync(join(tmpdir(), 'spkf_')), src = join(T, 'src.mp4');
const run = (cmd, args) => spawnSync(cmd, args, { encoding: 'utf8' });
let r = run('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=s=640x360:r=25:d=2', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', src]);
assert.equal(r.status, 0, r.stderr);
const prof = { ...defaultProfile(), preset: 'ultrafast', size: '640x360' };
const info = { width: 640, height: 360, fps: 25, duration: 2, alpha: false, hasAudio: false };
const probe = f => { const o = run('ffprobe', ['-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,nb_read_frames,pix_fmt', '-of', 'csv=p=0', f]).stdout.trim().split(','); return { w: +o[0], h: +o[1], pix: o[2], n: +o[3] }; };
const plain = join(T, 'plain.mp4'); assert.equal(run('ffmpeg', encodeArgs(src, plain, prof, info)).status, 0);
const psnr = (a, b) => { const o = run('ffmpeg', ['-i', a, '-i', b, '-lavfi', 'psnr', '-f', 'null', '-']).stderr; const m = o.match(/average:([\w.]+)/); return m ? (m[1] === 'inf' ? 99 : +m[1]) : NaN; };

test('there are ten filters with unique ids', () => { assert.equal(FILTERS.length, 10); assert.equal(new Set(FILTERS.map(f => f.id)).size, 10); });
for (const f of FILTERS) {
  for (const amount of [0, 50, 100]) {
    test(`${f.id} at ${amount}: valid video, right size and length`, () => {
      const out = join(T, `${f.id}_${amount}.mp4`);
      const extra = filterChain(f.id, amount, { w: 640, h: 360, dur: 2 });
      const res = run('ffmpeg', encodeArgs(src, out, prof, info, { extra }));
      assert.equal(res.status, 0, extra + '\n' + res.stderr.split('\n').slice(-6).join('\n'));
      const p = probe(out); assert.deepEqual([p.w, p.h, p.pix], [640, 360, 'yuv420p']); assert.equal(p.n, 50);
      if (amount === 50) assert.ok(psnr(plain, out) < 45, 'looks different from the plain clip');
    });
  }
}
test('filters work at other sizes and with a longer repeat', () => {
  const info2 = { ...info, width: 640, height: 360 }, prof2 = { ...prof, size: '854x480', fit: 'fill' };
  for (const f of ['kaleido', 'mirror', 'pixel', 'hue']) {
    const out = join(T, `big_${f}.mp4`), extra = filterChain(f, 60, { w: 854, h: 480, dur: 2 });
    const res = run('ffmpeg', encodeArgs(src, out, prof2, info2, { extra, repeat: 2 })); assert.equal(res.status, 0, f + res.stderr.slice(-300));
    const p = probe(out); assert.deepEqual([p.w, p.h], [854, 480]); assert.equal(p.n, 100);
  }
});
test('colour cycle goes round once per clip (a still picture ends the way it started)', () => {
  const still = join(T, 'still.mp4'); run('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', 'smptebars=s=640x360:r=25:d=2', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', still]);
  const out = join(T, 'hue.mp4'), mid = join(T, 'hue_mid.mp4');
  assert.equal(run('ffmpeg', encodeArgs(still, out, prof, info, { extra: filterChain('hue', 50, { w: 640, h: 360, dur: 2 }) })).status, 0);
  const png = n => { const p = join(T, `h${n}.png`); run('ffmpeg', ['-v', 'error', '-y', '-i', out, '-vf', `select=eq(n\\,${n})`, '-frames:v', '1', p]); return p; };
  const first = png(0), last = png(49), half = png(25);
  assert.ok(psnr(first, last) > 20, 'last frame is close to the first: ' + psnr(first, last));
  assert.ok(psnr(first, half) < 14, 'half way the colours are different: ' + psnr(first, half));
});
test('the {filter} naming token', () => {
  assert.equal(makeName('My Clip.mov', 0, { ...defaultNaming(), template: '{name}_{filter}' }, null, null, '', { filter: 'neon' }), 'My_Clip_neon');
});
