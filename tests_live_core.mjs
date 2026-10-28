import test from 'node:test'; import assert from 'node:assert/strict';
import * as C from './docs/live-dj/core.js';
test('audio gains: power keeps loudness, ends are exact', () => {
  assert.deepEqual(C.audioGains(0), { a: 1, b: 0 });
  const g = C.audioGains(1); assert.ok(Math.abs(g.a) < 1e-9 && g.b === 1);
  const m = C.audioGains(.5); assert.ok(Math.abs(m.a ** 2 + m.b ** 2 - 1) < 1e-9);
  assert.deepEqual(C.audioGains(.25, 'linear'), { a: .75, b: .25 });
  assert.deepEqual(C.audioGains(5), { a: 6.123233995736766e-17, b: 1 });
});
test('auto fade reaches the target and eases', () => {
  assert.equal(C.autoFadePos(0, 1, 0, 4000), 0); assert.equal(C.autoFadePos(0, 1, 4000, 4000), 1);
  assert.equal(C.autoFadePos(1, 0, 9999, 4000), 0);
  const q = C.autoFadePos(0, 1, 1000, 4000); assert.ok(q > 0 && q < .25);   // eased start
  assert.equal(C.autoFadePos(0, 1, 1, 0), 1);
});
test('poster frames', () => {
  assert.equal(C.posterFrame(-1).phase, 'off'); assert.equal(C.posterFrame(0).p, 0);
  assert.equal(C.posterFrame(700).phase, 'hold'); assert.equal(C.posterFrame(3000).p, 1);
  const o = C.posterFrame(700 + 6000 + 300); assert.equal(o.phase, 'out'); assert.ok(o.p > 0 && o.p < 1);
  assert.equal(C.posterFrame(1e6).phase, 'off');
  assert.equal(C.posterFrame(1e6, 700, Infinity).phase, 'hold');
});
test('titles from file names', () => {
  assert.deepEqual(C.parseTitle('Daft Punk - One More Time.mp4'), { artist: 'Daft Punk', title: 'One More Time' });
  assert.deepEqual(C.parseTitle('03 - Röyksopp - Remind Me.mov'), { artist: 'Röyksopp', title: 'Remind Me' });
  assert.deepEqual(C.parseTitle('just_a_name.webm'), { artist: '', title: 'just a name' });
  assert.deepEqual(C.parseTitle('A - B - C.mp4'), { artist: 'A', title: 'B - C' });
});
test('time format', () => { assert.equal(C.fmtTime(75.9), '1:15'); assert.equal(C.fmtTime(NaN), '0:00'); assert.equal(C.fmtTime(3600), '60:00'); });
test('midi parsing and routing', () => {
  assert.deepEqual(C.parseMidi([0xb0, 7, 127]), { type: 'cc', ch: 0, num: 7, val: 1 });
  assert.equal(C.parseMidi([0x90, 60, 0]).type, 'noteoff');
  assert.equal(C.parseMidi([0xf8]), null);
  const map = { 'cc:0:7': 'xfade', 'note:9:36': 'mix', 'cc:0:20': 'playA' };
  assert.deepEqual(C.routeMidi(C.parseMidi([0xb0, 7, 64]), map), { action: 'xfade', value: 64 / 127 });
  assert.equal(C.routeMidi(C.parseMidi([0x99, 36, 100]), map).action, 'mix');
  assert.equal(C.routeMidi(C.parseMidi([0x89, 36, 0]), map), null);             // note off ignored
  assert.equal(C.routeMidi(C.parseMidi([0x90, 7, 90]), map), null);             // fader needs cc
  assert.equal(C.routeMidi(C.parseMidi([0xb0, 20, 0]), map), null);             // button released
  assert.equal(C.routeMidi(C.parseMidi([0xb0, 20, 127]), map).action, 'playA');
  assert.equal(C.routeMidi(C.parseMidi([0xb0, 99, 5]), map), null);
});
