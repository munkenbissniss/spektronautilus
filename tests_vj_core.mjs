import test from 'node:test'; import assert from 'node:assert/strict';
import * as C from './docs/vj-pad/core.js';
import * as L from './docs/live-dj/core.js';
test('tap tempo', () => {
  assert.equal(C.tapBpm([0]), null);
  assert.equal(C.tapBpm([0, 500, 1000, 1500]), 120);
  assert.equal(C.tapBpm([0, 500, 1000, 1500, 9000, 9460, 9920, 10380]), 130.4);       // a pause starts a new count
  assert.equal(C.tapBpm([0, 1000, 2000]), 120);                                         // 60 folds up into range
  assert.equal(C.tapBpm([0, 250, 500, 750]), 120);                                      // 240 folds down
});
test('beat position and pulse', () => {
  assert.equal(C.beatPos(1000, 0, 500, 1), 0); assert.equal(C.beatPos(1250, 0, 500, 1), .5);
  assert.equal(C.beatPos(1750, 0, 500, 4), 3.5); assert.ok(C.beatPos(-100, 0, 500, 1) >= 0);
  assert.equal(C.pulse(0), 1); assert.equal(C.pulse(1), 0); assert.equal(C.pulse(1.5), 0); assert.ok(C.pulse(.5) < .3);
});
test('kick detector finds kicks, ignores a steady hum and does not double count', () => {
  const k = new C.KickDetector(); let kicks = 0;
  for (let t = 0; t < 4000; t += 16) { const phase = t % 500; const e = 0.08 + (phase < 60 ? 0.6 : 0); if (k.feed(e, t)) kicks++; }
  assert.ok(kicks >= 7 && kicks <= 8, 'kicks ' + kicks);
  const h = new C.KickDetector(); let n = 0; for (let t = 0; t < 4000; t += 16) if (h.feed(0.3, t)) n++; assert.ok(n <= 1, 'hum ' + n);
  const q = new C.KickDetector(); let m = 0; for (let t = 0; t < 2000; t += 16) if (q.feed(0.01, t)) m++; assert.equal(m, 0);
});
test('midi routing works with the VJ action list', () => {
  const map = { 'cc:0:1': 'op2', 'note:0:36': 'pad1', 'note:0:50': 'fx3' };
  assert.deepEqual(L.routeMidi(L.parseMidi([0xb0, 1, 127]), map, C.VJ_MIDI_ACTIONS), { action: 'op2', value: 1 });
  assert.equal(L.routeMidi(L.parseMidi([0x90, 36, 99]), map, C.VJ_MIDI_ACTIONS).action, 'pad1');
  assert.equal(L.routeMidi(L.parseMidi([0x90, 1, 99]), map, C.VJ_MIDI_ACTIONS), null);
  assert.equal(new Set(C.VJ_MIDI_ACTIONS.map(a => a.id)).size, C.VJ_MIDI_ACTIONS.length);
  assert.equal(C.PAD_CODES.length, C.PADS); assert.equal(C.FX_CODES.length, C.FX.length);
});
