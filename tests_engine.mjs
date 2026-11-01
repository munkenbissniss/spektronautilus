// WasmEngine: pressing Stop (terminate) while ffmpeg runs must not throw "null is not an object".
import test from 'node:test';
import assert from 'node:assert/strict';
import { WasmEngine } from './docs/tools/app/engine.js';

const make = ff => { const e = new WasmEngine(); e.ff = ff; return e; };

test('normal run returns code and log', async () => {
  const e = make({ exec: async () => { e.cur.log.push('hello'); return 0; } });
  const r = await e.exec(['-version']);
  assert.deepEqual(r, { code: 0, log: ['hello'] });
  assert.equal(e.cur, null);
});

test('Stop during a run does not throw a TypeError', async () => {
  let release;
  const e = make({ exec: () => new Promise(res => { release = res; }), terminate() {} });
  const p = e.exec(['x']);
  await new Promise(r => setTimeout(r, 5));
  e.terminate();
  release(1);
  const r = await p;
  assert.equal(r.code, 1);
  assert.equal(e.cur, null);
});

test('Stop where the worker rejects the pending run', async () => {
  let rej;
  const e = make({ exec: () => new Promise((_, r) => { rej = r; }), terminate() {} });
  const p = e.exec(['x']);
  await new Promise(r => setTimeout(r, 5));
  e.terminate();
  rej(new Error('called FFmpeg.terminate()'));
  await assert.rejects(p, err => !/null is not|Cannot read/.test(err.message));
  assert.equal(e.cur, null);
});
