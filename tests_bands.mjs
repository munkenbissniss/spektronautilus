// Smooth motion in bands (the browser version, so a phone does not run out of memory): the same picture as in one go, at a fraction of
// the memory. Real ffmpeg; the clip is a 2 s piece of a portrait 1080x1920 loop (made here, so the test needs no outside file).
import { engine, ff, info, d, frames } from './tests_loops_harness.mjs';
import * as loops from './docs/tools/app/loops.js';
import { defaultRecipe, runRecipe, bandPlan, BAND_PX } from './docs/tools/app/steps.js';
import { defaultProfile } from './docs/tools/app/core.js';
import { execFileSync, spawn } from 'node:child_process'; import { join } from 'node:path';
let bad = 0; const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) bad++; };
// 1. the bands cover every row once, have even sizes, and stay under the pixel budget (margins included)
for (const [w, h] of [[1080, 1920], [1920, 1080], [3840, 2160], [2160, 3840], [854, 480]]) {
  const b = bandPlan(w, h);
  if (w * h <= BAND_PX) { ok(b.length === 0, `${w}x${h}: small enough for one go`); continue; }
  const rows = new Array(h).fill(0); for (const x of b) for (let y = x.y0 + x.top; y < x.y0 + x.top + x.keep; y++) rows[y]++;
  ok(rows.every(n => n === 1) && b.every(x => x.ch % 2 === 0 && x.keep % 2 === 0 && x.y0 + x.ch <= h && x.top + x.keep <= x.ch), `${w}x${h}: ${b.length} bands cover every row once, even sizes`);
  ok(Math.max(...b.map(x => x.ch)) * w <= BAND_PX * 1.02, `${w}x${h}: each band is at most ${Math.round(Math.max(...b.map(x => x.ch)) * w / 1e3)} k pixels`);
}
// 2. the same result: Frame rate 30 -> 60 with Smooth motion, banded (browser) and in one go (local version)
ff('-f', 'lavfi', '-i', "color=c=black:s=1080x1920:r=30:d=2,geq=lum='128+90*sin((X+Y*0.5+300*T)/40)':cb='128+30*sin(Y/50+2*T)':cr=128", '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '14', 'p.mp4');
const R = defaultRecipe(); Object.assign(R.fps, { on: true, target: 60, engine: 'motion' });
const prof = { ...defaultProfile(), maxMBps: 0 };
const logs = []; const ex = engine.exec.bind(engine); engine.exec = async (a, o) => { logs.push(a.join(' ')); return ex(a, o); };
const web = { ...engine, kind: 'wasm', exec: engine.exec, info: engine.info };
await runRecipe(web, loops, 'p.mp4', 'banded.mp4', info('p.mp4'), R, prof, {}); const bandCmds = logs.filter(l => /crop=1080:\d+:0:\d+,minterpolate/.test(l)).length; logs.length = 0;
var local = { ...engine, kind: 'native', exec: engine.exec }; await runRecipe(local, loops, 'p.mp4', 'whole.mp4', info('p.mp4'), R, prof, {});
ok(logs.filter(l => /crop=1080:\d+:0:\d+,minterpolate/.test(l)).length === 0, 'the local version works on the whole picture in one go');
ok(bandCmds === bandPlan(1080, 1920).length, `the browser version works in ${bandCmds} bands`);
const a = info('banded.mp4'), b = info('whole.mp4');
ok(a.width === 1080 && a.height === 1920 && Math.abs(a.fps - 60) < 0.01 && Math.abs(a.duration - b.duration) < 0.02, `same size, 60 fps, same length (${a.width}x${a.height}, ${a.duration.toFixed(2)} s)`);
const out = (() => { try { return execFileSync('bash', ['-c', `ffmpeg -i "${join(d, 'banded.mp4')}" -i "${join(d, 'whole.mp4')}" -lavfi psnr -f null - 2>&1 | grep -o 'average:[0-9.inf]*'`]).toString(); } catch { return ''; } })();
const db = parseFloat((out.match(/average:([0-9.]+)/) || [])[1]); ok(db >= 38 && db < 99, `the picture is practically the same as in one go (PSNR ${out.trim()} dB; above 38 dB the difference cannot be seen)`);
// 2b. slow motion with Smooth motion, and a clip that steps (12 fps shown at 30, so frames repeat and are dropped first)
{
  const S = defaultRecipe(); Object.assign(S.slow, { on: true, factor: 2, engine: 'motion' });
  logs.length = 0; await runRecipe(web, loops, 'p.mp4', 'sb.mp4', info('p.mp4'), S, prof, {}); const nb = logs.filter(l => /crop=1080:\d+:0:\d+,minterpolate/.test(l)).length;
  await runRecipe(local, loops, 'p.mp4', 'sw.mp4', info('p.mp4'), S, prof, {});
  const x = info('sb.mp4'), y = info('sw.mp4'); ok(nb > 1 && Math.abs(x.duration - y.duration) < 0.05 && Math.abs(x.fps - y.fps) < 0.01 && frames('sb.mp4', 16, 9).length === frames('sw.mp4', 16, 9).length, `slow motion in ${nb} bands: ${x.duration.toFixed(2)} s, as in one go (${y.duration.toFixed(2)} s)`);
  ff('-f', 'lavfi', '-i', "color=c=black:s=1080x1920:r=12:d=2,geq=lum='128+90*sin((X+Y*0.5+300*T)/40)':cb=128:cr=128", '-vf', 'fps=30', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '14', 'st.mp4');
  logs.length = 0; await runRecipe(web, loops, 'st.mp4', 'tb.mp4', info('st.mp4'), R, prof, {}); const dd = logs.filter(l => /-vf mpdecimate /.test(l)).length;
  await runRecipe(local, loops, 'st.mp4', 'tw.mp4', info('st.mp4'), R, prof, {});
  const fb = info('tb.mp4'), fw = info('tw.mp4'); ok(dd === 1 && Math.abs(fb.duration - fw.duration) < 0.05 && frames('tb.mp4', 16, 9).length === frames('tw.mp4', 16, 9).length, `repeated frames are dropped once for all bands: ${frames('tb.mp4', 16, 9).length} frames, as in one go (${frames('tw.mp4', 16, 9).length})`);
}
// 2c. the local version (Linux): the bands run side by side, one per core. Faster, and the same picture as in one go.
{
  const { spawn } = await import('node:child_process'); const os = await import('node:os');
  const run = args => new Promise(res => { const p = spawn('ffmpeg', ['-nostdin', ...args], { cwd: d }); let e = ''; p.stderr.on('data', c => { e += c; }); p.on('close', code => res({ code, log: e.split(/\r?\n/) })); });
  const cores = Math.min(8, os.cpus().length);
  const mk = n => ({ ...engine, kind: 'native', info: { cores: n }, exec: async (a) => { logs.push(a.join(' ')); return run(a); } });
  logs.length = 0; let t = Date.now(); await runRecipe(mk(1), loops, 'p.mp4', 'one.mp4', info('p.mp4'), R, prof, {}); const t1 = (Date.now() - t) / 1000;
  ok(logs.filter(l => /crop=1080:\d+:0:\d+,minterpolate/.test(l)).length === 0, `one core: in one go (${t1.toFixed(1)} s)`);
  logs.length = 0; t = Date.now(); await runRecipe(mk(cores), loops, 'p.mp4', 'many.mp4', info('p.mp4'), R, prof, {}); const tn = (Date.now() - t) / 1000;
  const nb = logs.filter(l => /crop=1080:\d+:0:\d+,minterpolate/.test(l)).length;
  ok(cores < 2 || (nb === Math.min(cores, 12) && tn < t1 * 0.75), `${cores} cores: ${nb} bands side by side, ${tn.toFixed(1)} s instead of ${t1.toFixed(1)} s (${(t1 / tn).toFixed(1)}x faster)`);
  const out = (() => { try { return execFileSync('bash', ['-c', `ffmpeg -i "${join(d, 'many.mp4')}" -i "${join(d, 'one.mp4')}" -lavfi psnr -f null - 2>&1 | grep -o 'average:[0-9.inf]*'`]).toString(); } catch { return ''; } })();
  const db = parseFloat((out.match(/average:([0-9.]+)/) || [])[1]); ok(db >= 38, `the same picture as in one go (PSNR ${db} dB)`);
  const a = info('many.mp4'), b = info('one.mp4'); ok(Math.abs(a.duration - b.duration) < 0.02 && Math.abs(a.fps - 60) < 0.01, 'same length and 60 fps');
}
// 3. memory: one band pass against the whole picture (the peak of the ffmpeg process)
const peak = args => new Promise(res => { const p = spawn('ffmpeg', ['-v', 'error', '-y', '-threads', '1', ...args], { cwd: d }); let m = 0; const t = setInterval(() => { try { const s = execFileSync('cat', [`/proc/${p.pid}/status`]).toString(); const x = /VmHWM:\s+(\d+)/.exec(s); if (x) m = +x[1]; } catch {} }, 40); p.on('exit', () => { clearInterval(t); res(m / 1024); }); });
const mi = 'minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1', bp = bandPlan(1080, 1920)[1];
const whole = await peak(['-i', 'p.mp4', '-t', '0.4', '-vf', mi, '-c:v', 'libx264', '-preset', 'veryfast', '-threads', '1', 'm1.mp4']);
const band = await peak(['-i', 'p.mp4', '-t', '0.4', '-vf', `crop=1080:${bp.ch}:0:${bp.y0},${mi}`, '-c:v', 'libx264', '-preset', 'veryfast', '-threads', '1', 'm2.mp4']);
ok(band < whole * 0.55, `memory: ${Math.round(band)} MB for a band, ${Math.round(whole)} MB for the whole 1080x1920 picture`);
console.log(bad ? 'FAILED' : 'ALL OK'); process.exit(bad ? 1 : 0);
