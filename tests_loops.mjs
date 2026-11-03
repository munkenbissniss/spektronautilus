// Organic loops: the "back and forth" loop keeps its tempo, eases only at the turnarounds, and has no jump at the seam.
import { engine, ff, frames, mad, info } from './tests_loops_harness.mjs';
import { makeLoop } from './docs/tools/app/loops.js';
import { defaultProfile } from './docs/tools/app/core.js';
let bad = 0; const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) bad++; };
ff('-f', 'lavfi', '-i', `color=c=black:s=640x360:r=30:d=4,geq=lum='128+100*sin((X+120*T)/23)*sin(Y/31+X/97)':cb=128:cr=128`, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', 'c30.mp4');
const prof = { ...defaultProfile(), size: '640x360', maxMBps: 0 };
const r = await makeLoop(engine, 'c30.mp4', 'pp.mp4', prof, info('c30.mp4'), { mode: 'pingpong' });
const F = frames('pp.mp4'), s = []; for (let i = 1; i < F.length; i++) s.push(mad(F[i - 1], F[i]));
const mid = s.slice(Math.floor(s.length * .2), Math.floor(s.length * .32)), m = mid.reduce((a, b) => a + b, 0) / mid.length;
ok(r.method === 'pingpong' && F.length > 230, `pingpong made (${F.length} frames)`);
ok(Math.max(...mid) < m * 1.15 && Math.min(...mid) > m * .85, 'tempo is constant in the middle of the movement');
ok(Math.max(...s.slice(0, 4)) < m * .4, 'eases in at the start (no instant start)');
const turn = Math.round(F.length / 2); const around = s.slice(turn - 3, turn + 3);
ok(Math.max(...around) < m * .4, 'eases to a stop at the turnaround');
ok(mad(F[F.length - 1], F[0]) < m * .4, 'no jump where the loop starts over');
ok(s.every(x => x < m * 1.3), 'no spikes anywhere');
console.log(bad ? 'FAILED' : 'ALL OK'); process.exit(bad ? 1 : 0);
