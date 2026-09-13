// _audit/panel-corners.mjs — пиксельная проба кромок панели «Создать продукт» (7450) в настоящем Chrome.
// Что ищем: (1) светлый шов/линию там, где оверлей панели или кадр примыкают к безелю/полосам устройства;
//           (2) острые углы панели поверх скруглённых углов «экрана» (десктоп/планшет).
// Запуск: node _audit/panel-corners.mjs [dpr]   (например 1.25)
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const DPR = process.argv[2] || '1.25';
const URL = 'file:///C:/Users/asukharev/GitHub/DS/iiko-ds-prototypes/figma-7450-create-product.html';
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 9900 + Math.floor(Math.random() * 90);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'chrome-pcorn-'));

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--window-size=1400,1100', `--force-device-scale-factor=${DPR}`,
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
try {
  await waitFor(async () => (await fetch(`http://127.0.0.1:${PORT}/json/version`)).ok);
  const tab = await (await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent(URL)}`, { method: 'PUT' })).json();
  ws = new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result); }
  };
  const evaluate = async (expr) => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.exceptionDetails) throw new Error('eval: ' + JSON.stringify(r.exceptionDetails).slice(0, 300));
    return r.result.value;
  };
  await send('Runtime.enable');
  await send('Page.enable');
  await waitFor(async () => (await evaluate('document.readyState')) === 'complete');
  await sleep(1600);

  async function shot(name, x, y, w, h, scale) {
    const clip = { x: Math.round(x), y: Math.round(y), width: Math.round(w), height: Math.round(h), scale };
    await send('Page.captureScreenshot', { format: 'png', clip, captureBeyondViewport: true });
    await sleep(200);
    const s = await send('Page.captureScreenshot', { format: 'png', clip, captureBeyondViewport: true });
    const file = `c:/Users/asukharev/GitHub/DS/_audit/_pc_d${DPR}_${name}.png`;
    fs.writeFileSync(file, Buffer.from(s.data, 'base64'));
    console.log('saved ' + file);
  }

  for (const [preset, w] of [['desktop', 1184], ['tablet', 768], ['phone', 375]]) {
    await evaluate(`document.querySelector('.modes-bar__btn[data-w="${w}"]').click(); 'ok'`);
    await sleep(900);
    await evaluate(`window.scrollTo(0, 0); 'ok'`);
    await sleep(400);
    const p = JSON.parse(await evaluate(`JSON.stringify((() => {
      const r = document.getElementById('panel').getBoundingClientRect();
      const ov = document.getElementById('pp-overlay').getBoundingClientRect();
      return { left: r.left, top: r.top, right: r.right, bottom: r.bottom,
               ovTop: ov.top, ovBottom: ov.bottom };
    })())`));
    console.log(`${preset}: panel ${p.left},${p.top}..${p.right},${p.bottom} overlayY ${p.ovTop}..${p.ovBottom}`);
    if (preset === 'desktop') {
      await shot(`d_top-edge`, p.left + 500, p.top - 8, 80, 20, 10);
      await shot(`d_corner-tr`, p.right - 30, p.top - 30, 44, 44, 10);
      await shot(`d_corner-br`, p.right - 30, p.bottom - 14, 44, 44, 10);
      await shot(`d_scrim-left`, p.left - 6, p.top - 6, 40, 20, 10);   // левый верхний угол раздела «серая подложка»/безель
      await shot(`d_top-scrim`, p.left + 200, p.top - 10, 80, 22, 10);   // кромка безеля над серой зоной (середина слева)
      await shot(`d_corner-tl`, p.left - 30, p.top - 30, 44, 44, 10);
    } else {
      await shot(`${preset[0]}_top-junction`, p.left + 60, p.top + 30, 80, 30, 10);
      await shot(`${preset[0]}_bottom-junction`, p.left + 60, p.bottom - 58, 80, 30, 10);
      await shot(`${preset[0]}_corner-tr`, p.right - 30, p.top - 30, 44, 44, 10);
    }
  }
} catch (e) {
  console.error('Ошибка:', e.message || e);
} finally {
  try { chrome.kill(); } catch {}
}
