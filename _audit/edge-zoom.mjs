// _audit/edge-zoom.mjs — крупные кропы кромок «экрана» (телефон 375) в настоящем Chrome.
// Ищем светлый шов между тёмными полосами устройства и безелем (в т.ч. на дробном масштабе).
// Запуск: node _audit/edge-zoom.mjs [dpr]   (например 1.5)
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const DPR = process.argv[2] || '1';
const URL = 'file:///C:/Users/asukharev/GitHub/DS/iiko-ds-prototypes/figma-7450-create-product.html';
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 9600 + Math.floor(Math.random() * 300);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'chrome-edge-'));

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--window-size=1200,1100', `--force-device-scale-factor=${DPR}`,
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
  await evaluate(`document.querySelector('.modes-bar__btn[data-w="375"]').click(); 'ok'`);
  await sleep(800);
  await evaluate(`window.scrollTo(0, 0); 'ok'`);
  await sleep(400);
  const p = JSON.parse(await evaluate(`JSON.stringify((() => {
    const r = document.getElementById('panel').getBoundingClientRect();
    return { left: r.left, top: r.top, right: r.right, bottom: r.bottom };
  })())`));
  console.log(`panel: ${p.left},${p.top}..${p.right},${p.bottom} (page scroll might offset)`);
  const shots = [
    ['corner-tl', p.left - 16, p.top - 16, 52, 52, 8],
    ['edge-top', p.left + 170, p.top - 16, 60, 40, 8],
    ['edge-left-status', p.left - 16, p.top + 8, 44, 40, 8],
    ['edge-right-status', p.right - 28, p.top + 8, 44, 40, 8],
    ['corner-br', p.right - 36, p.bottom - 36, 52, 52, 8],
  ];
  for (const [name, x, y, w, h, scale] of shots) {
    const clip = { x: Math.round(x), y: Math.round(y), width: w, height: h, scale };
    await send('Page.captureScreenshot', { format: 'png', clip, captureBeyondViewport: true });
    await sleep(250);
    const s = await send('Page.captureScreenshot', { format: 'png', clip, captureBeyondViewport: true });
    const file = `c:/Users/asukharev/GitHub/DS/_audit/_edge_d${DPR}_${name}.png`;
    fs.writeFileSync(file, Buffer.from(s.data, 'base64'));
    console.log('saved ' + file);
  }
} catch (e) {
  console.error('Ошибка:', e.message || e);
} finally {
  try { chrome.kill(); } catch {}
}
