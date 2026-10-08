import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';

const base = new URL(process.env.REEF_TARGET || 'http://127.0.0.1:4173/preview/independent-scan/');
if (base.origin !== 'http://127.0.0.1:4173' || !base.pathname.endsWith('/')) throw Error('Isolated hosted preview required');
const here = path.dirname(fileURLToPath(import.meta.url));
const manifest = JSON.parse(await fs.readFile(path.join(here, 'seagrass-runtime-hashes.json'), 'utf8'));
const out = path.resolve('render-evidence');
await fs.mkdir(out, { recursive: true });
const started = Date.now(), key = 'azure-reef:exhibit-return:v2';
const report = { mode: 'mobile-recovery-native-v2', acceptedCommit: manifest.acceptedCommit, checkoutCommit: process.env.GITHUB_SHA || null, target: base.href, passed: false, contexts: [], limitations: ['Hosted 390x740 mouse/keyboard input, not physical-device touch or GPU acceptance.', 'Only one exact main-model request is intentionally interrupted; timeout/corrupt-storage cases are not covered.'] };
const assert = (condition, message) => { if (!condition) throw Error(message); };
const equal = (a, b) => ['camera', 'target'].every(k => a[k].every((v, i) => Math.abs(v - b[k][i]) < 1e-5));
const save = async () => { report.elapsedMs = Date.now() - started; await fs.writeFile(path.join(out, 'mobile-recovery.json'), JSON.stringify(report, null, 2) + '\n'); };
let browser;
const deadline = setTimeout(async () => {
  report.deadline = '320-second overall deadline';
  for (const motion of ['no-preference', 'reduce']) {
    let c = report.contexts.find(x => x.motion === motion);
    if (!c) { c = { motion, checkpoints: [] }; report.contexts.push(c); }
    if (!['passed', 'failed'].includes(c.outcome)) c.outcome = 'incomplete-overall-budget';
  }
  await save(); console.log('MOBILE_RECOVERY_SUMMARY ' + JSON.stringify(report)); process.exit(2);
}, 320000);

// Observation only: no focus, scrolling, click dispatch, or application calls.
function observation(selector) {
  const e = document.querySelector(selector), card = document.querySelector('#guideCard');
  const identify = n => n ? { tag: n.tagName, id: n.id, className: String(n.className), text: n.textContent?.slice(0, 80) } : null;
  const rect = n => { const r = n.getBoundingClientRect(); return { left: r.left, right: r.right, top: r.top, bottom: r.bottom, width: r.width, height: r.height }; };
  if (!e) return { selector, exists: false };
  const r = rect(e), s = getComputedStyle(e), x = (r.left + r.right) / 2, y = (r.top + r.bottom) / 2;
  const hit = document.elementFromPoint(x, y), containers = [];
  for (let n = e.parentElement; n; n = n.parentElement) {
    const cs = getComputedStyle(n);
    if (/(auto|scroll|hidden|clip)/.test(cs.overflow + cs.overflowY)) containers.push({ ...identify(n), rect: rect(n), overflow: cs.overflow, scrollTop: n.scrollTop, scrollHeight: n.scrollHeight, clientHeight: n.clientHeight });
  }
  return { selector, exists: true, rect: r, x, y, disabled: !!e.disabled, hidden: e.hidden, display: s.display, visibility: s.visibility, opacity: s.opacity, pointerEvents: s.pointerEvents, hit: identify(hit), hitMatches: hit === e || e.contains(hit), hitStack: document.elementsFromPoint(x, y).map(identify), containers, card: card ? { rect: rect(card), scrollTop: card.scrollTop, scrollHeight: card.scrollHeight, clientHeight: card.clientHeight } : null, overlays: ['loading', 'unsupported', 'help'].map(id => { const n = document.getElementById(id); return n ? { id, hidden: n.hidden, display: getComputedStyle(n).display } : null; }), viewport: { width: innerWidth, height: innerHeight } };
}

