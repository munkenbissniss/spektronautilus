// Loop Hospital: "Bring it to life" (slow in and out, breathing, floating, glow). Real ffmpeg, node's own test runner.
import test from 'node:test'; import assert from 'node:assert'; import { execFileSync, spawnSync } from 'node:child_process'; import { mkdtempSync, readFileSync } from 'node:fs'; import { tmpdir } from 'node:os'; import { join } from 'node:path';
import { defaultRecipe, runRecipe, planRecipe, lifePeriod, LIFE_STYLES, diagnose, mergeRecipe } from './docs/tools/app/steps.js';
import { defaultProfile } from './docs/tools/app/core.js';
const d = mkdtempSync(join(tmpdir(), 'life_')), ff = (...a) => execFileSync('ffmpeg', ['-v', 'error', '-y', '-nostdin', ...a]);
// a loop that really loops (period 4 s), bright everywhere so black borders would show; and a completely still picture
ff('-f', 'lavfi', '-i', 'color=c=black:s=640x360:r=25:d=4,geq=lum=\'150+80*sin(2*PI*(X/160+T/4))\':cb=\'128+50*sin(2*PI*(Y/90+T/4))\':cr=128', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', join(d, 'loop.mp4'));
ff('-f', 'lavfi', '-i', 'color=c=black:s=640x360:r=25:d=3,geq=lum=\'140+90*sin(X/50)*sin(Y/40)\':cb=128:cr=128', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', join(d, 'still.mp4'));
const probe = f => { const j = JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'stream=width,height,codec_name,nb_frames:format=duration', '-of', 'json', f])); return { w: j.streams[0].width, h: j.streams[0].height, dur: +j.format.duration, codec: j.streams[0].codec_name }; };
const engine = { async exec(args) { const r = spawnSync('ffmpeg', ['-nostdin', ...args], { cwd: d }); return { code: r.status, log: r.stderr.toString().split(/\r?\n/) }; }, async remove() {} };
const info = f => ({ ...probe(f), width: probe(f).w, height: probe(f).h, duration: probe(f).dur, fps: 25, hasAudio: false });
const treat = async (src, out, mod) => { const R = defaultRecipe(); mod(R); const i = info(join(d, src)); const r = await runRecipe(engine, {}, join(d, src), join(d, out), i, R, defaultProfile()); return { r, p: probe(join(d, out)) }; };
const frame = (f, n) => execFileSync('ffmpeg', ['-v', 'error', '-nostdin', '-i', join(d, f), '-vf', `select=eq(n\\,${n}),format=gray`, '-frames:v', '1', '-f', 'rawvideo', '-'], { maxBuffer: 1e8 });
const diff = (a, b) => { let s = 0; for (let i = 0; i < a.length; i++) s += Math.abs(a[i] - b[i]); return s / a.length; };

