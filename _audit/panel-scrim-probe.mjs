// _audit/panel-scrim-probe.mjs
// Проверка панели «Создать продукт» в НАСТОЯЩЕМ Chrome: десктоп/планшет/телефон.
// Снимаем кадр устройства целиком (панель открыта сразу): видно затемнение (Backdrop) и компоновку.
// Запуск: node _audit/panel-scrim-probe.mjs
// 2026-09-13: переведён на отдельную страницу панели figma-7450-create-product.html —
// клики для открытия больше не нужны (панель открыта по загрузке).
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const URL = 'file:///C:/Users/asukharev/GitHub/DS/iiko-ds-prototypes/figma-7450-create-product.html';
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 9600 + Math.floor(Math.random() * 300);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'chrome-pp-'));

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--window-size=1500,1450',
  `--remote-debugging-port=${PORT}`, '--remote-allow-origins=*', `--user-data-dir=${profile}`, 'about:blank',
], { stdio: 'ignore' });

let ws; let msgId = 0; const pending = new Map();
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const id = ++msgId;
  pending.set(id, { resolve, reject });
  ws.send(JSON.stringify({ id, method, params }));
});
async function waitFor(fn, timeout = 20000, step = 250) {
  const t0 = Date.now();
  while (Date.now() - t0 < timeout) { try { const v = await fn(); if (v) return v; } catch {} await sleep(step); }
  throw new Error('timeout');
}
let evaluate;
try {
  await waitFor(async () => (await fetch(`http://127.0.0.1:${PORT}/json/version`)).ok);
  const tab = await (await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent(URL)}`, { method: 'PUT' })).json();
  ws = new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result); }
  };
  evaluate = async (expr) => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.exceptionDetails) throw new Error('eval: ' + JSON.stringify(r.exceptionDetails).slice(0, 300));
    return r.result.value;
  };
  await send('Runtime.enable');
  await send('Page.enable');
  await waitFor(async () => (await evaluate('document.readyState')) === 'complete');
  await sleep(1600);

  async function shot(name, w) {
    await evaluate(`document.querySelector('.modes-bar__btn[data-w="${w}"]').click(); 'ok'`);
    await sleep(700);
    await evaluate(`(() => {
      const o = document.getElementById('pp-overlay');   // страница панели: держим её открытой
      if (o.hidden) { o.hidden = false; o.classList.add('is-open'); }
      window.scrollTo(0, 0);
      return 'ok';
    })()`);
    await sleep(600);
    const st = JSON.parse(await evaluate(`JSON.stringify((() => {
      const p = document.getElementById('panel').getBoundingClientRect();
      const bd = document.querySelector('.pp-overlay__backdrop').getBoundingClientRect();
      return { left: p.left, top: p.top, right: p.right, bottom: p.bottom,
               bdW: bd.width, bdH: bd.height, cls: document.body.className };
    })())`));
    const clip = { x: Math.max(0, st.left - 40), y: Math.max(0, st.top - 40), width: (st.right - st.left) + 80, height: (st.bottom - st.top) + 80, scale: 1 };
    await send('Page.captureScreenshot', { format: 'png', clip, captureBeyondViewport: true });   // прогрев: первый кадр после ресайза ловит stale-тайлы
    await sleep(300);
    const s = await send('Page.captureScreenshot', { format: 'png', clip, captureBeyondViewport: true });
    const file = `c:/Users/asukharev/GitHub/DS/_audit/_pp_${name}.png`;
    fs.writeFileSync(file, Buffer.from(s.data, 'base64'));
    console.log(`${name}: cls=${st.cls}, backdrop=${st.bdW}x${st.bdH} → ${file}`);
  }
  await shot('desktop', 1184);
  await shot('tablet', 768);
  await shot('phone', 375);
  console.log('done');
} catch (e) {
  console.error('Ошибка:', e.message || e);
} finally {
  try { chrome.kill(); } catch {}
}
