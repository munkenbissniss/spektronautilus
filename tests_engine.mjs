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

// ---- a dead worker must not lock the page for ever (a phone that ran out of memory)
import { STALLED } from './docs/tools/app/engine.js';
test('a run that goes silent is given up on, and the engine restarts for the next call', async () => {
  let terminated = 0; const e = make({ exec: () => new Promise(() => {}), terminate() { terminated++; } }); e.stallMs = 60;
  await assert.rejects(e.exec(['x']), err => err.message === STALLED);
  assert.equal(terminated, 1); assert.equal(e.ff, null, 'the dead worker is dropped, so the next call loads a fresh one'); assert.equal(e.cur, null);
});
test('a run that keeps logging is not given up on', async () => {
  const e = make({ exec: () => new Promise(res => { let n = 0; const t = setInterval(() => { e.last = Date.now(); if (++n === 8) { clearInterval(t); res(0); } }, 20); }), terminate() {} }); e.stallMs = 100;
  const r = await e.exec(['x']); assert.equal(r.code, 0);
});
test('an idle worker that no longer answers is replaced before the next call', async () => {
  let t = 0; const e = make({ listDir: () => new Promise(() => {}), terminate() { t++; } }); e.pingMs = 40; e.last = Date.now() - 60000;
  assert.equal(await e.alive(), false);
  e.loading = null; e.ff = { listDir: async () => [], terminate() {} }; e.last = Date.now() - 60000; assert.equal(await e.alive(), true, 'a worker that answers is kept');
});
test('file operations have a time limit too', async () => {
  let t = 0; const e = make({ readFile: () => new Promise(() => {}), terminate() { t++; } }); e.opMs = 50;
  await assert.rejects(e.read('a.mp4'), err => err.message === STALLED); assert.equal(t, 1);
});
