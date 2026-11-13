// Loop Hospital aims at 16:9 and 60 fps: the suggestions, and Smooth motion as the default method for slow motion and frame rate.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { diagnose, defaultRecipe, mergeRecipe } from './docs/tools/app/steps.js';
const ids = i => diagnose({ duration: 20, ...i }, null).map(x => x.id);
test('portrait: turn it and crop it to 16:9, in one suggestion', () => {
  const d = diagnose({ width: 1080, height: 1920, fps: 30, duration: 20 }, null), p = d.find(x => x.id === 'portrait');
  assert.ok(p && p.fix.rotate.turn === '90' && p.fix.crop.shape === '169', JSON.stringify(p));
  assert.ok(!d.find(x => x.id === 'shape'), 'not also a separate crop suggestion');
  const R = mergeRecipe(defaultRecipe(), p.fix); assert.ok(R.rotate.on && R.crop.on && R.crop.shape === '169');
});
test('square, 4:3 and ultra-wide: crop to 16:9', () => {
  for (const [w, h] of [[2160, 2160], [1440, 1080], [2560, 1080]]) assert.ok(ids({ width: w, height: h, fps: 60 }).includes('shape'), `${w}x${h}`);
});
test('16:9 already (also odd sizes close to it): nothing about shape', () => {
  for (const [w, h] of [[1920, 1080], [1280, 720], [854, 480]]) { const i = ids({ width: w, height: h, fps: 60 }); assert.ok(!i.includes('shape') && !i.includes('portrait'), `${w}x${h}`); }
});
test('under 60 fps: Frame rate to 60 with Smooth motion; 60 fps: nothing', () => {
  const f = diagnose({ width: 1920, height: 1080, fps: 33.33, duration: 20 }, null).find(x => x.id === 'fps');
  assert.ok(f && f.fix.fps.target === 60 && f.fix.fps.engine === 'motion' && /33\.33 fps/.test(f.text));
  assert.ok(!ids({ width: 1920, height: 1080, fps: 59.94 }).includes('fps') && !ids({ width: 1920, height: 1080, fps: 60 }).includes('fps'));
});
test('the goal suggestions come first', () => {
  const d = diagnose({ width: 300, height: 600, fps: 12, duration: 2 }, null).map(x => x.id);
  assert.deepEqual(d.slice(0, 2), ['portrait', 'fps']);
});
test('Smooth motion is the default for slow motion and frame rate', () => {
  const R = defaultRecipe(); assert.equal(R.slow.engine, 'motion'); assert.equal(R.fps.engine, 'motion');
  const s = diagnose({ width: 1920, height: 1080, fps: 60, duration: 2 }, null).find(x => x.id === 'short'); assert.equal(s.fix.slow.engine, 'motion');
});