try {
  browser = await chromium.launch({ channel: 'chromium', headless: true, chromiumSandbox: true, timeout: 30000, args: ['--enable-automation'], ignoreDefaultArgs: ['--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--ignore-gpu-blocklist'] });
  const cdp = await browser.newBrowserCDPSession();
  report.forbiddenFlags = (await cdp.send('Browser.getBrowserCommandLine')).arguments.filter(x => ['--no-sandbox', '--disable-gpu-sandbox', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'].includes(x));
  assert(!report.forbiddenFlags.length, 'Unsafe browser flag');
  for (const motion of ['no-preference', 'reduce']) {
    const c = { motion, outcome: 'running', checkpoints: [], interactions: [], events: [], errors: [], expectedNetworkFailures: [] };
    report.contexts.push(c); await save();
    let context, page, action = null, blocking = false, timedOut = false, caseTimer;
    const caseEnd = Math.min(Date.now() + 150000, started + 315000);
    try {
      assert(caseEnd > Date.now(), 'No reserved context budget remaining');
      context = await browser.newContext({ viewport: { width: 390, height: 740 }, deviceScaleFactor: 1, reducedMotion: motion });
      caseTimer = setTimeout(() => { timedOut = true; void context.close(); }, caseEnd - Date.now());
      await context.exposeBinding('__recordRecoveryInput', (_source, event) => { c.events.push({ action, ...event }); });
      await context.addInitScript(() => {
        for (const type of ['pointerdown', 'pointerup', 'click', 'wheel']) document.addEventListener(type, e => {
          const hit = document.elementFromPoint(e.clientX, e.clientY), r = e.target.getBoundingClientRect?.();
          void window.__recordRecoveryInput({ type, trusted: e.isTrusted, url: location.href, target: { tag: e.target.tagName, id: e.target.id }, pathIds: e.composedPath().map(n => n.id).filter(Boolean), x: e.clientX, y: e.clientY, hit: hit ? { tag: hit.tagName, id: hit.id } : null, hitStack: document.elementsFromPoint(e.clientX, e.clientY).map(n => ({ tag: n.tagName, id: n.id })), targetRect: r ? { left: r.left, top: r.top, right: r.right, bottom: r.bottom } : null, scrollTop: document.querySelector('#guideCard')?.scrollTop ?? null, time: performance.now() });
        }, { capture: true, passive: true });
      });
      page = await context.newPage(); page.setDefaultTimeout(6000);
      let modelURL;
      page.on('pageerror', e => c.errors.push(String(e)));
      page.on('requestfailed', r => { const msg = r.url() + ': ' + r.failure()?.errorText; if (blocking && r.url() === modelURL) c.expectedNetworkFailures.push(msg); else c.errors.push(msg); });
      page.on('response', r => { if (r.status() >= 400) c.errors.push('HTTP ' + r.status() + ': ' + r.url()); });
      for (const file of ['app.js', 'style.css', 'index.html', 'exhibit-entry.js', 'specimen-focus.js', 'model-version.js', 'scan-exhibit.js', 'scan-exhibit.html']) {
        const response = await context.request.get(new URL(file, base).href, { timeout: 6000 });
        const bytes = await response.body();
        assert(response.ok() && createHash('sha256').update(bytes).digest('hex') === manifest.files[file], 'Accepted snapshot mismatch: ' + file);
        if (file === 'model-version.js') { const match = bytes.toString().match(/MODEL_URL\s*=\s*['"]([^'"]+)['"]/); assert(match, 'Model URL export absent'); modelURL = new URL(match[1], base).href; }
      }
      c.modelURL = modelURL;
      const state = () => page.evaluate(() => window.reef3d?.getState());
      const checkpoint = async (name, detail = {}) => { c.checkpoints.push({ name, elapsedMs: Date.now() - started, ...detail }); console.log('MOBILE_RECOVERY_CHECKPOINT ' + JSON.stringify({ motion, ...c.checkpoints.at(-1) })); await save(); };
      const settle = selector => page.evaluate(selector => new Promise(resolve => {
        const started = performance.now(); let lastChange = started, previous = null, stable = 0;
        const sample = () => {
          const e = document.querySelector(selector), card = document.querySelector('#guideCard');
          if (!e) return resolve({ settled: false, reason: 'target-missing' });
          const r = e.getBoundingClientRect(), current = [r.left, r.top, r.right, r.bottom, card?.scrollTop ?? 0].join(',');
          if (current === previous) stable++; else { previous = current; stable = 0; lastChange = performance.now(); }
          if (stable >= 3 && performance.now() - lastChange >= 300) return resolve({ settled: true, durationMs: performance.now() - started, stableFrames: stable, sample: current });
          if (performance.now() - started >= 2500) return resolve({ settled: false, reason: 'scroll-or-layout-not-settled', sample: current });
          requestAnimationFrame(sample);
        }; requestAnimationFrame(sample);
      }), selector);
      const click = async (selector, wheel = false) => {
        action = motion + ':' + c.interactions.length + ':' + selector;
        const item = { action, selector, initial: await page.evaluate(observation, selector) }; c.interactions.push(item);
        try {
          if (wheel && item.initial.card) {
            const card = item.initial.card.rect;
            await page.mouse.move((card.left + card.right) / 2, (card.top + card.bottom) / 2);
            // One native wheel centers this target. No programmatic scroll or retries.
            const delta = item.initial.y - (card.top + card.bottom) / 2;
            item.wheelDelta = delta;
            await page.mouse.wheel(0, delta);
          }
          item.settlement = await settle(selector);
          item.pre = await page.evaluate(observation, selector);
          assert(item.settlement.settled, 'Unsettled target: ' + selector);
          assert(item.pre.exists && !item.pre.disabled && !item.pre.hidden && item.pre.display !== 'none' && item.pre.visibility === 'visible' && Number(item.pre.opacity) > 0 && item.pre.hitMatches, 'Target obstructed or unavailable: ' + selector);
          await page.locator(selector).click({ timeout: 6000 });
          try { item.post = await page.evaluate(() => ({ url: location.href, main: window.reef3d?.getState(), exhibit: window.reefExhibit?.getState(), restored: window.reefExhibitReturn })); } catch { item.post = { navigationInProgress: true }; }
          const input = c.events.filter(e => e.action === action && ['pointerdown', 'pointerup', 'click'].includes(e.type));
          assert(['pointerdown', 'pointerup', 'click'].every(type => input.some(e => e.type === type && e.trusted)), 'Incomplete trusted pointer sequence: ' + selector);
          const clicks = input.filter(e => e.type === 'click');
          assert(clicks.length === 1 && clicks[0].trusted, 'Missing or untrusted native click: ' + selector);
          if (selector.startsWith('#')) assert(clicks[0].pathIds.includes(selector.slice(1)), 'Native click reached wrong control: ' + selector);
          else assert(clicks[0].pathIds.includes('guideSteps'), 'Guide step click target wrong');
        } catch (e) { item.error = String(e); try { item.failure = await page.evaluate(observation, selector); } catch {} throw e; }
        finally { await save(); action = null; }
      };
      await page.goto(new URL('index.html', base).href, { waitUntil: 'domcontentloaded' });
      await page.waitForFunction(() => window.reef3d?.getState().ready, null, { timeout: 65000, polling: 250 });
      assert(await page.evaluate(() => matchMedia('(prefers-reduced-motion: reduce)').matches) === (motion === 'reduce'), 'Motion emulation mismatch');
      await click('#guideEntry'); await click('[data-guide="2"]', true); await click('#specimenInspect', true);
      const before = await state(); assert(before.specimenInspection && before.inspectionReturn && before.guide.paused && !before.guide.playing, 'Mobile inspect post-state wrong');
      const source = await page.locator('#guideSource').getAttribute('href');
      await checkpoint('mobile-native-inspection-after-settled-wheel', { before });
      await click('#enterScanExhibit');
      await page.waitForFunction(() => window.reefExhibit?.getState().ready, null, { timeout: 45000, polling: 250 });
      const raw = await page.evaluate(k => sessionStorage.getItem(k), key); assert(raw, 'Missing saved envelope');
      if (motion === 'no-preference') { blocking = true; await page.route(modelURL, route => route.abort('failed')); }
      await click('#returnWorld');
      if (motion === 'no-preference') {
        await page.waitForFunction(() => { const e = document.querySelector('#unsupported'); return !!e && !e.hidden; }, null, { timeout: 20000 });
        assert(await page.evaluate(k => sessionStorage.getItem(k), key) === raw, 'Failure consumed pending state');
        assert(new URL(page.url()).searchParams.get('return') === 'scan-exhibit', 'Failure cleared return intent');
        assert(c.expectedNetworkFailures.length === 1, 'Expected exactly one aborted model request');
        await checkpoint('model-failure-preserves-pending');
        await page.unroute(modelURL); blocking = false; await click('#retry');
      }
      const verifyRestored = async expected => {
        await page.waitForFunction(() => window.reefExhibitReturn?.restored, null, { timeout: 65000, polling: 250 });
        const restored = await state();
        assert(equal(expected, restored) && JSON.stringify(expected.inspectionReturn) === JSON.stringify(restored.inspectionReturn), 'Nested poses changed');
        assert(restored.specimenInspection && restored.guide.index === 2 && restored.guide.paused && !restored.guide.playing && !restored.tour, 'Restored guide state wrong');
        assert(restored.passageProgress === expected.passageProgress && restored.passageDirection === expected.passageDirection, 'Route context changed');
        assert(await page.locator('#guideSource').getAttribute('href') === source, 'Source changed');
        assert(await page.evaluate(k => sessionStorage.getItem(k), key) === null && !new URL(page.url()).searchParams.has('return'), 'Envelope not consumed exactly once');
        return restored;
      };
      await checkpoint('nested-state-restored-and-consumed', { nativeRetry: motion === 'no-preference', state: await verifyRestored(before) });
      await page.keyboard.press('Escape'); const exited = await state();
      assert(!exited.specimenInspection && equal(exited, { camera: before.inspectionReturn.position, target: before.inspectionReturn.target }), 'Escape exit pose wrong');
      assert(await page.locator('#viewName').textContent() === before.inspectionReturn.label, 'Exit label lost');
      await checkpoint('native-escape-restores-original-exit');
      await click('#specimenInspect', true); const repeated = await state(); assert(repeated.specimenInspection, 'Repeated inspection failed');
      await click('#enterScanExhibit'); await page.waitForFunction(() => window.reefExhibit?.getState().ready, null, { timeout: 45000, polling: 250 });
      await click('#returnWorld'); await checkpoint('second-native-route-return', { state: await verifyRestored(repeated) });
      await click('#specimenReturn', true); assert(equal(exited, await state()), 'Repeated button exit pose changed');
      await click('#guideNext', true); assert((await state()).guide.index === 3, 'Next did not advance');
      await checkpoint('native-return-and-next');
      assert(c.errors.length === 0, 'Unexpected page/network errors'); c.outcome = 'passed';
    } catch (e) { c.outcome = timedOut ? 'incomplete-context-budget' : 'failed'; c.failure = String(e.stack || e); }
    finally { clearTimeout(caseTimer); await context?.close().catch(() => {}); console.log('MOBILE_RECOVERY_CONTEXT ' + JSON.stringify(c)); await save(); }
  }
  report.passed = report.contexts.length === 2 && report.contexts.every(c => c.outcome === 'passed');
  if (!report.passed) process.exitCode = 1;
} catch (e) { report.failure = String(e.stack || e); process.exitCode = 1; }
finally {
  for (const motion of ['no-preference', 'reduce']) if (!report.contexts.some(c => c.motion === motion)) report.contexts.push({ motion, outcome: 'not-run-setup-failure', checkpoints: [] });
  await save(); await browser?.close().catch(() => {}); clearTimeout(deadline);
  console.log('MOBILE_RECOVERY_SUMMARY ' + JSON.stringify(report));
}