test('breath length is a whole number of loop lengths that fits into the final length', () => {
  assert.deepEqual([lifePeriod(4, 16, false).P, lifePeriod(4, 16, false).T], [8, 16]);
  assert.equal(lifePeriod(5, 16, false).P, 10); assert.equal(lifePeriod(20, 16, false).P, 20);
  assert.equal(lifePeriod(4, 16, true).P, 4, 'when something repeats the clip afterwards the breath must fit one loop');
  assert.equal(lifePeriod(0, 16, false).T, 0);
});
test('every style makes a 16 s mp4 of the same size', async () => {
  for (const st of Object.keys(LIFE_STYLES)) {
    const { p } = await treat('loop.mp4', `o_${st}.mp4`, R => { R.life = { on: true, style: st, ...LIFE_STYLES[st], minSeconds: 16 }; });
    assert.ok(Math.abs(p.dur - 16) < 0.1, `${st}: ${p.dur}`); assert.deepEqual([p.w, p.h, p.codec], [640, 360, 'h264'], st);
  }
});
test('the result still loops: the jump from the last frame to the first is as small as between any two frames', async () => {
  const f = 'o_float.mp4', n = 400, first = frame(f, 0), last = frame(f, n - 1), mid = [frame(f, 150), frame(f, 151)];
  const seam = diff(last, first), typical = diff(mid[0], mid[1]);
  assert.ok(seam <= typical * 2.5 + 0.5, `seam ${seam.toFixed(2)} vs normal step ${typical.toFixed(2)}`);
});
test('no black edges show while it floats and tilts', async () => {
  for (const n of [0, 60, 120, 180, 240, 300, 399]) { const g = frame('o_dream.mp4', n), W = 640, H = 360; for (const [x, y] of [[0, 0], [W - 1, 0], [0, H - 1], [W - 1, H - 1], [W / 2, 0], [0, H / 2]]) assert.ok(g[y * W + x] > 40, `frame ${n} at ${x},${y} is ${g[y * W + x]}`); }
});
test('a completely still picture comes alive', async () => {
  const { p } = await treat('still.mp4', 'o_still.mp4', R => { R.life = { on: true, style: 'calm', ...LIFE_STYLES.calm, minSeconds: 16 }; });
  assert.ok(Math.abs(p.dur - 15) < 0.1 || Math.abs(p.dur - 16.2) < 0.4 || p.dur >= 16, `length ${p.dur}`);
  assert.ok(diff(frame('o_still.mp4', 0), frame('o_still.mp4', 100)) > 1.5, 'the picture should move');
  const plain = await treat('still.mp4', 'o_plain.mp4', R => { R.out.minSeconds = 0; }); const pd = diff(frame('o_plain.mp4', 0), frame('o_plain.mp4', 50)), ld = diff(frame('o_still.mp4', 0), frame('o_still.mp4', 100)); assert.ok(ld > pd * 4 && ld > 1.5, `alive ${ld.toFixed(2)} vs plain ${pd.toFixed(2)}`);
});
test('slow in and out really changes the speed: the middle of the loop goes faster than the ends', async () => {
  const { p } = await treat('loop.mp4', 'o_ease.mp4', R => { R.life = { on: true, style: 'custom', ease: 100, breathe: 0, drift: 0, sway: 0, glow: 0, trails: false, minSeconds: 0 }; });
  assert.ok(Math.abs(p.dur - 4) < 0.1, `length stays ${p.dur}`);
  const ends = diff(frame('o_ease.mp4', 2), frame('o_ease.mp4', 5)), middle = diff(frame('o_ease.mp4', 48), frame('o_ease.mp4', 51));
  assert.ok(middle > ends * 1.5, `middle ${middle.toFixed(2)} vs ends ${ends.toFixed(2)}`);
});
test('Repeat-until-at-least now works without the loop step (it used to be ignored in the Hospital)', async () => {
  const { p } = await treat('loop.mp4', 'o_rep.mp4', R => { R.out.minSeconds = 16; }); assert.ok(Math.abs(p.dur - 16) < 0.1, `${p.dur}`);
});
test('a short clip gets the suggestion, and adding it turns the step on with 16 s', () => {
  const dg = diagnose({ width: 1280, height: 720, duration: 4, fps: 25 }, null), s = dg.find(x => x.id === 'still'); assert.ok(s, 'suggestion present');
  const R = mergeRecipe(defaultRecipe(), s.fix); assert.ok(R.life.on && R.life.minSeconds === 16 && R.life.breathe > 0);
  assert.ok(!diagnose({ width: 1280, height: 720, duration: 30, fps: 25 }, null).find(x => x.id === 'still'), 'no suggestion for long clips');
});
test('with the loop step on, the breath fits one loop (the loop step repeats it afterwards)', () => {
  const R = defaultRecipe(); R.life = { on: true, style: 'calm', ...LIFE_STYLES.calm, minSeconds: 16 }; R.loop.on = true;
  const p = planRecipe({ width: 640, height: 360, duration: 4, fps: 25 }, R, defaultProfile()); assert.match(p.extra, /on\/100\b|on\/100\)/);   // 4 s * 25 fps = 100 frames per breath
});
