// How Make it loop chooses (loops.js planLoop): already loops -> as is; a clean join -> the LONGEST clean trim; no clean join but a good
// blend -> crossfade with the best place and length; nothing good -> back and forth with gentle turns. Synthetic grey pictures.
import { planLoop, loopForecast, analyzeWithPlan, turnFrames } from './docs/tools/app/loops.js';
let bad = 0; const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) bad++; };
const S = 2304, mk = (n, f) => { const d = new Uint8Array(n * S); for (let i = 0; i < n; i++) for (let y = 0; y < 36; y++) for (let x = 0; x < 64; x++) d[i * S + y * 64 + x] = Math.max(0, Math.min(255, f(i, x, y))); return d; };
const pat = (ph, x, y) => 128 + 90 * Math.sin(2 * Math.PI * (x / 32 + ph)) * Math.cos(2 * Math.PI * (y / 18 + ph));
const fps = 30, n = 150, P = (d, o = {}) => planLoop(d, n, fps, { fadeAuto: true, ...o });
let p = P(mk(n, (i, x, y) => pat(i / n, x, y))); ok(p.method === 'asis', `a clip that loops is kept as it is (${p.method})`);
p = P(mk(n, (i, x, y) => pat(i / (0.85 * n), x, y))); ok(p.method === 'trim' && Math.abs(p.cut - 128) <= 1, `a clean point at 85 %: trimmed there (${p.method}, ${p.cut} frames)`);
p = P(mk(n, (i, x, y) => pat(i / (0.5 * (n - 3)), x, y))); ok(p.method === 'trim' && p.cut >= 145, `clean points at half and near the end: the LONGER loop is kept (${p.cut} of ${n} frames)`);
p = P(mk(n, (i, x, y) => pat(i / (0.85 * n), x, y) * 0.6 + i * 0.6)); ok(p.method === 'crossfade' && p.len >= 0.6 * n && p.ghost < 1, `brightness drifts, so no clean cut: crossfade with little ghosting (${p.method}, ${(p.xf / fps).toFixed(1)} s blend, ${p.len} frames, ghost ${p.ghost && p.ghost.toFixed(2)})`);
p = P(mk(n, (i, x, y) => 128 + 100 * Math.sin((x * x / 90 + i * 0.9) / 7) * Math.sin(y / 5 + i * 0.013 * (1 + x / 64))));
ok(p.method === 'pingpong' && p.E === Math.round(1.2 * fps), `nothing repeats: back and forth, with gentle 1.2 s turns (${p.method}, ${p.E} frames)`);
p = P(mk(n, (i, x, y) => pat(i / n, x, y)), { mode: 'pingpong', turn: 'quick' }); ok(p.method === 'pingpong' && p.E === Math.round(0.6 * fps) && p.len < P(mk(n, (i, x, y) => pat(i / n, x, y)), { mode: 'pingpong' }).len, `quick turns: 0.6 s, a shorter result (${p.E} frames)`);
p = P(mk(n, (i, x, y) => pat(i / (0.8 * n) + 0.06 * Math.sin(i / n * 2 * Math.PI * 1.3), x, y)), { mode: 'crossfade', fadeAuto: false, fade: 1 });
ok(p.method === 'crossfade' && p.xf === 30, `crossfade by hand: the length asked for (${p.xf} frames), at the best place`);
const r = analyzeWithPlan(mk(n, (i, x, y) => pat(i / (0.85 * n), x, y)), n, fps), f = loopForecast(r, { mode: 'auto' }, 5);
ok(r.plan && r.plan.method === 'trim' && Math.abs(f.len - 5 * 128 / 150) < 0.05, `the time estimate knows what Auto will do (${f.method}, ${f.len.toFixed(2)} s of 5)`);
const big = 600, t0 = performance.now(); planLoop(mk(big, (i, x, y) => pat(i / (0.8 * big) + 0.06 * Math.sin(i / big * 2 * Math.PI * 1.3), x, y)), big, 60, { fadeAuto: true });
ok(performance.now() - t0 < 3000, `10 s at 60 fps is planned quickly (${Math.round(performance.now() - t0)} ms)`);
ok(turnFrames(30, 30) === 9, 'a very short clip: the turns are at most a third of it');
console.log(bad ? `\n${bad} FAILED` : '\nALL OK'); process.exit(bad ? 1 : 0);
