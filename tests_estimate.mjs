// The planned time estimate: fitting the trial runs, and how the plan and the live speed are combined.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fitCost, leftFrom } from './docs/shared/progress.js';
test('two trial runs separate the start-up cost from the cost per second', () => {
  const { a, b } = fitCost({ t: 3 + 0.5 * 2, o: 0.5 }, { t: 3 + 1.5 * 2, o: 1.5 });   // 3 s start-up, 2 s per second of result
  assert.ok(Math.abs(a - 3) < 1e-9 && Math.abs(b - 2) < 1e-9);
  assert.ok(Math.abs(a + b * 16 - 35) < 1e-9, 'a 16 s result: 35 s');
});
test('one trial run: everything counted as cost per second (rather too high than too low)', () => {
  const { a, b } = fitCost({ t: 30, o: 0.5 }); assert.equal(a, 0); assert.equal(b, 60);
});
test('noise never gives a negative start-up cost or a negative speed', () => {
  const r = fitCost({ t: 2, o: 0.5 }, { t: 1.9, o: 1.5 }); assert.ok(r.a >= 0 && r.b > 0);
});
test('the plan counts, not the bar', () => {
  // the bar raced to 40 % in 10 s (cheap steps), but the plan says 100 s
  assert.equal(leftFrom(100, 10, 0.4), 90);
  assert.ok(leftFrom(0, 10, 0.4) < 20, 'without a plan the guess would be 15 s');
  assert.equal(leftFrom(100, 90, 0.1), 10, 'a bar that lags behind does not blow the estimate up');
});
test('late and clearly slower than planned: a light correction', () => {
  const r = leftFrom(100, 80, 0.6); assert.ok(r > 20 && r < 53.4, String(r));
});
test('past the plan: nothing is claimed (the page says "a little longer than estimated")', () => {
  assert.equal(leftFrom(100, 120, 0.8), null); assert.equal(leftFrom(100, 99, 0.1), null);
});
test('no plan: the old guess from the bar; no progress: nothing', () => { assert.equal(leftFrom(0, 10, 0.5), 10); assert.equal(leftFrom(0, 5, 0), null); });
