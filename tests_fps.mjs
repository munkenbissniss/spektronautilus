// Loop Hospital: "Frame rate" (60 fps without stutter). Real ffmpeg; the AI path uses a stand-in for Video2X.
import { engine, ff, frames, mad, info, d } from './tests_loops_harness.mjs';
import { execFileSync } from 'node:child_process';
import * as loops from './docs/tools/app/loops.js';
import { defaultRecipe, runRecipe, fpsPlan } from './docs/tools/app/steps.js';
import { defaultProfile } from './docs/tools/app/core.js';
let bad = 0; const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) bad++; };
const prof = { ...defaultProfile(), maxMBps: 0 };
// a seamless loop at 24 fps (4 s), the same movement shot on "twos" (12 fps shown in a 30 fps file), and a clip that does not loop
const loopSrc = (fps, n) => `color=c=black:s=320x180:r=${fps}:d=4,geq=lum='128+100*sin((X+160.2212*N/${n})/25.5)*sin(Y/23+X/61)':cb=128:cr=128`;
ff('-f', 'lavfi', '-i', loopSrc(24, 96), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '10', 'a24.mp4');
ff('-f', 'lavfi', '-i', loopSrc(12, 48), '-vf', 'fps=30', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '10', 'b12in30.mp4');
ff('-f', 'lavfi', '-i', `color=c=black:s=320x180:r=25:d=4,geq=lum='60+120*X/320+40*sin(Y/20+N/6)':cb=128:cr=128`, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '10', 'ramp25.mp4');
ff('-f', 'lavfi', '-i', loopSrc(60, 240), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '10', 'a60.mp4');
ff('-i', 'a24.mp4', '-vf', 'fps=60', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '10', 'naive.mp4');
const st = f => { const F = frames(f, 96, 54), s = []; for (let i = 1; i < F.length; i++) s.push(mad(F[i - 1], F[i])); const m = s.reduce((a, b) => a + b, 0) / s.length; return { n: F.length, mean: m, cv: Math.sqrt(s.reduce((a, b) => a + (b - m) ** 2, 0) / s.length) / m, zeros: s.filter(x => x < m * 0.1).length, seam: mad(F[F.length - 1], F[0]) }; };
const treat = async (src, out, mod, eng = engine) => { const R = defaultRecipe(); R.fps.on = true; mod && mod(R); const r = await runRecipe(eng, loops, src, out, info(src), R, prof, {}); return { r, i: info(out) }; };

