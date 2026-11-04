// Smooth out: stray frames are found, and the speed of a lurching clip is evened out (real ffmpeg).
import { engine, ff, frames, mad, info } from './tests_loops_harness.mjs';
import * as loops from './docs/tools/app/loops.js';
import { smoothPlan, defaultRecipe, runRecipe } from './docs/tools/app/steps.js';
import { defaultProfile } from './docs/tools/app/core.js';
let bad = 0; const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) bad++; };
const S = 64 * 36, mk = (n, f) => { const d = new Uint8Array(n * S); for (let i = 0; i < n; i++) for (let p = 0; p < S; p++) d[i * S + p] = f(i, p); return d; };
const pat = (t, p) => 128 + 100 * Math.sin((p % 64 + 3 * t) / 6) * Math.cos(Math.floor(p / 64) / 5);
// 1. a stray frame (a copy of a frame from far away) is dropped; nothing else is
let d = mk(120, (i, p) => i === 50 ? 255 - pat(i, p) : pat(i, p));
let pl = smoothPlan(d, 120, 30, { strength: 0 });
ok(pl.drop.length === 1 && pl.drop[0] === 50, `stray frame found (${pl.drop})`);
pl = smoothPlan(mk(120, (i, p) => pat(i, p)), 120, 30, { strength: 0.7 });
ok(pl.drop.length === 0, 'a clean clip loses no frames');
pl = smoothPlan(mk(120, (i, p) => pat(i, p)), 120, 30, { strength: 0 });
ok(!pl.changed, 'strength 0 and nothing to drop changes nothing');
// 2. a clip that lurches (4 of every 30 frames skipped) gets a steadier speed
ff('-f', 'lavfi', '-i', `color=c=black:s=320x180:r=30:d=12,geq=lum='128+100*sin((X+4*N)/17)*sin(Y/23+X/61)':cb=128:cr=128`, '-vf', `select='not(between(mod(n,30),10,13))',setpts=N/30/TB`, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '30', 'jerk.mp4');
const spread = f => { const F = frames(f, 96, 54), s = []; for (let i = 1; i < F.length; i++) s.push(mad(F[i - 1], F[i])); const q = s.slice(3, -3).sort((a, b) => a - b); return { n: F.length, ratio: q[Math.floor(q.length * .95)] / q[Math.floor(q.length * .05)], max: Math.max(...s.slice(3, -3)), med: q[q.length >> 1] }; };
const before = spread('jerk.mp4');
const R = defaultRecipe(); R.smooth.on = true; R.smooth.strength = 100;
const prof = { ...defaultProfile(), size: '320x180', maxMBps: 0 };
const r = await runRecipe(engine, loops, 'jerk.mp4', 'smooth.mp4', info('jerk.mp4'), R, prof, {});
const after = spread('smooth.mp4');
console.log('before', before, 'after', after, r.note);
ok(/smoothed/.test(r.note), `note says smoothed (${r.note})`);
const L = x => x.max / x.med;
ok(L(after) < L(before) * 0.65, `the lurch is ${L(before).toFixed(1)}x a normal step, then ${L(after).toFixed(1)}x`);
ok(Math.abs(after.n - before.n) < before.n * 0.2, `length about the same (${before.n} -> ${after.n} frames)`);
// 3. cut + smooth works together
const R2 = defaultRecipe(); R2.smooth.on = true; R2.cut = { on: true, start: 1, len: 4 };
const r2 = await runRecipe(engine, loops, 'jerk.mp4', 'smooth2.mp4', info('jerk.mp4'), R2, prof, {});
const i2 = info('smooth2.mp4'); ok(i2.duration > 3.3 && i2.duration < 4.7, `cut then smooth (${i2.duration.toFixed(2)} s)`);
console.log(bad ? 'FAILED' : 'ALL OK'); process.exit(bad ? 1 : 0);
