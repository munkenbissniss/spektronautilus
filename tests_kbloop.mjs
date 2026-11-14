// "Make it loop" together with Ken Burns or Bring it to life: the result reaches the length they ask for (24 / 16 s).
// And the forecast of what the loop step will do, used by the time estimate. Real ffmpeg.
import { engine, ff, info } from './tests_loops_harness.mjs';
import * as loops from './docs/tools/app/loops.js';
import { defaultRecipe, runRecipe } from './docs/tools/app/steps.js';
import { defaultProfile } from './docs/tools/app/core.js';
let bad = 0; const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) bad++; };
const prof = { ...defaultProfile(), maxMBps: 0 };
ff('-f', 'lavfi', '-i', 'testsrc2=size=320x180:rate=25:duration=3', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', 'k.mp4');
for (const [what, set, min] of [['Ken Burns', R => { R.kb.on = true; R.kb.minSeconds = 24; }, 24], ['Bring it to life', R => { R.life.on = true; R.life.minSeconds = 16; }, 16]]) {
  const R = defaultRecipe(); set(R); R.loop.on = true; R.loop.mode = 'pingpong';
  await runRecipe(engine, loops, 'k.mp4', 'o.mp4', info('k.mp4'), R, prof, {}); const d = info('o.mp4').duration;
  ok(d >= min - 0.1 && d < min + 6.5, `${what} + Make it loop: ${d.toFixed(1)} s (asks for at least ${min} s)`);
}
const F = loops.loopForecast;
ok(F({ isLoop: true }, { mode: 'auto' }, 5).method === 'asis' && F({ isLoop: true }, { mode: 'auto' }, 5).len === 5, 'a clip that loops is kept as it is');
ok(F({ isLoop: false, bestCut: -1 }, { mode: 'auto', fallback: 'pingpong' }, 5).len === 10, 'no good loop point: forward and backward, twice as long');
ok(F({ isLoop: false, bestCut: 80, bestRatio: 1.1, bestKeeps: 0.8 }, { mode: 'auto' }, 5).method === 'trim', 'a good loop point: trimmed');
ok(Math.abs(F(null, { mode: 'crossfade', fade: 1.5 }, 5).len - 3.5) < 1e-9, 'crossfade: shorter by the fade');
ok(F(null, { mode: 'none' }, 5).method === 'asis', 'no report: still a sensible answer');
console.log(bad ? 'FAILED' : 'ALL OK'); process.exit(bad ? 1 : 0);