// 1. the plan: it finds loops and repeated frames
{
  const g = await loops.grayFrames(engine, 'a24.mp4', 24), p = fpsPlan(g.data, g.n, 24, {});
  ok(!p.skip && p.wrap && !p.dedupe && p.outFrames === 240, `a smooth loop: seam kept, nothing repeated, 240 frames out (${p.note})`);
  const g2 = await loops.grayFrames(engine, 'b12in30.mp4', 30), p2 = fpsPlan(g2.data, g2.n, 30, {});
  ok(p2.dedupe && p2.wrap, `repeated frames found (${Math.round(p2.repeated * 100)} % of steps), and still a loop`);
  const g3 = await loops.grayFrames(engine, 'ramp25.mp4', 25), p3 = fpsPlan(g3.data, g3.n, 25, {});
  ok(!p3.wrap, 'a clip that does not loop is not wrapped');
  ok(fpsPlan(g.data, g.n, 24, { loop: false }).wrap === false && fpsPlan(g2.data, g2.n, 30, { fix: false }).dedupe === false, 'the two advanced switches turn them off');
  ok(fpsPlan(g.data, g.n, 60, {}).skip === true, 'a 60 fps clip is left alone');
}
// 2. 24 fps loop -> 60: smooth, same length, no repeated frames, the loop seam is as small as an ordinary step
{
  const { r, i } = await treat('a24.mp4', 'o24.mp4'), a = st('o24.mp4'), n = st('naive.mp4');
  ok(Math.abs(i.fps - 60) < 0.01 && Math.abs(i.duration - 4) < 0.05 && a.n === 240, `60 fps, same length (${i.fps} fps, ${i.duration.toFixed(2)} s, ${a.n} frames)`);
  ok(n.cv > 0.8 && a.cv < 0.3 && a.zeros === 0, `no judder: speed variation ${a.cv.toFixed(2)} (plain frame doubling gives ${n.cv.toFixed(2)}, with ${n.zeros} repeated frames)`);
  ok(a.seam < a.mean * 2.2, `the loop seam is as small as an ordinary step (${a.seam.toFixed(2)} vs ${a.mean.toFixed(2)})`);
  ok(/24 → 60 fps/.test(r.note) && /seam/.test(r.note), `the result says what happened: ${r.note}`);
}
// 3. stepping (12 fps in a 30 fps file) is spread out
{
  const before = st('b12in30.mp4'), { i } = await treat('b12in30.mp4', 'ob.mp4'), a = st('ob.mp4');
  ok(a.cv < 0.35 && a.zeros === 0 && Math.abs(i.duration - 4) < 0.05, `stepping removed: variation ${before.cv.toFixed(2)} -> ${a.cv.toFixed(2)}, no repeated frames, same length`);
  const { i: i2 } = await treat('b12in30.mp4', 'ob2.mp4', R => { R.fps.fix = false; }), a2 = st('ob2.mp4');
  ok(a2.cv > a.cv * 1.5, `with "fix stepping" off the stepping stays (${a2.cv.toFixed(2)})`);
}
// 4. not a loop: the length is kept and nothing is wrapped
{
  const { i } = await treat('ramp25.mp4', 'oramp.mp4'); ok(Math.abs(i.fps - 60) < 0.01 && Math.abs(i.duration - 4) < 0.1, `non-loop: 60 fps, about 4 s (${i.duration.toFixed(2)} s)`);
}
// 5. smooth motion, 30 and 50 fps targets, already 60, and together with Cut
{
  ff('-i', 'a24.mp4', '-t', '1', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '10', 'a24s.mp4');
  const { i } = await treat('a24s.mp4', 'omo.mp4', R => { R.fps.engine = 'motion'; }); ok(Math.abs(i.fps - 60) < 0.01, 'smooth motion (motion interpolation) makes 60 fps');
  const { i: i50 } = await treat('a24.mp4', 'o50.mp4', R => { R.fps.target = 50; }); ok(Math.abs(i50.fps - 50) < 0.01 && Math.abs(i50.duration - 4) < 0.05, '50 fps target works');
  const { r, i: i60 } = await treat('a60.mp4', 'o60.mp4'); ok(Math.abs(i60.fps - 60) < 0.01 && /already 60/.test(r.note), `a clip that already is 60 fps is untouched (${r.note})`);
  const { i: ic } = await treat('a24.mp4', 'ocut.mp4', R => { R.cut = { on: true, start: 1, len: 2 }; }); ok(Math.abs(ic.fps - 60) < 0.01 && Math.abs(ic.duration - 2) < 0.1, `cut, then 60 fps (${ic.duration.toFixed(2)} s)`);
}
// 6. AI (RIFE through a stand-in for Video2X): whole-number multiples, then a blend lands on 60; the loop keeps its length and seam
{
  const calls = [], inFrames = [];
  const aiEng = { ...engine, kind: 'native', info: { v2x: { ok: true, mul: '-m', dev: '-g' } }, async v2xGpus() { return { ok: true, lines: ['0. Fake GPU (Vulkan)'] }; },
    async v2x(args, opts) { calls.push(args.join(' ')); const g = k => args[args.indexOf(k) + 1], m = +g('-m'), fr = execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'csv=p=0', d + '/' + g('-i')]).toString().trim().split('/'), fps = +fr[0] / (+fr[1] || 1);
      inFrames.push(+execFileSync('ffprobe', ['-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', d + '/' + g('-i')]).toString().trim()); opts && opts.onProgress && opts.onProgress(1); return engine.exec(['-y', '-i', g('-i'), '-vf', `framerate=fps=${fps * m}:interp_start=0:interp_end=255:scene=100`, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', g('-o')]); } };
  const { r, i } = await treat('a24.mp4', 'oai.mp4', R => { R.fps.engine = 'ai'; }, aiEng), a = st('oai.mp4');
  ok(inFrames[0] === 97, `the clip handed to the AI is the loop plus its first frame (${inFrames[0]} frames)`);
  ok(calls.length === 1 && /-p rife/.test(calls[0]) && /-m 3\b/.test(calls[0]), `RIFE asked for 3x (24 -> 72 fps): ${calls[0] && calls[0].slice(0, 80)}`);
  ok(Math.abs(i.fps - 60) < 0.01 && a.n === 240 && Math.abs(i.duration - 4) < 0.05, `then exactly 60 fps and the same length (${a.n} frames, ${i.duration.toFixed(2)} s)`);
  ok(a.cv < 0.3 && a.seam < a.mean * 2.2, `smooth, and the loop seam is kept (variation ${a.cv.toFixed(2)}, seam ${a.seam.toFixed(2)} vs ${a.mean.toFixed(2)})`);
  ok(/AI 24 → 60 fps/.test(r.note), `the note says AI: ${r.note}`);
  calls.length = 0; const { i: i30 } = await treat('b12in30.mp4', 'oai30.mp4', R => { R.fps.engine = 'ai'; }, aiEng);
  ok(calls.length === 1 && /-m 2\b/.test(calls[0]) && Math.abs(i30.fps - 60) < 0.01, '30 fps -> RIFE 2x -> 60 fps exactly');
  let msg = ''; try { await treat('a24.mp4', 'oai2.mp4', R => { R.fps.engine = 'ai'; }, engine); } catch (e) { msg = e.message; }
  ok(/AI needs the Linux/.test(msg), 'AI without Video2X gives a clear message instead of failing');
}
console.log(bad ? 'FAILED' : 'ALL OK'); process.exit(bad ? 1 : 0);
